"""Runtime-neutral result types exposed by the agent package."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any


@dataclass(frozen=True)
class RunEvent:
    """One normalized event produced by a runtime execution."""

    sequence: int
    run_id: str
    phase: str
    status: str
    payload: dict[str, Any] = field(default_factory=dict)


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

    @property
    def succeeded(self) -> bool:
        return self.error is None and not self.is_paused

    @property
    def is_paused(self) -> bool:
        return bool(self.interrupts)
