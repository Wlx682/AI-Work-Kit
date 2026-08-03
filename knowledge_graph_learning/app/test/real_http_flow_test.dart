import 'dart:convert';
import 'dart:io';

import 'package:flutter_test/flutter_test.dart';
import 'package:http/http.dart' as http;
import 'package:nexus_learning/src/learning_api.dart';
import 'package:nexus_learning/src/learning_controller.dart';

void main() {
  final enabled =
      Platform.environment['R4_LIVE_DEEPSEEK'] == '1' &&
      (Platform.environment['DEEPSEEK_API_KEY']?.isNotEmpty ?? false);

  test(
    'real HTTP client completes the five-view learning state flow',
    () async {
      final python = Platform.environment['R4_PYTHON'];
      if (python == null || python.isEmpty) {
        fail('R4_PYTHON must point to a Python 3.10+ project runtime');
      }
      final flutterProject = Directory.current;
      final repository = flutterProject.parent.parent;
      final dataDirectory = await Directory.systemTemp.createTemp(
        'r4-learning-http-',
      );
      final reservation = await ServerSocket.bind(
        InternetAddress.loopbackIPv4,
        0,
      );
      final port = reservation.port;
      await reservation.close();
      final process = await Process.start(python, [
        '-m',
        'knowledge_graph_learning.backend',
        '--host',
        '127.0.0.1',
        '--port',
        '$port',
        '--data-dir',
        dataDirectory.path,
      ], workingDirectory: repository.path);
      final stdoutBuffer = StringBuffer();
      final stderrBuffer = StringBuffer();
      final stdoutSubscription = process.stdout
          .transform(utf8.decoder)
          .listen(stdoutBuffer.write);
      final stderrSubscription = process.stderr
          .transform(utf8.decoder)
          .listen(stderrBuffer.write);
      final client = http.Client();
      addTearDown(() async {
        client.close();
        process.kill();
        try {
          await process.exitCode.timeout(const Duration(seconds: 3));
        } on Exception {
          process.kill(ProcessSignal.sigkill);
        }
        await stdoutSubscription.cancel();
        await stderrSubscription.cancel();
        if (dataDirectory.existsSync()) {
          await dataDirectory.delete(recursive: true);
        }
      });

      final baseUrl = 'http://127.0.0.1:$port';
      var ready = false;
      for (var attempt = 0; attempt < 50; attempt++) {
        try {
          final response = await client
              .get(Uri.parse('$baseUrl/api/learning/health'))
              .timeout(const Duration(milliseconds: 300));
          if (response.statusCode == 200) {
            ready = true;
            break;
          }
        } on Exception {
          await Future<void>.delayed(const Duration(milliseconds: 100));
        }
      }
      if (!ready) {
        fail(
          'Learning API did not start. stdout=$stdoutBuffer stderr=$stderrBuffer',
        );
      }

      final controller = LearningController(
        HttpLearningApi(baseUrl, client: client),
      );
      addTearDown(controller.dispose);

      await controller.createGoal('理解 Python 装饰器并能在工程中正确使用');
      expect(controller.destination, WorkspaceDestination.graph);
      expect(controller.course!.nodes.length, inInclusiveRange(6, 12));

      await controller.selectDestination(WorkspaceDestination.path);
      expect(controller.recommendation!.reason, isNotEmpty);

      await controller.startRecommendedPractice();
      expect(controller.destination, WorkspaceDestination.practice);
      expect(controller.session!.nodeId, controller.recommendation!.node.id);
      expect(controller.activity!.content, isNotEmpty);
      expect(controller.activity!.question, isNotEmpty);

      await controller.submitEvidence(
        '装饰器接收一个可调用对象并返回新的可调用对象。工程里我会用 '
        'functools.wraps 保留元数据，并避免在装饰阶段执行有副作用的逻辑。',
      );
      expect(controller.destination, WorkspaceDestination.review);
      expect(controller.pendingReview!.reason, isNotEmpty);
      expect(
        controller.pendingReview!.events.map((event) => event.phase),
        containsAllInOrder(['tutor', 'evaluator']),
      );

      if (controller.pendingReview!.proposal != null) {
        await controller.decide(true);
        expect(controller.reviewOutcome, 'completed');
        expect(
          controller.pendingReview!.events.map((event) => event.phase),
          contains('apply_graph_update'),
        );
      }

      await controller.selectDestination(WorkspaceDestination.progress);
      expect(controller.destination, WorkspaceDestination.progress);
      expect(controller.course!.mastery, greaterThan(0));
    },
    skip: enabled
        ? false
        : 'Set R4_LIVE_DEEPSEEK=1 and DEEPSEEK_API_KEY to run live.',
    timeout: const Timeout(Duration(minutes: 3)),
  );
}
