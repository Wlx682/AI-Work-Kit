"""Application service for the knowledge-graph learning product.

The API intentionally stays in AI-Work-Kit: it exposes the existing learning
contracts and ``LearningAgentRuntime`` without coupling the practice to another
product repository.
"""

from __future__ import annotations

from dataclasses import asdict
import json
from pathlib import Path
from typing import Any
from uuid import uuid4

from agent.infrastructure.traces import TraceStore

from ..agents import LearningAgentTeam
from ..domain.contracts import (
    ApplyGraphOperationInput,
    ConceptNode,
    ConfirmGraphOperationInput,
    Course,
    CreateGraphOperationRequestInput,
    CreateLearningGoalInput,
    DependencyEdge,
    Evidence,
    EvalResult,
    GraphOperationProposal,
    InitializeCourseGraphInput,
    JsonLearningRepository,
    LearningGoal,
    LearningRecordNotFound,
    NodeProgress,
    ProposeGraphOperationInput,
    StartNodeLearningInput,
    SubmitEvalProgressInput,
    SubmitEvidenceInput,
    apply_graph_operation_api,
    confirm_graph_operation_api,
    create_graph_operation_request_api,
    create_learning_goal_api,
    initialize_course_graph_api,
    propose_graph_operation_api,
    start_node_learning_api,
    submit_eval_progress,
    submit_evidence_api,
)
from ..orchestration.runtime import (
    LearningAgentRuntime,
    LearningRuntimeTools,
)
from .intelligence import (
    EvaluationDraft,
    LearningActivity,
    LearningIntelligence,
    LearningIntelligenceError,
    validate_course_graph_draft,
    validate_learning_activity,
    validate_evaluation_draft,
    validate_recommendation,
)
from ..infrastructure.deepseek_intelligence import DeepSeekLearningIntelligence


class LearningApiError(Exception):
    """An error that can be safely returned by the local HTTP boundary."""

    def __init__(self, code: str, message: str, status: int = 400):
        super().__init__(message)
        self.code = code
        self.message = message
        self.status = status


