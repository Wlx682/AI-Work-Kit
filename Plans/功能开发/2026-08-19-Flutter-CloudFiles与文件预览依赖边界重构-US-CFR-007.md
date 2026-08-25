---
tags: [功能开发, 用户故事, TDD, Flutter, CloudFiles, 边界重构, 门禁]
type: plan
category: 功能开发
status: 已完成
date: 2026-08-20
lifecycle_state: story-development
parent: Plans/功能开发/2026-08-19-Flutter-CloudFiles与文件预览依赖边界重构.md
story_id: US-CFR-007
story_points: 3
sprint_scope: true
implementation_design: Plans/功能开发/2026-08-19-Flutter-CloudFiles与文件预览依赖边界重构-US-CFR-007.impl.json
tdd_evidence: Plans/功能开发/2026-08-19-Flutter-CloudFiles与文件预览依赖边界重构-US-CFR-007.tdd.json
---

# US-CFR-007：固化 Provider 装配规则与边界回归门禁

作为后续开发者，我要在约束文档与自动门禁中写明"具体 Provider 由对应 App composition 模块装配、`composition_root.dart` 只汇聚/暴露"，以便新文件能力有明确装配入口，且 Files→App、composition→root 的边界不会被后续提交悄悄破坏。

## 用户价值与纵向性

交付一个可验收的治理结果：读文档即知依赖方向与装配入口；边界断言进入构建前门禁（如 pre-commit / CI 分析），非法 import 在合入前被阻断并输出非法路径。规则文字与自动测试口径一致。

## 验收标准

- AC-10：目标架构与任务约束文档不再暗示"Provider 必须写进单一根文件"，改为"App composition 模块装配、root 汇聚"；规则文档审查通过。
- US-CFR-001 的边界断言升级为常驻门禁（构建前阻断），覆盖 `features/files/** → app/**` 与 `app/composition/** → composition_root.dart`（Files 范围）两条禁止关系，破坏时输出非法路径。
- 文档规则与自动门禁在同一故事验收，二者口径一致，无漂移。
- 命名规范门禁：CloudFiles/预览模块新增或改动类型符合技术方案 §4.6 后缀词典、前缀单复数与 Port/Contract 规则；`app_file_preview_naming_boundary_test.dart` 扩展覆盖词典一致性，违规输出类型名与被违反的规则项。

## 故事边界

含：修订会误导“Provider 进聚合根”的约束文档；把边界测试接入构建前门禁；规则与门禁一致性检查；把 §4.6 命名词典一致性纳入命名门禁。
不含：推广到 Chat/Claw 等其他 Feature 的全仓依赖治理（本 Epic 明确不做，另立治理任务）；`FilePreviewDestination`→`FilePreviewTarget`（属 core，已于 2026-08-20 按用户指示直接完成，不在本故事）；`AppFileDownloadRuntime` 改名（随 US-CFR-005/006 落地）。

### 现状证据（落点阶段定位具体文档）

- 目标架构与文件预览架构文档：`docs/versions/2.0.0/plan/baseline/target-architecture.md`、`docs/versions/2.0.0/plan/28-file-preview-architecture.md`（架构 skill_run 已标注后者"Provider 定义移出 root"表述不足以约束方向，需本故事修订）。
- 边界测试脚手架来自 US-CFR-001。

## 架构引用

- `Plans/技术方案/2026-08-19-Flutter-CloudFiles与文件预览依赖边界重构.md#ADR-CFR-001`
- `Plans/技术方案/2026-08-19-Flutter-CloudFiles与文件预览依赖边界重构.md#ADR-CFR-005`
- `Plans/技术方案/2026-08-19-Flutter-CloudFiles与文件预览依赖边界重构.md#ADR-CFR-007`（§4.6 词汇与命名规范）
- 技术方案 §十一 需求影响矩阵 CFR-007、§十四 验收标准末两项。

## 依赖

US-CFR-001..US-CFR-006（规则与门禁在全部边界闭合后固化）。

## 实现落点设计

- 修订正式 28 号文件预览架构与 target architecture，明确 App 只装配、Feature 承载 UI/协调/缓存/plugin adapter。
- `AppFilePreview*` 类型统一为 `FilePreview*`；App Provider 变量可保留 app 前缀。
- 自动门禁同时约束 Feature→App import、App integrations 职责、旧 Runtime/download/preview 类型名。

```yaml
skill_run:
  skill: implementation-design-assistant
  workflow_stage: implementation-design
  plan: Plans/功能开发/2026-08-19-Flutter-CloudFiles与文件预览依赖边界重构-US-CFR-007.md
  date: 2026-08-21
  contexts_used:
    - path: Plans/功能开发/2026-08-19-Flutter-CloudFiles与文件预览依赖边界重构-US-CFR-007.impl.json
      utility: high
      reason: "把正式文档、类型词典和现有边界测试收敛成最后一个可验收纵切"
  contexts_missing: []
  contexts_stale: []
  outcome_status: pass
  revisit_needed: false
```

## 续做

```text
/resume plan=Plans/功能开发/2026-08-19-Flutter-CloudFiles与文件预览依赖边界重构.md 进度=implementation-design US-CFR-007
```

## TDD 结果

- Red：边界测试命中 18 个 `AppFilePreview*` 命名债务。
- Green：60/60 聚焦测试通过，Feature→App import 为 0，App integrations 预览实现为 0。
- Refactor：scoped analyze、diff check、task-ID naming 均通过。
- Smoke：连接 iPhone 热重启成功，`home_first_frame=1776ms`。
- AC-10：PASS。完整 Android Phone/Pad/Fold + iPhone/iPad 矩阵 `NOT_RUN`。

```yaml
skill_run:
  skill: feature-dev-assistant
  workflow_stage: story-development
  plan: Plans/功能开发/2026-08-19-Flutter-CloudFiles与文件预览依赖边界重构-US-CFR-007.md
  date: 2026-08-21
  contexts_used:
    - path: Plans/功能开发/2026-08-19-Flutter-CloudFiles与文件预览依赖边界重构-US-CFR-007.impl.json
      utility: high
      reason: "按落点固化 Feature/App 归属、类型词典与自动边界"
    - path: Plans/功能开发/2026-08-19-Flutter-CloudFiles与文件预览依赖边界重构-US-CFR-007.tdd.json
      utility: high
      reason: "记录 Red/Green/Refactor、AC-10、iPhone smoke 和未运行设备矩阵"
  contexts_missing: []
  contexts_stale: []
  outcome_status: pass
  friction: "需要区分 Feature 实现类的中性命名与 App composition Provider 变量的宿主归属命名"
  revisit_needed: false
```
