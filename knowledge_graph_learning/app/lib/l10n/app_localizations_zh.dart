// ignore: unused_import
import 'package:intl/intl.dart' as intl;
import 'app_localizations.dart';

// ignore_for_file: type=lint

/// The translations for Chinese (`zh`).
class AppLocalizationsZh extends AppLocalizations {
  AppLocalizationsZh([String locale = 'zh']) : super(locale);

  @override
  String get appTitle => 'Nexus 学习系统';

  @override
  String get language => '语言';

  @override
  String get systemLanguage => '跟随系统';

  @override
  String get english => 'English';

  @override
  String get simplifiedChinese => '简体中文';

  @override
  String get navKnowledgeGraph => '知识图谱';

  @override
  String get navLearningPath => '学习路径';

  @override
  String get navGraph => '图谱';

  @override
  String get navPath => '路径';

  @override
  String get navPractice => '练习';

  @override
  String get navReview => '复盘';

  @override
  String get navProgress => '进度';

  @override
  String get currentCourse => '当前课程';

  @override
  String currentCourseSummary(int count, int mastery) {
    return '$count 个节点 · 掌握度 $mastery%';
  }

  @override
  String get personalLearningSpace => '个人学习空间';

  @override
  String get goalHeadline => '你想深入理解\n什么内容？';

  @override
  String get goalDescription =>
      'Nexus 会把目标转化为可检查的知识图谱，由 Tutor 和 Evaluator 协作，并在修改学习路径前征求你的确认。';

  @override
  String get goalHint => '描述一个学习目标…';

  @override
  String get generateGraph => '生成图谱';

  @override
  String get learningLoop => 'R4 学习闭环';

  @override
  String get loopGoalTitle => '目标 → 图谱';

  @override
  String get loopGoalDescription => '形成持久领域模型，而不是聊天记录。';

  @override
  String get loopEvidenceTitle => '证据 → 评估';

  @override
  String get loopEvidenceDescription => '学习进度来自可检查的学习证据。';

  @override
  String get loopProposalTitle => '提案 → 人工确认';

  @override
  String get loopProposalDescription => '修改图谱前，Runtime 会暂停等待确认。';

  @override
  String get waitingRecommendation => '正在等待学习推荐';

  @override
  String get waitingRecommendationDescription =>
      'Learning API 返回节点、前置依赖和推荐原因后，此页面才会展示内容。';

  @override
  String get pathEyebrow => '学习路径 · 后端决策';

  @override
  String get pathTitle => '下一步刻意练习';

  @override
  String get courseMastery => '课程掌握度';

  @override
  String get nextNode => '下一节点';

  @override
  String get learningApi => 'Learning API';

  @override
  String progressPercent(int progress) {
    return '进度 $progress%';
  }

  @override
  String prerequisitesCount(int count) {
    return '$count 个前置节点';
  }

  @override
  String get whyThisNode => '推荐原因';

  @override
  String get startRecommendedPractice => '开始推荐练习';

  @override
  String get prerequisites => '前置依赖';

  @override
  String get prerequisitesDescription => '以下依赖顺序来自后端推荐。';

  @override
  String get noPrerequisites => '没有前置依赖';

  @override
  String get decisionVerbatim => 'Flutter 原样展示后端决策，不在本地重新排序节点。';

  @override
  String get apiNode => 'API 节点';

  @override
  String get practiceEyebrow => '练习 · LEARNINGSESSION';

  @override
  String get practiceTitle => '把理解转化为学习证据';

  @override
  String get practiceDescription => 'Evaluator 运行前，你的回答会与当前节点和学习会话绑定。';

  @override
  String get chooseNodeBeforePractice => '请先选择学习节点';

  @override
  String get practiceRequiresSession => '没有绑定节点的 LearningSession，就不能提交练习答案。';

  @override
  String get openLearningPath => '打开学习路径';

  @override
  String get practiceQuestion => '练习问题';

  @override
  String sessionLabel(String id) {
    return '会话 $id';
  }

  @override
  String get yourEvidence => '你的学习证据';

  @override
  String get evidenceDescription => '请用自己的话说明。只有空白的回答会在调用 API 前被拒绝。';

  @override
  String get evidenceHint => '写下具体、可验证的解释…';

  @override
  String get evidenceFlow => '学习证据 → 评估 → 复盘';

  @override
  String characterCount(int count) {
    return '$count 字符';
  }

  @override
  String get submitEvidence => '提交学习证据';

  @override
  String get noEvalYet => '暂无评估';

  @override
  String get noEvalDescription => '请先在练习页提交学习证据；复盘页不会伪造评估结果。';

