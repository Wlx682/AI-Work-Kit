---
tags: [功能开发, 用户故事, TDD, Flutter, CloudFiles, 边界重构]
type: plan
category: 功能开发
status: 已完成
date: 2026-08-20
lifecycle_state: story-development
parent: Plans/功能开发/2026-08-19-Flutter-CloudFiles与文件预览依赖边界重构.md
story_id: US-CFR-001
story_points: 5
sprint_scope: false
implementation_design: Plans/功能开发/2026-08-19-Flutter-CloudFiles与文件预览依赖边界重构-US-CFR-001.impl.json
tdd_evidence: Plans/功能开发/2026-08-19-Flutter-CloudFiles与文件预览依赖边界重构-US-CFR-001.tdd.json
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

## 实际结果（2026-08-21）

- 已完成前置事实盘点：确认现有 CloudFiles/Preview 生产链、owner 围栏与既有测试均作为绿基线保留。
- 已确认两组待转绿的静态依赖：Feature → App 与 composition module → root。
- 已完成 `implementation_design`：边界探针落在现有 App boundary test + `test/support`，生命周期分别落在 CloudFiles/Preview Provider 测试；既有 Files/owner 集成用例作为绿基线复用。
- Red 表达固定为显式 `CFR_BOUNDARY_EXPECT_CLEAN=true` 命令；默认测试精确锁定并输出当前债务，避免把普通提交永久留红。
- 严格 clean 模式真实 Red：退出码 1，输出 6 条 Files→App 与 8 条 composition→root 违规。
- 默认债务快照、CloudFiles/Preview lifecycle 回归 `14/14 PASS`；owner fencing `1/1 PASS`；Files owner/preview smoke `3/3 PASS`。
- scoped analyze、impact selector（`unresolved_impacts=[]`）、task-ID naming 与 diff check 通过；本 Story 只修改 `test/**`，生产代码未变。
- Files 全文件额外运行时 56 个业务用例通过，唯一失败为既有 Figma Golden `0.11% / 327 px`，未更新基线。

## 实现落点设计

机器契约：`Plans/功能开发/2026-08-19-Flutter-CloudFiles与文件预览依赖边界重构-US-CFR-001.impl.json`。

- 新建 `test/support/source_import_boundary_probe.dart`，统一解析 package 与相对 import。
- 修改 `test/app/app_composition_boundary_test.dart`，提供默认债务快照与显式 clean Red 两种运行模式。
- 修改 CloudFiles/Preview Provider 测试，锁定同 owner 单实例、换代后旧 guard 失效及 ProviderContainer 生命周期。
- 复用 Files 页面与 environment owner 既有回归，不复制大体量 Widget/网络 Fake。

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

```yaml
skill_run:
  skill: feature-dev-assistant
  workflow_stage: story-development
  plan: Plans/功能开发/2026-08-19-Flutter-CloudFiles与文件预览依赖边界重构-US-CFR-001.md
  date: 2026-08-21
  contexts_used:
    - path: Plans/功能开发/2026-08-19-Flutter-CloudFiles与文件预览依赖边界重构-US-CFR-001.impl.json
      utility: high
      reason: "按已确认的 test-only 落点实现显式 Red、默认债务快照与 Provider 生命周期回归，没有提前修改生产依赖"
    - path: Plans/技术方案/2026-08-19-Flutter-CloudFiles与文件预览依赖边界重构.md
      utility: high
      reason: "用 ADR-CFR-001 和 owner/lifecycle NFR 校准静态边界与换代验收语义"
    - path: Contexts/决策/Skill反馈协议.md
      utility: high
      reason: "将 Red/Green/Refactor/Smoke 和已知 Golden 缺口写入可聚合反馈"
  contexts_missing: []
  contexts_stale: []
  outcome_status: pass
  friction: "并发 Flutter 命令会争用 iOS ephemeral；后续同工作树 Flutter 工具调用应串行"
  revisit_needed: false
```

```yaml
skill_run:
  skill: implementation-design-assistant
  workflow_stage: implementation-design
  plan: Plans/功能开发/2026-08-19-Flutter-CloudFiles与文件预览依赖边界重构-US-CFR-001.md
  date: 2026-08-21
  contexts_used:
    - path: Plans/技术方案/2026-08-19-Flutter-CloudFiles与文件预览依赖边界重构.md
      utility: high
      reason: "按 ADR-CFR-001、依赖可维护性、owner 并发和 Provider 生命周期约束确定测试落点与依赖方向"
    - path: Plans/需求分析/2026-08-19-Flutter-CloudFiles与文件预览依赖边界重构.md
      utility: high
      reason: "以 AC-06/AC-08 和无产品行为变化边界锁定 Red 探针与绿基线"
    - path: Plans/功能开发/2026-08-19-Flutter-CloudFiles与文件预览依赖边界重构.md
      utility: high
      reason: "确认 US-CFR-001 是当前唯一滚动 Scope，后续 Runtime 拆分与消费者迁移不得提前进入"
    - path: Contexts/决策/Skill反馈协议.md
      utility: high
      reason: "按 implementation-design 阶段协议记录可聚合的 plan 反馈"
  contexts_missing: []
  contexts_stale: []
  outcome_status: pass
  friction: "内部 Dio/平台无测试 factory，落点以 Provider 可观察生命周期 + onDispose 配对静态证据锁定基线，不改生产装配"
  revisit_needed: false
```

```yaml
skill_run:
  skill: resume-assistant
  workflow_stage: implementation-design
  plan: Plans/功能开发/2026-08-19-Flutter-CloudFiles与文件预览依赖边界重构-US-CFR-001.md
  date: 2026-08-21
  contexts_used:
    - path: Plans/Epic/2026-08-19-Flutter-CloudFiles与文件预览依赖边界重构.md
      utility: high
      reason: "回放最新 lifecycle 与滚动 Story，纠正旧线程停点并确认当前应完成 US-CFR-001 落点设计"
    - path: Plans/功能开发/2026-08-19-Flutter-CloudFiles与文件预览依赖边界重构.md
      utility: high
      reason: "确认 7 Story 已拆分、当前 Scope 仅 US-CFR-001，并在落点门禁通过后推进到 story-development"
    - path: Contexts/决策/Skill反馈协议.md
      utility: high
      reason: "按续作协议记录本次回放、阶段推进和下一继续点"
  contexts_missing: []
  contexts_stale: []
  outcome_status: pass
  revisit_needed: false
```

```yaml
skill_run:
  skill: feature-dev-assistant
  workflow_stage: story-development
  plan: Plans/功能开发/2026-08-19-Flutter-CloudFiles与文件预览依赖边界重构-US-CFR-001.md
  date: 2026-08-21
  contexts_used:
    - path: Plans/功能开发/2026-08-19-Flutter-CloudFiles与文件预览依赖边界重构-US-CFR-001.impl.json
      utility: high
      reason: "按确认落点完成 test-only Red、Green、Refactor 与 integration smoke"
    - path: Plans/技术方案/2026-08-19-Flutter-CloudFiles与文件预览依赖边界重构.md
      utility: high
      reason: "保持 Provider graph、owner 围栏和平台预览生产行为不变"
    - path: Contexts/决策/Skill反馈协议.md
      utility: high
      reason: "将当前 Story 完成反馈置于历史小票之后，供 story-development 门禁读取"
  contexts_missing: []
  contexts_stale: []
  outcome_status: pass
  revisit_needed: false
```

## 续做

```text
/resume plan=Plans/功能开发/2026-08-19-Flutter-CloudFiles与文件预览依赖边界重构.md 进度=implementation-design US-CFR-002
```
