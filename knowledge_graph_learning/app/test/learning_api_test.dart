import 'dart:convert';

import 'package:flutter_test/flutter_test.dart';
import 'package:http/http.dart' as http;
import 'package:http/testing.dart';
import 'package:nexus_learning/src/learning_api.dart';

void main() {
  test(
    'HTTP API parses the backend recommendation without local ranking',
    () async {
      final client = MockClient((request) async {
        expect(request.method, 'GET');
        expect(
          request.url.path,
          '/api/learning/courses/course-1/recommendation',
        );
        return http.Response(
          jsonEncode({
            'course_id': 'course-1',
            'node': {
              'id': 'course-1--checkpoint-interrupt',
              'slug': 'checkpoint-interrupt',
              'title': 'Checkpoint & Interrupt',
              'progress': 24,
              'mastery_state': 'recommended',
            },
            'prerequisite_node_ids': [
              'course-1--trace-events',
              'course-1--runtime-state',
            ],
            'reason': 'Backend-selected reason',
          }),
          200,
          headers: const {'content-type': 'application/json'},
        );
      });
      final api = HttpLearningApi('http://127.0.0.1:8765', client: client);

      final recommendation = await api.fetchRecommendation('course-1');

      expect(recommendation.node.slug, 'checkpoint-interrupt');
      expect(recommendation.prerequisiteNodeIds, hasLength(2));
      expect(recommendation.reason, 'Backend-selected reason');
    },
  );

  test(
    'HTTP session response exposes the DeepSeek learning activity',
    () async {
      final client = MockClient(
        (request) async => http.Response(
          jsonEncode({
            'session': {'id': 'session-1', 'node_id': 'node-1'},
            'activity': {
              'content': 'Generated tutor content',
              'insight': 'Generated insight',
              'question': 'Generated question?',
              'rubric': ['criterion one', 'criterion two'],
            },
          }),
          200,
        ),
      );
      final api = HttpLearningApi('http://127.0.0.1:8765', client: client);

      final started = await api.startSession('course-1', 'node-1');

      expect(started.session.nodeId, 'node-1');
      expect(started.activity.question, 'Generated question?');
      expect(started.activity.rubric, hasLength(2));
    },
  );

  test('HTTP review response keeps real resumed events in sequence', () async {
    final client = MockClient((request) async {
      expect(request.method, 'POST');
      expect(request.url.path, '/api/learning/reviews');
      return http.Response(
        jsonEncode({
          'runtime': {
            'outcome': 'completed',
            'events': [
              {
                'sequence': 2,
                'run_id': 'resume-run',
                'phase': 'apply_graph_update',
                'status': 'completed',
                'payload': {'applied': true},
              },
              {
                'sequence': 1,
                'run_id': 'resume-run',
                'phase': 'run',
                'status': 'resumed',
                'payload': {'parent_run_id': 'run-1'},
              },
            ],
          },
          'course': {
            'id': 'course-1',
            'title': 'Production Agents',
            'mastery': 60,
            'nodes': <Object>[],
            'edges': <Object>[],
          },
        }),
        200,
        headers: const {'content-type': 'application/json'},
      );
    });
    final api = HttpLearningApi('http://127.0.0.1:8765', client: client);

    final result = await api.reviewGraphUpdate(
      threadId: 'thread-1',
      parentRunId: 'run-1',
      courseId: 'course-1',
      approved: true,
    );

    expect(result.outcome, 'completed');
    expect(result.events.map((event) => event.phase), [
      'run',
      'apply_graph_update',
    ]);
    expect(result.events.last.payload['applied'], isTrue);
  });

  test(
    'HTTP Evidence response exposes the original runtime timeline',
    () async {
      final client = MockClient((request) async {
        expect(request.url.path, '/api/learning/evidence');
        return http.Response(
          jsonEncode({
            'evaluation': {
              'score': .86,
              'reason': 'State and Trace have distinct responsibilities.',
              'gaps': ['One remaining boundary.'],
            },
            'runtime': {
              'run_id': 'run-1',
              'thread_id': 'thread-1',
              'status': 'paused',
              'tutor': {'content': 'Tutor output'},
              'proposal': <String, Object>{},
              'events': [
                {
                  'sequence': 2,
                  'run_id': 'run-1',
                  'phase': 'evaluator',
                  'status': 'completed',
                  'payload': {'evaluation': true},
                },
                {
                  'sequence': 1,
                  'run_id': 'run-1',
                  'phase': 'tutor',
                  'status': 'completed',
                  'payload': {'tutor_content': true},
                },
              ],
            },
          }),
          200,
        );
      });
      final api = HttpLearningApi('http://127.0.0.1:8765', client: client);

      final review = await api.submitEvidence('session-1', 'answer');

      expect(review.events.map((event) => event.phase), ['tutor', 'evaluator']);
      expect(review.events.last.payload['evaluation'], isTrue);
      expect(review.gaps, ['One remaining boundary.']);
    },
  );
}
