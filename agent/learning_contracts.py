"""Contracts for the knowledge-graph learning loop."""

import json
from dataclasses import dataclass
from pathlib import Path

from .runtime import RunEvent, RunResult


@dataclass(frozen=True)
class LearningGoal:
    id: str
    title: str


@dataclass(frozen=True)
class Course:
    id: str
    goal_id: str
    title: str
    node_ids: tuple[str, ...]


@dataclass(frozen=True)
class ConceptNode:
    id: str
    course_id: str
    title: str


@dataclass(frozen=True)
class DependencyEdge:
    source_node_id: str
    target_node_id: str
    relation: str


@dataclass(frozen=True)
class CourseGraph:
    course: Course
    nodes: tuple[ConceptNode, ...]
    dependency_edges: tuple[DependencyEdge, ...] = ()


@dataclass(frozen=True)
class LearningSession:
    id: str
    goal_id: str
    course_id: str
    node_id: str
    status: str


@dataclass(frozen=True)
class Evidence:
    id: str
    session_id: str
    node_id: str
    kind: str
    content_ref: str


@dataclass(frozen=True)
class EvalResult:
    id: str
    evidence_id: str
    node_id: str
    passed: bool
    score: float
    reason: str


@dataclass(frozen=True)
class NodeProgress:
    node_id: str
    percent: int
    mastery_state: str


@dataclass(frozen=True)
class NextLearningNode:
    course_id: str
    node_id: str
    prerequisite_node_ids: tuple[str, ...]
    reason: str


@dataclass(frozen=True)
class TerminalStatus:
    run_id: str
    status: str
    reason: str
    recoverable: bool
    next_action: str


@dataclass(frozen=True)
class LearningLoopReplayRegressionSummary:
    run_id: str
    terminal_status: str
    completion_reason: str
    graph_replay_completed: bool
    replayed_request_count: int
    replayed_proposal_count: int
    replayed_confirmation_count: int
    replayed_applied_count: int
    trace_matches_contract: bool
    final_learning_completed: bool
    remaining_selectable_nodes: int
    regression_passed: bool
    report: str


@dataclass(frozen=True)
class GoldenLearningTask:
    id: str
    title: str
    goal_id: str
    course_id: str
    expected_terminal_status: str
    expected_completion_reason: str
    expected_graph_operation_count: int
    expected_remaining_selectable_nodes: int


@dataclass(frozen=True)
class GoldenLearningTaskReport:
    task_id: str
    task_title: str
    goal_id: str
    course_id: str
    run_id: str
    expected_terminal_status: str
    actual_terminal_status: str
    expected_completion_reason: str
    actual_completion_reason: str
    expected_graph_operation_count: int
    actual_graph_operation_count: int
    expected_remaining_selectable_nodes: int
    actual_remaining_selectable_nodes: int
    trace_matches_contract: bool
    graph_replay_completed: bool
    regression_passed: bool
    report: str


@dataclass(frozen=True)
class GoldenLearningTaskBatchReport:
    suite_id: str
    total_count: int
    passed_count: int
    failed_count: int
    failed_task_ids: tuple[str, ...]
    regression_passed: bool
    reports: tuple[GoldenLearningTaskReport, ...]
    report: str


@dataclass(frozen=True)
class GoldenLearningTaskRun:
    task: GoldenLearningTask
    result: RunResult
    replay: "GraphOperationReplay"


@dataclass(frozen=True)
class GoldenLearningTaskRunReference:
    task_id: str
    run_id: str


@dataclass(frozen=True)
class GraphOperationRequest:
    id: str
    course_id: str
    node_id: str
    operation_type: str
    user_intent: str
    source: str
    target_node_ids: tuple[str, ...] = ()
    context_refs: tuple[str, ...] = ()
    status: str = "created"


@dataclass(frozen=True)
class GraphOperationProposal:
    id: str
    request_id: str
    operation_type: str
    summary: str
    rationale: str
    affected_nodes: tuple[str, ...] = ()
    proposed_nodes: tuple[str, ...] = ()
    proposed_edges: tuple[tuple[str, str], ...] = ()
    progress_migration: str = ""
    risks: tuple[str, ...] = ()
    requires_confirmation: bool = True


@dataclass(frozen=True)
class AppliedGraphOperation:
    proposal_id: str
    request_id: str
    operation_type: str
    status: str
    applied_nodes: tuple[str, ...]


@dataclass(frozen=True)
class GraphOperationConfirmation:
    proposal_id: str
    request_id: str
    confirmed_by: str
    changes_requested: tuple[str, ...] = ()
    status: str = "confirmed"


@dataclass(frozen=True)
class GraphOperationReplay:
    requests: tuple[GraphOperationRequest, ...] = ()
    proposals: tuple[GraphOperationProposal, ...] = ()
    confirmations: tuple[GraphOperationConfirmation, ...] = ()
    applied_operations: tuple[AppliedGraphOperation, ...] = ()


@dataclass(frozen=True)
class CreateLearningGoalInput:
    goal: LearningGoal
    run_id: str
    sequence: int


@dataclass(frozen=True)
class InitializeCourseGraphInput:
    goal: LearningGoal
    course: Course
    nodes: tuple[ConceptNode, ...]
    run_id: str
    sequence: int
    dependency_edges: tuple[DependencyEdge, ...] = ()


@dataclass(frozen=True)
class StartNodeLearningInput:
    goal: LearningGoal
    course: Course
    node: ConceptNode
    session_id: str
    run_id: str
    sequence: int


@dataclass(frozen=True)
class SubmitEvidenceInput:
    session: LearningSession
    evidence: Evidence
    run_id: str
    sequence: int


@dataclass(frozen=True)
class SubmitEvalProgressInput:
    evidence: Evidence
    eval_result: EvalResult
    previous_percent: int
    run_id: str
    sequence: int


@dataclass(frozen=True)
class RecomputeParentProgressInput:
    node_id: str
    children: tuple[NodeProgress, ...]
    previous_percent: int
    run_id: str
    sequence: int


@dataclass(frozen=True)
class SelectNextLearningNodeInput:
    course_id: str
    run_id: str
    sequence: int


@dataclass(frozen=True)
class CompleteAgentRunInput:
    run_id: str
    sequence: int
    status: str
    reason: str
    recoverable: bool
    next_action: str


@dataclass(frozen=True)
class CreateGraphOperationRequestInput:
    request_id: str
    course_id: str
    node_id: str
    operation_type: str
    user_intent: str
    source: str
    run_id: str
    sequence: int
    target_node_ids: tuple[str, ...] = ()
    context_refs: tuple[str, ...] = ()


@dataclass(frozen=True)
class ProposeGraphOperationInput:
    request: GraphOperationRequest
    proposal_id: str
    summary: str
    rationale: str
    proposed_nodes: tuple[str, ...]
    run_id: str
    sequence: int
    proposed_edges: tuple[tuple[str, str], ...] = ()
    progress_migration: str = ""
    risks: tuple[str, ...] = ()
    affected_nodes: tuple[str, ...] | None = None
    requires_confirmation: bool = True


@dataclass(frozen=True)
class ConfirmGraphOperationInput:
    proposal: GraphOperationProposal
    confirmed_by: str
    run_id: str
    sequence: int
    changes_requested: tuple[str, ...] = ()


@dataclass(frozen=True)
class ApplyGraphOperationInput:
    proposal: GraphOperationProposal
    run_id: str
    sequence: int
    confirmed_by: str | None = None
    confirmation: GraphOperationConfirmation | None = None


@dataclass(frozen=True)
class ContractApiResult:
    ok: bool
    value: object | None
    error_code: str | None = None
    error_message: str | None = None


class LearningRecordNotFound(Exception):
    error_code = "LEARNING_RECORD_NOT_FOUND"

    def __init__(self, collection: str, item_id: str):
        self.collection = collection
        self.item_id = item_id
        super().__init__(f"{collection}/{item_id} not found")


