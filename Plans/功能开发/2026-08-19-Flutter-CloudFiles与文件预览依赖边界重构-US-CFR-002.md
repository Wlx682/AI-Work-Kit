---
tags: [功能开发, 用户故事, TDD, Flutter, CloudFiles, 边界重构]
type: plan
category: 功能开发
status: 已完成
date: 2026-08-20
lifecycle_state: story-development
parent: Plans/功能开发/2026-08-19-Flutter-CloudFiles与文件预览依赖边界重构.md
story_id: US-CFR-002
story_points: 5
sprint_scope: false
implementation_design: Plans/功能开发/2026-08-19-Flutter-CloudFiles与文件预览依赖边界重构-US-CFR-002.impl.json
tdd_evidence: Plans/功能开发/2026-08-19-Flutter-CloudFiles与文件预览依赖边界重构-US-CFR-002.tdd.json
---

# US-CFR-002：单向 App composition 装配链

作为 Flutter 维护者，我要让 Files 相关 composition 子模块不再反向 import `composition_root.dart`，改为依赖抽取出的最小 primitive 叶子模块，以便依赖只单向指向叶子，后续 Runtime 拆分不再复制依赖环。

## 用户价值与纵向性

交付一个可验收结果：`app/composition/{files,cloud_files,file_download,app_file_preview}_providers.dart` 对 `composition_root.dart` 的反向 import 归零，而 App 与 Files 的启动、装配、运行行为完全不变。这是一条端到端可运行的装配链改造，不是纯内部搬移。

## 验收标准

- AC-02：`app/composition/**`（Files 范围模块）对 `composition_root.dart` 的 import = 0；US-CFR-001 的边界探针在这些模块上由红转绿。
- 被 Files composition 依赖的共享 Provider（如 `appFileDirectoriesProvider` 及其最小闭包）迁入无反向依赖的叶子 primitive 模块；`composition_root.dart` 对非 Files 消费者可临时保留兼容 export（ADR-CFR-005）。
- 装配行为不变：Provider 图、生命周期、启动顺序无差异，既有测试与 US-CFR-001 基线全绿。

## 故事边界

含：抽取 composition primitives 最小依赖闭包为叶子模块、改写 Files 相关 4 个 composition 模块的 import 方向、必要的 root 兼容 export。
不含：拆 `CloudFilesRuntime`（US-CFR-003）、动 `features/files/**` 的 import（US-CFR-004）、清理与 Files 无关的 `composition_root.dart` 全量结构（本 Epic 明确不做）。

### 现状证据

- `lib/app/composition/cloud_files_providers.dart:39` `import '../composition_root.dart' show appFileDirectoriesProvider;`
- `lib/app/composition/files_providers.dart:6`、`file_download_providers.dart:15`、`app_file_preview_providers.dart:13` 反向 import `../composition_root.dart`。
- （`home_chat_route_factory_provider.dart`、`product_chat_providers.dart` 属 Chat 范围，不在本 Epic Scope，经兼容 export 过渡。）

## 架构引用

- `Plans/技术方案/2026-08-19-Flutter-CloudFiles与文件预览依赖边界重构.md#ADR-CFR-005`
- 技术方案 §4.2 模块边界（primitives / composition 分层）、§十三 顺序 2「提取 composition primitives 最小闭包」。

## 依赖

US-CFR-001（边界探针需已就绪以验证转绿）。

## TDD 结果（2026-08-21）

- Red：四文件聚焦边界用例精确报告 4 条 composition→root import，退出码 1。
- Green：抽取 environment/storage、gateway runtime、permission、QQ share 四个 primitive 叶子；root import/export 原声明做兼容，四个 Files composition 改为定向 import。
- Refactor：当前 Story 路径与 8 个 root 兼容消费者的 scoped analyze 均通过。
- Smoke：Workspace、CloudFiles/Preview/Download Provider、Files owner/preview、设备切换与下载/导出聚焦回归均通过；`unresolved_impacts=[]`。
- NOT_RUN：Android/iOS 真网络与支付设备围栏留待里程碑矩阵；既有 permission Widget 测试独立复跑仍因 `SharedPreferencesAsyncPlatform` 未注册失败，堆栈早于本 Story Provider 读取，未越界修改。

