---
tags: [功能开发, 用户故事, TDD, TypeScript, LangGraph, DeepSeek-Harness]
type: plan
category: 功能开发
status: 已完成
date: 2026-08-17
lifecycle_state: story-development
parent: Plans/功能开发/2026-08-17-agent-ts双runtime基座.md
story_id: US-TS-001
story_points: 5
sprint_scope: true
tdd_evidence: Plans/功能开发/2026-08-17-agent-ts双runtime基座-US-TS-001.tdd.json
implementation_design: Plans/功能开发/2026-08-17-agent-ts双runtime基座-US-TS-001.impl.json
relations:
  depends_on:
    - Plans/技术方案/2026-08-17-智能体控制系统工程架构-v0.1.md
    - Plans/代码重构/2026-08-17-agent控制系统工程落点-v0.1.md
  dependents: []
  supersedes: []
  superseded_by: []
  conflicts: []
---
# US-TS-001：双 TypeScript Runtime 基座与角色隔离

## 一、需求分析

需求真理源：[[Plans/需求分析/2026-08-17-agent-ts双runtime基座]]。

作为系统开发者，我想在不触碰当前 Python 脏工作区的前提下运行一个真实 LangGraph.js Learning Runtime，并让生产入口拒绝 Learning Runtime，以便开始全仓 TypeScript 改造，同时防止学习实现漂移成第二生产入口。

- AC1：根 pnpm workspace 可安装、typecheck 和运行 Vitest；
- AC2：`@langchain/langgraph` StateGraph 可执行并流式产生至少一个节点事件与确定终态；
- AC3：`runtimeRole=learning` 的 LangGraph.js Manifest 被生产守卫拒绝，`runtimeRole=production/runtimeType=dsh` 被接纳；
- AC4：生产 packages 不 import `labs/runtimes/langgraph-ts`，隔离测试可执行；
- AC5：原 `/Users/wanglongxiang/git/agent` 的用户修改保持原样，所有实现只发生在独立 worktree/branch。

## 故事内部实现边界

- Build：pnpm 11.7.0 workspace、严格 TypeScript、Vitest；
- Contract：`RuntimeManifest`、`runtimeRole` 与生产守卫；
- Learning Runtime：最小 LangGraph.js `StateGraph`、stream 和 CLI；
- Test：先写角色隔离和真实 graph Red，再做最小 Green；
- 不包含：DSH 正式包接入、Cordis 插件、生产写、安全执行器、可信 Evaluation Case、Python 删除。

## 实现落点设计

落点证据：`Plans/功能开发/2026-08-17-agent-ts双runtime基座-US-TS-001.impl.json`。

- 代码证据：旧 `orchestration/langgraph.py`、`core/models.py`、`tests/test_runtime.py`；
- 目标文件：根 workspace、`packages/contracts`、`labs/runtimes/langgraph-ts`、隔离测试；
- 模块边界：生产只依赖 contracts；Lab 可依赖 contracts，生产不得反向依赖 Lab；
- Red 命令：`corepack pnpm@11.7.0 test`。

## TDD

1. Red：先创建测试与 workspace 声明，运行时因 contracts/graph 尚未实现而失败；
2. Green：最小实现 RuntimeManifest guard 和 LangGraph.js StateGraph；
3. Refactor：收紧导出、命名、dependency direction；
4. Integration smoke：typecheck、全部 Vitest、LangGraph CLI。

## 故事验收

- [x] implementation_design 校验通过；
- [x] AC1—AC5 全部有证据；
- [x] Red / Green / Refactor / integration smoke 证据齐全；
- [x] 不宣称 DSH 或全量迁移已完成。

## 续做

```text
/resume plan=Plans/功能开发/2026-08-17-agent-ts双runtime基座-US-TS-001.md 进度=从 RuntimeRole 与 LangGraph.js StateGraph Red 开始
```

## 反馈（skill_run）

```yaml
skill_run:
  skill: feature-dev-assistant
  workflow_stage: story-development
  plan: Plans/功能开发/2026-08-17-agent-ts双runtime基座-US-TS-001.md
  date: 2026-08-17
  contexts_used:
    - path: Plans/技术方案/2026-08-17-智能体控制系统工程架构-v0.1.md
      utility: high
      reason: "提供 DSH 生产默认、LangGraph.js Learning Runtime 与 runtimeRole 隔离边界"
    - path: /Users/wanglongxiang/git/agent-ts-rewrite/labs/runtimes/langgraph-ts/src/graph.ts
      utility: high
      reason: "已落地真实 StateGraph、updates stream 与确定终态"
    - path: Plans/功能开发/2026-08-17-agent-ts双runtime基座-US-TS-001.tdd.json
      utility: high
      reason: "记录 Red、Green、Refactor、集成 smoke 和 AC1—AC5 证据"
  contexts_missing: []
  contexts_stale: []
  outcome: "完成 pnpm/TypeScript 基座、真实 LangGraph.js Learning Runtime 与 production/dsh 角色硬隔离，提交 c9db93d"
  utility: high
  reason: "首个纵切通过 4 个测试、严格类型检查和 CLI smoke，并保持原脏工作区不变"
```
