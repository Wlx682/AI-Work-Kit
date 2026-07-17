"""Offline tests for the LangGraph runtime migration."""

import unittest
from unittest.mock import patch

from agent.langgraph_runtime import LangGraphRuntime
from agent.orchestrator import Orchestrator


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
    def test_records_replan_trace_and_framework_checkpoints(self):
        memory = FakeMemory()
        orchestrator = Orchestrator(memory)
        self.assertIsInstance(orchestrator.runtime, LangGraphRuntime)

        with (
            patch("agent.langgraph_runtime.planning.make_plan", return_value=["first", "second"]),
            patch("agent.langgraph_runtime.world_model.predict", return_value=[]),
            patch("agent.langgraph_runtime.world_model.has_high_risk", return_value=[]),
            patch("agent.langgraph_runtime.act.run_step", side_effect=["first result", "final result"]),
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
        self.assertGreater(orchestrator.runtime.checkpoint_count(result.run_id), 1)
        self.assertEqual(result.events[-1].status, "completed")

    def test_captures_planning_failure_as_a_structured_result(self):
        orchestrator = Orchestrator(FakeMemory())

        with patch("agent.langgraph_runtime.planning.make_plan", side_effect=RuntimeError("LLM unavailable")):
            result = orchestrator.run_with_trace("test task")

        self.assertFalse(result.succeeded)
        self.assertIn("LLM unavailable", result.error)
        self.assertEqual(result.events[-1].status, "failed")


if __name__ == "__main__":
    unittest.main()
