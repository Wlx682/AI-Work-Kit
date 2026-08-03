import 'dart:async';

import 'package:flutter/foundation.dart';
import 'package:flutter/widgets.dart';
import 'package:flutter_localizations/flutter_localizations.dart';
import 'package:intl/intl.dart' as intl;

import 'app_localizations_en.dart';
import 'app_localizations_zh.dart';

// ignore_for_file: type=lint

/// Callers can lookup localized strings with an instance of AppLocalizations
/// returned by `AppLocalizations.of(context)`.
///
/// Applications need to include `AppLocalizations.delegate()` in their app's
/// `localizationDelegates` list, and the locales they support in the app's
/// `supportedLocales` list. For example:
///
/// ```dart
/// import 'l10n/app_localizations.dart';
///
/// return MaterialApp(
///   localizationsDelegates: AppLocalizations.localizationsDelegates,
///   supportedLocales: AppLocalizations.supportedLocales,
///   home: MyApplicationHome(),
/// );
/// ```
///
/// ## Update pubspec.yaml
///
/// Please make sure to update your pubspec.yaml to include the following
/// packages:
///
/// ```yaml
/// dependencies:
///   # Internationalization support.
///   flutter_localizations:
///     sdk: flutter
///   intl: any # Use the pinned version from flutter_localizations
///
///   # Rest of dependencies
/// ```
///
/// ## iOS Applications
///
/// iOS applications define key application metadata, including supported
/// locales, in an Info.plist file that is built into the application bundle.
/// To configure the locales supported by your app, you’ll need to edit this
/// file.
///
/// First, open your project’s ios/Runner.xcworkspace Xcode workspace file.
/// Then, in the Project Navigator, open the Info.plist file under the Runner
/// project’s Runner folder.
///
/// Next, select the Information Property List item, select Add Item from the
/// Editor menu, then select Localizations from the pop-up menu.
///
/// Select and expand the newly-created Localizations item then, for each
/// locale your application supports, add a new item and select the locale
/// you wish to add from the pop-up menu in the Value field. This list should
/// be consistent with the languages listed in the AppLocalizations.supportedLocales
/// property.
abstract class AppLocalizations {
  AppLocalizations(String locale)
    : localeName = intl.Intl.canonicalizedLocale(locale.toString());

  final String localeName;

  static AppLocalizations? of(BuildContext context) {
    return Localizations.of<AppLocalizations>(context, AppLocalizations);
  }

  static const LocalizationsDelegate<AppLocalizations> delegate =
      _AppLocalizationsDelegate();

  /// A list of this localizations delegate along with the default localizations
  /// delegates.
  ///
  /// Returns a list of localizations delegates containing this delegate along with
  /// GlobalMaterialLocalizations.delegate, GlobalCupertinoLocalizations.delegate,
  /// and GlobalWidgetsLocalizations.delegate.
  ///
  /// Additional delegates can be added by appending to this list in
  /// MaterialApp. This list does not have to be used at all if a custom list
  /// of delegates is preferred or required.
  static const List<LocalizationsDelegate<dynamic>> localizationsDelegates =
      <LocalizationsDelegate<dynamic>>[
        delegate,
        GlobalMaterialLocalizations.delegate,
        GlobalCupertinoLocalizations.delegate,
        GlobalWidgetsLocalizations.delegate,
      ];

  /// A list of this localizations delegate's supported locales.
  static const List<Locale> supportedLocales = <Locale>[
    Locale('en'),
    Locale('zh'),
  ];

  /// No description provided for @appTitle.
  ///
  /// In en, this message translates to:
  /// **'Nexus Learning OS'**
  String get appTitle;

  /// No description provided for @language.
  ///
  /// In en, this message translates to:
  /// **'Language'**
  String get language;

  /// No description provided for @systemLanguage.
  ///
  /// In en, this message translates to:
  /// **'System'**
  String get systemLanguage;

  /// No description provided for @english.
  ///
  /// In en, this message translates to:
  /// **'English'**
  String get english;

