---
tags: [功能开发, 用户故事, TDD]
type: plan
category: 功能开发
status: 进行中
date: 2026-08-10
lifecycle_state: story-development
parent: Plans/功能开发/2026-08-10-cloud-drive-browser-folder-move.md
story_id: US-002
story_points: 5
sprint_scope: true
tdd_evidence: Plans/功能开发/2026-08-10-cloud-drive-browser-folder-move-US-002.tdd.json
implementation_design: Plans/功能开发/2026-08-10-cloud-drive-browser-folder-move-US-002.impl.json
---

# US-002：在当前个人云盘目录新建文件夹

## 一、需求分析

- 需求基线：`Plans/需求分析/2026-08-10-cloud-drive-browser-folder-move.md`

## 用户故事与 AC

作为已登录用户，我想在当前目录新建文件夹，以便按自己的结构整理文件。覆盖 GWT-007～011、017、018；架构 ADR-002/003/004/006。

## 故事内部实现边界

- UI：iOS 居中弹窗、键盘联动、草稿/错误/提交状态。
- Domain：name policy、single-flight、owner fence、resultUnknown、当前目录失效。
- Data：窄创建 Repository 与 policy port 的生产接线。
- 测试：空白、明确违规、policy 降级、重复提交、切 owner、三档 resize。

## 实现落点设计

`.impl.json` 已生成并补入共享集成落点。当前已落地 policy/create/reconcile 状态机、Fake、iOS 对齐弹窗、content audit/mkdir/exact-exists 生产 adapter、入口刷新与 l10n。

## TDD

Red → Green → Refactor 与 76 项 Cloud Drive/宿主回归已执行，证据写入 `tdd_evidence`。候选已以 `7be6420` 提交，但尚缺受控真实账号写入、真机键盘/窗口切换和五形态证据，Story 保持进行中。

## 反馈（skill_run）

```yaml
skill_run:
  skill: feature-dev-assistant
  workflow_stage: story-development
  plan: Plans/功能开发/2026-08-10-cloud-drive-browser-folder-move-US-002.md
  date: 2026-08-10
  contexts_used:
    - path: Contexts/决策/Skill反馈协议.md
      utility: high
      reason: "如实记录创建文件夹自动化链路已完成、真实写入与设备证据仍待补齐。"
  contexts_missing: []
  contexts_stale: []
  outcome_status: partial
  revisit_needed: true
  revisit_reason: "补齐受控真实账号写入、真机键盘与窗口切换及五形态证据。"
```
