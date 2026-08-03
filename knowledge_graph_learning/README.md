# Knowledge Graph Learning

R4 知识图谱驱动学习系统的正式产品目录。它与通用 `agent/` 底座平级，不再存放在 `tmp/`。

```text
knowledge_graph_learning/
├── backend/
│   ├── domain/          # 学习、图谱、Evidence、进度等领域契约
│   ├── application/     # 用例服务与 LearningIntelligence 端口
│   ├── agents/          # 四个学习 Agent、Definition 与 Prompt
│   ├── orchestration/   # LangGraph、checkpoint、HITL
│   ├── infrastructure/  # DeepSeek 等出站适配器
│   ├── interfaces/      # HTTP 入站适配器和 CLI
│   └── tests/           # 后端回归测试
└── app/                 # Flutter 多端客户端
```

## 启动

在仓库根目录启动后端：

```bash
cp .env.example .env
# 编辑 .env，把占位值替换为真实 DeepSeek API Key
uv run python -m knowledge_graph_learning.backend --port 8765
```

后端会自动读取仓库根目录 `.env`。已有进程环境变量优先，不会被 `.env` 覆盖；也可以通过 `--env-file /path/to/file` 指定其他文件。

另开终端启动 Flutter Web：

```bash
cd knowledge_graph_learning/app
/Users/wanglongxiang/development/flutter/bin/flutter run -d chrome \
  --dart-define=LEARNING_API_URL=http://127.0.0.1:8765
```

本地运行数据默认写入仓库根目录 `.runtime/knowledge-graph-learning/`，不会进入版本库。
