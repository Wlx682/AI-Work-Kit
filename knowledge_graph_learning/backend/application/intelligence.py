"""Structured DeepSeek capabilities for the R4 learning system.

Production code uses :class:`DeepSeekLearningIntelligence`. Tests may inject
``ScriptedLearningIntelligence`` explicitly; there is intentionally no runtime
fallback from DeepSeek to scripted or fixture content.
"""

from __future__ import annotations

from dataclasses import dataclass
import math
import re
from typing import Any, Callable, Mapping, Protocol, TypeVar


_SLUG = re.compile(r"^[a-z0-9][a-z0-9-]{1,63}$")


class LearningIntelligenceError(RuntimeError):
    """Typed failure raised by the learning intelligence boundary."""

    def __init__(self, code: str, message: str):
        super().__init__(message)
        self.code = code
        self.message = message


@dataclass(frozen=True)
class CourseNodeDraft:
    slug: str
    title: str


@dataclass(frozen=True)
class CourseEdgeDraft:
    source_slug: str
    target_slug: str


@dataclass(frozen=True)
class CourseGraphDraft:
    title: str
    nodes: tuple[CourseNodeDraft, ...]
    edges: tuple[CourseEdgeDraft, ...]


@dataclass(frozen=True)
class RecommendationDraft:
    node_id: str
    reason: str


@dataclass(frozen=True)
class LearningActivity:
    content: str
    insight: str
    question: str
    rubric: tuple[str, ...]


@dataclass(frozen=True)
class ProposalNodeDraft:
    id: str
    title: str


@dataclass(frozen=True)
class GraphProposalDraft:
    operation_type: str
    summary: str
    rationale: str
    affected_node_ids: tuple[str, ...]
    proposed_nodes: tuple[ProposalNodeDraft, ...]
    proposed_edges: tuple[tuple[str, str], ...]
    progress_migration: str
    risks: tuple[str, ...]


@dataclass(frozen=True)
class EvaluationDraft:
    passed: bool
    score: float
    reason: str
    gaps: tuple[str, ...]
    proposal: GraphProposalDraft | None = None


class LearningIntelligence(Protocol):
    """Semantic decisions needed by the Learning API."""

    def generate_course_graph(self, goal_title: str) -> CourseGraphDraft: ...

    def recommend_next_node(self, course: Mapping[str, Any]) -> RecommendationDraft: ...

    def create_learning_activity(
        self, course: Mapping[str, Any], node_id: str
    ) -> LearningActivity: ...

    def evaluate_evidence(
        self,
        course: Mapping[str, Any],
        node_id: str,
        answer: str,
        activity: LearningActivity | None = None,
    ) -> EvaluationDraft: ...


def _object(value: object, label: str) -> dict[str, Any]:
    if not isinstance(value, dict):
        raise LearningIntelligenceError(
            "INVALID_INTELLIGENCE_OUTPUT", f"{label} must be a JSON object"
        )
    return value


def _list(value: object, label: str) -> list[Any]:
    if not isinstance(value, list):
        raise LearningIntelligenceError(
            "INVALID_INTELLIGENCE_OUTPUT", f"{label} must be a JSON array"
        )
    return value


def _text(value: object, label: str) -> str:
    if not isinstance(value, str) or not value.strip():
        raise LearningIntelligenceError(
            "INVALID_INTELLIGENCE_OUTPUT", f"{label} must be a non-empty string"
        )
    return value.strip()


def _texts(value: object, label: str, *, allow_empty: bool = False) -> tuple[str, ...]:
    values = _list(value, label)
    if not allow_empty and not values:
        raise LearningIntelligenceError(
            "INVALID_INTELLIGENCE_OUTPUT", f"{label} must not be empty"
        )
    return tuple(_text(item, f"{label}[]") for item in values)


