---
tags: [功能开发, R4, R3, AgentDefinition, 子任务]
type: plan
category: 功能开发
status: 已完成
date: 2026-08-03
lifecycle_state: development
epic: Plans/Epic/2026-07-08-智能体开发.md
parent: Plans/功能开发/2026-08-03-R4真实DeepSeek学习智能接入.md
含业务逻辑: 是
relations:
  depends_on:
    - Plans/需求分析/2026-08-03-R4真实DeepSeek学习智能接入.md
    - Plans/技术方案/2026-08-03-R4真实DeepSeek学习智能接入.md
    - Plans/功能开发/2026-08-03-R4真实DeepSeek学习智能接入-子任务05-Flutter动态工作台.md
  dependents:
    - Plans/功能开发/2026-08-03-R4真实DeepSeek学习智能接入-子任务05c-产品目录与Agent分层重构.md
  supersedes: []
  superseded_by: []
  conflicts: []
---

# 子任务 05b：声明式 AgentDefinition 统一

## 一、需求分析（开工门禁）

- 需求：`Plans/需求分析/2026-08-03-R4真实DeepSeek学习智能接入.md`
- 技术方案：`Plans/技术方案/2026-08-03-R4真实DeepSeek学习智能接入.md`
- P0=0；覆盖 AC-S7-8。

## 二、原子目标

复用 R3 `AgentDefinition`/loader/BaseAgent，为 GraphCurator、LearningPlanner、Tutor、Evaluator 建立独立 JSON+Markdown definition，由 `LearningAgentTeam` 统一装配 DeepSeek prompt 与 Runtime roles；从 Learning API 删除 `_roles()`，trace 携带 definition id/version。

## 三、输入与输出

| 输入 | 输出 |
|------|------|
| R3 `agent/core/definition.py`、`roles/base.py`，R4 intelligence/runtime/API | definition schema version、4 JSON、4 prompts、`knowledge_graph_learning/backend/agents/`、测试与架构回写 |

## 四、验收

- [x] 四个 definition 可被 R3 loader 校验，id/role/goal/tools/acceptance/instructions/version 独立。
- [x] 四类 DeepSeek structured call 使用对应 definition prompt context。
- [x] `LearningAgentTeam` 是 Runtime roles 唯一装配入口，API 无 `_roles()`。
- [x] 四个角色 trace 均含 definition id/version；HITL tool 不进入 Agent tool allowlist。
- [x] Agent 全量 142 tests 通过；Flutter analyze 与 13 tests 回归通过。

## 五、续做

`/resume plan=Plans/功能开发/2026-08-03-R4真实DeepSeek学习智能接入-子任务05c-产品目录与Agent分层重构.md 进度=05b完成；四角色声明式Definition/Team/DeepSeek/Trace统一；进入产品目录治理`

## 六、反馈（skill_run）

```yaml
skill_run:
  skill: feature-dev-assistant
  plan: Plans/功能开发/2026-08-03-R4真实DeepSeek学习智能接入-子任务05b-声明式AgentDefinition统一.md
  date: 2026-08-03
  contexts_used:
    - path: Plans/技术方案/2026-08-03-R4真实DeepSeek学习智能接入.md
      utility: high
      reason: "按统一架构实现四角色 Definition、LearningAgentTeam、definition-bound DeepSeek 与 trace 元数据。"
    - path: Plans/学习循环/2026-08-01-学习记录-智能体开发-08-R3.3-声明式Agent定义.md
      utility: high
      reason: "复用 AgentDefinition 只承载策略、Runtime 保留控制流的既有边界。"
  contexts_missing: []
  contexts_stale: []
  outcome_status: pass
  revisit_needed: false
```
