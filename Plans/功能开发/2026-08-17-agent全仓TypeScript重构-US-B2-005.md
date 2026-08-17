---
tags: [功能开发, B2, Tools, CLI]
type: plan
category: 功能开发
status: 待开发
date: 2026-08-17
lifecycle_state: story-development
parent: Plans/功能开发/2026-08-17-agent全仓TypeScript重构.md
story_id: US-B2-005
story_points: 8
sprint_scope: false
tdd_evidence: Plans/功能开发/2026-08-17-agent全仓TypeScript重构-US-B2-005.tdd.json
implementation_design: Plans/功能开发/2026-08-17-agent全仓TypeScript重构-US-B2-005.impl.json
---
# US-B2-005：通过结构化工具与 CLI 操作、暂停和恢复任务

作为学习者，我想通过 TS CLI 查看结构化工具结果、审批原因、warning 并恢复同一 thread，以便完整保留原 TUI/工具的可观察语义。

覆盖 `M044—M060`。工具 schema 错误不能包装成成功；CLI 必须支持中文、结构化 unknown resolution 和可操作错误。

续做：`/resume plan=Plans/功能开发/2026-08-17-agent全仓TypeScript重构-US-B2-005.md 进度=implementation-design`
