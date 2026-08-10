---
tags: [功能开发, 用户故事, TDD]
type: plan
category: 功能开发
status: 进行中
date: 2026-08-10
lifecycle_state: story-development
parent: Plans/功能开发/2026-08-10-cloud-drive-browser-folder-move.md
story_id: US-001
story_points: 8
sprint_scope: true
tdd_evidence: Plans/功能开发/2026-08-10-cloud-drive-browser-folder-move-US-001.tdd.json
implementation_design: Plans/功能开发/2026-08-10-cloud-drive-browser-folder-move-US-001.impl.json
---

# US-001：浏览搜索并进入个人云盘目录

## 一、需求分析

- 需求基线：`Plans/需求分析/2026-08-10-cloud-drive-browser-folder-move.md`

## 用户故事与 AC

作为已登录用户，我想浏览、搜索、刷新和进入个人云盘目录，以便找到和整理自己的文件。覆盖 GWT-001～006、017、018；架构 ADR-001/002/003/006。

## 故事内部实现边界

- UI：iOS 个人云盘列表、搜索、刷新、面包屑、加载/空/局部错误/分页及三档 renderer。
- Domain：owner/query/cursor/item/page/capability/failure。
- Data：窄 Repository 与生产 Cloud provider adapter 接线；不得复用 Gateway 个人云盘。
- 测试：分页去重、重叠搜索、切 owner、三档状态保持、真实账号冒烟。

## 实现落点设计

`.impl.json` 已生成并补入共享集成落点。当前已落地领域模型、窄 Repository、Controller、Fake、独立浏览视图、YunPan HTTP/token/signature 生产 adapter、App 入口与 l10n。

## TDD

Red → Green → Refactor 与 76 项 Cloud Drive/宿主回归已执行，证据写入 `tdd_evidence`。候选已以 `7be6420` 提交，但尚缺真实账号目录冒烟、Android 协议身份复核和五形态真机证据，Story 保持进行中。

## 反馈（skill_run）

```yaml
skill_run:
  skill: feature-dev-assistant
  workflow_stage: story-development
  plan: Plans/功能开发/2026-08-10-cloud-drive-browser-folder-move-US-001.md
  date: 2026-08-10
  contexts_used:
    - path: Contexts/决策/Skill反馈协议.md
      utility: high
      reason: "如实记录已完成自动化回归但仍缺真实账号和多形态设备证据的部分完成状态。"
  contexts_missing: []
  contexts_stale: []
  outcome_status: partial
  revisit_needed: true
  revisit_reason: "补齐真实账号目录冒烟、Android 协议身份复核和五形态真机证据。"
```
