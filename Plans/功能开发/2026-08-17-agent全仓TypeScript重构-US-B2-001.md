---
tags: [功能开发, B2, Action, 人工审批]
type: plan
category: 功能开发
status: 已完成
date: 2026-08-17
lifecycle_state: story-development
parent: Plans/功能开发/2026-08-17-agent全仓TypeScript重构.md
story_id: US-B2-001
story_points: 8
sprint_scope: false
tdd_evidence: Plans/功能开发/2026-08-17-agent全仓TypeScript重构-US-B2-001.tdd.json
implementation_design: Plans/功能开发/2026-08-17-agent全仓TypeScript重构-US-B2-001.impl.json
---
# US-B2-001：迁写 Action、审批与 unknown 行为语义

作为学习者，我想在 TS Learning Runtime 中保留 action ID、审批、拒绝、unknown 与人工恢复语义，以便安全地理解并重放原系统动作生命周期。

覆盖 `M001—M011`。不得重放未知现实动作，不得把虚拟输入当作现实 Action。

## 当前 Scope

- 用户在 `US-B1-002` 完成后回复“继续任务”，因此本轮只激活 `US-B2-001`。
- 前置 `US-B1-002` 已完成并有 TDD 证据；其余未完成 Story 保持 `sprint_scope=false`。
- 当前先完成 implementation-design；未经落点门禁确认，不进入 Red/Green，也不激活 `US-B2-002`。

## 实现落点设计草案

机器真理源：`Plans/功能开发/2026-08-17-agent全仓TypeScript重构-US-B2-001.impl.json`。用户在四项落点门禁摘要后回复“继续”，当前 `confirmed=true`，允许进入 Red。

- 共享契约：新增 `packages/contracts/src/action.ts` 与 `learning-action-session.v1.json`，只描述可序列化 Learning Action session，不抢占 B4 production ActionIntent/Receipt。
- Learning 实现：新增 `labs/runtimes/langgraph-ts/src/action.ts`，以纯状态机和注入 port 保留审批、unknown、人工恢复、虚拟输入与不可信输出语义，不接 DSH/生产凭证。
- Red：`packages/contracts/test/action.spec.ts`、`labs/runtimes/langgraph-ts/test/act.spec.ts` 与迁移映射验收，逐项覆盖 M001—M011。
- 漂移修复：把 `migration/legacy-test-map.json` 的 M001—M011 旧 `packages/agent-loop` 目标同步到已采纳需求矩阵，禁止形成第二生产 Agent Loop。
- 组合证据：共享 contracts 变更会改变受控 DSH 组合哈希；integration smoke 只观察到 `contracts` 与总指纹变化，需显式重冻并复验，其余生产配置不得漂移。

落点已确认；开发必须先执行上述 Red 并保存非零退出证据，再进入 Green。

## TDD 完成证据

- 提交：`bded643f54700136681b0a819034c7d21fc1e65f`。
- Red：contracts/action 与 Learning/action 不存在、M001—M011 迁移目标仍为旧路径，三组命令均按预期非零失败。
- Green/Refactor：定向 3 文件 15/15，通过 contracts 与 Learning Lab typecheck；unknown 人工 `not_executed` 会清除 pending call。
- Integration smoke：TypeScript 66/66、Python 60/60、全仓 typecheck、DSH composition verify 与生产依赖扫描通过。
- 组合指纹：`80f0fc8e5024808d88ddf64bbfffcd42a917e75bcabb72ad3a93c7c13346701e`；仅共享 contracts artifact 与总指纹变化。
- TDD 真理源：`Plans/功能开发/2026-08-17-agent全仓TypeScript重构-US-B2-001.tdd.json`。

本 Story 已完成并退出当前滚动 Scope；用户回复“继续”后，下一条 `US-B2-002` 已单独激活。

续做：`/resume plan=Plans/功能开发/2026-08-17-agent全仓TypeScript重构.md 进度=next-story-scope`
