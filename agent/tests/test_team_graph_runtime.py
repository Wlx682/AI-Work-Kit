"""Offline tests for the LangGraph Team migration."""

import unittest
from tempfile import TemporaryDirectory
from unittest.mock import patch

from langgraph.checkpoint.memory import InMemorySaver

from agent.orchestration.team_graph import TeamGraphRuntime
from agent.infrastructure.traces import TraceStore


class FakeMemory:
    def __init__(self):
        self.episodes = []

    def to_context(self):
        return "(无记忆)"

    def episodic_add(self, task, steps, results, outcome):
        self.episodes.append((task, steps, results, outcome))

    def semantic_add(self, fact, source=""):
        pass

    def procedural_add(self, pattern, steps):
        pass

    def corrections_add(self, mistake, lesson, source=""):
        pass


class TeamGraphRuntimeTests(unittest.TestCase):
    @staticmethod
    def runtime(memory, trace_store=None):
        return TeamGraphRuntime(memory, trace_store, checkpointer=InMemorySaver())

    def test_routes_safe_plan_to_execution_and_persists_handoffs(self):
        memory = FakeMemory()
        with TemporaryDirectory() as directory:
            store = TraceStore(directory)
            runtime = self.runtime(memory, store)

            with (
                patch("agent.roles.planner.planning.make_plan", return_value=["only step"]),
                patch("agent.roles.predictor.world_model.predict", return_value=[]),
                patch("agent.roles.predictor.world_model.has_high_risk", return_value=[]),
                patch("agent.roles.executor.act.advance", return_value={"status": "done", "result": "done"}),
                patch("agent.roles.reviewer.reviewing.review", return_value={
                    "verdict": "accept", "reason": "complete", "suggestion": "",
                }),
            ):
                result = runtime.run("test task")

            self.assertTrue(result.succeeded)
            self.assertEqual(result.outcome, "done")
            self.assertEqual(
                [event.phase for event in result.events],
                ["run", "load_memory", "plan", "predict", "prepare_action", "review", "save_memory", "run"],
            )
            handoffs = [
                event.payload["handoffs"][0]
                for event in result.events
                if "handoffs" in event.payload
            ]
            self.assertEqual(
                [(item["sender"], item["recipient"], item["intent"]) for item in handoffs],
                [
                    ("Planner", "Predictor", "plan"),
                    ("Predictor", "Executor", "plan_approved"),
                    ("Executor", "Reviewer", "result"),
                    ("Reviewer", "Team", "accept"),
                ],
            )
            self.assertNotEqual(result.run_id, result.thread_id)
            self.assertGreater(runtime.checkpoint_count(result.thread_id), 1)
            self.assertEqual(store.load(result.run_id), result)

    def test_routes_risk_and_review_rejection_through_graph_edges(self):
        memory = FakeMemory()
        with TemporaryDirectory() as directory:
            runtime = self.runtime(memory, TraceStore(directory))
            risk = [{"step": "first", "risk": "unsafe", "suggestion": "adjust"}]

            with (
                patch("agent.roles.planner.planning.make_plan", return_value=["first"]),
                patch("agent.roles.predictor.world_model.predict", return_value=risk),
                patch("agent.roles.predictor.world_model.has_high_risk", return_value=risk),
                patch("agent.roles.planner.planning.adjust_plan", return_value=["safer"]),
                patch("agent.roles.executor.act.advance", side_effect=[
                    {"status": "done", "result": "first result"},
                    {"status": "done", "result": "final result"},
                ]),
                patch("agent.roles.reviewer.reviewing.review", side_effect=[
                    {"verdict": "revise", "reason": "incomplete", "suggestion": "fix it"},
                    {"verdict": "accept", "reason": "complete", "suggestion": ""},
                ]),
                patch("agent.roles.planner.planning.revise_plan", return_value={
                    "decision": "tweak", "steps": ["revised"],
                }),
                patch("agent.orchestration.team_graph.self_improve.distill", return_value={}),
                patch("agent.orchestration.team_graph.self_improve.consolidate", return_value=0),
            ):
                result = runtime.run("test task", max_retries=1)

            self.assertTrue(result.succeeded)
            self.assertEqual(result.outcome, "final result")
            self.assertEqual(
                [event.phase for event in result.events],
                [
                    "run", "load_memory", "plan", "predict", "adjust_plan", "prepare_action", "review",
                    "revise_plan", "prepare_action", "review", "save_memory", "run",
                ],
            )
            self.assertEqual(memory.episodes[0][1], ["revised"])

    def test_trace_failure_is_only_a_warning_for_team_execution(self):
        memory = FakeMemory()
        runtime = self.runtime(memory)

        with (
            patch.object(runtime.trace_store, "save", side_effect=OSError("disk full")),
            patch("agent.roles.planner.planning.make_plan", return_value=["only step"]),
            patch("agent.roles.predictor.world_model.predict", return_value=[]),
            patch("agent.roles.predictor.world_model.has_high_risk", return_value=[]),
            patch("agent.roles.executor.act.advance", return_value={"status": "done", "result": "done"}),
            patch("agent.roles.reviewer.reviewing.review", return_value={"verdict": "accept"}),
        ):
            result = runtime.run("test task")

        self.assertTrue(result.succeeded)
        self.assertEqual(result.warnings, ("trace_persist_failed: disk full",))

    def test_stops_after_the_configured_retry_limit(self):
        memory = FakeMemory()
        with TemporaryDirectory() as directory:
            runtime = self.runtime(memory, TraceStore(directory))

            with (
                patch("agent.roles.planner.planning.make_plan", return_value=["only step"]),
                patch("agent.roles.predictor.world_model.predict", return_value=[]),
                patch("agent.roles.predictor.world_model.has_high_risk", return_value=[]),
                patch("agent.roles.executor.act.advance", return_value={"status": "done", "result": "partial"}),
                patch("agent.roles.reviewer.reviewing.review", return_value={
                    "verdict": "revise", "reason": "incomplete", "suggestion": "fix it",
                }),
                patch("agent.roles.planner.planning.revise_plan") as revise_plan,
                patch("agent.orchestration.team_graph.self_improve.distill", return_value={}) as distill,
                patch("agent.orchestration.team_graph.self_improve.consolidate", return_value=0),
            ):
                result = runtime.run("test task", max_retries=0)

            self.assertTrue(result.succeeded)
            self.assertEqual(result.outcome, "partial")
            self.assertNotIn("revise_plan", [event.phase for event in result.events])
            revise_plan.assert_not_called()
            distill.assert_called_once()

    def test_resumes_the_exact_team_tool_proposal_without_restarting_the_session(self):
        memory = FakeMemory()
        with TemporaryDirectory() as directory:
            runtime = self.runtime(memory, TraceStore(directory))
            session = {"messages": [{"role": "user", "content": "step"}], "pending_calls": [], "tool_rounds": 1}
            proposal = {
                "kind": "approval",
                "action_id": "action-1",
                "tool_call_id": "call-1",
                "tool": "run_shell",
                "args": {"command": "rm -rf scratch"},
                "reason": "危险命令模式: rm -rf",
            }

            with (
                patch("agent.roles.planner.planning.make_plan", return_value=["sensitive step"]),
                patch("agent.roles.predictor.world_model.predict", return_value=[]),
                patch("agent.roles.predictor.world_model.has_high_risk", return_value=[]),
                patch("agent.roles.executor.act.start_step", return_value=session) as start_step,
                patch("agent.roles.executor.act.advance", side_effect=[
                    {"status": "interrupted", "session": session, "interruption": proposal},
                    {"status": "done", "result": "executed"},
                ]) as advance,
                patch("agent.roles.executor.act.resolve_interruption", return_value={
                    "status": "resolved",
                    "session": session,
                    "actions": [{"action_id": "action-1", "status": "called"}],
                }) as resolve,
                patch("agent.roles.reviewer.reviewing.review", return_value={"verdict": "accept"}),
            ):
                paused = runtime.run("test task")
                resumed = runtime.resume(
                    paused.thread_id,
                    {"approved": True},
                    parent_run_id=paused.run_id,
                )

            self.assertTrue(paused.is_paused)
            self.assertEqual(paused.interrupts[0]["value"], proposal)
            self.assertEqual(
                next(event for event in resumed.events if event.phase == "interrupt_for_human").payload["action_events"][0]["action_id"],
                "action-1",
            )
            self.assertTrue(resumed.succeeded)
            self.assertNotEqual(resumed.run_id, paused.run_id)
            self.assertEqual(resumed.thread_id, paused.thread_id)
            self.assertEqual(resumed.parent_run_id, paused.run_id)
            self.assertIsNotNone(resumed.recovered_from_checkpoint_id)
            self.assertEqual(runtime.trace_store.load(paused.run_id), paused)
            start_step.assert_called_once()
            self.assertEqual(advance.call_count, 2)
            self.assertEqual(resolve.call_args.args[0], session)
            self.assertEqual(resumed.outcome, "executed")

    def test_pauses_team_execution_when_an_action_is_unknown(self):
        memory = FakeMemory()
        runtime = self.runtime(memory)
        session = {"messages": [], "pending_calls": [], "tool_rounds": 1}
        unknown = {
            "kind": "unknown",
            "action_id": "action-1",
            "tool": "run_shell",
            "args": {"command": "sleep 60"},
            "error": "command timed out after 30 seconds",
        }

        with (
            patch("agent.roles.planner.planning.make_plan", return_value=["run step"]),
            patch("agent.roles.predictor.world_model.predict", return_value=[]),
            patch("agent.roles.predictor.world_model.has_high_risk", return_value=[]),
            patch("agent.roles.executor.act.start_step", return_value=session),
            patch("agent.roles.executor.act.advance", return_value={
                "status": "interrupted", "session": session, "interruption": unknown,
                "actions": [{"action_id": "action-1", "status": "unknown"}],
            }),
        ):
            paused = runtime.run("test task")

        self.assertTrue(paused.is_paused)
        self.assertEqual(paused.interrupts[0]["value"], unknown)
        self.assertEqual(paused.events[-1].phase, "unknown")


if __name__ == "__main__":
    unittest.main()
