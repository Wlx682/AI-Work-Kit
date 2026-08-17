---
tags: [功能开发, B2, LangGraph, Checkpoint]
type: plan
category: 功能开发
status: 待开发
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

续做：`/resume plan=Plans/功能开发/2026-08-17-agent全仓TypeScript重构-US-B2-003.md 进度=implementation-design`
