---
tags: [功能开发, B5, Cutover, 删除]
type: plan
category: 功能开发
status: 待开发
date: 2026-08-17
lifecycle_state: story-development
parent: Plans/功能开发/2026-08-17-agent全仓TypeScript重构.md
story_id: US-B5-002
story_points: 5
sprint_scope: false
tdd_evidence: Plans/功能开发/2026-08-17-agent全仓TypeScript重构-US-B5-002.tdd.json
implementation_design: Plans/功能开发/2026-08-17-agent全仓TypeScript重构-US-B5-002.impl.json
---
# US-B5-002：人工批准后一次切换并保留回滚基线

作为发布负责人，我想在所有证据全绿且人工批准后一次删除 Python 并切换 DSH 入口，以便得到纯 TypeScript 工作树且仍能从 baseline 引用审计回滚。

覆盖 cutover 侧 `GWT-021—022`。这是独立破坏性 Story；实现与执行都需要当时的明确人工批准，任何红灯都保持 blocked。

续做：`/resume plan=Plans/功能开发/2026-08-17-agent全仓TypeScript重构-US-B5-002.md 进度=implementation-design`
