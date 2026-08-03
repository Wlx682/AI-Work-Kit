---
tags: [功能开发, R4, 架构重构, 目录治理, 子任务]
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
    - Plans/功能开发/2026-08-03-R4真实DeepSeek学习智能接入-子任务05b-声明式AgentDefinition统一.md
  dependents:
    - Plans/功能开发/2026-08-03-R4真实DeepSeek学习智能接入-子任务05d-dotenv本地配置.md
  supersedes: []
  superseded_by: []
  conflicts: []
---

# 子任务 05c：产品目录与 Agent 分层重构

## 一、需求分析（开工门禁）

- 需求：用户要求把正式项目从 `tmp/` 移出，与 `agent/` 平级，并从架构设计角度优化目录。
- 需求 plan：`Plans/需求分析/2026-08-03-R4真实DeepSeek学习智能接入.md`。
- 技术方案：`Plans/技术方案/2026-08-03-R4真实DeepSeek学习智能接入.md`。
- 边界：API Schema、领域行为和 HITL 流程不变；只调整产品归属、分层、导入和运行数据位置。

## 二、原子目标

建立 `knowledge_graph_learning/` 正式产品包，把 Flutter、R4 后端、学习 Agent Definition/Prompt 和产品测试统一归位；将通用 `agent/` 重组为 core、cognition、infrastructure、orchestration、guardrails 等职责目录，形成 `knowledge_graph_learning → agent` 单向依赖。

## 三、架构决策

| 决策 | 结果 |
|------|------|
| 正式产品目录 | `knowledge_graph_learning/` 与 `agent/` 平级；Flutter 位于 `app/`，后端位于 `backend/`。 |
| 后端分层 | domain / application / agents / orchestration / infrastructure / interfaces / tests。 |
| Agent 底座 | core / cognition / infrastructure / orchestration / guardrails / capabilities / roles / tools。 |
| 策略归属 | learning-* Definition 与 Prompt 属于学习产品；通用 Definition 留在 `agent/`。 |
| 运行数据 | `.runtime/knowledge-graph-learning/`，统一被 `.gitignore` 排除。 |
| 兼容策略 | 不保留旧平铺模块壳；代码与测试直接迁至新路径，避免双入口长期漂移。 |

## 四、验收

- [x] `tmp/knowledge-graph-learning-flutter` 已迁为 `knowledge_graph_learning/app/`。
- [x] R4 后端与学习 Agent 策略已从 `agent/` 迁入 `knowledge_graph_learning/backend/`。
- [x] `agent/` 根目录不再包含任何 `learning_*` 产品模块，并具有职责目录说明。
- [x] 后端 HTTP 与 application service 分离；DeepSeek adapter 与 Intelligence port 分离。
- [x] 启动入口变为 `uv run python -m knowledge_graph_learning.backend`。
- [x] 通用 Agent 45 tests、学习后端 97 tests 通过，合计 142。
- [x] Flutter analyze 与 13 tests 通过；真实 online smoke 仍由子任务 06 的 key 门禁控制。

## 五、续做

`/resume plan=Plans/功能开发/2026-08-03-R4真实DeepSeek学习智能接入-子任务06-在线闭环验收.md 进度=05c完成；knowledge_graph_learning产品包与agent通用底座已分层；仅待key在线smoke`

## 六、反馈（skill_run）

```yaml
skill_run:
  skill: feature-dev-assistant
  plan: Plans/功能开发/2026-08-03-R4真实DeepSeek学习智能接入-子任务05c-产品目录与Agent分层重构.md
  date: 2026-08-03
  contexts_used:
    - path: Plans/技术方案/2026-08-03-R4真实DeepSeek学习智能接入.md
      utility: high
      reason: "以产品/平台单向依赖和 hexagonal 分层约束目录迁移、接口边界与启动入口。"
    - path: Plans/功能开发/2026-08-03-R4真实DeepSeek学习智能接入-子任务05b-声明式AgentDefinition统一.md
      utility: high
      reason: "保留四个 AgentDefinition 的唯一真理源和 Runtime trace 身份语义，同时把策略归属迁回学习产品。"
  contexts_missing: []
  contexts_stale: []
  outcome_status: pass
  revisit_needed: false
```