  /// No description provided for @simplifiedChinese.
  ///
  /// In en, this message translates to:
  /// **'简体中文'**
  String get simplifiedChinese;

  /// No description provided for @navKnowledgeGraph.
  ///
  /// In en, this message translates to:
  /// **'Knowledge graph'**
  String get navKnowledgeGraph;

  /// No description provided for @navLearningPath.
  ///
  /// In en, this message translates to:
  /// **'Learning path'**
  String get navLearningPath;

  /// No description provided for @navGraph.
  ///
  /// In en, this message translates to:
  /// **'Graph'**
  String get navGraph;

  /// No description provided for @navPath.
  ///
  /// In en, this message translates to:
  /// **'Path'**
  String get navPath;

  /// No description provided for @navPractice.
  ///
  /// In en, this message translates to:
  /// **'Practice'**
  String get navPractice;

  /// No description provided for @navReview.
  ///
  /// In en, this message translates to:
  /// **'Review'**
  String get navReview;

  /// No description provided for @navProgress.
  ///
  /// In en, this message translates to:
  /// **'Progress'**
  String get navProgress;

  /// No description provided for @currentCourse.
  ///
  /// In en, this message translates to:
  /// **'CURRENT COURSE'**
  String get currentCourse;

  /// No description provided for @currentCourseSummary.
  ///
  /// In en, this message translates to:
  /// **'{count} nodes · {mastery}% mastery'**
  String currentCourseSummary(int count, int mastery);

  /// No description provided for @personalLearningSpace.
  ///
  /// In en, this message translates to:
  /// **'PERSONAL LEARNING SPACE'**
  String get personalLearningSpace;

  /// No description provided for @goalHeadline.
  ///
  /// In en, this message translates to:
  /// **'What do you want\nto understand deeply?'**
  String get goalHeadline;

  /// No description provided for @goalDescription.
  ///
  /// In en, this message translates to:
  /// **'Nexus turns a goal into an inspectable graph, runs Tutor and Evaluator roles, then asks before changing your learning path.'**
  String get goalDescription;

  /// No description provided for @goalHint.
  ///
  /// In en, this message translates to:
  /// **'Describe a learning goal…'**
  String get goalHint;

  /// No description provided for @generateGraph.
  ///
  /// In en, this message translates to:
  /// **'Generate graph'**
  String get generateGraph;

  /// No description provided for @learningLoop.
  ///
  /// In en, this message translates to:
  /// **'THE R4 LEARNING LOOP'**
  String get learningLoop;

  /// No description provided for @loopGoalTitle.
  ///
  /// In en, this message translates to:
  /// **'Goal → Graph'**
  String get loopGoalTitle;

  /// No description provided for @loopGoalDescription.
  ///
  /// In en, this message translates to:
  /// **'A durable domain model, not chat history.'**
  String get loopGoalDescription;

  /// No description provided for @loopEvidenceTitle.
  ///
  /// In en, this message translates to:
  /// **'Evidence → Eval'**
  String get loopEvidenceTitle;

  /// No description provided for @loopEvidenceDescription.
  ///
  /// In en, this message translates to:
  /// **'Progress comes from inspectable evidence.'**
  String get loopEvidenceDescription;

  /// No description provided for @loopProposalTitle.
  ///
  /// In en, this message translates to:
  /// **'Proposal → HITL'**
  String get loopProposalTitle;

  /// No description provided for @loopProposalDescription.
  ///
  /// In en, this message translates to:
  /// **'Runtime pauses before graph mutation.'**
  String get loopProposalDescription;

  /// No description provided for @waitingRecommendation.
  ///
  /// In en, this message translates to:
  /// **'Waiting for a recommendation'**
  String get waitingRecommendation;

  /// No description provided for @waitingRecommendationDescription.
  ///
  /// In en, this message translates to:
  /// **'This view stays empty until the Learning API returns a node, its prerequisites, and a reason.'**
  String get waitingRecommendationDescription;