class LearningRepositoryDataCorrupted(Exception):
    error_code = "LEARNING_REPOSITORY_DATA_CORRUPTED"

    def __init__(self, collection: str, item_id: str):
        self.collection = collection
        self.item_id = item_id
        super().__init__(f"{collection}/{item_id} has corrupted repository data")


class LearningRepositoryJsonFieldMissing(Exception):
    error_code = "LEARNING_REPOSITORY_JSON_FIELD_MISSING"

    def __init__(self, collection: str, item_id: str, field: str):
        self.collection = collection
        self.item_id = item_id
        self.field = field
        super().__init__(f"{collection}/{item_id} missing required JSON field: {field}")


def repository_operation_api(operation) -> ContractApiResult:
    try:
        return ContractApiResult(ok=True, value=operation())
    except (
        LearningRecordNotFound,
        LearningRepositoryDataCorrupted,
        LearningRepositoryJsonFieldMissing,
    ) as error:
        return ContractApiResult(
            ok=False,
            value=None,
            error_code=error.error_code,
            error_message=str(error),
        )
    except OSError as error:
        return ContractApiResult(
            ok=False,
            value=None,
            error_code="LEARNING_REPOSITORY_IO_ERROR",
            error_message=str(error),
        )


class JsonLearningRepository:
    def __init__(self, directory: str):
        self.directory = Path(directory)
        self.directory.mkdir(parents=True, exist_ok=True)

    def save_goal(self, goal: LearningGoal) -> None:
        self._write(
            "goals",
            goal.id,
            {
                "id": goal.id,
                "title": goal.title,
            },
        )

    def load_goal(self, goal_id: str) -> LearningGoal:
        data = self._read("goals", goal_id)
        self._ensure_fields(data, "goals", goal_id, ("id", "title"))
        return LearningGoal(
            id=data["id"],
            title=data["title"],
        )

    def save_course(self, course: Course) -> None:
        self._write(
            "courses",
            course.id,
            {
                "id": course.id,
                "goal_id": course.goal_id,
                "title": course.title,
                "node_ids": list(course.node_ids),
            },
        )

    def load_course(self, course_id: str) -> Course:
        data = self._read("courses", course_id)
        self._ensure_fields(data, "courses", course_id, ("id", "goal_id", "title", "node_ids"))
        return Course(
            id=data["id"],
            goal_id=data["goal_id"],
            title=data["title"],
            node_ids=tuple(data["node_ids"]),
        )

    def save_node(self, node: ConceptNode) -> None:
        self._write(
            "nodes",
            node.id,
            {
                "id": node.id,
                "course_id": node.course_id,
                "title": node.title,
            },
        )

    def load_node(self, node_id: str) -> ConceptNode:
        data = self._read("nodes", node_id)
        self._ensure_fields(data, "nodes", node_id, ("id", "course_id", "title"))
        return ConceptNode(
            id=data["id"],
            course_id=data["course_id"],
            title=data["title"],
        )

    def save_dependency_edges(self, course_id: str, edges: tuple[DependencyEdge, ...]) -> None:
        self._write(
            "dependency_edges",
            course_id,
            {
                "course_id": course_id,
                "edges": [
                    {
                        "source_node_id": edge.source_node_id,
                        "target_node_id": edge.target_node_id,
                        "relation": edge.relation,
                    }
                    for edge in edges
                ],
            },
        )

    def load_dependency_edges(self, course_id: str) -> tuple[DependencyEdge, ...]:
        data = self._read("dependency_edges", course_id)
        self._ensure_fields(data, "dependency_edges", course_id, ("course_id", "edges"))
        return tuple(
            DependencyEdge(
                source_node_id=edge["source_node_id"],
                target_node_id=edge["target_node_id"],
                relation=edge["relation"],
            )
            for edge in data["edges"]
        )

    def save_course_graph(self, graph: CourseGraph) -> None:
        self.save_course(graph.course)
        for node in graph.nodes:
            self.save_node(node)
        self.save_dependency_edges(graph.course.id, graph.dependency_edges)

    def load_course_graph(self, course_id: str) -> CourseGraph:
        course = self.load_course(course_id)
        return CourseGraph(
            course=course,
            nodes=tuple(self.load_node(node_id) for node_id in course.node_ids),
            dependency_edges=self.load_dependency_edges(course.id),
        )

    def save_session(self, session: LearningSession) -> None:
        self._write(
            "sessions",
            session.id,
            {
                "id": session.id,
                "goal_id": session.goal_id,
                "course_id": session.course_id,
                "node_id": session.node_id,
                "status": session.status,
            },
        )

    def load_session(self, session_id: str) -> LearningSession:
        data = self._read("sessions", session_id)
        self._ensure_fields(data, "sessions", session_id, ("id", "goal_id", "course_id", "node_id", "status"))
        return LearningSession(
            id=data["id"],
            goal_id=data["goal_id"],
            course_id=data["course_id"],
            node_id=data["node_id"],
            status=data["status"],
        )

    def save_evidence(self, evidence: Evidence) -> None:
        self._write(
            "evidence",
            evidence.id,
            {
                "id": evidence.id,
                "session_id": evidence.session_id,
                "node_id": evidence.node_id,
                "kind": evidence.kind,
                "content_ref": evidence.content_ref,
            },
        )

    def load_evidence(self, evidence_id: str) -> Evidence:
        data = self._read("evidence", evidence_id)
        self._ensure_fields(data, "evidence", evidence_id, ("id", "session_id", "node_id", "kind", "content_ref"))
        return Evidence(
            id=data["id"],
            session_id=data["session_id"],
            node_id=data["node_id"],
            kind=data["kind"],
            content_ref=data["content_ref"],
        )

    def save_eval_result(self, eval_result: EvalResult) -> None:
        self._write(
            "eval_results",
            eval_result.id,
            {
                "id": eval_result.id,
                "evidence_id": eval_result.evidence_id,
                "node_id": eval_result.node_id,
                "passed": eval_result.passed,
                "score": eval_result.score,
                "reason": eval_result.reason,
            },
        )

    def load_eval_result(self, eval_result_id: str) -> EvalResult:
        data = self._read("eval_results", eval_result_id)
        self._ensure_fields(
            data,
            "eval_results",
            eval_result_id,
            ("id", "evidence_id", "node_id", "passed", "score", "reason"),
        )
        return EvalResult(
            id=data["id"],
            evidence_id=data["evidence_id"],
            node_id=data["node_id"],
            passed=data["passed"],
            score=data["score"],
            reason=data["reason"],
        )

    def save_progress(self, progress: NodeProgress) -> None:
        self._write(
            "progress",
            progress.node_id,
            {
                "node_id": progress.node_id,
                "percent": progress.percent,
                "mastery_state": progress.mastery_state,
            },
        )

    def load_progress(self, node_id: str) -> NodeProgress:
        data = self._read("progress", node_id)
        self._ensure_fields(data, "progress", node_id, ("node_id", "percent", "mastery_state"))
        return NodeProgress(
            node_id=data["node_id"],
            percent=data["percent"],
            mastery_state=data["mastery_state"],
        )

    def save_graph_operation_request(self, request: GraphOperationRequest) -> None:
        self._write(
            "graph_operation_requests",
            request.id,
            {
                "id": request.id,
                "course_id": request.course_id,
                "node_id": request.node_id,
                "operation_type": request.operation_type,
                "user_intent": request.user_intent,
                "source": request.source,
                "target_node_ids": list(request.target_node_ids),
                "context_refs": list(request.context_refs),
                "status": request.status,
            },
        )

    def load_graph_operation_request(self, request_id: str) -> GraphOperationRequest:
        data = self._read("graph_operation_requests", request_id)
        self._ensure_fields(
            data,
            "graph_operation_requests",
            request_id,
            (
                "id",
                "course_id",
                "node_id",
                "operation_type",
                "user_intent",
                "source",
                "target_node_ids",
                "context_refs",
                "status",
            ),
        )
        return GraphOperationRequest(
            id=data["id"],
            course_id=data["course_id"],
            node_id=data["node_id"],
            operation_type=data["operation_type"],
            user_intent=data["user_intent"],
            source=data["source"],
            target_node_ids=tuple(data["target_node_ids"]),
            context_refs=tuple(data["context_refs"]),
            status=data["status"],
        )

    def save_graph_operation_proposal(self, proposal: GraphOperationProposal) -> None:
        self._write(
            "graph_operation_proposals",
            proposal.id,
            {
                "id": proposal.id,
                "request_id": proposal.request_id,
                "operation_type": proposal.operation_type,
                "summary": proposal.summary,
                "rationale": proposal.rationale,
                "affected_nodes": list(proposal.affected_nodes),
                "proposed_nodes": list(proposal.proposed_nodes),
                "proposed_edges": [list(edge) for edge in proposal.proposed_edges],
                "progress_migration": proposal.progress_migration,
                "risks": list(proposal.risks),
                "requires_confirmation": proposal.requires_confirmation,
            },
        )

    def load_graph_operation_proposal(self, proposal_id: str) -> GraphOperationProposal:
        data = self._read("graph_operation_proposals", proposal_id)
        self._ensure_fields(
            data,
            "graph_operation_proposals",
            proposal_id,
            (
                "id",
                "request_id",
                "operation_type",
                "summary",
                "rationale",
                "affected_nodes",
                "proposed_nodes",
                "proposed_edges",
                "progress_migration",
                "risks",
                "requires_confirmation",
            ),
        )
        return GraphOperationProposal(
            id=data["id"],
            request_id=data["request_id"],
            operation_type=data["operation_type"],
            summary=data["summary"],
            rationale=data["rationale"],
            affected_nodes=tuple(data["affected_nodes"]),
            proposed_nodes=tuple(data["proposed_nodes"]),
            proposed_edges=tuple(tuple(edge) for edge in data["proposed_edges"]),
            progress_migration=data["progress_migration"],
            risks=tuple(data["risks"]),
            requires_confirmation=data["requires_confirmation"],
        )

    def save_graph_operation_confirmation(self, confirmation: GraphOperationConfirmation) -> None:
        self._write(
            "graph_operation_confirmations",
            confirmation.proposal_id,
            {
                "proposal_id": confirmation.proposal_id,
                "request_id": confirmation.request_id,
                "confirmed_by": confirmation.confirmed_by,
                "changes_requested": list(confirmation.changes_requested),
                "status": confirmation.status,
            },
        )

    def load_graph_operation_confirmation(self, proposal_id: str) -> GraphOperationConfirmation:
        data = self._read("graph_operation_confirmations", proposal_id)
        self._ensure_fields(
            data,
            "graph_operation_confirmations",
            proposal_id,
            ("proposal_id", "request_id", "confirmed_by", "changes_requested", "status"),
        )
        return GraphOperationConfirmation(
            proposal_id=data["proposal_id"],
            request_id=data["request_id"],
            confirmed_by=data["confirmed_by"],
            changes_requested=tuple(data["changes_requested"]),
            status=data["status"],
        )

    def save_applied_graph_operation(self, applied: AppliedGraphOperation) -> None:
        self._write(
            "graph_operation_applied",
            applied.proposal_id,
            {
                "proposal_id": applied.proposal_id,
                "request_id": applied.request_id,
                "operation_type": applied.operation_type,
                "status": applied.status,
                "applied_nodes": list(applied.applied_nodes),
            },
        )

    def load_applied_graph_operation(self, proposal_id: str) -> AppliedGraphOperation:
        data = self._read("graph_operation_applied", proposal_id)
        self._ensure_fields(
            data,
            "graph_operation_applied",
            proposal_id,
            ("proposal_id", "request_id", "operation_type", "status", "applied_nodes"),
        )
        return AppliedGraphOperation(
            proposal_id=data["proposal_id"],
            request_id=data["request_id"],
            operation_type=data["operation_type"],
            status=data["status"],
            applied_nodes=tuple(data["applied_nodes"]),
        )

    def save_golden_learning_task(self, task: GoldenLearningTask) -> None:
        self._write(
            "golden_learning_tasks",
            task.id,
            {
                "id": task.id,
                "title": task.title,
                "goal_id": task.goal_id,
                "course_id": task.course_id,
                "expected_terminal_status": task.expected_terminal_status,
                "expected_completion_reason": task.expected_completion_reason,
                "expected_graph_operation_count": task.expected_graph_operation_count,
                "expected_remaining_selectable_nodes": task.expected_remaining_selectable_nodes,
            },
        )

    def load_golden_learning_task(self, task_id: str) -> GoldenLearningTask:
        data = self._read("golden_learning_tasks", task_id)
        self._ensure_fields(
            data,
            "golden_learning_tasks",
            task_id,
            (
                "id",
                "title",
                "goal_id",
                "course_id",
                "expected_terminal_status",
                "expected_completion_reason",
                "expected_graph_operation_count",
                "expected_remaining_selectable_nodes",
            ),
        )
        return GoldenLearningTask(
            id=data["id"],
            title=data["title"],
            goal_id=data["goal_id"],
            course_id=data["course_id"],
            expected_terminal_status=data["expected_terminal_status"],
            expected_completion_reason=data["expected_completion_reason"],
            expected_graph_operation_count=data["expected_graph_operation_count"],
            expected_remaining_selectable_nodes=data["expected_remaining_selectable_nodes"],
        )

    def save_golden_learning_task_report(self, report: GoldenLearningTaskReport) -> None:
        self._write(
            "golden_learning_task_reports",
            self._golden_learning_task_report_id(report.task_id, report.run_id),
            {
                "task_id": report.task_id,
                "task_title": report.task_title,
                "goal_id": report.goal_id,
                "course_id": report.course_id,
                "run_id": report.run_id,
                "expected_terminal_status": report.expected_terminal_status,
                "actual_terminal_status": report.actual_terminal_status,
                "expected_completion_reason": report.expected_completion_reason,
                "actual_completion_reason": report.actual_completion_reason,
                "expected_graph_operation_count": report.expected_graph_operation_count,
                "actual_graph_operation_count": report.actual_graph_operation_count,
                "expected_remaining_selectable_nodes": report.expected_remaining_selectable_nodes,
                "actual_remaining_selectable_nodes": report.actual_remaining_selectable_nodes,
                "trace_matches_contract": report.trace_matches_contract,
                "graph_replay_completed": report.graph_replay_completed,
                "regression_passed": report.regression_passed,
                "report": report.report,
            },
        )

    def load_golden_learning_task_report(self, task_id: str, run_id: str) -> GoldenLearningTaskReport:
        item_id = self._golden_learning_task_report_id(task_id, run_id)
        data = self._read("golden_learning_task_reports", item_id)
        self._ensure_fields(
            data,
            "golden_learning_task_reports",
            item_id,
            (
                "task_id",
                "task_title",
                "goal_id",
                "course_id",
                "run_id",
                "expected_terminal_status",
                "actual_terminal_status",
                "expected_completion_reason",
                "actual_completion_reason",
                "expected_graph_operation_count",
                "actual_graph_operation_count",
                "expected_remaining_selectable_nodes",
                "actual_remaining_selectable_nodes",
                "trace_matches_contract",
                "graph_replay_completed",
                "regression_passed",
                "report",
            ),
        )
        return GoldenLearningTaskReport(
            task_id=data["task_id"],
            task_title=data["task_title"],
            goal_id=data["goal_id"],
            course_id=data["course_id"],
            run_id=data["run_id"],
            expected_terminal_status=data["expected_terminal_status"],
            actual_terminal_status=data["actual_terminal_status"],
            expected_completion_reason=data["expected_completion_reason"],
            actual_completion_reason=data["actual_completion_reason"],
            expected_graph_operation_count=data["expected_graph_operation_count"],
            actual_graph_operation_count=data["actual_graph_operation_count"],
            expected_remaining_selectable_nodes=data["expected_remaining_selectable_nodes"],
            actual_remaining_selectable_nodes=data["actual_remaining_selectable_nodes"],
            trace_matches_contract=data["trace_matches_contract"],
            graph_replay_completed=data["graph_replay_completed"],
            regression_passed=data["regression_passed"],
            report=data["report"],
        )

    def save_golden_learning_task_batch_report(self, batch_report: GoldenLearningTaskBatchReport) -> None:
        self._write(
            "golden_learning_task_batch_reports",
            batch_report.suite_id,
            {
                "suite_id": batch_report.suite_id,
                "total_count": batch_report.total_count,
                "passed_count": batch_report.passed_count,
                "failed_count": batch_report.failed_count,
                "failed_task_ids": list(batch_report.failed_task_ids),
                "regression_passed": batch_report.regression_passed,
                "reports": [report.__dict__ for report in batch_report.reports],
                "report": batch_report.report,
            },
        )

    def load_golden_learning_task_batch_report(self, suite_id: str) -> GoldenLearningTaskBatchReport:
        data = self._read("golden_learning_task_batch_reports", suite_id)
        self._ensure_fields(
            data,
            "golden_learning_task_batch_reports",
            suite_id,
            (
                "suite_id",
                "total_count",
                "passed_count",
                "failed_count",
                "failed_task_ids",
                "regression_passed",
                "reports",
                "report",
            ),
        )
        return GoldenLearningTaskBatchReport(
            suite_id=data["suite_id"],
            total_count=data["total_count"],
            passed_count=data["passed_count"],
            failed_count=data["failed_count"],
            failed_task_ids=tuple(data["failed_task_ids"]),
            regression_passed=data["regression_passed"],
            reports=tuple(GoldenLearningTaskReport(**report) for report in data["reports"]),
            report=data["report"],
        )

    @staticmethod
    def _golden_learning_task_report_id(task_id: str, run_id: str) -> str:
        return f"{task_id}__{run_id}"

    def _write(self, collection: str, item_id: str, data: dict[str, object]) -> None:
        path = self.directory / collection
        path.mkdir(exist_ok=True)
        (path / f"{item_id}.json").write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")

    def _read(self, collection: str, item_id: str) -> dict[str, object]:
        try:
            data = json.loads((self.directory / collection / f"{item_id}.json").read_text(encoding="utf-8"))
        except FileNotFoundError as error:
            raise LearningRecordNotFound(collection, item_id) from error
        except json.JSONDecodeError as error:
            raise LearningRepositoryDataCorrupted(collection, item_id) from error
        if not isinstance(data, dict):
            raise LearningRepositoryDataCorrupted(collection, item_id)
        return data

    def _ensure_fields(
        self,
        data: dict[str, object],
        collection: str,
        item_id: str,
        fields: tuple[str, ...],
    ) -> None:
        for field in fields:
            if field not in data:
                raise LearningRepositoryJsonFieldMissing(collection, item_id, field)


