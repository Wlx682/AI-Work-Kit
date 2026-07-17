---
tags: [功能开发, 智能体开发, R3, LangGraph]
type: plan
category: 功能开发
status: 已采纳
date: 2026-07-17
workflow: learning-loop
lifecycle_state: development
epic: Plans/Epic/2026-07-08-智能体开发.md
requirement_plan: Plans/需求分析/2026-07-17-Orchestrator迁移LangGraphRuntime.md
relations:
  depends_on:
    - Plans/功能开发/2026-07-17-Orchestrator最小RuntimeAdapter.md
  dependents: []
  supersedes: []
  superseded_by: []
  conflicts: []
---

# 功能开发：Orchestrator 迁移 LangGraph Runtime

**创建日期**：2026-07-17  
**状态**：已采纳  
**所属 Epic**：`Plans/Epic/2026-07-08-智能体开发.md`

## 一、需求分析

需求来源：[Orchestrator 迁移 LangGraph Runtime 需求分析](../需求分析/2026-07-17-Orchestrator迁移LangGraphRuntime.md)。本次是用户明确要求的第三方 runtime 迁移，`p0_open=0`。

## 二、目标与边界

用 LangGraph `StateGraph` 替代单智能体的手写主调度。业务能力仍复用现有模块，第三方 runtime 负责状态图执行、节点流更新和 thread checkpoint。保留 `RunResult` 作为 CLI 与测试的兼容输出。

## 三、实施切片

- [x] 1. 安装并锁定 `langgraph==1.2.9`。
- [x] 2. 定义 AgentState 和六个图节点。
- [x] 3. 定义执行/反思后的条件边，覆盖完成、提前结束、重规划与最大步数边界。
- [x] 4. 用 LangGraph stream 更新构造兼容的 `RunEvent`。
- [x] 5. 用 `InMemorySaver` 为每个 run 写入 framework checkpoint。
- [x] 6. 添加离线测试覆盖重规划、checkpoint 和规划失败。
- [x] 7. 清理当前 `agent/` 中遗留的 System 1/System 2 命名，统一为图节点和能力名称。
- [x] 8. 为结构化 LLM 输出增加一次 JSON 语法修复重试，并覆盖成功修复和再次失败。

## 四、验收标准

| 验收项 | 标准 |
|--------|------|
| 第三方 runtime | 默认 Orchestrator 使用 LangGraph。 |
| 业务语义 | 仍按 记忆→规划→预测→执行/反思→沉淀 运行。 |
| 重规划 | reflect 返回 replan 后，图继续执行新步骤。 |
| 可观察性 | 节点更新归一化为 `RunEvent`，框架保存多个 checkpoint。 |
| 失败收口 | 节点异常返回失败 `RunResult`。 |
| 结构化输出 | JSON 首次解析失败时仅重试一次语法修复；仍失败时给出明确错误。 |

## 五、实现与验证

| 产物 | 说明 |
|------|------|
| `agent/langgraph_runtime.py` | StateGraph、AgentState、节点、条件边、stream/checkpoint 适配。 |
| `agent/orchestrator.py` | 保留公开 API，默认委托给 `LangGraphRuntime`。 |
| `agent/runtime.py` | 仅保留 runtime-neutral 的 `RunEvent` 与 `RunResult`。 |
| `agent/tests/test_runtime.py` | 重规划回环、checkpoint 数量、规划失败的离线测试。 |
| `pyproject.toml` | 锁定 LangGraph 1.2.9。 |

验证结果：`python3 -m unittest discover -s agent/tests -v` 通过 4 项；`python3 -m compileall -q agent` 通过。

JSON 健壮性：`chat_json()` 首次遇到模型格式错误时，会把原始输出交给模型只修复 JSON 语法；修复后才继续执行，第二次失败则终止并保留解析位置。这避免单个缺逗号的模型输出直接中断整次运行。

命名清理：当前实现不再使用 System 1/System 2 作为架构概念；控制台和代码注释统一为规划、预测、执行、反思、记忆沉淀等节点/能力名称。Epic 中的同名表述保留为学习历史，不表示当前代码结构。

角色抽象：曾尝试为节点增加 `GraphRole` 标签，但它没有接入工具权限、模型配置、路由或独立上下文，仅服务日志和测试，因此已删除。当前单智能体图直接使用节点名表达职责；控制台保留 `[记忆]`、`[规划]`、`[预测]`、`[执行]`、`[反思]` 作为纯展示标签。`Team` 的独立角色与消息总线仍是另一种编排方式。

## 续做

```text
/resume plan=Plans/功能开发/2026-07-17-Orchestrator迁移LangGraphRuntime.md 进度=LangGraph runtime 已通过离线验证；下一步在该 runtime 上做 trace 持久化或 eval harness
```

## 反馈（skill_run）

```yaml
skill_run:
  skill: feature-dev-assistant
  plan: Plans/功能开发/2026-07-17-Orchestrator迁移LangGraphRuntime.md
  date: 2026-07-17
  contexts_used:
    - path: Plans/需求分析/2026-07-17-Orchestrator迁移LangGraphRuntime.md
      utility: high
      reason: "固定了第三方 runtime 迁移的边界、验收与非目标。"
    - path: Plans/功能开发/2026-07-17-Orchestrator最小RuntimeAdapter.md
      utility: high
      reason: "提供既有 RunResult/RunEvent 兼容契约作为迁移对照。"
  contexts_missing: []
  contexts_stale: []
```
