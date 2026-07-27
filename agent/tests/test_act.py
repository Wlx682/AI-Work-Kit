"""Tests for checkpointable tool-use sessions."""

import unittest

from agent.capabilities import act


class ActionSessionTests(unittest.TestCase):
    def test_rejection_discards_later_calls_from_the_same_model_turn(self):
        session = {
            "messages": [{"role": "assistant", "content": None, "tool_calls": []}],
            "pending_calls": [
                {"id": "call-1", "name": "run_shell", "args": {"command": "rm -rf scratch"}},
                {"id": "call-2", "name": "write_file", "args": {"path": "report.md", "content": "done"}},
            ],
            "tool_rounds": 1,
        }

        resolved = act.resolve_approval(session, {"approved": False})

        self.assertEqual(resolved["pending_calls"], [])
        self.assertEqual(resolved["messages"][-1], {
            "role": "tool",
            "tool_call_id": "call-1",
            "content": "用户拒绝执行该操作",
        })


if __name__ == "__main__":
    unittest.main()
