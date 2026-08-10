---
tags: [Epic, client-dev, 云盘, 文件操作]
type: plan
category: Epic
status: 进行中
date: 2026-08-10
epic_id: cloud-drive-rename-delete
workflow: client-dev
lifecycle_state: requirement
platform: 客户端
repo: namiwork-flutter
branch: dev
p0_open: 0
plans:
  requirement: Plans/需求分析/2026-08-10-cloud-drive-rename-delete.md
  prioritization: Plans/需求排序/2026-08-10-cloud-drive-rename-delete.md
  architecture: Plans/技术方案/2026-08-10-cloud-drive-rename-delete.md
  development: Plans/功能开发/2026-08-10-cloud-drive-rename-delete.md
  integration_plan: Plans/自动化测试/2026-08-10-cloud-drive-rename-delete-集成测试计划.md
  integration: Plans/自动化测试/2026-08-10-cloud-drive-rename-delete-集成测试.md
relations:
  depends_on:
    - Plans/Epic/2026-08-10-cloud-drive-browser-folder-move.md
    - Templates/模板约定.md
  dependents: []
  supersedes: []
  superseded_by: []
  conflicts: []
---

# Epic：个人云盘重命名与删除（client-dev）

**创建日期**：2026-08-10  
**关联仓库**：`namiwork-flutter` · **分支**：`dev`

> 本 Epic 只承接已分配的个人云盘文件重命名与删除，复用已提交的 YunPan token/signature/owner 底座。上传、下载、picker 与 Workspace 不进入本轮。

## 一、阶段索引

| 阶段 | stage key | Plan | 状态 |
|---|---|---|---|
| 需求分析 | requirement | `Plans/需求分析/2026-08-10-cloud-drive-rename-delete.md` | ⬜ |
| 需求排序 | prioritization | `Plans/需求排序/2026-08-10-cloud-drive-rename-delete.md` | ⬜ |
| 正式架构设计 | architecture | `Plans/技术方案/2026-08-10-cloud-drive-rename-delete.md` | ⬜ |
| 功能故事拆分 | story-split | `Plans/功能开发/2026-08-10-cloud-drive-rename-delete.md` | ⬜ |
| 实现落点设计 | implementation-design | 同上及动态 Story 子 Plan | ⬜ |
| 逐故事 TDD | story-development | 同上及动态 Story 子 Plan | ⬜ |
| 集成测试计划 | integration-test-plan | `Plans/自动化测试/2026-08-10-cloud-drive-rename-delete-集成测试计划.md` | ⬜ |
| 全量集成测试 | integration-test | `Plans/自动化测试/2026-08-10-cloud-drive-rename-delete-集成测试.md` | ⬜ |

## 二、范围与门禁

- 正式任务：文件重命名、个人云盘文件删除。
- 事实源：05 任务卡、MAP/PRE 冻结结论、iOS/Android 固定快照与用户最新裁决。
- 完成门禁：typed result、single-flight、owner fence、结果未知 reconcile、分页失效、三档 Widget 及真实账号/真机证据。
- 状态裁决：未关闭真实写操作与五形态证据前只能保持 `PARTIAL`。

## 三、动态用户故事看板

故事真理源：`Plans/功能开发/2026-08-10-cloud-drive-rename-delete.stories.json`。

| Story | 用户能力 | 优先级 | 点数 | Scope | 依赖 | 状态 |
|---|---|---|---|---|---|---|
| US-001 | 重命名当前个人云盘项目 | P0 | 待评 | true | 已有个人云盘浏览底座 | 待开发 |
| US-002 | 确认后删除个人云盘项目 | P0 | 待评 | true | US-001 共享失效/结果收敛 | 待开发 |

## 四、变更记录

| 日期 | 变更 | 影响阶段 | 证据 | 确认人 |
|---|---|---|---|---|
| 2026-08-10 | 用户要求继续迁移文件 Tab，建立下一批 Pure Dart 文件操作 Epic | requirement | 05 任务卡与看板 Owner | 王龙祥 |

## 续做

```text
/resume plan=Plans/Epic/2026-08-10-cloud-drive-rename-delete.md 进度=需求分析
```

## 反馈（skill_run）

```yaml
skill_run:
  skill: template-generator
  workflow_stage: epic-init
  plan: Plans/Epic/2026-08-10-cloud-drive-rename-delete.md
  date: 2026-08-10
  contexts_used:
    - path: Contexts/决策/Skill原子契约.md
      utility: high
      reason: "按 client-dev Epic 原子契约只建立阶段索引与范围骨架"
  contexts_missing: []
  contexts_stale: []
  outcome_status: pass
  revisit_needed: false
```