AC-02：**PASS**。四个 Files App composition 模块对 `composition_root.dart` import 已归零，现有 Provider 图、owner 围栏、生命周期与平台选择保持不变。

## 续做

```text
/resume plan=Plans/功能开发/2026-08-19-Flutter-CloudFiles与文件预览依赖边界重构.md 进度=implementation-design US-CFR-003
```

## 反馈（skill_run）

```yaml
skill_run:
  skill: implementation-design-assistant
  workflow_stage: implementation-design
  plan: Plans/功能开发/2026-08-19-Flutter-CloudFiles与文件预览依赖边界重构-US-CFR-002.md
  date: 2026-08-21
  contexts_used:
    - path: Plans/技术方案/2026-08-19-Flutter-CloudFiles与文件预览依赖边界重构.md
      utility: high
      reason: "依据 §4.2、ADR-CFR-005 与实施顺序 2，将 Files composition 的共享前置收敛为无 root 反向依赖的最小 primitive 闭包"
    - path: Plans/功能开发/2026-08-19-Flutter-CloudFiles与文件预览依赖边界重构-US-CFR-001.impl.json
      utility: high
      reason: "复用已落地的边界探针、owner/lifecycle 基线与聚焦回归位置，不重建测试脚手架"
    - path: Contexts/决策/Skill反馈协议.md
      utility: high
      reason: "按 implementation-design 阶段协议记录设计证据、风险和可恢复续做点"
  contexts_missing: []
  contexts_stale: []
  outcome_status: pass
  friction: "composition_root 中 Gateway primitive 声明分布在两个区段，实现时必须整体迁移而非创建 alias Provider"
  revisit_needed: false
```

```yaml
skill_run:
  skill: resume-assistant
  workflow_stage: implementation-design
  plan: Plans/功能开发/2026-08-19-Flutter-CloudFiles与文件预览依赖边界重构-US-CFR-002.md
  date: 2026-08-21
  contexts_used:
    - path: Plans/Epic/2026-08-19-Flutter-CloudFiles与文件预览依赖边界重构.md
      utility: high
      reason: "从最新 Epic 快照确认当前滚动 Story 为 US-CFR-002，且本次只完成 implementation-design"
    - path: Plans/功能开发/2026-08-19-Flutter-CloudFiles与文件预览依赖边界重构-US-CFR-002.impl.json
      utility: high
      reason: "确认落点 JSON 已包含代码证据、目标文件、依赖规则和可复跑 Red 命令"
    - path: Contexts/决策/Skill反馈协议.md
      utility: high
      reason: "按续作协议记录阶段推进与下一恢复点"
  contexts_missing: []
  contexts_stale: []
  outcome_status: pass
  revisit_needed: false
```

```yaml
skill_run:
  skill: feature-dev-assistant
  workflow_stage: story-development
  plan: Plans/功能开发/2026-08-19-Flutter-CloudFiles与文件预览依赖边界重构-US-CFR-002.md
  date: 2026-08-21
  contexts_used:
    - path: Plans/功能开发/2026-08-19-Flutter-CloudFiles与文件预览依赖边界重构-US-CFR-002.impl.json
      utility: high
      reason: "按已确认的四叶子闭包、root 兼容 export、四文件 Red 与聚焦回归落点完成 TDD"
    - path: Plans/技术方案/2026-08-19-Flutter-CloudFiles与文件预览依赖边界重构.md
      utility: high
      reason: "保持 ADR-CFR-005 的最小 primitive 闭包、root 只汇聚与无产品行为变化约束"
    - path: Contexts/决策/Skill反馈协议.md
      utility: high
      reason: "将 Red/Green/Refactor/Smoke、已知非 Scope 失败与 NOT_RUN 设备围栏写入可聚合反馈"
  contexts_missing: []
  contexts_stale: []
  outcome_status: pass
  friction: "permission Widget 回归被既有 SharedPreferencesAsyncPlatform 测试初始化问题阻断；root 兼容消费者 scoped analyze 与本 Story 主链回归已独立通过"
  revisit_needed: false
```
