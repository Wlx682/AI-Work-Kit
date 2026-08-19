---
tags: [功能开发, 用户故事, TDD, Flutter, 附件]
type: plan
category: 功能开发
status: 已完成
date: 2026-08-19
lifecycle_state: story-development
epic: Plans/Epic/2026-08-18-Flutter组件化InputBar.md
parent: Plans/功能开发/2026-08-18-Flutter组件化InputBar.md
requirement_plan: Plans/需求分析/2026-08-18-Flutter组件化InputBar.md
architecture_plan: Plans/技术方案/2026-08-18-Flutter组件化InputBar.md
story_id: US-IB-002
story_points: 8
sprint_scope: true
含业务逻辑: 是
implementation_design: Plans/功能开发/2026-08-18-Flutter组件化InputBar-US-IB-002.impl.json
tdd_evidence: Plans/功能开发/2026-08-18-Flutter组件化InputBar-US-IB-002.tdd.json
commit: 45e48c2ce2f596b0837e2ad5ddb10e48010f1a5a
---

# US-IB-002：附件选择、上传与媒体预览闭环

作为 Chat 用户，我要选择照片、视频、本地文件或云盘文件，并查看真实上传进度，以便在失败时重试/删除、成功后预览。

## 验收标准

- AC-IB-005/反例：系统 Picker 返回 typed source；取消、拒绝、超限不污染已有草稿。
- AC-IB-006/007：上传进度单调，失败可重试/删除，迟到结果受 owner/operation 围栏。
- AC-IB-008/009：MediaPreview 展示各 phase；存在未成功附件时禁止发送。

## 故事边界

本故事包含 FileInput UI、Picker adapters、上传 Repository、MediaPreview UI、失败恢复和测试；不把 Fake 或只展示本地缩略图视为完成。

InputBar 只定义附件自身的最小数据和 Picker/Upload/Preview 端口；不修改 AgentSummary、Skill 或云盘业务模型。云盘选中项由其业务模块未来投影为 InputBar 的 trusted remote attachment，不阻塞当前的拍照/相册/本地文件上传链。

## 完成结果

- 每个 ProductChat/InputBar 实例独立创建附件 Controller、Picker、上传 Repository 与预览 adapter；未增加全局 InputBar runtime/provider/factory。
- 拍照、相册、本地文件选择，签名 multipart 上传，单调进度，失败重试/删除，owner+operation 迟到围栏和精确终态清理已闭合。
- 成功附件接入现有 App 图片、视频、文档真实预览栈；未成功附件不会调用远端预览。
- commit：`45e48c2ce2f596b0837e2ad5ddb10e48010f1a5a`；TDD 证据见 `Plans/功能开发/2026-08-18-Flutter组件化InputBar-US-IB-002.tdd.json`。
- 真机 Picker、真实签名上传和 Android/iOS 系统预览矩阵：`NOT_RUN`，在 Epic 集成里程碑统一执行。

## 反馈（skill_run）

```yaml
skill_run:
  skill: implementation-design-assistant
  workflow_stage: implementation-design
  plan: Plans/功能开发/2026-08-18-Flutter组件化InputBar-US-IB-002.md
  date: 2026-08-19
  contexts_used:
    - path: Plans/技术方案/2026-08-18-Flutter组件化InputBar.md
      utility: high
      reason: "落实 per-instance Controller、typed Picker/Upload/Preview port、`/api/s3/upload` 和 owner/operation 围栏"
    - path: Plans/功能开发/2026-08-18-Flutter组件化InputBar-US-IB-002.impl.json
      utility: high
      reason: "复核 domain/application/data/components/生产使用处和 Red 测试的逐文件落点"
    - path: Plans/功能开发/2026-08-18-Flutter组件化InputBar.stories.json
      utility: high
      reason: "确认 US-IB-002 是当前唯一滚动 Scope，且不提前修改 Model/Skill 外部契约"
  contexts_missing: []
  contexts_stale: []
  outcome_status: pass
  outcome: "落点与当前工作树一致；补入 platform picker 和 Chat 终态精确附件清理测试位置，可进入 story-development"
  revisit_needed: false
```
