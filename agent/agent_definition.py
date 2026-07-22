"""Load and validate declarative Agent policy without owning runtime control flow."""

from __future__ import annotations

from dataclasses import dataclass
import json
from pathlib import Path
from typing import Iterable


DEFINITIONS_DIRECTORY = Path(__file__).parent / "definitions"
PROMPTS_DIRECTORY = Path(__file__).parent / "prompts"
REQUIRED_FIELDS = {"id", "role", "goal", "tools", "acceptance", "prompt"}


@dataclass(frozen=True)
class AgentDefinition:
    """Reviewed policy inputs consumed by an Agent runtime."""

    id: str
    role: str
    goal: str
    tools: tuple[str, ...]
    acceptance: tuple[str, ...]
    instructions: str

    def prompt_context(self) -> str:
        acceptance = "\n".join(f"- {item}" for item in self.acceptance)
        return (
            f"当前 Agent 定义：{self.id}\n"
            f"角色：{self.role}\n"
            f"目标：{self.goal}\n"
            f"验收标准：\n{acceptance}\n\n"
            f"角色说明：\n{self.instructions}"
        )


def load_agent_definition(
    definition_id: str = "general-assistant",
    *,
    definitions_directory: Path = DEFINITIONS_DIRECTORY,
    prompts_directory: Path = PROMPTS_DIRECTORY,
    available_tools: Iterable[str] | None = None,
) -> AgentDefinition:
    """Load a JSON policy plus its Markdown instructions into a typed definition."""
    _validate_filename(definition_id)
    path = definitions_directory / f"{definition_id}.json"
    try:
        document = json.loads(path.read_text(encoding="utf-8"))
    except FileNotFoundError as error:
        raise ValueError(f"agent definition not found: {definition_id}") from error
    except json.JSONDecodeError as error:
        raise ValueError(f"agent definition is not valid JSON: {definition_id}") from error

    if set(document) != REQUIRED_FIELDS:
        missing = sorted(REQUIRED_FIELDS - set(document))
        unknown = sorted(set(document) - REQUIRED_FIELDS)
        details = []
        if missing:
            details.append(f"missing={missing}")
        if unknown:
            details.append(f"unknown={unknown}")
        raise ValueError(f"invalid agent definition fields: {', '.join(details)}")

    identifier = _required_text(document, "id")
    if identifier != definition_id:
        raise ValueError(f"definition id does not match filename: {identifier}")
    prompt_name = _required_text(document, "prompt")
    _validate_filename(prompt_name, suffix=".md")
    tools = _string_list(document, "tools", allow_empty=True)
    acceptance = _string_list(document, "acceptance")
    permitted_tools = set(available_tools) if available_tools is not None else _registered_tools()
    unknown_tools = sorted(set(tools) - permitted_tools)
    if unknown_tools:
        raise ValueError(f"agent definition contains unknown tools: {unknown_tools}")

    try:
        instructions = (prompts_directory / prompt_name).read_text(encoding="utf-8").strip()
    except FileNotFoundError as error:
        raise ValueError(f"agent prompt not found: {prompt_name}") from error
    if not instructions:
        raise ValueError(f"agent prompt is empty: {prompt_name}")

    return AgentDefinition(
        id=identifier,
        role=_required_text(document, "role"),
        goal=_required_text(document, "goal"),
        tools=tools,
        acceptance=acceptance,
        instructions=instructions,
    )


def _registered_tools() -> set[str]:
    from .tools import list_tools

    return set(list_tools())


def _required_text(document: dict, field: str) -> str:
    value = document.get(field)
    if not isinstance(value, str) or not value.strip():
        raise ValueError(f"agent definition field '{field}' must be non-empty text")
    return value.strip()


def _string_list(document: dict, field: str, *, allow_empty: bool = False) -> tuple[str, ...]:
    value = document.get(field)
    if not isinstance(value, list) or (not allow_empty and not value) or any(not isinstance(item, str) or not item.strip() for item in value):
        requirement = "a string list" if allow_empty else "a non-empty string list"
        raise ValueError(f"agent definition field '{field}' must be {requirement}")
    return tuple(item.strip() for item in value)


def _validate_filename(value: str, suffix: str = "") -> None:
    if not value or Path(value).name != value or (suffix and not value.endswith(suffix)):
        raise ValueError("agent definition paths must be simple filenames")
