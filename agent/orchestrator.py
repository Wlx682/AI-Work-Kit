"""Single-agent entry point backed by the LangGraph runtime."""

from .langgraph_runtime import LangGraphRuntime
from .memory import Memory
from .runtime import RunResult


class Orchestrator:
    """Keeps the public agent API while delegating orchestration to LangGraph."""

    def __init__(self, memory: Memory, runtime: LangGraphRuntime | None = None):
        self.memory = memory
        self.runtime = runtime or LangGraphRuntime(memory)

    def run(self, task: str) -> str:
        """Keep the legacy text result API for existing callers."""
        result = self.run_with_trace(task)
        return result.outcome if result.succeeded else f"(执行失败: {result.error})"

    def run_with_trace(self, task: str) -> RunResult:
        """Execute the task through LangGraph and return normalized trace data."""
        return self.runtime.run(task)

    def resume(self, run_id: str, decision: object) -> RunResult:
        """Resume a paused tool approval for the same run."""
        return self.runtime.resume(run_id, decision)
