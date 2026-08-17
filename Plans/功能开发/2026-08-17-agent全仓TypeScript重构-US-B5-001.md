---
tags: [功能开发, B5, Rehearsal, Release]
type: plan
category: 功能开发
status: 待开发
date: 2026-08-17
lifecycle_state: story-development
parent: Plans/功能开发/2026-08-17-agent全仓TypeScript重构.md
story_id: US-B5-001
story_points: 8
sprint_scope: false
tdd_evidence: Plans/功能开发/2026-08-17-agent全仓TypeScript重构-US-B5-001.tdd.json
implementation_design: Plans/功能开发/2026-08-17-agent全仓TypeScript重构-US-B5-001.impl.json
---
# US-B5-001：运行完整 cutover rehearsal 并展示阻断证据

作为发布负责人，我想运行不执行删除的全量 rehearsal，并看到每个红灯及其证据，以便在不冒险切换的情况下判断候选是否 ready。

覆盖 rehearsal 侧 `GWT-021—022`。必须汇总 G-EQ、60 parity、lifecycle、fault、safety、隔离、回滚和人工状态。

续做：`/resume plan=Plans/功能开发/2026-08-17-agent全仓TypeScript重构-US-B5-001.md 进度=implementation-design`