  @override
  String get reviewTitle => '运行证据与决策';

  @override
  String get reviewEyebrow => '复盘 · 真实 RUNTIME 事件';

  @override
  String get submittedEvidence => '已提交的学习证据';

  @override
  String get runtimeTimeline => 'RUNTIME 时间线';

  @override
  String eventCount(int count) {
    return '$count 个事件';
  }

  @override
  String get noRuntimeEvents => 'API 没有返回 Runtime 事件。';

  @override
  String get noPayloadFields => '没有载荷字段';

  @override
  String get progressEyebrow => '进度 · 只读课程数据';

  @override
  String get progressTitle => '课程进度概览';

  @override
  String get nodeProgress => '节点进度';

  @override
  String nodesCalculatedByApi(int count) {
    return '$count 个节点 · 由 Learning API 计算';
  }

  @override
  String get knowledgeGraphEyebrow => '知识图谱 · 实时 RUNTIME';

  @override
  String get legendLearning => '学习中';

  @override
  String get legendPracticed => '已练习';

  @override
  String get legendLocked => '未解锁';

  @override
  String get selectGraphNode => '选择一个图谱节点';

  @override
  String get selectGraphNodeDescription => '只有明确选择节点后，系统才会创建 LearningSession。';

  @override
  String get currentNodeEyebrow => '当前节点 · 学习中';

  @override
  String get nexusTutor => 'NEXUS TUTOR';

  @override
  String get tutorLoading => 'Tutor 内容加载中…';

  @override
  String get waitingLearningActivity => '正在等待学习活动。';

  @override
  String get nextAction => '下一步';

  @override
  String get graphPracticeDescription =>
      '问题、回答和学习证据都属于练习页；图谱只负责选择节点并启动 LearningSession。';

  @override
  String get openPractice => '打开练习';

  @override
  String get evaluatorResult => '评估结果';

  @override
  String get humanDecisionRecorded => '人工决策已记录';

  @override
  String get humanReviewRequired => '需要人工确认';

  @override
  String get graphUpdateProposal => '图谱更新提案';

  @override
  String proposalMeta(int nodes, int risks) {
    return '+$nodes 个节点 · $risks 项风险 · 保留进度';
  }

  @override
  String graphUpdateApplied(String outcome) {
    return '图谱更新已应用 · $outcome';
  }

  @override
  String graphPreserved(String outcome) {
    return '已保留原图谱 · $outcome';
  }

  @override
  String get keepGraph => '保留图谱';

  @override
  String get applyProposal => '应用提案';

  @override
  String get stateVerified => '已掌握';

  @override
  String get statePracticed => '已练习';

  @override
  String get stateRecommended => '已推荐';

  @override
  String get stateLocked => '未解锁';

  @override
  String get stateUnknown => '未知';

  @override
  String get statusCompleted => '已完成';

  @override
  String get statusPaused => '已暂停';

  @override
  String get statusFailed => '失败';

  @override
  String noticeGraphGenerated(int count) {
    return '学习图谱已生成 · $count 个节点';
  }

  @override
  String noticeWorkspaceOpened(String workspace) {
    return '已打开$workspace';
  }

  @override
  String get noticeRecommendationLoaded => '后端推荐已加载';

  @override
  String noticePracticeOpened(String title) {
    return '已打开“$title”练习';
  }

  @override
  String noticeSessionStarted(String title) {
    return '“$title”学习会话已启动';
  }

  @override
  String get errorSelectNodeBeforeEvidence => '提交学习证据前请先选择节点';

  @override
  String get errorEvidenceEmpty => '学习证据不能为空';

  @override
  String get noticeEvidenceReviewRequired => '学习证据已评估 · 等待人工确认';

  @override
  String get noticeEvidenceReviewReady => '学习证据已评估 · 可以复盘';

  @override
  String noticeProposalApplied(int count) {
    return '提案已应用 · 图谱现有 $count 个节点';
  }

  @override
  String get noticeProposalRejected => '提案已拒绝 · 已保留当前图谱';

  @override
  String get errorDeepSeekNotConfigured =>
      'DeepSeek 尚未配置。请在仓库根目录 .env 中添加 DEEPSEEK_API_KEY 并重启后端。';

  @override
  String get errorIntelligenceFailed => 'DeepSeek 暂时无法完成请求，请重试。';

  @override
  String get errorInvalidIntelligenceOutput => '生成的学习内容未通过校验，请重试。';

  @override
  String errorGenericApi(String message) {
    return 'Learning API 错误：$message';
  }
}
