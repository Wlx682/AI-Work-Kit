"""Single loader and registry for all declarative learning Agent policies."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

from agent.core.definition import AgentDefinition, load_agent_definition


POLICY_DIRECTORY = Path(__file__).parent


@dataclass(frozen=True)
class LearningAgentCatalog:
    graph_curator: AgentDefinition
    planner: AgentDefinition
    tutor: AgentDefinition
    evaluator: AgentDefinition

    @classmethod
    def load(cls) -> "LearningAgentCatalog":
        catalog = cls(
            graph_curator=load_agent_definition(
                "learning-graph-curator",
                definitions_directory=POLICY_DIRECTORY / "definitions",
                prompts_directory=POLICY_DIRECTORY / "prompts",
            ),
            planner=load_agent_definition(
                "learning-planner",
                definitions_directory=POLICY_DIRECTORY / "definitions",
                prompts_directory=POLICY_DIRECTORY / "prompts",
            ),
            tutor=load_agent_definition(
                "learning-tutor",
                definitions_directory=POLICY_DIRECTORY / "definitions",
                prompts_directory=POLICY_DIRECTORY / "prompts",
            ),
            evaluator=load_agent_definition(
                "learning-evaluator",
                definitions_directory=POLICY_DIRECTORY / "definitions",
                prompts_directory=POLICY_DIRECTORY / "prompts",
            ),
        )
        identifiers = [definition.id for definition in catalog.all]
        if len(set(identifiers)) != len(identifiers):
            raise ValueError("learning agent definition ids must be unique")
        return catalog

    @property
    def all(self) -> tuple[AgentDefinition, ...]:
        return self.graph_curator, self.planner, self.tutor, self.evaluator
