"""Tests for the controlled learning-agent runtime."""

from __future__ import annotations

import unittest
from pathlib import Path
from tempfile import TemporaryDirectory

from langgraph.checkpoint.memory import InMemorySaver

from knowledge_graph_learning.backend.orchestration.runtime import (
    LearningAgentRuntime,
    LearningRuntimeRoles,
    LearningRuntimeTools,
)
from agent.infrastructure.traces import TraceStore


class LearningAgentRuntimeTests(unittest.TestCase):
    @staticmethod
    def roles(calls: list[str], proposal: dict | None = None) -> LearningRuntimeRoles:
        def graph_curator(state):
            calls.append("graph_curator")
            return {"nodes": [state["request"]["concept_id"]]}

        def learning_planner(state):
            calls.append("learning_planner")
            return {"next_concept_id": state["graph_context"]["nodes"][0]}

        def tutor(state):
            calls.append("tutor")
            return {"content": f"learn {state['learning_plan']['next_concept_id']}"}

        def evaluator(state):
            calls.append("evaluator")
            result = {"passed": True, "evidence_id": "evidence-1"}
            if proposal is not None:
                result["graph_update_proposal"] = proposal
            return result

        return LearningRuntimeRoles(
            graph_curator=graph_curator,
            learning_planner=learning_planner,
            tutor=tutor,
            evaluator=evaluator,
        )

    @staticmethod
    def runtime(roles, tool, trace_store=None):
        return LearningAgentRuntime(
            roles,
            LearningRuntimeTools(apply_graph_update=tool),
            trace_store=trace_store,
            checkpointer=InMemorySaver(),
        )

    def test_runs_four_roles_in_order_and_persists_a_trace_without_a_proposal(self):
        calls = []
        with TemporaryDirectory() as directory:
            store = TraceStore(directory)
            runtime = self.runtime(self.roles(calls), lambda proposal: {}, store)

            result = runtime.run({"task": "learn runtime", "concept_id": "runtime-state"})

            self.assertTrue(result.succeeded)
            self.assertEqual(result.outcome, "completed")
            self.assertEqual(
                calls,
                ["graph_curator", "learning_planner", "tutor", "evaluator"],
            )
            phases = [event.phase for event in result.events]
            self.assertEqual(
                phases,
                [
                    "run",
                    "graph_curator",
                    "learning_planner",
                    "tutor",
                    "evaluator",
                    "complete",
                    "run",
                ],
            )
            self.assertEqual(store.load(result.run_id), result)

    def test_pauses_before_a_graph_update_and_saves_a_checkpoint(self):
        calls = []
        tool_calls = []
        proposal = {"operation": "record_evidence", "evidence_id": "evidence-1"}
        runtime = self.runtime(
            self.roles(calls, proposal),
            lambda value: tool_calls.append(value) or {"applied": True},
        )

        paused = runtime.run({"task": "learn runtime", "concept_id": "runtime-state"})

        self.assertTrue(paused.is_paused)
        self.assertIsNone(paused.outcome)
        self.assertEqual(tool_calls, [])
        self.assertEqual(paused.interrupts[0]["value"], {
            "kind": "graph_update_confirmation",
            "proposal": proposal,
        })
        self.assertGreater(len(runtime.checkpoint_history(paused.thread_id)), 0)
        self.assertEqual(paused.events[-1].status, "paused")

    def test_resumes_an_approved_proposal_and_calls_the_write_tool_once(self):
        calls = []
        tool_calls = []
        proposal = {"operation": "record_evidence", "evidence_id": "evidence-1"}
        runtime = self.runtime(
            self.roles(calls, proposal),
            lambda value: tool_calls.append(value) or {"applied": True},
        )
        paused = runtime.run({"task": "learn runtime", "concept_id": "runtime-state"})

        resumed = runtime.resume(
            paused.thread_id,
            {"approved": True},
            parent_run_id=paused.run_id,
        )

        self.assertTrue(resumed.succeeded)
        self.assertEqual(resumed.outcome, "completed")
        self.assertEqual(tool_calls, [proposal])
        self.assertEqual(resumed.thread_id, paused.thread_id)
        self.assertEqual(resumed.parent_run_id, paused.run_id)
        self.assertIsNotNone(resumed.recovered_from_checkpoint_id)
        self.assertIn("human_review", [event.phase for event in resumed.events])
        self.assertIn("apply_graph_update", [event.phase for event in resumed.events])

    def test_rejection_completes_without_calling_the_write_tool(self):
        calls = []
        tool_calls = []
        proposal = {"operation": "record_evidence", "evidence_id": "evidence-1"}
        runtime = self.runtime(
            self.roles(calls, proposal),
            lambda value: tool_calls.append(value) or {"applied": True},
        )
        paused = runtime.run({"task": "learn runtime", "concept_id": "runtime-state"})

        resumed = runtime.resume(paused.thread_id, False, parent_run_id=paused.run_id)

        self.assertTrue(resumed.succeeded)
        self.assertEqual(resumed.outcome, "completed_without_graph_update")
        self.assertEqual(tool_calls, [])
        self.assertNotIn("apply_graph_update", [event.phase for event in resumed.events])

    def test_role_failure_closes_with_a_failed_terminal_trace(self):
        calls = []
        roles = self.roles(calls)

        def failing_planner(state):
            raise RuntimeError("planner unavailable")

        roles = LearningRuntimeRoles(
            graph_curator=roles.graph_curator,
            learning_planner=failing_planner,
            tutor=roles.tutor,
            evaluator=roles.evaluator,
        )
        runtime = self.runtime(roles, lambda proposal: {})

        result = runtime.run({"task": "learn runtime", "concept_id": "runtime-state"})

        self.assertFalse(result.succeeded)
        self.assertIn("planner unavailable", result.error)
        self.assertEqual(result.events[-1].phase, "run")
        self.assertEqual(result.events[-1].status, "failed")

    def test_tool_failure_after_approval_closes_with_a_failed_terminal_trace(self):
        calls = []
        proposal = {"operation": "record_evidence", "evidence_id": "evidence-1"}

        def failing_tool(value):
            raise OSError("graph store unavailable")

        runtime = self.runtime(self.roles(calls, proposal), failing_tool)
        paused = runtime.run({"task": "learn runtime", "concept_id": "runtime-state"})

        resumed = runtime.resume(paused.thread_id, True, parent_run_id=paused.run_id)

        self.assertFalse(resumed.succeeded)
        self.assertIn("graph store unavailable", resumed.error)
        self.assertEqual(resumed.events[-1].status, "failed")

    def test_resumes_from_sqlite_with_a_fresh_runtime_instance(self):
        calls = []
        tool_calls = []
        proposal = {"operation": "record_evidence", "evidence_id": "evidence-1"}
        roles = self.roles(calls, proposal)
        tool = lambda value: tool_calls.append(value) or {"applied": True}

        with TemporaryDirectory() as directory:
            checkpoint_path = Path(directory) / "learning-runtime.sqlite"
            trace_store = TraceStore(Path(directory) / "traces")
            runtime = LearningAgentRuntime(
                roles,
                LearningRuntimeTools(apply_graph_update=tool),
                trace_store=trace_store,
                checkpoint_path=str(checkpoint_path),
            )
            paused = runtime.run({"task": "learn runtime", "concept_id": "runtime-state"})
            runtime.close()

            fresh_runtime = LearningAgentRuntime(
                roles,
                LearningRuntimeTools(apply_graph_update=tool),
                trace_store=trace_store,
                checkpoint_path=str(checkpoint_path),
            )
            resumed = fresh_runtime.resume(
                paused.thread_id,
                {"approved": True},
                parent_run_id=paused.run_id,
            )
            fresh_runtime.close()

        self.assertTrue(paused.is_paused)
        self.assertTrue(resumed.succeeded)
        self.assertEqual(resumed.outcome, "completed")
        self.assertEqual(tool_calls, [proposal])
        self.assertEqual(calls, ["graph_curator", "learning_planner", "tutor", "evaluator"])

    def test_rejects_a_non_json_role_output_as_a_contract_failure(self):
        roles = self.roles([])

        def invalid_evaluator(state):
            return {"evidence": object()}

        runtime = self.runtime(
            LearningRuntimeRoles(
                graph_curator=roles.graph_curator,
                learning_planner=roles.learning_planner,
                tutor=roles.tutor,
                evaluator=invalid_evaluator,
            ),
            lambda proposal: {},
        )

        result = runtime.run({"task": "learn runtime", "concept_id": "runtime-state"})

        self.assertFalse(result.succeeded)
        self.assertIn("INVALID_ROLE_OUTPUT", result.error)
        self.assertEqual(result.events[-1].status, "failed")


if __name__ == "__main__":
    unittest.main()
