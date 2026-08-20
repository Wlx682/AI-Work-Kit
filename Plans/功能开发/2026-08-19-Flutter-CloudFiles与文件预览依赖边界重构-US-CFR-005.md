---
tags: [功能开发, 用户故事, TDD, Flutter, CloudFiles, 文件预览, 边界重构]
type: plan
category: 功能开发
status: 草稿
date: 2026-08-20
lifecycle_state: story-split
parent: Plans/功能开发/2026-08-19-Flutter-CloudFiles与文件预览依赖边界重构.md
story_id: US-CFR-005
story_points: 5
sprint_scope: false
---

# US-CFR-005：预览/传输 typed host actions

作为终端用户，我要预览与下载云盘、Workspace、AI 文件，且预览/下载/上传/分享由 App 侧 `FilesHostActions` 以 typed item + expected identity/generation 执行，Feature 只发意图、不接触具体 Runtime，以便系统预览的平台选择、缓存与取消/失败恢复行为保持不变。

## 用户价值与纵向性

面向终端用户的预览/传输能力端到端可用：Feature 发 typed intent → Host 读取当前 `CloudFilesAppRuntime` 并复核 identity → 用 App 内部实现打开预览/执行下载 → 返回既有结果。改造后回调参数不再出现 `CloudFilesAppRuntime`/`Ref`/Provider，且 iOS/Android 预览行为零差异。

## 验收标准

- AC-05：预览、下载、分享、上传实现留在 App；Feature 仅依赖 `FilePreviewPort` / `FilesHostActions` typed 契约；contract + adapter 定向测试通过。
- AC-07（预览/传输范围）：iOS/Android 平台预览选择、download/cache/external-open 降级链、cancellation 与失败恢复与重构前一致；协议、签名、缓存 namespace 无变化，diff 审查 + focused regression 通过。
- 每个 host action 执行前与异步返回后都复核 expected identity/generation；owner 切换期间旧预览/下载不借新凭据续跑（AC-06 迟到隔离在预览路径成立）。
- Preview source 无法解析时显式失败，不回退到错误 source 或伪成功。

## 故事边界

含：把预览/下载/上传/分享改为 App 实现的 typed host actions；Feature 侧 `FilePreviewSource`/`FilePreviewPort` 契约与 fake 测试；Host 执行处的 identity 复核。
不含：拆 Runtime 本体（US-CFR-003 已完成）、迁移 Projects/Download 等外部消费者与生命周期总闭合（US-CFR-006）。

### 现状证据

- 预览装配 `lib/app/composition/app_file_preview_providers.dart`、`lib/app/composition/file_download_providers.dart`。
- 预览下载消费方 `lib/features/files/download/**`、`lib/features/files/presentation/files_page.dart`（现持 `ActiveGatewayRuntimeIdentity expectedIdentity` 参数，改造为 typed host action）。

## 架构引用

- `Plans/技术方案/2026-08-19-Flutter-CloudFiles与文件预览依赖边界重构.md#ADR-CFR-004`
- 技术方案 §7.3 Host actions、§7.4 内部错误码、§十三 顺序 5「Preview/Transfer typed actions」。

## 依赖

US-CFR-003、US-CFR-004。

## 续做

```text
/resume plan=Plans/功能开发/2026-08-19-Flutter-CloudFiles与文件预览依赖边界重构.md 进度=implementation-design US-CFR-005
```
