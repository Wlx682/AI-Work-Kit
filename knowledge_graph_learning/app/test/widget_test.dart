import 'package:flutter/material.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:nexus_learning/src/learning_api.dart';
import 'package:nexus_learning/src/models.dart';
import 'package:nexus_learning/src/nexus_app.dart';

import 'test_support.dart';

void main() {
  testWidgets('language menu switches the interface to Simplified Chinese', (
    tester,
  ) async {
    await tester.binding.setSurfaceSize(const Size(1280, 900));
    addTearDown(() => tester.binding.setSurfaceSize(null));
    await tester.pumpWidget(NexusApp(api: FakeLearningApi()));

    expect(
      find.text('What do you want\nto understand deeply?'),
      findsOneWidget,
    );
    await tester.tap(find.byKey(const Key('language-menu')));
    await tester.pumpAndSettle();
    await tester.tap(find.text('简体中文').last);
    await tester.pumpAndSettle();

    expect(find.text('你想深入理解\n什么内容？'), findsOneWidget);
    expect(find.text('生成图谱'), findsOneWidget);
    expect(find.text('个人学习空间'), findsOneWidget);
    expect(tester.takeException(), isNull);
  });

  testWidgets('an explicit Chinese locale renders localized API errors', (
    tester,
  ) async {
    await tester.binding.setSurfaceSize(const Size(1280, 900));
    addTearDown(() => tester.binding.setSurfaceSize(null));
    await tester.pumpWidget(
      NexusApp(api: _FailingLearningApi(), initialLocale: const Locale('zh')),
    );

    await tester.tap(find.byKey(const Key('create-goal')));
    await tester.pumpAndSettle();

    expect(find.textContaining('DeepSeek 尚未配置'), findsOneWidget);
  });

  testWidgets('goal creation opens the live knowledge graph', (tester) async {
    await tester.binding.setSurfaceSize(const Size(1280, 900));
    addTearDown(() => tester.binding.setSurfaceSize(null));
    await tester.pumpWidget(NexusApp(api: FakeLearningApi()));

    final goalInput = tester.widget<TextField>(
      find.byKey(const Key('goal-input')),
    );
    expect(goalInput.controller!.text, isEmpty);
    expect(find.text('Vincent'), findsNothing);
    expect(find.text('12 days'), findsNothing);

    expect(
      find.text('What do you want\nto understand deeply?'),
      findsOneWidget,
    );
    await tester.tap(find.byKey(const Key('create-goal')));
    await tester.pumpAndSettle();

    expect(find.byKey(const Key('graph-canvas')), findsOneWidget);
    expect(find.text('Production-grade AI Agents'), findsOneWidget);
    expect(find.byKey(const Key('node-runtime-state')), findsOneWidget);
    final nodeLocations = sampleCourse().nodes
        .map((node) => tester.getTopLeft(find.byKey(Key('node-${node.slug}'))))
        .toSet();
    expect(nodeLocations, hasLength(sampleCourse().nodes.length));
    final foundation = tester.getCenter(
      find.byKey(const Key('node-agent-foundations')),
    );
    final runtimeBasics = tester.getCenter(
      find.byKey(const Key('node-runtime-basics')),
    );
    final toolBoundaries = tester.getCenter(
      find.byKey(const Key('node-tool-boundaries')),
    );
    expect(runtimeBasics.dy, greaterThan(foundation.dy));
    expect(toolBoundaries.dy, closeTo(runtimeBasics.dy, 1));
    expect(toolBoundaries.dx, isNot(closeTo(runtimeBasics.dx, 1)));

    await tester.tap(find.byKey(const Key('nav-path')));
    await tester.pumpAndSettle();
    expect(find.byKey(const Key('workspace-path')), findsOneWidget);
    expect(find.byKey(const Key('path-recommendation')), findsOneWidget);
    expect(find.text('Checkpoint & Interrupt'), findsOneWidget);
    expect(find.text('Runtime State'), findsOneWidget);
    expect(find.textContaining('Course graph marks'), findsOneWidget);
    expect(find.byKey(const Key('graph-canvas')), findsNothing);
  });

  testWidgets('mobile layout keeps graph and bottom navigation available', (
    tester,
  ) async {
    await tester.binding.setSurfaceSize(const Size(390, 844));
    addTearDown(() => tester.binding.setSurfaceSize(null));
    await tester.pumpWidget(NexusApp(api: FakeLearningApi()));
    expect(
      tester.takeException(),
      isNull,
      reason: 'initial mobile goal layout',
    );
    await tester.tap(find.byKey(const Key('create-goal')));
    await tester.pumpAndSettle();

    expect(find.byType(NavigationBar), findsOneWidget);
    expect(find.byKey(const Key('graph-canvas')), findsOneWidget);
    expect(tester.takeException(), isNull, reason: 'mobile graph layout');

    await tester.tap(find.text('Path'));
    await tester.pumpAndSettle();
    expect(find.byKey(const Key('path-recommendation')), findsOneWidget);
    expect(find.byKey(const Key('path-prerequisites')), findsOneWidget);
    expect(tester.takeException(), isNull, reason: 'mobile path layout');

    await tester.tap(find.text('Practice'));
    await tester.pumpAndSettle();
    expect(find.byKey(const Key('workspace-practice')), findsOneWidget);
    expect(find.byKey(const Key('graph-canvas')), findsNothing);
    expect(tester.takeException(), isNull, reason: 'mobile practice layout');

    await tester.tap(find.text('Review'));
    await tester.pumpAndSettle();
    expect(find.byKey(const Key('workspace-review')), findsOneWidget);
    expect(find.byKey(const Key('runtime-timeline')), findsNothing);
    expect(tester.takeException(), isNull, reason: 'mobile empty review');

    await tester.tap(find.text('Progress'));
    await tester.pumpAndSettle();
    expect(find.byKey(const Key('workspace-progress')), findsOneWidget);
    expect(find.byKey(const Key('progress-mastery')), findsOneWidget);
    expect(find.byKey(const Key('progress-state-verified')), findsOneWidget);
    expect(find.text('51%'), findsOneWidget);
    expect(tester.takeException(), isNull, reason: 'mobile progress layout');
  });

  testWidgets(
    'recommended Practice submits trimmed Evidence and opens Review',
    (tester) async {
      await tester.binding.setSurfaceSize(const Size(1280, 900));
      addTearDown(() => tester.binding.setSurfaceSize(null));
      final api = FakeLearningApi();
      await tester.pumpWidget(NexusApp(api: api));
      await tester.tap(find.byKey(const Key('create-goal')));
      await tester.pumpAndSettle();
      await tester.tap(find.byKey(const Key('nav-path')));
      await tester.pumpAndSettle();

      await tester.tap(find.byKey(const Key('start-recommended-practice')));
      await tester.pumpAndSettle();

      expect(find.byKey(const Key('workspace-practice')), findsOneWidget);
      expect(find.byKey(const Key('practice-question')), findsOneWidget);
      expect(find.text('Checkpoint & Interrupt'), findsOneWidget);
      expect(find.text('API-generated practice question?'), findsOneWidget);
      expect(find.textContaining('Explain the boundary'), findsOneWidget);
      final submitFinder = find.byKey(const Key('practice-submit-evidence'));
      expect(tester.widget<FilledButton>(submitFinder).onPressed, isNull);

      await tester.enterText(
        find.byKey(const Key('practice-evidence-input')),
        '  Checkpoint persists state; Interrupt pauses for a human decision.  ',
      );
      await tester.pump();
      expect(tester.widget<FilledButton>(submitFinder).onPressed, isNotNull);
      await tester.ensureVisible(submitFinder);
      await tester.tap(submitFinder);
      await tester.pumpAndSettle();

      expect(api.evidenceCalls, 1);
      expect(
        api.lastEvidenceAnswer,
        'Checkpoint persists state; Interrupt pauses for a human decision.',
      );
      expect(find.byKey(const Key('workspace-review')), findsOneWidget);
      expect(find.byKey(const Key('review-evidence')), findsOneWidget);
      expect(find.text('86%'), findsOneWidget);
      expect(find.byKey(const Key('runtime-timeline')), findsOneWidget);
      expect(find.byKey(const Key('runtime-event-evaluator')), findsOneWidget);
      expect(
        find.byKey(const Key('runtime-event-human_review')),
        findsOneWidget,
      );

      final approveFinder = find.byKey(const Key('approve-proposal'));
      await tester.ensureVisible(approveFinder);
      await tester.tap(approveFinder);
      await tester.pumpAndSettle();

      expect(api.reviewCalls, 1);
      expect(find.byKey(const Key('review-decision-result')), findsOneWidget);
      expect(
        find.byKey(const Key('runtime-event-apply_graph_update')),
        findsOneWidget,
      );
      expect(find.byKey(const Key('approve-proposal')), findsNothing);

      await tester.tap(find.byKey(const Key('nav-progress')));
      await tester.pumpAndSettle();
      expect(find.byKey(const Key('workspace-progress')), findsOneWidget);
      expect(find.byKey(const Key('progress-state-unknown')), findsOneWidget);
      expect(find.text('38%'), findsOneWidget);
    },
  );
}

class _FailingLearningApi extends FakeLearningApi {
  @override
  Future<GoalCreation> createGoal(String title) {
    throw const LearningApiException(
      'DEEPSEEK_API_KEY is not configured',
      code: 'LLM_NOT_CONFIGURED',
    );
  }
}
