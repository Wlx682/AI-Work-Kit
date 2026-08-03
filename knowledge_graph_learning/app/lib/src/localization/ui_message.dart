// Locale-neutral presentation messages emitted by the controller.

enum UiMessageKey {
  graphGenerated,
  workspaceOpened,
  recommendationLoaded,
  practiceOpened,
  sessionStarted,
  selectNodeBeforeEvidence,
  evidenceEmpty,
  evidenceReviewRequired,
  evidenceReviewReady,
  proposalApplied,
  proposalRejected,
  apiError,
  unexpectedError,
}

class UiMessage {
  const UiMessage(this.key, [this.arguments = const {}]);

  final UiMessageKey key;
  final Map<String, Object?> arguments;

  String? get text => arguments['text'] as String?;
  String? get code => arguments['code'] as String?;
  String? get title => arguments['title'] as String?;
  int? get count => arguments['count'] as int?;
  String? get destination => arguments['destination'] as String?;
}
