---
tags: [需求分析, 智能体开发, R3, runtime]
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
  dependents:
    - Plans/功能开发/2026-07-17-Orchestrator最小RuntimeAdapter.md
  supersedes: []
  superseded_by: []
  conflicts: []
---

# 需求分析：Orchestrator 最小 Runtime Adapter

## 一、需求分析

用户在 R3 生产化学习中确定两项决策：第一刀只迁移单智能体 `Orchestrator`，且不引入任何外部依赖。当前编排器已经能完成“加载记忆、规划、风险预测、逐步执行与反思、经验沉淀”的业务闭环，但运行过程主要依赖终端 `print`，调用方只能拿到最终字符串。这样的形态适合学习手写循环，却无法稳定回答一次运行经历了哪些阶段、在哪一步失败、是否发生重规划，也不方便让测试或后续评估程序读取执行过程。

本需求是在不改变现有 Agent 策略的前提下，增加一个最小运行时边界。每次运行应有独立 ID、按顺序排列的阶段事件和明确的终态结果。运行时负责生命周期与异常收口；`planning`、`act`、`reviewing`、`world_model`、`Memory`、安全层及经验蒸馏仍归业务编排器所有。旧的 `Orchestrator.run()` 保持返回最终文本，避免这次重构连带破坏已有的命令行或练习代码。

## 二、范围与非目标

范围包括：`RunEvent`、`RunResult`、零依赖 `Runtime`、Orchestrator 的 trace 入口、单智能体 CLI 对结构化失败状态的消费，以及不访问真实 LLM 的离线测试。事件至少覆盖记忆加载与保存、规划、预测、步骤执行、反思、编排完成和运行失败。

非目标包括：迁移 `Team` 或 A2A 消息总线、引入第三方 Agent runtime、持久化 trace、可视化页面、取消令牌、重试策略和 Markdown 声明式角色。这些都属于后续 R3 切片，不能掩盖本次要先学清的最小 runtime 契约。用户已明确：待 R3 学习完成后，第三方 runtime 接入是既定后续步骤，不是可选项。

## 三、验收标准

| 编号 | 验收标准 |
|------|----------|
| AC1 | 运行时仅使用 Python 标准库，并为每次 `run` 生成唯一 run ID。 |
| AC2 | 成功运行返回 `RunResult`，其中事件 sequence 连续，且有 started/completed 终态。 |
| AC3 | 规划、预测、步骤、反思、记忆至少各产生一个结构化事件（路径实际经过时）。 |
| AC4 | 业务异常不丢失，返回失败 `RunResult` 并附带 failed 事件与错误信息。 |
| AC5 | `Orchestrator.run()` 仍向旧调用方返回最终文本；新增 `run_with_trace()` 供 CLI、测试与后续评估使用。 |
| AC6 | 离线测试覆盖重规划的 trace 和规划阶段失败，无需真实 API Key 或网络。 |

## 续做

```text
/resume plan=Plans/需求分析/2026-07-17-Orchestrator最小RuntimeAdapter.md 进度=需求已采纳，开发与离线验证已完成
```

## 反馈（skill_run）

```yaml
skill_run:
  skill: feature-dev-assistant
  plan: Plans/需求分析/2026-07-17-Orchestrator最小RuntimeAdapter.md
  date: 2026-07-17
  contexts_used:
    - path: Plans/学习循环/2026-07-17-学习-智能体开发-08-R3生产化.md
      utility: high
      reason: "记录了用户对 R3 第一刀和零依赖实现方式的设计决策。"
  contexts_missing: []
  contexts_stale: []
```
