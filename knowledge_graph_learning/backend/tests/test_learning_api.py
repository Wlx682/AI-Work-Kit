"""Integration tests for the R4 local HTTP boundary."""

from __future__ import annotations

from http.server import ThreadingHTTPServer
import json
import os
from pathlib import Path
from tempfile import TemporaryDirectory
from threading import Thread
import unittest
from unittest.mock import patch
from urllib.error import HTTPError
from urllib.request import Request, urlopen

from knowledge_graph_learning.backend.application.service import (
    LearningApiError,
    LearningApiService,
)
from knowledge_graph_learning.backend.interfaces.http_api import (
    make_learning_api_handler,
)
from knowledge_graph_learning.backend.application.intelligence import (
    CourseEdgeDraft,
    CourseGraphDraft,
    CourseNodeDraft,
    EvaluationDraft,
    GraphProposalDraft,
    LearningActivity,
    ProposalNodeDraft,
    RecommendationDraft,
    ScriptedLearningIntelligence,
)


def scripted_intelligence():
    node_specs = (
        ("agent-foundations", "Agent Foundations"),
        ("runtime-basics", "Runtime Basics"),
        ("tool-boundaries", "Tool Boundaries"),
        ("trace-events", "Trace Events"),
        ("runtime-state", "Runtime State"),
        ("eval-harness", "Eval Harness"),
        ("checkpoint-interrupt", "Checkpoint & Interrupt"),
        ("replay-recovery", "Replay & Recovery"),
        ("production-signals", "Production Signals"),
        ("production-agent", "Production Agent"),
    )
    edge_specs = (
        ("agent-foundations", "runtime-basics"),
        ("agent-foundations", "tool-boundaries"),
        ("runtime-basics", "trace-events"),
        ("runtime-basics", "runtime-state"),
        ("tool-boundaries", "eval-harness"),
        ("runtime-state", "checkpoint-interrupt"),
        ("runtime-state", "replay-recovery"),
        ("eval-harness", "production-signals"),
        ("checkpoint-interrupt", "production-agent"),
    )
    return ScriptedLearningIntelligence(
        course_graph=lambda goal: CourseGraphDraft(
            goal,
            tuple(CourseNodeDraft(*spec) for spec in node_specs),
            tuple(CourseEdgeDraft(*spec) for spec in edge_specs),
        ),
        recommendation=lambda course: RecommendationDraft(
            next(node["id"] for node in course["nodes"] if node["slug"] == "agent-foundations"),
            "This foundation node has no unmet prerequisites.",
        ),
        activity=LearningActivity("content", "insight", "question", ("rubric",)),
        evaluation=lambda course, node_id, answer, activity: EvaluationDraft(
            True,
            0.9,
            "The answer satisfies the activity rubric.",
            ("One remaining gap.",),
            GraphProposalDraft(
                operation_type="expand_node",
                summary="Expand the selected concept into verifiable subskills.",
                rationale="The evidence is strong enough to move into deeper practice.",
                affected_node_ids=(node_id,),
                proposed_nodes=tuple(
                    ProposalNodeDraft(
                        f"{course['id']}--{slug}", title
                    )
                    for slug, title in (
                        ("checkpoint-anatomy", "Checkpoint Anatomy"),
                        ("interrupt-contract", "Interrupt Contract"),
                        ("resume-semantics", "Resume Semantics"),
                    )
                ),
                proposed_edges=tuple(
                    (node_id, f"{course['id']}--{slug}")
                    for slug in (
                        "checkpoint-anatomy",
                        "interrupt-contract",
                        "resume-semantics",
                    )
                ),
                progress_migration="Keep parent progress; start new nodes at zero.",
                risks=("The learning path will change.",),
            ),
        ),
    )


