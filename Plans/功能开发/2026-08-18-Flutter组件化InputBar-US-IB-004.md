---
tags: [功能开发, 用户故事, TDD, Flutter, Model, Skill]
type: plan
category: 功能开发
status: 已完成
date: 2026-08-19
lifecycle_state: story-development
parent: Plans/功能开发/2026-08-18-Flutter组件化InputBar.md
story_id: US-IB-004
story_points: 8
sprint_scope: true
implementation_design: Plans/功能开发/2026-08-18-Flutter组件化InputBar-US-IB-004.impl.json
tdd_evidence: Plans/功能开发/2026-08-18-Flutter组件化InputBar-US-IB-004.tdd.json
commit: b7d091c710374cbb3eedc608819b7f6da4ed2af0
---

# US-IB-004：外部契约稳定后的 Model、Skill 与完整五组件生产组合

作为高级 Chat 用户，我要选择本轮 Model 和 Skill，并在同一 InputBar 中使用完整输入能力，以便发送快照不受发送后的改选影响。

## 验收标准

- AC-IB-001：生产 Chat 组装 Slate Text、FileInput、MediaPreview、Model、Skill 五类真实组件。
- AC-IB-011：Model/Skill 在点击时冻结，发送后的改选只影响下一条。
- 不渲染 `NMNewTextAndVoiceComponent`、Voice 或 AIGC。

## 故事边界

本故事包含 catalog adapter、选择 UI、快照映射、最终 Composition Root 和回归；选择组件不能只是无生产消费者的胶囊占位。

当前依赖已取证：Model 使用 `CloudModelOption.internalModelId`；Skill 只投影稳定的 package/prompt name 与展示名，不修改 `AgentSummary`、`SkillReference` 等公共模型。普通 Skill 对齐 iOS 进入 `use_skill` prompt，不复用技能创建/调试专用 `chat.send.skillId/skillName`。

## 实现落点设计

见 `Plans/功能开发/2026-08-18-Flutter组件化InputBar-US-IB-004.impl.json`。

## 完成结果

- 新增实例级 `NamiModelComponent` 与 `NamiSkillComponent`，生产 Chat 已组装 Model、Skill、MediaPreview、Slate Text、FileInput 五类组件。
- Model 使用 `internalModelId` 冻结到 `selectedModel`；普通 Skill 仅通过 iOS `use_skill` 模板进入 prompt，不占用技能创建/调试字段。
- 外部状态同步不再触发 `onStateChanged`；双 InputBar 的 Model/Skill 互相隔离，成功结算只清理精确 Skill，Model 持久保留。
- ProductChat 在使用处从 CloudConfig 投影模型与 Skill 模板，未新增 InputBar 全局 Provider/Runtime/Factory。
- commit：`b7d091c710374cbb3eedc608819b7f6da4ed2af0`；InputBar 53 条、ProductChat durable 影响集 87 条通过；真机矩阵 `NOT_RUN`。

## 反馈（skill_run）

```yaml
skill_run:
  skill: feature-dev-assistant
  workflow_stage: story-development
  plan: Plans/功能开发/2026-08-18-Flutter组件化InputBar-US-IB-004.md
  date: 2026-08-19
  contexts_used:
    - path: Plans/功能开发/2026-08-18-Flutter组件化InputBar-US-IB-004.impl.json
      utility: high
      reason: "按最小 Model/Skill 投影、五组件生产组合、use_skill prompt 与 selectedModel 冻结落点实现"
    - path: Plans/技术方案/2026-08-18-Flutter组件化InputBar.md
      utility: high
      reason: "遵守独立 InputBar、per-instance 注入、禁用普通 Skill 复用 chat.send.skillId/skillName 的 ADR"
    - path: Plans/功能开发/2026-08-18-Flutter组件化InputBar-US-IB-004.tdd.json
      utility: high
      reason: "记录 Red/Green/Refactor、防回环、多实例、成功结算与影响集回归"
  contexts_missing: []
  contexts_stale: []
  outcome_status: pass
  outcome: "US-IB-004 在 b7d091c7 完成：Model/Skill 生产组件、五组件组合、冻结映射与状态防回环"
  revisit_needed: false
```
