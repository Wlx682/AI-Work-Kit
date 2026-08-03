"""Tests for capability-aware planning prompts."""

import unittest
from unittest.mock import patch

from agent.core.definition import AgentDefinition
from agent.capabilities import planning


class PlanningTests(unittest.TestCase):
    def test_plan_receives_execution_capabilities_not_just_planner_policy(self):
        definition = AgentDefinition(
            id="planner",
            role="planner",
            goal="plan",
            tools=(),
            acceptance=("finish",),
            instructions="plan only",
        )

        with patch("agent.capabilities.planning.llm.chat_json", return_value=["ask for city"]) as chat:
            steps = planning.make_plan(
                "天气预报",
                definition=definition,
                execution_tools=("read_file", "get_current_time"),
            )

        prompt = chat.call_args.args[0][0]["content"]
        self.assertEqual(steps, ["ask for city"])
        self.assertIn("已注册的执行工具：read_file, get_current_time", prompt)
        self.assertIn("request_user_input", prompt)
        self.assertIn("API 密钥", prompt)

    def test_risk_adjustment_keeps_the_same_capability_boundary(self):
        with patch("agent.capabilities.planning.llm.chat_json", return_value=["ask for city"]) as chat:
            planning.adjust_plan(
                ["ask for city"],
                [{"step": "ask for city", "risk": "none", "suggestion": ""}],
                execution_tools=("get_current_time",),
            )

        prompt = chat.call_args.args[0][0]["content"]
        self.assertIn("已注册的执行工具：get_current_time", prompt)
        self.assertIn("不要把通用的网络", prompt)

    def test_rejects_non_string_steps_before_they_enter_graph_state(self):
        with (
            patch("agent.capabilities.planning.llm.chat_json", return_value=[{"step": "invalid"}]),
            self.assertRaisesRegex(ValueError, "plan output does not match schema"),
        ):
            planning.adjust_plan(["valid step"], [])


if __name__ == "__main__":
    unittest.main()
