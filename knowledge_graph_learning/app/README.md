# Nexus Learning OS · R4 Flutter Client

这是 R4「知识图谱驱动学习系统」自己的 Flutter 工程，不依赖 LearnStudio 或其他旧项目。

## 本地运行

在仓库根目录启动 API：

```bash
cp .env.example .env
# 编辑 .env，把占位值替换为真实 DeepSeek API Key
uv run python -m knowledge_graph_learning.backend --port 8765
```

另开终端启动 Flutter Web：

```bash
cd knowledge_graph_learning/app
/Users/wanglongxiang/development/flutter/bin/flutter run -d chrome \
  --dart-define=LEARNING_API_URL=http://127.0.0.1:8765
```

也可运行 macOS、iOS 或 Android；真机需把 `LEARNING_API_URL` 改为设备可访问的主机地址。

## 已接通的主链

1. DeepSeek 根据任意学习目标生成并校验层级学习树，不使用固定初始图谱。
2. Graph 动态布局后端节点；Path 展示 DeepSeek recommendation、前置依赖和 reason。
3. 选择节点后，DeepSeek Tutor 生成内容、洞察、练习题和 rubric，并绑定 `LearningSession`。
4. Practice 把回答记作 `Evidence`；DeepSeek Evaluator 生成 score、reason、gaps 和可选图谱提案。
5. Review 按 run 展示 timeline；有图谱提案时在 checkpoint 暂停，等待人工批准或拒绝。
6. 若模型提出结构变更，批准后应用动态节点并保留 resume events；拒绝后保留原图。
7. Progress 从 Course DTO 只读展示 mastery、状态分布和节点进度。

## 验证

```bash
/Users/wanglongxiang/development/flutter/bin/flutter analyze
R4_LIVE_DEEPSEEK=1 \
  DEEPSEEK_API_KEY="$DEEPSEEK_API_KEY" \
  R4_PYTHON="$(cd ../.. && pwd)/.venv/bin/python" \
  /Users/wanglongxiang/development/flutter/bin/flutter test test/real_http_flow_test.dart
/Users/wanglongxiang/development/flutter/bin/flutter build web
```

在线用例会启动临时 Python Learning API，并真正调用 DeepSeek 跑通 Goal → Graph → Path → Tutor/Practice → Eval → 可选 Review。缺少 key 时明确跳过；生产 API 缺 key 会返回 `LLM_NOT_CONFIGURED`，不会回退到演示数据。
