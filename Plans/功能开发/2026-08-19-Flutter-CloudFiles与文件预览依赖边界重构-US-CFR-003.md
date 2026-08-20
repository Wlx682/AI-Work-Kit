---
tags: [功能开发, 用户故事, TDD, Flutter, CloudFiles, 边界重构]
type: plan
category: 功能开发
status: 草稿
date: 2026-08-20
lifecycle_state: story-split
parent: Plans/功能开发/2026-08-19-Flutter-CloudFiles与文件预览依赖边界重构.md
story_id: US-CFR-003
story_points: 8
sprint_scope: false
---

# US-CFR-003：分离 CloudFilesAppRuntime 与 CloudFilesFeatureRuntime

作为 Flutter 维护者，我要把当前混为一体的 `CloudFilesRuntime` 拆成 App 私有运行时 `CloudFilesAppRuntime` 与 Feature 可见投影 `CloudFilesFeatureRuntime`，SessionSnapshot 留 App 私有，以便网络/鉴权/签名/平台实现不再泄漏给 Feature，同时 owner 围栏语义保持不变。

## 用户价值与纵向性

交付一个可验收的运行时边界：App 侧完整实现（Dio、AuthSession、签名、token、上传下载、preview coordinator、缓存）与 Feature 侧投影（identity、domain owners、领域 Repository）在类型上分离且各自装配、运行、被测试。生产链在拆分后端到端仍可运行、owner 切换行为不变。

## 验收标准

- AC-03：`CloudFilesFeatureRuntime` 类型字段不含 `CloudFileClient`/`SignedHttpClient`/context factory、`AuthSession`/token/签名材料、`NamiCloudUploadPlatform`/download platform、`AppFilePreviewCoordinator`/platform previewer、`Ref`/`WidgetRef`/App Provider；字段可见性由类型字段测试锁定。
- AC-06：拆分后 owner identity/generation/lease 围栏语义与迟到结果隔离与拆分前一致，由 CloudFiles runtime provider 与 owner fencing 回归证明（复用 US-CFR-001 基线，不得削弱）。
- `CloudFilesSessionSnapshot`（environment/generation/AuthSession）保持 App 私有，不进入 Feature。
- 生命周期不变：runtime 创建/释放次数与拆分前一致。

## 故事边界

含：`lib/app/cloud_files_runtime.dart` 拆分为 App 运行时 + Feature 投影 + App 私有 session snapshot；对应 composition 装配调整；Runtime 字段边界与 owner fence 测试。
不含：改 `features/files/**` 消费方式与 import（US-CFR-004）、把预览改成 typed port（US-CFR-005）、迁移 Main/Projects 等外部消费者（US-CFR-006）。类型后缀可按职责在落点阶段选 `Runtime`/`Scope`，但字段边界不得放宽。

### 现状证据

- `lib/app/cloud_files_runtime.dart`（单一 Runtime 同时持有 App 装配对象与 Feature 消费对象）。
- 装配入口 `lib/app/composition/cloud_files_providers.dart`。

## 架构引用

- `Plans/技术方案/2026-08-19-Flutter-CloudFiles与文件预览依赖边界重构.md#ADR-CFR-001`
- `Plans/技术方案/2026-08-19-Flutter-CloudFiles与文件预览依赖边界重构.md#ADR-CFR-003`
- 技术方案 §4.4 Runtime 拆分 class 图、§7.1 Feature Runtime schema、§六 状态机。

## 依赖

US-CFR-001、US-CFR-002。

## 续做

```text
/resume plan=Plans/功能开发/2026-08-19-Flutter-CloudFiles与文件预览依赖边界重构.md 进度=implementation-design US-CFR-003
```
