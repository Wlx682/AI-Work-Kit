---
tags: [功能开发, 用户故事, 云盘]
type: plan
category: 功能开发
status: 进行中
date: 2026-08-10
lifecycle_state: story-development
epic: Plans/Epic/2026-08-10-cloud-drive-browser-folder-move.md
requirement_plan: Plans/需求分析/2026-08-10-cloud-drive-browser-folder-move.md
architecture_plan: Plans/技术方案/2026-08-10-cloud-drive-browser-folder-move.md
story_index: Plans/功能开发/2026-08-10-cloud-drive-browser-folder-move.stories.json
relations:
  depends_on:
    - Plans/需求分析/2026-08-10-cloud-drive-browser-folder-move.md
    - Plans/技术方案/2026-08-10-cloud-drive-browser-folder-move.md
  dependents: []
  supersedes: []
  superseded_by: []
  conflicts: []
---

# 用户故事拆分：个人云盘浏览、新建文件夹与移动

## 一、输入门禁

- 需求排序已采纳：`Plans/需求排序/2026-08-10-cloud-drive-browser-folder-move.md`。
- 架构方案已采纳：`Plans/技术方案/2026-08-10-cloud-drive-browser-folder-move.md`。
- 用户已明确选择三张任务并要求继续；本轮 Scope 包含全部三张卡。

## 二、纵向故事索引

| Story | 用户能力 | AC/GWT | 架构 | 依赖 | 优先级 | 点数 | Scope | 子 Plan |
|-------|----------|--------|------|------|--------|------|-------|---------|
| US-001 | 浏览、搜索和进入个人云盘目录 | 001–006/017/018 | ADR-001/002/003/006 | — | P0 | 8 | true | `...-US-001.md` |
| US-002 | 在当前目录新建文件夹 | 007–011/017/018 | ADR-002/003/004/006 | US-001 | P0 | 5 | true | `...-US-002.md` |
| US-003 | 通过目录选择器移动文件或文件夹 | 012–018 | ADR-002/003/004/005/006 | US-001, US-002 | P0 | 8 | true | `...-US-003.md` |

## 三、故事边界

- 每个 Story 同时包含 UI、Domain、Data/API adapter、失败恢复和测试，能以真实账号独立演示。
- 共享 Cloud adapter/l10n/App Shell 接线归串行集成队列，但对应故事在接线完成前不得标记完成。
- AI 文件、Workspace、上传/下载/重命名/删除不扩入三张故事。

## 四、Scope 确认

- [x] GWT-001～018 均由至少一个 Scope Story 覆盖。
- [x] 故事点采用 8/5/8，未换算工时；无 13 点故事。
- [x] `scope_confirmed: true`，依据用户已确认三张任务并在恢复后要求继续。

## 五、实现落点设计

| Story | 落点设计 | 状态 |
|-------|----------|------|
| US-001 | `Plans/功能开发/2026-08-10-cloud-drive-browser-folder-move-US-001.impl.json` | 已确认；Cloud adapter/Auth/Composition Root/l10n 已接线 |
| US-002 | `Plans/功能开发/2026-08-10-cloud-drive-browser-folder-move-US-002.impl.json` | 已确认；policy/mkdir/reconcile 与入口已接线 |
| US-003 | `Plans/功能开发/2026-08-10-cloud-drive-browser-folder-move-US-003.impl.json` | 已确认；move/list/reconcile/l10n 与入口已接线 |

写代码先按每个 JSON 的 Red 测试落点执行；Feature 实现可推进，但这些共享接线问题关闭前 Story 只能保持进行中/部分完成。

## 六、Story Development 进度