def _assert_acyclic(node_ids: set[str], edges: tuple[tuple[str, str], ...]) -> None:
    outgoing = {node_id: [] for node_id in node_ids}
    indegree = {node_id: 0 for node_id in node_ids}
    for source, target in edges:
        if source not in node_ids or target not in node_ids:
            raise LearningIntelligenceError(
                "INVALID_INTELLIGENCE_OUTPUT",
                f"edge references an unknown node: {source} -> {target}",
            )
        if source == target:
            raise LearningIntelligenceError(
                "INVALID_INTELLIGENCE_OUTPUT", "course graph cannot contain self edges"
            )
        outgoing[source].append(target)
        indegree[target] += 1
    queue = [node_id for node_id, degree in indegree.items() if degree == 0]
    visited = 0
    while queue:
        source = queue.pop()
        visited += 1
        for target in outgoing[source]:
            indegree[target] -= 1
            if indegree[target] == 0:
                queue.append(target)
    if visited != len(node_ids):
        raise LearningIntelligenceError(
            "INVALID_INTELLIGENCE_OUTPUT", "course graph must be acyclic"
        )


def _assert_tree_shaped(node_ids: set[str], edges: tuple[tuple[str, str], ...]) -> None:
    outgoing = {node_id: [] for node_id in node_ids}
    indegree = {node_id: 0 for node_id in node_ids}
    for source, target in edges:
        outgoing[source].append(target)
        indegree[target] += 1
    roots = [node_id for node_id, degree in indegree.items() if degree == 0]
    if len(roots) != 1:
        raise LearningIntelligenceError(
            "INVALID_INTELLIGENCE_OUTPUT", "course graph must have exactly one root node"
        )
    multi_parent_nodes = [node_id for node_id, degree in indegree.items() if degree > 1]
    if multi_parent_nodes:
        raise LearningIntelligenceError(
            "INVALID_INTELLIGENCE_OUTPUT",
            "course graph tree nodes cannot have multiple parents",
        )
    if len(edges) != len(node_ids) - 1:
        raise LearningIntelligenceError(
            "INVALID_INTELLIGENCE_OUTPUT",
            "course graph must be a tree with exactly one parent edge per non-root node",
        )
    if not any(len(targets) > 1 for targets in outgoing.values()):
        raise LearningIntelligenceError(
            "INVALID_INTELLIGENCE_OUTPUT",
            "course graph must branch instead of a single linear path",
        )
    visited = set()
    stack = roots[:]
    while stack:
        node_id = stack.pop()
        if node_id in visited:
            continue
        visited.add(node_id)
        stack.extend(outgoing[node_id])
    if visited != node_ids:
        raise LearningIntelligenceError(
            "INVALID_INTELLIGENCE_OUTPUT",
            "course graph must be connected from the single root node",
        )


def parse_course_graph(value: object) -> CourseGraphDraft:
    raw = _object(value, "course_graph")
    raw_nodes = _list(raw.get("nodes"), "nodes")
    if not 6 <= len(raw_nodes) <= 12:
        raise LearningIntelligenceError(
            "INVALID_INTELLIGENCE_OUTPUT", "course graph must contain 6 to 12 nodes"
        )
    nodes = tuple(
        CourseNodeDraft(
            _text(_object(item, "nodes[]").get("slug"), "nodes[].slug"),
            _text(_object(item, "nodes[]").get("title"), "nodes[].title"),
        )
        for item in raw_nodes
    )
    slugs = [node.slug for node in nodes]
    titles = [node.title.casefold() for node in nodes]
    if any(not _SLUG.fullmatch(slug) for slug in slugs):
        raise LearningIntelligenceError(
            "INVALID_INTELLIGENCE_OUTPUT",
            "node slugs must be lowercase ASCII kebab-case",
        )
    if len(set(slugs)) != len(slugs) or len(set(titles)) != len(titles):
        raise LearningIntelligenceError(
            "INVALID_INTELLIGENCE_OUTPUT", "node slugs and titles must be unique"
        )
    edges = tuple(
        CourseEdgeDraft(
            _text(_object(item, "edges[]").get("source_slug"), "edges[].source_slug"),
            _text(_object(item, "edges[]").get("target_slug"), "edges[].target_slug"),
        )
        for item in _list(raw.get("edges"), "edges")
    )
    pairs = tuple((edge.source_slug, edge.target_slug) for edge in edges)
    if len(set(pairs)) != len(pairs):
        raise LearningIntelligenceError(
            "INVALID_INTELLIGENCE_OUTPUT", "course graph contains duplicate edges"
        )
    _assert_acyclic(set(slugs), pairs)
    _assert_tree_shaped(set(slugs), pairs)
    return CourseGraphDraft(_text(raw.get("title"), "title"), nodes, edges)


