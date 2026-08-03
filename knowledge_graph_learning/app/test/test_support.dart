import 'package:nexus_learning/src/learning_api.dart';
import 'package:nexus_learning/src/models.dart';

LearningCourse sampleCourse({bool expanded = false}) {
  final nodes = [
    const LearningNode(
      id: 'course--agent-foundations',
      slug: 'agent-foundations',
      title: 'Agent Foundations',
      progress: 100,
      masteryState: 'verified',
    ),
    const LearningNode(
      id: 'course--runtime-basics',
      slug: 'runtime-basics',
      title: 'Runtime Basics',
      progress: 100,
      masteryState: 'verified',
    ),
    const LearningNode(
      id: 'course--tool-boundaries',
      slug: 'tool-boundaries',
      title: 'Tool Boundaries',
      progress: 100,
      masteryState: 'verified',
    ),
    const LearningNode(
      id: 'course--trace-events',
      slug: 'trace-events',
      title: 'Trace Events',
      progress: 84,
      masteryState: 'practiced',
    ),
    const LearningNode(
      id: 'course--runtime-state',
      slug: 'runtime-state',
      title: 'Runtime State',
      progress: 68,
      masteryState: 'learning',
    ),
    const LearningNode(
      id: 'course--eval-harness',
      slug: 'eval-harness',
      title: 'Eval Harness',
      progress: 32,
      masteryState: 'available',
    ),
    const LearningNode(
      id: 'course--checkpoint-interrupt',
      slug: 'checkpoint-interrupt',
      title: 'Checkpoint & Interrupt',
      progress: 24,
      masteryState: 'recommended',
    ),
    const LearningNode(
      id: 'course--replay-recovery',
      slug: 'replay-recovery',
      title: 'Replay & Recovery',
      progress: 0,
      masteryState: 'locked',
    ),
    const LearningNode(
      id: 'course--production-signals',
      slug: 'production-signals',
      title: 'Production Signals',
      progress: 0,
      masteryState: 'locked',
    ),
    const LearningNode(
      id: 'course--production-agent',
      slug: 'production-agent',
      title: 'Production Agent',
      progress: 0,
      masteryState: 'locked',
    ),
    if (expanded) ...const [
      LearningNode(
        id: 'course--checkpoint-anatomy',
        slug: 'checkpoint-anatomy',
        title: 'Checkpoint Anatomy',
        progress: 0,
        masteryState: 'unknown',
      ),
      LearningNode(
        id: 'course--interrupt-contract',
        slug: 'interrupt-contract',
        title: 'Interrupt Contract',
        progress: 0,
        masteryState: 'unknown',
      ),
      LearningNode(
        id: 'course--resume-semantics',
        slug: 'resume-semantics',
        title: 'Resume Semantics',
        progress: 0,
        masteryState: 'unknown',
      ),
    ],
  ];
  return LearningCourse(
    id: 'course',
    title: 'Production-grade AI Agents',
    mastery: expanded ? 38 : 51,
    nodes: nodes,
    edges: const [
      LearningEdge('course--agent-foundations', 'course--runtime-basics'),
      LearningEdge('course--agent-foundations', 'course--tool-boundaries'),
      LearningEdge('course--runtime-basics', 'course--trace-events'),
      LearningEdge('course--runtime-basics', 'course--runtime-state'),
      LearningEdge('course--tool-boundaries', 'course--eval-harness'),
      LearningEdge('course--runtime-state', 'course--checkpoint-interrupt'),
      LearningEdge('course--runtime-state', 'course--replay-recovery'),
      LearningEdge('course--eval-harness', 'course--production-signals'),
      LearningEdge('course--checkpoint-interrupt', 'course--production-agent'),
    ],
  );
}

class FakeLearningApi implements LearningApi {
  int recommendationCalls = 0;
  int evidenceCalls = 0;
  int reviewCalls = 0;
  String? lastEvidenceAnswer;
  bool? lastDecision;

  @override
  Future<GoalCreation> createGoal(String title) async =>
      GoalCreation('goal', sampleCourse());

  @override
  Future<LearningRecommendation> fetchRecommendation(String courseId) async {
    recommendationCalls += 1;
    final course = sampleCourse();
    return LearningRecommendation(
      courseId: courseId,
      node: course.nodes.firstWhere(
        (node) => node.slug == 'checkpoint-interrupt',
      ),
      prerequisiteNodeIds: const ['course--runtime-state'],
      reason:
          'Course graph marks this as the next target; prerequisites stay visible.',
    );
  }

  @override
  Future<LearningSessionStart> startSession(
    String courseId,
    String nodeId,
  ) async => LearningSessionStart(
    LearningSession(id: 'session', nodeId: nodeId),
    const LearningActivity(
      content: 'API Tutor content for the selected node.',
      insight: 'API Tutor insight.',
      question: 'API-generated practice question?',
      rubric: ['Explain the boundary', 'Give one example'],
    ),
  );

  @override
  Future<RuntimeReview> submitEvidence(String sessionId, String answer) async {
    evidenceCalls += 1;
    lastEvidenceAnswer = answer;
    return const RuntimeReview(
      runId: 'run',
      threadId: 'thread',
      status: 'paused',
      score: .86,
      reason: 'Evidence distinguishes State from Trace.',
      gaps: ['Clarify one failure boundary.'],
      tutorContent: 'Runtime State is durable current truth.',
      proposal: {
        'operation_type': 'expand_node',
        'summary': 'Expand Runtime State into three recovery concepts',
        'rationale': 'Evidence is ready for deeper practice.',
        'proposed_nodes': ['one', 'two', 'three'],
        'risks': ['changes next path'],
      },
      events: [
        RuntimeEvent(
          sequence: 1,
          runId: 'run',
          phase: 'run',
          status: 'started',
          payload: {},
        ),
        RuntimeEvent(
          sequence: 2,
          runId: 'run',
          phase: 'graph_curator',
          status: 'completed',
          payload: {},
        ),
        RuntimeEvent(
          sequence: 3,
          runId: 'run',
          phase: 'learning_planner',
          status: 'completed',
          payload: {},
        ),
        RuntimeEvent(
          sequence: 4,
          runId: 'run',
          phase: 'tutor',
          status: 'completed',
          payload: {},
        ),
        RuntimeEvent(
          sequence: 5,
          runId: 'run',
          phase: 'evaluator',
          status: 'completed',
          payload: {},
        ),
        RuntimeEvent(
          sequence: 6,
          runId: 'run',
          phase: 'human_review',
          status: 'paused',
          payload: {},
        ),
      ],
    );
  }

  @override
  Future<ReviewDecisionResult> reviewGraphUpdate({
    required String threadId,
    required String parentRunId,
    required String courseId,
    required bool approved,
  }) async {
    reviewCalls += 1;
    lastDecision = approved;
    return ReviewDecisionResult(
      approved ? 'completed' : 'completed_without_graph_update',
      sampleCourse(expanded: approved),
      [
        const RuntimeEvent(
          sequence: 1,
          runId: 'resume-run',
          phase: 'run',
          status: 'resumed',
          payload: {},
        ),
        RuntimeEvent(
          sequence: 2,
          runId: 'resume-run',
          phase: approved ? 'apply_graph_update' : 'complete',
          status: 'completed',
          payload: const {},
        ),
        const RuntimeEvent(
          sequence: 3,
          runId: 'resume-run',
          phase: 'run',
          status: 'completed',
          payload: {},
        ),
      ],
    );
  }
}