LEARNING_LOOP_EVENT_TYPES = (
    "goal_created",
    "course_graph_created",
    "node_learning_started",
    "evidence_submitted",
    "progress_updated",
    "node_progress_recomputed",
    "graph_operation_requested",
    "graph_operation_proposed",
    "graph_operation_confirmed",
    "graph_update_applied",
    "node_selected",
    "node_learning_started",
    "evidence_submitted",
    "progress_updated",
    "node_progress_recomputed",
    "node_selected",
    "node_learning_started",
    "evidence_submitted",
    "progress_updated",
    "node_progress_recomputed",
    "run_completed",
)


def create_learning_goal(
    goal: LearningGoal,
    *,
    run_id: str,
    sequence: int,
) -> tuple[LearningGoal, RunEvent]:
    event = RunEvent(
        sequence=sequence,
        run_id=run_id,
        phase="goal",
        status="created",
        payload={
            "event_type": "goal_created",
            "goal_id": goal.id,
            "title": goal.title,
        },
    )
    return goal, event


def create_learning_goal_api(
    request: CreateLearningGoalInput,
    repository: JsonLearningRepository,
) -> ContractApiResult:
    goal, event = create_learning_goal(
        request.goal,
        run_id=request.run_id,
        sequence=request.sequence,
    )
    return repository_operation_api(lambda: _save_goal_and_return(repository, goal, event))


