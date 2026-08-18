---
tags: [功能开发, 用户故事, TDD, Flutter, InputBar]
type: plan
category: 功能开发
status: 已完成
date: 2026-08-18
lifecycle_state: story-development
requirement_plan: Plans/需求分析/2026-08-18-Flutter组件化InputBar.md
parent: Plans/功能开发/2026-08-18-Flutter组件化InputBar.md
story_id: US-IB-001
story_points: 8
sprint_scope: true
tdd_evidence: Plans/功能开发/2026-08-18-Flutter组件化InputBar-US-IB-001.tdd.json
implementation_design: Plans/功能开发/2026-08-18-Flutter组件化InputBar-US-IB-001.impl.json
---

# US-IB-001：按 iOS 架构实现 Flutter 组件化 InputBar 并接入聊天页

作为 Flutter 聊天输入区消费者，我需要与 iOS 同构的中心状态和可插拔组件容器，以便文本、语音、附件、模型、Skill 等能力可以独立组合且共享一致状态。

## 验收标准

- AC-IB-001：公开 API 包含与 iOS 对齐的 State、Component、ComponentDelegate、Bar、BarDelegate 与 Config。
- AC-IB-002：支持 top/main/bottom/background 四种 position 及运行时 add/remove。
- AC-IB-003：组件状态经 merge 进入中心状态，再分发给所有组件。
- AC-IB-004：首个文本组件使用 Flutter `TextField`，禁用和发送由中心状态驱动。
- AC-IB-005：聊天页移除私有 `_Composer`，生产发送、草稿恢复和 busy 禁用聚焦回归通过。

## 实现落点设计

机器契约：`Plans/功能开发/2026-08-18-Flutter组件化InputBar-US-IB-001.impl.json`。

## 实际结果

- 与 iOS 同构的中心状态、组件协议、双 delegate、四位置、Config、动态 add/remove 已落地。
- 首个 `NamiTextInputComponent` 使用 Flutter `TextField/TextEditingValue`。
- 聊天生产页已移除私有 `_Composer` 并完成接线；语音、附件、模型、Skill 组件不在本故事内。
- TDD 与集成证据：`Plans/功能开发/2026-08-18-Flutter组件化InputBar-US-IB-001.tdd.json`。

## 反馈（skill_run）

```yaml
skill_run:
  skill: implementation-design-assistant
  workflow_stage: implementation-design
  plan: Plans/功能开发/2026-08-18-Flutter组件化InputBar-US-IB-001.md
  date: 2026-08-18
  contexts_used:
    - path: Plans/需求分析/2026-08-18-Flutter组件化InputBar.md
      utility: high
      reason: "沉淀内部设计文档的单一状态源、组件化、观察者和委托约束"
    - path: /Users/wanglongxiang/git/NNamiWork/NAMIWork/Share/UI/InputBar
      utility: high
      reason: "以固定 iOS commit 取证协议、四位置、状态合并和生产组件组合"
  contexts_missing: []
  contexts_stale: []
  outcome: "确认 Flutter 只替换文本编辑内核，InputBar 组件边界与 iOS 保持同构"
  utility: high
  reason: "避免把组件化误做成单个 TextField 包装器"
```

```yaml
skill_run:
  skill: feature-dev-assistant
  workflow_stage: story-development
  plan: Plans/功能开发/2026-08-18-Flutter组件化InputBar-US-IB-001.md
  date: 2026-08-18
  contexts_used:
    - path: Plans/功能开发/2026-08-18-Flutter组件化InputBar-US-IB-001.impl.json
      utility: high
      reason: "固定 State/Component/Delegate/Bar/TextComponent 与生产入口落点"
    - path: Plans/功能开发/2026-08-18-Flutter组件化InputBar-US-IB-001.tdd.json
      utility: high
      reason: "记录 Red-Green-Refactor、生产回归和逐 AC 证据"
  contexts_missing: []
  contexts_stale: []
  outcome: "完成 Flutter 组件化 InputBar 首个纵切并接入 ChatPage，无原生桥接"
  utility: high
  reason: "中心状态、可插拔组件和现有 durable submission 语义同时闭合"
```