def validate_course_graph_draft(draft: CourseGraphDraft) -> CourseGraphDraft:
    """Revalidate an injected draft at the application boundary."""

    return parse_course_graph({
        "title": draft.title,
        "nodes": [
            {"slug": node.slug, "title": node.title} for node in draft.nodes
        ],
        "edges": [
            {
                "source_slug": edge.source_slug,
                "target_slug": edge.target_slug,
            }
            for edge in draft.edges
        ],
    })


def parse_recommendation(value: object) -> RecommendationDraft:
    raw = _object(value, "recommendation")
    return RecommendationDraft(
        _text(raw.get("node_id"), "node_id"),
        _text(raw.get("reason"), "reason"),
    )


def validate_recommendation(
    recommendation: RecommendationDraft, course: Mapping[str, Any]
) -> RecommendationDraft:
    nodes = {
        _text(node.get("id"), "course.nodes[].id"): node
        for node in _list(course.get("nodes"), "course.nodes")
        if isinstance(node, dict)
    }
    if recommendation.node_id not in nodes:
        raise LearningIntelligenceError(
            "INVALID_INTELLIGENCE_OUTPUT", "recommended node is not in the course"
        )
    prerequisites = [
        edge.get("source_node_id")
        for edge in _list(course.get("edges", []), "course.edges")
        if isinstance(edge, dict) and edge.get("target_node_id") == recommendation.node_id
    ]
    incomplete = [
        node_id
        for node_id in prerequisites
        if node_id not in nodes or int(nodes[node_id].get("progress", 0)) < 100
    ]
    if incomplete:
        raise LearningIntelligenceError(
            "INVALID_INTELLIGENCE_OUTPUT",
            "recommended node has incomplete prerequisites: " + ", ".join(incomplete),
        )
    return recommendation


def parse_learning_activity(value: object) -> LearningActivity:
    raw = _object(value, "learning_activity")
    return LearningActivity(
        content=_text(raw.get("content"), "content"),
        insight=_text(raw.get("insight"), "insight"),
        question=_text(raw.get("question"), "question"),
        rubric=_texts(raw.get("rubric"), "rubric"),
    )


def validate_learning_activity(activity: LearningActivity) -> LearningActivity:
    return parse_learning_activity({
        "content": activity.content,
        "insight": activity.insight,
        "question": activity.question,
        "rubric": list(activity.rubric),
    })


def _parse_proposal(value: object) -> GraphProposalDraft:
    raw = _object(value, "proposal")
    nodes = tuple(
        ProposalNodeDraft(
            _text(_object(item, "proposed_nodes[]").get("id"), "proposed_nodes[].id"),
            _text(_object(item, "proposed_nodes[]").get("title"), "proposed_nodes[].title"),
        )
        for item in _list(raw.get("proposed_nodes"), "proposed_nodes")
    )
    edges = []
    for item in _list(raw.get("proposed_edges"), "proposed_edges"):
        pair = _list(item, "proposed_edges[]")
        if len(pair) != 2:
            raise LearningIntelligenceError(
                "INVALID_INTELLIGENCE_OUTPUT", "each proposed edge needs two node ids"
            )
        edges.append((_text(pair[0], "edge.source"), _text(pair[1], "edge.target")))
    return GraphProposalDraft(
        operation_type=_text(raw.get("operation_type"), "operation_type"),
        summary=_text(raw.get("summary"), "summary"),
        rationale=_text(raw.get("rationale"), "rationale"),
        affected_node_ids=_texts(raw.get("affected_node_ids"), "affected_node_ids"),
        proposed_nodes=nodes,
        proposed_edges=tuple(edges),
        progress_migration=_text(raw.get("progress_migration"), "progress_migration"),
        risks=_texts(raw.get("risks"), "risks", allow_empty=True),
    )


def parse_evaluation(value: object) -> EvaluationDraft:
    raw = _object(value, "evaluation")
    passed = raw.get("passed")
    score = raw.get("score")
    if not isinstance(passed, bool):
        raise LearningIntelligenceError(
            "INVALID_INTELLIGENCE_OUTPUT", "passed must be a boolean"
        )
    if isinstance(score, bool) or not isinstance(score, (int, float)):
        raise LearningIntelligenceError(
            "INVALID_INTELLIGENCE_OUTPUT", "score must be a number"
        )
    numeric_score = float(score)
    if not math.isfinite(numeric_score) or not 0 <= numeric_score <= 1:
        raise LearningIntelligenceError(
            "INVALID_INTELLIGENCE_OUTPUT", "score must be between 0 and 1"
        )
    proposal_value = raw.get("proposal")
    return EvaluationDraft(
        passed=passed,
        score=numeric_score,
        reason=_text(raw.get("reason"), "reason"),
        gaps=_texts(raw.get("gaps"), "gaps", allow_empty=True),
        proposal=None if proposal_value is None else _parse_proposal(proposal_value),
    )