def _save_goal_and_return(
    repository: JsonLearningRepository,
    goal: LearningGoal,
    event: RunEvent,
) -> tuple[LearningGoal, RunEvent]:
    repository.save_goal(goal)
    return goal, event


def initialize_course_graph(
    goal: LearningGoal,
    course: Course,
    nodes: tuple[ConceptNode, ...],
    *,
    dependency_edges: tuple[DependencyEdge, ...] = (),
    run_id: str,
    sequence: int,
) -> tuple[CourseGraph, RunEvent]:
    if course.goal_id != goal.id:
        raise ValueError("course must belong to learning goal")
    node_ids = tuple(node.id for node in nodes)
    if node_ids != course.node_ids or any(node.course_id != course.id for node in nodes):
        raise ValueError("nodes must match course graph")
    node_id_set = set(course.node_ids)
    if any(edge.source_node_id not in node_id_set or edge.target_node_id not in node_id_set for edge in dependency_edges):
        raise ValueError("nodes must match course graph")
    graph = CourseGraph(
        course=course,
        nodes=nodes,
        dependency_edges=dependency_edges,
    )
    event = RunEvent(
        sequence=sequence,
        run_id=run_id,
        phase="course_graph",
        status="created",
        payload={
            "event_type": "course_graph_created",
            "goal_id": goal.id,
            "course_id": course.id,
            "node_ids": course.node_ids,
            "dependency_edges": tuple(
                (edge.source_node_id, edge.target_node_id, edge.relation)
                for edge in dependency_edges
            ),
        },
    )
    return graph, event


def initialize_course_graph_api(
    request: InitializeCourseGraphInput,
    repository: JsonLearningRepository,
) -> ContractApiResult:
    try:
        graph, event = initialize_course_graph(
            request.goal,
            request.course,
            request.nodes,
            dependency_edges=request.dependency_edges,
            run_id=request.run_id,
            sequence=request.sequence,
        )
    except ValueError as error:
        message = str(error)
        if message == "course must belong to learning goal":
            error_code = "COURSE_GOAL_MISMATCH"
        elif message == "nodes must match course graph":
            error_code = "NODE_NOT_IN_COURSE_GRAPH"
        else:
            raise
        return ContractApiResult(
            ok=False,
            value=None,
            error_code=error_code,
            error_message=message,
        )
    return repository_operation_api(lambda: _save_course_graph_and_return(repository, graph, event))


def _save_course_graph_and_return(
    repository: JsonLearningRepository,
    graph: CourseGraph,
    event: RunEvent,
) -> tuple[CourseGraph, RunEvent]:
    repository.save_course_graph(graph)
    return graph, event


def start_node_learning(
    goal: LearningGoal,
    course: Course,
    node: ConceptNode,
    *,
    session_id: str,
    run_id: str,
    sequence: int,
) -> tuple[LearningSession, RunEvent]:
    if course.goal_id != goal.id:
        raise ValueError("course must belong to learning goal")
    if node.course_id != course.id or node.id not in course.node_ids:
        raise ValueError("node must belong to course graph")
    session = LearningSession(
        id=session_id,
        goal_id=goal.id,
        course_id=course.id,
        node_id=node.id,
        status="learning",
    )
    event = RunEvent(
        sequence=sequence,
        run_id=run_id,
        phase="node_learning",
        status="started",
        payload={
            "event_type": "node_learning_started",
            "goal_id": goal.id,
            "course_id": course.id,
            "node_id": node.id,
            "session_id": session_id,
        },
    )
    return session, event


