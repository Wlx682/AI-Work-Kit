---
tags: [功能开发, 用户故事, TDD, 云盘]
type: plan
category: 功能开发
status: 进行中
date: 2026-08-10
lifecycle_state: story-development
parent: Plans/功能开发/2026-08-10-cloud-drive-rename-delete.md
story_id: US-001
story_points: 8
sprint_scope: true
tdd_evidence: Plans/功能开发/2026-08-10-cloud-drive-rename-delete-US-001.tdd.json
implementation_design: Plans/功能开发/2026-08-10-cloud-drive-rename-delete-US-001.impl.json
---

# US-001：重命名当前个人云盘文件或文件夹

## 一、需求分析

- 需求基线：`Plans/需求分析/2026-08-10-cloud-drive-rename-delete.md`

## 用户故事与 AC

作为个人云盘用户，我想从文件 Tab 操作菜单修改当前项目名称，以便整理云端内容。覆盖 GWT-001..009、015..018；架构 ADR-002/003/004/005。

## 纵向交付边界

- UI：操作菜单入口、iOS 基线重命名对话框、校验/审核降级/提交/对账/失败状态及三档布局。
- Domain/Application：名称规则、single-flight、owner/generation fence、unknown 自动对账和失效。
- Data/Core：`File.rename`、内容审核、精确旧/新路径存在性。
- 测试：领域/Repository/Controller/Widget/宿主集成及真实账号写操作。

## 实现落点设计

已确认 `implementation_design` JSON：新增 rename 的 Domain/Application/Data/Presentation/Testing；扩展 personal cloud typed client，并在 runtime、composition root、browser host 与 l10n 串行接线。Red 从 Controller、Dialog、core client 和 adapter 合同开始。

## 停止条件

目标自动化验证通过后可进入故事验收；Android oracle、真实账号或多形态证据缺失时保持进行中/PARTIAL，不宣称 VERIFIED。

## 当前实现证据

- 已完成共享 optimistic rename、明确失败 rollback、unknown/indeterminate 精确对账、owner/runtime fence、分页与搜索 stale overlay、typed failure 和三档对话框接线。
- `flutter test test/core/personal_cloud test/features/cloud_drive`：105/105 PASS。
- 定向 `flutter analyze`、format、任务 ID 命名门禁与 `git diff --check`：PASS。
- Flutter 与 iOS 两位独立 reviewer 最终结论均为 P0/P1 清零。
- Red 首次失败日志未单独留存；TDD 证据如实标记 `NOT_RECORDED`，不补造历史。
- 尚缺 Android oracle、真实账号写操作与 iPhone/iPad/Android Phone/Pad/Fold 真机证据，故事保持进行中。

## 续做

```text
/resume plan=Plans/功能开发/2026-08-10-cloud-drive-rename-delete-US-001.md 进度=实现落点设计
```

## 反馈（skill_run）

```yaml
skill_run:
  skill: feature-dev-assistant
  workflow_stage: story-development
  plan: Plans/功能开发/2026-08-10-cloud-drive-rename-delete-US-001.md
  date: 2026-08-10
  contexts_used:
    - path: Contexts/决策/Skill反馈协议.md
      utility: high
      reason: "如实记录重命名自动化回归通过但真实账号和多形态设备验收尚未完成。"
  contexts_missing: []
  contexts_stale: []
  outcome_status: partial
  revisit_needed: true
  revisit_reason: "补齐 Android oracle、真实账号重命名和五形态真机证据。"
```
