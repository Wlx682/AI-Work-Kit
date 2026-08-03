import 'dart:convert';

import 'package:http/http.dart' as http;

import 'models.dart';

abstract class LearningApi {
  Future<GoalCreation> createGoal(String title);
  Future<LearningRecommendation> fetchRecommendation(String courseId);
  Future<LearningSessionStart> startSession(String courseId, String nodeId);
  Future<RuntimeReview> submitEvidence(String sessionId, String answer);
  Future<ReviewDecisionResult> reviewGraphUpdate({
    required String threadId,
    required String parentRunId,
    required String courseId,
    required bool approved,
  });
}

class LearningApiException implements Exception {
  const LearningApiException(this.message, {this.code});
  final String message;
  final String? code;

  @override
  String toString() => message;
}

class HttpLearningApi implements LearningApi {
  HttpLearningApi(this.baseUrl, {http.Client? client})
    : _client = client ?? http.Client();

  final String baseUrl;
  final http.Client _client;

  @override
  Future<GoalCreation> createGoal(String title) async {
    final json = await _post('/api/learning/goals', {'title': title});
    return GoalCreation(
      (json['goal'] as Map<String, dynamic>)['id'] as String,
      LearningCourse.fromJson(json['course'] as Map<String, dynamic>),
    );
  }

  @override
  Future<LearningRecommendation> fetchRecommendation(String courseId) async {
    final json = await _get('/api/learning/courses/$courseId/recommendation');
    return LearningRecommendation.fromJson(json);
  }

  @override
  Future<LearningSessionStart> startSession(
    String courseId,
    String nodeId,
  ) async {
    final json = await _post('/api/learning/sessions', {
      'course_id': courseId,
      'node_id': nodeId,
    });
    return LearningSessionStart(
      LearningSession.fromJson(json['session'] as Map<String, dynamic>),
      LearningActivity.fromJson(json['activity'] as Map<String, dynamic>),
    );
  }

  @override
  Future<RuntimeReview> submitEvidence(String sessionId, String answer) async {
    final json = await _post('/api/learning/evidence', {
      'session_id': sessionId,
      'answer': answer,
    });
    return RuntimeReview.fromEvidenceJson(json);
  }

  @override
  Future<ReviewDecisionResult> reviewGraphUpdate({
    required String threadId,
    required String parentRunId,
    required String courseId,
    required bool approved,
  }) async {
    final json = await _post('/api/learning/reviews', {
      'thread_id': threadId,
      'parent_run_id': parentRunId,
      'course_id': courseId,
      'approved': approved,
    });
    final runtime = json['runtime'] as Map<String, dynamic>;
    return ReviewDecisionResult(
      runtime['outcome'] as String,
      LearningCourse.fromJson(json['course'] as Map<String, dynamic>),
      RuntimeEvent.listFromJson(runtime['events']),
    );
  }

  Future<Map<String, dynamic>> _post(
    String path,
    Map<String, dynamic> payload,
  ) async {
    final response = await _client.post(
      Uri.parse('$baseUrl$path'),
      headers: const {'Content-Type': 'application/json'},
      body: jsonEncode(payload),
    );
    return _decode(response);
  }

  Future<Map<String, dynamic>> _get(String path) async {
    final response = await _client.get(Uri.parse('$baseUrl$path'));
    return _decode(response);
  }

  Map<String, dynamic> _decode(http.Response response) {
    final decoded = jsonDecode(response.body) as Map<String, dynamic>;
    if (response.statusCode < 200 || response.statusCode >= 300) {
      final error = decoded['error'] as Map<String, dynamic>?;
      throw LearningApiException(
        error?['message'] as String? ?? 'Learning API ${response.statusCode}',
        code: error?['code'] as String?,
      );
    }
    return decoded;
  }
}
