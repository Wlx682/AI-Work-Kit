---
tags: [功能开发, 用户故事, TDD, Flutter, CloudFiles, 边界重构]
type: plan
category: 功能开发
status: 已完成
date: 2026-08-20
lifecycle_state: story-development
parent: Plans/功能开发/2026-08-19-Flutter-CloudFiles与文件预览依赖边界重构.md
story_id: US-CFR-004
story_points: 8
sprint_scope: false
implementation_design: Plans/功能开发/2026-08-19-Flutter-CloudFiles与文件预览依赖边界重构-US-CFR-004.impl.json
tdd_evidence: Plans/功能开发/2026-08-19-Flutter-CloudFiles与文件预览依赖边界重构-US-CFR-004.tdd.json
---

# US-CFR-004：Files 页面消费 Host 注入的窄依赖并去 app import

作为终端用户，我要在 Files 页面浏览云盘目录与 Workspace 文件，且页面与 AI Files 控制器只消费 `FilesDestination` 注入的 Feature 窄依赖（runtime state、领域 Repository、Gateway lease、Host actions），以便 `features/files/**` 对 `app/**` 的 import 归零，而浏览行为与重构前完全一致。

## 用户价值与纵向性

面向终端用户的浏览能力端到端保持可用：从 Host 注入依赖 → 页面/控制器消费 → Repository 加载目录 → owner lease 复核 → UI 更新。改造后 Feature 不再 import 任何 App 符号，真实生产页面入口闭合（不是用 Fake 替代）。

## 验收标准

- AC-01：`features/files/**` 对 `app/**` 的 import = 0；US-CFR-001 边界探针在 Files feature 上全绿。
- AC-04：`FilesDestination` 成为唯一生产注入点，Files dependency slots 全部由 Host 覆盖；页面/控制器不再 `ref.read(clawApiProvider)`、不再直接持有 `ActiveGatewayRuntimeIdentity` 作为 App Provider 读取来源，而是消费注入的 Feature Gateway lease 与 Repository。
- `CloudBrowserController` 的连接恢复下沉到 Repository/DataSource，Controller 只消费 Feature lease。
- 目录/列表加载、搜索、取消、owner 切换行为与重构前一致（复用 US-CFR-001 回归）。

## 故事边界

含：`FilesDestination` 投影注入 Feature 依赖槽；改写 `files_page.dart`、`cloud_browser_controller.dart`、`cloud_drive_sdk.dart` 去除 `app/**` import；Files dependency slot Provider 定义在 Feature 并 fail-fast 默认实现；生产调用链/Widget 测试闭合真实入口。
不含：预览/下载改 typed port（US-CFR-005，本故事预览可暂经既有注入通道过渡但不得重新引入 app import）、迁移非 Files 外部消费者（US-CFR-006）。

### 现状证据

- `lib/features/files/presentation/files_page.dart:6-9` import 4 个 `app/**` 符号。
- `lib/features/files/ai_files/browser/application/cloud_browser_controller.dart:3` import root，`:155` `ref.read(clawApiProvider)`，多处持有 `ActiveGatewayRuntimeIdentity`。
- `lib/features/files/ai_files/sdk/cloud_drive_sdk.dart:3,9` import root 且 `ref.watch(clawApiProvider)`。
- 注入宿主 `lib/app/integrations/files_destination.dart`。

## 架构引用

- `Plans/技术方案/2026-08-19-Flutter-CloudFiles与文件预览依赖边界重构.md#ADR-CFR-002`
- `Plans/技术方案/2026-08-19-Flutter-CloudFiles与文件预览依赖边界重构.md#ADR-CFR-004`
- 技术方案 §4.3 Provider 归属规则、§4.5 Gateway/AI/Workspace 边界、§八 关键流程时序。

## 依赖

US-CFR-003（需要 Feature Runtime 投影可注入）。

## TDD 结果（2026-08-21）

