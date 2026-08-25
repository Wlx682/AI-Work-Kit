---
tags: [功能开发, 用户故事, TDD, Flutter, CloudFiles, 边界重构]
type: plan
category: 功能开发
status: 已完成
date: 2026-08-20
lifecycle_state: story-development
parent: Plans/功能开发/2026-08-19-Flutter-CloudFiles与文件预览依赖边界重构.md
story_id: US-CFR-003
story_points: 8
sprint_scope: false
implementation_design: Plans/功能开发/2026-08-19-Flutter-CloudFiles与文件预览依赖边界重构-US-CFR-003.impl.json
tdd_evidence: Plans/功能开发/2026-08-19-Flutter-CloudFiles与文件预览依赖边界重构-US-CFR-003.tdd.json
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

## TDD 结果（2026-08-21）

- Red：Feature Runtime 字段/import 与 App Runtime provider 投影测试均因新类型、投影和 owner guard 尚未实现而编译失败。
- Green：新增 `CloudFilesRuntimeIdentity` / `CloudFilesFeatureRuntime`，将单一 Runtime 分为 App-private Runtime 与 Feature 窄投影；9/9 聚焦测试通过。
- Refactor：Feature Runtime 只 import Files cloud-file domain contracts，静态禁止 App/Core/外部 package 和网络/鉴权/平台/Riverpod 类型；scoped analyze 无问题。
- Smoke：owner 凭据换代、Files 预览取消/新 owner 恢复、目录换代关闭和 App 边界均通过；Provider 同 owner 仍只创建/释放一次。
- NOT_RUN：Android/iOS 真网络与支付设备围栏留待 Epic 里程碑矩阵；本 Story 未改 HTTP/签名/支付/原生插件。

AC-03、AC-06：**PASS**。机器证据见 `…-US-CFR-003.tdd.json`。

## 实现落点设计

- Feature 契约新建于 `lib/features/files/cloud_files_feature_runtime.dart`：`CloudFilesRuntimeIdentity` 仅含 environment/provider/stableId/generation，`CloudFilesFeatureRuntime` 仅含 identity、五组 domain owner 与 repository contract。
- `lib/app/cloud_files_runtime.dart` 保留 SessionSnapshot/Store，新建 `CloudFilesAppRuntime` 承载 client、签名 context、上传/预览平台、`isCurrentOwner` 与唯一 `featureRuntime` 投影。
- 生产 composition 必须显式先构造 Feature Runtime 再注入 App Runtime，复用原 `isCurrentSnapshot` 围栏与原 onDispose，不新增 Provider/网络/平台实例。
- 为不跨入 US-CFR-004/005/006，`CloudFilesRuntime` 及现有上传/预览访问只作 App 侧临时别名/兼容面；`features/files/presentation/files_page.dart` 本 Story 不改。
- Red 位于 `test/features/files/cloud_files_feature_runtime_test.dart` 与 `test/app/cloud_files_runtime_provider_test.dart`，分别锁定禁止字段/import 以及投影、owner generation 围栏、单次创建/释放。

机器可读细节见 `Plans/功能开发/2026-08-19-Flutter-CloudFiles与文件预览依赖边界重构-US-CFR-003.impl.json`。

## 续做

```text
/resume plan=Plans/功能开发/2026-08-19-Flutter-CloudFiles与文件预览依赖边界重构.md 进度=implementation-design US-CFR-004
```

## 反馈（skill_run）

```yaml
skill_run:
  skill: resume-assistant
  workflow_stage: implementation-design
  plan: Plans/功能开发/2026-08-19-Flutter-CloudFiles与文件预览依赖边界重构-US-CFR-003.md
  date: 2026-08-21
  contexts_used:
    - path: Plans/Epic/2026-08-19-Flutter-CloudFiles与文件预览依赖边界重构.md
      utility: high
      reason: "确认 US-CFR-001/002 已完成且当前唯一滚动 Scope 为 US-CFR-003"
    - path: Plans/功能开发/2026-08-19-Flutter-CloudFiles与文件预览依赖边界重构.md
      utility: high
      reason: "回放 implementation-design 门禁后只处理缺失的 US-CFR-003 implementation_design，不重做前两个 Story"
    - path: Contexts/决策/Skill反馈协议.md
      utility: high
      reason: "按协议记录续作的阶段、上下文和下一恢复点"
  contexts_missing: []
  contexts_stale: []
  outcome_status: pass
  friction: "现有 Files/Main/Projects 仍直接标注 CloudFilesRuntime，需通过 App 侧兼容面保持本 Story 不跨 Scope"
  revisit_needed: false
```

