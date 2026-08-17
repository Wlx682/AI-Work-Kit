---
tags: [功能开发, B4, Safety, ActionIntent]
type: plan
category: 功能开发
status: 待开发
date: 2026-08-17
lifecycle_state: story-development
parent: Plans/功能开发/2026-08-17-agent全仓TypeScript重构.md
story_id: US-B4-001
story_points: 8
sprint_scope: false
tdd_evidence: Plans/功能开发/2026-08-17-agent全仓TypeScript重构-US-B4-001.tdd.json
implementation_design: Plans/功能开发/2026-08-17-agent全仓TypeScript重构-US-B4-001.impl.json
---
# US-B4-001：经独立 Safety Executor 安全执行并对账现实效果

作为 Runtime，我想只提交 ActionIntent，由独立身份的 Executor 授权、幂等执行和核验效果，以便在无长期写凭证时完成受控现实动作。

覆盖 `GWT-015—018`。必须验证旁路拒绝、重复 Intent 去重和 `EFFECT_UNKNOWN` reconcile；同进程 mock 不构成生产证明。

续做：`/resume plan=Plans/功能开发/2026-08-17-agent全仓TypeScript重构-US-B4-001.md 进度=implementation-design`
