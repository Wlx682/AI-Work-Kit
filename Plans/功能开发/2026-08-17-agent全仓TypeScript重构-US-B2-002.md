---
tags: [功能开发, B2, Definition, Planning, Roles]
type: plan
category: 功能开发
status: 待开发
date: 2026-08-17
lifecycle_state: story-development
parent: Plans/功能开发/2026-08-17-agent全仓TypeScript重构.md
story_id: US-B2-002
story_points: 8
sprint_scope: false
tdd_evidence: Plans/功能开发/2026-08-17-agent全仓TypeScript重构-US-B2-002.tdd.json
implementation_design: Plans/功能开发/2026-08-17-agent全仓TypeScript重构-US-B2-002.impl.json
---
# US-B2-002：迁写 Definition、LLM JSON、Planning 与 Role 语义

作为维护者，我想用共享 TS Definition/Prompt 契约和 Learning Runtime 验证 JSON、规划及角色边界，以便两个 Runtime 使用一致资产但各自采用原生编排机制。

覆盖 `M012—M025`。定义引用未知工具、非法版本或非字符串步骤时失败关闭；风险调整不得扩权。

续做：`/resume plan=Plans/功能开发/2026-08-17-agent全仓TypeScript重构-US-B2-002.md 进度=implementation-design`
