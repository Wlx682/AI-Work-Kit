"""Offline tests for resilient structured LLM output parsing."""

import unittest
from unittest.mock import patch

from agent.infrastructure import llm


class ChatJsonTests(unittest.TestCase):
    def test_repairs_one_malformed_json_response(self):
        malformed = '[{"step": "inspect", "risk": "missing comma" "suggestion": "retry"}]'
        repaired = '[{"step": "inspect", "risk": "missing comma", "suggestion": "retry"}]'

        with patch("agent.infrastructure.llm.chat", side_effect=[
            {"content": malformed},
            {"content": repaired},
        ]) as chat:
            result = llm.chat_json([{"role": "user", "content": "return JSON"}])

        self.assertEqual(result, [{"step": "inspect", "risk": "missing comma", "suggestion": "retry"}])
        self.assertEqual(chat.call_count, 2)
        repair_messages = chat.call_args_list[1].args[0]
        self.assertEqual(repair_messages[-2]["content"], malformed)
        self.assertIn("只修复 JSON 语法", repair_messages[-1]["content"])

    def test_reports_failure_after_one_repair_attempt(self):
        with patch("agent.infrastructure.llm.chat", side_effect=[
            {"content": "{invalid"},
            {"content": "still invalid"},
        ]):
            with self.assertRaisesRegex(ValueError, "after one repair attempt"):
                llm.chat_json([{"role": "user", "content": "return JSON"}])


if __name__ == "__main__":
    unittest.main()
