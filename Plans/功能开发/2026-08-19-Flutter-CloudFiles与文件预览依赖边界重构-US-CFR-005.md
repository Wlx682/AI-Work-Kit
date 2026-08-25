---
tags: [功能开发, 用户故事, TDD, Flutter, CloudFiles, 文件预览, 边界重构]
type: plan
category: 功能开发
status: 已完成
date: 2026-08-20
lifecycle_state: story-development
parent: Plans/功能开发/2026-08-19-Flutter-CloudFiles与文件预览依赖边界重构.md
story_id: US-CFR-005
story_points: 8
sprint_scope: false
implementation_design: Plans/功能开发/2026-08-19-Flutter-CloudFiles与文件预览依赖边界重构-US-CFR-005.impl.json
tdd_evidence: Plans/功能开发/2026-08-19-Flutter-CloudFiles与文件预览依赖边界重构-US-CFR-005.tdd.json
---

# US-CFR-005：文件预览 Feature 归位与 typed host actions

作为终端用户，我要预览云盘、Workspace、AI 和附件文件，且预览 UI、协调、缓存与 Flutter 插件适配由独立 `features/file_preview` 纵切承载，App 只装配 typed port/binding 并复核 identity/generation，以便目录能直接表达业务归属且平台行为保持不变。

## 用户价值与纵向性

面向终端用户的预览能力端到端可用：Files/Projects/Attachment 发 typed intent → App composition 注入当前无凭据 binding → FilePreview Feature 选择 renderer/plugin 并打开页面 → Host 前后复核 identity → 返回既有结果。Feature 不 import App，也不接收 `CloudFilesAppRuntime`/`Ref`/Provider。

## 验收标准

- AC-05：预览 UI/application/data/plugin adapter 归 `features/file_preview`，传输实现归 `features/files`；App 只保留 composition/navigation 和 typed binding；Feature → App 边界测试通过。
- AC-07（预览/传输范围）：iOS/Android 平台预览选择、download/cache/external-open 降级链、cancellation 与失败恢复与重构前一致；协议、签名、缓存 namespace 无变化，diff 审查 + focused regression 通过。
- 每个 host action 执行前与异步返回后都复核 expected identity/generation；owner 切换期间旧预览/下载不借新凭据续跑（AC-06 迟到隔离在预览路径成立）。
- Preview source 无法解析时显式失败，不回退到错误 source 或伪成功。

## 故事边界

含：建立 `features/file_preview` 分层；迁移 preview source/result/coordinator/cache/progress/pages/plugin adapter；将 Gateway/Cloud 输入收窄为 Feature 类型 binding/lease；将 download/upload launcher 归位 `features/files`；保留 App composition 与 `FilesDestination` 路由注入。
不含：拆 Runtime 本体（US-CFR-003 已完成）、完全删除 Projects/Attachment 兼容 provider 与生命周期总闭合（US-CFR-006）。

### 现状证据

- 预览装配 `lib/app/composition/app_file_preview_providers.dart`、`lib/app/composition/file_download_providers.dart`。
- 预览下载消费方 `lib/features/files/download/**`、`lib/features/files/presentation/files_page.dart`（现持 `ActiveGatewayRuntimeIdentity expectedIdentity` 参数，改造为 typed host action）。

## 架构引用

- `Plans/技术方案/2026-08-19-Flutter-CloudFiles与文件预览依赖边界重构.md#ADR-CFR-004`
- `Plans/技术方案/2026-08-19-Flutter-CloudFiles与文件预览依赖边界重构.md#ADR-CFR-008`
- 技术方案 §7.3 Host actions、§7.4 内部错误码、§十三 顺序 5「Preview/Transfer typed actions」。

## 依赖

US-CFR-003、US-CFR-004。

## 实现落点设计

- 结构化证据：`Plans/功能开发/2026-08-19-Flutter-CloudFiles与文件预览依赖边界重构-US-CFR-005.impl.json`
- 边界：`App composition/navigation → FilePreview/Files infrastructure → domain/core/plugin`；`features/file_preview/**` 与 `features/files/**` 对 `lib/app/**` 保持零 import。
- Red 位置：新增 Feature 归位边界测试，精确报出当前 `app/integrations` 中预览 UI/application/data 实现债务。

## 续做

```text
/resume plan=Plans/功能开发/2026-08-19-Flutter-CloudFiles与文件预览依赖边界重构.md 进度=implementation-design US-CFR-006
```

## TDD 与验收结果

- Red：归位边界测试列出 App 中 27 个文件预览/传输实现，证明目录职责债务真实存在。
- Green：预览、Files 页面、上传下载、owner 换代、App composition 与 registry 两轮最终定向回归共 233/233 PASS。
- Refactor：57 个 Dart 路径已格式化，scoped analyze、`git diff --check`、task-ID naming 均通过。
- 真机：连接 iPhone 热重启成功，`home_first_frame=1800ms`；完整 Android/iOS 形态矩阵 `NOT_RUN`，留里程碑执行。
- AC-05、AC-07：**PASS**。机器证据见 `…-US-CFR-005.tdd.json`。

## 反馈（skill_run）

```yaml
skill_run:
  skill: implementation-design-assistant
  workflow_stage: implementation-design
  plan: Plans/功能开发/2026-08-19-Flutter-CloudFiles与文件预览依赖边界重构-US-CFR-005.md
  date: 2026-08-21
  contexts_used:
    - path: Plans/技术方案/2026-08-19-Flutter-CloudFiles与文件预览依赖边界重构.md
      utility: high
      reason: "按 ADR-CFR-004/008 将 Preview 纵切归位 Feature，App 只留装配/路由/owner 复核"
    - path: Contexts/决策/2026-08-21-文件预览归位Feature-变更影响.md
      utility: high
      reason: "确认本次调整已获用户授权且 US-CFR-001～004 成果保留"
  contexts_missing: []
  contexts_stale: []
  outcome_status: pass
  revisit_needed: false
```

```yaml
skill_run:
  skill: feature-dev-assistant
  workflow_stage: story-development
  plan: Plans/功能开发/2026-08-19-Flutter-CloudFiles与文件预览依赖边界重构-US-CFR-005.md
  date: 2026-08-21
  contexts_used:
    - path: Plans/功能开发/2026-08-19-Flutter-CloudFiles与文件预览依赖边界重构-US-CFR-005.impl.json
      utility: high
      reason: "按已确认落点迁移 FilePreview 纵切、Files transfer 实现并建立无凭据 binding/lease"
    - path: Plans/功能开发/2026-08-19-Flutter-CloudFiles与文件预览依赖边界重构-US-CFR-005.tdd.json
      utility: high
      reason: "以 Red/Green/Refactor、真机 smoke 与 AC-05/07 作为完成真理源"
  contexts_missing: []
  contexts_stale: []
  outcome_status: pass
  friction: "既有实现文件和公开类型带 AppFile 前缀；本 Story 先关闭物理模块与依赖方向，兼容命名随剩余消费者和规则故事收口"
  revisit_needed: false
```
