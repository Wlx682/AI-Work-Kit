"""Offline contract tests for the real DeepSeek learning intelligence port."""

import os
import unittest
from unittest.mock import patch

from knowledge_graph_learning.backend.application.intelligence import (
    CourseGraphDraft,
    CourseNodeDraft,
    EvaluationDraft,
    LearningActivity,
    LearningIntelligenceError,
    RecommendationDraft,
    ScriptedLearningIntelligence,
    parse_course_graph,
    parse_evaluation,
    validate_recommendation,
)
from knowledge_graph_learning.backend.infrastructure.deepseek_intelligence import (
    DeepSeekLearningIntelligence,
)


def valid_graph_json():
    nodes = [
        {"slug": slug, "title": title}
        for slug, title in (
            ("python-basics", "Python Basics"),
            ("data-models", "Data Models"),
            ("api-design", "API Design"),
            ("testing", "Testing"),
            ("observability", "Observability"),
            ("production", "Production"),
        )
    ]
    return {
        "title": "Backend Engineering",
        "nodes": nodes,
        "edges": [
            {"source_slug": "python-basics", "target_slug": "data-models"},
            {"source_slug": "python-basics", "target_slug": "api-design"},
            {"source_slug": "data-models", "target_slug": "testing"},
            {"source_slug": "api-design", "target_slug": "observability"},
            {"source_slug": "observability", "target_slug": "production"},
        ],
    }


class LearningIntelligenceValidationTests(unittest.TestCase):
    def test_parses_a_valid_course_tree(self):
        graph = parse_course_graph(valid_graph_json())

        self.assertEqual(graph.title, "Backend Engineering")
        self.assertEqual(len(graph.nodes), 6)
        self.assertEqual(graph.edges[-1].target_slug, "production")

    def test_rejects_a_linear_course_graph(self):
        raw = valid_graph_json()
        raw["edges"] = [
            {"source_slug": "python-basics", "target_slug": "data-models"},
            {"source_slug": "data-models", "target_slug": "api-design"},
            {"source_slug": "api-design", "target_slug": "testing"},
            {"source_slug": "testing", "target_slug": "observability"},
            {"source_slug": "observability", "target_slug": "production"},
        ]

        with self.assertRaisesRegex(LearningIntelligenceError, "branch"):
            parse_course_graph(raw)

    def test_rejects_a_converging_dag_course_graph(self):
        raw = valid_graph_json()
        raw["edges"] = [
            {"source_slug": "python-basics", "target_slug": "data-models"},
            {"source_slug": "python-basics", "target_slug": "api-design"},
            {"source_slug": "data-models", "target_slug": "testing"},
            {"source_slug": "api-design", "target_slug": "testing"},
            {"source_slug": "testing", "target_slug": "observability"},
            {"source_slug": "observability", "target_slug": "production"},
        ]

        with self.assertRaisesRegex(LearningIntelligenceError, "multiple parents"):
            parse_course_graph(raw)

    def test_rejects_a_cyclic_course_graph(self):
        raw = valid_graph_json()
        raw["edges"].append(
            {"source_slug": "production", "target_slug": "python-basics"}
        )

        with self.assertRaisesRegex(LearningIntelligenceError, "acyclic"):
            parse_course_graph(raw)

    def test_rejects_recommendation_with_incomplete_prerequisite(self):
        course = {
            "nodes": [
                {"id": "a", "progress": 50},
                {"id": "b", "progress": 0},
            ],
            "edges": [{"source_node_id": "a", "target_node_id": "b"}],
        }

        with self.assertRaisesRegex(LearningIntelligenceError, "incomplete"):
            validate_recommendation(RecommendationDraft("b", "next"), course)

    def test_rejects_out_of_range_evaluation_score(self):
        with self.assertRaisesRegex(LearningIntelligenceError, "between 0 and 1"):
            parse_evaluation({
                "passed": True,
                "score": 1.2,
                "reason": "Strong answer",
                "gaps": [],
                "proposal": None,
            })