def start_node_learning_api(
    request: StartNodeLearningInput,
    repository: JsonLearningRepository | None = None,
) -> ContractApiResult:
    try:
        value = start_node_learning(
            request.goal,
            request.course,
            request.node,
            session_id=request.session_id,
            run_id=request.run_id,
            sequence=request.sequence,
        )
    except ValueError as error:
        message = str(error)
        if message == "course must belong to learning goal":
            return ContractApiResult(
                ok=False,
                value=None,
                error_code="COURSE_GOAL_MISMATCH",
                error_message=message,
            )
        if message == "node must belong to course graph":
            return ContractApiResult(
                ok=False,
                value=None,
                error_code="NODE_NOT_IN_COURSE_GRAPH",
                error_message=message,
            )
        raise
    if repository is None:
        return ContractApiResult(ok=True, value=value)
    session, event = value
    return repository_operation_api(lambda: _save_session_and_return(repository, session, event))


def _save_session_and_return(
    repository: JsonLearningRepository,
    session: LearningSession,
    event: RunEvent,
) -> tuple[LearningSession, RunEvent]:
    repository.save_session(session)
    return session, event


def submit_evidence(
    session: LearningSession,
    evidence: Evidence,
    *,
    run_id: str,
    sequence: int,
) -> tuple[Evidence, RunEvent]:
    if evidence.session_id != session.id:
        raise ValueError("evidence must belong to learning session")
    if evidence.node_id != session.node_id:
        raise ValueError("evidence must match learning session node")
    event = RunEvent(
        sequence=sequence,
        run_id=run_id,
        phase="evidence",
        status="submitted",
        payload={
            "event_type": "evidence_submitted",
            "session_id": session.id,
            "node_id": evidence.node_id,
            "evidence_id": evidence.id,
            "kind": evidence.kind,
            "content_ref": evidence.content_ref,
        },
    )
    return evidence, event


def submit_evidence_api(
    request: SubmitEvidenceInput,
    repository: JsonLearningRepository,
) -> ContractApiResult:
    try:
        evidence, event = submit_evidence(
            request.session,
            request.evidence,
            run_id=request.run_id,
            sequence=request.sequence,
        )
    except ValueError as error:
        message = str(error)
        if message == "evidence must belong to learning session":
            error_code = "EVIDENCE_SESSION_MISMATCH"
        elif message == "evidence must match learning session node":
            error_code = "EVIDENCE_NODE_MISMATCH"
        else:
            raise
        return ContractApiResult(
            ok=False,
            value=None,
            error_code=error_code,
            error_message=message,
        )
    return repository_operation_api(lambda: _save_evidence_and_return(repository, evidence, event))


def _save_evidence_and_return(
    repository: JsonLearningRepository,
    evidence: Evidence,
    event: RunEvent,
) -> tuple[Evidence, RunEvent]:
    repository.save_evidence(evidence)
    return evidence, event


def apply_eval_result_to_progress(
    evidence: Evidence,
    eval_result: EvalResult,
    *,
    previous_percent: int,
    run_id: str,
    sequence: int,
) -> tuple[NodeProgress, RunEvent]:
    if eval_result.evidence_id != evidence.id:
        raise ValueError("eval result must reference evidence")
    percent = round(eval_result.score * 100)
    mastery_state = "verified" if eval_result.passed else "practiced"
    progress = NodeProgress(eval_result.node_id, percent, mastery_state)
    event = RunEvent(
        sequence=sequence,
        run_id=run_id,
        phase="progress",
        status="updated",
        payload={
            "event_type": "progress_updated",
            "node_id": eval_result.node_id,
            "evidence_id": evidence.id,
            "eval_result_id": eval_result.id,
            "from_percent": previous_percent,
            "to_percent": percent,
        },
    )
    return progress, event


def submit_eval_progress(
    request: SubmitEvalProgressInput,
    repository: JsonLearningRepository | None = None,
) -> ContractApiResult:
    try:
        value = apply_eval_result_to_progress(
            request.evidence,
            request.eval_result,
            previous_percent=request.previous_percent,
            run_id=request.run_id,
            sequence=request.sequence,
        )
    except ValueError as error:
        return ContractApiResult(
            ok=False,
            value=None,
            error_code="EVAL_EVIDENCE_MISMATCH",
            error_message=str(error),
        )
    if repository is None:
        return ContractApiResult(ok=True, value=value)
    progress, event = value
    return repository_operation_api(
        lambda: _save_eval_progress_and_return(repository, request.eval_result, progress, event)
    )


def _save_eval_progress_and_return(
    repository: JsonLearningRepository,
    eval_result: EvalResult,
    progress: NodeProgress,
    event: RunEvent,
) -> tuple[NodeProgress, RunEvent]:
    repository.save_eval_result(eval_result)
    repository.save_progress(progress)
    return progress, event


def create_graph_operation_request(
    *,
    request_id: str,
    course_id: str,
    node_id: str,
    operation_type: str,
    user_intent: str,
    source: str,
    run_id: str,
    sequence: int,
    target_node_ids: tuple[str, ...] = (),
    context_refs: tuple[str, ...] = (),
) -> tuple[GraphOperationRequest, RunEvent]:
    request = GraphOperationRequest(
        id=request_id,
        course_id=course_id,
        node_id=node_id,
        operation_type=operation_type,
        user_intent=user_intent,
        source=source,
        target_node_ids=target_node_ids,
        context_refs=context_refs,
    )
    event = RunEvent(
        sequence=sequence,
        run_id=run_id,
        phase="graph_update",
        status="requested",
        payload={
            "event_type": "graph_operation_requested",
            "request_id": request_id,
            "course_id": course_id,
            "node_id": node_id,
            "operation_type": operation_type,
            "source": source,
            "user_intent": user_intent,
            "target_node_ids": target_node_ids,
            "context_refs": context_refs,
        },
    )
    return request, event


def create_graph_operation_request_api(
    request: CreateGraphOperationRequestInput,
    repository: JsonLearningRepository | None = None,
) -> ContractApiResult:
    value = create_graph_operation_request(
        request_id=request.request_id,
        course_id=request.course_id,
        node_id=request.node_id,
        operation_type=request.operation_type,
        user_intent=request.user_intent,
        source=request.source,
        target_node_ids=request.target_node_ids,
        context_refs=request.context_refs,
        run_id=request.run_id,
        sequence=request.sequence,
    )
    if repository is None:
        return ContractApiResult(ok=True, value=value)
    graph_request, event = value
    return repository_operation_api(lambda: _save_graph_operation_request_and_return(repository, graph_request, event))


def _save_graph_operation_request_and_return(
    repository: JsonLearningRepository,
    request: GraphOperationRequest,
    event: RunEvent,
) -> tuple[GraphOperationRequest, RunEvent]:
    repository.save_graph_operation_request(request)
    return request, event


def propose_graph_operation(
    request: GraphOperationRequest,
    *,
    proposal_id: str,
    summary: str,
    rationale: str,
    proposed_nodes: tuple[str, ...],
    proposed_edges: tuple[tuple[str, str], ...] = (),
    progress_migration: str = "",
    risks: tuple[str, ...] = (),
    run_id: str,
    sequence: int,
    affected_nodes: tuple[str, ...] | None = None,
    requires_confirmation: bool = True,
) -> tuple[GraphOperationProposal, RunEvent]:
    if affected_nodes is None:
        affected_nodes = tuple(dict.fromkeys((request.node_id, *request.target_node_ids)))
    proposal = GraphOperationProposal(
        id=proposal_id,
        request_id=request.id,
        operation_type=request.operation_type,
        summary=summary,
        rationale=rationale,
        affected_nodes=affected_nodes,
        proposed_nodes=proposed_nodes,
        proposed_edges=proposed_edges,
        progress_migration=progress_migration,
        risks=risks,
        requires_confirmation=requires_confirmation,
    )
    event = RunEvent(
        sequence=sequence,
        run_id=run_id,
        phase="graph_update",
        status="proposed",
        payload={
            "event_type": "graph_operation_proposed",
            "proposal_id": proposal_id,
            "request_id": request.id,
            "operation_type": request.operation_type,
            "summary": summary,
            "affected_nodes": affected_nodes,
            "proposed_nodes": proposed_nodes,
            "proposed_edges": proposed_edges,
            "progress_migration": progress_migration,
            "risks": risks,
            "rationale": rationale,
            "requires_confirmation": requires_confirmation,
        },
    )
    return proposal, event


