---
tags: [自动化测试, 集成测试计划, client-dev, Flutter, InputBar]
type: plan
category: 自动化测试
status: 已采纳
date: 2026-08-19
lifecycle_state: integration-test-plan
epic: Plans/Epic/2026-08-18-Flutter组件化InputBar.md
story_index: Plans/功能开发/2026-08-18-Flutter组件化InputBar.stories.json
target_commit: "79dfcc0b2dc43251d5fd6f98b623e0819ae1cc4e"
test_case_index: Plans/自动化测试/2026-08-18-Flutter组件化InputBar-集成测试计划.cases.json
test_review: Plans/自动化测试/2026-08-18-Flutter组件化InputBar-集成测试计划.review.json
relations:
  depends_on:
    - Plans/功能开发/2026-08-18-Flutter组件化InputBar.md
    - Plans/功能开发/2026-08-18-Flutter组件化InputBar-US-IB-001.tdd-v2.json
    - Plans/功能开发/2026-08-18-Flutter组件化InputBar-US-IB-002.tdd.json
    - Plans/功能开发/2026-08-18-Flutter组件化InputBar-US-IB-003.tdd.json
    - Plans/功能开发/2026-08-18-Flutter组件化InputBar-US-IB-004.tdd.json
    - Plans/技术方案/2026-08-18-Flutter组件化InputBar.md
  dependents: []
  supersedes: []
  superseded_by: []
  conflicts: []
---

# 集成测试计划：Flutter 组件化 InputBar

## 一、测试策略

- 目标 commit：`79dfcc0b2dc43251d5fd6f98b623e0819ae1cc4e`（包含 Slate 默认 50000 字边界、生产附件组合跨 owner 域回归、Figma 五态与 iOS 连续高度动画校正，以及阻断真机构建的越南语 ARB 修复）。
- Scope：US-IB-001..004 全部 AC；Slate/@、附件 Picker/上传/预览、durable 快照/结算、Model/Skill 五组件生产组合、多实例和防回环。
- 非目标：Voice、`NMNewTextAndVoiceComponent`、AIGC、PlatformView/原生 TextView；未稳定的 AgentSummary/SkillReference/CloudFiles 业务数据模型。
- 自动化环境：macOS + Flutter 3.44.8，typed Fake/Stub Gateway、Durable Outbox、Picker/Upload/Preview ports；不记录正文、凭证或文件二进制。
- 真机环境：Android Phone/Pad/Fold 与 iPhone/iPad，需有效登录、Gateway、签名上传和系统 Picker/预览权限。
- 风险分级：原子 Slate/reference、迟到结果、未成功附件发送、durable 结算、Model/Skill 字段误用、状态死循环为 P0；50000 字边界为 P1。

## 二、测试用例

> 机械真理源为 `test_case_index` JSON；本表用于人工审核。

| 用例 ID | 标题 | 关联 Story / AC | 优先级 | 类型 | 自动化 |
|---|---|---|---|---|---|
| IT-IB-101 | Slate/单 TextField/reference 完整往返 | US-IB-001 / 002、014、015 | P0 | contract-widget | automated |
| IT-IB-102 | @、原子编辑、IME、迟到与防回环 | US-IB-001 / 003、003-反、004、016 | P0 | interaction-recovery | automated |
| IT-IB-103 | 50000 字/grapheme overflow 边界 | US-IB-001 / 017 | P1 | boundary | automated |
| IT-IB-104 | Figma 五态布局与 iOS 连续高度动画 | US-IB-001/004 / 016、001 | P0 | visual-interaction | automated |
| IT-IB-201 | Picker typed source 与反例 | US-IB-002 / 005、005-反 | P0 | adapter-negative | automated |
| IT-IB-202 | 上传进度、恢复、owner/operation 围栏 | US-IB-002 / 006、007 | P0 | state-machine-recovery | automated |
| IT-IB-203 | MediaPreview phase 与发送硬门禁 | US-IB-002 / 008、009 | P0 | widget-gate | automated |
| IT-IB-301 | Slate+附件冻结为 durable delivery | US-IB-003 / 010 | P0 | cross-story-durable | automated |
| IT-IB-302 | 非成功保留与精确 completed 结算 | US-IB-003 / 012、013 | P0 | durable-recovery | automated |
| IT-IB-401 | 五组件生产组合与实例隔离 | US-IB-004 / 001 | P0 | production-composition | automated |
| IT-IB-402 | Model/Skill 冻结、字段和持久策略 | US-IB-004 / 011 | P0 | cross-story-command | automated |
| IT-IB-501 | 五类真机 Picker/上传/预览/自适应 | 跨 Story 核心 AC | P0 | device-matrix | manual |

## 三、需求与用例覆盖

