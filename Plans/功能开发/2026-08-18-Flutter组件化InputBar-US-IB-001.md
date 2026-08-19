---
tags: [功能开发, 用户故事, TDD, Flutter, Slate]
type: plan
category: 功能开发
status: 已完成
date: 2026-08-19
lifecycle_state: story-development
parent: Plans/功能开发/2026-08-18-Flutter组件化InputBar.md
story_id: US-IB-001
story_points: 8
sprint_scope: false
implementation_design: Plans/功能开发/2026-08-18-Flutter组件化InputBar-US-IB-001.impl.json
tdd_evidence: Plans/功能开发/2026-08-18-Flutter组件化InputBar-US-IB-001.tdd-v2.json
---

# US-IB-001：Flutter Slate 文本与 @专家生产发送

作为 Chat 用户，我要在 Flutter 输入框中编辑 Slate 文档并 @专家，以便界面展示原子 `@名称`，发送时提交 `@[名称](agentId)`。

## 验收标准

- AC-IB-002：多段文本可在 Slate JSON、编辑投影、display/prompt 间无损往返。
- AC-IB-003/反例：`@` 候选可选择或取消；取消不丢字，选择后形成原子 mention。
- AC-IB-004：退格/选区删除不会留下半个 mention，selection/composing 合法。
- AC-IB-014：只使用一个 Flutter `TextField` renderer，具备 plain/Slate/simple 导入导出、set/clear/focus/selection 与文档变化出口。
- AC-IB-015：agent/file reference 可解析、插入、替换、删除、提取；点击已有 agent mention 可带默认值重选。
- AC-IB-016：跨段编辑、emoji/UTF-16、IME composing、程序化回写和连续状态分发不破坏文档且不形成回写循环。
- AC-IB-017：对齐 iOS 50000 字上限，超限通过回调交给附件业务处理；Slate 编辑器自身不依赖上传服务。
- 生产 Chat 仍可发送纯文本和 mention prompt；失败保留当前草稿。

## 故事边界

本故事内部包含 Slate domain、单一 Flutter TextView 编辑内核、最小 reference picker 回调、组件 UI、Chat prompt 接线和针对性测试；不包含附件上传、Model、Skill，也不迁 iOS YY/Native/Porton 多 renderer 与 renderer adapter。

## 实际结果

- `ea5773b6` 只完成 Slate JSON/双导出、Flutter editing projection、原子 mention 和可注入候选 picker 的 MVP，不能作为完整 Slate 迁移完成证据。
- 删除 iOS 手工高度、Voice/ASR 遗留契约；InputBar 依赖 Flutter 自动布局。
- 不修改 `AgentSummary` 或 Skill 公共模型；生产数据 adapter 后置，不把本故事宣称为外部数据接线完成。
- 2026-08-19 用户要求重新打开本 Story：完整迁移 Slate 编辑行为，但只实现一个 Flutter TextView，不迁多 renderer/adapter。
- `a38fa1fc` 完成单一 `NamiSlateTextView(TextField)`、agent/file reference、@取消/新增/重选、IME、full/simple JSON、overflow callback 与程序化回写防循环；51 条聚焦回归通过。
- `c26d3adc` 关闭代码审查边界：picker 以 controller/document revision 隔离迟到结果并保留最新排队请求；reference 选区原子吸附且末尾不误触；paragraph 显示、编辑后 block 保留与 extended grapheme 语义对齐固定 iOS。InputBar 目录 42 tests 与 scoped analyze 通过，真机矩阵仍为 `NOT_RUN`。

## 实现落点设计

机器契约：`Plans/功能开发/2026-08-18-Flutter组件化InputBar-US-IB-001.impl.json`。Slate domain 与 Flutter editing projection 分离；InputBar 只消费最小候选投影，不修改或依赖 `AgentSummary`。

## 反馈（skill_run）

```yaml
skill_run:
  skill: implementation-design-assistant
  workflow_stage: implementation-design
  plan: Plans/功能开发/2026-08-18-Flutter组件化InputBar-US-IB-001.md
  date: 2026-08-19
  contexts_used:
    - path: Plans/技术方案/2026-08-18-Flutter组件化InputBar.md
      utility: high
      reason: "落实 Flutter renderer + Slate domain、最小 mention 投影与自动布局"
    - path: Plans/技术方案/2026-08-18-Flutter组件化InputBar.md
      utility: high
      reason: "固定 Slate JSON、UTF-16 range 与 prompt mention 协议"
    - path: Plans/功能开发/2026-08-18-Flutter组件化InputBar.md
      utility: high
      reason: "保护现有初始草稿、失败恢复与 durable send 语义"
  contexts_missing: []
  contexts_stale:
    - path: Plans/功能开发/2026-08-18-Flutter组件化InputBar-US-IB-001.impl.json
      reason: "旧版本只覆盖 TextEditingValue 与 mention MVP，本次已按单一 Flutter TextView 完整重写"
  outcome_status: pass
  outcome: "确定 Slate domain、editing projection、可注入候选和生产发送的逐文件落点；外部 Agent adapter 后置"
  revisit_needed: false
```