def propose_graph_operation_api(
    request: ProposeGraphOperationInput,
    repository: JsonLearningRepository | None = None,
) -> ContractApiResult:
    value = propose_graph_operation(
        request.request,
        proposal_id=request.proposal_id,
        summary=request.summary,
        rationale=request.rationale,
        proposed_nodes=request.proposed_nodes,
        proposed_edges=request.proposed_edges,
        progress_migration=request.progress_migration,
        risks=request.risks,
        affected_nodes=request.affected_nodes,
        requires_confirmation=request.requires_confirmation,
        run_id=request.run_id,
        sequence=request.sequence,
    )
    if repository is None:
        return ContractApiResult(ok=True, value=value)
    proposal, event = value
    return repository_operation_api(lambda: _save_graph_operation_proposal_and_return(repository, proposal, event))


def _save_graph_operation_proposal_and_return(
    repository: JsonLearningRepository,
    proposal: GraphOperationProposal,
    event: RunEvent,
) -> tuple[GraphOperationProposal, RunEvent]:
    repository.save_graph_operation_proposal(proposal)
    return proposal, event


def confirm_graph_operation(
    proposal: GraphOperationProposal,
    *,
    confirmed_by: str,
    run_id: str,
    sequence: int,
    changes_requested: tuple[str, ...] = (),
) -> tuple[GraphOperationConfirmation, RunEvent]:
    confirmation = GraphOperationConfirmation(
        proposal_id=proposal.id,
        request_id=proposal.request_id,
        confirmed_by=confirmed_by,
        changes_requested=changes_requested,
    )
    event = RunEvent(
        sequence=sequence,
        run_id=run_id,
        phase="graph_update",
        status="confirmed",
        payload={
            "event_type": "graph_operation_confirmed",
            "proposal_id": proposal.id,
            "request_id": proposal.request_id,
            "confirmed_by": confirmed_by,
            "changes_requested": changes_requested,
        },
    )
    return confirmation, event


def confirm_graph_operation_api(
    request: ConfirmGraphOperationInput,
    repository: JsonLearningRepository | None = None,
) -> ContractApiResult:
    value = confirm_graph_operation(
        request.proposal,
        confirmed_by=request.confirmed_by,
        changes_requested=request.changes_requested,
        run_id=request.run_id,
        sequence=request.sequence,
    )
    if repository is None:
        return ContractApiResult(ok=True, value=value)
    confirmation, event = value
    return repository_operation_api(lambda: _save_graph_operation_confirmation_and_return(repository, confirmation, event))


def _save_graph_operation_confirmation_and_return(
    repository: JsonLearningRepository,
    confirmation: GraphOperationConfirmation,
    event: RunEvent,
) -> tuple[GraphOperationConfirmation, RunEvent]:
    repository.save_graph_operation_confirmation(confirmation)
    return confirmation, event


def apply_graph_operation(
    proposal: GraphOperationProposal,
    *,
    confirmed_by: str | None = None,
    confirmation: GraphOperationConfirmation | None = None,
    run_id: str,
    sequence: int,
) -> tuple[AppliedGraphOperation, RunEvent]:
    if confirmation:
        if confirmation.proposal_id != proposal.id or confirmation.request_id != proposal.request_id:
            raise ValueError("confirmation must match proposal")
        confirmed_by = confirmation.confirmed_by
    if proposal.requires_confirmation and not confirmed_by:
        raise ValueError("graph operation requires confirmation")
    applied = AppliedGraphOperation(
        proposal_id=proposal.id,
        request_id=proposal.request_id,
        operation_type=proposal.operation_type,
        status="applied",
        applied_nodes=proposal.proposed_nodes,
    )
    event = RunEvent(
        sequence=sequence,
        run_id=run_id,
        phase="graph_update",
        status="applied",
        payload={
            "event_type": "graph_update_applied",
            "proposal_id": proposal.id,
            "request_id": proposal.request_id,
            "operation_type": proposal.operation_type,
            "confirmed_by": confirmed_by,
            "created_nodes": proposal.proposed_nodes,
            "created_edges": proposal.proposed_edges,
        },
    )
    return applied, event


def apply_graph_operation_api(
    request: ApplyGraphOperationInput,
    repository: JsonLearningRepository | None = None,
) -> ContractApiResult:
    try:
        value = apply_graph_operation(
            request.proposal,
            confirmed_by=request.confirmed_by,
            confirmation=request.confirmation,
            run_id=request.run_id,
            sequence=request.sequence,
        )
    except ValueError as error:
        message = str(error)
        error_code = "GRAPH_OPERATION_CONFIRMATION_MISMATCH"
        if message == "graph operation requires confirmation":
            error_code = "GRAPH_OPERATION_CONFIRMATION_REQUIRED"
        return ContractApiResult(
            ok=False,
            value=None,
            error_code=error_code,
            error_message=message,
        )
    if repository is None:
        return ContractApiResult(ok=True, value=value)
    applied, event = value
    return repository_operation_api(
        lambda: _save_applied_graph_operation_and_return(
            repository,
            request.proposal,
            applied,
            event,
        )
    )


def apply_graph_operation_to_course_graph(
    graph: CourseGraph,
    proposal: GraphOperationProposal,
) -> tuple[CourseGraph, tuple[NodeProgress, ...]]:
    existing_node_ids = set(graph.course.node_ids)
    new_node_ids = tuple(
        node_id
        for node_id in dict.fromkeys(proposal.proposed_nodes)
        if node_id not in existing_node_ids
    )
    updated_course = Course(
        id=graph.course.id,
        goal_id=graph.course.goal_id,
        title=graph.course.title,
        node_ids=(*graph.course.node_ids, *new_node_ids),
    )
    new_nodes = tuple(
        ConceptNode(node_id, graph.course.id, node_id)
        for node_id in new_node_ids
    )
    proposed_edges = tuple(
        DependencyEdge(source_node_id, target_node_id, "prerequisite")
        for source_node_id, target_node_id in proposal.proposed_edges
    )
    existing_edges = {
        (edge.source_node_id, edge.target_node_id, edge.relation)
        for edge in graph.dependency_edges
    }
    new_edges = tuple(
        edge
        for edge in proposed_edges
        if (edge.source_node_id, edge.target_node_id, edge.relation) not in existing_edges
    )
    updated_graph = CourseGraph(
        course=updated_course,
        nodes=(*graph.nodes, *new_nodes),
        dependency_edges=(*graph.dependency_edges, *new_edges),
    )
    initialized_progress = tuple(
        NodeProgress(node_id, 0, "unknown")
        for node_id in new_node_ids
    )
    return updated_graph, initialized_progress


def _save_applied_graph_operation_and_return(
    repository: JsonLearningRepository,
    proposal: GraphOperationProposal,
    applied: AppliedGraphOperation,
    event: RunEvent,
) -> tuple[AppliedGraphOperation, RunEvent]:
    try:
        graph_request = repository.load_graph_operation_request(proposal.request_id)
        graph = repository.load_course_graph(graph_request.course_id)
    except LearningRecordNotFound:
        repository.save_applied_graph_operation(applied)
        return applied, event
    updated_graph, initialized_progress = apply_graph_operation_to_course_graph(graph, proposal)
    repository.save_course_graph(updated_graph)
    for progress in initialized_progress:
        repository.save_progress(progress)
    repository.save_applied_graph_operation(applied)
    updated_event = RunEvent(
        sequence=event.sequence,
        run_id=event.run_id,
        phase=event.phase,
        status=event.status,
        payload={
            **event.payload,
            "course_id": graph_request.course_id,
            "updated_node_ids": updated_graph.course.node_ids,
            "initialized_progress": tuple(
                (progress.node_id, progress.percent, progress.mastery_state)
                for progress in initialized_progress
            ),
        },
    )
    return applied, updated_event


