import json
from pathlib import Path
from tempfile import TemporaryDirectory
import unittest

from agent.agent_definition import AgentDefinition, load_agent_definition
from agent.capabilities.act import _tool_schemas


class AgentDefinitionTests(unittest.TestCase):
    def test_loads_default_definition(self):
        definition = load_agent_definition()

        self.assertEqual(definition.id, "general-assistant")
        self.assertIn("run_shell", definition.tools)
        self.assertIn("通用任务执行助手", definition.prompt_context())

    def test_rejects_unknown_tools(self):
        with TemporaryDirectory() as directory:
            root = Path(directory)
            definitions = root / "definitions"
            prompts = root / "prompts"
            definitions.mkdir()
            prompts.mkdir()
            (definitions / "test-agent.json").write_text(json.dumps({
                "id": "test-agent",
                "role": "tester",
                "goal": "test",
                "tools": ["unknown_tool"],
                "acceptance": ["finish"],
                "prompt": "test.md",
            }), encoding="utf-8")
            (prompts / "test.md").write_text("test prompt", encoding="utf-8")

            with self.assertRaisesRegex(ValueError, "unknown tools"):
                load_agent_definition(
                    "test-agent",
                    definitions_directory=definitions,
                    prompts_directory=prompts,
                    available_tools={"read_file"},
                )

    def test_tool_schemas_follow_the_definition_allowlist(self):
        definition = AgentDefinition(
            id="read-only",
            role="reader",
            goal="read",
            tools=("read_file",),
            acceptance=("finish",),
            instructions="read only",
        )

        self.assertEqual([schema["function"]["name"] for schema in _tool_schemas(definition)], ["read_file"])


if __name__ == "__main__":
    unittest.main()
