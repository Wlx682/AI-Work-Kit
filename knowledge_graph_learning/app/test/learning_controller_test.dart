import 'package:flutter_test/flutter_test.dart';
import 'package:nexus_learning/src/learning_controller.dart';
import 'package:nexus_learning/src/localization/ui_message.dart';

import 'test_support.dart';

void main() {
  test(
    'workspace destination changes without replacing course state',
    () async {
      final controller = LearningController(FakeLearningApi());
      await controller.createGoal('Production-grade AI Agents');
      final course = controller.course;

      await controller.selectDestination(WorkspaceDestination.practice);

      expect(controller.destination, WorkspaceDestination.practice);
      expect(controller.course, same(course));
      expect(controller.notice?.key, UiMessageKey.workspaceOpened);
      expect(controller.notice?.destination, 'practice');
    },
  );

  test('path loads its recommendation from the API exactly once', () async {
    final api = FakeLearningApi();
    final controller = LearningController(api);
    await controller.createGoal('Production-grade AI Agents');

    await controller.selectDestination(WorkspaceDestination.path);
    await controller.selectDestination(WorkspaceDestination.path);

    expect(api.recommendationCalls, 1);
    expect(controller.recommendation!.node.slug, 'checkpoint-interrupt');
    expect(controller.recommendation!.prerequisiteNodeIds, hasLength(1));
    expect(controller.recommendation!.reason, contains('Course graph marks'));
  });

  test('empty Evidence is rejected before the API call', () async {
    final api = FakeLearningApi();
    final controller = LearningController(api);
    await controller.createGoal('Production-grade AI Agents');
    await controller.selectNode(controller.course!.nodes[4]);

    expect(controller.activity!.question, 'API-generated practice question?');

    await controller.submitEvidence('   ');

    expect(api.evidenceCalls, 0);
    expect(controller.error?.key, UiMessageKey.evidenceEmpty);
    expect(controller.pendingReview, isNull);
  });

  test('successful Evidence is trimmed and opens Review', () async {
    final api = FakeLearningApi();
    final controller = LearningController(api);
    await controller.createGoal('Production-grade AI Agents');
    await controller.selectNode(controller.course!.nodes[4]);
    await controller.selectDestination(WorkspaceDestination.practice);

    await controller.submitEvidence('  State is resumable truth.  ');

    expect(api.evidenceCalls, 1);
    expect(api.lastEvidenceAnswer, 'State is resumable truth.');
    expect(controller.submittedEvidence, 'State is resumable truth.');
    expect(controller.pendingReview, isNotNull);
    expect(controller.destination, WorkspaceDestination.review);
  });

  test(
    'controller completes goal, session, Evidence, HITL, and graph apply',
    () async {
      final api = FakeLearningApi();
      final controller = LearningController(api);

      await controller.createGoal('Production-grade AI Agents');
      final runtimeState = controller.course!.nodes.firstWhere(
        (node) => node.slug == 'runtime-state',
      );
      await controller.selectNode(runtimeState);
      await controller.submitEvidence(
        'State resumes execution; Trace explains history.',
      );

      expect(controller.pendingReview!.status, 'paused');
      expect(controller.course!.nodes, hasLength(10));

      await controller.decide(true);

      expect(api.reviewCalls, 1);
      expect(api.lastDecision, isTrue);
      expect(controller.pendingReview, isNotNull);
      expect(controller.reviewApproved, isTrue);
      expect(controller.reviewOutcome, 'completed');
      expect(
        controller.pendingReview!.events.map((event) => event.phase),
        contains('apply_graph_update'),
      );
      expect(controller.course!.nodes, hasLength(13));
      expect(controller.notice?.key, UiMessageKey.proposalApplied);
      expect(controller.notice?.count, 13);
    },
  );

  test('rejection preserves the ten-node graph', () async {
    final api = FakeLearningApi();
    final controller = LearningController(api);
    await controller.createGoal('Production-grade AI Agents');
    await controller.selectNode(controller.course!.nodes[4]);
    await controller.submitEvidence('State and Trace are separate.');

    await controller.decide(false);

    expect(api.lastDecision, isFalse);
    expect(controller.course!.nodes, hasLength(10));
    expect(controller.reviewApproved, isFalse);
    expect(controller.reviewOutcome, 'completed_without_graph_update');
    expect(controller.notice?.key, UiMessageKey.proposalRejected);
  });
}
