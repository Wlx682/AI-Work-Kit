---
tags: [需求分析, 智能体开发, R3, LangGraph]
type: plan
category: 需求分析
status: 已采纳
date: 2026-07-17
workflow: learning-loop
lifecycle_state: requirement
p0_open: 0
epic: Plans/Epic/2026-07-08-智能体开发.md
relations:
  depends_on:
    - Plans/学习循环/2026-07-17-学习-智能体开发-08-R3生产化.md
    - Plans/功能开发/2026-07-17-Orchestrator最小RuntimeAdapter.md
  dependents:
    - Plans/功能开发/2026-07-17-Orchestrator迁移LangGraphRuntime.md
  supersedes: []
  superseded_by: []
  conflicts: []
---

# 需求分析：Orchestrator 迁移 LangGraph Runtime

## 一、需求分析

用户在理解自建 runtime 与 `EventEmitter` 的边界后，明确要求立即改为第三方 runtime。此前的最小 adapter 已经完成学习任务：它证明了一次运行需要唯一 ID、事件序列、终态结果和失败收口，但它不应继续扩张成另一套自研框架。本切片将单智能体 Orchestrator 的主调度迁移到 LangGraph，保留既有能力函数、DeepSeek/OpenAI 兼容调用、工具、安全、世界模型与记忆策略。

迁移后的执行过程必须由图而非手写 `while` 循环管理。记忆加载、规划、预测、单步执行、反思和记忆沉淀成为图节点；边决定顺序、重规划后的回环和终止。LangGraph 的 `InMemorySaver` 为每个 run 的 thread 保存 checkpoint，框架 stream 产生节点更新。项目仍向调用方返回既有 `RunResult`，但其中事件由 LangGraph 的节点更新归一化而来。

## 二、范围与非目标

范围包括：新增 `langgraph==1.2.9` 依赖，定义 `StateGraph` 与 `AgentState`，将默认 Orchestrator 绑定到 `LangGraphRuntime`，将框架 stream 更新转换为兼容的 `RunEvent`，并验证重规划回环、checkpoint 与失败收口。用户已经明确允许提前执行原路线中的第三方 runtime 接入，因此 trace 持久化、eval harness、声明式 Agent 定义不再是它的前置条件，而是迁移完成后继续在 LangGraph 之上学习的后续切片。

非目标包括：迁移 Team/A2A、多智能体子图、接入 LangSmith 云端服务、引入数据库 checkpointer、修改 DeepSeek 模型客户端、改变工具安全策略，以及删除 `RunResult` 兼容 API。`InMemorySaver` 仅用于本地学习和测试；跨进程持久化将在后续 trace 切片中选择合适的 checkpointer。

## 三、验收标准

| 编号 | 验收标准 |
|------|----------|
| AC1 | `pyproject.toml` 声明精确的 `langgraph==1.2.9` 依赖。 |
| AC2 | 默认 `Orchestrator` 使用 `LangGraphRuntime`，而不是手写 Runtime 主循环。 |
| AC3 | 图中包含 load_memory、plan、predict、execute_step、reflect、save_memory 六个节点。 |
| AC4 | 重规划时图从 reflect 回到 execute_step，最终结果与原有语义一致。 |
| AC5 | 每次 run 使用 LangGraph thread/checkpointer，离线测试验证 checkpoint 数量大于 1。 |
| AC6 | 规划异常返回失败 `RunResult`，其事件序列以 failed 终态结束。 |

## 续做

```text
/resume plan=Plans/需求分析/2026-07-17-Orchestrator迁移LangGraphRuntime.md 进度=需求已采纳，LangGraph 迁移已完成并通过离线验证
```

## 反馈（skill_run）

```yaml
skill_run:
  skill: feature-dev-assistant
  plan: Plans/需求分析/2026-07-17-Orchestrator迁移LangGraphRuntime.md
  date: 2026-07-17
  contexts_used:
    - path: Plans/学习循环/2026-07-17-学习-智能体开发-08-R3生产化.md
      utility: high
      reason: "提供 R3.4 第三方 runtime 接入的既定路线和用户最新决策。"
  contexts_missing: []
  contexts_stale: []
```