  /// No description provided for @pathEyebrow.
  ///
  /// In en, this message translates to:
  /// **'LEARNING PATH · BACKEND DECISION'**
  String get pathEyebrow;

  /// No description provided for @pathTitle.
  ///
  /// In en, this message translates to:
  /// **'Your next deliberate step'**
  String get pathTitle;

  /// No description provided for @courseMastery.
  ///
  /// In en, this message translates to:
  /// **'COURSE MASTERY'**
  String get courseMastery;

  /// No description provided for @nextNode.
  ///
  /// In en, this message translates to:
  /// **'NEXT NODE'**
  String get nextNode;

  /// No description provided for @learningApi.
  ///
  /// In en, this message translates to:
  /// **'Learning API'**
  String get learningApi;

  /// No description provided for @progressPercent.
  ///
  /// In en, this message translates to:
  /// **'{progress}% progress'**
  String progressPercent(int progress);

  /// No description provided for @prerequisitesCount.
  ///
  /// In en, this message translates to:
  /// **'{count} prerequisites'**
  String prerequisitesCount(int count);

  /// No description provided for @whyThisNode.
  ///
  /// In en, this message translates to:
  /// **'WHY THIS NODE'**
  String get whyThisNode;

  /// No description provided for @startRecommendedPractice.
  ///
  /// In en, this message translates to:
  /// **'Start recommended practice'**
  String get startRecommendedPractice;

  /// No description provided for @prerequisites.
  ///
  /// In en, this message translates to:
  /// **'PREREQUISITES'**
  String get prerequisites;

  /// No description provided for @prerequisitesDescription.
  ///
  /// In en, this message translates to:
  /// **'Dependency order returned with the recommendation.'**
  String get prerequisitesDescription;

  /// No description provided for @noPrerequisites.
  ///
  /// In en, this message translates to:
  /// **'No prerequisites'**
  String get noPrerequisites;

  /// No description provided for @decisionVerbatim.
  ///
  /// In en, this message translates to:
  /// **'Flutter displays this decision verbatim; it does not rank nodes locally.'**
  String get decisionVerbatim;

  /// No description provided for @apiNode.
  ///
  /// In en, this message translates to:
  /// **'API NODE'**
  String get apiNode;

  /// No description provided for @practiceEyebrow.
  ///
  /// In en, this message translates to:
  /// **'PRACTICE · LEARNINGSESSION'**
  String get practiceEyebrow;

  /// No description provided for @practiceTitle.
  ///
  /// In en, this message translates to:
  /// **'Turn understanding into Evidence'**
  String get practiceTitle;

  /// No description provided for @practiceDescription.
  ///
  /// In en, this message translates to:
  /// **'Your answer stays bound to this node and session before the Evaluator runs.'**
  String get practiceDescription;

  /// No description provided for @chooseNodeBeforePractice.
  ///
  /// In en, this message translates to:
  /// **'Choose a node before practice'**
  String get chooseNodeBeforePractice;

  /// No description provided for @practiceRequiresSession.
  ///
  /// In en, this message translates to:
  /// **'A Practice answer cannot exist without a node-bound LearningSession.'**
  String get practiceRequiresSession;

  /// No description provided for @openLearningPath.
  ///
  /// In en, this message translates to:
  /// **'Open learning path'**
  String get openLearningPath;

  /// No description provided for @practiceQuestion.
  ///
  /// In en, this message translates to:
  /// **'PRACTICE QUESTION'**
  String get practiceQuestion;

  /// No description provided for @sessionLabel.
  ///
  /// In en, this message translates to:
  /// **'Session {id}'**
  String sessionLabel(String id);

  /// No description provided for @yourEvidence.
  ///
  /// In en, this message translates to:
  /// **'YOUR EVIDENCE'**
  String get yourEvidence;

  /// No description provided for @evidenceDescription.
  ///
  /// In en, this message translates to:
  /// **'Use your own explanation. Whitespace-only answers are rejected before any API call.'**
  String get evidenceDescription;

