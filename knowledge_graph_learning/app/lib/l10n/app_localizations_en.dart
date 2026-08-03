// ignore: unused_import
import 'package:intl/intl.dart' as intl;
import 'app_localizations.dart';

// ignore_for_file: type=lint

/// The translations for English (`en`).
class AppLocalizationsEn extends AppLocalizations {
  AppLocalizationsEn([String locale = 'en']) : super(locale);

  @override
  String get appTitle => 'Nexus Learning OS';

  @override
  String get language => 'Language';

  @override
  String get systemLanguage => 'System';

  @override
  String get english => 'English';

  @override
  String get simplifiedChinese => '简体中文';

  @override
  String get navKnowledgeGraph => 'Knowledge graph';

  @override
  String get navLearningPath => 'Learning path';

  @override
  String get navGraph => 'Graph';

  @override
  String get navPath => 'Path';

  @override
  String get navPractice => 'Practice';

  @override
  String get navReview => 'Review';

  @override
  String get navProgress => 'Progress';

  @override
  String get currentCourse => 'CURRENT COURSE';

  @override
  String currentCourseSummary(int count, int mastery) {
    return '$count nodes · $mastery% mastery';
  }

  @override
  String get personalLearningSpace => 'PERSONAL LEARNING SPACE';

  @override
  String get goalHeadline => 'What do you want\nto understand deeply?';

  @override
  String get goalDescription =>
      'Nexus turns a goal into an inspectable graph, runs Tutor and Evaluator roles, then asks before changing your learning path.';

  @override
  String get goalHint => 'Describe a learning goal…';

  @override
  String get generateGraph => 'Generate graph';

  @override
  String get learningLoop => 'THE R4 LEARNING LOOP';

  @override
  String get loopGoalTitle => 'Goal → Graph';

  @override
  String get loopGoalDescription => 'A durable domain model, not chat history.';

  @override
  String get loopEvidenceTitle => 'Evidence → Eval';

  @override
  String get loopEvidenceDescription =>
      'Progress comes from inspectable evidence.';

  @override
  String get loopProposalTitle => 'Proposal → HITL';

  @override
  String get loopProposalDescription => 'Runtime pauses before graph mutation.';

  @override
  String get waitingRecommendation => 'Waiting for a recommendation';

  @override
  String get waitingRecommendationDescription =>
      'This view stays empty until the Learning API returns a node, its prerequisites, and a reason.';

  @override
  String get pathEyebrow => 'LEARNING PATH · BACKEND DECISION';

  @override
  String get pathTitle => 'Your next deliberate step';

  @override
  String get courseMastery => 'COURSE MASTERY';

  @override
  String get nextNode => 'NEXT NODE';

  @override
  String get learningApi => 'Learning API';

  @override
  String progressPercent(int progress) {
    return '$progress% progress';
  }

  @override
  String prerequisitesCount(int count) {
    return '$count prerequisites';
  }

  @override
  String get whyThisNode => 'WHY THIS NODE';

  @override
  String get startRecommendedPractice => 'Start recommended practice';

  @override
  String get prerequisites => 'PREREQUISITES';

  @override
  String get prerequisitesDescription =>
      'Dependency order returned with the recommendation.';

  @override
  String get noPrerequisites => 'No prerequisites';

  @override
  String get decisionVerbatim =>
      'Flutter displays this decision verbatim; it does not rank nodes locally.';

  @override
  String get apiNode => 'API NODE';

  @override
  String get practiceEyebrow => 'PRACTICE · LEARNINGSESSION';

  @override
  String get practiceTitle => 'Turn understanding into Evidence';

  @override
  String get practiceDescription =>
      'Your answer stays bound to this node and session before the Evaluator runs.';

  @override
  String get chooseNodeBeforePractice => 'Choose a node before practice';

  @override
  String get practiceRequiresSession =>
      'A Practice answer cannot exist without a node-bound LearningSession.';

  @override
  String get openLearningPath => 'Open learning path';

  @override
  String get practiceQuestion => 'PRACTICE QUESTION';

  @override
  String sessionLabel(String id) {
    return 'Session $id';
  }

  @override
  String get yourEvidence => 'YOUR EVIDENCE';

  @override
  String get evidenceDescription =>
      'Use your own explanation. Whitespace-only answers are rejected before any API call.';

  @override
  String get evidenceHint => 'Write a concrete, testable explanation…';

  @override
  String get evidenceFlow => 'Evidence → Eval → Review';

  @override
  String characterCount(int count) {
    return '$count chars';
  }

  @override
  String get submitEvidence => 'Submit Evidence';

  @override
  String get noEvalYet => 'No Eval yet';

  @override
  String get noEvalDescription =>
      'Submit Evidence from Practice first. Review never fabricates an evaluation.';

