# Agent platform

`agent/` 是可复用的智能体编排底座，不承载具体产品领域对象或页面 API。

```text
agent/
├── core/             # AgentDefinition、RunEvent、RunResult 等稳定契约
├── cognition/        # 记忆、世界模型、经验提炼
├── infrastructure/   # DeepSeek 客户端、checkpoint、trace 持久化
├── orchestration/    # 单 Agent 与 Team 的 LangGraph 控制流
├── guardrails/       # 工具执行安全策略
├── capabilities/     # planning / act / reviewing 共享能力
├── roles/            # 通用 Planner / Predictor / Executor / Reviewer
├── tools/            # 工具注册与实现
├── definitions/      # 通用 Agent 策略 JSON
├── prompts/          # 通用 Agent 长指令
└── main.py           # CLI 适配层
```

依赖方向固定为：`orchestration → capabilities/roles/cognition → core`；基础设施通过明确模块引入，`core` 不反向依赖产品代码。知识图谱学习产品位于同级的 `knowledge_graph_learning/`，仅消费此底座的公开契约。