```yaml
skill_run:
  skill: implementation-design-assistant
  workflow_stage: implementation-design
  plan: Plans/功能开发/2026-08-19-Flutter-CloudFiles与文件预览依赖边界重构-US-CFR-003.md
  date: 2026-08-21
  contexts_used:
    - path: Plans/技术方案/2026-08-19-Flutter-CloudFiles与文件预览依赖边界重构.md
      utility: high
      reason: "依据 §4.4、§7.1 和 ADR-CFR-003 锁定 App/Feature Runtime 字段与依赖方向"
    - path: lib/app/cloud_files_runtime.dart
      utility: high
      reason: "盘点单一 Runtime 中需分属 App 与 Feature 的真实字段"
    - path: lib/app/composition/cloud_files_providers.dart
      utility: high
      reason: "锁定生产投影构造、isCurrentSnapshot 围栏与 onDispose 不变量"
    - path: lib/features/automation/automation_runtime.dart
      utility: medium
      reason: "选择 Files Feature 根目录的 Runtime 命名和放置惯例"
    - path: Contexts/决策/Skill反馈协议.md
      utility: high
      reason: "保证最后 skill_run 对齐 implementation-design 机械门禁"
  contexts_missing: []
  contexts_stale: []
  outcome_status: pass
  friction: "为避免提前修改 US-CFR-004/006 消费者，设计需显式标记 CloudFilesRuntime 为 App 侧临时兼容面"
  revisit_needed: false
```

```yaml
skill_run:
  skill: resume-assistant
  workflow_stage: story-development
  plan: Plans/功能开发/2026-08-19-Flutter-CloudFiles与文件预览依赖边界重构-US-CFR-003.md
  date: 2026-08-21
  contexts_used:
    - path: Plans/Epic/2026-08-19-Flutter-CloudFiles与文件预览依赖边界重构.md
      utility: high
      reason: "回放当前唯一滚动 Scope 与 story-development 门禁，确认不重做 US-CFR-001/002"
    - path: Plans/功能开发/2026-08-19-Flutter-CloudFiles与文件预览依赖边界重构-US-CFR-003.impl.json
      utility: high
      reason: "以已确认目标文件、兼容 seam、Red 位置与禁止跨 Story 边界恢复开发"
    - path: Contexts/决策/Skill反馈协议.md
      utility: high
      reason: "记录续作阶段、经过的门禁和下一滚动 Story"
  contexts_missing: []
  contexts_stale: []
  outcome_status: pass
  friction: "impact selector 以整个未提交工作树选择围栏，需区分 US-CFR-003 新文件与前置 Story 累积路径"
  revisit_needed: false
```

```yaml
skill_run:
  skill: feature-dev-assistant
  workflow_stage: story-development
  plan: Plans/功能开发/2026-08-19-Flutter-CloudFiles与文件预览依赖边界重构-US-CFR-003.md
  date: 2026-08-21
  contexts_used:
    - path: Plans/功能开发/2026-08-19-Flutter-CloudFiles与文件预览依赖边界重构-US-CFR-003.impl.json
      utility: high
      reason: "按机器落点完成 Feature contract、App runtime、生产投影与兼容面的 Red→Green→Refactor"
    - path: Plans/功能开发/2026-08-19-Flutter-CloudFiles与文件预览依赖边界重构-US-CFR-003.tdd.json
      utility: high
      reason: "固化 AC-03/06、owner/lifecycle、Files 换代 smoke 与 NOT_RUN 设备围栏证据"
    - path: Contexts/决策/Skill反馈协议.md
      utility: high
      reason: "保证 Story 末尾反馈与 story-development 机械验收对齐"
  contexts_missing: []
  contexts_stale: []
  outcome_status: pass
  friction: "为不跨入 US-CFR-004/006，保留 CloudFilesRuntime App 侧类型别名和兼容构造，后续需按 Story 删除"
  revisit_needed: false
```