class DeepSeekLearningIntelligenceTests(unittest.TestCase):
    def test_missing_key_is_explicit_and_does_not_call_llm(self):
        intelligence = DeepSeekLearningIntelligence()
        with patch.dict(os.environ, {}, clear=True), patch(
            "knowledge_graph_learning.backend.infrastructure.deepseek_intelligence.llm.chat_json"
        ) as chat_json:
            with self.assertRaises(LearningIntelligenceError) as raised:
                intelligence.generate_course_graph("learn compilers")

        self.assertEqual(raised.exception.code, "LLM_NOT_CONFIGURED")
        chat_json.assert_not_called()

    def test_course_generation_uses_agent_llm_and_validates_result(self):
        intelligence = DeepSeekLearningIntelligence()
        with patch.dict(os.environ, {"DEEPSEEK_API_KEY": "test-key"}), patch(
            "knowledge_graph_learning.backend.infrastructure.deepseek_intelligence.llm.chat_json", return_value=valid_graph_json()
        ) as chat_json:
            graph = intelligence.generate_course_graph("learn backend engineering")

        self.assertEqual(len(graph.nodes), 6)
        self.assertEqual(chat_json.call_count, 1)
        request = chat_json.call_args.args[0]
        self.assertIn("learn backend engineering", request[-1]["content"])
        self.assertIn("strict rooted tree", request[-1]["content"])
        self.assertIn("learning-graph-curator", request[0]["content"])
        self.assertIn("策略版本：1.0.0", request[0]["content"])

    def test_each_structured_call_uses_its_own_declarative_agent(self):
        intelligence = DeepSeekLearningIntelligence()
        course = {
            "id": "course-1",
            "nodes": [{
                "id": "node-1",
                "title": "Node One",
                "progress": 0,
                "mastery_state": "available",
            }],
            "edges": [],
        }
        with patch.dict(os.environ, {"DEEPSEEK_API_KEY": "test-key"}), patch(
            "knowledge_graph_learning.backend.infrastructure.deepseek_intelligence.llm.chat_json",
            side_effect=[
                {"node_id": "node-1", "reason": "No unmet prerequisites."},
                {
                    "content": "content",
                    "insight": "insight",
                    "question": "question",
                    "rubric": ["criterion"],
                },
                {
                    "passed": True,
                    "score": 0.9,
                    "reason": "meets rubric",
                    "gaps": [],
                    "proposal": None,
                },
            ],
        ) as chat_json:
            intelligence.recommend_next_node(course)
            activity = intelligence.create_learning_activity(course, "node-1")
            intelligence.evaluate_evidence(course, "node-1", "answer", activity)

        system_prompts = [
            call.args[0][0]["content"] for call in chat_json.call_args_list
        ]
        self.assertIn("learning-planner", system_prompts[0])
        self.assertIn("learning-tutor", system_prompts[1])
        self.assertIn("learning-evaluator", system_prompts[2])

    def test_llm_transport_failure_is_typed(self):
        intelligence = DeepSeekLearningIntelligence()
        with patch.dict(os.environ, {"DEEPSEEK_API_KEY": "test-key"}), patch(
            "knowledge_graph_learning.backend.infrastructure.deepseek_intelligence.llm.chat_json", side_effect=TimeoutError("slow")
        ):
            with self.assertRaises(LearningIntelligenceError) as raised:
                intelligence.generate_course_graph("learn databases")

        self.assertEqual(raised.exception.code, "LEARNING_INTELLIGENCE_FAILED")

    def test_scripted_double_requires_explicit_injection(self):
        graph = CourseGraphDraft(
            "Test Course",
            tuple(CourseNodeDraft(f"node-{index}", f"Node {index}") for index in range(6)),
            (),
        )
        scripted = ScriptedLearningIntelligence(
            course_graph=graph,
            recommendation=RecommendationDraft("node-0", "scripted reason"),
            activity=LearningActivity("content", "insight", "question", ("rubric",)),
            evaluation=EvaluationDraft(True, 0.9, "reason", ()),
        )

        self.assertIs(scripted.generate_course_graph("anything"), graph)
        self.assertEqual(scripted.evaluate_evidence({}, "node-0", "answer").score, 0.9)


if __name__ == "__main__":
    unittest.main()
