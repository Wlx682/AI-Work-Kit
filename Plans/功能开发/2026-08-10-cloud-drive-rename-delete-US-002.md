---
tags: [功能开发, 用户故事, TDD, 云盘]
type: plan
category: 功能开发
status: 进行中
date: 2026-08-10
lifecycle_state: story-development
parent: Plans/功能开发/2026-08-10-cloud-drive-rename-delete.md
story_id: US-002
story_points: 5
sprint_scope: true
tdd_evidence: Plans/功能开发/2026-08-10-cloud-drive-rename-delete-US-002.tdd.json
implementation_design: Plans/功能开发/2026-08-10-cloud-drive-rename-delete-US-002.impl.json
---

# US-002：确认后永久删除个人云盘文件或文件夹

## 一、需求分析

- 需求基线：`Plans/需求分析/2026-08-10-cloud-drive-rename-delete.md`

## 用户故事与 AC

作为个人云盘用户，我想在明确知道不可恢复后永久删除当前项目，以便清理不再需要的云端内容。覆盖 GWT-010..018；架构 ADR-001/002/003/004。

## 纵向交付边界

- UI：操作菜单危险入口、包含项目名和不可恢复文案的确认框、取消/提交/对账/失败状态。
- Domain/Application：确认前不创建命令、single-flight、owner/generation fence、unknown 自动对账和失效。
- Data/Core：`File.delete` + `is_clean_master=1`、精确源路径不存在性。
- 测试：取消不请求、成功/明确失败/unknown、迟到结果、三档 Widget 与宿主刷新。

## 实现落点设计

已确认 `implementation_design` JSON：新增 deletion 的 Domain/Application/Data/Presentation/Testing；扩展 personal cloud 永久删除契约，并在 runtime、composition root、browser host 与 l10n 串行接线。Red 从确认门禁、Controller、Dialog、core client 和 adapter 合同开始。

## 停止条件

目标自动化验证通过后可进入故事验收；永久删除真实账号证据缺失时保持进行中/PARTIAL，不宣称 VERIFIED。

## 当前实现证据

- 已完成不可恢复确认、`File.delete + is_clean_master=1`、single-flight、unknown/indeterminate 对账、runtime 恢复只 reconcile、稳定 ID tombstone 与分页/搜索 stale 屏蔽。
- `flutter test test/core/personal_cloud test/features/cloud_drive`：105/105 PASS。
- 定向 `flutter analyze`、format、任务 ID 命名门禁与 `git diff --check`：PASS。
- Flutter 与 iOS 两位独立 reviewer 最终结论均为 P0/P1 清零。
- Red 首次失败日志未单独留存；TDD 证据如实标记 `NOT_RECORDED`，不补造历史。
- 尚缺 Android oracle、真实账号永久删除与多形态真机证据，故事保持进行中。

## 续做

```text
/resume plan=Plans/功能开发/2026-08-10-cloud-drive-rename-delete-US-002.md 进度=实现落点设计
```

## 反馈（skill_run）

```yaml
skill_run:
  skill: feature-dev-assistant
  workflow_stage: story-development
  plan: Plans/功能开发/2026-08-10-cloud-drive-rename-delete-US-002.md
  date: 2026-08-10
  contexts_used:
    - path: Contexts/决策/Skill反馈协议.md
      utility: high
      reason: "如实记录永久删除自动化回归通过但破坏性真实账号验证仍未完成。"
  contexts_missing: []
  contexts_stale: []
  outcome_status: partial
  revisit_needed: true
  revisit_reason: "补齐 Android oracle、受控真实账号永久删除和五形态真机证据。"
```
