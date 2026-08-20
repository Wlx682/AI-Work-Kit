---
tags: [功能开发, 用户故事, TDD, Flutter, CloudFiles, 边界重构]
type: plan
category: 功能开发
status: 草稿
date: 2026-08-20
lifecycle_state: story-split
parent: Plans/功能开发/2026-08-19-Flutter-CloudFiles与文件预览依赖边界重构.md
story_id: US-CFR-002
story_points: 5
sprint_scope: false
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

## 续做

```text
/resume plan=Plans/功能开发/2026-08-19-Flutter-CloudFiles与文件预览依赖边界重构.md 进度=implementation-design US-CFR-002
```