class LearningApiServiceTests(unittest.TestCase):
    def setUp(self):
        self.directory = TemporaryDirectory()
        self.service = LearningApiService(
            self.directory.name, intelligence=scripted_intelligence()
        )

    def tearDown(self):
        self.service.close()
        self.directory.cleanup()

    def _reach_proposal(self):
        created = self.service.create_goal("掌握生产级 Agent Runtime")
        course = created["course"]
        selected = next(node for node in course["nodes"] if node["slug"] == "runtime-state")
        session = self.service.start_session(course["id"], selected["id"])["session"]
        evidence = self.service.submit_evidence(
            session["id"],
            "State 保存恢复执行所需的当前事实，Trace 保存决策和工具调用历史。",
        )
        return course, evidence

    def test_create_goal_uses_generated_graph_with_zero_real_progress(self):
        created = self.service.create_goal("掌握分布式系统")

        self.assertEqual(created["course"]["title"], "掌握分布式系统")
        self.assertEqual(len(created["course"]["nodes"]), 10)
        self.assertEqual(
            {node["progress"] for node in created["course"]["nodes"]}, {0}
        )
        root = next(
            node for node in created["course"]["nodes"]
            if node["slug"] == "agent-foundations"
        )
        self.assertEqual(root["mastery_state"], "available")

    def test_invalid_generated_graph_is_rejected_before_any_domain_write(self):
        invalid = scripted_intelligence()
        invalid.course_graph = CourseGraphDraft(
            "Too Small",
            tuple(CourseNodeDraft(f"node-{index}", f"Node {index}") for index in range(5)),
            (),
        )
        with TemporaryDirectory() as directory:
            service = LearningApiService(directory, intelligence=invalid)
            try:
                with self.assertRaises(LearningApiError) as raised:
                    service.create_goal("invalid graph")
                persisted = list((Path(directory) / "learning").rglob("*.json"))
            finally:
                service.close()

        self.assertEqual(raised.exception.code, "INVALID_INTELLIGENCE_OUTPUT")
        self.assertEqual(persisted, [])

    def test_missing_deepseek_key_is_explicit_without_demo_fallback(self):
        with TemporaryDirectory() as directory, patch.dict(os.environ, {}, clear=True):
            service = LearningApiService(directory)
            try:
                with self.assertRaises(LearningApiError) as raised:
                    service.create_goal("learn compilers")
            finally:
                service.close()

        self.assertEqual(raised.exception.code, "LLM_NOT_CONFIGURED")
        self.assertEqual(raised.exception.status, 503)

    def test_recommendation_cannot_bypass_incomplete_prerequisites(self):
        invalid = scripted_intelligence()
        invalid.recommendation = lambda course: RecommendationDraft(
            next(node["id"] for node in course["nodes"] if node["slug"] == "runtime-basics"),
            "skip ahead",
        )
        with TemporaryDirectory() as directory:
            service = LearningApiService(directory, intelligence=invalid)
            try:
                course = service.create_goal("Agent Runtime")["course"]
                with self.assertRaises(LearningApiError) as raised:
                    service.get_recommendation(course["id"])
            finally:
                service.close()

        self.assertEqual(raised.exception.code, "INVALID_INTELLIGENCE_OUTPUT")

    def test_create_goal_session_and_evidence_pause_at_human_review(self):
        course, evidence = self._reach_proposal()

        self.assertEqual(len(course["nodes"]), 10)
        self.assertTrue(evidence["evaluation"]["passed"])
        self.assertEqual(evidence["evaluation"]["score"], 0.9)
        self.assertEqual(evidence["evaluation"]["gaps"], ["One remaining gap."])
        self.assertTrue(
            evidence["evidence"]["content_ref"].startswith("learning-evidence://")
        )
        self.assertEqual(
            self.service._load_evidence_content(evidence["evidence"]["id"]),
            "State 保存恢复执行所需的当前事实，Trace 保存决策和工具调用历史。",
        )
        self.assertEqual(evidence["runtime"]["status"], "paused")
        self.assertEqual(
            evidence["runtime"]["proposal"]["operation_type"], "expand_node"
        )
        self.assertEqual(
            [event["phase"] for event in evidence["runtime"]["events"]],
            ["run", "graph_curator", "learning_planner", "tutor", "evaluator", "human_review"],
        )
        role_events = {
            event["phase"]: event["payload"]
            for event in evidence["runtime"]["events"]
        }
        self.assertEqual(
            role_events["graph_curator"]["graph_context"]["agent_definition_id"],
            "learning-graph-curator",
        )
        self.assertEqual(
            role_events["learning_planner"]["learning_plan"]["agent_definition_id"],
            "learning-planner",
        )
        self.assertEqual(
            role_events["tutor"]["tutor_content"]["agent_definition_id"],
            "learning-tutor",
        )
        self.assertEqual(
            role_events["evaluator"]["evaluation"]["agent_definition_id"],
            "learning-evaluator",
        )
        self.assertTrue(all(
            "1.0.0" in str(payload) for payload in (
                role_events["graph_curator"],
                role_events["learning_planner"],
                role_events["tutor"],
                role_events["evaluator"],
            )
        ))

    def test_start_session_returns_and_persists_real_tutor_activity(self):
        course = self.service.create_goal("Agent Runtime")["course"]
        selected = next(node for node in course["nodes"] if node["slug"] == "runtime-state")

        started = self.service.start_session(course["id"], selected["id"])
        loaded = self.service._load_activity(started["session"]["id"])

        self.assertEqual(started["activity"]["question"], "question")
        self.assertEqual(started["activity"]["rubric"], ("rubric",))
        self.assertEqual(loaded.content, "content")

    def test_tutor_failure_does_not_create_a_session(self):
        failing = scripted_intelligence()
        failing.activity = LearningActivity("", "insight", "question", ("rubric",))
        with TemporaryDirectory() as directory:
            service = LearningApiService(directory, intelligence=failing)
            try:
                course = service.create_goal("Agent Runtime")["course"]
                selected = course["nodes"][0]
                with self.assertRaises(LearningApiError) as raised:
                    service.start_session(course["id"], selected["id"])
                session_files = list(
                    (Path(directory) / "learning" / "sessions").glob("*.json")
                )
            finally:
                service.close()

        self.assertEqual(raised.exception.code, "INVALID_INTELLIGENCE_OUTPUT")
        self.assertEqual(session_files, [])

    def test_invalid_evaluation_keeps_progress_and_proposal_unchanged(self):
        invalid = scripted_intelligence()
        invalid.evaluation = EvaluationDraft(True, 1.2, "invalid score", ())
        with TemporaryDirectory() as directory:
            service = LearningApiService(directory, intelligence=invalid)
            try:
                course = service.create_goal("Agent Runtime")["course"]
                selected = next(
                    node for node in course["nodes"] if node["slug"] == "runtime-state"
                )
                session = service.start_session(course["id"], selected["id"])["session"]
                with self.assertRaises(LearningApiError) as raised:
                    service.submit_evidence(session["id"], "answer")
                progress = service.repository.load_progress(selected["id"])
                eval_files = list(
                    (Path(directory) / "learning" / "eval_results").glob("*.json")
                )
                proposal_files = list(
                    (Path(directory) / "learning" / "graph_operation_proposals").glob("*.json")
                )
            finally:
                service.close()

        self.assertEqual(raised.exception.code, "INVALID_INTELLIGENCE_OUTPUT")
        self.assertEqual(progress.percent, 0)
        self.assertEqual(eval_files, [])
        self.assertEqual(proposal_files, [])

    def test_recommendation_returns_node_prerequisites_and_backend_reason(self):
        course = self.service.create_goal("掌握生产级 Agent Runtime")["course"]

        recommendation = self.service.get_recommendation(course["id"])

        self.assertEqual(recommendation["course_id"], course["id"])
        self.assertEqual(recommendation["node"]["slug"], "agent-foundations")
        self.assertEqual(recommendation["prerequisite_node_ids"], [])
        self.assertIn("no unmet prerequisites", recommendation["reason"])

    def test_approved_review_applies_three_nodes_once(self):
        course, evidence = self._reach_proposal()
        runtime = evidence["runtime"]

        reviewed = self.service.review_graph_update(
            runtime["thread_id"], runtime["run_id"], course["id"], True
        )

        self.assertEqual(reviewed["runtime"]["outcome"], "completed")
        self.assertEqual(len(reviewed["course"]["nodes"]), 13)
        titles = {node["title"] for node in reviewed["course"]["nodes"]}
        self.assertIn("Checkpoint Anatomy", titles)
        phases = [event["phase"] for event in reviewed["runtime"]["events"]]
        self.assertIn("apply_graph_update", phases)

    def test_rejected_review_preserves_the_graph(self):
        course, evidence = self._reach_proposal()
        runtime = evidence["runtime"]

        reviewed = self.service.review_graph_update(
            runtime["thread_id"], runtime["run_id"], course["id"], False
        )

        self.assertEqual(
            reviewed["runtime"]["outcome"], "completed_without_graph_update"
        )
        self.assertEqual(len(reviewed["course"]["nodes"]), 10)