  @override
  String get reviewTitle => 'Run evidence and decisions';

  @override
  String get reviewEyebrow => 'REVIEW · REAL RUNTIME EVENTS';

  @override
  String get submittedEvidence => 'SUBMITTED EVIDENCE';

  @override
  String get runtimeTimeline => 'RUNTIME TIMELINE';

  @override
  String eventCount(int count) {
    return '$count EVENTS';
  }

  @override
  String get noRuntimeEvents => 'No runtime events returned by the API.';

  @override
  String get noPayloadFields => 'No payload fields';

  @override
  String get progressEyebrow => 'PROGRESS · READ-ONLY COURSE DTO';

  @override
  String get progressTitle => 'Course progress at a glance';

  @override
  String get nodeProgress => 'NODE PROGRESS';

  @override
  String nodesCalculatedByApi(int count) {
    return '$count nodes · calculated by the Learning API';
  }

  @override
  String get knowledgeGraphEyebrow => 'KNOWLEDGE GRAPH · LIVE RUNTIME';

  @override
  String get legendLearning => 'Learning';

  @override
  String get legendPracticed => 'Practiced';

  @override
  String get legendLocked => 'Locked';

  @override
  String get selectGraphNode => 'Select a graph node';

  @override
  String get selectGraphNodeDescription =>
      'A LearningSession starts only after an explicit node choice.';

  @override
  String get currentNodeEyebrow => 'CURRENT NODE · LEARNING';

  @override
  String get nexusTutor => 'NEXUS TUTOR';

  @override
  String get tutorLoading => 'Tutor content is loading…';

  @override
  String get waitingLearningActivity => 'Waiting for the learning activity.';

  @override
  String get nextAction => 'NEXT ACTION';

  @override
  String get graphPracticeDescription =>
      'Practice owns the question, answer and Evidence submission. The graph only selects the node and starts its LearningSession.';

  @override
  String get openPractice => 'Open Practice';

  @override
  String get evaluatorResult => 'EVALUATOR RESULT';

  @override
  String get humanDecisionRecorded => 'HUMAN DECISION RECORDED';

  @override
  String get humanReviewRequired => 'HUMAN REVIEW REQUIRED';

  @override
  String get graphUpdateProposal => 'Graph update proposal';

  @override
  String proposalMeta(int nodes, int risks) {
    return '+$nodes nodes · $risks risks · progress preserved';
  }

  @override
  String graphUpdateApplied(String outcome) {
    return 'Graph update applied · $outcome';
  }

  @override
  String graphPreserved(String outcome) {
    return 'Graph preserved · $outcome';
  }

  @override
  String get keepGraph => 'Keep graph';

  @override
  String get applyProposal => 'Apply proposal';

  @override
  String get stateVerified => 'Verified';

  @override
  String get statePracticed => 'Practiced';

  @override
  String get stateRecommended => 'Recommended';

  @override
  String get stateLocked => 'Locked';

  @override
  String get stateUnknown => 'Unknown';

  @override
  String get statusCompleted => 'Completed';

  @override
  String get statusPaused => 'Paused';

  @override
  String get statusFailed => 'Failed';

  @override
  String noticeGraphGenerated(int count) {
    return 'Learning graph generated · $count nodes';
  }

  @override
  String noticeWorkspaceOpened(String workspace) {
    return '$workspace workspace opened';
  }

  @override
  String get noticeRecommendationLoaded => 'Backend recommendation loaded';

  @override
  String noticePracticeOpened(String title) {
    return '$title practice opened';
  }

  @override
  String noticeSessionStarted(String title) {
    return '$title session started';
  }

  @override
  String get errorSelectNodeBeforeEvidence =>
      'Select a node before submitting Evidence';

  @override
  String get errorEvidenceEmpty => 'Evidence cannot be empty';

  @override
  String get noticeEvidenceReviewRequired =>
      'Evidence evaluated · human review required';

  @override
  String get noticeEvidenceReviewReady => 'Evidence evaluated · review ready';

  @override
  String noticeProposalApplied(int count) {
    return 'Proposal applied · graph now has $count nodes';
  }

  @override
  String get noticeProposalRejected =>
      'Proposal rejected · current graph preserved';

  @override
  String get errorDeepSeekNotConfigured =>
      'DeepSeek is not configured. Add DEEPSEEK_API_KEY to the repository .env and restart the backend.';

  @override
  String get errorIntelligenceFailed =>
      'DeepSeek could not complete this request. Please retry.';

  @override
  String get errorInvalidIntelligenceOutput =>
      'The generated learning content failed validation. Please retry.';

  @override
  String errorGenericApi(String message) {
    return 'Learning API error: $message';
  }
}
