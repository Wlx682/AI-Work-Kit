// Maps locale-neutral controller state and backend codes to ARB messages.

import '../../l10n/app_localizations.dart';
import '../learning_controller.dart';
import 'ui_message.dart';

String localizeDestination(
  AppLocalizations localizations,
  WorkspaceDestination destination,
) {
  return switch (destination) {
    WorkspaceDestination.graph => localizations.navKnowledgeGraph,
    WorkspaceDestination.path => localizations.navLearningPath,
    WorkspaceDestination.practice => localizations.navPractice,
    WorkspaceDestination.review => localizations.navReview,
    WorkspaceDestination.progress => localizations.navProgress,
  };
}

String localizeMasteryState(AppLocalizations localizations, String state) {
  return switch (state) {
    'verified' => localizations.stateVerified,
    'practiced' => localizations.statePracticed,
    'recommended' => localizations.stateRecommended,
    'locked' => localizations.stateLocked,
    _ => localizations.stateUnknown,
  };
}

String localizeRuntimeStatus(AppLocalizations localizations, String status) {
  return switch (status) {
    'completed' => localizations.statusCompleted,
    'paused' => localizations.statusPaused,
    'failed' => localizations.statusFailed,
    _ => status,
  };
}

String localizeUiMessage(AppLocalizations localizations, UiMessage message) {
  return switch (message.key) {
    UiMessageKey.graphGenerated => localizations.noticeGraphGenerated(
      message.count ?? 0,
    ),
    UiMessageKey.workspaceOpened => localizations.noticeWorkspaceOpened(
      localizeDestination(
        localizations,
        WorkspaceDestination.values.byName(message.destination ?? 'graph'),
      ),
    ),
    UiMessageKey.recommendationLoaded =>
      localizations.noticeRecommendationLoaded,
    UiMessageKey.practiceOpened => localizations.noticePracticeOpened(
      message.title ?? '',
    ),
    UiMessageKey.sessionStarted => localizations.noticeSessionStarted(
      message.title ?? '',
    ),
    UiMessageKey.selectNodeBeforeEvidence =>
      localizations.errorSelectNodeBeforeEvidence,
    UiMessageKey.evidenceEmpty => localizations.errorEvidenceEmpty,
    UiMessageKey.evidenceReviewRequired =>
      localizations.noticeEvidenceReviewRequired,
    UiMessageKey.evidenceReviewReady => localizations.noticeEvidenceReviewReady,
    UiMessageKey.proposalApplied => localizations.noticeProposalApplied(
      message.count ?? 0,
    ),
    UiMessageKey.proposalRejected => localizations.noticeProposalRejected,
    UiMessageKey.apiError => _localizeApiError(localizations, message),
    UiMessageKey.unexpectedError => localizations.errorGenericApi(
      message.text ?? '',
    ),
  };
}

String _localizeApiError(AppLocalizations localizations, UiMessage message) {
  return switch (message.code) {
    'LLM_NOT_CONFIGURED' => localizations.errorDeepSeekNotConfigured,
    'LEARNING_INTELLIGENCE_FAILED' => localizations.errorIntelligenceFailed,
    'INVALID_INTELLIGENCE_OUTPUT' =>
      localizations.errorInvalidIntelligenceOutput,
    _ => localizations.errorGenericApi(message.text ?? message.code ?? ''),
  };
}
