"""Runtime-neutral result types exposed by the agent package."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any


ALLOWED_RECOVERY_STATE_PATCH_KEYS = frozenset({"steps"})


def validate_recovery_state_patch(state_patch: dict | None) -> None:
    """Permit only human plan corrections during a recovery fork."""
    if not state_patch:
        return
    disallowed = sorted(set(state_patch) - ALLOWED_RECOVERY_STATE_PATCH_KEYS)
    if disallowed:
        raise ValueError(f"recovery state patch cannot modify: {', '.join(disallowed)}")
    steps = state_patch.get("steps")
    if steps is not None and (
        not isinstance(steps, list) or not all(isinstance(step, str) for step in steps)
    ):
        raise ValueError("recovery state patch steps must be a list of strings")


@dataclass(frozen=True)
class RunEvent:
    """One normalized event produced by a runtime execution."""

    sequence: int
    run_id: str
    phase: str
    status: str
    payload: dict[str, Any] = field(default_factory=dict)


@dataclass(frozen=True)
class CheckpointInfo:
    """A selectable checkpoint in one LangGraph thread's history."""

    checkpoint_id: str
    next_nodes: tuple[str, ...]


@dataclass(frozen=True)
class RunResult:
    """Structured state for one agent execution, including approval pauses."""

    run_id: str
    task: str
    outcome: str | None
    events: tuple[RunEvent, ...]
    error: str | None = None
    warnings: tuple[str, ...] = ()
    interrupts: tuple[dict[str, Any], ...] = ()
    thread_id: str | None = None
    parent_run_id: str | None = None
    recovered_from_checkpoint_id: str | None = None
    recovery_mode: str | None = None

    @property
    def succeeded(self) -> bool:
        return self.error is None and not self.is_paused

    @property
    def is_paused(self) -> bool:
        return bool(self.interrupts)
