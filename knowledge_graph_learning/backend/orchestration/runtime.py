"""Controlled LangGraph runtime for the knowledge-graph learning workflow."""

from __future__ import annotations

from dataclasses import dataclass, replace
import json
from typing import Any, Callable, TypedDict
from uuid import uuid4

from langgraph.checkpoint.base import BaseCheckpointSaver
from langgraph.graph import END, START, StateGraph
from langgraph.types import Command, interrupt

from agent.core.models import CheckpointInfo, RunEvent, RunResult
from agent.infrastructure.checkpoints import (
    DEFAULT_CHECKPOINT_PATH,
    open_sqlite_checkpointer,
)
from agent.infrastructure.traces import TraceStore


RolePort = Callable[[dict[str, Any]], dict[str, Any]]
GraphUpdatePort = Callable[[dict[str, Any]], dict[str, Any]]


@dataclass(frozen=True)
class LearningRuntimeRoles:
    """Pure role ports injected into the controlled learning state graph."""

    graph_curator: RolePort
    learning_planner: RolePort
    tutor: RolePort
    evaluator: RolePort


@dataclass(frozen=True)
class LearningRuntimeTools:
    """Side-effect ports that the runtime may call only from guarded nodes."""

    apply_graph_update: GraphUpdatePort


class LearningAgentState(TypedDict):
    task: str
    request: dict[str, Any]
    graph_context: dict[str, Any]
    learning_plan: dict[str, Any]
    tutor_content: dict[str, Any]
    evaluation: dict[str, Any]
    graph_update_proposal: dict[str, Any]
    graph_update_decision: dict[str, Any]
    graph_update_result: dict[str, Any]
    outcome: str