  /// No description provided for @evidenceHint.
  ///
  /// In en, this message translates to:
  /// **'Write a concrete, testable explanation…'**
  String get evidenceHint;

  /// No description provided for @evidenceFlow.
  ///
  /// In en, this message translates to:
  /// **'Evidence → Eval → Review'**
  String get evidenceFlow;

  /// No description provided for @characterCount.
  ///
  /// In en, this message translates to:
  /// **'{count} chars'**
  String characterCount(int count);

  /// No description provided for @submitEvidence.
  ///
  /// In en, this message translates to:
  /// **'Submit Evidence'**
  String get submitEvidence;

  /// No description provided for @noEvalYet.
  ///
  /// In en, this message translates to:
  /// **'No Eval yet'**
  String get noEvalYet;

  /// No description provided for @noEvalDescription.
  ///
  /// In en, this message translates to:
  /// **'Submit Evidence from Practice first. Review never fabricates an evaluation.'**
  String get noEvalDescription;

  /// No description provided for @reviewTitle.
  ///
  /// In en, this message translates to:
  /// **'Run evidence and decisions'**
  String get reviewTitle;

  /// No description provided for @reviewEyebrow.
  ///
  /// In en, this message translates to:
  /// **'REVIEW · REAL RUNTIME EVENTS'**
  String get reviewEyebrow;

  /// No description provided for @submittedEvidence.
  ///
  /// In en, this message translates to:
  /// **'SUBMITTED EVIDENCE'**
  String get submittedEvidence;

  /// No description provided for @runtimeTimeline.
  ///
  /// In en, this message translates to:
  /// **'RUNTIME TIMELINE'**
  String get runtimeTimeline;

  /// No description provided for @eventCount.
  ///
  /// In en, this message translates to:
  /// **'{count} EVENTS'**
  String eventCount(int count);

  /// No description provided for @noRuntimeEvents.
  ///
  /// In en, this message translates to:
  /// **'No runtime events returned by the API.'**
  String get noRuntimeEvents;

  /// No description provided for @noPayloadFields.
  ///
  /// In en, this message translates to:
  /// **'No payload fields'**
  String get noPayloadFields;

  /// No description provided for @progressEyebrow.
  ///
  /// In en, this message translates to:
  /// **'PROGRESS · READ-ONLY COURSE DTO'**
  String get progressEyebrow;

  /// No description provided for @progressTitle.
  ///
  /// In en, this message translates to:
  /// **'Course progress at a glance'**
  String get progressTitle;

  /// No description provided for @nodeProgress.
  ///
  /// In en, this message translates to:
  /// **'NODE PROGRESS'**
  String get nodeProgress;

  /// No description provided for @nodesCalculatedByApi.
  ///
  /// In en, this message translates to:
  /// **'{count} nodes · calculated by the Learning API'**
  String nodesCalculatedByApi(int count);

  /// No description provided for @knowledgeGraphEyebrow.
  ///
  /// In en, this message translates to:
  /// **'KNOWLEDGE GRAPH · LIVE RUNTIME'**
  String get knowledgeGraphEyebrow;

  /// No description provided for @legendLearning.
  ///
  /// In en, this message translates to:
  /// **'Learning'**
  String get legendLearning;

  /// No description provided for @legendPracticed.
  ///
  /// In en, this message translates to:
  /// **'Practiced'**
  String get legendPracticed;

  /// No description provided for @legendLocked.
  ///
  /// In en, this message translates to:
  /// **'Locked'**
  String get legendLocked;

  /// No description provided for @selectGraphNode.
  ///
  /// In en, this message translates to:
  /// **'Select a graph node'**
  String get selectGraphNode;

  /// No description provided for @selectGraphNodeDescription.
  ///
  /// In en, this message translates to:
  /// **'A LearningSession starts only after an explicit node choice.'**
  String get selectGraphNodeDescription;

