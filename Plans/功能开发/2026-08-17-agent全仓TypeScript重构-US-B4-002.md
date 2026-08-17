---
tags: [功能开发, B4, Watchdog, Recovery]
type: plan
category: 功能开发
status: 待开发
date: 2026-08-17
lifecycle_state: story-development
parent: Plans/功能开发/2026-08-17-agent全仓TypeScript重构.md
story_id: US-B4-002
story_points: 5
sprint_scope: false
tdd_evidence: Plans/功能开发/2026-08-17-agent全仓TypeScript重构-US-B4-002.tdd.json
implementation_design: Plans/功能开发/2026-08-17-agent全仓TypeScript重构-US-B4-002.impl.json
---
# US-B4-002：Watchdog 证明权限组合并在失联时自动降级

作为运维者，我想由独立 Watchdog 观察心跳、水位、组合与旁路证明，以便证明不完整时自动停止受控写并进入 read-only/recovery。

覆盖 `GWT-020`。普通 Profile/Patch/插件不得重新开放高权限写能力。

续做：`/resume plan=Plans/功能开发/2026-08-17-agent全仓TypeScript重构-US-B4-002.md 进度=implementation-design`
