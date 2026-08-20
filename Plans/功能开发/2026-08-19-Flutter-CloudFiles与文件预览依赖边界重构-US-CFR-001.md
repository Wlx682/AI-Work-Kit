---
tags: [功能开发, 用户故事, TDD, Flutter, CloudFiles, 边界重构]
type: plan
category: 功能开发
status: 进行中
date: 2026-08-20
lifecycle_state: implementation-design
parent: Plans/功能开发/2026-08-19-Flutter-CloudFiles与文件预览依赖边界重构.md
story_id: US-CFR-001
story_points: 5
sprint_scope: true
---

# US-CFR-001：边界与行为不变量回归网（先红后绿基线）

作为 Flutter 维护者与测试人员，我要先建立**依赖边界断言**与**行为不变量回归网**，以便后续每一步重构都有可回退的红/绿基线，任一步引入行为回退都能立即被捕获。

## 用户价值与纵向性

一次交付一个可运行、可验收的能力：一套自动测试。运行后能同时给出两类信号——
- **红**：`features/files/** → app/**`、`app/composition/** → composition_root.dart` 的当前违规被明确列出（证明债务存在，后续故事逐一转绿）。
- **绿**：owner 切换迟到结果隔离、ProviderContainer 生命周期、云文件预览/上传下载在**当前生产代码**上的行为回归全部通过（作为无行为变更基线）。

本故事不改任何生产代码，只新增测试与测试脚手架。

## 验收标准

- AC-06：owner 切换、迟到结果、取消的**当前行为**由回归用例锁定并通过（基线绿）。
- AC-08：ProviderContainer 生命周期（Dio/download/upload platform/coordinator 最多创建/释放一次）由 lifecycle 测试锁定并通过（基线绿）。
- 边界探针：`features/files/** → app/**` 与 `app/composition/** → composition_root.dart` 的非法 import 探测用例存在，能输出非法路径清单；在当前代码上按预期为红（记录为已知违规基线，不作为本故事阻断）。
- 运行不新增网络请求、缓存层或重复 runtime。

## 故事边界

含：静态 import 边界断言（基于源码扫描）、owner fencing 与生命周期的聚焦回归、既有 CloudFiles/Preview 测试的补齐与归拢。
不含：删除或改写任何 `import`、拆分 Runtime、迁移消费者——这些留给 US-CFR-002..006。

### 现状证据（Red 目标锚点）

- `lib/features/files/presentation/files_page.dart` import `app/composition_root.dart`、`app/composition/files_providers.dart`、`app/composition/cloud_files_providers.dart`、`app/cloud_files_runtime.dart`。
- `lib/features/files/ai_files/browser/application/cloud_browser_controller.dart`、`lib/features/files/ai_files/sdk/cloud_drive_sdk.dart` import `app/composition_root.dart` 并读取 `clawApiProvider` / `ActiveGatewayRuntimeIdentity`。
- `lib/app/composition/{files_providers,file_download_providers,cloud_files_providers,app_file_preview_providers}.dart` 反向 import `../composition_root.dart`。

## 当前进度（2026-08-20）

- 已完成前置事实盘点：确认现有 CloudFiles/Preview 生产链、owner 围栏与既有测试均作为绿基线保留。
- 已确认两组待转绿的静态依赖：Feature → App 与 composition module → root。
- 尚未创建 `implementation_design` JSON，尚未新增本 Story 的边界探针和生命周期回归；因此当前状态为“实现落点设计中”，不是 TDD 开发中或已完成。
- 下一步只做落点设计：明确新增/复用的测试文件、源码扫描规则、已知 Red 表达方式和不变量绿基线，不修改生产代码。

## 架构引用

- `Plans/技术方案/2026-08-19-Flutter-CloudFiles与文件预览依赖边界重构.md#ADR-CFR-001`
- 技术方案 §九「依赖可维护性 / 并发 / 生命周期」验证方式、§十三 顺序 1「锁定 import、行为与生命周期回归」。

## 依赖

无（首个滚动 Scope）。

## 反馈（skill_run）

```yaml
skill_run:
  skill: resume-assistant
  plan: Plans/功能开发/2026-08-19-Flutter-CloudFiles与文件预览依赖边界重构-US-CFR-001.md
  date: 2026-08-20
  contexts_used:
    - path: Contexts/决策/2026-08-20-开发流程审计报告.md
      utility: high
      reason: "使用提交、生产依赖和门禁复核结果更新当前 Story 的真实起点与未完成边界"
    - path: Plans/Epic/2026-08-19-Flutter-CloudFiles与文件预览依赖边界重构.md
      utility: high
      reason: "确认 US-CFR-001 是当前滚动 Scope，且 Epic 当前阶段为 implementation-design"
  contexts_missing: []
  contexts_stale: []
  outcome_status: partial
  friction: "缺少 US-CFR-001 implementation_design JSON，尚不能进入逐故事 TDD"
  revisit_needed: false
```

## 续做

```text
/resume plan=Plans/功能开发/2026-08-19-Flutter-CloudFiles与文件预览依赖边界重构.md 进度=implementation-design US-CFR-001
```