  /// No description provided for @currentNodeEyebrow.
  ///
  /// In en, this message translates to:
  /// **'CURRENT NODE · LEARNING'**
  String get currentNodeEyebrow;

  /// No description provided for @nexusTutor.
  ///
  /// In en, this message translates to:
  /// **'NEXUS TUTOR'**
  String get nexusTutor;

  /// No description provided for @tutorLoading.
  ///
  /// In en, this message translates to:
  /// **'Tutor content is loading…'**
  String get tutorLoading;

  /// No description provided for @waitingLearningActivity.
  ///
  /// In en, this message translates to:
  /// **'Waiting for the learning activity.'**
  String get waitingLearningActivity;

  /// No description provided for @nextAction.
  ///
  /// In en, this message translates to:
  /// **'NEXT ACTION'**
  String get nextAction;

  /// No description provided for @graphPracticeDescription.
  ///
  /// In en, this message translates to:
  /// **'Practice owns the question, answer and Evidence submission. The graph only selects the node and starts its LearningSession.'**
  String get graphPracticeDescription;

  /// No description provided for @openPractice.
  ///
  /// In en, this message translates to:
  /// **'Open Practice'**
  String get openPractice;

  /// No description provided for @evaluatorResult.
  ///
  /// In en, this message translates to:
  /// **'EVALUATOR RESULT'**
  String get evaluatorResult;

  /// No description provided for @humanDecisionRecorded.
  ///
  /// In en, this message translates to:
  /// **'HUMAN DECISION RECORDED'**
  String get humanDecisionRecorded;

  /// No description provided for @humanReviewRequired.
  ///
  /// In en, this message translates to:
  /// **'HUMAN REVIEW REQUIRED'**
  String get humanReviewRequired;

  /// No description provided for @graphUpdateProposal.
  ///
  /// In en, this message translates to:
  /// **'Graph update proposal'**
  String get graphUpdateProposal;

  /// No description provided for @proposalMeta.
  ///
  /// In en, this message translates to:
  /// **'+{nodes} nodes · {risks} risks · progress preserved'**
  String proposalMeta(int nodes, int risks);

  /// No description provided for @graphUpdateApplied.
  ///
  /// In en, this message translates to:
  /// **'Graph update applied · {outcome}'**
  String graphUpdateApplied(String outcome);

  /// No description provided for @graphPreserved.
  ///
  /// In en, this message translates to:
  /// **'Graph preserved · {outcome}'**
  String graphPreserved(String outcome);

  /// No description provided for @keepGraph.
  ///
  /// In en, this message translates to:
  /// **'Keep graph'**
  String get keepGraph;

  /// No description provided for @applyProposal.
  ///
  /// In en, this message translates to:
  /// **'Apply proposal'**
  String get applyProposal;

  /// No description provided for @stateVerified.
  ///
  /// In en, this message translates to:
  /// **'Verified'**
  String get stateVerified;

  /// No description provided for @statePracticed.
  ///
  /// In en, this message translates to:
  /// **'Practiced'**
  String get statePracticed;

  /// No description provided for @stateRecommended.
  ///
  /// In en, this message translates to:
  /// **'Recommended'**
  String get stateRecommended;

  /// No description provided for @stateLocked.
  ///
  /// In en, this message translates to:
  /// **'Locked'**
  String get stateLocked;

  /// No description provided for @stateUnknown.
  ///
  /// In en, this message translates to:
  /// **'Unknown'**
  String get stateUnknown;

  /// No description provided for @statusCompleted.
  ///
  /// In en, this message translates to:
  /// **'Completed'**
  String get statusCompleted;

  /// No description provided for @statusPaused.
  ///
  /// In en, this message translates to:
  /// **'Paused'**
  String get statusPaused;

  /// No description provided for @statusFailed.
  ///
  /// In en, this message translates to:
  /// **'Failed'**
  String get statusFailed;

