class LearningNode {
  const LearningNode({
    required this.id,
    required this.slug,
    required this.title,
    required this.progress,
    required this.masteryState,
  });

  factory LearningNode.fromJson(Map<String, dynamic> json) => LearningNode(
    id: json['id'] as String,
    slug: json['slug'] as String,
    title: json['title'] as String,
    progress: json['progress'] as int,
    masteryState: json['mastery_state'] as String,
  );

  final String id;
  final String slug;
  final String title;
  final int progress;
  final String masteryState;
}

class LearningEdge {
  const LearningEdge(this.sourceNodeId, this.targetNodeId);

  factory LearningEdge.fromJson(Map<String, dynamic> json) => LearningEdge(
    json['source_node_id'] as String,
    json['target_node_id'] as String,
  );

  final String sourceNodeId;
  final String targetNodeId;
}

class LearningCourse {
  const LearningCourse({
    required this.id,
    required this.title,
    required this.mastery,
    required this.nodes,
    required this.edges,
  });

  factory LearningCourse.fromJson(Map<String, dynamic> json) => LearningCourse(
    id: json['id'] as String,
    title: json['title'] as String,
    mastery: json['mastery'] as int,
    nodes: (json['nodes'] as List<dynamic>)
        .map((value) => LearningNode.fromJson(value as Map<String, dynamic>))
        .toList(growable: false),
    edges: (json['edges'] as List<dynamic>)
        .map((value) => LearningEdge.fromJson(value as Map<String, dynamic>))
        .toList(growable: false),
  );

  final String id;
  final String title;
  final int mastery;
  final List<LearningNode> nodes;
  final List<LearningEdge> edges;
}

class LearningRecommendation {
  const LearningRecommendation({
    required this.courseId,
    required this.node,
    required this.prerequisiteNodeIds,
    required this.reason,
  });

  factory LearningRecommendation.fromJson(Map<String, dynamic> json) =>
      LearningRecommendation(
        courseId: json['course_id'] as String,
        node: LearningNode.fromJson(json['node'] as Map<String, dynamic>),
        prerequisiteNodeIds: (json['prerequisite_node_ids'] as List<dynamic>)
            .cast<String>(),
        reason: json['reason'] as String,
      );

  final String courseId;
  final LearningNode node;
  final List<String> prerequisiteNodeIds;
  final String reason;
}

class LearningSession {
  const LearningSession({required this.id, required this.nodeId});

  factory LearningSession.fromJson(Map<String, dynamic> json) =>
      LearningSession(
        id: json['id'] as String,
        nodeId: json['node_id'] as String,
      );

  final String id;
  final String nodeId;
}

class LearningActivity {
  const LearningActivity({
    required this.content,
    required this.insight,
    required this.question,
    required this.rubric,
  });

  factory LearningActivity.fromJson(Map<String, dynamic> json) =>
      LearningActivity(
        content: json['content'] as String,
        insight: json['insight'] as String,
        question: json['question'] as String,
        rubric: (json['rubric'] as List<dynamic>).cast<String>(),
      );

  final String content;
  final String insight;
  final String question;
  final List<String> rubric;
}

class LearningSessionStart {
  const LearningSessionStart(this.session, this.activity);

  final LearningSession session;
  final LearningActivity activity;
}

class RuntimeEvent {
  const RuntimeEvent({
    required this.sequence,
    required this.runId,
    required this.phase,
    required this.status,
    required this.payload,
  });

  factory RuntimeEvent.fromJson(Map<String, dynamic> json) => RuntimeEvent(
    sequence: json['sequence'] as int,
    runId: json['run_id'] as String,
    phase: json['phase'] as String,
    status: json['status'] as String,
    payload: Map<String, dynamic>.from(
      json['payload'] as Map<String, dynamic>? ?? const {},
    ),
  );

  static List<RuntimeEvent> listFromJson(Object? raw) {
    final events = (raw as List<dynamic>? ?? const [])
        .map((value) => RuntimeEvent.fromJson(value as Map<String, dynamic>))
        .toList(growable: false);
    return events
      ..sort((left, right) => left.sequence.compareTo(right.sequence));
  }

  final int sequence;
  final String runId;
  final String phase;
  final String status;
  final Map<String, dynamic> payload;
}

class RuntimeReview {
  const RuntimeReview({
    required this.runId,
    required this.threadId,
    required this.status,
    required this.score,
    required this.reason,
    required this.gaps,
    required this.tutorContent,
    required this.proposal,
    required this.events,
  });

  factory RuntimeReview.fromEvidenceJson(Map<String, dynamic> json) {
    final runtime = json['runtime'] as Map<String, dynamic>;
    final evaluation = json['evaluation'] as Map<String, dynamic>;
    final tutor = runtime['tutor'] as Map<String, dynamic>? ?? const {};
    return RuntimeReview(
      runId: runtime['run_id'] as String,
      threadId: runtime['thread_id'] as String,
      status: runtime['status'] as String,
      score: (evaluation['score'] as num).toDouble(),
      reason: evaluation['reason'] as String,
      gaps: (evaluation['gaps'] as List<dynamic>? ?? const []).cast<String>(),
      tutorContent: tutor['content'] as String? ?? '',
      proposal: runtime['proposal'] as Map<String, dynamic>?,
      events: RuntimeEvent.listFromJson(runtime['events']),
    );
  }

  RuntimeReview withAdditionalEvents(List<RuntimeEvent> additionalEvents) =>
      RuntimeReview(
        runId: runId,
        threadId: threadId,
        status: status,
        score: score,
        reason: reason,
        gaps: gaps,
        tutorContent: tutorContent,
        proposal: proposal,
        events: [...events, ...additionalEvents],
      );

  final String runId;
  final String threadId;
  final String status;
  final double score;
  final String reason;
  final List<String> gaps;
  final String tutorContent;
  final Map<String, dynamic>? proposal;
  final List<RuntimeEvent> events;
}

class GoalCreation {
  const GoalCreation(this.goalId, this.course);

  final String goalId;
  final LearningCourse course;
}

class ReviewDecisionResult {
  const ReviewDecisionResult(this.outcome, this.course, this.events);

  final String outcome;
  final LearningCourse course;
  final List<RuntimeEvent> events;
}
