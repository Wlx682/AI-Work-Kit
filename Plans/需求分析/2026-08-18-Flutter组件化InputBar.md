---
tags: [需求分析, Flutter, InputBar, 组件化]
type: plan
category: 需求分析
status: 已确认
date: 2026-08-18
---

# Flutter 组件化 InputBar

## 用户裁决

- 放弃 PlatformView 与 iOS/Android TextView 桥接方案，性能问题暂不作为本轮门禁。
- InputBar 的设计完整参考 iOS `NMInputBar` 及《输入框组件设计文档 NMInputBar》。
- 文本编辑表面先使用 Flutter `TextField`，不引入原生插件。

## 架构约束

1. `NamiInputState` 是输入栏唯一状态源；组件交互先合并到中心状态，再统一分发。
2. `NamiInputComponent` 是可插拔组件契约，保留 `top/main/bottom/background` 四种位置。
3. `NamiInputBar` 负责动态组装、状态同步、重置和事件转发，不承载聊天业务状态机。
4. `NamiInputComponentDelegate` 负责组件向容器上报状态、发送、停止、预览和 ASR 事件。
5. `NamiInputBarDelegate` 负责容器向业务层交付发送与停止等事件。
6. 首个文本组件使用 Flutter `TextField`，通过 `TextEditingValue` 保留文本、selection 与 composing。

## 首轮验收标准

- AC-IB-001：Flutter 存在与 iOS 对齐的 State、Component、ComponentDelegate、Bar、BarDelegate 与 Config 边界。
- AC-IB-002：组件可以按四种 position 动态添加、移除并由容器排列。
- AC-IB-003：任一组件上报状态后，容器更新单一状态源并向全部组件分发。
- AC-IB-004：文本组件使用 Flutter `TextField`，发送/禁用行为由中心状态驱动。
- AC-IB-005：现有生产聊天页面改为组合 `NamiInputBar + NamiTextInputComponent`，发送与草稿恢复语义不回归。

## 非目标

- 10 万字性能结论与真机性能矩阵。
- PlatformView、Pigeon、原生 UITextView/EditText。
- 本轮不实现语音、附件、模型、Skill 的具体业务组件，只固定可插拔契约。