  /// No description provided for @noticeGraphGenerated.
  ///
  /// In en, this message translates to:
  /// **'Learning graph generated · {count} nodes'**
  String noticeGraphGenerated(int count);

  /// No description provided for @noticeWorkspaceOpened.
  ///
  /// In en, this message translates to:
  /// **'{workspace} workspace opened'**
  String noticeWorkspaceOpened(String workspace);

  /// No description provided for @noticeRecommendationLoaded.
  ///
  /// In en, this message translates to:
  /// **'Backend recommendation loaded'**
  String get noticeRecommendationLoaded;

  /// No description provided for @noticePracticeOpened.
  ///
  /// In en, this message translates to:
  /// **'{title} practice opened'**
  String noticePracticeOpened(String title);

  /// No description provided for @noticeSessionStarted.
  ///
  /// In en, this message translates to:
  /// **'{title} session started'**
  String noticeSessionStarted(String title);

  /// No description provided for @errorSelectNodeBeforeEvidence.
  ///
  /// In en, this message translates to:
  /// **'Select a node before submitting Evidence'**
  String get errorSelectNodeBeforeEvidence;

  /// No description provided for @errorEvidenceEmpty.
  ///
  /// In en, this message translates to:
  /// **'Evidence cannot be empty'**
  String get errorEvidenceEmpty;

  /// No description provided for @noticeEvidenceReviewRequired.
  ///
  /// In en, this message translates to:
  /// **'Evidence evaluated · human review required'**
  String get noticeEvidenceReviewRequired;

  /// No description provided for @noticeEvidenceReviewReady.
  ///
  /// In en, this message translates to:
  /// **'Evidence evaluated · review ready'**
  String get noticeEvidenceReviewReady;

  /// No description provided for @noticeProposalApplied.
  ///
  /// In en, this message translates to:
  /// **'Proposal applied · graph now has {count} nodes'**
  String noticeProposalApplied(int count);

  /// No description provided for @noticeProposalRejected.
  ///
  /// In en, this message translates to:
  /// **'Proposal rejected · current graph preserved'**
  String get noticeProposalRejected;

  /// No description provided for @errorDeepSeekNotConfigured.
  ///
  /// In en, this message translates to:
  /// **'DeepSeek is not configured. Add DEEPSEEK_API_KEY to the repository .env and restart the backend.'**
  String get errorDeepSeekNotConfigured;

  /// No description provided for @errorIntelligenceFailed.
  ///
  /// In en, this message translates to:
  /// **'DeepSeek could not complete this request. Please retry.'**
  String get errorIntelligenceFailed;

  /// No description provided for @errorInvalidIntelligenceOutput.
  ///
  /// In en, this message translates to:
  /// **'The generated learning content failed validation. Please retry.'**
  String get errorInvalidIntelligenceOutput;

  /// No description provided for @errorGenericApi.
  ///
  /// In en, this message translates to:
  /// **'Learning API error: {message}'**
  String errorGenericApi(String message);
}

class _AppLocalizationsDelegate
    extends LocalizationsDelegate<AppLocalizations> {
  const _AppLocalizationsDelegate();

  @override
  Future<AppLocalizations> load(Locale locale) {
    return SynchronousFuture<AppLocalizations>(lookupAppLocalizations(locale));
  }

  @override
  bool isSupported(Locale locale) =>
      <String>['en', 'zh'].contains(locale.languageCode);

  @override
  bool shouldReload(_AppLocalizationsDelegate old) => false;
}

AppLocalizations lookupAppLocalizations(Locale locale) {
  // Lookup logic when only language code is specified.
  switch (locale.languageCode) {
    case 'en':
      return AppLocalizationsEn();
    case 'zh':
      return AppLocalizationsZh();
  }

  throw FlutterError(
    'AppLocalizations.delegate failed to load unsupported locale "$locale". This is likely '
    'an issue with the localizations generation tool. Please file an issue '
    'on GitHub with a reproducible sample app and the gen-l10n configuration '
    'that was used.',
  );
}
