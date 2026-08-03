# Learning Agents

本目录只负责把 R3 的声明式 `AgentDefinition` 装配成 R4 学习角色，不存放领域实体、HTTP 或 LangGraph 控制流。

```text
catalog.py  加载并校验四个 learning-* Definition
team.py     构造四个 BaseAgent 子类并输出 LearningRuntimeRoles
```

角色策略的唯一真理源位于：

- `definitions/learning-*.json`：id、version、role、goal、tool allowlist、acceptance。
- `prompts/learning-*.md`：长角色指令。

边界：

- `application/intelligence.py` 定义端口、DTO 与结构校验。
- `infrastructure/deepseek_intelligence.py` 使用对应 Definition 构造 DeepSeek prompt。
- `orchestration/runtime.py` 只负责状态图、checkpoint、interrupt/resume 和工具门禁。
- `application/service.py` 只注入 Team、Intelligence、Repository，不声明角色。
- 图谱 apply 是 Runtime tool，不能放进任何学习 Agent 的 tools allowlist。
