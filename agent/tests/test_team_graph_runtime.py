"""Offline tests for the LangGraph Team migration."""

import unittest
from tempfile import TemporaryDirectory
from unittest.mock import patch

from agent.team_graph_runtime import TeamGraphRuntime
from agent.trace_store import TraceStore


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
    def test_routes_safe_plan_to_execution_and_persists_handoffs(self):
        memory = FakeMemory()
        with TemporaryDirectory() as directory:
            store = TraceStore(directory)
            runtime = TeamGraphRuntime(memory, store)

            with (
                patch("agent.roles.planner.planning.make_plan", return_value=["only step"]),
                patch("agent.roles.predictor.world_model.predict", return_value=[]),
                patch("agent.roles.predictor.world_model.has_high_risk", return_value=[]),
                patch("agent.roles.executor.act.run_step", return_value="done"),
                patch("agent.roles.reviewer.reviewing.review", return_value={
                    "verdict": "accept", "reason": "complete", "suggestion": "",
                }),
            ):
                result = runtime.run("test task")

            self.assertTrue(result.succeeded)
            self.assertEqual(result.outcome, "done")
            self.assertEqual(
                [event.phase for event in result.events],
                ["run", "load_memory", "plan", "predict", "execute", "review", "save_memory", "run"],
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
            self.assertGreater(runtime.checkpoint_count(result.run_id), 1)
            self.assertEqual(store.load(result.run_id), result)

    def test_routes_risk_and_review_rejection_through_graph_edges(self):
        memory = FakeMemory()
        with TemporaryDirectory() as directory:
            runtime = TeamGraphRuntime(memory, TraceStore(directory))
            risk = [{"step": "first", "risk": "unsafe", "suggestion": "adjust"}]

            with (
                patch("agent.roles.planner.planning.make_plan", return_value=["first"]),
                patch("agent.roles.predictor.world_model.predict", return_value=risk),
                patch("agent.roles.predictor.world_model.has_high_risk", return_value=risk),
                patch("agent.roles.planner.planning.adjust_plan", return_value=["safer"]),
                patch("agent.roles.executor.act.run_step", side_effect=["first result", "final result"]),
                patch("agent.roles.reviewer.reviewing.review", side_effect=[
                    {"verdict": "revise", "reason": "incomplete", "suggestion": "fix it"},
                    {"verdict": "accept", "reason": "complete", "suggestion": ""},
                ]),
                patch("agent.roles.planner.planning.revise_plan", return_value={
                    "decision": "tweak", "steps": ["revised"],
                }),
                patch("agent.team_graph_runtime.self_improve.distill", return_value={}),
                patch("agent.team_graph_runtime.self_improve.consolidate", return_value=0),
            ):
                result = runtime.run("test task", max_retries=1)

            self.assertTrue(result.succeeded)
            self.assertEqual(result.outcome, "final result")
            self.assertEqual(
                [event.phase for event in result.events],
                [
                    "run", "load_memory", "plan", "predict", "adjust_plan", "execute", "review",
                    "revise_plan", "execute", "review", "save_memory", "run",
                ],
            )
            self.assertEqual(memory.episodes[0][1], ["revised"])

    def test_trace_failure_is_only_a_warning_for_team_execution(self):
        memory = FakeMemory()
        runtime = TeamGraphRuntime(memory)

        with (
            patch.object(runtime.trace_store, "save", side_effect=OSError("disk full")),
            patch("agent.roles.planner.planning.make_plan", return_value=["only step"]),
            patch("agent.roles.predictor.world_model.predict", return_value=[]),
            patch("agent.roles.predictor.world_model.has_high_risk", return_value=[]),
            patch("agent.roles.executor.act.run_step", return_value="done"),
            patch("agent.roles.reviewer.reviewing.review", return_value={"verdict": "accept"}),
        ):
            result = runtime.run("test task")

        self.assertTrue(result.succeeded)
        self.assertEqual(result.warnings, ("trace_persist_failed: disk full",))

    def test_stops_after_the_configured_retry_limit(self):
        memory = FakeMemory()
        with TemporaryDirectory() as directory:
            runtime = TeamGraphRuntime(memory, TraceStore(directory))

            with (
                patch("agent.roles.planner.planning.make_plan", return_value=["only step"]),
                patch("agent.roles.predictor.world_model.predict", return_value=[]),
                patch("agent.roles.predictor.world_model.has_high_risk", return_value=[]),
                patch("agent.roles.executor.act.run_step", return_value="partial"),
                patch("agent.roles.reviewer.reviewing.review", return_value={
                    "verdict": "revise", "reason": "incomplete", "suggestion": "fix it",
                }),
                patch("agent.roles.planner.planning.revise_plan") as revise_plan,
                patch("agent.team_graph_runtime.self_improve.distill", return_value={}) as distill,
                patch("agent.team_graph_runtime.self_improve.consolidate", return_value=0),
            ):
                result = runtime.run("test task", max_retries=0)

            self.assertTrue(result.succeeded)
            self.assertEqual(result.outcome, "partial")
            self.assertNotIn("revise_plan", [event.phase for event in result.events])
            revise_plan.assert_not_called()
            distill.assert_called_once()


if __name__ == "__main__":
    unittest.main()
