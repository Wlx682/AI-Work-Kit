---
tags: [功能开发, 用户故事, TDD, Flutter, CloudFiles, 边界重构]
type: plan
category: 功能开发
status: 已完成
date: 2026-08-20
lifecycle_state: story-development
parent: Plans/功能开发/2026-08-19-Flutter-CloudFiles与文件预览依赖边界重构.md
story_id: US-CFR-006
story_points: 5
sprint_scope: false
implementation_design: Plans/功能开发/2026-08-19-Flutter-CloudFiles与文件预览依赖边界重构-US-CFR-006.impl.json
tdd_evidence: Plans/功能开发/2026-08-19-Flutter-CloudFiles与文件预览依赖边界重构-US-CFR-006.tdd.json
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
/resume plan=Plans/功能开发/2026-08-19-Flutter-CloudFiles与文件预览依赖边界重构.md 进度=implementation-design US-CFR-007
```

## TDD 与验收结果

- Red：旧 Runtime typedef/消费者和 Files download 的 `AppFile*` 类型命名被边界测试精确命中。
- Green：最终 focused bundles 84/84、14/14、Projects runtime 2/2 PASS；连接 iPhone 启动 smoke 通过。
- Refactor：scoped analyze、format、diff check、task-ID naming 全部通过。
- AC-07、AC-08、AC-09：**PASS**；完整设备矩阵 `NOT_RUN`。机器证据见 `…-US-CFR-006.tdd.json`。

```yaml
skill_run:
  skill: feature-dev-assistant
  workflow_stage: story-development
  plan: Plans/功能开发/2026-08-19-Flutter-CloudFiles与文件预览依赖边界重构-US-CFR-006.md
  date: 2026-08-21
  contexts_used:
    - path: Plans/功能开发/2026-08-19-Flutter-CloudFiles与文件预览依赖边界重构-US-CFR-006.impl.json
      utility: high
      reason: "按落点删除旧 Runtime 别名、收口 download Feature 命名并强化单实例生命周期"
    - path: Plans/功能开发/2026-08-19-Flutter-CloudFiles与文件预览依赖边界重构-US-CFR-006.tdd.json
      utility: high
      reason: "以 Red/Green/Refactor、Projects/Files/Preview 回归和 iPhone smoke 作为完成真理源"
  contexts_missing: []
  contexts_stale: []
  outcome_status: pass
  revisit_needed: false
```

```yaml
skill_run:
  skill: feature-dev-assistant
  workflow_stage: story-development
  plan: Plans/功能开发/2026-08-19-Flutter-CloudFiles与文件预览依赖边界重构-US-CFR-006.md
  date: 2026-08-21
  contexts_used:
    - path: Plans/功能开发/2026-08-19-Flutter-CloudFiles与文件预览依赖边界重构-US-CFR-006.impl.json
      utility: high
      reason: "按落点删除旧 Runtime 别名、收口 download Feature 命名并强化单实例生命周期"
    - path: Plans/功能开发/2026-08-19-Flutter-CloudFiles与文件预览依赖边界重构-US-CFR-006.tdd.json
      utility: high
      reason: "以 Red/Green/Refactor、Projects/Files/Preview 回归和 iPhone smoke 作为完成真理源"
  contexts_missing: []
  contexts_stale: []
  outcome_status: pass
  revisit_needed: false
```

## 实现落点设计

- 删除旧 `CloudFilesRuntime` typedef，App 消费者显式使用 `CloudFilesAppRuntime`；Feature 继续只见 `CloudFilesFeatureRuntime`/binding/lease。
- Files download application 去除 `AppFile*` 类型前缀，App Provider 变量保留 app 前缀以表达装配入口。
- Red 锁在兼容名源码边界和 runtime/manager 单实例生命周期；不改协议、缓存、UI、provider key 或下载 reason code。
- 结构化证据：`Plans/功能开发/2026-08-19-Flutter-CloudFiles与文件预览依赖边界重构-US-CFR-006.impl.json`。

## 反馈（skill_run）

```yaml
skill_run:
  skill: implementation-design-assistant
  workflow_stage: implementation-design
  plan: Plans/功能开发/2026-08-19-Flutter-CloudFiles与文件预览依赖边界重构-US-CFR-006.md
  date: 2026-08-21
  contexts_used:
    - path: Plans/功能开发/2026-08-19-Flutter-CloudFiles与文件预览依赖边界重构-US-CFR-006.impl.json
      utility: high
      reason: "以真实剩余引用锁定旧 Runtime typedef、下载 Feature 命名与 Provider 生命周期 Red"
    - path: Plans/功能开发/2026-08-19-Flutter-CloudFiles与文件预览依赖边界重构-US-CFR-005.tdd.json
      utility: high
      reason: "在 FilePreview 已归位且 binding/lease 回归全绿的基础上只收剩余兼容消费者"
  contexts_missing: []
  contexts_stale: []
  outcome_status: pass
  revisit_needed: false
```

```yaml
skill_run:
  skill: feature-dev-assistant
  workflow_stage: story-development
  plan: Plans/功能开发/2026-08-19-Flutter-CloudFiles与文件预览依赖边界重构-US-CFR-006.md
  date: 2026-08-21
  contexts_used:
    - path: Plans/功能开发/2026-08-19-Flutter-CloudFiles与文件预览依赖边界重构-US-CFR-006.impl.json
      utility: high
      reason: "按落点删除旧 Runtime 别名、收口 download Feature 命名并强化单实例生命周期"
    - path: Plans/功能开发/2026-08-19-Flutter-CloudFiles与文件预览依赖边界重构-US-CFR-006.tdd.json
      utility: high
      reason: "以 Red/Green/Refactor、Projects/Files/Preview 回归和 iPhone smoke 作为完成真理源"
  contexts_missing: []
  contexts_stale: []
  outcome_status: pass
  revisit_needed: false
```
