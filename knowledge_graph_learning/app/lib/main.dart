import 'package:flutter/material.dart';

import 'src/learning_api.dart';
import 'src/nexus_app.dart';

void main() {
  const apiUrl = String.fromEnvironment(
    'LEARNING_API_URL',
    defaultValue: 'http://127.0.0.1:8765',
  );
  runApp(NexusApp(api: HttpLearningApi(apiUrl)));
}