- Red：clean boundary 精确锁定 Files→App 6 条 import；dependency slots 与 SDK preparation 因契约尚不存在而编译失败。
- Green：新增 Files dependency scope 与 route owner feeds，`FilesDestination` 成为真实生产注入点；FilesPage、Controller、SDK 均只消费 Feature identity/lease/repository，Files→App import 清零。
- Refactor：Gateway 连接准备进入 SDK/DataSource，notifier 声明 scoped dependencies；Overlay 目录通过无凭证 owner feed 在 runtime/lease 换代时取消旧预览并关闭旧目录/菜单。
- 回归：FilesPage 57/57、边界/slot/SDK/生产注入/owner/preview/runtime 31/31、下载与 Feature Runtime 30/30 全部 PASS；scoped analyze、task-ID naming 与 diff check PASS。
- NOT_RUN：Android/iOS 真网络与支付设备围栏留待 Epic 里程碑矩阵；本 Story 未改 HTTP/签名、支付或原生插件。

AC-01、AC-04：**PASS**。机器证据见 `…-US-CFR-004.tdd.json`。

## 实现落点设计

- 新建 `lib/features/files/files_dependency_scope.dart`，集中声明 `FilesRuntimeState<T>`、`FilesGatewayLease` 以及 runtime/lease/CloudDrive Repository/Workspace Repository/附件能力/retry slots；默认只能显式 unavailable 或以 `files_dependency_not_installed` fail-fast，禁止创建 App/Fake 运行时。
- `lib/app/composition/files_providers.dart` 负责真实投影和 concrete builder：把 `CloudFilesAppRuntime` 映射为缓存稳定的 `FilesRuntimeState<CloudFilesFeatureRuntime>`，把 `ActiveGatewayRuntimeIdentity` 映射为 `FilesGatewayLease`，并用真实 `ClawApi` 构造 CloudDrive/Workspace Repository。`FilesDestination` 再以子 `ProviderScope` 覆盖全部 Feature slots，成为唯一生产注入点。
- `files_page.dart` 只消费 `CloudFilesFeatureRuntime`、`FilesGatewayLease` 与 Feature slots；现有 constructor callback 继续作为 US-CFR-004 的过渡注入 seam，但 Cloud 动作只传 `CloudFilesRuntimeIdentity`，AI/Workspace 动作只传 `FilesGatewayLease`，不再把 `CloudFilesAppRuntime` / `ActiveGatewayRuntimeIdentity` / Provider 传回 Feature。正式聚合 `FilesHostActions` typed port 留 US-CFR-005。
- `cloud_browser_controller.dart` 删除 `clawApiProvider` 与 App identity 读取，保留本地 generation、item identity 和 lease 复核；连接准备下沉到 `FilesystemCloudDriveSdk`，沿用 Workspace DataSource 的 injected preparation 模式覆盖全部读写调用。
- App 侧 preview launcher 改读 `appCloudDriveRepositoryProvider`，因此 Projects/attachment 等非 Files 消费者无需进入 Files 子 Scope；其正式迁移仍留 US-CFR-006。平台预览、下载、上传插件继续和 UI 处于同一 App 产品入口，但实现不下沉 Files Feature。
- Red 先锁 6 条 Files→App 债务、dependency slot 默认与 `FilesDestination` 逐槽覆盖、SDK preparation，再复用页面/Controller 的目录、搜索、取消、分页和 owner 换代回归。

机器可读细节见 `Plans/功能开发/2026-08-19-Flutter-CloudFiles与文件预览依赖边界重构-US-CFR-004.impl.json`。

## 续做

```text
/resume plan=Plans/功能开发/2026-08-19-Flutter-CloudFiles与文件预览依赖边界重构.md 进度=implementation-design US-CFR-005
```

## 反馈（skill_run）

```yaml
skill_run:
  skill: resume-assistant
  workflow_stage: implementation-design
  plan: Plans/功能开发/2026-08-19-Flutter-CloudFiles与文件预览依赖边界重构-US-CFR-004.md
  date: 2026-08-21
  contexts_used:
    - path: Plans/Epic/2026-08-19-Flutter-CloudFiles与文件预览依赖边界重构.md
      utility: high
      reason: "回放当前滚动 Scope 与前置 Story 完成事实，确认只补 US-CFR-004 的 implementation-design"
    - path: Plans/功能开发/2026-08-19-Flutter-CloudFiles与文件预览依赖边界重构.md
      utility: high
      reason: "依据主 Plan 的 Story/AC 矩阵与当前阶段恢复，不重做 US-CFR-001..003"
    - path: Contexts/决策/Skill反馈协议.md
      utility: high
      reason: "按续作协议记录当前阶段、上下文和下一 story-development 恢复点"
  contexts_missing: []
  contexts_stale: []
  outcome_status: pass
  friction: "Flutter 工作树累积前置 Story 未提交改动，落点设计需按路径隔离且本轮不触碰生产代码"
  revisit_needed: false
```

