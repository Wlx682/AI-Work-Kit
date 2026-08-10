---
tags: [工作流, merge-code]
type: plan
category: 代码重构
status: 已采纳
p0_open: 0
date: 2026-08-10
workflow: merge-code
workflow_stage: intent-analysis
task_id: merge-code-2026-08-10-提交-Files-Workspace-migration
task_title: 提交 Files Workspace migration
skill: merge-code-assistant
---

# 双边代码意图与业务冲突分析：提交 Files Workspace migration

**工作流**：`merge-code`
**阶段**：`intent-analysis` / 双边代码意图与业务冲突分析
**推荐 Skill**：`merge-code-assistant`
**存放路径**：`Plans/代码重构/2026-08-10-合并意图分析-提交-Files-Workspace-migration.md`

---

## 一、输入

- 来源：用户要求提交当前 Files / User Upload / AI Files / Workspace 迁移实现，并在需要时解决与最新 `origin/dev` 的冲突。
- 范围：分析 `origin/dev@27da2c1` 的 41 个上游提交与本地 `dev@c5190de` 上尚未提交的 Files 迁移，确定共同路径的合并语义和组合验证。
- 非目标：不 rebase、不 squash、不 force push、不自动 push，不改变已确认的 Files 产品裁决。

## 二、阶段产出

- [x] 双边代码意图
- [x] 业务冲突矩阵
- [x] 开发者决策清单
- [x] 合并策略与验证映射


## 双边代码意图

| 意图ID | 分支侧 | 文件/模块 | 代码变化 | 业务目标 | 行为/规则变化 | 证据 | 置信度 |
|--------|--------|-----------|----------|----------|---------------|------|--------|
| SI-001 | 源分支 | App composition、navigation、l10n、theme、`pubspec.yaml` | 上游 41 个提交扩展首页、Skills 市场、Mine、Legal、Markdown、认证与应用壳接线 | 保留 `dev` 已交付的非 Files 产品能力 | 新增页面、依赖、文案与壳层 provider，不得被本地 Files 改动覆盖 | `git log c5190de..origin/dev`；17 个共同路径清单 | 高 |
| SI-002 | 源分支 | Personal Cloud controller/repository、Gateway API/Fake、对应测试 | 上游包含个人云盘与共享 Gateway 契约的持续演进 | 保持远端调用方和既有个人云盘行为可用 | 公共 API、Fake 和 owner 生命周期不能因合并丢失 | `git diff --name-only c5190de..origin/dev`；共同路径中的 cloud/Gateway 测试 | 高 |
| TI-001 | 目标分支 | `features/cloud_drive/**`、Files assets、design-system components | 新增用户上传、AI 文件、工作空间三 Tab，独立目录路由、面包屑、文件菜单及 iOS/Figma 视觉收敛 | 完成 Files Tab 迁移并与固定 iOS 行为一致 | 文件夹以新页面打开；菜单、面包屑、失败恢复和自适应布局按最终裁决工作 | 当前工作树；Files/Workspace 定向回归 218/218 | 高 |
| TI-002 | 目标分支 | Personal Cloud network/signing/bootstrap/mutations | 接通签名 token、真实列表、目录 bootstrap、移动/重命名/删除，并增加 owner 与不确定结果围栏 | 用户上传真实数据可用且写操作不重复、不跨账号 | 平台身份 fail-closed；mutation outcomeUnknown 先对账；旧 owner 结果不得覆盖当前状态 | `dio_personal_cloud_client_test.dart`、`personal_cloud_repository_adapters_test.dart`、runtime owner tests | 高 |
| TI-003 | 目标分支 | `features/workspace/**`、filesystem Gateway/catalog/runtime | 接入 canonical `filesystem.ws.*` 浏览与搜索、typed mixed result、分页和 owner 生命周期 | Workspace 能分层浏览、搜索并在账号/Gateway 更换时隔离数据 | 空查询走 list，搜索走 ws.search；严格 codec；迟到响应丢弃 | Workspace repository/controller/view tests、Gateway wire tests | 高 |
| TI-004 | 目标分支 | App shell、theme、l10n、composition root | 将 Files 入口、白色 SafeArea、动态提示和生产 providers 接入应用 | Files 功能可从真实 App 壳进入且视觉/本地化一致 | Files destination 白底；其他 destination 保持主题默认；三语言生成物包含新增文案 | app shell/theme/l10n tests、页面集成测试 | 高 |

