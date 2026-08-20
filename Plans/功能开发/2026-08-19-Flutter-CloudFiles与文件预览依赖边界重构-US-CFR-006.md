---
tags: [功能开发, 用户故事, TDD, Flutter, CloudFiles, 边界重构]
type: plan
category: 功能开发
status: 草稿
date: 2026-08-20
lifecycle_state: story-split
parent: Plans/功能开发/2026-08-19-Flutter-CloudFiles与文件预览依赖边界重构.md
story_id: US-CFR-006
story_points: 5
sprint_scope: false
---

# US-CFR-006：迁移剩余生产消费者并闭合生命周期

作为 Flutter 维护者，我要把 Main、Projects、Download 等仍消费旧 `CloudFilesRuntime` 的生产消费者迁到 App 内部能力/窄投影，并闭合 ProviderContainer 生命周期，以便旧大 Runtime 的暴露面可安全收窄，且资源最多创建/释放一次。

## 用户价值与纵向性

面向维护者与终端用户：所有仍依赖旧 Runtime 的真实生产入口都迁到新边界并端到端可运行；owner 重建 ProviderContainer 时旧资源仅释放一次、新资源仅创建一次；无任何消费者以 Fake/Contract 冒充完成。这是关闭"生产链 PARTIAL"的收口故事。

## 验收标准

- AC-09：架构需求影响矩阵中列出的旧生产消费者（Main/Projects/Download 等）逐项完成迁移落点，无遗留反向依赖；迁移完成后旧 Runtime 暴露面可删除。
- AC-08：ProviderContainer lifecycle 测试证明 Dio、download/upload platform、coordinator 最多创建/释放一次，dispose 幂等（复用并强化 US-CFR-001 基线）。
- AC-07（全量范围）：完成后对 Files/上传下载/预览做完整 diff 审查 + focused regression，协议、签名、缓存 namespace `personal-cloud`、持久化格式与 UI/文案零变化。
- 迁移过程中若任一生产行为回归，回滚该结构提交，状态保持 PARTIAL，不改协议/清缓存绕过。

## 故事边界

含：迁移 `lib/app/projects_runtime.dart`、`projects_workspace.dart`、Main 启动链、`features/files/download/**` 等对旧 Runtime 的引用；收窄旧 `cloud_files_runtime.dart` 暴露面；生命周期总测试。
不含：新增功能、动协议/缓存；文档与门禁固化留 US-CFR-007。

### 现状证据（迁移面，落点阶段细化）

- App 侧消费者：`lib/app/projects_runtime.dart`、`lib/app/projects_workspace.dart`、`lib/app/composition/file_download_providers.dart`、启动链 `lib/app/startup/**`。
- 旧 Runtime 暴露面：`lib/app/cloud_files_runtime.dart`（US-CFR-003 拆分后残留的兼容面）。

## 架构引用

- `Plans/技术方案/2026-08-19-Flutter-CloudFiles与文件预览依赖边界重构.md#ADR-CFR-003`
- `Plans/技术方案/2026-08-19-Flutter-CloudFiles与文件预览依赖边界重构.md#ADR-CFR-005`
- `Plans/技术方案/2026-08-19-Flutter-CloudFiles与文件预览依赖边界重构.md#ADR-CFR-006`
- 技术方案 §十一 需求影响矩阵 CFR-006、§十三 顺序 6「迁移 Main/Projects/Download 等消费者」。

## 依赖

US-CFR-003、US-CFR-004、US-CFR-005。

## 续做

```text
/resume plan=Plans/功能开发/2026-08-19-Flutter-CloudFiles与文件预览依赖边界重构.md 进度=implementation-design US-CFR-006
```
