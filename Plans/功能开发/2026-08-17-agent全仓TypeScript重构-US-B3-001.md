---
tags: [功能开发, B3, Ledger, SQLite]
type: plan
category: 功能开发
status: 待开发
date: 2026-08-17
lifecycle_state: story-development
parent: Plans/功能开发/2026-08-17-agent全仓TypeScript重构.md
story_id: US-B3-001
story_points: 8
sprint_scope: false
tdd_evidence: Plans/功能开发/2026-08-17-agent全仓TypeScript重构-US-B3-001.tdd.json
implementation_design: Plans/功能开发/2026-08-17-agent全仓TypeScript重构-US-B3-001.impl.json
---
# US-B3-001：从 SQLite 控制账本重放 DSH 运行动态镜像

作为监督者，我想按稳定序号查看并重放 DSH 控制事实，以便从不可变事实重建动态镜像，而不是相信运行时自报状态。

覆盖 append-only、幂等、durable commit、稳定 sequence、projection state hash 与损坏恢复；遵循 ENG-012 Provider Port。

续做：`/resume plan=Plans/功能开发/2026-08-17-agent全仓TypeScript重构-US-B3-001.md 进度=implementation-design`