def replay_graph_operations_from_trace(
    result: RunResult,
    repository: JsonLearningRepository,
) -> GraphOperationReplay:
    requests: list[GraphOperationRequest] = []
    proposals: list[GraphOperationProposal] = []
    confirmations: list[GraphOperationConfirmation] = []
    applied_operations: list[AppliedGraphOperation] = []
    for event in sorted(result.events, key=lambda item: item.sequence):
        payload = event.payload
        event_type = payload.get("event_type")
        if event_type == "graph_operation_requested":
            request = GraphOperationRequest(
                id=payload["request_id"],
                course_id=payload["course_id"],
                node_id=payload["node_id"],
                operation_type=payload["operation_type"],
                user_intent=payload["user_intent"],
                source=payload["source"],
                target_node_ids=_tuple(payload.get("target_node_ids")),
                context_refs=_tuple(payload.get("context_refs")),
                status="created",
            )
            repository.save_graph_operation_request(request)
            requests.append(request)
        elif event_type == "graph_operation_proposed":
            proposal = GraphOperationProposal(
                id=payload["proposal_id"],
                request_id=payload["request_id"],
                operation_type=payload["operation_type"],
                summary=payload["summary"],
                rationale=payload["rationale"],
                affected_nodes=_tuple(payload.get("affected_nodes")),
                proposed_nodes=_tuple(payload.get("proposed_nodes")),
                proposed_edges=_edge_tuple(payload.get("proposed_edges")),
                progress_migration=payload.get("progress_migration", ""),
                risks=_tuple(payload.get("risks")),
                requires_confirmation=payload.get("requires_confirmation", True),
            )
            repository.save_graph_operation_proposal(proposal)
            proposals.append(proposal)
        elif event_type == "graph_operation_confirmed":
            confirmation = GraphOperationConfirmation(
                proposal_id=payload["proposal_id"],
                request_id=payload["request_id"],
                confirmed_by=payload["confirmed_by"],
                changes_requested=_tuple(payload.get("changes_requested")),
                status=event.status,
            )
            repository.save_graph_operation_confirmation(confirmation)
            confirmations.append(confirmation)
        elif event_type == "graph_update_applied":
            applied = AppliedGraphOperation(
                proposal_id=payload["proposal_id"],
                request_id=payload["request_id"],
                operation_type=payload["operation_type"],
                status=event.status,
                applied_nodes=_tuple(payload.get("created_nodes")),
            )
            repository.save_applied_graph_operation(applied)
            applied_operations.append(applied)
    return GraphOperationReplay(
        requests=tuple(requests),
        proposals=tuple(proposals),
        confirmations=tuple(confirmations),
        applied_operations=tuple(applied_operations),
    )


def summarize_learning_loop_replay_regression(
    result: RunResult,
    replay: GraphOperationReplay,
) -> LearningLoopReplayRegressionSummary:
    completed_events = [
        event
        for event in sorted(result.events, key=lambda item: item.sequence)
        if event.payload.get("event_type") == "run_completed"
    ]
    terminal_payload = completed_events[-1].payload if completed_events else {}
    terminal_status = terminal_payload.get("terminal_status", "missing")
    completion_reason = terminal_payload.get("reason", "")
    no_remaining_nodes = (
        completion_reason == "no selectable learning node"
        and terminal_payload.get("next_action") == "no remaining learning nodes"
    )
    remaining_selectable_nodes = 0 if no_remaining_nodes else 1
    graph_replay_completed = bool(replay.requests) and (
        len(replay.requests)
        == len(replay.proposals)
        == len(replay.confirmations)
        == len(replay.applied_operations)
    )
    trace_matches_contract = tuple(
        event.payload.get("event_type")
        for event in sorted(result.events, key=lambda item: item.sequence)
    ) == LEARNING_LOOP_EVENT_TYPES
    final_learning_completed = terminal_status == "completed" and remaining_selectable_nodes == 0
    regression_passed = graph_replay_completed and trace_matches_contract and final_learning_completed
    report = (
        "Learning loop completed; graph expansion replayed; no remaining selectable nodes."
        if regression_passed
        else "Learning loop replay regression incomplete."
    )
    return LearningLoopReplayRegressionSummary(
        run_id=result.run_id,
        terminal_status=terminal_status,
        completion_reason=completion_reason,
        graph_replay_completed=graph_replay_completed,
        replayed_request_count=len(replay.requests),
        replayed_proposal_count=len(replay.proposals),
        replayed_confirmation_count=len(replay.confirmations),
        replayed_applied_count=len(replay.applied_operations),
        trace_matches_contract=trace_matches_contract,
        final_learning_completed=final_learning_completed,
        remaining_selectable_nodes=remaining_selectable_nodes,
        regression_passed=regression_passed,
        report=report,
    )


def build_golden_learning_task_report(
    task: GoldenLearningTask,
    summary: LearningLoopReplayRegressionSummary,
) -> GoldenLearningTaskReport:
    actual_graph_operation_count = summary.replayed_applied_count
    regression_passed = (
        summary.regression_passed
        and summary.terminal_status == task.expected_terminal_status
        and summary.completion_reason == task.expected_completion_reason
        and actual_graph_operation_count == task.expected_graph_operation_count
        and summary.remaining_selectable_nodes == task.expected_remaining_selectable_nodes
    )
    status = "passed" if regression_passed else "failed"
    return GoldenLearningTaskReport(
        task_id=task.id,
        task_title=task.title,
        goal_id=task.goal_id,
        course_id=task.course_id,
        run_id=summary.run_id,
        expected_terminal_status=task.expected_terminal_status,
        actual_terminal_status=summary.terminal_status,
        expected_completion_reason=task.expected_completion_reason,
        actual_completion_reason=summary.completion_reason,
        expected_graph_operation_count=task.expected_graph_operation_count,
        actual_graph_operation_count=actual_graph_operation_count,
        expected_remaining_selectable_nodes=task.expected_remaining_selectable_nodes,
        actual_remaining_selectable_nodes=summary.remaining_selectable_nodes,
        trace_matches_contract=summary.trace_matches_contract,
        graph_replay_completed=summary.graph_replay_completed,
        regression_passed=regression_passed,
        report=f"Golden learning task {status}: {task.id}.",
    )


def build_golden_learning_task_batch_report(
    suite_id: str,
    reports: tuple[GoldenLearningTaskReport, ...],
) -> GoldenLearningTaskBatchReport:
    failed_task_ids = tuple(report.task_id for report in reports if not report.regression_passed)
    passed_count = len(reports) - len(failed_task_ids)
    regression_passed = bool(reports) and not failed_task_ids
    status = "passed" if regression_passed else "failed"
    return GoldenLearningTaskBatchReport(
        suite_id=suite_id,
        total_count=len(reports),
        passed_count=passed_count,
        failed_count=len(failed_task_ids),
        failed_task_ids=failed_task_ids,
        regression_passed=regression_passed,
        reports=reports,
        report=f"Golden learning task suite {status}: {passed_count}/{len(reports)} passed.",
    )


def build_golden_learning_task_batch_report_from_replays(
    suite_id: str,
    runs: tuple[GoldenLearningTaskRun, ...],
) -> GoldenLearningTaskBatchReport:
    reports = tuple(
        build_golden_learning_task_report(
            run.task,
            summarize_learning_loop_replay_regression(run.result, run.replay),
        )
        for run in runs
    )
    return build_golden_learning_task_batch_report(suite_id, reports)


def run_golden_learning_task_batch_from_repository(
    suite_id: str,
    run_references: tuple[GoldenLearningTaskRunReference, ...],
    repository: JsonLearningRepository,
    trace_store,
    replay_repository: JsonLearningRepository,
) -> ContractApiResult:
    return repository_operation_api(
        lambda: _run_golden_learning_task_batch_from_repository(
            suite_id,
            run_references,
            repository,
            trace_store,
            replay_repository,
        )
    )