## 业务冲突矩阵

| 冲突ID | 关联意图 | 冲突类型 | 业务影响 | AI结论 | 需开发者决策 | 决策ID |
|--------|----------|----------|----------|--------|----------------|--------|
| MC-001 | SI-001, TI-001, TI-004 | 公共依赖、跨模块组合 | composition、navigation、l10n、theme 与 pubspec 若选单边会丢失远端页面或 Files 入口 | 可证明兼容：采用并集，保留远端新增产品能力，同时接入本地 Files providers/routes/keys；最终 ARB 合并后重生本地化生成物 | 否 | 无 |
| MC-002 | SI-002, TI-002 | 状态机、数据不变量、幂等并发 | Personal Cloud 共同代码若误覆盖会导致真实列表失败、重复 mutation 或跨 owner 陈旧数据 | 可证明兼容：保留远端公共契约增量，并以本地经过 iOS 源码和回归验证的 owner fence、single-flight、reconcile 规则作为更严格不变量 | 否 | 无 |
| MC-003 | SI-001, SI-002, TI-003, TI-004 | API/事件契约、公共依赖 | Gateway catalog/Fake/composition 合并不完整会使 Workspace RPC 不可调用或破坏远端调用方 | 可证明兼容：公共 RPC/catalog/Fake 取并集，保持旧签名兼容；用 wire、contract、Workspace 分页/搜索测试验证组合 | 否 | 无 |

## 开发者决策清单

| 决策ID | 待决策问题 | 可选方案及影响 | 开发者结论 | 决策人 | 确认记录 | 状态 |
|--------|------------|----------------|------------|--------|----------|------|
| 无 | 无不可证明的业务规则冲突 | 双方能力可通过公共 API 并集及更严格 owner/codec 不变量组合 | 无需决策 | AI 依据代码与测试证据判定 | 2026-08-10 合并意图分析 | 无需决策 |

## 合并策略与验证映射

| 冲突ID | 处理策略 | 影响范围 | 验证场景 | 状态 |
|--------|----------|----------|----------|------|
| MC-001 | App composition/navigation/pubspec 逐项取并集；ARB 先合并事实源再生成 Dart l10n | App 壳、Files 入口、远端新页面、本地化 | 运行 app shell、theme、Files 页面集成及 l10n analyze，确认 Files 与远端 destination 均可构建 | 已规划 |
| MC-002 | 手工合并 Personal Cloud，共享新增 API 保留，本地 owner/single-flight/reconcile 不变量不降级 | 用户上传读取与写操作 | 运行 token/Dio/repository/controller/runtime owner/deletion/rename 定向测试 | 已规划 |
| MC-003 | Gateway RPC/catalog/Fake 采用兼容并集，逐个修复调用方而非选择单边 | Workspace browse/search/pagination 与共享 Gateway | 运行 Gateway contract/wire/self-test 与 Workspace repository/controller/view 测试 | 已规划 |

## 三、完成门禁

- `childPlanExists`: True
- `status`: ['已采纳']
- `sectionsPresent`: True
- `mergeAnalysis`: True
- `skillRun`: True

> 完成阶段工作后，在本 plan 末尾追加 `skill_run`，再运行 `bash scripts/workflow-gate.sh --workflow merge-code --json`。

## 四、续做

```text
/resume plan=Plans/代码重构/2026-08-10-合并意图分析-提交-Files-Workspace-migration.md 进度=【当前完成情况】
```

## 反馈（skill_run）

```yaml
skill_run:
  skill: merge-code-assistant
  plan: Plans/代码重构/2026-08-10-合并意图分析-提交-Files-Workspace-migration.md
  date: 2026-08-10
  contexts_used:
    - path: Contexts/决策/Skill原子契约.md
      utility: high
      reason: 用原子产物和可验证门禁约束双边意图、冲突矩阵与验证映射
  contexts_missing: []
  contexts_stale: []
  outcome_status: pass
  revisit_needed: false
```