| Story | 已落地 | 未完成停止条件 | 状态 |
|-------|--------|----------------|------|
| US-001 | owner/generation 隔离、重叠搜索、分页去重、刷新保旧、目录导航与面包屑、三档浏览视图、YunPan token/signature/list/search 生产链路、App 入口与 l10n | 真实账号目录冒烟、Android 协议身份复核、五形态真机验证 | 进行中 |
| US-002 | policy 三态、single-flight、resultUnknown/reconcile、owner fence、iOS 居中弹窗、content audit/mkdir/exact-exists 生产 adapter、入口刷新与 l10n | 受控真实账号写入、真机键盘/窗口切换、五形态验证 | 进行中 |
| US-003 | 目录过滤、非法目标、single-flight、resultUnknown/reconcile、双目录失效、iOS 近全高弹层、move/list/exact-exists 生产 adapter、入口与 l10n | 受控真实账号移动冒烟、真机边缘手势/窗口切换、五形态验证 | 进行中 |

当前候选已以 `7be6420` 提交，但外部验收停止条件未关闭，三张子 Plan 均不得升级为已完成；正式任务继续保持 `PARTIAL`。

## 反馈（skill_run）

```yaml
skill_run:
  skill: task-splitter
  workflow_stage: story-split
  plan: Plans/功能开发/2026-08-10-cloud-drive-browser-folder-move.md
  date: 2026-08-10
  contexts_used:
    - path: Contexts/需求分析/需求分析规范.md
      utility: high
      reason: "按三条完整用户事件链拆为可独立演示的纵向 Story"
  contexts_missing: []
  contexts_stale: []
  outcome_status: pass
  revisit_needed: false
```

```yaml
skill_run:
  skill: feature-dev-assistant
  workflow_stage: story-development
  plan: Plans/功能开发/2026-08-10-cloud-drive-browser-folder-move.md
  date: 2026-08-10
  contexts_used:
    - path: Contexts/需求分析/需求分析规范.md
      utility: high
      reason: "从 GWT 反向补齐刷新保旧、owner fence、非法目标和结果未知恢复"
  contexts_missing: []
  contexts_stale: []
  outcome_status: partial
  friction: "生产接线已落地；受控真实账号写操作、Android 协议身份复核与五形态真机证据仍缺失"
  revisit_needed: true
```

```yaml
skill_run:
  skill: implementation-design-assistant
  workflow_stage: implementation-design
  plan: Plans/功能开发/2026-08-10-cloud-drive-browser-folder-move.md
  date: 2026-08-10
  contexts_used:
    - path: Contexts/需求分析/需求分析规范.md
      utility: high
      reason: "将已采纳 AC 落到三个纵向模块和先失败的测试位置"
  contexts_missing: []
  contexts_stale: []
  outcome_status: partial
  friction: "集成 Owner 已由用户确认并完成接线；只剩外部账号/设备验证门禁"
  revisit_needed: false
```

## 七、提交前 Code Review

### Findings-first

| 级别 | 位置 | 问题 | 结果 |
|---|---|---|---|
| 高（已关闭） | `cloud_move_controller.dart` / `personal_cloud_browser_repository_impl.dart` | 服务端或调用方的根目录外路径可进入浏览/移动链路 | 增加 root confinement 与失败回归；根外目录不展示、不发请求 |
| 高（已关闭） | `folder_creation_dialog.dart` / `cloud_move_sheet.dart` | 写请求在飞时系统返回/下拉可销毁 UI owner，丢失结果收敛 | busy 阶段用 `PopScope` 禁止退出，建目录与移动路由回归通过 |
| 中（已关闭） | `composition_root.dart` | 设备元数据 await 期间 provider 失效后仍可继续装配旧 runtime | await 后先检查 `ref.mounted`，再校验 owner snapshot |

复审结论：修改后未发现未关闭的阻塞/高优先级问题；76 项相关测试、改动范围静态分析、格式和任务 ID 门禁通过。本提交不修改 Android/iOS 原生文件，故不需要原生 reviewer；候选仍为 `PARTIAL`，未对真实账号与五形态验收给出 PASS。

```yaml
skill_run:
  skill: code-review
  workflow_stage: review
  plan: Plans/功能开发/2026-08-10-cloud-drive-browser-folder-move.md
  date: 2026-08-10
  contexts_used:
    - path: Contexts/决策/Skill原子契约.md
      utility: high
      reason: "按 Findings-first、严重级、位置和残余风险冻结提交前 diff"
  contexts_missing: []
  contexts_stale: []
  outcome_status: pass
  revisit_needed: false
```
