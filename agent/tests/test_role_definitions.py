import unittest
from unittest.mock import patch

from agent.agent_definition import AgentDefinition
from agent.roles import Executor, Planner, Predictor, Reviewer


def definition(identifier: str, tools: tuple[str, ...] = ()) -> AgentDefinition:
    return AgentDefinition(
        id=identifier,
        role=identifier,
        goal="test",
        tools=tools,
        acceptance=("finish",),
        instructions="test instructions",
    )


class RoleDefinitionTests(unittest.TestCase):
    def test_default_roles_load_distinct_definitions(self):
        self.assertEqual(Planner().definition.id, "planner")
        self.assertEqual(Predictor().definition.id, "predictor")
        self.assertEqual(Executor().definition.id, "executor")
        self.assertEqual(Reviewer().definition.id, "reviewer")

    def test_roles_pass_their_definition_to_shared_capabilities(self):
        planner = Planner(definition("planner"))
        predictor = Predictor(definition("predictor"))
        executor = Executor(definition("executor", ("read_file",)))
        reviewer = Reviewer(definition("reviewer"))

        with (
            patch("agent.roles.planner.planning.make_plan", return_value=["step"]) as make_plan,
            patch("agent.roles.predictor.world_model.predict", return_value=[]) as predict,
            patch("agent.roles.executor.act.run_step", return_value="done") as run_step,
            patch("agent.roles.reviewer.reviewing.review", return_value={"verdict": "accept"}) as review,
        ):
            planner.make_plan("task")
            predictor.evaluate(["step"])
            executor.run(["step"])
            reviewer.review("task", ["step"], ["done"])

        self.assertIs(make_plan.call_args.args[2], planner.definition)
        self.assertIs(predict.call_args.args[2], predictor.definition)
        self.assertIs(run_step.call_args.args[2], executor.definition)
        self.assertEqual(review.call_args.args[3], reviewer.definition.acceptance)


if __name__ == "__main__":
    unittest.main()
