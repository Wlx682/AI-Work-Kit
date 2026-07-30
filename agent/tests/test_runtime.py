"""Offline tests for the LangGraph runtime migration."""

import unittest
from pathlib import Path
from tempfile import TemporaryDirectory
from unittest.mock import patch

from langgraph.checkpoint.memory import InMemorySaver

from agent.langgraph_runtime import LangGraphRuntime
from agent.orchestrator import Orchestrator
from agent.trace_store import TraceStore


class FakeMemory:
    def __init__(self):
        self.working = []
        self.episodes = []

    def to_context(self):
        return "(无记忆)"

    def working_add(self, entry):
        self.working.append(entry)

    def working_clear(self):
        self.working.clear()

    def episodic_add(self, task, steps, results, outcome):
        self.episodes.append((task, steps, results, outcome))

    def semantic_add(self, fact, source=""):
        pass

    def procedural_add(self, pattern, steps):
        pass

    def corrections_add(self, mistake, lesson, source=""):
        pass


class LangGraphRuntimeTests(unittest.TestCase):
    @staticmethod
    def runtime(memory, trace_store=None):
        return LangGraphRuntime(memory, trace_store, checkpointer=InMemorySaver())

    def test_persists_normal_completion_trace(self):
        memory = FakeMemory()
        with TemporaryDirectory() as directory:
            store = TraceStore(directory)
            orchestrator = Orchestrator(memory, self.runtime(memory, store))

            with (
                patch("agent.langgraph_runtime.planning.make_plan", return_value=["only step"]),
                patch("agent.langgraph_runtime.world_model.predict", return_value=[]),
                patch("agent.langgraph_runtime.world_model.has_high_risk", return_value=[]),
                patch("agent.langgraph_runtime.act.advance", return_value={"status": "done", "result": "done"}),
            ):
                result = orchestrator.run_with_trace("test task")

            self.assertTrue(result.succeeded)
            self.assertEqual(store.load(result.run_id), result)
            self.assertEqual(
                [event.phase for event in result.events],
                ["run", "load_memory", "plan", "predict", "prepare_action", "save_memory", "run"],
            )

    def test_records_replan_trace_and_framework_checkpoints(self):
        memory = FakeMemory()
        with TemporaryDirectory() as directory:
            store = TraceStore(directory)
            orchestrator = Orchestrator(memory, self.runtime(memory, store))
            self.assertIsInstance(orchestrator.runtime, LangGraphRuntime)

            with (
                patch("agent.langgraph_runtime.planning.make_plan", return_value=["first", "second"]),
                patch("agent.langgraph_runtime.world_model.predict", return_value=[]),
                patch("agent.langgraph_runtime.world_model.has_high_risk", return_value=[]),
                patch("agent.langgraph_runtime.act.advance", side_effect=[
                    {"status": "done", "result": "first result"},
                    {"status": "done", "result": "final result"},
                ]),
                patch("agent.langgraph_runtime.reviewing.reflect", return_value={
                    "action": "replan",
                    "new_steps": ["second revised"],
                    "has_lesson": True,
                }),
                patch("agent.langgraph_runtime.self_improve.distill", return_value={}),
                patch("agent.langgraph_runtime.self_improve.consolidate", return_value=0),
            ):
                result = orchestrator.run_with_trace("test task")

            self.assertTrue(result.succeeded)
            self.assertEqual(result.outcome, "final result")
            self.assertEqual(memory.episodes[0][3], "final result")
            self.assertEqual([event.sequence for event in result.events], list(range(1, len(result.events) + 1)))
            self.assertEqual(result.events[0].phase, "run")
            self.assertIn("plan", [event.phase for event in result.events])
            self.assertIn("reflect", [event.phase for event in result.events])
            self.assertNotEqual(result.run_id, result.thread_id)
            self.assertGreater(orchestrator.runtime.checkpoint_count(result.thread_id), 1)
            self.assertEqual(result.events[-1].status, "completed")
            self.assertEqual(store.load(result.run_id), result)

    def test_captures_planning_failure_as_a_structured_result(self):
        memory = FakeMemory()
        with TemporaryDirectory() as directory:
            store = TraceStore(directory)
            orchestrator = Orchestrator(memory, self.runtime(memory, store))

            with patch("agent.langgraph_runtime.planning.make_plan", side_effect=RuntimeError("LLM unavailable")):
                result = orchestrator.run_with_trace("test task")

            self.assertFalse(result.succeeded)
            self.assertIn("LLM unavailable", result.error)
            self.assertEqual(result.events[-1].status, "failed")
            self.assertEqual(store.load(result.run_id), result)

    def test_trace_failure_is_a_warning_not_a_business_failure(self):
        memory = FakeMemory()
        runtime = self.runtime(memory)
        orchestrator = Orchestrator(memory, runtime)

        with (
            patch.object(runtime.trace_store, "save", side_effect=OSError("disk full")),
            patch("agent.langgraph_runtime.planning.make_plan", return_value=["only step"]),
            patch("agent.langgraph_runtime.world_model.predict", return_value=[]),
            patch("agent.langgraph_runtime.world_model.has_high_risk", return_value=[]),
            patch("agent.langgraph_runtime.act.advance", return_value={"status": "done", "result": "done"}),
        ):
            result = orchestrator.run_with_trace("test task")

        self.assertTrue(result.succeeded)
        self.assertEqual(result.outcome, "done")
        self.assertEqual(result.warnings, ("trace_persist_failed: disk full",))

    def test_resumes_the_exact_tool_proposal_without_restarting_the_session(self):
        memory = FakeMemory()
        with TemporaryDirectory() as directory:
            runtime = self.runtime(memory, TraceStore(directory))
            session = {"messages": [{"role": "user", "content": "step"}], "pending_calls": [], "tool_rounds": 1}
            proposal = {
                "action_id": "action-1",
                "tool_call_id": "call-1",
                "tool": "run_shell",
                "args": {"command": "rm -rf scratch"},
                "reason": "危险命令模式: rm -rf",
            }

            with (
                patch("agent.langgraph_runtime.planning.make_plan", return_value=["sensitive step"]),
                patch("agent.langgraph_runtime.world_model.predict", return_value=[]),
                patch("agent.langgraph_runtime.world_model.has_high_risk", return_value=[]),
                patch("agent.langgraph_runtime.act.start_step", return_value=session) as start_step,
                patch("agent.langgraph_runtime.act.advance", side_effect=[
                    {"status": "approval_required", "session": session, "proposal": proposal},
                    {"status": "done", "result": "executed"},
                ]) as advance,
                patch("agent.langgraph_runtime.act.resolve_approval", return_value=session) as resolve,
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
                next(event for event in resumed.events if event.phase == "approve_tool").payload["action_events"][0]["action_id"],
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
            self.assertEqual(resolve.call_args.args[1], {"approved": True})
            self.assertEqual(resumed.outcome, "executed")

    def test_resumes_from_sqlite_after_creating_a_fresh_runtime(self):
        memory = FakeMemory()
        with TemporaryDirectory() as directory:
            checkpoint_path = Path(directory) / "checkpoints.sqlite"
            trace_store = TraceStore(Path(directory) / "traces")
            session = {"messages": [{"role": "user", "content": "step"}], "pending_calls": [], "tool_rounds": 1}
            proposal = {
                "action_id": "action-1",
                "tool_call_id": "call-1",
                "tool": "run_shell",
                "args": {"command": "rm -rf scratch"},
                "reason": "危险命令模式: rm -rf",
            }
            runtime = LangGraphRuntime(memory, trace_store, checkpoint_path=str(checkpoint_path))

            with (
                patch("agent.langgraph_runtime.planning.make_plan", return_value=["sensitive step"]),
                patch("agent.langgraph_runtime.world_model.predict", return_value=[]),
                patch("agent.langgraph_runtime.world_model.has_high_risk", return_value=[]),
                patch("agent.langgraph_runtime.act.start_step", return_value=session) as start_step,
                patch("agent.langgraph_runtime.act.advance", side_effect=[
                    {"status": "approval_required", "session": session, "proposal": proposal},
                    {"status": "done", "result": "executed"},
                ]) as advance,
                patch("agent.langgraph_runtime.act.resolve_approval", return_value=session) as resolve,
            ):
                paused = runtime.run("test task")
                runtime.close()

                fresh_runtime = LangGraphRuntime(memory, trace_store, checkpoint_path=str(checkpoint_path))
                resumed = fresh_runtime.resume(
                    paused.thread_id,
                    {"approved": True},
                    parent_run_id=paused.run_id,
                )
                fresh_runtime.close()

            self.assertTrue(paused.is_paused)
            self.assertTrue(resumed.succeeded)
            self.assertNotEqual(resumed.run_id, paused.run_id)
            self.assertEqual(resumed.thread_id, paused.thread_id)
            self.assertEqual(resumed.parent_run_id, paused.run_id)
            start_step.assert_called_once()
            self.assertEqual(advance.call_count, 2)
            self.assertEqual(resolve.call_args.args[0], session)
            self.assertEqual(resumed.outcome, "executed")

    def test_replays_and_forks_from_a_selected_checkpoint(self):
        memory = FakeMemory()
        with TemporaryDirectory() as directory:
            store = TraceStore(directory)
            runtime = self.runtime(memory, store)

            with (
                patch("agent.langgraph_runtime.planning.make_plan", return_value=["original step"]),
                patch("agent.langgraph_runtime.world_model.predict", return_value=[]) as predict,
                patch("agent.langgraph_runtime.world_model.has_high_risk", return_value=[]) as has_high_risk,
                patch("agent.langgraph_runtime.act.advance", side_effect=[
                    {"status": "done", "result": "original result"},
                    {"status": "done", "result": "replayed result"},
                    {"status": "done", "result": "forked result"},
                ]) as advance,
            ):
                original = runtime.run("test task")
                checkpoints = runtime.checkpoint_history(original.thread_id)
                selected = next(item for item in checkpoints if item.next_nodes == ("prepare_action",))
                replayed = runtime.recover(
                    original.thread_id,
                    selected.checkpoint_id,
                    parent_run_id=original.run_id,
                )
                forked = runtime.recover(
                    original.thread_id,
                    selected.checkpoint_id,
                    state_patch={"steps": ["forked step"]},
                    parent_run_id=original.run_id,
                )

            self.assertTrue(original.succeeded)
            self.assertTrue(replayed.succeeded)
            self.assertTrue(forked.succeeded)
            self.assertEqual(replayed.outcome, "replayed result")
            self.assertEqual(forked.outcome, "forked result")
            self.assertEqual(replayed.recovery_mode, "replay")
            self.assertEqual(forked.recovery_mode, "fork")
            self.assertEqual(replayed.recovered_from_checkpoint_id, selected.checkpoint_id)
            self.assertEqual(forked.recovered_from_checkpoint_id, selected.checkpoint_id)
            self.assertEqual(replayed.parent_run_id, original.run_id)
            self.assertEqual(forked.parent_run_id, original.run_id)
            self.assertEqual(advance.call_count, 3)
            self.assertEqual(predict.call_count, 2)
            self.assertEqual(has_high_risk.call_count, 2)
            self.assertEqual(forked.events[0].payload["patched_fields"], ["steps"])
            self.assertEqual(store.load(original.run_id), original)
            self.assertEqual(store.load(replayed.run_id), replayed)
            self.assertEqual(store.load(forked.run_id), forked)

    def test_recovery_fork_rejects_state_that_could_bypass_approval(self):
        memory = FakeMemory()
        runtime = self.runtime(memory)
        with (
            patch("agent.langgraph_runtime.planning.make_plan", return_value=["only step"]),
            patch("agent.langgraph_runtime.world_model.predict", return_value=[]),
            patch("agent.langgraph_runtime.world_model.has_high_risk", return_value=[]),
            patch("agent.langgraph_runtime.act.advance", return_value={"status": "done", "result": "done"}),
        ):
            original = runtime.run("test task")
            checkpoint = runtime.checkpoint_history(original.thread_id)[0]
            with self.assertRaisesRegex(ValueError, "pending_approval"):
                runtime.recover(
                    original.thread_id,
                    checkpoint.checkpoint_id,
                    state_patch={"pending_approval": {}},
                    parent_run_id=original.run_id,
                )


if __name__ == "__main__":
    unittest.main()
