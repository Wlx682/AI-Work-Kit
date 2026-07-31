"""Tests for MCP-style local tool results and outputSchema validation."""

import os
from tempfile import TemporaryDirectory
import unittest
from unittest.mock import patch

from agent.capabilities import act
from agent.tools import get_function, validate_tool_result


class ToolResultTests(unittest.TestCase):
    def test_all_local_tools_return_schema_valid_structured_content(self):
        with TemporaryDirectory() as directory:
            source = os.path.join(directory, "source.txt")
            target = os.path.join(directory, "target.txt")
            with open(source, "w", encoding="utf-8") as file:
                file.write("hello")

            results = {
                "read_file": get_function("read_file")(source),
                "write_file": get_function("write_file")(target, "written"),
                "list_directory": get_function("list_directory")(directory),
                "run_shell": get_function("run_shell")("printf protocol-ok"),
                "get_current_time": get_function("get_current_time")(),
            }

        for name, result in results.items():
            with self.subTest(name=name):
                self.assertFalse(result["isError"])
                self.assertIs(validate_tool_result(name, result), result)

    def test_explicit_tool_errors_keep_the_mcp_error_shape(self):
        result = get_function("read_file")("/definitely/missing/file.txt")

        self.assertTrue(result["isError"])
        self.assertNotIn("structuredContent", result)
        self.assertIs(validate_tool_result("read_file", result), result)

    def test_act_rejects_a_success_result_that_violates_output_schema(self):
        invalid_result = {
            "content": [{"type": "text", "text": "looks successful"}],
            "structuredContent": {"path": "notes.txt"},
            "isError": False,
        }
        with (
            patch("agent.capabilities.act.get_function", return_value=lambda **_: invalid_result),
            patch("agent.capabilities.act.safety.log") as log,
        ):
            result = act._execute_with_verdict(
                "read_file", {"path": "notes.txt"}, {"allowed": True}, "action-1",
            )

        self.assertTrue(result["isError"])
        self.assertIn("Error executing read_file", result["content"][0]["text"])
        log.assert_called_once_with("read_file", {"path": "notes.txt"}, "executed", "action-1")


if __name__ == "__main__":
    unittest.main()