```yaml
skill_run:
  skill: implementation-design-assistant
  workflow_stage: implementation-design
  plan: Plans/功能开发/2026-08-19-Flutter-CloudFiles与文件预览依赖边界重构-US-CFR-004.md
  date: 2026-08-21
  contexts_used:
    - path: Plans/技术方案/2026-08-19-Flutter-CloudFiles与文件预览依赖边界重构.md
      utility: high
      reason: "依据 ADR-CFR-002/004 与 §4.3/4.5 锁定 Feature slots、Host 注入、Gateway lease 和连接恢复方向"
    - path: Plans/功能开发/2026-08-19-Flutter-CloudFiles与文件预览依赖边界重构-US-CFR-004.impl.json
      utility: high
      reason: "固化真实目标文件、依赖规则、Red 位置、平台边界和不跨 US-CFR-005/006 的风险围栏"
    - path: Contexts/决策/Skill反馈协议.md
      utility: high
      reason: "保证最后 skill_run 精确对应 implementation-design 机械门禁"
  contexts_missing: []
  contexts_stale: []
  outcome_status: pass
  friction: "既要让 Files callback 不再携带 App runtime，又不能提前建立 US-CFR-005 的正式 typed port；以窄 identity/lease callback seam 分阶段闭合"
  revisit_needed: false
```

```yaml
skill_run:
  skill: resume-assistant
  workflow_stage: story-development
  plan: Plans/功能开发/2026-08-19-Flutter-CloudFiles与文件预览依赖边界重构-US-CFR-004.md
  date: 2026-08-21
  contexts_used:
    - path: Plans/Epic/2026-08-19-Flutter-CloudFiles与文件预览依赖边界重构.md
      utility: high
      reason: "回放当前滚动 Scope 与 workflow gate，确认 US-CFR-004 是唯一未完成 Story"
    - path: Plans/功能开发/2026-08-19-Flutter-CloudFiles与文件预览依赖边界重构-US-CFR-004.impl.json
      utility: high
      reason: "按已确认落点恢复 Red→Green→Refactor，不提前聚合 US-CFR-005 typed host actions"
    - path: Contexts/决策/Skill反馈协议.md
      utility: high
      reason: "记录续作阶段、真实测试证据和下一 implementation-design 恢复点"
  contexts_missing: []
  contexts_stale: []
  outcome_status: pass
  friction: "Flutter 工作树累积 US-CFR-001..003 未提交改动，需以专用 tdd_evidence、聚焦路径与 base_commit 隔离本 Story"
  revisit_needed: false
```

```yaml
skill_run:
  skill: feature-dev-assistant
  workflow_stage: story-development
  plan: Plans/功能开发/2026-08-19-Flutter-CloudFiles与文件预览依赖边界重构-US-CFR-004.md
  date: 2026-08-21
  contexts_used:
    - path: Plans/功能开发/2026-08-19-Flutter-CloudFiles与文件预览依赖边界重构-US-CFR-004.impl.json
      utility: high
      reason: "按机器落点完成 Feature slots、App production injection、SDK preparation 与 Files 零 App import"
    - path: Plans/功能开发/2026-08-19-Flutter-CloudFiles与文件预览依赖边界重构-US-CFR-004.tdd.json
      utility: high
      reason: "固化 Red/Green/Refactor、AC-01/04、57 项页面回归、owner feed 与 NOT_RUN 设备围栏"
    - path: Contexts/决策/Skill反馈协议.md
      utility: high
      reason: "保证 Story 最后 skill_run 精确对应 story-development 机械门禁"
  contexts_missing: []
  contexts_stale: []
  outcome_status: pass
  friction: "ProviderScope 不会穿过根 Navigator Overlay；以 Host 持有的无凭证 route owner feed 传播换代并关闭旧路由，避免复用同一 ProviderContainer"
  revisit_needed: false
```
