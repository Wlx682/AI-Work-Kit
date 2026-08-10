---
tags: [功能开发, 用户故事, TDD]
type: plan
category: 功能开发
status: 进行中
date: 2026-08-10
lifecycle_state: story-development
parent: Plans/功能开发/2026-08-10-cloud-drive-browser-folder-move.md
story_id: US-003
story_points: 8
sprint_scope: true
tdd_evidence: Plans/功能开发/2026-08-10-cloud-drive-browser-folder-move-US-003.tdd.json
implementation_design: Plans/功能开发/2026-08-10-cloud-drive-browser-folder-move-US-003.impl.json
---

# US-003：选择目标目录并移动文件或文件夹

## 一、需求分析

- 需求基线：`Plans/需求分析/2026-08-10-cloud-drive-browser-folder-move.md`

## 用户故事与 AC

作为已登录用户，我想浏览目标目录并移动个人云盘项目，以便修正文件位置且不会误移到非法目录。覆盖 GWT-012～018；架构 ADR-002/003/004/005/006。

## 故事内部实现边界

- UI：iOS 近全高底部弹层、drag/header/breadcrumb/目录列表/bottom bar/边缘返回。
- Domain：destination stack、非法目标、single-flight、reconcile、双目录和搜索失效。
- Data：目录只读 Repository、move/reconcile 生产接线。
- 测试：自身/后代、失败保持、结果未知、切 owner、三档 resize、真实账号冒烟。

## 实现落点设计

`.impl.json` 已生成并补入共享集成落点。当前已落地目录选择、非法目标过滤、move/reconcile 状态机、Fake、iOS 对齐底部弹层、YunPan move/list/exact-exists 生产 adapter、入口与 l10n。

## TDD

Red → Green → Refactor 与 76 项 Cloud Drive/宿主回归已执行，证据写入 `tdd_evidence`。候选已以 `7be6420` 提交，但尚缺受控真实账号移动冒烟、真机边缘手势/窗口切换和五形态证据，Story 保持进行中。

## 反馈（skill_run）

```yaml
skill_run:
  skill: feature-dev-assistant
  workflow_stage: story-development
  plan: Plans/功能开发/2026-08-10-cloud-drive-browser-folder-move-US-003.md
  date: 2026-08-10
  contexts_used:
    - path: Contexts/决策/Skill反馈协议.md
      utility: high
      reason: "如实记录移动状态机与回归已完成、真实移动和设备交互证据仍待补齐。"
  contexts_missing: []
  contexts_stale: []
  outcome_status: partial
  revisit_needed: true
  revisit_reason: "补齐真实账号移动冒烟、真机边缘手势与窗口切换及五形态证据。"
```
