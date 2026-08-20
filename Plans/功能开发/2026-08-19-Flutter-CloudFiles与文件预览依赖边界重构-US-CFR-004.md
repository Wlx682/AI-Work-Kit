---
tags: [功能开发, 用户故事, TDD, Flutter, CloudFiles, 边界重构]
type: plan
category: 功能开发
status: 草稿
date: 2026-08-20
lifecycle_state: story-split
parent: Plans/功能开发/2026-08-19-Flutter-CloudFiles与文件预览依赖边界重构.md
story_id: US-CFR-004
story_points: 8
sprint_scope: false
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

## 续做

```text
/resume plan=Plans/功能开发/2026-08-19-Flutter-CloudFiles与文件预览依赖边界重构.md 进度=implementation-design US-CFR-004
```