| Story | AC | 覆盖用例 | 优先级 | 结论 |
|---|---|---|---|---|
| US-IB-001 | 002、003、003-反、004、014..017 | IT-IB-101..104、501 | P0/P1 | 已覆盖 |
| US-IB-002 | 005、005-反、006..009 | IT-IB-201..203、501 | P0 | 已覆盖 |
| US-IB-003 | 010、012、013 | IT-IB-301、302、501 | P0 | 已覆盖 |
| US-IB-004 | 001、011 | IT-IB-401、402、501 | P0 | 已覆盖 |

## 四、执行 Suite

| Suite | 用例 | 命令 / 方式 |
|---|---|---|
| input-bar-all | IT-IB-101..203、401（含 IT-IB-104） | `flutter test test/features/chat/presentation/input_bar` |
| product-chat-durable | IT-IB-301、302、402 | 执行 impact selector 选中的 8 个 ProductChat durable targets |
| input-bar-and-product-chat | IT-IB-401 | 同时使用 InputBar 全量组件回归与 ProductChat 生产 key/发送回归取证 |
| scoped-analyze | 全部自动化用例的静态门禁 | `flutter analyze lib/l10n lib/features/chat/presentation/input_bar lib/features/chat/presentation/chat_page.dart lib/features/chat/presentation/chat_controller.dart lib/app/product_chat_destination.dart` |
| device-matrix | IT-IB-501 | 依 `docs/standards/dual-platform-device-regression.md` 人工执行并留存设备证据 |

## 五、测试审核

- [x] Scope 内 US-IB-001..004 的全部 AC 均有结构化用例覆盖。
- [x] P0/P1 主路径、反例、边界、owner/迟到和 durable 恢复场景已列入审核范围。
- [x] 自动化 suite 与真机环境/数据/执行方式可复现。
- [x] `test_review` 已记录审核人、时间、目标 commit 和用例索引 SHA-256。
- [x] 五项审核 finding 已关闭，未解决意见为 0。

```text
python3 scripts/validate-client-dev.py test-plan --plan Plans/自动化测试/2026-08-18-Flutter组件化InputBar-集成测试计划.md
```

## 反馈（skill_run）

```yaml
skill_run:
  skill: test-generator
  workflow_stage: integration-test-plan
  plan: Plans/自动化测试/2026-08-18-Flutter组件化InputBar-集成测试计划.md
  date: 2026-08-19
  contexts_used:
    - path: Plans/功能开发/2026-08-18-Flutter组件化InputBar.stories.json
      utility: high
      reason: "按 Epic Scope 覆盖四个 Story 的全部 AC，不再复用已撤回的纯文本计划"
    - path: Plans/功能开发/2026-08-18-Flutter组件化InputBar-US-IB-004.tdd.json
      utility: high
      reason: "将五组件、多实例、防回环、Model/Skill 冻结与结算纳入集成用例"
    - path: Templates/集成测试计划模板.md
      utility: high
      reason: "遵守 target commit、结构化 case index、SHA-256 审核与执行前冻结门禁"
  contexts_missing:
    - "Android Phone/Pad/Fold 与 iPhone/iPad 真机及有效签名上传环境"
  contexts_stale:
    - path: Plans/自动化测试/2026-08-18-Flutter组件化InputBar-集成测试计划.md
      reason: "旧 target 474e5cd2 仅覆盖纯文本框架；本次已以 b7d091c7 和 11 条完整用例重建"
  outcome_status: pass
  outcome: "11 条用例已覆盖全部 Story/AC；生产真机发现的附件 owner 代际误判已修复并重审，冻结 beeff8dd，可继续集成执行"
  revisit_needed: false
```

```yaml
skill_run:
  skill: test-generator
  workflow_stage: integration-test-plan
  plan: Plans/自动化测试/2026-08-18-Flutter组件化InputBar-集成测试计划.md
  date: 2026-08-19
  contexts_used:
    - path: Plans/功能开发/2026-08-19-Flutter组件化InputBar-Figma还原自检.md
      utility: high
      reason: "把 Figma 默认/聚焦/多行/长文本/收起态与 100ms 动画转成 IT-IB-104 可执行用例"
    - path: Plans/自动化测试/2026-08-18-Flutter组件化InputBar-集成测试计划.review.json
      utility: high
      reason: "刷新当前候选、用例索引 SHA-256 和五项已关闭审核意见"
  contexts_missing:
    - "当前候选 Android Phone/Pad/Fold、iPhone InputBar 交互与 iPad 真机证据"
  contexts_stale:
    - path: Plans/自动化测试/2026-08-18-Flutter组件化InputBar-集成测试计划.cases.json
      reason: "旧索引未覆盖 Figma 五态和连续高度动画，且 target commit 已变化；本次已重建并重审"
  outcome_status: pass
  outcome: "12 条用例重新审核通过，冻结 79dfcc0b；IT-IB-104 覆盖 Figma/iOS 视觉动效校正"
  revisit_needed: false
```
