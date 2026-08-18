---
tags: [功能开发, B2, LangGraph, Team]
type: plan
category: 功能开发
status: 已完成
date: 2026-08-17
lifecycle_state: story-development
parent: Plans/功能开发/2026-08-17-agent全仓TypeScript重构.md
story_id: US-B2-004
story_points: 5
sprint_scope: false
tdd_evidence: Plans/功能开发/2026-08-17-agent全仓TypeScript重构-US-B2-004.tdd.json
implementation_design: Plans/功能开发/2026-08-17-agent全仓TypeScript重构-US-B2-004.impl.json
---
# US-B2-004：运行并恢复多角色 Team Learning Graph

作为学习者，我想运行显式多角色 StateGraph、查看 handoff 并从暂停点恢复，以便学习团队路由且不把它接入生产控制面。

覆盖 `M038—M043`。风险、review rejection 与 retry limit 必须由显式 graph edge 表达。

## 当前 Scope

- 用户在 `US-B2-003` 完成后回复“继续”，因此本轮只激活 `US-B2-004`。
- 前置 `US-B2-003` 已完成并有 TDD/提交证据；其余 7 个未完成 Story 保持 `sprint_scope=false`。
- 用户已确认落点；`US-B2-004` 已完成 Red→Green→Refactor，且没有激活 `US-B2-005`。

## 实现落点设计草案

机器真理源：`Plans/功能开发/2026-08-17-agent全仓TypeScript重构-US-B2-004.impl.json`；用户回复“继续”后已更新为 `confirmed=true`，允许进入 Red。

- Team Graph：新增与单 Agent 并列的 `team-graph.ts`，用原生 StateGraph 条件边显式表达 risk adjustment、review rejection、retry exhaustion 与 human interrupt；不在节点内部用隐式循环替代路由证据。
- 角色与恢复：复用四个共享 Definition 和 Learning Action session，只补 Planner adjust/revise、Executor resolve 的注入式角色能力；`prepare_action` 推进并检查点化 session/proposal，`interrupt_for_human` 只消费原 proposal，禁止重启 Action。
- 事件与持久化：每个节点追加带 phase/payload 的 TeamVisit，handoff 可按 Planner→Predictor→Executor→Reviewer→Team 顺序从 RunEvent 读取；结果继续使用 `learning-run-result.v1` 与现有 TraceStore，不新增共享持久契约。
- Red：`M038—M043` 全部集中到已采纳的 `labs/runtimes/langgraph-ts/test/team-runtime.spec.ts`，并修正 migration map 漂移；Team CLI 留给 `US-B2-005`，当前不修改 `cli.ts`。

文件落点、模块边界、Red、风险和停止条件已经用户确认，并已按该设计完成 TDD。

## TDD 完成证据

- 代码提交：`4931d3285256388c5cfb0ec73ac087db86a7a851`。
- Red：Team 测试因 `team-runtime.ts` 尚不存在失败，角色回归因 `adjustPlan` 尚不存在失败；迁移路径门禁已先通过，失败仅来自本 Story 未实现。
- Green/Refactor：`M038—M043` Team 目标 `6/6`、角色回归 `2/2`、迁移路径 `1/1`；全仓 TypeScript `100/100`。
- Integration smoke：Python `60/60`、全仓 typecheck、冻结安装、DSH composition verify 与真实 headless `--help` 通过。
- 组合指纹保持 `f699e62362fde18ceecbd0b0f5622c2763a8ac05953ba96a8cba33aa14545b39`；生产 DSH/Cordis/Profile/Provider/finalConfig 未变化。
- TDD 真理源：`Plans/功能开发/2026-08-17-agent全仓TypeScript重构-US-B2-004.tdd.json`。

本 Story 已完成并退出滚动 Scope；用户回复“继续”后，下一条 `US-B2-005` 已单独激活。

续做：`/resume plan=Plans/功能开发/2026-08-17-agent全仓TypeScript重构.md 进度=next-story-scope`