class LearningApiHttpTests(unittest.TestCase):
    def test_http_flow_runs_goal_session_evidence_review_and_graph_apply(self):
        with TemporaryDirectory() as directory:
            service = LearningApiService(
                directory, intelligence=scripted_intelligence()
            )
            server = ThreadingHTTPServer(
                ("127.0.0.1", 0), make_learning_api_handler(service)
            )
            thread = Thread(target=server.serve_forever, daemon=True)
            thread.start()
            base_url = f"http://127.0.0.1:{server.server_port}"
            try:
                health = self._request(f"{base_url}/api/learning/health")
                created = self._request(
                    f"{base_url}/api/learning/goals",
                    {"title": "Agent Runtime"},
                )
                course = self._request(
                    f"{base_url}/api/learning/courses/{created['course']['id']}"
                )
                recommendation = self._request(
                    f"{base_url}/api/learning/courses/{course['id']}/recommendation"
                )
                selected = next(
                    node for node in course["nodes"] if node["slug"] == "runtime-state"
                )
                session = self._request(
                    f"{base_url}/api/learning/sessions",
                    {"course_id": course["id"], "node_id": selected["id"]},
                )["session"]
                evidence = self._request(
                    f"{base_url}/api/learning/evidence",
                    {
                        "session_id": session["id"],
                        "answer": "State 保存恢复执行所需事实，Trace 保存历史证据。",
                    },
                )
                runtime = evidence["runtime"]
                reviewed = self._request(
                    f"{base_url}/api/learning/reviews",
                    {
                        "thread_id": runtime["thread_id"],
                        "parent_run_id": runtime["run_id"],
                        "course_id": course["id"],
                        "approved": True,
                    },
                )
            finally:
                server.shutdown()
                server.server_close()
                service.close()
                thread.join(timeout=2)

        self.assertEqual(health["status"], "ok")
        self.assertEqual(course["title"], "Agent Runtime")
        self.assertEqual(len(course["nodes"]), 10)
        self.assertEqual(
            recommendation["node"]["slug"], "agent-foundations"
        )
        self.assertEqual(len(recommendation["prerequisite_node_ids"]), 0)
        self.assertEqual(runtime["status"], "paused")
        self.assertEqual(reviewed["runtime"]["outcome"], "completed")
        self.assertEqual(len(reviewed["course"]["nodes"]), 13)

    @staticmethod
    def _request(url: str, payload: dict | None = None) -> dict:
        data = None if payload is None else json.dumps(payload).encode("utf-8")
        request = Request(
            url,
            data=data,
            headers={"Content-Type": "application/json"},
            method="GET" if payload is None else "POST",
        )
        try:
            with urlopen(request, timeout=5) as response:
                return json.loads(response.read())
        except HTTPError as error:  # pragma: no cover - improves failure diagnostics
            raise AssertionError(error.read().decode("utf-8")) from error


if __name__ == "__main__":
    unittest.main()
