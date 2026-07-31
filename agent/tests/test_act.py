"""Tests for checkpointable tool-use sessions."""

import unittest
from types import SimpleNamespace
from unittest.mock import patch

from agent.capabilities import act


class ActionSessionTests(unittest.TestCase):
    def test_generates_runtime_action_ids_for_model_tool_calls(self):
        tool_call = SimpleNamespace(
            id="call-1",
            function=SimpleNamespace(name="read_file", arguments='{"path": "notes.txt"}'),
        )

        call = act._normalize_tool_calls([tool_call])[0]

        self.assertEqual(call["id"], "call-1")
        self.assertEqual(call["name"], "read_file")
        self.assertEqual(len(call["action_id"]), 32)

    def test_rejection_discards_later_calls_from_the_same_model_turn(self):
        session = {
            "messages": [{"role": "assistant", "content": None, "tool_calls": []}],
            "pending_calls": [
                {"action_id": "action-1", "id": "call-1", "name": "run_shell", "args": {"command": "rm -rf scratch"}},
                {"action_id": "action-2", "id": "call-2", "name": "write_file", "args": {"path": "report.md", "content": "done"}},
            ],
            "tool_rounds": 1,
        }

        with patch("agent.capabilities.act.safety.log") as log:
            resolved = act.resolve_approval(session, {"approved": False})

        self.assertEqual(resolved["pending_calls"], [])
        self.assertEqual(resolved["messages"][-1], {
            "role": "tool",
            "tool_call_id": "call-1",
            "content": "用户拒绝执行该操作",
        })
        log.assert_called_once_with(
            "run_shell", {"command": "rm -rf scratch"}, "rejected_by_user", "action-1",
        )

    def test_records_safe_calls_before_later_approval_is_requested(self):
        session = {
            "messages": [],
            "pending_calls": [
                {"action_id": "action-1", "id": "call-1", "name": "read_file", "args": {"path": "notes.txt"}},
                {"action_id": "action-2", "id": "call-2", "name": "run_shell", "args": {"command": "rm -rf scratch"}},
            ],
            "tool_rounds": 1,
        }

        with (
            patch("agent.capabilities.act._tool_verdict", side_effect=[
                {"allowed": True},
                {"needs_approval": True, "reason": "危险命令模式: rm -rf"},
            ]),
            patch("agent.capabilities.act._execute_with_verdict", return_value={
                "content": [{"type": "text", "text": "contents"}],
                "structuredContent": {
                    "path": "notes.txt", "content": "contents", "truncated": False,
                },
                "isError": False,
            }),
        ):
            progress = act.advance(session)

        self.assertEqual(progress["status"], "approval_required")
        self.assertEqual(progress["proposal"]["action_id"], "action-2")
        self.assertEqual(progress["actions"], [{
            "action_id": "action-1",
            "tool": "read_file",
            "args": {"path": "notes.txt"},
            "status": "called",
        }])


if __name__ == "__main__":
    unittest.main()
