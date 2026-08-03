"""DeepSeek adapter implementing the learning intelligence port."""

from __future__ import annotations

import json
import os
from typing import Any, Mapping

from agent.core.definition import AgentDefinition
from agent.infrastructure import llm

from ..agents.catalog import LearningAgentCatalog
from ..application.intelligence import (
    CourseGraphDraft,
    EvaluationDraft,
    LearningActivity,
    LearningIntelligenceError,
    RecommendationDraft,
    parse_course_graph,
    parse_evaluation,
    parse_learning_activity,
    parse_recommendation,
    validate_course_graph_draft,
    validate_evaluation_draft,
    validate_learning_activity,
    validate_recommendation,
)


class DeepSeekLearningIntelligence:
    """Production adapter backed by the shared DeepSeek client."""

    _SYSTEM = (
        "You are the structured intelligence layer of a learning system. "
        "Return only one JSON object matching the requested schema. Never use Markdown."
    )

    def __init__(self, catalog: LearningAgentCatalog | None = None):
        self.catalog = catalog or LearningAgentCatalog.load()

    def _call(
        self,
        definition: AgentDefinition,
        instruction: str,
        payload: Mapping[str, Any],
    ) -> object:
        if not os.environ.get("DEEPSEEK_API_KEY"):
            raise LearningIntelligenceError(
                "LLM_NOT_CONFIGURED", "DEEPSEEK_API_KEY is not configured"
            )
        try:
            return llm.chat_json([
                {
                    "role": "system",
                    "content": self._SYSTEM + "\n\n" + definition.prompt_context(),
                },
                {
                    "role": "user",
                    "content": instruction + "\nINPUT:\n" + json.dumps(
                        payload, ensure_ascii=False, separators=(",", ":")
                    ),
                },
            ])
        except LearningIntelligenceError:
            raise
        except Exception as error:
            raise LearningIntelligenceError(
                "LEARNING_INTELLIGENCE_FAILED", f"DeepSeek request failed: {error}"
            ) from error

    def generate_course_graph(self, goal_title: str) -> CourseGraphDraft:
        value = self._call(
            self.catalog.graph_curator,
            "Generate a coherent prerequisite tree for this learning goal. Schema: "
            '{"title":string,"nodes":[{"slug":lowercase-kebab-case,"title":string}],'
            '"edges":[{"source_slug":string,"target_slug":string}]}. '
            "Return 6 to 12 unique nodes. An edge means source is the parent prerequisite of target. "
            "The graph must be a strict rooted tree: exactly one root, every other node has exactly one parent, no cross-links, no converging diamonds, and at least one parent has two or more children. "
            "The root should be the broadest foundation concept, and each deeper layer should be learned after its parent layer. "
            "Write the course title and every node title in the same natural language as goal_title.",
            {"goal_title": goal_title},
        )
        return validate_course_graph_draft(parse_course_graph(value))

    def recommend_next_node(self, course: Mapping[str, Any]) -> RecommendationDraft:
        value = self._call(
            self.catalog.planner,
            "Choose exactly one unmastered node whose prerequisites are all at 100%. "
            'Schema: {"node_id":string,"reason":string}. Use an exact input node id. '
            "Write reason in the same natural language as the course and node titles.",
            {"course": course},
        )
        return validate_recommendation(parse_recommendation(value), course)

    def create_learning_activity(
        self, course: Mapping[str, Any], node_id: str
    ) -> LearningActivity:
        value = self._call(
            self.catalog.tutor,
            "Create one focused learning activity for the selected node. Schema: "
            '{"content":string,"insight":string,"question":string,"rubric":[string]}. '
            "The question must test understanding rather than recall. Write all learner-facing "
            "fields in the same natural language as the course and selected node title.",
            {"course": course, "node_id": node_id},
        )
        return validate_learning_activity(parse_learning_activity(value))

    def evaluate_evidence(
        self,
        course: Mapping[str, Any],
        node_id: str,
        answer: str,
        activity: LearningActivity | None = None,
    ) -> EvaluationDraft:
        value = self._call(
            self.catalog.evaluator,
            "Evaluate the answer against the selected node and rubric. Score is 0..1. "
            'Schema: {"passed":boolean,"score":number,"reason":string,"gaps":[string],'
            '"proposal":null|{"operation_type":string,"summary":string,"rationale":string,'
            '"affected_node_ids":[string],"proposed_nodes":[{"id":string,"title":string}],'
            '"proposed_edges":[[string,string]],"progress_migration":string,"risks":[string]}}. '
            "Use proposal only when the course structure should change; it always requires human review. "
            "Every proposed node id must be a new exact id in the form "
            "<course.id>--<lowercase-kebab-slug>; edge endpoints must use exact existing "
            "or proposed node ids. Write reason, gaps, and all learner-facing proposal text "
            "in the same natural language as the course and selected node title.",
            {
                "course": course,
                "node_id": node_id,
                "answer": answer,
                "activity": None if activity is None else {
                    "content": activity.content,
                    "insight": activity.insight,
                    "question": activity.question,
                    "rubric": list(activity.rubric),
                },
            },
        )
        return validate_evaluation_draft(parse_evaluation(value), course, node_id)