class LearningAgentRuntime:
    """Run four learning roles with checkpointed human review and normalized traces."""

    def __init__(
        self,
        roles: LearningRuntimeRoles,
        tools: LearningRuntimeTools,
        trace_store: TraceStore | None = None,
        checkpointer: BaseCheckpointSaver | None = None,
        checkpoint_path: str | None = None,
    ):
        self.roles = roles
        self.tools = tools
        self.trace_store = trace_store or TraceStore()
        self._checkpoint_connection = None
        if checkpointer is None:
            self.checkpointer, self._checkpoint_connection = open_sqlite_checkpointer(
                checkpoint_path or DEFAULT_CHECKPOINT_PATH,
            )
        else:
            self.checkpointer = checkpointer
        self.graph = self._build_graph()

    def close(self) -> None:
        """Close the SQLite connection owned by this runtime, if any."""
        if self._checkpoint_connection is not None:
            self._checkpoint_connection.close()
            self._checkpoint_connection = None

    def run(self, request: dict[str, Any], thread_id: str | None = None) -> RunResult:
        """Start a learning-agent run from a JSON-like request."""
        run_id = uuid4().hex
        thread_id = thread_id or uuid4().hex
        task = self._task_label(request)
        if not isinstance(request, dict):
            return self._failed_result(
                run_id,
                task,
                thread_id,
                ValueError("INVALID_REQUEST: expected an object"),
            )
        events = [RunEvent(1, run_id, "run", "started", {
            "task": task,
            "thread_id": thread_id,
        })]
        config = self._config(thread_id)
        initial_state: LearningAgentState = {
            "task": task,
            "request": dict(request),
            "graph_context": {},
            "learning_plan": {},
            "tutor_content": {},
            "evaluation": {},
            "graph_update_proposal": {},
            "graph_update_decision": {},
            "graph_update_result": {},
            "outcome": "",
        }
        return self._execute_graph(
            task,
            run_id,
            thread_id,
            initial_state,
            config,
            events,
        )

    def resume(
        self,
        thread_id: str,
        decision: object,
        parent_run_id: str | None = None,
    ) -> RunResult:
        """Resume the latest human-review checkpoint with an approval decision."""
        run_id = uuid4().hex
        config = self._config(thread_id)
        try:
            snapshot = self.graph.get_state(config)
            checkpoint_id = snapshot.config.get("configurable", {}).get("checkpoint_id")
            task = snapshot.values.get("task")
            if not checkpoint_id or not task:
                raise ValueError(f"unknown or expired thread: {thread_id}")
        except Exception as error:
            return self._failed_result(
                run_id,
                "learning-agent-run",
                thread_id,
                error,
                parent_run_id=parent_run_id,
            )

        events = [RunEvent(1, run_id, "run", "resumed", {
            "thread_id": thread_id,
            "parent_run_id": parent_run_id,
            "recovered_from_checkpoint_id": checkpoint_id,
            "recovery_mode": "replay",
        })]
        return self._execute_graph(
            task,
            run_id,
            thread_id,
            Command(resume=decision),
            config,
            events,
            parent_run_id=parent_run_id,
            recovered_from_checkpoint_id=checkpoint_id,
            recovery_mode="replay",
        )

    def checkpoint_history(self, thread_id: str) -> tuple[CheckpointInfo, ...]:
        """Return framework checkpoints for one learning thread, newest first."""
        config = {"configurable": {"thread_id": thread_id}}
        history = []
        for snapshot in self.graph.get_state_history(config):
            checkpoint_id = snapshot.config.get("configurable", {}).get("checkpoint_id")
            if checkpoint_id:
                history.append(CheckpointInfo(checkpoint_id, tuple(snapshot.next)))
        return tuple(history)

    @staticmethod
    def _config(thread_id: str) -> dict[str, Any]:
        return {"configurable": {"thread_id": thread_id}, "recursion_limit": 20}

    @staticmethod
    def _task_label(request: object) -> str:
        if not isinstance(request, dict):
            return "learning-agent-run"
        for key in ("task", "goal_id", "concept_id"):
            value = request.get(key)
            if isinstance(value, str) and value:
                return value
        return "learning-agent-run"

    def _execute_graph(
        self,
        task: str,
        run_id: str,
        thread_id: str,
        graph_input: object,
        config: dict[str, Any],
        events: list[RunEvent],
        parent_run_id: str | None = None,
        recovered_from_checkpoint_id: str | None = None,
        recovery_mode: str | None = None,
    ) -> RunResult:
        interrupts: list[dict[str, Any]] = []
        try:
            for chunk in self.graph.stream(
                graph_input,
                config,
                stream_mode="updates",
                version="v2",
            ):
                if chunk["type"] != "updates":
                    continue
                for node_name, update in chunk["data"].items():
                    if node_name == "__interrupt__":
                        payload = self._interrupt_payload(update)
                        interrupts.extend(payload)
                        events.append(RunEvent(
                            len(events) + 1,
                            run_id,
                            "human_review",
                            "paused",
                            {"interrupts": payload},
                        ))
                        continue
                    events.append(RunEvent(
                        len(events) + 1,
                        run_id,
                        node_name,
                        "completed",
                        dict(update) if update else {},
                    ))

            if interrupts:
                return self._persist_trace(RunResult(
                    run_id,
                    task,
                    None,
                    tuple(events),
                    interrupts=tuple(interrupts),
                    thread_id=thread_id,
                    parent_run_id=parent_run_id,
                    recovered_from_checkpoint_id=recovered_from_checkpoint_id,
                    recovery_mode=recovery_mode,
                ))

            state = self.graph.get_state({"configurable": {"thread_id": thread_id}}).values
            outcome = state.get("outcome") or "completed"
        except Exception as error:
            message = self._error_message(error)
            events.append(RunEvent(
                len(events) + 1,
                run_id,
                "run",
                "failed",
                {"error": message},
            ))
            return self._persist_trace(RunResult(
                run_id,
                task,
                None,
                tuple(events),
                message,
                thread_id=thread_id,
                parent_run_id=parent_run_id,
                recovered_from_checkpoint_id=recovered_from_checkpoint_id,
                recovery_mode=recovery_mode,
            ))

        events.append(RunEvent(
            len(events) + 1,
            run_id,
            "run",
            "completed",
            {"outcome": outcome},
        ))
        return self._persist_trace(RunResult(
            run_id,
            task,
            outcome,
            tuple(events),
            thread_id=thread_id,
            parent_run_id=parent_run_id,
            recovered_from_checkpoint_id=recovered_from_checkpoint_id,
            recovery_mode=recovery_mode,
        ))

    def _failed_result(
        self,
        run_id: str,
        task: str,
        thread_id: str,
        error: Exception,
        parent_run_id: str | None = None,
    ) -> RunResult:
        message = self._error_message(error)
        event = RunEvent(1, run_id, "run", "failed", {"error": message})
        return self._persist_trace(RunResult(
            run_id,
            task,
            None,
            (event,),
            message,
            thread_id=thread_id,
            parent_run_id=parent_run_id,
        ))

    @staticmethod
    def _error_message(error: Exception) -> str:
        return str(error) or error.__class__.__name__

    @staticmethod
    def _interrupt_payload(update: object) -> list[dict[str, Any]]:
        return [{"id": item.id, "value": item.value} for item in update]

    def _persist_trace(self, result: RunResult) -> RunResult:
        try:
            self.trace_store.save(result)
        except Exception as error:
            message = self._error_message(error)
            return replace(result, warnings=result.warnings + (f"trace_persist_failed: {message}",))
        return result

    def _build_graph(self):
        builder = StateGraph(LearningAgentState)
        builder.add_node("graph_curator", self._graph_curator)
        builder.add_node("learning_planner", self._learning_planner)
        builder.add_node("tutor", self._tutor)
        builder.add_node("evaluator", self._evaluator)
        builder.add_node("human_review", self._human_review)
        builder.add_node("apply_graph_update", self._apply_graph_update)
        builder.add_node("complete", self._complete)

        builder.add_edge(START, "graph_curator")
        builder.add_edge("graph_curator", "learning_planner")
        builder.add_edge("learning_planner", "tutor")
        builder.add_edge("tutor", "evaluator")
        builder.add_conditional_edges("evaluator", self._after_evaluator, {
            "human_review": "human_review",
            "complete": "complete",
        })
        builder.add_conditional_edges("human_review", self._after_human_review, {
            "apply_graph_update": "apply_graph_update",
            "complete": "complete",
        })
        builder.add_edge("apply_graph_update", "complete")
        builder.add_edge("complete", END)
        return builder.compile(checkpointer=self.checkpointer)

    def _graph_curator(self, state: LearningAgentState) -> dict[str, Any]:
        output = self._role_output("graph_curator", self.roles.graph_curator, state)
        return {"graph_context": output}

    def _learning_planner(self, state: LearningAgentState) -> dict[str, Any]:
        output = self._role_output("learning_planner", self.roles.learning_planner, state)
        return {"learning_plan": output}

    def _tutor(self, state: LearningAgentState) -> dict[str, Any]:
        output = self._role_output("tutor", self.roles.tutor, state)
        return {"tutor_content": output}

    def _evaluator(self, state: LearningAgentState) -> dict[str, Any]:
        output = self._role_output("evaluator", self.roles.evaluator, state)
        proposal = output.get("graph_update_proposal")
        if proposal is not None and not isinstance(proposal, dict):
            raise ValueError("INVALID_ROLE_OUTPUT: evaluator graph_update_proposal must be an object")
        return {
            "evaluation": output,
            "graph_update_proposal": dict(proposal) if proposal else {},
        }

    @staticmethod
    def _role_output(
        role_name: str,
        role: RolePort,
        state: LearningAgentState,
    ) -> dict[str, Any]:
        output = role(dict(state))
        if not isinstance(output, dict):
            raise ValueError(f"INVALID_ROLE_OUTPUT: {role_name} must return an object")
        LearningAgentRuntime._require_json_value(
            output,
            f"INVALID_ROLE_OUTPUT: {role_name} must return a JSON-serializable object",
        )
        return dict(output)

    @staticmethod
    def _require_json_value(value: object, message: str) -> None:
        try:
            json.dumps(value, ensure_ascii=False)
        except (TypeError, ValueError) as error:
            raise ValueError(message) from error

    @staticmethod
    def _after_evaluator(state: LearningAgentState) -> str:
        return "human_review" if state["graph_update_proposal"] else "complete"

    @staticmethod
    def _human_review(state: LearningAgentState) -> dict[str, Any]:
        proposal = state["graph_update_proposal"]
        raw_decision = interrupt({
            "kind": "graph_update_confirmation",
            "proposal": proposal,
        })
        return {"graph_update_decision": LearningAgentRuntime._normalize_decision(raw_decision)}

    @staticmethod
    def _normalize_decision(decision: object) -> dict[str, bool]:
        if isinstance(decision, bool):
            return {"approved": decision}
        if isinstance(decision, dict) and isinstance(decision.get("approved"), bool):
            return {"approved": decision["approved"]}
        raise ValueError("INVALID_HUMAN_DECISION: expected bool or object with boolean approved")

    @staticmethod
    def _after_human_review(state: LearningAgentState) -> str:
        if state["graph_update_decision"].get("approved"):
            return "apply_graph_update"
        return "complete"

    def _apply_graph_update(self, state: LearningAgentState) -> dict[str, Any]:
        output = self.tools.apply_graph_update(dict(state["graph_update_proposal"]))
        if not isinstance(output, dict):
            raise ValueError("INVALID_TOOL_OUTPUT: apply_graph_update must return an object")
        self._require_json_value(
            output,
            "INVALID_TOOL_OUTPUT: apply_graph_update must return a JSON-serializable object",
        )
        return {"graph_update_result": dict(output)}

    @staticmethod
    def _complete(state: LearningAgentState) -> dict[str, str]:
        if state["graph_update_proposal"] and not state["graph_update_decision"].get("approved"):
            return {"outcome": "completed_without_graph_update"}
        return {"outcome": "completed"}
