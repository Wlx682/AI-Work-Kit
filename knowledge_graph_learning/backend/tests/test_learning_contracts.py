import unittest
from pathlib import Path
from tempfile import TemporaryDirectory

import knowledge_graph_learning.backend.domain.contracts as learning_contracts
from agent.core.models import RunEvent, RunResult
from agent.infrastructure.traces import TraceStore

from knowledge_graph_learning.backend.domain.contracts import (
    AppliedGraphOperation,
    ConceptNode,
    ContractApiResult,
    Course,
    Evidence,
    EvalResult,
    GraphOperationConfirmation,
    GraphOperationProposal,
    GraphOperationRequest,
    JsonLearningRepository,
    LearningGoal,
    LearningSession,
    NodeProgress,
    LEARNING_LOOP_EVENT_TYPES,
    apply_eval_result_to_progress,
    apply_graph_operation,
    apply_graph_operation_api,
    create_graph_operation_request,
    confirm_graph_operation,
    propose_graph_operation,
    recompute_parent_progress,
    start_node_learning,
    submit_eval_progress,
    submit_evidence,
)


class LearningContractTests(unittest.TestCase):
    def test_main_loop_event_types_are_ordered(self):
        self.assertEqual(
            LEARNING_LOOP_EVENT_TYPES,
            (
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
            ),
        )

    def _completed_learning_loop_run_result(self, run_id):
        events = tuple(
            RunEvent(
                sequence=index + 1,
                run_id=run_id,
                phase="test",
                status="completed" if event_type == "run_completed" else "recorded",
                payload={
                    "event_type": event_type,
                    **(
                        {
                            "terminal_status": "completed",
                            "reason": "no selectable learning node",
                            "next_action": "no remaining learning nodes",
                        }
                        if event_type == "run_completed"
                        else {}
                    ),
                },
            )
            for index, event_type in enumerate(LEARNING_LOOP_EVENT_TYPES)
        )
        return RunResult(
            run_id=run_id,
            task="completed learning loop",
            outcome="completed",
            events=events,
        )

    def _completed_learning_loop_run_result_with_replay_payload(self, run_id):
        request_id = f"request-{run_id}"
        proposal_id = f"proposal-{run_id}"
        graph_payloads = {
            "graph_operation_requested": {
                "request_id": request_id,
                "course_id": "course-1",
                "node_id": "trace-event",
                "operation_type": "expand",
                "user_intent": "这个点不够细，展开下一级",
                "source": "menu",
            },
            "graph_operation_proposed": {
                "proposal_id": proposal_id,
                "request_id": request_id,
                "operation_type": "expand",
                "summary": "expand trace event into replay-focused subnodes",
                "rationale": "learner needs finer trace replay boundaries",
                "affected_nodes": ("trace-event",),
                "proposed_nodes": ("trace-payload-schema",),
                "proposed_edges": (("trace-event", "trace-payload-schema"),),
                "requires_confirmation": True,
            },
            "graph_operation_confirmed": {
                "proposal_id": proposal_id,
                "request_id": request_id,
                "confirmed_by": "user",
                "changes_requested": (),
            },
            "graph_update_applied": {
                "proposal_id": proposal_id,
                "request_id": request_id,
                "operation_type": "expand",
                "created_nodes": ("trace-payload-schema",),
            },
            "run_completed": {
                "terminal_status": "completed",
                "reason": "no selectable learning node",
                "next_action": "no remaining learning nodes",
            },
        }
        events = tuple(
            RunEvent(
                sequence=index + 1,
                run_id=run_id,
                phase="test",
                status="completed" if event_type == "run_completed" else "recorded",
                payload={"event_type": event_type, **graph_payloads.get(event_type, {})},
            )
            for index, event_type in enumerate(LEARNING_LOOP_EVENT_TYPES)
        )
        return RunResult(
            run_id=run_id,
            task="completed learning loop",
            outcome="completed",
            events=events,
        )

    def test_learning_loop_replay_regression_summary_fails_when_trace_is_incomplete(self):
        summarize_regression = getattr(learning_contracts, "summarize_learning_loop_replay_regression", None)
        summary_type = getattr(learning_contracts, "LearningLoopReplayRegressionSummary", None)
        self.assertIsNotNone(summarize_regression)
        self.assertIsNotNone(summary_type)

        summary = summarize_regression(
            RunResult(
                run_id="run-r4",
                task="incomplete learning loop",
                outcome="failed",
                events=(),
            ),
            learning_contracts.GraphOperationReplay(),
        )

        self.assertEqual(
            summary,
            learning_contracts.LearningLoopReplayRegressionSummary(
                run_id="run-r4",
                terminal_status="missing",
                completion_reason="",
                graph_replay_completed=False,
                replayed_request_count=0,
                replayed_proposal_count=0,
                replayed_confirmation_count=0,
                replayed_applied_count=0,
                trace_matches_contract=False,
                final_learning_completed=False,
                remaining_selectable_nodes=1,
                regression_passed=False,
                report="Learning loop replay regression incomplete.",
            ),
        )

    def test_golden_learning_task_report_passes_when_summary_matches_expectations(self):
        task_type = getattr(learning_contracts, "GoldenLearningTask", None)
        report_type = getattr(learning_contracts, "GoldenLearningTaskReport", None)
        build_report = getattr(learning_contracts, "build_golden_learning_task_report", None)
        self.assertIsNotNone(task_type)
        self.assertIsNotNone(report_type)
        self.assertIsNotNone(build_report)
        task = task_type(
            id="golden-r4-main-loop",
            title="学习闭环图谱扩展回归",
            goal_id="goal-1",
            course_id="course-1",
            expected_terminal_status="completed",
            expected_completion_reason="no selectable learning node",
            expected_graph_operation_count=1,
            expected_remaining_selectable_nodes=0,
        )
        summary = learning_contracts.LearningLoopReplayRegressionSummary(
            run_id="run-r4",
            terminal_status="completed",
            completion_reason="no selectable learning node",
            graph_replay_completed=True,
            replayed_request_count=1,
            replayed_proposal_count=1,
            replayed_confirmation_count=1,
            replayed_applied_count=1,
            trace_matches_contract=True,
            final_learning_completed=True,
            remaining_selectable_nodes=0,
            regression_passed=True,
            report="Learning loop completed; graph expansion replayed; no remaining selectable nodes.",
        )

        report = build_report(task, summary)

        self.assertEqual(
            report,
            report_type(
                task_id="golden-r4-main-loop",
                task_title="学习闭环图谱扩展回归",
                goal_id="goal-1",
                course_id="course-1",
                run_id="run-r4",
                expected_terminal_status="completed",
                actual_terminal_status="completed",
                expected_completion_reason="no selectable learning node",
                actual_completion_reason="no selectable learning node",
                expected_graph_operation_count=1,
                actual_graph_operation_count=1,
                expected_remaining_selectable_nodes=0,
                actual_remaining_selectable_nodes=0,
                trace_matches_contract=True,
                graph_replay_completed=True,
                regression_passed=True,
                report="Golden learning task passed: golden-r4-main-loop.",
            ),
        )

    def test_golden_learning_task_report_fails_when_summary_misses_expectations(self):
        task_type = getattr(learning_contracts, "GoldenLearningTask", None)
        report_type = getattr(learning_contracts, "GoldenLearningTaskReport", None)
        build_report = getattr(learning_contracts, "build_golden_learning_task_report", None)
        self.assertIsNotNone(task_type)
        self.assertIsNotNone(report_type)
        self.assertIsNotNone(build_report)
        task = task_type(
            id="golden-r4-main-loop",
            title="学习闭环图谱扩展回归",
            goal_id="goal-1",
            course_id="course-1",
            expected_terminal_status="completed",
            expected_completion_reason="no selectable learning node",
            expected_graph_operation_count=1,
            expected_remaining_selectable_nodes=0,
        )
        summary = learning_contracts.LearningLoopReplayRegressionSummary(
            run_id="run-r4",
            terminal_status="completed",
            completion_reason="no selectable learning node",
            graph_replay_completed=False,
            replayed_request_count=1,
            replayed_proposal_count=1,
            replayed_confirmation_count=0,
            replayed_applied_count=0,
            trace_matches_contract=True,
            final_learning_completed=False,
            remaining_selectable_nodes=1,
            regression_passed=False,
            report="Learning loop replay regression incomplete.",
        )

        report = build_report(task, summary)

        self.assertEqual(
            report,
            report_type(
                task_id="golden-r4-main-loop",
                task_title="学习闭环图谱扩展回归",
                goal_id="goal-1",
                course_id="course-1",
                run_id="run-r4",
                expected_terminal_status="completed",
                actual_terminal_status="completed",
                expected_completion_reason="no selectable learning node",
                actual_completion_reason="no selectable learning node",
                expected_graph_operation_count=1,
                actual_graph_operation_count=0,
                expected_remaining_selectable_nodes=0,
                actual_remaining_selectable_nodes=1,
                trace_matches_contract=True,
                graph_replay_completed=False,
                regression_passed=False,
                report="Golden learning task failed: golden-r4-main-loop.",
            ),
        )

    def test_json_repository_saves_golden_learning_task_and_report(self):
        task = learning_contracts.GoldenLearningTask(
            id="golden-main-loop",
            title="学习闭环图谱扩展回归",
            goal_id="goal-1",
            course_id="course-1",
            expected_terminal_status="completed",
            expected_completion_reason="no selectable learning node",
            expected_graph_operation_count=1,
            expected_remaining_selectable_nodes=0,
        )
        report = learning_contracts.GoldenLearningTaskReport(
            task_id="golden-main-loop",
            task_title="学习闭环图谱扩展回归",
            goal_id="goal-1",
            course_id="course-1",
            run_id="run-1",
            expected_terminal_status="completed",
            actual_terminal_status="completed",
            expected_completion_reason="no selectable learning node",
            actual_completion_reason="no selectable learning node",
            expected_graph_operation_count=1,
            actual_graph_operation_count=1,
            expected_remaining_selectable_nodes=0,
            actual_remaining_selectable_nodes=0,
            trace_matches_contract=True,
            graph_replay_completed=True,
            regression_passed=True,
            report="Golden learning task passed: golden-main-loop.",
        )

        with TemporaryDirectory() as directory:
            writer = JsonLearningRepository(directory)
            writer.save_golden_learning_task(task)
            writer.save_golden_learning_task_report(report)

            reader = JsonLearningRepository(directory)
            loaded_task = reader.load_golden_learning_task("golden-main-loop")
            loaded_report = reader.load_golden_learning_task_report("golden-main-loop", "run-1")

        self.assertEqual(loaded_task, task)
        self.assertEqual(loaded_report, report)

    def test_golden_learning_task_batch_report_summarizes_pass_fail_reports(self):
        batch_type = getattr(learning_contracts, "GoldenLearningTaskBatchReport", None)
        build_batch_report = getattr(learning_contracts, "build_golden_learning_task_batch_report", None)
        self.assertIsNotNone(batch_type)
        self.assertIsNotNone(build_batch_report)
        passed_report = learning_contracts.GoldenLearningTaskReport(
            task_id="golden-pass",
            task_title="通过任务",
            goal_id="goal-1",
            course_id="course-1",
            run_id="run-pass",
            expected_terminal_status="completed",
            actual_terminal_status="completed",
            expected_completion_reason="no selectable learning node",
            actual_completion_reason="no selectable learning node",
            expected_graph_operation_count=1,
            actual_graph_operation_count=1,
            expected_remaining_selectable_nodes=0,
            actual_remaining_selectable_nodes=0,
            trace_matches_contract=True,
            graph_replay_completed=True,
            regression_passed=True,
            report="Golden learning task passed: golden-pass.",
        )
        failed_report = learning_contracts.GoldenLearningTaskReport(
            task_id="golden-fail",
            task_title="失败任务",
            goal_id="goal-1",
            course_id="course-1",
            run_id="run-fail",
            expected_terminal_status="completed",
            actual_terminal_status="missing",
            expected_completion_reason="no selectable learning node",
            actual_completion_reason="",
            expected_graph_operation_count=1,
            actual_graph_operation_count=0,
            expected_remaining_selectable_nodes=0,
            actual_remaining_selectable_nodes=1,
            trace_matches_contract=False,
            graph_replay_completed=False,
            regression_passed=False,
            report="Golden learning task failed: golden-fail.",
        )

        batch_report = build_batch_report("suite-main-loop", (passed_report, failed_report))

        self.assertEqual(
            batch_report,
            batch_type(
                suite_id="suite-main-loop",
                total_count=2,
                passed_count=1,
                failed_count=1,
                failed_task_ids=("golden-fail",),
                regression_passed=False,
                reports=(passed_report, failed_report),
                report="Golden learning task suite failed: 1/2 passed.",
            ),
        )

    def test_golden_learning_task_batch_report_builds_from_run_results_and_replays(self):
        run_type = getattr(learning_contracts, "GoldenLearningTaskRun", None)
        build_from_replays = getattr(
            learning_contracts,
            "build_golden_learning_task_batch_report_from_replays",
            None,
        )
        self.assertIsNotNone(run_type)
        self.assertIsNotNone(build_from_replays)
        passed_task = learning_contracts.GoldenLearningTask(
            id="golden-pass",
            title="通过任务",
            goal_id="goal-1",
            course_id="course-1",
            expected_terminal_status="completed",
            expected_completion_reason="no selectable learning node",
            expected_graph_operation_count=1,
            expected_remaining_selectable_nodes=0,
        )
        failed_task = learning_contracts.GoldenLearningTask(
            id="golden-fail",
            title="失败任务",
            goal_id="goal-1",
            course_id="course-1",
            expected_terminal_status="completed",
            expected_completion_reason="no selectable learning node",
            expected_graph_operation_count=2,
            expected_remaining_selectable_nodes=0,
        )
        replay = learning_contracts.GraphOperationReplay(
            requests=(GraphOperationRequest("request-1", "course-1", "trace-event", "expand", "expand", "user"),),
            proposals=(GraphOperationProposal("proposal-1", "request-1", "expand", "summary", "rationale"),),
            confirmations=(GraphOperationConfirmation("proposal-1", "request-1", "user"),),
            applied_operations=(AppliedGraphOperation("proposal-1", "request-1", "expand", "applied", ("trace-payload-schema",)),),
        )
        run_inputs = (
            run_type(passed_task, self._completed_learning_loop_run_result("run-pass"), replay),
            run_type(failed_task, self._completed_learning_loop_run_result("run-fail"), replay),
        )

        batch_report = build_from_replays("suite-main-loop", run_inputs)

        passed_report = learning_contracts.GoldenLearningTaskReport(
            task_id="golden-pass",
            task_title="通过任务",
            goal_id="goal-1",
            course_id="course-1",
            run_id="run-pass",
            expected_terminal_status="completed",
            actual_terminal_status="completed",
            expected_completion_reason="no selectable learning node",
            actual_completion_reason="no selectable learning node",
            expected_graph_operation_count=1,
            actual_graph_operation_count=1,
            expected_remaining_selectable_nodes=0,
            actual_remaining_selectable_nodes=0,
            trace_matches_contract=True,
            graph_replay_completed=True,
            regression_passed=True,
            report="Golden learning task passed: golden-pass.",
        )
        failed_report = learning_contracts.GoldenLearningTaskReport(
            task_id="golden-fail",
            task_title="失败任务",
            goal_id="goal-1",
            course_id="course-1",
            run_id="run-fail",
            expected_terminal_status="completed",
            actual_terminal_status="completed",
            expected_completion_reason="no selectable learning node",
            actual_completion_reason="no selectable learning node",
            expected_graph_operation_count=2,
            actual_graph_operation_count=1,
            expected_remaining_selectable_nodes=0,
            actual_remaining_selectable_nodes=0,
            trace_matches_contract=True,
            graph_replay_completed=True,
            regression_passed=False,
            report="Golden learning task failed: golden-fail.",
        )
        self.assertEqual(
            batch_report,
            learning_contracts.GoldenLearningTaskBatchReport(
                suite_id="suite-main-loop",
                total_count=2,
                passed_count=1,
                failed_count=1,
                failed_task_ids=("golden-fail",),
                regression_passed=False,
                reports=(passed_report, failed_report),
                report="Golden learning task suite failed: 1/2 passed.",
            ),
        )

    def test_persisted_golden_learning_task_batch_runner_loads_traces_replays_and_saves_reports(self):
        run_reference_type = getattr(learning_contracts, "GoldenLearningTaskRunReference", None)
        run_batch = getattr(learning_contracts, "run_golden_learning_task_batch_from_repository", None)
        self.assertIsNotNone(run_reference_type)
        self.assertIsNotNone(run_batch)
        passed_task = learning_contracts.GoldenLearningTask(
            id="golden-pass",
            title="通过任务",
            goal_id="goal-1",
            course_id="course-1",
            expected_terminal_status="completed",
            expected_completion_reason="no selectable learning node",
            expected_graph_operation_count=1,
            expected_remaining_selectable_nodes=0,
        )
        failed_task = learning_contracts.GoldenLearningTask(
            id="golden-fail",
            title="失败任务",
            goal_id="goal-1",
            course_id="course-1",
            expected_terminal_status="completed",
            expected_completion_reason="no selectable learning node",
            expected_graph_operation_count=2,
            expected_remaining_selectable_nodes=0,
        )

        with TemporaryDirectory() as directory:
            repository = JsonLearningRepository(f"{directory}/learning")
            replay_repository = JsonLearningRepository(f"{directory}/replay")
            trace_store = TraceStore(f"{directory}/traces")
            repository.save_golden_learning_task(passed_task)
            repository.save_golden_learning_task(failed_task)
            trace_store.save(self._completed_learning_loop_run_result_with_replay_payload("run-pass"))
            trace_store.save(self._completed_learning_loop_run_result_with_replay_payload("run-fail"))

            result = run_batch(
                "suite-main-loop",
                (
                    run_reference_type("golden-pass", "run-pass"),
                    run_reference_type("golden-fail", "run-fail"),
                ),
                repository,
                trace_store,
                replay_repository,
            )
            reader = JsonLearningRepository(f"{directory}/learning")
            replay_reader = JsonLearningRepository(f"{directory}/replay")
            loaded_batch_report = reader.load_golden_learning_task_batch_report("suite-main-loop")
            loaded_pass_report = reader.load_golden_learning_task_report("golden-pass", "run-pass")
            loaded_fail_report = reader.load_golden_learning_task_report("golden-fail", "run-fail")
            loaded_replayed_request = replay_reader.load_graph_operation_request("request-run-pass")

        self.assertTrue(result.ok)
        self.assertIsNone(result.error_code)
        batch_report = result.value
        self.assertEqual(batch_report.total_count, 2)
        self.assertEqual(batch_report.passed_count, 1)
        self.assertEqual(batch_report.failed_count, 1)
        self.assertEqual(batch_report.failed_task_ids, ("golden-fail",))
        self.assertFalse(batch_report.regression_passed)
        self.assertEqual(loaded_batch_report, batch_report)
        self.assertEqual(loaded_pass_report, batch_report.reports[0])
        self.assertEqual(loaded_fail_report, batch_report.reports[1])
        self.assertEqual(loaded_replayed_request.id, "request-run-pass")
        self.assertEqual(loaded_replayed_request.course_id, "course-1")

    def test_persisted_golden_learning_task_batch_runner_maps_missing_task_to_error_code(self):
        with TemporaryDirectory() as directory:
            result = learning_contracts.run_golden_learning_task_batch_from_repository(
                "suite-missing-task",
                (learning_contracts.GoldenLearningTaskRunReference("missing-task", "run-1"),),
                JsonLearningRepository(f"{directory}/learning"),
                TraceStore(f"{directory}/traces"),
                JsonLearningRepository(f"{directory}/replay"),
            )

        self.assertEqual(
            result,
            ContractApiResult(
                ok=False,
                value=None,
                error_code="GOLDEN_LEARNING_TASK_NOT_FOUND",
                error_message="golden learning task not found: missing-task",
            ),
        )

    def test_persisted_golden_learning_task_batch_runner_maps_missing_trace_to_error_code(self):
        task = learning_contracts.GoldenLearningTask(
            id="golden-pass",
            title="通过任务",
            goal_id="goal-1",
            course_id="course-1",
            expected_terminal_status="completed",
            expected_completion_reason="no selectable learning node",
            expected_graph_operation_count=1,
            expected_remaining_selectable_nodes=0,
        )

        with TemporaryDirectory() as directory:
            repository = JsonLearningRepository(f"{directory}/learning")
            repository.save_golden_learning_task(task)
            result = learning_contracts.run_golden_learning_task_batch_from_repository(
                "suite-missing-trace",
                (learning_contracts.GoldenLearningTaskRunReference("golden-pass", "missing-run"),),
                repository,
                TraceStore(f"{directory}/traces"),
                JsonLearningRepository(f"{directory}/replay"),
            )

        self.assertEqual(
            result,
            ContractApiResult(
                ok=False,
                value=None,
                error_code="GOLDEN_LEARNING_TASK_TRACE_NOT_FOUND",
                error_message="golden learning task trace not found: missing-run",
            ),
        )

    def test_persisted_golden_learning_task_batch_runner_maps_invalid_trace_schema_to_error_code(self):
        task = learning_contracts.GoldenLearningTask(
            id="golden-pass",
            title="通过任务",
            goal_id="goal-1",
            course_id="course-1",
            expected_terminal_status="completed",
            expected_completion_reason="no selectable learning node",
            expected_graph_operation_count=1,
            expected_remaining_selectable_nodes=0,
        )

        with TemporaryDirectory() as directory:
            repository = JsonLearningRepository(f"{directory}/learning")
            trace_directory = Path(directory) / "traces"
            trace_directory.mkdir()
            repository.save_golden_learning_task(task)
            (trace_directory / "run-bad-schema.json").write_text(
                '{"schema_version": 999, "result": {}}',
                encoding="utf-8",
            )
            result = learning_contracts.run_golden_learning_task_batch_from_repository(
                "suite-bad-trace",
                (learning_contracts.GoldenLearningTaskRunReference("golden-pass", "run-bad-schema"),),
                repository,
                TraceStore(trace_directory),
                JsonLearningRepository(f"{directory}/replay"),
            )

        self.assertEqual(
            result,
            ContractApiResult(
                ok=False,
                value=None,
                error_code="GOLDEN_LEARNING_TASK_TRACE_INVALID",
                error_message="golden learning task trace is invalid: run-bad-schema",
            ),
        )

    def test_persisted_golden_learning_task_batch_runner_maps_replay_write_failure_to_error_code(self):
        task = learning_contracts.GoldenLearningTask(
            id="golden-pass",
            title="通过任务",
            goal_id="goal-1",
            course_id="course-1",
            expected_terminal_status="completed",
            expected_completion_reason="no selectable learning node",
            expected_graph_operation_count=1,
            expected_remaining_selectable_nodes=0,
        )

        class FailingReplayRepository(JsonLearningRepository):
            def save_graph_operation_request(self, request):
                raise OSError("replay storage unavailable")

        with TemporaryDirectory() as directory:
            repository = JsonLearningRepository(f"{directory}/learning")
            trace_store = TraceStore(f"{directory}/traces")
            repository.save_golden_learning_task(task)
            trace_store.save(self._completed_learning_loop_run_result_with_replay_payload("run-replay-fail"))
            result = learning_contracts.run_golden_learning_task_batch_from_repository(
                "suite-replay-fail",
                (learning_contracts.GoldenLearningTaskRunReference("golden-pass", "run-replay-fail"),),
                repository,
                trace_store,
                FailingReplayRepository(f"{directory}/replay"),
            )

        self.assertEqual(
            result,
            ContractApiResult(
                ok=False,
                value=None,
                error_code="GOLDEN_LEARNING_TASK_REPLAY_IO_ERROR",
                error_message="golden learning task replay failed for run-replay-fail: replay storage unavailable",
            ),
        )

    def test_persisted_golden_learning_task_batch_runner_rejects_empty_suite(self):
        with TemporaryDirectory() as directory:
            result = learning_contracts.run_golden_learning_task_batch_from_repository(
                "suite-empty",
                (),
                JsonLearningRepository(f"{directory}/learning"),
                TraceStore(f"{directory}/traces"),
                JsonLearningRepository(f"{directory}/replay"),
            )

        self.assertEqual(
            result,
            ContractApiResult(
                ok=False,
                value=None,
                error_code="EMPTY_GOLDEN_LEARNING_TASK_SUITE",
                error_message="golden learning task suite has no run references: suite-empty",
            ),
        )

    def test_json_repository_round_trips_golden_learning_task_suite_manifest(self):
        manifest_type = getattr(learning_contracts, "GoldenLearningTaskSuiteManifest", None)
        self.assertIsNotNone(manifest_type)
        manifest = manifest_type(
            "suite-main-loop",
            (
                learning_contracts.GoldenLearningTaskRunReference("golden-pass", "run-pass"),
                learning_contracts.GoldenLearningTaskRunReference("golden-fail", "run-fail"),
            ),
        )

        with TemporaryDirectory() as directory:
            repository = JsonLearningRepository(directory)
            repository.save_golden_learning_task_suite_manifest(manifest)
            loaded = JsonLearningRepository(directory).load_golden_learning_task_suite_manifest(
                "suite-main-loop"
            )

        self.assertEqual(loaded, manifest)

    def test_save_golden_learning_task_suite_manifest_api_rejects_empty_manifest(self):
        manifest_type = getattr(learning_contracts, "GoldenLearningTaskSuiteManifest", None)
        save_manifest = getattr(learning_contracts, "save_golden_learning_task_suite_manifest_api", None)
        self.assertIsNotNone(manifest_type)
        self.assertIsNotNone(save_manifest)

        with TemporaryDirectory() as directory:
            result = save_manifest(
                manifest_type("suite-empty", ()),
                JsonLearningRepository(directory),
            )

        self.assertEqual(
            result,
            ContractApiResult(
                ok=False,
                value=None,
                error_code="EMPTY_GOLDEN_LEARNING_TASK_SUITE_MANIFEST",
                error_message="golden learning task suite manifest has no run references: suite-empty",
            ),
        )

    def test_save_golden_learning_task_suite_manifest_api_rejects_duplicate_task_reference(self):
        manifest_type = getattr(learning_contracts, "GoldenLearningTaskSuiteManifest", None)
        save_manifest = getattr(learning_contracts, "save_golden_learning_task_suite_manifest_api", None)
        self.assertIsNotNone(manifest_type)
        self.assertIsNotNone(save_manifest)
        manifest = manifest_type(
            "suite-duplicate-task",
            (
                learning_contracts.GoldenLearningTaskRunReference("golden-pass", "run-1"),
                learning_contracts.GoldenLearningTaskRunReference("golden-pass", "run-2"),
            ),
        )

        with TemporaryDirectory() as directory:
            result = save_manifest(manifest, JsonLearningRepository(directory))

        self.assertEqual(
            result,
            ContractApiResult(
                ok=False,
                value=None,
                error_code="DUPLICATE_GOLDEN_LEARNING_TASK_REFERENCE",
                error_message="golden learning task suite manifest has duplicate task reference: golden-pass",
            ),
        )

    def test_save_golden_learning_task_suite_manifest_api_rejects_duplicate_run_reference(self):
        manifest_type = getattr(learning_contracts, "GoldenLearningTaskSuiteManifest", None)
        save_manifest = getattr(learning_contracts, "save_golden_learning_task_suite_manifest_api", None)
        self.assertIsNotNone(manifest_type)
        self.assertIsNotNone(save_manifest)
        manifest = manifest_type(
            "suite-duplicate-run",
            (
                learning_contracts.GoldenLearningTaskRunReference("golden-1", "run-pass"),
                learning_contracts.GoldenLearningTaskRunReference("golden-2", "run-pass"),
            ),
        )

        with TemporaryDirectory() as directory:
            result = save_manifest(manifest, JsonLearningRepository(directory))

        self.assertEqual(
            result,
            ContractApiResult(
                ok=False,
                value=None,
                error_code="DUPLICATE_GOLDEN_LEARNING_RUN_REFERENCE",
                error_message="golden learning task suite manifest has duplicate run reference: run-pass",
            ),
        )

    def test_golden_learning_task_batch_by_suite_id_maps_missing_manifest_to_error_code(self):
        run_suite = getattr(learning_contracts, "run_golden_learning_task_batch_by_suite_id", None)
        self.assertIsNotNone(run_suite)

        with TemporaryDirectory() as directory:
            result = run_suite(
                "missing-suite",
                JsonLearningRepository(f"{directory}/learning"),
                TraceStore(f"{directory}/traces"),
                JsonLearningRepository(f"{directory}/replay"),
            )

        self.assertEqual(
            result,
            ContractApiResult(
                ok=False,
                value=None,
                error_code="GOLDEN_LEARNING_TASK_SUITE_MANIFEST_NOT_FOUND",
                error_message="golden learning task suite manifest not found: missing-suite",
            ),
        )

    def test_golden_learning_task_batch_runner_runs_from_persisted_suite_manifest(self):
        manifest_type = getattr(learning_contracts, "GoldenLearningTaskSuiteManifest", None)
        save_manifest = getattr(learning_contracts, "save_golden_learning_task_suite_manifest_api", None)
        run_suite = getattr(learning_contracts, "run_golden_learning_task_batch_by_suite_id", None)
        self.assertIsNotNone(manifest_type)
        self.assertIsNotNone(save_manifest)
        self.assertIsNotNone(run_suite)
        passed_task = learning_contracts.GoldenLearningTask(
            id="golden-pass",
            title="通过任务",
            goal_id="goal-1",
            course_id="course-1",
            expected_terminal_status="completed",
            expected_completion_reason="no selectable learning node",
            expected_graph_operation_count=1,
            expected_remaining_selectable_nodes=0,
        )
        failed_task = learning_contracts.GoldenLearningTask(
            id="golden-fail",
            title="失败任务",
            goal_id="goal-1",
            course_id="course-1",
            expected_terminal_status="completed",
            expected_completion_reason="no selectable learning node",
            expected_graph_operation_count=2,
            expected_remaining_selectable_nodes=0,
        )
        manifest = manifest_type(
            "suite-main-loop",
            (
                learning_contracts.GoldenLearningTaskRunReference("golden-pass", "run-pass"),
                learning_contracts.GoldenLearningTaskRunReference("golden-fail", "run-fail"),
            ),
        )

        with TemporaryDirectory() as directory:
            repository = JsonLearningRepository(f"{directory}/learning")
            replay_repository = JsonLearningRepository(f"{directory}/replay")
            trace_store = TraceStore(f"{directory}/traces")
            repository.save_golden_learning_task(passed_task)
            repository.save_golden_learning_task(failed_task)
            trace_store.save(self._completed_learning_loop_run_result_with_replay_payload("run-pass"))
            trace_store.save(self._completed_learning_loop_run_result_with_replay_payload("run-fail"))
            saved = save_manifest(manifest, repository)
            result = run_suite("suite-main-loop", repository, trace_store, replay_repository)
            loaded_batch = repository.load_golden_learning_task_batch_report("suite-main-loop")

        self.assertTrue(saved.ok)
        self.assertTrue(result.ok)
        self.assertEqual(result.value, loaded_batch)
        self.assertEqual(result.value.total_count, 2)
        self.assertEqual(result.value.failed_task_ids, ("golden-fail",))

    def test_create_learning_goal_api_persists_goal_and_emits_trace(self):
        request_type = getattr(learning_contracts, "CreateLearningGoalInput", None)
        create_api = getattr(learning_contracts, "create_learning_goal_api", None)
        self.assertIsNotNone(request_type)
        self.assertIsNotNone(create_api)
        goal = LearningGoal("goal-1", "掌握生产级 Agent Runtime")

        with TemporaryDirectory() as directory:
            repository = JsonLearningRepository(directory)
            result = create_api(
                request_type(goal=goal, run_id="run-1", sequence=1),
                repository,
            )
            loaded_goal = JsonLearningRepository(directory).load_goal("goal-1")

        self.assertTrue(result.ok)
        self.assertIsNone(result.error_code)
        created_goal, event = result.value
        self.assertEqual(created_goal, goal)
        self.assertEqual(loaded_goal, goal)
        self.assertEqual(event.sequence, 1)
        self.assertEqual(event.run_id, "run-1")
        self.assertEqual(event.phase, "goal")
        self.assertEqual(event.status, "created")
        self.assertEqual(event.payload["event_type"], "goal_created")
        self.assertEqual(event.payload["goal_id"], "goal-1")
        self.assertEqual(event.payload["title"], "掌握生产级 Agent Runtime")

    def test_initialize_course_graph_api_persists_graph_and_emits_trace(self):
        edge_type = getattr(learning_contracts, "DependencyEdge", None)
        graph_type = getattr(learning_contracts, "CourseGraph", None)
        request_type = getattr(learning_contracts, "InitializeCourseGraphInput", None)
        initialize_api = getattr(learning_contracts, "initialize_course_graph_api", None)
        self.assertIsNotNone(edge_type)
        self.assertIsNotNone(graph_type)
        self.assertIsNotNone(request_type)
        self.assertIsNotNone(initialize_api)
        goal = LearningGoal("goal-1", "掌握生产级 Agent Runtime")
        course = Course("course-1", "goal-1", "知识图谱学习系统", ("runtime-state", "trace-event"))
        nodes = (
            ConceptNode("runtime-state", "course-1", "Runtime 状态契约"),
            ConceptNode("trace-event", "course-1", "Trace 事件契约"),
        )
        edges = (edge_type("runtime-state", "trace-event", "prerequisite"),)
        expected_graph = graph_type(course=course, nodes=nodes, dependency_edges=edges)

        with TemporaryDirectory() as directory:
            repository = JsonLearningRepository(directory)
            repository.save_goal(goal)
            result = initialize_api(
                request_type(
                    goal=goal,
                    course=course,
                    nodes=nodes,
                    dependency_edges=edges,
                    run_id="run-1",
                    sequence=2,
                ),
                repository,
            )
            loaded_graph = JsonLearningRepository(directory).load_course_graph("course-1")

        self.assertTrue(result.ok)
        self.assertIsNone(result.error_code)
        graph, event = result.value
        self.assertEqual(graph, expected_graph)
        self.assertEqual(loaded_graph, expected_graph)
        self.assertEqual(event.sequence, 2)
        self.assertEqual(event.run_id, "run-1")
        self.assertEqual(event.phase, "course_graph")
        self.assertEqual(event.status, "created")
        self.assertEqual(event.payload["event_type"], "course_graph_created")
        self.assertEqual(event.payload["goal_id"], "goal-1")
        self.assertEqual(event.payload["course_id"], "course-1")
        self.assertEqual(event.payload["node_ids"], ("runtime-state", "trace-event"))
        self.assertEqual(event.payload["dependency_edges"], (("runtime-state", "trace-event", "prerequisite"),))

    def test_initialize_course_graph_api_maps_invalid_graph_to_error_code(self):
        edge_type = getattr(learning_contracts, "DependencyEdge", None)
        request_type = getattr(learning_contracts, "InitializeCourseGraphInput", None)
        initialize_api = getattr(learning_contracts, "initialize_course_graph_api", None)
        self.assertIsNotNone(edge_type)
        self.assertIsNotNone(request_type)
        self.assertIsNotNone(initialize_api)
        request = request_type(
            goal=LearningGoal("goal-1", "掌握生产级 Agent Runtime"),
            course=Course("course-1", "goal-1", "知识图谱学习系统", ("runtime-state",)),
            nodes=(ConceptNode("trace-event", "course-1", "Trace 事件契约"),),
            dependency_edges=(edge_type("runtime-state", "trace-event", "prerequisite"),),
            run_id="run-1",
            sequence=2,
        )

        with TemporaryDirectory() as directory:
            result = initialize_api(request, JsonLearningRepository(directory))

        self.assertEqual(
            result,
            ContractApiResult(
                ok=False,
                value=None,
                error_code="NODE_NOT_IN_COURSE_GRAPH",
                error_message="nodes must match course graph",
            ),
        )

    def test_eval_result_updates_leaf_progress_with_trace(self):
        evidence = Evidence(
            id="evidence-1",
            session_id="session-1",
            node_id="runtime-state",
            kind="answer",
            content_ref="answer://runtime-state/1",
        )
        eval_result = EvalResult(
            id="eval-1",
            evidence_id="evidence-1",
            node_id="runtime-state",
            passed=True,
            score=0.82,
            reason="answer explains runtime state boundaries",
        )

        progress, event = apply_eval_result_to_progress(
            evidence,
            eval_result,
            previous_percent=20,
            run_id="run-1",
            sequence=7,
        )

        self.assertEqual(progress.node_id, "runtime-state")
        self.assertEqual(progress.percent, 82)
        self.assertEqual(progress.mastery_state, "verified")
        self.assertEqual(event.sequence, 7)
        self.assertEqual(event.run_id, "run-1")
        self.assertEqual(event.phase, "progress")
        self.assertEqual(event.status, "updated")
        self.assertEqual(event.payload["event_type"], "progress_updated")
        self.assertEqual(event.payload["evidence_id"], "evidence-1")
        self.assertEqual(event.payload["eval_result_id"], "eval-1")
        self.assertEqual(event.payload["from_percent"], 20)
        self.assertEqual(event.payload["to_percent"], 82)

    def test_eval_result_must_reference_evidence(self):
        evidence = Evidence(
            id="evidence-1",
            session_id="session-1",
            node_id="runtime-state",
            kind="answer",
            content_ref="answer://runtime-state/1",
        )
        eval_result = EvalResult(
            id="eval-1",
            evidence_id="other-evidence",
            node_id="runtime-state",
            passed=True,
            score=0.82,
            reason="answer explains runtime state boundaries",
        )

        with self.assertRaisesRegex(ValueError, "eval result must reference evidence"):
            apply_eval_result_to_progress(
                evidence,
                eval_result,
                previous_percent=20,
                run_id="run-1",
                sequence=7,
            )

    def test_submit_eval_progress_returns_contract_result_from_request_schema(self):
        request_type = getattr(learning_contracts, "SubmitEvalProgressInput", None)
        self.assertIsNotNone(request_type)
        request = request_type(
            evidence=Evidence(
                id="evidence-1",
                session_id="session-1",
                node_id="runtime-state",
                kind="answer",
                content_ref="answer://runtime-state/1",
            ),
            eval_result=EvalResult(
                id="eval-1",
                evidence_id="evidence-1",
                node_id="runtime-state",
                passed=True,
                score=0.82,
                reason="answer explains runtime state boundaries",
            ),
            previous_percent=20,
            run_id="run-1",
            sequence=7,
        )

        result = submit_eval_progress(request)

        self.assertTrue(result.ok)
        self.assertIsNone(result.error_code)
        progress, event = result.value
        self.assertEqual(progress, NodeProgress("runtime-state", 82, "verified"))
        self.assertEqual(event.sequence, 7)
        self.assertEqual(event.run_id, "run-1")
        self.assertEqual(event.payload["event_type"], "progress_updated")

    def test_submit_eval_progress_persists_eval_result_and_progress_when_repository_provided(self):
        request_type = getattr(learning_contracts, "SubmitEvalProgressInput", None)
        self.assertIsNotNone(request_type)
        evidence = Evidence(
            id="evidence-1",
            session_id="session-1",
            node_id="runtime-state",
            kind="answer",
            content_ref="answer://runtime-state/1",
        )
        eval_result = EvalResult(
            id="eval-1",
            evidence_id="evidence-1",
            node_id="runtime-state",
            passed=True,
            score=0.82,
            reason="answer explains runtime state boundaries",
        )
        request = request_type(
            evidence=evidence,
            eval_result=eval_result,
            previous_percent=20,
            run_id="run-1",
            sequence=7,
        )

        with TemporaryDirectory() as directory:
            repository = JsonLearningRepository(directory)
            repository.save_evidence(evidence)
            result = submit_eval_progress(request, repository)
            loaded_eval_result = JsonLearningRepository(directory).load_eval_result("eval-1")
            loaded_progress = JsonLearningRepository(directory).load_progress("runtime-state")

        self.assertTrue(result.ok)
        self.assertIsNone(result.error_code)
        progress, event = result.value
        self.assertEqual(progress, NodeProgress("runtime-state", 82, "verified"))
        self.assertEqual(loaded_eval_result, eval_result)
        self.assertEqual(loaded_progress, progress)
        self.assertEqual(event.sequence, 7)
        self.assertEqual(event.run_id, "run-1")
        self.assertEqual(event.payload["event_type"], "progress_updated")

    def test_submit_eval_progress_maps_evidence_mismatch_to_error_code(self):
        evidence = Evidence(
            id="evidence-1",
            session_id="session-1",
            node_id="runtime-state",
            kind="answer",
            content_ref="answer://runtime-state/1",
        )
        eval_result = EvalResult(
            id="eval-1",
            evidence_id="other-evidence",
            node_id="runtime-state",
            passed=True,
            score=0.82,
            reason="answer explains runtime state boundaries",
        )

        request = learning_contracts.SubmitEvalProgressInput(
            evidence=evidence,
            eval_result=eval_result,
            previous_percent=20,
            run_id="run-1",
            sequence=7,
        )

        result = submit_eval_progress(request)

        self.assertEqual(
            result,
            ContractApiResult(
                ok=False,
                value=None,
                error_code="EVAL_EVIDENCE_MISMATCH",
                error_message="eval result must reference evidence",
            ),
        )

    def test_graph_operation_request_emits_request_trace(self):
        request, event = create_graph_operation_request(
            request_id="request-1",
            course_id="course-1",
            node_id="runtime-state",
            operation_type="expand",
            user_intent="这个点不够细，展开下一级",
            source="menu",
            context_refs=("session://session-1", "node://runtime-parent"),
            run_id="run-1",
            sequence=8,
        )

        self.assertEqual(
            request,
            GraphOperationRequest(
                id="request-1",
                course_id="course-1",
                node_id="runtime-state",
                operation_type="expand",
                user_intent="这个点不够细，展开下一级",
                source="menu",
                target_node_ids=(),
                context_refs=("session://session-1", "node://runtime-parent"),
                status="created",
            ),
        )
        self.assertEqual(event.sequence, 8)
        self.assertEqual(event.run_id, "run-1")
        self.assertEqual(event.phase, "graph_update")
        self.assertEqual(event.status, "requested")
        self.assertEqual(event.payload["event_type"], "graph_operation_requested")
        self.assertEqual(event.payload["request_id"], "request-1")
        self.assertEqual(event.payload["node_id"], "runtime-state")
        self.assertEqual(event.payload["operation_type"], "expand")
        self.assertEqual(event.payload["source"], "menu")
        self.assertEqual(event.payload["user_intent"], "这个点不够细，展开下一级")
        self.assertEqual(event.payload["context_refs"], ("session://session-1", "node://runtime-parent"))

    def test_graph_operation_proposal_emits_proposal_trace(self):
        request = GraphOperationRequest(
            id="request-1",
            course_id="course-1",
            node_id="runtime-state",
            operation_type="expand",
            user_intent="这个点不够细，展开下一级",
            source="menu",
        )

        proposal, event = propose_graph_operation(
            request,
            proposal_id="proposal-1",
            summary="expand runtime state into smaller concepts",
            rationale="learner asked for finer structure",
            proposed_nodes=("runtime-phase", "terminal-status"),
            proposed_edges=(("runtime-phase", "terminal-status"),),
            run_id="run-1",
            sequence=9,
        )

        self.assertEqual(
            proposal,
            GraphOperationProposal(
                id="proposal-1",
                request_id="request-1",
                operation_type="expand",
                summary="expand runtime state into smaller concepts",
                rationale="learner asked for finer structure",
                affected_nodes=("runtime-state",),
                proposed_nodes=("runtime-phase", "terminal-status"),
                proposed_edges=(("runtime-phase", "terminal-status"),),
                requires_confirmation=True,
            ),
        )
        self.assertEqual(event.sequence, 9)
        self.assertEqual(event.run_id, "run-1")
        self.assertEqual(event.phase, "graph_update")
        self.assertEqual(event.status, "proposed")
        self.assertEqual(event.payload["event_type"], "graph_operation_proposed")
        self.assertEqual(event.payload["proposal_id"], "proposal-1")
        self.assertEqual(event.payload["request_id"], "request-1")
        self.assertEqual(event.payload["affected_nodes"], ("runtime-state",))
        self.assertEqual(event.payload["proposed_nodes"], ("runtime-phase", "terminal-status"))
        self.assertEqual(event.payload["rationale"], "learner asked for finer structure")

    def test_graph_operation_proposal_carries_structured_plan_fields(self):
        request = GraphOperationRequest(
            id="request-1",
            course_id="course-1",
            node_id="runtime-state",
            operation_type="split",
            user_intent="把这个节点拆细",
            source="chat_input",
            target_node_ids=("trace-event",),
        )
        proposal_fields = GraphOperationProposal.__dataclass_fields__
        self.assertIn("affected_nodes", proposal_fields)
        self.assertIn("progress_migration", proposal_fields)
        self.assertIn("risks", proposal_fields)

        proposal, event = propose_graph_operation(
            request,
            proposal_id="proposal-1",
            summary="split runtime state into observable sub-concepts",
            rationale="current node mixes state, event, and terminal semantics",
            proposed_nodes=("runtime-phase", "run-event", "terminal-status"),
            proposed_edges=(("runtime-phase", "run-event"), ("run-event", "terminal-status")),
            progress_migration="keep existing parent progress and require child evidence before verification",
            risks=("拆分过细会增加学习路径负担", "已有证据可能无法覆盖新增子节点"),
            run_id="run-1",
            sequence=9,
        )

        self.assertEqual(proposal.affected_nodes, ("runtime-state", "trace-event"))
        self.assertEqual(
            proposal.progress_migration,
            "keep existing parent progress and require child evidence before verification",
        )
        self.assertEqual(proposal.risks, ("拆分过细会增加学习路径负担", "已有证据可能无法覆盖新增子节点"))
        self.assertEqual(event.payload["affected_nodes"], ("runtime-state", "trace-event"))
        self.assertEqual(
            event.payload["progress_migration"],
            "keep existing parent progress and require child evidence before verification",
        )
        self.assertEqual(event.payload["risks"], ("拆分过细会增加学习路径负担", "已有证据可能无法覆盖新增子节点"))

    def test_graph_operation_requires_confirmation(self):
        proposal = GraphOperationProposal(
            id="proposal-1",
            request_id="request-1",
            operation_type="expand",
            summary="expand runtime state into smaller concepts",
            rationale="learner asked for finer structure",
            proposed_nodes=("runtime-phase", "terminal-status"),
            proposed_edges=(("runtime-phase", "terminal-status"),),
            requires_confirmation=True,
        )

        with self.assertRaisesRegex(ValueError, "requires confirmation"):
            apply_graph_operation(
                proposal,
                confirmed_by=None,
                run_id="run-1",
                sequence=9,
            )

    def test_apply_graph_operation_api_returns_contract_result_from_request_schema(self):
        request_type = getattr(learning_contracts, "ApplyGraphOperationInput", None)
        self.assertIsNotNone(request_type)
        proposal = GraphOperationProposal(
            id="proposal-1",
            request_id="request-1",
            operation_type="expand",
            summary="expand runtime state into smaller concepts",
            rationale="learner asked for finer structure",
            proposed_nodes=("runtime-phase",),
            requires_confirmation=True,
        )
        request = request_type(
            proposal=proposal,
            run_id="run-1",
            sequence=10,
            confirmed_by="user",
        )

        result = apply_graph_operation_api(request)

        self.assertTrue(result.ok)
        self.assertIsNone(result.error_code)
        applied, event = result.value
        self.assertEqual(
            applied,
            AppliedGraphOperation(
                proposal_id="proposal-1",
                request_id="request-1",
                operation_type="expand",
                status="applied",
                applied_nodes=("runtime-phase",),
            ),
        )
        self.assertEqual(event.run_id, "run-1")
        self.assertEqual(event.sequence, 10)
        self.assertEqual(event.payload["event_type"], "graph_update_applied")

    def test_apply_graph_operation_api_maps_missing_confirmation_to_error_code(self):
        proposal = GraphOperationProposal(
            id="proposal-1",
            request_id="request-1",
            operation_type="expand",
            summary="expand runtime state into smaller concepts",
            rationale="learner asked for finer structure",
            proposed_nodes=("runtime-phase",),
            requires_confirmation=True,
        )

        request = learning_contracts.ApplyGraphOperationInput(
            proposal=proposal,
            run_id="run-1",
            sequence=10,
            confirmed_by=None,
        )

        result = apply_graph_operation_api(request)

        self.assertEqual(
            result,
            ContractApiResult(
                ok=False,
                value=None,
                error_code="GRAPH_OPERATION_CONFIRMATION_REQUIRED",
                error_message="graph operation requires confirmation",
            ),
        )

    def test_graph_operation_confirmation_emits_confirmation_trace(self):
        proposal = GraphOperationProposal(
            id="proposal-1",
            request_id="request-1",
            operation_type="expand",
            summary="expand runtime state into smaller concepts",
            rationale="learner asked for finer structure",
            proposed_nodes=("runtime-phase", "terminal-status"),
            proposed_edges=(("runtime-phase", "terminal-status"),),
            requires_confirmation=True,
        )

        confirmation, event = confirm_graph_operation(
            proposal,
            confirmed_by="user",
            run_id="run-1",
            sequence=9,
        )

        self.assertEqual(
            confirmation,
            GraphOperationConfirmation(
                proposal_id="proposal-1",
                request_id="request-1",
                confirmed_by="user",
                changes_requested=(),
                status="confirmed",
            ),
        )
        self.assertEqual(event.sequence, 9)
        self.assertEqual(event.run_id, "run-1")
        self.assertEqual(event.phase, "graph_update")
        self.assertEqual(event.status, "confirmed")
        self.assertEqual(event.payload["event_type"], "graph_operation_confirmed")
        self.assertEqual(event.payload["proposal_id"], "proposal-1")
        self.assertEqual(event.payload["request_id"], "request-1")
        self.assertEqual(event.payload["confirmed_by"], "user")
        self.assertEqual(event.payload["changes_requested"], ())

    def test_confirmed_graph_operation_emits_apply_trace(self):
        proposal = GraphOperationProposal(
            id="proposal-1",
            request_id="request-1",
            operation_type="expand",
            summary="expand runtime state into smaller concepts",
            rationale="learner asked for finer structure",
            proposed_nodes=("runtime-phase", "terminal-status"),
            proposed_edges=(("runtime-phase", "terminal-status"),),
            requires_confirmation=True,
        )

        applied, event = apply_graph_operation(
            proposal,
            confirmed_by="user",
            run_id="run-1",
            sequence=10,
        )

        self.assertEqual(
            applied,
            AppliedGraphOperation(
                proposal_id="proposal-1",
                request_id="request-1",
                operation_type="expand",
                status="applied",
                applied_nodes=("runtime-phase", "terminal-status"),
            ),
        )
        self.assertEqual(event.sequence, 10)
        self.assertEqual(event.run_id, "run-1")
        self.assertEqual(event.phase, "graph_update")
        self.assertEqual(event.status, "applied")
        self.assertEqual(event.payload["event_type"], "graph_update_applied")
        self.assertEqual(event.payload["proposal_id"], "proposal-1")
        self.assertEqual(event.payload["request_id"], "request-1")
        self.assertEqual(event.payload["confirmed_by"], "user")
        self.assertEqual(event.payload["created_nodes"], ("runtime-phase", "terminal-status"))

    def test_graph_operation_sequence_keeps_single_run_context(self):
        request, requested = create_graph_operation_request(
            request_id="request-1",
            course_id="course-1",
            node_id="runtime-state",
            operation_type="expand",
            user_intent="这个点不够细，展开下一级",
            source="menu",
            run_id="run-1",
            sequence=8,
        )
        proposal, proposed = propose_graph_operation(
            request,
            proposal_id="proposal-1",
            summary="expand runtime state into smaller concepts",
            rationale="learner asked for finer structure",
            proposed_nodes=("runtime-phase", "terminal-status"),
            proposed_edges=(("runtime-phase", "terminal-status"),),
            run_id="run-1",
            sequence=9,
        )
        confirmation, confirmed = confirm_graph_operation(
            proposal,
            confirmed_by="user",
            run_id="run-1",
            sequence=10,
        )
        applied, apply_event = apply_graph_operation(
            proposal,
            confirmation=confirmation,
            run_id="run-1",
            sequence=11,
        )

        events = (requested, proposed, confirmed, apply_event)
        self.assertEqual([event.sequence for event in events], [8, 9, 10, 11])
        self.assertEqual({event.run_id for event in events}, {"run-1"})
        self.assertEqual(
            [event.payload["event_type"] for event in events],
            [
                "graph_operation_requested",
                "graph_operation_proposed",
                "graph_operation_confirmed",
                "graph_update_applied",
            ],
        )
        self.assertEqual(proposal.request_id, request.id)
        self.assertEqual(confirmation.request_id, request.id)
        self.assertEqual(confirmation.proposal_id, proposal.id)
        self.assertEqual(applied.request_id, request.id)
        self.assertEqual(applied.proposal_id, proposal.id)
        self.assertEqual(apply_event.payload["confirmed_by"], "user")

    def test_graph_operation_apply_requires_matching_confirmation(self):
        proposal = GraphOperationProposal(
            id="proposal-1",
            request_id="request-1",
            operation_type="expand",
            summary="expand runtime state into smaller concepts",
            rationale="learner asked for finer structure",
            proposed_nodes=("runtime-phase",),
            requires_confirmation=True,
        )
        confirmation = GraphOperationConfirmation(
            proposal_id="other-proposal",
            request_id="request-1",
            confirmed_by="user",
        )

        with self.assertRaisesRegex(ValueError, "confirmation must match proposal"):
            apply_graph_operation(
                proposal,
                confirmation=confirmation,
                run_id="run-1",
                sequence=10,
            )

    def test_apply_graph_operation_api_maps_confirmation_mismatch_to_error_code(self):
        proposal = GraphOperationProposal(
            id="proposal-1",
            request_id="request-1",
            operation_type="expand",
            summary="expand runtime state into smaller concepts",
            rationale="learner asked for finer structure",
            proposed_nodes=("runtime-phase",),
            requires_confirmation=True,
        )
        confirmation = GraphOperationConfirmation(
            proposal_id="other-proposal",
            request_id="request-1",
            confirmed_by="user",
        )

        request = learning_contracts.ApplyGraphOperationInput(
            proposal=proposal,
            run_id="run-1",
            sequence=10,
            confirmation=confirmation,
        )

        result = apply_graph_operation_api(request)

        self.assertEqual(
            result,
            ContractApiResult(
                ok=False,
                value=None,
                error_code="GRAPH_OPERATION_CONFIRMATION_MISMATCH",
                error_message="confirmation must match proposal",
            ),
        )

    def test_trace_store_round_trips_graph_operation_events(self):
        _, requested = create_graph_operation_request(
            request_id="request-1",
            course_id="course-1",
            node_id="runtime-state",
            operation_type="expand",
            user_intent="这个点不够细，展开下一级",
            source="menu",
            run_id="run-1",
            sequence=1,
        )
        proposal = GraphOperationProposal(
            id="proposal-1",
            request_id="request-1",
            operation_type="expand",
            summary="expand runtime state into smaller concepts",
            rationale="learner asked for finer structure",
            proposed_nodes=("runtime-phase", "terminal-status"),
            proposed_edges=(("runtime-phase", "terminal-status"),),
            requires_confirmation=True,
        )
        _, confirmed = confirm_graph_operation(
            proposal,
            confirmed_by="user",
            run_id="run-1",
            sequence=2,
        )
        _, applied = apply_graph_operation(
            proposal,
            confirmed_by="user",
            run_id="run-1",
            sequence=3,
        )
        result = RunResult(
            run_id="run-1",
            task="expand runtime-state",
            outcome="applied",
            events=(requested, confirmed, applied),
        )

        with TemporaryDirectory() as directory:
            store = TraceStore(directory)
            store.save(result)

            loaded = store.load("run-1")

        self.assertEqual(loaded, result)

    def test_trace_replay_persists_graph_operation_lifecycle(self):
        request, requested = create_graph_operation_request(
            request_id="request-1",
            course_id="course-1",
            node_id="runtime-state",
            operation_type="expand",
            user_intent="这个点不够细，展开下一级",
            source="menu",
            run_id="run-1",
            sequence=1,
        )
        proposal, proposed = propose_graph_operation(
            request,
            proposal_id="proposal-1",
            summary="expand runtime state into smaller concepts",
            rationale="learner asked for finer structure",
            proposed_nodes=("runtime-phase", "terminal-status"),
            proposed_edges=(("runtime-phase", "terminal-status"),),
            progress_migration="keep parent progress until child evidence passes",
            risks=("拆分过细会增加学习路径负担",),
            run_id="run-1",
            sequence=2,
        )
        confirmation, confirmed = confirm_graph_operation(
            proposal,
            confirmed_by="user",
            run_id="run-1",
            sequence=3,
        )
        applied, apply_event = apply_graph_operation(
            proposal,
            confirmation=confirmation,
            run_id="run-1",
            sequence=4,
        )
        result = RunResult(
            run_id="run-1",
            task="expand runtime-state",
            outcome="applied",
            events=(requested, proposed, confirmed, apply_event),
        )

        with TemporaryDirectory() as directory:
            trace_store = TraceStore(f"{directory}/traces")
            trace_store.save(result)
            repository = JsonLearningRepository(f"{directory}/learning")

            replay_function = getattr(learning_contracts, "replay_graph_operations_from_trace", None)
            self.assertIsNotNone(replay_function)
            replay = replay_function(trace_store.load("run-1"), repository)
            reloaded = JsonLearningRepository(f"{directory}/learning")
            loaded_proposal = reloaded.load_graph_operation_proposal("proposal-1")
            loaded_confirmation = reloaded.load_graph_operation_confirmation("proposal-1")
            loaded_applied = reloaded.load_applied_graph_operation("proposal-1")

        self.assertEqual(replay.proposals, (proposal,))
        self.assertEqual(replay.confirmations, (confirmation,))
        self.assertEqual(replay.applied_operations, (applied,))
        self.assertEqual(loaded_proposal, proposal)
        self.assertEqual(loaded_confirmation, confirmation)
        self.assertEqual(loaded_applied, applied)

    def test_repository_backed_graph_operation_api_persists_lifecycle_and_trace_order(self):
        create_input_type = getattr(learning_contracts, "CreateGraphOperationRequestInput", None)
        propose_input_type = getattr(learning_contracts, "ProposeGraphOperationInput", None)
        confirm_input_type = getattr(learning_contracts, "ConfirmGraphOperationInput", None)
        create_api = getattr(learning_contracts, "create_graph_operation_request_api", None)
        propose_api = getattr(learning_contracts, "propose_graph_operation_api", None)
        confirm_api = getattr(learning_contracts, "confirm_graph_operation_api", None)
        self.assertIsNotNone(create_input_type)
        self.assertIsNotNone(propose_input_type)
        self.assertIsNotNone(confirm_input_type)
        self.assertIsNotNone(create_api)
        self.assertIsNotNone(propose_api)
        self.assertIsNotNone(confirm_api)

        with TemporaryDirectory() as directory:
            repository = JsonLearningRepository(f"{directory}/learning")
            request_result = create_api(
                create_input_type(
                    request_id="request-1",
                    course_id="course-1",
                    node_id="runtime-state",
                    operation_type="expand",
                    user_intent="这个点不够细，展开下一级",
                    source="menu",
                    context_refs=("session://session-1",),
                    run_id="run-graph",
                    sequence=7,
                ),
                repository,
            )
            graph_request, request_event = request_result.value
            proposal_result = propose_api(
                propose_input_type(
                    request=graph_request,
                    proposal_id="proposal-1",
                    summary="expand runtime state into smaller concepts",
                    rationale="learner asked for finer structure",
                    proposed_nodes=("runtime-phase", "terminal-status"),
                    proposed_edges=(("runtime-phase", "terminal-status"),),
                    progress_migration="keep parent progress until child evidence passes",
                    risks=("拆分过细会增加学习路径负担",),
                    run_id="run-graph",
                    sequence=8,
                ),
                repository,
            )
            proposal, proposal_event = proposal_result.value
            confirmation_result = confirm_api(
                confirm_input_type(
                    proposal=proposal,
                    confirmed_by="user",
                    run_id="run-graph",
                    sequence=9,
                ),
                repository,
            )
            confirmation, confirmation_event = confirmation_result.value
            apply_result = apply_graph_operation_api(
                learning_contracts.ApplyGraphOperationInput(
                    proposal=proposal,
                    confirmation=confirmation,
                    run_id="run-graph",
                    sequence=10,
                ),
                repository,
            )
            applied, apply_event = apply_result.value
            trace_store = TraceStore(f"{directory}/traces")
            trace_store.save(
                RunResult(
                    run_id="run-graph",
                    task="repository-backed graph operation lifecycle",
                    outcome="applied",
                    events=(request_event, proposal_event, confirmation_event, apply_event),
                )
            )

            reloaded = JsonLearningRepository(f"{directory}/learning")
            loaded_request = reloaded.load_graph_operation_request("request-1")
            loaded_proposal = reloaded.load_graph_operation_proposal("proposal-1")
            loaded_confirmation = reloaded.load_graph_operation_confirmation("proposal-1")
            loaded_applied = reloaded.load_applied_graph_operation("proposal-1")
            loaded_trace = trace_store.load("run-graph")

        for result in (request_result, proposal_result, confirmation_result, apply_result):
            self.assertTrue(result.ok)
            self.assertIsNone(result.error_code)
        self.assertEqual(loaded_request, graph_request)
        self.assertEqual(loaded_proposal, proposal)
        self.assertEqual(loaded_confirmation, confirmation)
        self.assertEqual(loaded_applied, applied)
        self.assertEqual([event.sequence for event in loaded_trace.events], [7, 8, 9, 10])
        self.assertEqual({event.run_id for event in loaded_trace.events}, {"run-graph"})
        self.assertEqual(
            [event.payload["event_type"] for event in loaded_trace.events],
            [
                "graph_operation_requested",
                "graph_operation_proposed",
                "graph_operation_confirmed",
                "graph_update_applied",
            ],
        )

    def test_repository_backed_apply_graph_operation_updates_course_graph_and_initializes_progress(self):
        course = Course(
            id="course-1",
            goal_id="goal-1",
            title="知识图谱学习系统",
            node_ids=("runtime-state", "trace-event"),
        )
        graph = learning_contracts.CourseGraph(
            course=course,
            nodes=(
                ConceptNode("runtime-state", "course-1", "Runtime 状态契约"),
                ConceptNode("trace-event", "course-1", "Trace 事件契约"),
            ),
            dependency_edges=(
                learning_contracts.DependencyEdge("runtime-state", "trace-event", "prerequisite"),
            ),
        )
        request = GraphOperationRequest(
            id="request-1",
            course_id="course-1",
            node_id="trace-event",
            operation_type="expand",
            user_intent="这个点不够细，展开下一级",
            source="menu",
        )
        proposal = GraphOperationProposal(
            id="proposal-1",
            request_id="request-1",
            operation_type="expand",
            summary="expand trace event into replay-focused subnodes",
            rationale="learner needs finer trace replay boundaries",
            affected_nodes=("trace-event",),
            proposed_nodes=("trace-payload-schema", "trace-replay-boundary"),
            proposed_edges=(
                ("trace-event", "trace-payload-schema"),
                ("trace-payload-schema", "trace-replay-boundary"),
            ),
            requires_confirmation=True,
        )
        confirmation = GraphOperationConfirmation(
            proposal_id="proposal-1",
            request_id="request-1",
            confirmed_by="user",
        )

        with TemporaryDirectory() as directory:
            repository = JsonLearningRepository(directory)
            repository.save_course_graph(graph)
            repository.save_graph_operation_request(request)
            result = apply_graph_operation_api(
                learning_contracts.ApplyGraphOperationInput(
                    proposal=proposal,
                    confirmation=confirmation,
                    run_id="run-graph",
                    sequence=10,
                ),
                repository,
            )
            loaded_graph = JsonLearningRepository(directory).load_course_graph("course-1")
            loaded_progress = (
                JsonLearningRepository(directory).load_progress("trace-payload-schema"),
                JsonLearningRepository(directory).load_progress("trace-replay-boundary"),
            )

        self.assertTrue(result.ok)
        self.assertIsNone(result.error_code)
        applied, event = result.value
        self.assertEqual(applied.applied_nodes, ("trace-payload-schema", "trace-replay-boundary"))
        self.assertEqual(
            loaded_graph.course.node_ids,
            ("runtime-state", "trace-event", "trace-payload-schema", "trace-replay-boundary"),
        )
        self.assertEqual(
            loaded_graph.nodes,
            (
                ConceptNode("runtime-state", "course-1", "Runtime 状态契约"),
                ConceptNode("trace-event", "course-1", "Trace 事件契约"),
                ConceptNode("trace-payload-schema", "course-1", "trace-payload-schema"),
                ConceptNode("trace-replay-boundary", "course-1", "trace-replay-boundary"),
            ),
        )
        self.assertEqual(
            loaded_graph.dependency_edges,
            (
                learning_contracts.DependencyEdge("runtime-state", "trace-event", "prerequisite"),
                learning_contracts.DependencyEdge("trace-event", "trace-payload-schema", "prerequisite"),
                learning_contracts.DependencyEdge("trace-payload-schema", "trace-replay-boundary", "prerequisite"),
            ),
        )
        self.assertEqual(
            loaded_progress,
            (
                NodeProgress("trace-payload-schema", 0, "unknown"),
                NodeProgress("trace-replay-boundary", 0, "unknown"),
            ),
        )
        self.assertEqual(event.payload["course_id"], "course-1")
        self.assertEqual(
            event.payload["initialized_progress"],
            (
                ("trace-payload-schema", 0, "unknown"),
                ("trace-replay-boundary", 0, "unknown"),
            ),
        )

    def test_learning_planner_selects_first_unknown_node_with_verified_prerequisites(self):
        next_node_type = getattr(learning_contracts, "NextLearningNode", None)
        select_function = getattr(learning_contracts, "select_next_learning_node", None)
        self.assertIsNotNone(next_node_type)
        self.assertIsNotNone(select_function)
        graph = learning_contracts.CourseGraph(
            course=Course(
                id="course-1",
                goal_id="goal-1",
                title="知识图谱学习系统",
                node_ids=("runtime-state", "trace-event", "trace-payload-schema", "trace-replay-boundary"),
            ),
            nodes=(
                ConceptNode("runtime-state", "course-1", "Runtime 状态契约"),
                ConceptNode("trace-event", "course-1", "Trace 事件契约"),
                ConceptNode("trace-payload-schema", "course-1", "trace-payload-schema"),
                ConceptNode("trace-replay-boundary", "course-1", "trace-replay-boundary"),
            ),
            dependency_edges=(
                learning_contracts.DependencyEdge("runtime-state", "trace-event", "prerequisite"),
                learning_contracts.DependencyEdge("trace-event", "trace-payload-schema", "prerequisite"),
                learning_contracts.DependencyEdge("trace-payload-schema", "trace-replay-boundary", "prerequisite"),
            ),
        )
        progress = (
            NodeProgress("runtime-state", 80, "learning"),
            NodeProgress("trace-event", 80, "verified"),
            NodeProgress("trace-payload-schema", 0, "unknown"),
            NodeProgress("trace-replay-boundary", 0, "unknown"),
        )

        next_node, event = select_function(
            graph,
            progress,
            run_id="run-plan",
            sequence=11,
        )

        self.assertEqual(
            next_node,
            next_node_type(
                course_id="course-1",
                node_id="trace-payload-schema",
                prerequisite_node_ids=("trace-event",),
                reason="first unknown node with prerequisites satisfied",
            ),
        )
        self.assertEqual(event.sequence, 11)
        self.assertEqual(event.run_id, "run-plan")
        self.assertEqual(event.phase, "planning")
        self.assertEqual(event.status, "selected")
        self.assertEqual(event.payload["event_type"], "node_selected")
        self.assertEqual(event.payload["course_id"], "course-1")
        self.assertEqual(event.payload["node_id"], "trace-payload-schema")
        self.assertEqual(event.payload["alternatives"], ())
        self.assertEqual(event.payload["prerequisite_node_ids"], ("trace-event",))
        self.assertEqual(
            event.payload["selection_reason"],
            "first unknown node with prerequisites satisfied",
        )

    def test_learning_planner_api_loads_expanded_graph_and_progress_from_repository(self):
        input_type = getattr(learning_contracts, "SelectNextLearningNodeInput", None)
        next_node_type = getattr(learning_contracts, "NextLearningNode", None)
        select_api = getattr(learning_contracts, "select_next_learning_node_api", None)
        self.assertIsNotNone(input_type)
        self.assertIsNotNone(next_node_type)
        self.assertIsNotNone(select_api)
        graph = learning_contracts.CourseGraph(
            course=Course(
                id="course-1",
                goal_id="goal-1",
                title="知识图谱学习系统",
                node_ids=("runtime-state", "trace-event", "trace-payload-schema", "trace-replay-boundary"),
            ),
            nodes=(
                ConceptNode("runtime-state", "course-1", "Runtime 状态契约"),
                ConceptNode("trace-event", "course-1", "Trace 事件契约"),
                ConceptNode("trace-payload-schema", "course-1", "trace-payload-schema"),
                ConceptNode("trace-replay-boundary", "course-1", "trace-replay-boundary"),
            ),
            dependency_edges=(
                learning_contracts.DependencyEdge("runtime-state", "trace-event", "prerequisite"),
                learning_contracts.DependencyEdge("trace-event", "trace-payload-schema", "prerequisite"),
                learning_contracts.DependencyEdge("trace-payload-schema", "trace-replay-boundary", "prerequisite"),
            ),
        )

        with TemporaryDirectory() as directory:
            repository = JsonLearningRepository(directory)
            repository.save_course_graph(graph)
            repository.save_progress(NodeProgress("runtime-state", 80, "learning"))
            repository.save_progress(NodeProgress("trace-event", 80, "verified"))
            repository.save_progress(NodeProgress("trace-payload-schema", 0, "unknown"))
            repository.save_progress(NodeProgress("trace-replay-boundary", 0, "unknown"))
            result = select_api(
                input_type(
                    course_id="course-1",
                    run_id="run-plan",
                    sequence=11,
                ),
                repository,
            )

        self.assertTrue(result.ok)
        self.assertIsNone(result.error_code)
        next_node, event = result.value
        self.assertEqual(
            next_node,
            next_node_type(
                course_id="course-1",
                node_id="trace-payload-schema",
                prerequisite_node_ids=("trace-event",),
                reason="first unknown node with prerequisites satisfied",
            ),
        )
        self.assertEqual(event.payload["event_type"], "node_selected")
        self.assertEqual(event.payload["node_id"], "trace-payload-schema")

    def test_json_learning_repository_missing_record_raises_domain_error(self):
        error_type = getattr(learning_contracts, "LearningRecordNotFound", None)
        self.assertIsNotNone(error_type)

        with TemporaryDirectory() as directory:
            repository = JsonLearningRepository(directory)

            with self.assertRaises(error_type) as context:
                repository.load_progress("missing-node")

        error = context.exception
        self.assertEqual(error.error_code, "LEARNING_RECORD_NOT_FOUND")
        self.assertEqual(error.collection, "progress")
        self.assertEqual(error.item_id, "missing-node")
        self.assertEqual(str(error), "progress/missing-node not found")

    def test_repository_operation_api_maps_missing_record_to_error_code(self):
        repository_operation_api = getattr(learning_contracts, "repository_operation_api", None)
        self.assertIsNotNone(repository_operation_api)

        with TemporaryDirectory() as directory:
            repository = JsonLearningRepository(directory)
            result = repository_operation_api(lambda: repository.load_progress("missing-node"))

        self.assertEqual(
            result,
            ContractApiResult(
                ok=False,
                value=None,
                error_code="LEARNING_RECORD_NOT_FOUND",
                error_message="progress/missing-node not found",
            ),
        )

    def test_repository_operation_api_maps_file_errors_to_error_code(self):
        repository_operation_api = getattr(learning_contracts, "repository_operation_api", None)
        self.assertIsNotNone(repository_operation_api)

        result = repository_operation_api(lambda: (_ for _ in ()).throw(OSError("disk full")))

        self.assertEqual(
            result,
            ContractApiResult(
                ok=False,
                value=None,
                error_code="LEARNING_REPOSITORY_IO_ERROR",
                error_message="disk full",
            ),
        )

    def test_repository_operation_api_maps_corrupt_json_to_error_code(self):
        repository_operation_api = getattr(learning_contracts, "repository_operation_api", None)
        self.assertIsNotNone(repository_operation_api)

        with TemporaryDirectory() as directory:
            progress_dir = Path(directory) / "progress"
            progress_dir.mkdir()
            (progress_dir / "runtime-state.json").write_text("{", encoding="utf-8")

            try:
                result = repository_operation_api(
                    lambda: JsonLearningRepository(directory).load_progress("runtime-state")
                )
            except Exception as error:
                self.fail(f"repository_operation_api raised {error!r}")

        self.assertEqual(
            result,
            ContractApiResult(
                ok=False,
                value=None,
                error_code="LEARNING_REPOSITORY_DATA_CORRUPTED",
                error_message="progress/runtime-state has corrupted repository data",
            ),
        )

    def test_repository_operation_api_maps_non_object_json_to_data_corrupted_error_code(self):
        repository_operation_api = getattr(learning_contracts, "repository_operation_api", None)
        self.assertIsNotNone(repository_operation_api)

        with TemporaryDirectory() as directory:
            progress_dir = Path(directory) / "progress"
            progress_dir.mkdir()
            (progress_dir / "runtime-state.json").write_text("[]", encoding="utf-8")

            try:
                result = repository_operation_api(
                    lambda: JsonLearningRepository(directory).load_progress("runtime-state")
                )
            except Exception as error:
                self.fail(f"repository_operation_api raised {error!r}")

        self.assertEqual(
            result,
            ContractApiResult(
                ok=False,
                value=None,
                error_code="LEARNING_REPOSITORY_DATA_CORRUPTED",
                error_message="progress/runtime-state has corrupted repository data",
            ),
        )

    def test_repository_operation_api_maps_missing_json_field_to_error_code(self):
        repository_operation_api = getattr(learning_contracts, "repository_operation_api", None)
        self.assertIsNotNone(repository_operation_api)

        with TemporaryDirectory() as directory:
            progress_dir = Path(directory) / "progress"
            progress_dir.mkdir()
            (progress_dir / "runtime-state.json").write_text(
                '{"node_id": "runtime-state", "percent": 82}',
                encoding="utf-8",
            )

            try:
                result = repository_operation_api(
                    lambda: JsonLearningRepository(directory).load_progress("runtime-state")
                )
            except Exception as error:
                self.fail(f"repository_operation_api raised {error!r}")

        self.assertEqual(
            result,
            ContractApiResult(
                ok=False,
                value=None,
                error_code="LEARNING_REPOSITORY_JSON_FIELD_MISSING",
                error_message="progress/runtime-state missing required JSON field: mastery_state",
            ),
        )

    def test_json_learning_repository_round_trips_course_node_and_progress(self):
        repository_type = getattr(learning_contracts, "JsonLearningRepository", None)
        self.assertIsNotNone(repository_type)
        course = Course(
            id="course-1",
            goal_id="goal-1",
            title="知识图谱学习系统",
            node_ids=("runtime-state", "trace-event"),
        )
        node = ConceptNode(
            id="runtime-state",
            course_id="course-1",
            title="Runtime 状态契约",
        )
        progress = NodeProgress("runtime-state", 82, "verified")

        with TemporaryDirectory() as directory:
            repository = repository_type(directory)
            repository.save_course(course)
            repository.save_node(node)
            repository.save_progress(progress)

            reloaded = repository_type(directory)
            self.assertEqual(reloaded.load_course("course-1"), course)
            self.assertEqual(reloaded.load_node("runtime-state"), node)
            self.assertEqual(reloaded.load_progress("runtime-state"), progress)

    def test_parent_progress_uses_child_average(self):
        children = (
            NodeProgress("runtime-phase", 100, "verified"),
            NodeProgress("terminal-status", 50, "practiced"),
            NodeProgress("checkpoint", 0, "unknown"),
        )

        progress, event = recompute_parent_progress(
            "runtime-state",
            children,
            previous_percent=20,
            run_id="run-1",
            sequence=11,
        )

        self.assertEqual(progress, NodeProgress("runtime-state", 50, "learning"))
        self.assertEqual(event.sequence, 11)
        self.assertEqual(event.phase, "progress")
        self.assertEqual(event.status, "recomputed")
        self.assertEqual(event.payload["event_type"], "node_progress_recomputed")
        self.assertEqual(event.payload["node_id"], "runtime-state")
        self.assertEqual(event.payload["child_node_ids"], ("runtime-phase", "terminal-status", "checkpoint"))
        self.assertEqual(event.payload["from_percent"], 20)
        self.assertEqual(event.payload["to_percent"], 50)

    def test_recompute_parent_progress_api_persists_parent_progress_when_repository_provided(self):
        request_type = getattr(learning_contracts, "RecomputeParentProgressInput", None)
        recompute_api = getattr(learning_contracts, "recompute_parent_progress_api", None)
        self.assertIsNotNone(request_type)
        self.assertIsNotNone(recompute_api)
        children = (
            NodeProgress("runtime-phase", 100, "verified"),
            NodeProgress("terminal-status", 50, "practiced"),
            NodeProgress("checkpoint", 0, "unknown"),
        )
        request = request_type(
            node_id="runtime-state",
            children=children,
            previous_percent=20,
            run_id="run-1",
            sequence=11,
        )

        with TemporaryDirectory() as directory:
            repository = JsonLearningRepository(directory)
            for child in children:
                repository.save_progress(child)
            result = recompute_api(request, repository)
            loaded_progress = JsonLearningRepository(directory).load_progress("runtime-state")

        self.assertTrue(result.ok)
        self.assertIsNone(result.error_code)
        progress, event = result.value
        self.assertEqual(progress, NodeProgress("runtime-state", 50, "learning"))
        self.assertEqual(loaded_progress, progress)
        self.assertEqual(event.sequence, 11)
        self.assertEqual(event.run_id, "run-1")
        self.assertEqual(event.payload["event_type"], "node_progress_recomputed")
        self.assertEqual(event.payload["child_node_ids"], ("runtime-phase", "terminal-status", "checkpoint"))

    def test_recompute_parent_progress_api_maps_empty_children_to_error_code(self):
        request_type = getattr(learning_contracts, "RecomputeParentProgressInput", None)
        recompute_api = getattr(learning_contracts, "recompute_parent_progress_api", None)
        self.assertIsNotNone(request_type)
        self.assertIsNotNone(recompute_api)
        request = request_type(
            node_id="runtime-state",
            children=(),
            previous_percent=20,
            run_id="run-1",
            sequence=11,
        )

        result = recompute_api(request)

        self.assertEqual(
            result,
            ContractApiResult(
                ok=False,
                value=None,
                error_code="EMPTY_CHILD_PROGRESS",
                error_message="parent progress requires child progress",
            ),
        )

    def test_start_node_learning_emits_trace(self):
        goal = LearningGoal("goal-1", "掌握生产级 Agent Runtime")
        course = Course(
            id="course-1",
            goal_id="goal-1",
            title="知识图谱学习系统",
            node_ids=("runtime-state",),
        )
        node = ConceptNode(
            id="runtime-state",
            course_id="course-1",
            title="Runtime 状态契约",
        )

        session, event = start_node_learning(
            goal,
            course,
            node,
            session_id="session-1",
            run_id="run-1",
            sequence=3,
        )

        self.assertEqual(
            session,
            LearningSession(
                id="session-1",
                goal_id="goal-1",
                course_id="course-1",
                node_id="runtime-state",
                status="learning",
            ),
        )
        self.assertEqual(event.sequence, 3)
        self.assertEqual(event.phase, "node_learning")
        self.assertEqual(event.status, "started")
        self.assertEqual(event.payload["event_type"], "node_learning_started")
        self.assertEqual(event.payload["goal_id"], "goal-1")
        self.assertEqual(event.payload["course_id"], "course-1")
        self.assertEqual(event.payload["node_id"], "runtime-state")

    def test_start_node_learning_requires_course_node(self):
        goal = LearningGoal("goal-1", "掌握生产级 Agent Runtime")
        course = Course(
            id="course-1",
            goal_id="goal-1",
            title="知识图谱学习系统",
            node_ids=("runtime-state",),
        )
        node = ConceptNode(
            id="trace-event",
            course_id="course-1",
            title="TraceEvent",
        )

        with self.assertRaisesRegex(ValueError, "node must belong to course graph"):
            start_node_learning(
                goal,
                course,
                node,
                session_id="session-1",
                run_id="run-1",
                sequence=3,
            )

    def test_start_node_learning_requires_goal_course_match(self):
        goal = LearningGoal("goal-1", "掌握生产级 Agent Runtime")
        course = Course(
            id="course-1",
            goal_id="other-goal",
            title="知识图谱学习系统",
            node_ids=("runtime-state",),
        )
        node = ConceptNode(
            id="runtime-state",
            course_id="course-1",
            title="Runtime 状态契约",
        )

        with self.assertRaisesRegex(ValueError, "course must belong to learning goal"):
            start_node_learning(
                goal,
                course,
                node,
                session_id="session-1",
                run_id="run-1",
                sequence=3,
            )

    def test_start_node_learning_api_returns_contract_result(self):
        request_type = getattr(learning_contracts, "StartNodeLearningInput", None)
        self.assertIsNotNone(request_type)
        start_api = getattr(learning_contracts, "start_node_learning_api", None)
        self.assertIsNotNone(start_api)
        request = request_type(
            goal=LearningGoal("goal-1", "掌握生产级 Agent Runtime"),
            course=Course(
                id="course-1",
                goal_id="goal-1",
                title="知识图谱学习系统",
                node_ids=("runtime-state",),
            ),
            node=ConceptNode(
                id="runtime-state",
                course_id="course-1",
                title="Runtime 状态契约",
            ),
            session_id="session-1",
            run_id="run-1",
            sequence=3,
        )

        result = start_api(request)

        self.assertTrue(result.ok)
        self.assertIsNone(result.error_code)
        self.assertIsNone(result.error_message)
        session, event = result.value
        self.assertEqual(
            session,
            LearningSession(
                id="session-1",
                goal_id="goal-1",
                course_id="course-1",
                node_id="runtime-state",
                status="learning",
            ),
        )
        self.assertEqual(event.sequence, 3)
        self.assertEqual(event.run_id, "run-1")
        self.assertEqual(event.payload["event_type"], "node_learning_started")

    def test_start_node_learning_api_persists_session_when_repository_provided(self):
        request = learning_contracts.StartNodeLearningInput(
            goal=LearningGoal("goal-1", "掌握生产级 Agent Runtime"),
            course=Course(
                id="course-1",
                goal_id="goal-1",
                title="知识图谱学习系统",
                node_ids=("runtime-state",),
            ),
            node=ConceptNode(
                id="runtime-state",
                course_id="course-1",
                title="Runtime 状态契约",
            ),
            session_id="session-1",
            run_id="run-1",
            sequence=3,
        )

        with TemporaryDirectory() as directory:
            repository = JsonLearningRepository(directory)
            result = learning_contracts.start_node_learning_api(request, repository)
            loaded_session = JsonLearningRepository(directory).load_session("session-1")

        self.assertTrue(result.ok)
        session, event = result.value
        self.assertEqual(loaded_session, session)
        self.assertEqual(
            loaded_session,
            LearningSession(
                id="session-1",
                goal_id="goal-1",
                course_id="course-1",
                node_id="runtime-state",
                status="learning",
            ),
        )
        self.assertEqual(event.payload["event_type"], "node_learning_started")

    def test_submit_evidence_api_persists_evidence_and_emits_trace(self):
        request_type = getattr(learning_contracts, "SubmitEvidenceInput", None)
        submit_api = getattr(learning_contracts, "submit_evidence_api", None)
        self.assertIsNotNone(request_type)
        self.assertIsNotNone(submit_api)
        session = LearningSession(
            id="session-1",
            goal_id="goal-1",
            course_id="course-1",
            node_id="runtime-state",
            status="learning",
        )
        evidence = Evidence(
            id="evidence-1",
            session_id="session-1",
            node_id="runtime-state",
            kind="answer",
            content_ref="answer://runtime-state/1",
        )

        with TemporaryDirectory() as directory:
            repository = JsonLearningRepository(directory)
            repository.save_session(session)
            result = submit_api(
                request_type(
                    session=session,
                    evidence=evidence,
                    run_id="run-1",
                    sequence=4,
                ),
                repository,
            )
            loaded_evidence = JsonLearningRepository(directory).load_evidence("evidence-1")

        self.assertTrue(result.ok)
        self.assertIsNone(result.error_code)
        submitted_evidence, event = result.value
        self.assertEqual(submitted_evidence, evidence)
        self.assertEqual(loaded_evidence, evidence)
        self.assertEqual(event.sequence, 4)
        self.assertEqual(event.run_id, "run-1")
        self.assertEqual(event.phase, "evidence")
        self.assertEqual(event.status, "submitted")
        self.assertEqual(event.payload["event_type"], "evidence_submitted")
        self.assertEqual(event.payload["session_id"], "session-1")
        self.assertEqual(event.payload["evidence_id"], "evidence-1")
        self.assertEqual(event.payload["kind"], "answer")
        self.assertEqual(event.payload["content_ref"], "answer://runtime-state/1")

    def test_submit_evidence_api_maps_session_mismatch_to_error_code(self):
        request_type = getattr(learning_contracts, "SubmitEvidenceInput", None)
        submit_api = getattr(learning_contracts, "submit_evidence_api", None)
        self.assertIsNotNone(request_type)
        self.assertIsNotNone(submit_api)
        request = request_type(
            session=LearningSession(
                id="session-1",
                goal_id="goal-1",
                course_id="course-1",
                node_id="runtime-state",
                status="learning",
            ),
            evidence=Evidence(
                id="evidence-1",
                session_id="other-session",
                node_id="runtime-state",
                kind="answer",
                content_ref="answer://runtime-state/1",
            ),
            run_id="run-1",
            sequence=4,
        )

        with TemporaryDirectory() as directory:
            result = submit_api(request, JsonLearningRepository(directory))

        self.assertEqual(
            result,
            ContractApiResult(
                ok=False,
                value=None,
                error_code="EVIDENCE_SESSION_MISMATCH",
                error_message="evidence must belong to learning session",
            ),
        )

    def test_start_node_learning_api_maps_course_goal_mismatch_to_error_code(self):
        request = learning_contracts.StartNodeLearningInput(
            goal=LearningGoal("goal-1", "掌握生产级 Agent Runtime"),
            course=Course(
                id="course-1",
                goal_id="other-goal",
                title="知识图谱学习系统",
                node_ids=("runtime-state",),
            ),
            node=ConceptNode(
                id="runtime-state",
                course_id="course-1",
                title="Runtime 状态契约",
            ),
            session_id="session-1",
            run_id="run-1",
            sequence=3,
        )

        try:
            result = learning_contracts.start_node_learning_api(request)
        except ValueError as error:
            self.fail(f"start_node_learning_api raised {error}")

        self.assertEqual(
            result,
            ContractApiResult(
                ok=False,
                value=None,
                error_code="COURSE_GOAL_MISMATCH",
                error_message="course must belong to learning goal",
            ),
        )

    def test_start_node_learning_api_maps_node_course_mismatch_to_error_code(self):
        request = learning_contracts.StartNodeLearningInput(
            goal=LearningGoal("goal-1", "掌握生产级 Agent Runtime"),
            course=Course(
                id="course-1",
                goal_id="goal-1",
                title="知识图谱学习系统",
                node_ids=("runtime-state",),
            ),
            node=ConceptNode(
                id="trace-event",
                course_id="course-1",
                title="TraceEvent",
            ),
            session_id="session-1",
            run_id="run-1",
            sequence=3,
        )

        try:
            result = learning_contracts.start_node_learning_api(request)
        except ValueError as error:
            self.fail(f"start_node_learning_api raised {error}")

        self.assertEqual(
            result,
            ContractApiResult(
                ok=False,
                value=None,
                error_code="NODE_NOT_IN_COURSE_GRAPH",
                error_message="node must belong to course graph",
            ),
        )

    def test_json_learning_repository_round_trips_course_node_and_progress(self):
        course = Course(
            id="course-1",
            goal_id="goal-1",
            title="知识图谱学习系统",
            node_ids=("runtime-state", "trace-event"),
        )
        node = ConceptNode(
            id="runtime-state",
            course_id="course-1",
            title="Runtime 状态契约",
        )
        progress = NodeProgress("runtime-state", 75, "learning")

        with TemporaryDirectory() as directory:
            writer = JsonLearningRepository(directory)
            writer.save_course(course)
            writer.save_node(node)
            writer.save_progress(progress)

            reader = JsonLearningRepository(directory)
            loaded_course = reader.load_course("course-1")
            loaded_node = reader.load_node("runtime-state")
            loaded_progress = reader.load_progress("runtime-state")

        self.assertEqual(loaded_course, course)
        self.assertEqual(loaded_node, node)
        self.assertEqual(loaded_progress, progress)
    def test_json_learning_repository_persists_updated_progress(self):
        evidence = Evidence(
            id="evidence-1",
            session_id="session-1",
            node_id="runtime-state",
            kind="answer",
            content_ref="answer://runtime-state/1",
        )
        eval_result = EvalResult(
            id="eval-1",
            evidence_id="evidence-1",
            node_id="runtime-state",
            passed=True,
            score=0.9,
            reason="answer explains runtime state boundaries",
        )

        with TemporaryDirectory() as directory:
            repository = JsonLearningRepository(directory)
            repository.save_progress(NodeProgress("runtime-state", 20, "learning"))
            progress, _ = apply_eval_result_to_progress(
                evidence,
                eval_result,
                previous_percent=repository.load_progress("runtime-state").percent,
                run_id="run-1",
                sequence=7,
            )
            repository.save_progress(progress)

            loaded_progress = JsonLearningRepository(directory).load_progress("runtime-state")

        self.assertEqual(loaded_progress, NodeProgress("runtime-state", 90, "verified"))

    def test_repository_backed_main_loop_persists_records_and_trace_order(self):
        goal = LearningGoal("goal-1", "掌握生产级 Agent Runtime")
        course = Course(
            id="course-1",
            goal_id="goal-1",
            title="知识图谱学习系统",
            node_ids=("runtime-state", "trace-event"),
        )
        nodes = (
            ConceptNode("runtime-state", "course-1", "Runtime 状态契约"),
            ConceptNode("trace-event", "course-1", "Trace 事件契约"),
        )
        dependency_edges = (
            learning_contracts.DependencyEdge("runtime-state", "trace-event", "prerequisite"),
        )
        evidence = Evidence(
            id="evidence-1",
            session_id="session-1",
            node_id="trace-event",
            kind="answer",
            content_ref="answer://trace-event/1",
        )
        eval_result = EvalResult(
            id="eval-1",
            evidence_id="evidence-1",
            node_id="trace-event",
            passed=True,
            score=0.8,
            reason="answer explains trace event payloads",
        )

        with TemporaryDirectory() as directory:
            repository = JsonLearningRepository(f"{directory}/learning")
            goal_result = learning_contracts.create_learning_goal_api(
                learning_contracts.CreateLearningGoalInput(
                    goal=goal,
                    run_id="run-e2e",
                    sequence=1,
                ),
                repository,
            )
            graph_result = learning_contracts.initialize_course_graph_api(
                learning_contracts.InitializeCourseGraphInput(
                    goal=goal,
                    course=course,
                    nodes=nodes,
                    dependency_edges=dependency_edges,
                    run_id="run-e2e",
                    sequence=2,
                ),
                repository,
            )
            session_result = learning_contracts.start_node_learning_api(
                learning_contracts.StartNodeLearningInput(
                    goal=goal,
                    course=course,
                    node=nodes[1],
                    session_id="session-1",
                    run_id="run-e2e",
                    sequence=3,
                ),
                repository,
            )
            session, session_event = session_result.value
            evidence_result = learning_contracts.submit_evidence_api(
                learning_contracts.SubmitEvidenceInput(
                    session=session,
                    evidence=evidence,
                    run_id="run-e2e",
                    sequence=4,
                ),
                repository,
            )
            eval_progress_result = submit_eval_progress(
                learning_contracts.SubmitEvalProgressInput(
                    evidence=evidence,
                    eval_result=eval_result,
                    previous_percent=0,
                    run_id="run-e2e",
                    sequence=5,
                ),
                repository,
            )
            leaf_progress, progress_event = eval_progress_result.value
            parent_progress_result = learning_contracts.recompute_parent_progress_api(
                learning_contracts.RecomputeParentProgressInput(
                    node_id="runtime-state",
                    children=(leaf_progress,),
                    previous_percent=0,
                    run_id="run-e2e",
                    sequence=6,
                ),
                repository,
            )
            parent_progress, parent_event = parent_progress_result.value
            goal_event = goal_result.value[1]
            graph_event = graph_result.value[1]
            evidence_event = evidence_result.value[1]
            events = (goal_event, graph_event, session_event, evidence_event, progress_event, parent_event)
            trace_store = TraceStore(f"{directory}/traces")
            trace_store.save(
                RunResult(
                    run_id="run-e2e",
                    task="repository-backed learning loop",
                    outcome="completed",
                    events=events,
                )
            )

            reloaded = JsonLearningRepository(f"{directory}/learning")
            loaded_goal = reloaded.load_goal("goal-1")
            loaded_graph = reloaded.load_course_graph("course-1")
            loaded_session = reloaded.load_session("session-1")
            loaded_evidence = reloaded.load_evidence("evidence-1")
            loaded_eval_result = reloaded.load_eval_result("eval-1")
            loaded_leaf_progress = reloaded.load_progress("trace-event")
            loaded_parent_progress = reloaded.load_progress("runtime-state")
            loaded_trace = trace_store.load("run-e2e")

        for result in (
            goal_result,
            graph_result,
            session_result,
            evidence_result,
            eval_progress_result,
            parent_progress_result,
        ):
            self.assertTrue(result.ok)
            self.assertIsNone(result.error_code)
        self.assertEqual(loaded_goal, goal)
        self.assertEqual(loaded_graph.course, course)
        self.assertEqual(loaded_graph.nodes, nodes)
        self.assertEqual(loaded_graph.dependency_edges, dependency_edges)
        self.assertEqual(loaded_session, session)
        self.assertEqual(loaded_evidence, evidence)
        self.assertEqual(loaded_eval_result, eval_result)
        self.assertEqual(loaded_leaf_progress, leaf_progress)
        self.assertEqual(loaded_parent_progress, parent_progress)
        self.assertEqual(leaf_progress, NodeProgress("trace-event", 80, "verified"))
        self.assertEqual(parent_progress, NodeProgress("runtime-state", 80, "learning"))
        self.assertEqual([event.sequence for event in loaded_trace.events], [1, 2, 3, 4, 5, 6])
        self.assertEqual({event.run_id for event in loaded_trace.events}, {"run-e2e"})
        self.assertEqual(
            [event.payload["event_type"] for event in loaded_trace.events],
            [
                "goal_created",
                "course_graph_created",
                "node_learning_started",
                "evidence_submitted",
                "progress_updated",
                "node_progress_recomputed",
            ],
        )

    def test_repository_backed_learning_loop_persists_graph_expansion_trace_and_replay_boundary(self):
        goal = LearningGoal("goal-1", "掌握生产级 Agent Runtime")
        course = Course(
            id="course-1",
            goal_id="goal-1",
            title="知识图谱学习系统",
            node_ids=("runtime-state", "trace-event"),
        )
        nodes = (
            ConceptNode("runtime-state", "course-1", "Runtime 状态契约"),
            ConceptNode("trace-event", "course-1", "Trace 事件契约"),
        )
        dependency_edges = (
            learning_contracts.DependencyEdge("runtime-state", "trace-event", "prerequisite"),
        )
        evidence = Evidence(
            id="evidence-1",
            session_id="session-1",
            node_id="trace-event",
            kind="answer",
            content_ref="answer://trace-event/1",
        )
        eval_result = EvalResult(
            id="eval-1",
            evidence_id="evidence-1",
            node_id="trace-event",
            passed=True,
            score=0.8,
            reason="answer explains trace event payloads",
        )
        next_evidence = Evidence(
            id="evidence-2",
            session_id="session-2",
            node_id="trace-payload-schema",
            kind="answer",
            content_ref="answer://trace-payload-schema/1",
        )
        next_eval_result = EvalResult(
            id="eval-2",
            evidence_id="evidence-2",
            node_id="trace-payload-schema",
            passed=True,
            score=0.9,
            reason="answer explains trace payload schema boundaries",
        )
        final_evidence = Evidence(
            id="evidence-3",
            session_id="session-3",
            node_id="trace-replay-boundary",
            kind="answer",
            content_ref="answer://trace-replay-boundary/1",
        )
        final_eval_result = EvalResult(
            id="eval-3",
            evidence_id="evidence-3",
            node_id="trace-replay-boundary",
            passed=True,
            score=1.0,
            reason="answer explains replay boundary checks",
        )

        with TemporaryDirectory() as directory:
            repository = JsonLearningRepository(f"{directory}/learning")
            goal_result = learning_contracts.create_learning_goal_api(
                learning_contracts.CreateLearningGoalInput(
                    goal=goal,
                    run_id="run-r4",
                    sequence=1,
                ),
                repository,
            )
            graph_result = learning_contracts.initialize_course_graph_api(
                learning_contracts.InitializeCourseGraphInput(
                    goal=goal,
                    course=course,
                    nodes=nodes,
                    dependency_edges=dependency_edges,
                    run_id="run-r4",
                    sequence=2,
                ),
                repository,
            )
            session_result = learning_contracts.start_node_learning_api(
                learning_contracts.StartNodeLearningInput(
                    goal=goal,
                    course=course,
                    node=nodes[1],
                    session_id="session-1",
                    run_id="run-r4",
                    sequence=3,
                ),
                repository,
            )
            session, session_event = session_result.value
            evidence_result = learning_contracts.submit_evidence_api(
                learning_contracts.SubmitEvidenceInput(
                    session=session,
                    evidence=evidence,
                    run_id="run-r4",
                    sequence=4,
                ),
                repository,
            )
            eval_progress_result = submit_eval_progress(
                learning_contracts.SubmitEvalProgressInput(
                    evidence=evidence,
                    eval_result=eval_result,
                    previous_percent=0,
                    run_id="run-r4",
                    sequence=5,
                ),
                repository,
            )
            leaf_progress, progress_event = eval_progress_result.value
            parent_progress_result = learning_contracts.recompute_parent_progress_api(
                learning_contracts.RecomputeParentProgressInput(
                    node_id="runtime-state",
                    children=(leaf_progress,),
                    previous_percent=0,
                    run_id="run-r4",
                    sequence=6,
                ),
                repository,
            )
            _, parent_event = parent_progress_result.value
            request_result = learning_contracts.create_graph_operation_request_api(
                learning_contracts.CreateGraphOperationRequestInput(
                    request_id="request-1",
                    course_id="course-1",
                    node_id="trace-event",
                    operation_type="expand",
                    user_intent="这个点不够细，展开下一级",
                    source="menu",
                    context_refs=("session://session-1", "evidence://evidence-1"),
                    run_id="run-r4",
                    sequence=7,
                ),
                repository,
            )
            graph_request, request_event = request_result.value
            proposal_result = learning_contracts.propose_graph_operation_api(
                learning_contracts.ProposeGraphOperationInput(
                    request=graph_request,
                    proposal_id="proposal-1",
                    summary="expand trace event into replay-focused subnodes",
                    rationale="learner needs finer trace replay boundaries",
                    proposed_nodes=("trace-payload-schema", "trace-replay-boundary"),
                    proposed_edges=(
                        ("trace-event", "trace-payload-schema"),
                        ("trace-payload-schema", "trace-replay-boundary"),
                    ),
                    progress_migration="keep parent progress and require new child evidence",
                    risks=("新增子节点可能让学习路径变长",),
                    run_id="run-r4",
                    sequence=8,
                ),
                repository,
            )
            proposal, proposal_event = proposal_result.value
            confirmation_result = learning_contracts.confirm_graph_operation_api(
                learning_contracts.ConfirmGraphOperationInput(
                    proposal=proposal,
                    confirmed_by="user",
                    run_id="run-r4",
                    sequence=9,
                ),
                repository,
            )
            confirmation, confirmation_event = confirmation_result.value
            apply_result = apply_graph_operation_api(
                learning_contracts.ApplyGraphOperationInput(
                    proposal=proposal,
                    confirmation=confirmation,
                    run_id="run-r4",
                    sequence=10,
                ),
                repository,
            )
            applied, apply_event = apply_result.value
            next_node_result = learning_contracts.select_next_learning_node_api(
                learning_contracts.SelectNextLearningNodeInput(
                    course_id="course-1",
                    run_id="run-r4",
                    sequence=11,
                ),
                repository,
            )
            next_node, next_node_event = next_node_result.value
            loaded_updated_graph = repository.load_course_graph("course-1")
            next_session_result = learning_contracts.start_node_learning_api(
                learning_contracts.StartNodeLearningInput(
                    goal=goal,
                    course=loaded_updated_graph.course,
                    node=repository.load_node(next_node.node_id),
                    session_id="session-2",
                    run_id="run-r4",
                    sequence=12,
                ),
                repository,
            )
            next_session, next_session_event = next_session_result.value
            loaded_next_session = repository.load_session("session-2")
            loaded_initialized_progress = (
                repository.load_progress("trace-payload-schema"),
                repository.load_progress("trace-replay-boundary"),
            )
            next_evidence_result = learning_contracts.submit_evidence_api(
                learning_contracts.SubmitEvidenceInput(
                    session=next_session,
                    evidence=next_evidence,
                    run_id="run-r4",
                    sequence=13,
                ),
                repository,
            )
            next_evidence_submitted, next_evidence_event = next_evidence_result.value
            next_eval_progress_result = submit_eval_progress(
                learning_contracts.SubmitEvalProgressInput(
                    evidence=next_evidence_submitted,
                    eval_result=next_eval_result,
                    previous_percent=loaded_initialized_progress[0].percent,
                    run_id="run-r4",
                    sequence=14,
                ),
                repository,
            )
            next_node_progress, next_progress_event = next_eval_progress_result.value
            trace_event_progress_before_recompute = repository.load_progress("trace-event")
            trace_event_parent_progress_result = learning_contracts.recompute_parent_progress_api(
                learning_contracts.RecomputeParentProgressInput(
                    node_id="trace-event",
                    children=(next_node_progress, repository.load_progress("trace-replay-boundary")),
                    previous_percent=trace_event_progress_before_recompute.percent,
                    run_id="run-r4",
                    sequence=15,
                ),
                repository,
            )
            trace_event_parent_progress, trace_event_parent_event = trace_event_parent_progress_result.value
            followup_next_node_result = learning_contracts.select_next_learning_node_api(
                learning_contracts.SelectNextLearningNodeInput(
                    course_id="course-1",
                    run_id="run-r4",
                    sequence=16,
                ),
                repository,
            )
            followup_next_node, followup_next_node_event = followup_next_node_result.value
            loaded_next_evidence = repository.load_evidence("evidence-2")
            loaded_next_eval_result = repository.load_eval_result("eval-2")
            loaded_next_node_progress = repository.load_progress("trace-payload-schema")
            loaded_trace_event_parent_progress = repository.load_progress("trace-event")
            followup_session_result = learning_contracts.start_node_learning_api(
                learning_contracts.StartNodeLearningInput(
                    goal=goal,
                    course=loaded_updated_graph.course,
                    node=repository.load_node(followup_next_node.node_id),
                    session_id="session-3",
                    run_id="run-r4",
                    sequence=17,
                ),
                repository,
            )
            followup_session, followup_session_event = followup_session_result.value
            loaded_followup_session = repository.load_session("session-3")
            final_evidence_result = learning_contracts.submit_evidence_api(
                learning_contracts.SubmitEvidenceInput(
                    session=followup_session,
                    evidence=final_evidence,
                    run_id="run-r4",
                    sequence=18,
                ),
                repository,
            )
            final_evidence_submitted, final_evidence_event = final_evidence_result.value
            final_eval_progress_result = submit_eval_progress(
                learning_contracts.SubmitEvalProgressInput(
                    evidence=final_evidence_submitted,
                    eval_result=final_eval_result,
                    previous_percent=repository.load_progress("trace-replay-boundary").percent,
                    run_id="run-r4",
                    sequence=19,
                ),
                repository,
            )
            final_node_progress, final_progress_event = final_eval_progress_result.value
            trace_event_progress_before_final_recompute = repository.load_progress("trace-event")
            final_trace_event_parent_progress_result = learning_contracts.recompute_parent_progress_api(
                learning_contracts.RecomputeParentProgressInput(
                    node_id="trace-event",
                    children=(repository.load_progress("trace-payload-schema"), final_node_progress),
                    previous_percent=trace_event_progress_before_final_recompute.percent,
                    run_id="run-r4",
                    sequence=20,
                ),
                repository,
            )
            final_trace_event_parent_progress, final_trace_event_parent_event = final_trace_event_parent_progress_result.value
            terminal_next_node_result = learning_contracts.select_next_learning_node_api(
                learning_contracts.SelectNextLearningNodeInput(
                    course_id="course-1",
                    run_id="run-r4",
                    sequence=21,
                ),
                repository,
            )
            terminal_result = learning_contracts.complete_agent_run_api(
                learning_contracts.CompleteAgentRunInput(
                    run_id="run-r4",
                    sequence=21,
                    status="completed",
                    reason=terminal_next_node_result.error_message,
                    recoverable=False,
                    next_action="no remaining learning nodes",
                )
            )
            terminal_status, terminal_event = terminal_result.value
            loaded_final_evidence = repository.load_evidence("evidence-3")
            loaded_final_eval_result = repository.load_eval_result("eval-3")
            loaded_final_node_progress = repository.load_progress("trace-replay-boundary")
            loaded_final_trace_event_parent_progress = repository.load_progress("trace-event")
            events = (
                goal_result.value[1],
                graph_result.value[1],
                session_event,
                evidence_result.value[1],
                progress_event,
                parent_event,
                request_event,
                proposal_event,
                confirmation_event,
                apply_event,
                next_node_event,
                next_session_event,
                next_evidence_event,
                next_progress_event,
                trace_event_parent_event,
                followup_next_node_event,
                followup_session_event,
                final_evidence_event,
                final_progress_event,
                final_trace_event_parent_event,
                terminal_event,
            )
            trace_store = TraceStore(f"{directory}/traces")
            trace_store.save(
                RunResult(
                    run_id="run-r4",
                    task="repository-backed learning loop with graph expansion",
                    outcome="completed",
                    events=events,
                )
            )

            loaded_trace = trace_store.load("run-r4")
            replay_repository = JsonLearningRepository(f"{directory}/replay")
            replay = learning_contracts.replay_graph_operations_from_trace(loaded_trace, replay_repository)
            loaded_replayed_request = replay_repository.load_graph_operation_request("request-1")
            loaded_replayed_proposal = replay_repository.load_graph_operation_proposal("proposal-1")
            loaded_replayed_confirmation = replay_repository.load_graph_operation_confirmation("proposal-1")
            loaded_replayed_applied = replay_repository.load_applied_graph_operation("proposal-1")
            summarize_regression = getattr(learning_contracts, "summarize_learning_loop_replay_regression", None)
            summary_type = getattr(learning_contracts, "LearningLoopReplayRegressionSummary", None)
            self.assertIsNotNone(summarize_regression)
            self.assertIsNotNone(summary_type)
            regression_summary = summarize_regression(loaded_trace, replay)
            with self.assertRaises(learning_contracts.LearningRecordNotFound):
                replay_repository.load_goal("goal-1")

        for result in (
            goal_result,
            graph_result,
            session_result,
            evidence_result,
            eval_progress_result,
            parent_progress_result,
            request_result,
            proposal_result,
            confirmation_result,
            apply_result,
            next_node_result,
            next_session_result,
            next_evidence_result,
            next_eval_progress_result,
            trace_event_parent_progress_result,
            followup_next_node_result,
            followup_session_result,
            final_evidence_result,
            final_eval_progress_result,
            final_trace_event_parent_progress_result,
            terminal_result,
        ):
            self.assertTrue(result.ok)
            self.assertIsNone(result.error_code)
        self.assertEqual(tuple(event.payload["event_type"] for event in loaded_trace.events), LEARNING_LOOP_EVENT_TYPES)
        self.assertEqual([event.sequence for event in loaded_trace.events], list(range(1, 22)))
        self.assertEqual({event.run_id for event in loaded_trace.events}, {"run-r4"})
        self.assertEqual(
            loaded_updated_graph.course.node_ids,
            ("runtime-state", "trace-event", "trace-payload-schema", "trace-replay-boundary"),
        )
        self.assertEqual(
            loaded_updated_graph.nodes,
            (
                ConceptNode("runtime-state", "course-1", "Runtime 状态契约"),
                ConceptNode("trace-event", "course-1", "Trace 事件契约"),
                ConceptNode("trace-payload-schema", "course-1", "trace-payload-schema"),
                ConceptNode("trace-replay-boundary", "course-1", "trace-replay-boundary"),
            ),
        )
        self.assertEqual(
            loaded_updated_graph.dependency_edges,
            (
                learning_contracts.DependencyEdge("runtime-state", "trace-event", "prerequisite"),
                learning_contracts.DependencyEdge("trace-event", "trace-payload-schema", "prerequisite"),
                learning_contracts.DependencyEdge("trace-payload-schema", "trace-replay-boundary", "prerequisite"),
            ),
        )
        self.assertEqual(
            loaded_initialized_progress,
            (
                NodeProgress("trace-payload-schema", 0, "unknown"),
                NodeProgress("trace-replay-boundary", 0, "unknown"),
            ),
        )
        self.assertEqual(apply_event.payload["course_id"], "course-1")
        self.assertEqual(
            apply_event.payload["initialized_progress"],
            (
                ("trace-payload-schema", 0, "unknown"),
                ("trace-replay-boundary", 0, "unknown"),
            ),
        )
        self.assertEqual(
            next_node,
            learning_contracts.NextLearningNode(
                course_id="course-1",
                node_id="trace-payload-schema",
                prerequisite_node_ids=("trace-event",),
                reason="first unknown node with prerequisites satisfied",
            ),
        )
        self.assertEqual(next_node_event.payload["event_type"], "node_selected")
        self.assertEqual(next_node_event.payload["node_id"], "trace-payload-schema")
        self.assertEqual(next_node_event.payload["prerequisite_node_ids"], ("trace-event",))
        self.assertEqual(
            next_session,
            LearningSession(
                id="session-2",
                goal_id="goal-1",
                course_id="course-1",
                node_id="trace-payload-schema",
                status="learning",
            ),
        )
        self.assertEqual(loaded_next_session, next_session)
        self.assertEqual(next_session_event.payload["event_type"], "node_learning_started")
        self.assertEqual(next_session_event.payload["node_id"], next_node.node_id)
        self.assertEqual(next_session_event.payload["session_id"], "session-2")
        self.assertEqual(loaded_next_evidence, next_evidence)
        self.assertEqual(loaded_next_eval_result, next_eval_result)
        self.assertEqual(loaded_next_node_progress, NodeProgress("trace-payload-schema", 90, "verified"))
        self.assertEqual(loaded_trace_event_parent_progress, NodeProgress("trace-event", 45, "learning"))
        self.assertEqual(next_node_progress, loaded_next_node_progress)
        self.assertEqual(trace_event_parent_progress, loaded_trace_event_parent_progress)
        self.assertEqual(next_evidence_event.payload["event_type"], "evidence_submitted")
        self.assertEqual(next_evidence_event.payload["session_id"], "session-2")
        self.assertEqual(next_progress_event.payload["event_type"], "progress_updated")
        self.assertEqual(next_progress_event.payload["node_id"], "trace-payload-schema")
        self.assertEqual(trace_event_parent_event.payload["event_type"], "node_progress_recomputed")
        self.assertEqual(trace_event_parent_event.payload["node_id"], "trace-event")
        self.assertEqual(
            followup_next_node,
            learning_contracts.NextLearningNode(
                course_id="course-1",
                node_id="trace-replay-boundary",
                prerequisite_node_ids=("trace-payload-schema",),
                reason="first unknown node with prerequisites satisfied",
            ),
        )
        self.assertEqual(followup_next_node_event.payload["event_type"], "node_selected")
        self.assertEqual(followup_next_node_event.payload["node_id"], "trace-replay-boundary")
        self.assertEqual(followup_next_node_event.payload["prerequisite_node_ids"], ("trace-payload-schema",))
        self.assertEqual(
            followup_session,
            LearningSession(
                id="session-3",
                goal_id="goal-1",
                course_id="course-1",
                node_id="trace-replay-boundary",
                status="learning",
            ),
        )
        self.assertEqual(loaded_followup_session, followup_session)
        self.assertEqual(followup_session_event.payload["event_type"], "node_learning_started")
        self.assertEqual(followup_session_event.payload["node_id"], followup_next_node.node_id)
        self.assertEqual(followup_session_event.payload["session_id"], "session-3")
        self.assertEqual(loaded_final_evidence, final_evidence)
        self.assertEqual(loaded_final_eval_result, final_eval_result)
        self.assertEqual(loaded_final_node_progress, NodeProgress("trace-replay-boundary", 100, "verified"))
        self.assertEqual(loaded_final_trace_event_parent_progress, NodeProgress("trace-event", 95, "learning"))
        self.assertEqual(final_node_progress, loaded_final_node_progress)
        self.assertEqual(final_trace_event_parent_progress, loaded_final_trace_event_parent_progress)
        self.assertEqual(final_evidence_event.payload["event_type"], "evidence_submitted")
        self.assertEqual(final_evidence_event.payload["session_id"], "session-3")
        self.assertEqual(final_progress_event.payload["event_type"], "progress_updated")
        self.assertEqual(final_progress_event.payload["node_id"], "trace-replay-boundary")
        self.assertEqual(final_trace_event_parent_event.payload["event_type"], "node_progress_recomputed")
        self.assertEqual(final_trace_event_parent_event.payload["node_id"], "trace-event")
        self.assertEqual(
            terminal_next_node_result,
            ContractApiResult(
                ok=False,
                value=None,
                error_code="NEXT_LEARNING_NODE_NOT_FOUND",
                error_message="no selectable learning node",
            ),
        )
        self.assertEqual(
            terminal_status,
            learning_contracts.TerminalStatus(
                run_id="run-r4",
                status="completed",
                reason="no selectable learning node",
                recoverable=False,
                next_action="no remaining learning nodes",
            ),
        )
        self.assertEqual(terminal_event.payload["event_type"], "run_completed")
        self.assertEqual(terminal_event.payload["terminal_status"], "completed")
        self.assertEqual(terminal_event.payload["reason"], "no selectable learning node")
        self.assertEqual(terminal_event.payload["recoverable"], False)
        self.assertEqual(terminal_event.payload["next_action"], "no remaining learning nodes")
        self.assertEqual(
            regression_summary,
            learning_contracts.LearningLoopReplayRegressionSummary(
                run_id="run-r4",
                terminal_status="completed",
                completion_reason="no selectable learning node",
                graph_replay_completed=True,
                replayed_request_count=1,
                replayed_proposal_count=1,
                replayed_confirmation_count=1,
                replayed_applied_count=1,
                trace_matches_contract=True,
                final_learning_completed=True,
                remaining_selectable_nodes=0,
                regression_passed=True,
                report="Learning loop completed; graph expansion replayed; no remaining selectable nodes.",
            ),
        )
        self.assertEqual(replay.requests, (graph_request,))
        self.assertEqual(replay.proposals, (proposal,))
        self.assertEqual(replay.confirmations, (confirmation,))
        self.assertEqual(replay.applied_operations, (applied,))
        self.assertEqual(loaded_replayed_request, graph_request)
        self.assertEqual(loaded_replayed_proposal, proposal)
        self.assertEqual(loaded_replayed_confirmation, confirmation)
        self.assertEqual(loaded_replayed_applied, applied)


if __name__ == "__main__":
    unittest.main()
