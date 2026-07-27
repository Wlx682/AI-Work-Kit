"""Executor：执行者 Agent。只按计划干活，看不到全局意图。"""

from ..capabilities import act
from .base import BaseAgent


class Executor(BaseAgent):
    name = "Executor"
    definition_id = "executor"

    def start_step(self, step: str, context: str = "") -> dict:
        """Create a checkpointable tool-use session for one assigned step."""
        return act.start_step(step, context)

    def advance_step(self, session: dict) -> dict:
        """Propose or run safe tool calls until approval or completion."""
        return act.advance(session, self.definition)

    def resolve_approval(self, session: dict, decision: object) -> dict:
        """Apply a decision to the exact proposal stored in graph state."""
        return act.resolve_approval(session, decision, self.definition)