def _run_golden_learning_task_batch_from_repository(
    suite_id: str,
    run_references: tuple[GoldenLearningTaskRunReference, ...],
    repository: JsonLearningRepository,
    trace_store,
    replay_repository: JsonLearningRepository,
) -> GoldenLearningTaskBatchReport:
    runs = []
    for reference in run_references:
        task = repository.load_golden_learning_task(reference.task_id)
        result = trace_store.load(reference.run_id)
        replay = replay_graph_operations_from_trace(result, replay_repository)
        runs.append(GoldenLearningTaskRun(task, result, replay))
    batch_report = build_golden_learning_task_batch_report_from_replays(suite_id, tuple(runs))
    for report in batch_report.reports:
        repository.save_golden_learning_task_report(report)
    repository.save_golden_learning_task_batch_report(batch_report)
    return batch_report


def _tuple(value: object) -> tuple:
    if value is None:
        return ()
    return tuple(value)


def _edge_tuple(value: object) -> tuple[tuple[str, str], ...]:
    if value is None:
        return ()
    return tuple(tuple(edge) for edge in value)


def recompute_parent_progress(
    node_id: str,
    children: tuple[NodeProgress, ...],
    *,
    previous_percent: int,
    run_id: str,
    sequence: int,
) -> tuple[NodeProgress, RunEvent]:
    if not children:
        raise ValueError("parent progress requires child progress")
    percent = round(sum(child.percent for child in children) / len(children))
    if percent == 0:
        mastery_state = "unknown"
    elif percent == 100:
        mastery_state = "verified"
    else:
        mastery_state = "learning"
    progress = NodeProgress(node_id, percent, mastery_state)
    event = RunEvent(
        sequence=sequence,
        run_id=run_id,
        phase="progress",
        status="recomputed",
        payload={
            "event_type": "node_progress_recomputed",
            "node_id": node_id,
            "child_node_ids": tuple(child.node_id for child in children),
            "from_percent": previous_percent,
            "to_percent": percent,
        },
    )
    return progress, event


def recompute_parent_progress_api(
    request: RecomputeParentProgressInput,
    repository: JsonLearningRepository | None = None,
) -> ContractApiResult:
    try:
        value = recompute_parent_progress(
            request.node_id,
            request.children,
            previous_percent=request.previous_percent,
            run_id=request.run_id,
            sequence=request.sequence,
        )
    except ValueError as error:
        message = str(error)
        if message == "parent progress requires child progress":
            return ContractApiResult(
                ok=False,
                value=None,
                error_code="EMPTY_CHILD_PROGRESS",
                error_message=message,
            )
        raise
    if repository is None:
        return ContractApiResult(ok=True, value=value)
    progress, event = value
    return repository_operation_api(lambda: _save_progress_and_return(repository, progress, event))


def _save_progress_and_return(
    repository: JsonLearningRepository,
    progress: NodeProgress,
    event: RunEvent,
) -> tuple[NodeProgress, RunEvent]:
    repository.save_progress(progress)
    return progress, event


def select_next_learning_node(
    graph: CourseGraph,
    progress: tuple[NodeProgress, ...],
    *,
    run_id: str,
    sequence: int,
) -> tuple[NextLearningNode, RunEvent]:
    progress_by_node_id = {item.node_id: item for item in progress}
    prerequisites_by_node_id = _prerequisites_by_node_id(graph.dependency_edges)
    candidates: list[tuple[str, tuple[str, ...]]] = []
    for node_id in graph.course.node_ids:
        node_progress = progress_by_node_id.get(node_id, NodeProgress(node_id, 0, "unknown"))
        if node_progress.mastery_state != "unknown":
            continue
        prerequisite_node_ids = prerequisites_by_node_id.get(node_id, ())
        if all(_is_mastered(progress_by_node_id.get(prerequisite_id)) for prerequisite_id in prerequisite_node_ids):
            candidates.append((node_id, prerequisite_node_ids))
    if not candidates:
        raise ValueError("no selectable learning node")
    node_id, prerequisite_node_ids = candidates[0]
    reason = "first unknown node with prerequisites satisfied"
    next_node = NextLearningNode(
        course_id=graph.course.id,
        node_id=node_id,
        prerequisite_node_ids=prerequisite_node_ids,
        reason=reason,
    )
    event = RunEvent(
        sequence=sequence,
        run_id=run_id,
        phase="planning",
        status="selected",
        payload={
            "event_type": "node_selected",
            "course_id": graph.course.id,
            "node_id": node_id,
            "alternatives": tuple(candidate_node_id for candidate_node_id, _ in candidates[1:]),
            "prerequisite_node_ids": prerequisite_node_ids,
            "selection_reason": reason,
        },
    )
    return next_node, event


def select_next_learning_node_api(
    request: SelectNextLearningNodeInput,
    repository: JsonLearningRepository,
) -> ContractApiResult:
    try:
        graph = repository.load_course_graph(request.course_id)
        progress = tuple(_load_progress_or_unknown(repository, node_id) for node_id in graph.course.node_ids)
        value = select_next_learning_node(
            graph,
            progress,
            run_id=request.run_id,
            sequence=request.sequence,
        )
    except ValueError as error:
        message = str(error)
        if message == "no selectable learning node":
            return ContractApiResult(
                ok=False,
                value=None,
                error_code="NEXT_LEARNING_NODE_NOT_FOUND",
                error_message=message,
            )
        raise
    except (
        LearningRecordNotFound,
        LearningRepositoryDataCorrupted,
        LearningRepositoryJsonFieldMissing,
    ) as error:
        return ContractApiResult(
            ok=False,
            value=None,
            error_code=error.error_code,
            error_message=str(error),
        )
    except OSError as error:
        return ContractApiResult(
            ok=False,
            value=None,
            error_code="LEARNING_REPOSITORY_IO_ERROR",
            error_message=str(error),
        )
    return ContractApiResult(ok=True, value=value)


def complete_agent_run(
    *,
    run_id: str,
    sequence: int,
    status: str,
    reason: str,
    recoverable: bool,
    next_action: str,
) -> tuple[TerminalStatus, RunEvent]:
    terminal_status = TerminalStatus(
        run_id=run_id,
        status=status,
        reason=reason,
        recoverable=recoverable,
        next_action=next_action,
    )
    event = RunEvent(
        sequence=sequence,
        run_id=run_id,
        phase="completed",
        status=status,
        payload={
            "event_type": "run_completed",
            "terminal_status": status,
            "reason": reason,
            "recoverable": recoverable,
            "next_action": next_action,
        },
    )
    return terminal_status, event


def complete_agent_run_api(request: CompleteAgentRunInput) -> ContractApiResult:
    return ContractApiResult(
        ok=True,
        value=complete_agent_run(
            run_id=request.run_id,
            sequence=request.sequence,
            status=request.status,
            reason=request.reason,
            recoverable=request.recoverable,
            next_action=request.next_action,
        ),
    )

def _prerequisites_by_node_id(
    dependency_edges: tuple[DependencyEdge, ...],
) -> dict[str, tuple[str, ...]]:
    prerequisites: dict[str, list[str]] = {}
    for edge in dependency_edges:
        if edge.relation == "prerequisite":
            prerequisites.setdefault(edge.target_node_id, []).append(edge.source_node_id)
    return {node_id: tuple(node_ids) for node_id, node_ids in prerequisites.items()}


def _is_mastered(progress: NodeProgress | None) -> bool:
    return progress is not None and progress.mastery_state in {"verified", "retained"}


def _load_progress_or_unknown(repository: JsonLearningRepository, node_id: str) -> NodeProgress:
    try:
        return repository.load_progress(node_id)
    except LearningRecordNotFound as error:
        if error.collection == "progress":
            return NodeProgress(node_id, 0, "unknown")
        raise