def validate_evaluation_draft(
    draft: EvaluationDraft,
    course: Mapping[str, Any],
    selected_node_id: str,
) -> EvaluationDraft:
    """Validate semantic output references before any progress/graph mutation."""

    validated = parse_evaluation({
        "passed": draft.passed,
        "score": draft.score,
        "reason": draft.reason,
        "gaps": list(draft.gaps),
        "proposal": None if draft.proposal is None else {
            "operation_type": draft.proposal.operation_type,
            "summary": draft.proposal.summary,
            "rationale": draft.proposal.rationale,
            "affected_node_ids": list(draft.proposal.affected_node_ids),
            "proposed_nodes": [
                {"id": node.id, "title": node.title}
                for node in draft.proposal.proposed_nodes
            ],
            "proposed_edges": [list(edge) for edge in draft.proposal.proposed_edges],
            "progress_migration": draft.proposal.progress_migration,
            "risks": list(draft.proposal.risks),
        },
    })
    existing_nodes = {
        _text(node.get("id"), "course.nodes[].id")
        for node in _list(course.get("nodes"), "course.nodes")
        if isinstance(node, dict)
    }
    if selected_node_id not in existing_nodes:
        raise LearningIntelligenceError(
            "INVALID_INTELLIGENCE_OUTPUT", "evaluated node is not in the course"
        )
    proposal = validated.proposal
    if proposal is None:
        return validated
    if any(node_id not in existing_nodes for node_id in proposal.affected_node_ids):
        raise LearningIntelligenceError(
            "INVALID_INTELLIGENCE_OUTPUT", "proposal affects an unknown course node"
        )
    proposed_ids = [node.id for node in proposal.proposed_nodes]
    course_prefix = _text(course.get("id"), "course.id") + "--"
    if len(set(proposed_ids)) != len(proposed_ids):
        raise LearningIntelligenceError(
            "INVALID_INTELLIGENCE_OUTPUT", "proposal contains duplicate node ids"
        )
    if any(node_id in existing_nodes or not node_id.startswith(course_prefix) for node_id in proposed_ids):
        raise LearningIntelligenceError(
            "INVALID_INTELLIGENCE_OUTPUT",
            "proposed node ids must be new ids in the current course namespace",
        )
    combined_nodes = existing_nodes | set(proposed_ids)
    existing_edges = tuple(
        (edge.get("source_node_id"), edge.get("target_node_id"))
        for edge in _list(course.get("edges", []), "course.edges")
        if isinstance(edge, dict)
    )
    _assert_acyclic(combined_nodes, existing_edges + proposal.proposed_edges)
    return validated


T = TypeVar("T")
Script = T | Callable[..., T]


@dataclass
class ScriptedLearningIntelligence:
    """Explicitly injected deterministic test double; never a production fallback."""

    course_graph: Script[CourseGraphDraft]
    recommendation: Script[RecommendationDraft]
    activity: Script[LearningActivity]
    evaluation: Script[EvaluationDraft]

    @staticmethod
    def _resolve(script: Script[T], *args: object) -> T:
        return script(*args) if callable(script) else script

    def generate_course_graph(self, goal_title: str) -> CourseGraphDraft:
        return self._resolve(self.course_graph, goal_title)

    def recommend_next_node(self, course: Mapping[str, Any]) -> RecommendationDraft:
        return self._resolve(self.recommendation, course)

    def create_learning_activity(
        self, course: Mapping[str, Any], node_id: str
    ) -> LearningActivity:
        return self._resolve(self.activity, course, node_id)

    def evaluate_evidence(
        self,
        course: Mapping[str, Any],
        node_id: str,
        answer: str,
        activity: LearningActivity | None = None,
    ) -> EvaluationDraft:
        return self._resolve(self.evaluation, course, node_id, answer, activity)
