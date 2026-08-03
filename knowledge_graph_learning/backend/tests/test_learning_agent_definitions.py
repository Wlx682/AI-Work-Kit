"""R3 AgentDefinition integration tests for all R4 learning roles."""

import unittest

from knowledge_graph_learning.backend.agents import LearningAgentCatalog, LearningAgentTeam


class LearningAgentDefinitionTests(unittest.TestCase):
    def test_loads_four_distinct_versioned_toolless_definitions(self):
        catalog = LearningAgentCatalog.load()

        self.assertEqual(
            {definition.id for definition in catalog.all},
            {
                "learning-graph-curator",
                "learning-planner",
                "learning-tutor",
                "learning-evaluator",
            },
        )
        self.assertTrue(all(definition.version == "1.0.0" for definition in catalog.all))
        self.assertTrue(all(definition.tools == () for definition in catalog.all))
        self.assertTrue(all(definition.instructions for definition in catalog.all))

    def test_team_runtime_roles_emit_definition_identity_and_version(self):
        team = LearningAgentTeam()
        roles = team.runtime_roles(lambda course_id: {
            "id": course_id,
            "nodes": [{"id": "node-1"}],
        })
        request = {
            "course_id": "course-1",
            "concept_id": "node-1",
            "activity": {
                "content": "content",
                "insight": "insight",
                "question": "question",
                "rubric": ["criterion"],
            },
            "evaluation": {
                "passed": True,
                "score": 0.9,
                "reason": "reason",
                "gaps": [],
            },
            "graph_update_proposal": None,
        }
        state = {"request": request}

        outputs = (
            roles.graph_curator(state),
            roles.learning_planner(state),
            roles.tutor(state),
            roles.evaluator(state),
        )

        self.assertEqual(
            [output["agent_definition_id"] for output in outputs],
            [definition.id for definition in team.catalog.all],
        )
        self.assertTrue(
            all(output["agent_definition_version"] == "1.0.0" for output in outputs)
        )


if __name__ == "__main__":
    unittest.main()