```yaml
skill_run:
  skill: feature-dev-assistant
  workflow_stage: story-development
  plan: Plans/功能开发/2026-08-18-Flutter组件化InputBar-US-IB-001.md
  date: 2026-08-19
  contexts_used:
    - path: Plans/代码重构/2026-08-19-Flutter-Slate-代码审查.md
      utility: high
      reason: "以四项 finding 作为 Red 回归和修复边界"
    - path: Plans/功能开发/2026-08-18-Flutter组件化InputBar-US-IB-001.impl.json
      utility: high
      reason: "保持单一 Flutter TextView、独立组件和实例级依赖边界"
    - path: /Users/wanglongxiang/git/NNamiWork/NAMIWork/Share/UI/InputBar/NMSlateEditor
      utility: high
      reason: "核对 paragraph、grapheme 与系统剪贴板行为，不臆造 Flutter 私有协议"
  contexts_missing: []
  contexts_stale: []
  outcome_status: pass
  outcome: "c26d3adc 完成 review fix；20 条 Slate 聚焦测试、42 条 InputBar 测试与 scoped analyze 通过"
  revisit_needed: false
```

```yaml
skill_run:
  skill: feature-dev-assistant
  workflow_stage: story-development
  plan: Plans/功能开发/2026-08-18-Flutter组件化InputBar-US-IB-001.md
  date: 2026-08-19
  contexts_used:
    - path: Plans/功能开发/2026-08-18-Flutter组件化InputBar-US-IB-001.impl.json
      utility: high
      reason: "按单一 Flutter TextView 落点完成 Slate domain、editing controller 与 widget TDD"
    - path: Plans/技术方案/2026-08-18-Flutter组件化InputBar.md
      utility: high
      reason: "保持独立组件、多实例、实例级依赖注入和纯 Flutter 边界"
    - path: Contexts/决策/2026-08-19-开发流程审计报告.md
      utility: high
      reason: "关闭此前把 mention MVP 错报成 Slate 完成的审计缺口"
  contexts_missing: []
  contexts_stale: []
  outcome_status: pass
  revisit_needed: false
```

```yaml
skill_run:
  skill: feature-dev-assistant
  workflow_stage: story-development
  plan: Plans/功能开发/2026-08-18-Flutter组件化InputBar-US-IB-001.md
  date: 2026-08-19
  contexts_used:
    - path: Plans/功能开发/2026-08-18-Flutter组件化InputBar-US-IB-001.impl.json
      utility: high
      reason: "按单一 Flutter TextView 落点完成 Slate domain、editing controller 与 widget TDD"
    - path: Plans/技术方案/2026-08-18-Flutter组件化InputBar.md
      utility: high
      reason: "保持独立组件、多实例、实例级依赖注入和纯 Flutter 边界"
    - path: Contexts/决策/2026-08-19-开发流程审计报告.md
      utility: high
      reason: "关闭此前把 mention MVP 错报成 Slate 完成的审计缺口"
  contexts_missing: []
  contexts_stale: []
  outcome_status: pass
  revisit_needed: false
```

```yaml
skill_run:
  skill: implementation-design-assistant
  workflow_stage: implementation-design
  plan: Plans/功能开发/2026-08-18-Flutter组件化InputBar-US-IB-001.md
  date: 2026-08-19
  contexts_used:
    - path: Plans/技术方案/2026-08-18-Flutter组件化InputBar.md
      utility: high
      reason: "沿用纯 Flutter、独立组件、多实例和实例级依赖注入边界"
    - path: Plans/功能开发/2026-08-18-Flutter组件化InputBar-US-IB-001.impl.json
      utility: high
      reason: "固定单一 Flutter TextView、Slate domain 与 editing controller 的逐文件落点"
    - path: Contexts/决策/2026-08-19-开发流程审计报告.md
      utility: high
      reason: "依据审计缺口重新打开 Slate Story，避免继续以 mention MVP 作为完成口径"
  contexts_missing: []
  contexts_stale: []
  outcome_status: pass
  friction: "iOS 多 renderer 目录不能机械映射到 Flutter，需要按生产行为收敛为单一编辑内核"
  revisit_needed: false
```

```yaml
skill_run:
  skill: feature-dev-assistant
  workflow_stage: story-development
  plan: Plans/功能开发/2026-08-18-Flutter组件化InputBar-US-IB-001.md
  date: 2026-08-19
  contexts_used:
    - path: Plans/功能开发/2026-08-18-Flutter组件化InputBar-US-IB-001.impl.json
      utility: high
      reason: "按单一 Flutter TextView 落点完成 Slate domain、editing controller 与 widget TDD"
    - path: Plans/技术方案/2026-08-18-Flutter组件化InputBar.md
      utility: high
      reason: "保持独立组件、多实例、实例级依赖注入和纯 Flutter 边界"
    - path: Contexts/决策/2026-08-19-开发流程审计报告.md
      utility: high
      reason: "关闭此前把 mention MVP 错报成 Slate 完成的审计缺口"
  contexts_missing: []
  contexts_stale: []
  outcome_status: pass
  revisit_needed: false
```
