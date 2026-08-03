import 'package:flutter/foundation.dart';

import 'learning_api.dart';
import 'localization/ui_message.dart';
import 'models.dart';

enum WorkspaceDestination { graph, path, practice, review, progress }

class LearningController extends ChangeNotifier {
  LearningController(this.api);

  final LearningApi api;

  LearningCourse? course;
  LearningRecommendation? recommendation;
  LearningNode? selectedNode;
  LearningSession? session;
  LearningActivity? activity;
  String? submittedEvidence;
  RuntimeReview? pendingReview;
  bool? reviewApproved;
  String? reviewOutcome;
  WorkspaceDestination destination = WorkspaceDestination.graph;
  bool busy = false;
  UiMessage? error;
  UiMessage? notice;

  Future<void> createGoal(String title) => _perform(() async {
    final created = await api.createGoal(title);
    course = created.course;
    recommendation = null;
    selectedNode = null;
    session = null;
    activity = null;
    submittedEvidence = null;
    pendingReview = null;
    reviewApproved = null;
    reviewOutcome = null;
    destination = WorkspaceDestination.graph;
    notice = UiMessage(UiMessageKey.graphGenerated, {
      'count': course!.nodes.length,
    });
  });

  Future<void> selectDestination(WorkspaceDestination value) async {
    if (destination != value) {
      destination = value;
      notice = UiMessage(UiMessageKey.workspaceOpened, {
        'destination': value.name,
      });
      notifyListeners();
    }
    if (value == WorkspaceDestination.path && recommendation == null && !busy) {
      final currentCourse = course;
      if (currentCourse == null) return;
      await _perform(() async {
        recommendation = await api.fetchRecommendation(currentCourse.id);
        notice = const UiMessage(UiMessageKey.recommendationLoaded);
      });
    }
  }

  Future<void> startRecommendedPractice() async {
    final current = recommendation;
    if (current == null) return;
    await selectNode(current.node);
    if (error != null || session == null) return;
    destination = WorkspaceDestination.practice;
    notice = UiMessage(UiMessageKey.practiceOpened, {
      'title': current.node.title,
    });
    notifyListeners();
  }

  Future<void> selectNode(LearningNode node) => _perform(() async {
    final currentCourse = course;
    if (currentCourse == null) return;
    selectedNode = node;
    final started = await api.startSession(currentCourse.id, node.id);
    session = started.session;
    activity = started.activity;
    submittedEvidence = null;
    pendingReview = null;
    reviewApproved = null;
    reviewOutcome = null;
    notice = UiMessage(UiMessageKey.sessionStarted, {'title': node.title});
  });

  Future<void> submitEvidence(String answer) => _perform(() async {
    final currentSession = session;
    if (currentSession == null) {
      error = const UiMessage(UiMessageKey.selectNodeBeforeEvidence);
      return;
    }
    final normalized = answer.trim();
    if (normalized.isEmpty) {
      error = const UiMessage(UiMessageKey.evidenceEmpty);
      return;
    }
    pendingReview = await api.submitEvidence(currentSession.id, normalized);
    submittedEvidence = normalized;
    reviewApproved = null;
    reviewOutcome = null;
    destination = WorkspaceDestination.review;
    notice = UiMessage(
      pendingReview!.status == 'paused'
          ? UiMessageKey.evidenceReviewRequired
          : UiMessageKey.evidenceReviewReady,
    );
  });

  Future<void> decide(bool approved) => _perform(() async {
    final review = pendingReview;
    final currentCourse = course;
    if (review == null || currentCourse == null) return;
    final result = await api.reviewGraphUpdate(
      threadId: review.threadId,
      parentRunId: review.runId,
      courseId: currentCourse.id,
      approved: approved,
    );
    course = result.course;
    recommendation = null;
    pendingReview = review.withAdditionalEvents(result.events);
    reviewApproved = approved;
    reviewOutcome = result.outcome;
    selectedNode = course!.nodes.firstWhere(
      (node) => node.id == selectedNode?.id,
      orElse: () => course!.nodes.first,
    );
    notice = approved
        ? UiMessage(UiMessageKey.proposalApplied, {
            'count': course!.nodes.length,
          })
        : const UiMessage(UiMessageKey.proposalRejected);
  });

  Future<void> _perform(Future<void> Function() operation) async {
    busy = true;
    error = null;
    notifyListeners();
    try {
      await operation();
    } catch (exception) {
      error = exception is LearningApiException
          ? UiMessage(UiMessageKey.apiError, {
              'code': exception.code,
              'text': exception.message,
            })
          : UiMessage(UiMessageKey.unexpectedError, {
              'text': exception.toString(),
            });
    } finally {
      busy = false;
      notifyListeners();
    }
  }
}
