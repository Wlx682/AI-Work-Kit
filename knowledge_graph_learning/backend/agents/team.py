"""Definition-bound learning role objects and Runtime role assembly."""

from __future__ import annotations

from typing import Any, Callable

from agent.roles.base import BaseAgent

from ..orchestration.runtime import LearningRuntimeRoles
from .catalog import LearningAgentCatalog


CourseReader = Callable[[str], dict[str, Any]]


class LearningRoleAgent(BaseAgent):
    def _policy_metadata(self) -> dict[str, str]:
        return {
            "agent_definition_id": self.definition.id,
            "agent_definition_version": self.definition.version,
        }


class GraphCuratorAgent(LearningRoleAgent):
    name = "GraphCurator"
    definition_id = "learning-graph-curator"

    def observe(self, state: dict[str, Any], course_reader: CourseReader) -> dict[str, Any]:
        request = state["request"]
        graph = course_reader(request["course_id"])
        return {
            **self._policy_metadata(),
            "course_id": graph["id"],
            "node_count": len(graph["nodes"]),
            "selected_node_id": request["concept_id"],
        }


class LearningPlannerAgent(LearningRoleAgent):
    name = "LearningPlanner"
    definition_id = "learning-planner"

    def plan(self, state: dict[str, Any]) -> dict[str, Any]:
        request = state["request"]
        activity = request["activity"]
        return {
            **self._policy_metadata(),
            "next_concept_id": request["concept_id"],
            "objective": activity["question"],
            "rubric": activity["rubric"],
        }


class TutorAgent(LearningRoleAgent):
    name = "Tutor"
    definition_id = "learning-tutor"

    def teach(self, state: dict[str, Any]) -> dict[str, Any]:
        return {
            **self._policy_metadata(),
            **state["request"]["activity"],
        }


class EvaluatorAgent(LearningRoleAgent):
    name = "Evaluator"
    definition_id = "learning-evaluator"

    def evaluate(self, state: dict[str, Any]) -> dict[str, Any]:
        request = state["request"]
        return {
            **self._policy_metadata(),
            **request["evaluation"],
            "graph_update_proposal": request["graph_update_proposal"],
        }


class LearningAgentTeam:
    """The only assembly point for learning policies and Runtime roles."""

    def __init__(self, catalog: LearningAgentCatalog | None = None):
        self.catalog = catalog or LearningAgentCatalog.load()
        self.graph_curator = GraphCuratorAgent(self.catalog.graph_curator)
        self.planner = LearningPlannerAgent(self.catalog.planner)
        self.tutor = TutorAgent(self.catalog.tutor)
        self.evaluator = EvaluatorAgent(self.catalog.evaluator)

    def runtime_roles(self, course_reader: CourseReader) -> LearningRuntimeRoles:
        return LearningRuntimeRoles(
            graph_curator=lambda state: self.graph_curator.observe(state, course_reader),
            learning_planner=self.planner.plan,
            tutor=self.tutor.teach,
            evaluator=self.evaluator.evaluate,
        )
