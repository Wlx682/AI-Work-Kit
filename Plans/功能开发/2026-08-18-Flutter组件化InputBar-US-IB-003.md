---
tags: [功能开发, 用户故事, TDD, Flutter, Durable]
type: plan
category: 功能开发
status: 已完成
date: 2026-08-19
lifecycle_state: implementation-design
epic: Plans/Epic/2026-08-18-Flutter组件化InputBar.md
parent: Plans/功能开发/2026-08-18-Flutter组件化InputBar.md
requirement_plan: Plans/需求分析/2026-08-18-Flutter组件化InputBar.md
architecture_plan: Plans/技术方案/2026-08-18-Flutter组件化InputBar.md
story_id: US-IB-003
story_points: 8
sprint_scope: true
含业务逻辑: 是
implementation_design: Plans/功能开发/2026-08-18-Flutter组件化InputBar-US-IB-003.impl.json
tdd_evidence: Plans/功能开发/2026-08-18-Flutter组件化InputBar-US-IB-003.tdd.json
commit: 6973cc9794c6c1ffce30156d5cd225fb50ab449f
---

# US-IB-003：Slate 与成功附件的 durable 发送和草稿结算

作为 Chat 用户，我要把当前 Slate prompt 和成功附件作为同一不可变 delivery 发送，以便重试不会串附件，失败/未知也不会误删新草稿。

## 验收标准

- AC-IB-010：仅附件或文本+附件均可冻结，远程引用进入受控 prompt。
- AC-IB-012：失败、未知和 owner 换代保留正确 revision 草稿。
- AC-IB-013：只有精确 delivery 成功才清理对应 Slate/附件。

## 故事边界

本故事包含 SnapshotFactory、ChatController/Outbox 映射、idempotency/owner 结算与集成测试；不修改未确认的 Gateway remote attachment schema。

## 实现落点结论

- 新建 immutable `NamiInputSubmissionSnapshot`/typed `NamiInputSnapshotFactory`，一次性冻结 Slate prompt 与成功附件列表。
- `ChatController.sendInput(snapshot)` 只把冻结 prompt 交给既有 durable outbox；远程 URL 不误填 Gateway base64 attachment 字段。
- ProductChat 仅在精确 completed delivery 结算时清理对应 revision/attachment snapshot；userAborted、error、unknown、owner 换代保留草稿。

## 完成结果

- `NamiInputSnapshotFactory` 一次冻结 Slate document、受控 prompt、成功附件及后续 Model/Skill/turnOptions 承载位；空、禁用、未就绪输入 typed 拒绝。
- `ChatController.sendInput(snapshot)` 复用既有 durable outbox/idempotency/recovery，不在 await 或 retry 后重读 InputBar。
- 只有精确 completed terminal 清理相同 document revision 与 attachment snapshot；`userAborted`、error、unknown 保留，成功后新增附件不被误删。
- commit：`6973cc9794c6c1ffce30156d5cd225fb50ab449f`；InputBar 48 / ProductChat durable 86 tests；真机矩阵 `NOT_RUN`。

## 反馈（skill_run）

```yaml
skill_run:
  skill: implementation-design-assistant
  workflow_stage: implementation-design
  plan: Plans/功能开发/2026-08-18-Flutter组件化InputBar-US-IB-003.md
  date: 2026-08-19
  contexts_used:
    - path: Plans/技术方案/2026-08-18-Flutter组件化InputBar.md
      utility: high
      reason: "落实 SnapshotFactory、受控 remote URL prompt 和既有 durable outbox ADR"
    - path: Plans/功能开发/2026-08-18-Flutter组件化InputBar-US-IB-003.impl.json
      utility: high
      reason: "固定 snapshot/sendInput/终态结算和 Red 测试的逐文件落点"
  contexts_missing: []
  contexts_stale: []
  outcome_status: pass
  outcome: "US-IB-003 落点已确认，可从 snapshot freeze 与 aborted 保留回归进入 Red"
  revisit_needed: false
```
