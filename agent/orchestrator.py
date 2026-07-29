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

    def resume(self, thread_id: str, decision: object, parent_run_id: str | None = None) -> RunResult:
        """Resume a paused thread into a separately traced child run."""
        return self.runtime.resume(thread_id, decision, parent_run_id)

    def checkpoint_history(self, thread_id: str):
        """List checkpoints a caller may replay or fork from."""
        return self.runtime.checkpoint_history(thread_id)

    def recover(
        self,
        thread_id: str,
        checkpoint_id: str,
        state_patch: dict | None = None,
        parent_run_id: str | None = None,
    ) -> RunResult:
        """Replay a checkpoint, or fork when state_patch is explicitly supplied."""
        return self.runtime.recover(thread_id, checkpoint_id, state_patch, parent_run_id)