class LearningApiService:
    """Application service composing contracts, persistence, and agent runtime."""

    def __init__(
        self,
        data_directory: str | Path,
        intelligence: LearningIntelligence | None = None,
        agent_team: LearningAgentTeam | None = None,
    ):
        self.data_directory = Path(data_directory)
        self.data_directory.mkdir(parents=True, exist_ok=True)
        self.repository = JsonLearningRepository(str(self.data_directory / "learning"))
        self.agent_team = agent_team or LearningAgentTeam()
        self.intelligence = intelligence or DeepSeekLearningIntelligence(
            self.agent_team.catalog
        )
        self.activities_directory = self.data_directory / "learning-activities"
        self.activities_directory.mkdir(parents=True, exist_ok=True)
        self.evidence_content_directory = self.data_directory / "learning-evidence"
        self.evidence_content_directory.mkdir(parents=True, exist_ok=True)
        self.runtime = LearningAgentRuntime(
            self.agent_team.runtime_roles(self.get_course),
            LearningRuntimeTools(apply_graph_update=self._apply_graph_update),
            trace_store=TraceStore(self.data_directory / "traces"),
            checkpoint_path=str(self.data_directory / "learning-runtime.sqlite"),
        )

    def close(self) -> None:
        self.runtime.close()

    def create_goal(self, title: object) -> dict[str, Any]:
        if not isinstance(title, str) or not title.strip():
            raise LearningApiError("INVALID_GOAL", "title must be a non-empty string")
        draft = self._intelligence(
            lambda: self.intelligence.generate_course_graph(title.strip())
        )
        draft = self._intelligence(lambda: validate_course_graph_draft(draft))
        suffix = uuid4().hex[:8]
        goal = LearningGoal(f"goal-{suffix}", title.strip())
        course_id = f"course-{suffix}"
        node_ids = tuple(self._node_id(course_id, node.slug) for node in draft.nodes)
        course = Course(course_id, goal.id, draft.title, node_ids)
        nodes = tuple(
            ConceptNode(self._node_id(course_id, node.slug), course_id, node.title)
            for node in draft.nodes
        )
        edges = tuple(
            DependencyEdge(
                self._node_id(course_id, edge.source_slug),
                self._node_id(course_id, edge.target_slug),
                "prerequisite",
            )
            for edge in draft.edges
        )
        run_id = f"setup-{suffix}"
        self._require(create_learning_goal_api(
            CreateLearningGoalInput(goal, run_id, 1), self.repository
        ))
        self._require(initialize_course_graph_api(
            InitializeCourseGraphInput(
                goal=goal,
                course=course,
                nodes=nodes,
                run_id=run_id,
                sequence=2,
                dependency_edges=edges,
            ),
            self.repository,
        ))
        prerequisite_targets = {edge.target_node_id for edge in edges}
        for node in nodes:
            self.repository.save_progress(NodeProgress(
                node.id,
                0,
                "available" if node.id not in prerequisite_targets else "locked",
            ))
        return {"goal": asdict(goal), "course": self.get_course(course_id)}

    def get_course(self, course_id: object) -> dict[str, Any]:
        if not isinstance(course_id, str) or not course_id:
            raise LearningApiError("INVALID_COURSE", "course_id is required")
        try:
            graph = self.repository.load_course_graph(course_id)
        except LearningRecordNotFound as error:
            raise LearningApiError("COURSE_NOT_FOUND", str(error), 404) from error
        nodes = []
        for node in graph.nodes:
            try:
                progress = self.repository.load_progress(node.id)
            except LearningRecordNotFound:
                progress = NodeProgress(node.id, 0, "unknown")
            nodes.append({
                **asdict(node),
                "slug": self._node_slug(node.id),
                "progress": progress.percent,
                "mastery_state": progress.mastery_state,
            })
        return {
            "id": graph.course.id,
            "goal_id": graph.course.goal_id,
            "title": graph.course.title,
            "mastery": round(sum(node["progress"] for node in nodes) / len(nodes)),
            "nodes": nodes,
            "edges": [asdict(edge) for edge in graph.dependency_edges],
        }

    def get_recommendation(self, course_id: object) -> dict[str, Any]:
        """Return a DeepSeek decision validated against the current course."""
        course = self.get_course(course_id)
        recommendation = self._intelligence(
            lambda: self.intelligence.recommend_next_node(course)
        )
        recommendation = self._intelligence(
            lambda: validate_recommendation(recommendation, course)
        )
        prerequisite_node_ids = tuple(
            edge["source_node_id"]
            for edge in course["edges"]
            if edge["target_node_id"] == recommendation.node_id
        )

        selected_node = next(
            node for node in course["nodes"] if node["id"] == recommendation.node_id
        )
        return {
            "course_id": course["id"],
            "node": selected_node,
            "prerequisite_node_ids": list(prerequisite_node_ids),
            "reason": recommendation.reason,
        }

    def start_session(self, course_id: object, node_id: object) -> dict[str, Any]:
        if not isinstance(course_id, str) or not isinstance(node_id, str):
            raise LearningApiError("INVALID_SESSION", "course_id and node_id are required")
        try:
            course = self.repository.load_course(course_id)
            goal = self.repository.load_goal(course.goal_id)
            node = self.repository.load_node(node_id)
        except LearningRecordNotFound as error:
            raise LearningApiError("LEARNING_RECORD_NOT_FOUND", str(error), 404) from error
        course_view = self.get_course(course_id)
        activity = self._intelligence(
            lambda: self.intelligence.create_learning_activity(course_view, node_id)
        )
        activity = self._intelligence(lambda: validate_learning_activity(activity))
        session_id = f"session-{uuid4().hex[:10]}"
        run_id = f"session-run-{uuid4().hex[:10]}"
        result = self._require(start_node_learning_api(
            StartNodeLearningInput(goal, course, node, session_id, run_id, 1),
            self.repository,
        ))
        session, event = result
        self._save_activity(session.id, activity)
        return {
            "session": asdict(session),
            "event": self._event_dict(event),
            "activity": asdict(activity),
        }

    def submit_evidence(self, session_id: object, answer: object) -> dict[str, Any]:
        if not isinstance(session_id, str) or not session_id:
            raise LearningApiError("INVALID_EVIDENCE", "session_id is required")
        if not isinstance(answer, str) or not answer.strip():
            raise LearningApiError("INVALID_EVIDENCE", "answer must be a non-empty string")
        try:
            session = self.repository.load_session(session_id)
            node = self.repository.load_node(session.node_id)
        except LearningRecordNotFound as error:
            raise LearningApiError("LEARNING_RECORD_NOT_FOUND", str(error), 404) from error

        suffix = uuid4().hex[:10]
        run_id = f"evidence-run-{suffix}"
        evidence_id = f"evidence-{suffix}"
        evidence = Evidence(
            evidence_id,
            session.id,
            session.node_id,
            "answer",
            f"learning-evidence://{evidence_id}",
        )
        self._save_evidence_content(evidence.id, answer.strip())
        self._require(submit_evidence_api(
            SubmitEvidenceInput(session, evidence, run_id, 1), self.repository
        ))
        course_view = self.get_course(session.course_id)
        activity = self._load_activity(session.id)
        evaluation_draft = self._intelligence(
            lambda: self.intelligence.evaluate_evidence(
                course_view,
                session.node_id,
                answer.strip(),
                activity,
            )
        )
        evaluation_draft = self._intelligence(
            lambda: validate_evaluation_draft(
                evaluation_draft, course_view, session.node_id
            )
        )
        evaluation = EvalResult(
            f"eval-{suffix}",
            evidence.id,
            session.node_id,
            evaluation_draft.passed,
            round(evaluation_draft.score, 4),
            evaluation_draft.reason,
        )
        try:
            previous_percent = self.repository.load_progress(session.node_id).percent
        except LearningRecordNotFound:
            previous_percent = 0
        self._require(submit_eval_progress(
            SubmitEvalProgressInput(evidence, evaluation, previous_percent, run_id, 2),
            self.repository,
        ))

        runtime_result = self.runtime.run({
            "task": f"learn {node.title}",
            "goal_id": session.goal_id,
            "course_id": session.course_id,
            "concept_id": session.node_id,
            "concept_title": node.title,
            "evidence_id": evidence.id,
            "answer": answer.strip(),
            "activity": asdict(activity),
            "evaluation": {
                **asdict(evaluation),
                "gaps": list(evaluation_draft.gaps),
            },
            "graph_update_proposal": self._proposal_payload(
                session.course_id,
                session.node_id,
                evaluation_draft,
            ),
        })
        if runtime_result.error:
            raise LearningApiError("RUNTIME_FAILED", runtime_result.error, 500)
        return {
            "evidence": asdict(evidence),
            "evaluation": {
                **asdict(evaluation),
                "gaps": list(evaluation_draft.gaps),
            },
            "runtime": self._runtime_dict(runtime_result),
            "course": self.get_course(session.course_id),
        }

    def review_graph_update(
        self,
        thread_id: object,
        parent_run_id: object,
        course_id: object,
        approved: object,
    ) -> dict[str, Any]:
        if not all(isinstance(value, str) and value for value in (
            thread_id, parent_run_id, course_id
        )):
            raise LearningApiError(
                "INVALID_REVIEW", "thread_id, parent_run_id, and course_id are required"
            )
        if not isinstance(approved, bool):
            raise LearningApiError("INVALID_REVIEW", "approved must be a boolean")
        result = self.runtime.resume(
            thread_id,
            {"approved": approved},
            parent_run_id=parent_run_id,
        )
        if result.error:
            raise LearningApiError("RUNTIME_RESUME_FAILED", result.error, 409)
        return {
            "runtime": self._runtime_dict(result),
            "course": self.get_course(course_id),
        }

    def _proposal_payload(
        self,
        course_id: str,
        node_id: str,
        evaluation: EvaluationDraft,
    ) -> dict[str, Any] | None:
        proposal = evaluation.proposal
        if proposal is None:
            return None
        request_id = f"graph-request-{uuid4().hex[:10]}"
        proposal_id = f"proposal-{uuid4().hex[:10]}"
        return {
            "request_id": request_id,
            "proposal_id": proposal_id,
            "course_id": course_id,
            "node_id": node_id,
            "operation_type": proposal.operation_type,
            "summary": proposal.summary,
            "rationale": proposal.rationale,
            "affected_nodes": list(proposal.affected_node_ids),
            "proposed_nodes": [item.id for item in proposal.proposed_nodes],
            "node_titles": {item.id: item.title for item in proposal.proposed_nodes},
            "proposed_edges": [list(edge) for edge in proposal.proposed_edges],
            "progress_migration": proposal.progress_migration,
            "risks": list(proposal.risks),
        }

    def _apply_graph_update(self, raw: dict[str, Any]) -> dict[str, Any]:
        run_id = f"apply-{uuid4().hex[:10]}"
        graph_request, _ = self._require(create_graph_operation_request_api(
            CreateGraphOperationRequestInput(
                raw["request_id"], raw["course_id"], raw["node_id"],
                raw["operation_type"], raw["summary"], "learning-agent-runtime",
                run_id, 1,
            ),
            self.repository,
        ))
        proposal, _ = self._require(propose_graph_operation_api(
            ProposeGraphOperationInput(
                request=graph_request,
                proposal_id=raw["proposal_id"],
                summary=raw["summary"],
                rationale=raw["rationale"],
                proposed_nodes=tuple(raw["proposed_nodes"]),
                run_id=run_id,
                sequence=2,
                proposed_edges=tuple(tuple(edge) for edge in raw["proposed_edges"]),
                progress_migration=raw["progress_migration"],
                risks=tuple(raw["risks"]),
                affected_nodes=tuple(raw["affected_nodes"]),
                requires_confirmation=True,
            ),
            self.repository,
        ))
        confirmation, _ = self._require(confirm_graph_operation_api(
            ConfirmGraphOperationInput(proposal, "user", run_id, 3),
            self.repository,
        ))
        applied, event = self._require(apply_graph_operation_api(
            ApplyGraphOperationInput(proposal, run_id, 4, confirmation=confirmation),
            self.repository,
        ))
        for node_id, title in raw["node_titles"].items():
            self.repository.save_node(ConceptNode(node_id, raw["course_id"], title))
        return {"applied": asdict(applied), "event": self._event_dict(event)}

    @staticmethod
    def _require(result):
        if not result.ok:
            raise LearningApiError(
                result.error_code or "LEARNING_CONTRACT_FAILED",
                result.error_message or "learning contract failed",
                409,
            )
        return result.value

    @staticmethod
    def _intelligence(operation):
        try:
            return operation()
        except LearningIntelligenceError as error:
            status = 503 if error.code == "LLM_NOT_CONFIGURED" else 502
            raise LearningApiError(error.code, error.message, status) from error

    def _save_activity(self, session_id: str, activity: LearningActivity) -> None:
        path = self.activities_directory / f"{session_id}.json"
        path.write_text(
            json.dumps(asdict(activity), ensure_ascii=False, indent=2),
            encoding="utf-8",
        )

    def _load_activity(self, session_id: str) -> LearningActivity:
        path = self.activities_directory / f"{session_id}.json"
        try:
            raw = json.loads(path.read_text(encoding="utf-8"))
        except (FileNotFoundError, json.JSONDecodeError) as error:
            raise LearningApiError(
                "LEARNING_ACTIVITY_NOT_FOUND",
                f"learning activity not found for session: {session_id}",
                404,
            ) from error
        return self._intelligence(lambda: validate_learning_activity(
            LearningActivity(
                content=raw.get("content"),
                insight=raw.get("insight"),
                question=raw.get("question"),
                rubric=tuple(raw.get("rubric", [])),
            )
        ))

    def _save_evidence_content(self, evidence_id: str, content: str) -> None:
        (self.evidence_content_directory / f"{evidence_id}.txt").write_text(
            content,
            encoding="utf-8",
        )

    def _load_evidence_content(self, evidence_id: str) -> str:
        try:
            return (self.evidence_content_directory / f"{evidence_id}.txt").read_text(
                encoding="utf-8"
            )
        except FileNotFoundError as error:
            raise LearningApiError(
                "EVIDENCE_CONTENT_NOT_FOUND",
                f"evidence content not found: {evidence_id}",
                404,
            ) from error

    @staticmethod
    def _event_dict(event) -> dict[str, Any]:
        return {
            "sequence": event.sequence,
            "run_id": event.run_id,
            "phase": event.phase,
            "status": event.status,
            "payload": event.payload,
        }

    def _runtime_dict(self, result) -> dict[str, Any]:
        proposal = None
        tutor = None
        evaluation = None
        for event in result.events:
            if event.phase == "tutor":
                tutor = event.payload.get("tutor_content")
            elif event.phase == "evaluator":
                evaluation = event.payload.get("evaluation")
            elif event.phase == "human_review" and event.status == "paused":
                interrupts = event.payload.get("interrupts", [])
                if interrupts:
                    proposal = interrupts[0].get("value", {}).get("proposal")
        return {
            "run_id": result.run_id,
            "thread_id": result.thread_id,
            "status": "paused" if result.is_paused else "completed",
            "outcome": result.outcome,
            "tutor": tutor,
            "evaluation": evaluation,
            "proposal": proposal,
            "events": [self._event_dict(event) for event in result.events],
        }

    @staticmethod
    def _node_id(course_id: str, slug: str) -> str:
        return f"{course_id}--{slug}"

    @staticmethod
    def _node_slug(node_id: str) -> str:
        return node_id.split("--", 1)[-1]
