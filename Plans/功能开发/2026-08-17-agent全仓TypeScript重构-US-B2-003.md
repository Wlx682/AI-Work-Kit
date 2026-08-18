---
tags: [功能开发, B2, LangGraph, Checkpoint]
type: plan
category: 功能开发
status: 已完成
date: 2026-08-17
lifecycle_state: story-development
parent: Plans/功能开发/2026-08-17-agent全仓TypeScript重构.md
story_id: US-B2-003
story_points: 8
sprint_scope: false
tdd_evidence: Plans/功能开发/2026-08-17-agent全仓TypeScript重构-US-B2-003.tdd.json
implementation_design: Plans/功能开发/2026-08-17-agent全仓TypeScript重构-US-B2-003.impl.json
---
# US-B2-003：运行、暂停、恢复、回放和 fork 单 Agent 会话

作为学习者，我想从 SQLite checkpoint 精确恢复同一会话、回放或 fork 合法状态，以便学习 LangGraph.js 原生持久化而不绕过审批。

覆盖 `M026—M037`。恢复不得重放工具、不得通过修改状态绕过审批；trace 失败只形成 warning。

## 当前 Scope

- 用户在 `US-B2-002` 完成后回复“继续”，因此本轮只激活 `US-B2-003`。
- 前置 `US-B2-001`、`US-B2-002` 均已完成并有 TDD/提交证据；其余未完成 Story 保持 `sprint_scope=false`。
- 用户已确认实现落点；`US-B2-003` 已完成 Red→Green→Refactor，且没有激活 `US-B2-004`。

## 实现落点设计草案

机器真理源：`Plans/功能开发/2026-08-17-agent全仓TypeScript重构-US-B2-003.impl.json`，用户回复“继续”后已更新为 `confirmed=true`。

- 单 Agent Graph：把现有一次性演示图扩为注入 ports 的 plan→predict/adjust→action→human interrupt→reflect/replan→complete/failed StateGraph，复用已完成的 Definition、Planning 和 Action，不复制能力逻辑。
- 恢复安全：resume 只用原生 `Command` 消费已 checkpoint 的精确 session/proposal；fork 仅允许安全 checkpoint 的 `steps` patch，审批/input/unknown 中断态整体禁止 fork。
- 持久证据：新增版本化 Learning RunResult/RunEvent/Checkpoint 契约与按 runId 原子 trace；trace 失败只追加 warning，SQLite checkpoint 失败仍是业务失败。
- Red：按已采纳矩阵在 contracts、runtime、recovery、persistence、CLI 与 migration map 中逐项覆盖 `M026—M037`。

落点、依赖方向、Red 和停止条件已经用户确认，并已按该设计完成 TDD。

## TDD 完成证据

- 代码提交：`b359c774b6dacddf050463a06634332362986dcc`。
- Red：6 组目标命令因 RunResult/Trace 模块、recover/history API、CLI 命令与迁移路径尚不存在而失败，`exit_code=1`。
- Green/Refactor：M026—M037、版本化契约、真实 CLI 与迁移索引定向 `15/15` 通过；全仓 TypeScript `94/94`。
- Integration smoke：Python `60/60`、全仓 typecheck、冻结安装、DSH composition verify 与真实 headless `--help` 通过。
- 组合指纹：`f699e62362fde18ceecbd0b0f5622c2763a8ac05953ba96a8cba33aa14545b39`；仅 contracts artifact SHA 与总指纹变化，生产 DSH/Cordis/Profile/Provider/finalConfig 不变。
- TDD 真理源：`Plans/功能开发/2026-08-17-agent全仓TypeScript重构-US-B2-003.tdd.json`。

本 Story 已完成并退出滚动 Scope；用户回复“继续”后，下一条 `US-B2-004` 已单独激活。

续做：`/resume plan=Plans/功能开发/2026-08-17-agent全仓TypeScript重构.md 进度=next-story-scope`
