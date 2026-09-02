---
tags: [Epic, client-dev, Flutter, InputBar, 组件化]
type: plan
category: Epic
status: 已归档
date: 2026-08-18
epic_id: flutter-componentized-input-bar
workflow: client-dev
lifecycle_state: integration-test
platform: 客户端
repo: namiwork-flutter
branch: dev
p0_open: 0
plans:
  requirement: Plans/需求分析/2026-08-18-Flutter组件化InputBar.md
  prioritization: Plans/需求排序/2026-08-18-Flutter组件化InputBar.md
  architecture: Plans/技术方案/2026-08-18-Flutter组件化InputBar.md
  development: Plans/功能开发/2026-08-18-Flutter组件化InputBar.md
  integration_plan: Plans/自动化测试/2026-08-18-Flutter组件化InputBar-集成测试计划.md
  integration: Plans/自动化测试/2026-08-18-Flutter组件化InputBar-集成测试.md
relations:
  depends_on:
    - Templates/模板约定.md
    - Templates/需求排序模板.md
    - Templates/技术方案模板.md
    - Templates/客户端功能开发模板.md
    - Templates/集成测试计划模板.md
    - Templates/集成测试模板.md
  dependents: []
  supersedes: []
  superseded_by: []
  conflicts: []
---

# Epic：Flutter 组件化 InputBar（client-dev）

**创建日期**：2026-08-18
**关联仓库**：`namiwork-flutter` · **分支**：`dev`

> Epic 聚合纯 Flutter 组件化 InputBar 的需求、架构、Story 与验证证据。原生 TextView/PlatformView 桥接方向已由用户明确撤销，不属于本 Epic。

## 一、阶段索引

| 阶段 | stage key | Plan | 状态 |
|------|-----------|------|------|
| 需求分析 | requirement | `Plans/需求分析/2026-08-18-Flutter组件化InputBar.md` | 已有 |
| 需求排序 | prioritization | `Plans/需求排序/2026-08-18-Flutter组件化InputBar.md` | 待工作流派生 |
| 正式架构设计 | architecture | `Plans/技术方案/2026-08-18-Flutter组件化InputBar.md` | 待工作流派生 |
| 功能故事拆分与故事点 | story-split | `Plans/功能开发/2026-08-18-Flutter组件化InputBar.md` | 已有 |
| 实现落点设计 | implementation-design | 同上及动态故事子 Plan | US-IB-001..004 已通过 |
| 逐故事 TDD | story-development | 同上及动态故事子 Plan | US-IB-001..004 已通过 |
| 集成测试计划与审核 | integration-test-plan | `Plans/自动化测试/2026-08-18-Flutter组件化InputBar-集成测试计划.md` | 已重审：12 条用例，target `79dfcc0b` |
| 全量集成测试 | integration-test | `Plans/自动化测试/2026-08-18-Flutter组件化InputBar-集成测试.md` | PARTIAL：自动化 55+89；Android Phone 长文本/附件链/失败重试/旋转恢复 PASS；iPhone 安装启动 PASS；剩余矩阵待补 |

## 二、阶段门禁

| 阶段 | 退出条件 |
|------|----------|
| requirement | 需求已采纳、P0=0、边界/异常/AC 齐全 |
| prioritization | Backlog 价值/紧迫度/依赖/优先级/依据齐全且团队确认 |
| architecture | 模块、模型、API、NFR、ADR、需求影响矩阵齐全并已采纳 |
| story-split | 每个 Scope 故事可独立验收、有故事点、AC 和架构引用 |
| implementation-design | 每个 Scope 故事有实现落点 JSON，明确代码证据、目标文件、分层边界和 Red 测试位置 |
| story-development | 每个 Scope 故事 Red/Green/Refactor/冒烟/AC 证据齐全 |
| integration-test-plan | Scope 内每个 Story/AC 都有结构化测试用例；测试审核通过且审核证据与用例版本一致 |
| integration-test | 当前目标 commit 的全量集成报告通过；随后直接 Done |

## 三、动态用户故事看板

故事真理源：`Plans/功能开发/2026-08-18-Flutter组件化InputBar.stories.json`。

| Story | 用户能力 | 优先级 | 点数 | Scope | 依赖 | 状态 |
|-------|----------|--------|------|-------|------|------|
| US-IB-001 | 单一 Flutter TextView 完整 Slate 编辑与 @专家 | P0 | 8 | false | — | DONE：`c26d3adc`，review findings 已关闭，InputBar 42 tests |
| US-IB-002 | 附件选择、上传与媒体预览闭环 | P0 | 8 | true | US-IB-001 | DONE：`45e48c2c`，InputBar 45 / ProductChat 84 / Preview 32 tests |
| US-IB-003 | Slate 与成功附件的 durable 发送和草稿结算 | P0 | 8 | true | US-IB-001/002 | DONE：`6973cc97`，InputBar 48 / ProductChat durable 86 tests |
| US-IB-004 | Model、Skill 与完整五组件生产组合 | P1 | 8 | false | US-IB-001/002/003 | DONE：`b7d091c7`，InputBar 53 / ProductChat durable 87 tests |

当前交付必须继续覆盖 iOS Chat 实际注册的生产组件；不能再把组件扩展点或空接口视为完成。

## 四、2026-08-19 变更影响

用户指出当前实现缺少 Slate/@、生产组件、文件/照片选择和文件上传，原“纯文本首个纵切即完成”结论撤回。

| 影响面 | 必须重写/补齐 |
|---|---|
| 需求 | `document` 改为 Slate 结构化文档；纳入 @专家、生产 5 组件、媒体选择、上传/重试/删除/预览、附件发送 |
| Backlog | 增加 Slate/@、FileInput、MediaPreview+Upload、Model/Skill 及生产接线；移除 TextAndVoice、Voice、AIGC |
| 架构 | 增加 Slate document/projection、MentionProvider、Picker ports、owner-bound UploadRepository、typed send snapshot |
| Story | US-IB-001 降为底座 PARTIAL；新能力必须拆为可独立验收纵向 Story，不允许接口占位 |
| 代码 | `NamiInputState.document`、文本组件、缺失组件、ChatController 附件/mention/options 发送链均受影响 |
| 测试 | commit `474e5cd2` 的 7 条旧测试计划不再覆盖完整 Scope，必须在新 Story 完成后重建并重审 |

迁移以固定 iOS 行为为参考，但范围服从用户最终裁决：实现 Slate Text、FileInput、MediaPreview、Model、Skill；不迁 `NMNewTextAndVoiceComponent`、独立 Voice 与 AIGC。Dark 变体、旧 FormTextView、自研 Camera/Photo UI 等未被当前范围消费的实现不迁；Flutter 使用现有系统选择器、图片选择和上传基础设施。

## 五、变更记录

| 日期 | 变更 | 影响阶段 | 证据 | 确认人 |
|------|------|----------|------|--------|
| 2026-08-18 | 创建纯 Flutter 组件化 InputBar Epic；排除原生桥接 | requirement / architecture / development | 用户裁决、iOS 固定源码、InputBar 设计文档 | 用户 |
| 2026-08-19 | 撤回“基础文本即完整交付”；补入 Slate/@、生产组件、选择与上传 | requirement → integration-test-plan 全链路 | 用户四项缺口、iOS `NMChatViewController` 固定源码 | 用户 |
| 2026-08-19 | 移除 TextAndVoice、Voice、AIGC；固定 5 组件范围 | requirement → architecture → Story | 用户连续范围裁决 | 用户 |
| 2026-08-19 | 删除手工高度回调；AgentSummary/Skill 跨业务适配后置，InputBar 先做 Slate 与附件链 | architecture → Story | 用户模块边界裁决 | 用户 |
| 2026-08-19 | InputBar 保持独立组件；删除聚合 Runtime/Provider/Factory，具体 Picker/Upload 服务只在使用处注入当前实例 | architecture → US-IB-002 | 用户多实例与组件接入裁决 | 用户 |
| 2026-08-19 | 重新打开并完成 Slate：只保留一个 Flutter TextView，补齐生产编辑行为，不迁多 renderer/adapter | US-IB-001 story-development | `a38fa1fc`、51 条聚焦回归 | 用户 |
| 2026-08-19 | 完善 Slate 边界：迟到 picker 隔离、最新请求排队、reference 原子选区、iOS paragraph/block 与 grapheme 对齐 | US-IB-001 review fix | `c26d3adc`、InputBar 42 tests、scoped analyze | 用户继续完善 |
| 2026-08-19 | 完成附件选择、签名上传、失败恢复、媒体预览与发送硬门禁；保持 per-instance 注入 | US-IB-002 story-development | `45e48c2c`、InputBar 45 / ProductChat 84 / Preview 32 tests | 用户继续任务 |
| 2026-08-19 | 冻结 InputBar submission snapshot，接入 durable sendInput；仅 completed 精确清理，中止保留 | US-IB-003 story-development | `6973cc97`、InputBar 48 / ProductChat durable 86 tests | 用户继续任务 |
| 2026-08-19 | 完成 Model/Skill 与五组件生产组合；修复外部状态误回调防止死循环 | US-IB-004 story-development → integration-test-plan | `b7d091c7`、InputBar 53 / ProductChat durable 87 tests | 用户继续任务 |
| 2026-08-19 | 重建并审核完整集成计划，补默认 50000 字边界；自动化集成全通过 | integration-test-plan → integration-test | `709c4261`、InputBar 54 / ProductChat durable 87；IT-IB-501 NOT_RUN | Codex QA / test-generator |
| 2026-08-19 | 真机发现生产附件组件被跨 owner 代际误判关闭；修复后完成 Android Phone Picker→签名上传→预览→删除核心链 | integration-test | `beeff8dd`、InputBar 54 / ProductChat durable 88；Android Phone IT-IB-501 部分 PASS；iPhone network registry PASS | Codex QA / test-generator |
| 2026-08-19 | 对齐 Figma 五态与 iOS 连续高度动画，刷新审核计划；修复越南语 ARB 构建阻塞并完成当前候选 iPhone 安装启动 | integration-test-plan → integration-test | `79dfcc0b`、InputBar 55 / ProductChat durable 89；iPhone build/sign/install/launch PASS，交互矩阵 NOT_RUN | 用户继续任务 / test-generator |
| 2026-08-19 | 在当前候选补 Android Phone 长文本自动换行、生产 InputBar、拍照/相册/文件 Picker、签名上传、离线失败重试、文本预览、删除恢复与旋转草稿保持 | integration-test | `79dfcc0b`、Android Phone IT-IB-501 PARTIAL；未发送真实消息，剩余形态仍 NOT_RUN | 用户继续任务 / test-generator |

## 反馈（skill_run）

```yaml
skill_run:
  skill: template-generator
  workflow_stage: requirement
  plan: Plans/Epic/2026-08-18-Flutter组件化InputBar.md
  date: 2026-08-18
  contexts_used:
    - path: Templates/Epic模板-client-dev.md
      utility: high
      reason: "按 client-dev 蓝图补齐 Epic frontmatter、阶段索引和动态 Story 看板入口"
  contexts_missing: []
  contexts_stale: []
  outcome: "创建 Flutter 组件化 InputBar Epic，并挂接既有需求、Story、落点和 TDD 证据"
  utility: high
  reason: "修复旧桥接 Epic 删除后缺少工作流总入口的问题"
```

```yaml
skill_run:
  skill: change-impact-analysis
  plan: Plans/Epic/2026-08-18-Flutter组件化InputBar.md
  date: 2026-08-19
  contexts_used:
    - path: Plans/需求分析/2026-08-18-Flutter组件化InputBar.md
      utility: high
      reason: "定位把真实组件错误排除在本轮 Scope 外的旧裁决"
    - path: Plans/技术方案/2026-08-18-Flutter组件化InputBar.md
      utility: high
      reason: "确认 Slate、Picker、Upload 和发送快照均没有架构落点"
    - path: ios@4d405cf068488b33396aada07febc3cdb5f31f5f:NAMIWork/Features/ClawChat/NMChatViewController.swift
      utility: high
      reason: "固定 iOS 参考行为，并按用户最终裁决收口为 5 个生产组件"
  contexts_missing: []
  contexts_stale:
    - path: Plans/自动化测试/2026-08-18-Flutter组件化InputBar-集成测试计划.md
      reason: "旧集成测试计划只覆盖框架和 TextField，不能继续送审"
  outcome_status: pass
  outcome: "确认 P0 Scope 扩展，Epic 回退需求/架构并撤回旧完成结论"
  revisit_needed: false
```

```yaml
skill_run:
  skill: dev-lifecycle-audit-assistant
  plan: Plans/Epic/2026-08-18-Flutter组件化InputBar.md
  date: 2026-08-19
  contexts_used:
    - path: Contexts/决策/2026-08-19-开发流程审计报告.md
      utility: high
      reason: "沉淀 Epic 阶段、Story 声明、代码能力和测试证据的 A-E 对账结论"
    - path: Plans/功能开发/2026-08-18-Flutter组件化InputBar-US-IB-001.md
      utility: high
      reason: "核对 Slate Story 的完成声明、验收边界与实际实现口径"
    - path: Plans/功能开发/2026-08-18-Flutter组件化InputBar-US-IB-001.tdd-v2.json
      utility: high
      reason: "确认现有 TDD 证据只覆盖最小 Slate 协议与 mention 行为"
  contexts_missing:
    - "Flutter Slate 对齐 iOS 的完整编辑行为与性能验收矩阵"
  contexts_stale:
    - path: Plans/功能开发/2026-08-18-Flutter组件化InputBar-US-IB-001.md
      reason: "status=已完成与 lifecycle_state=implementation-design、代码范围及测试证据冲突"
  outcome_status: partial
  friction: "US-IB-001 将 Slate 协议 MVP 与完整 Slate 编辑组件迁移混为同一完成口径"
  revisit_needed: true
  revisit_reason: "需重新打开 Slate Story，补齐当前生产使用的 iOS 编辑能力和可测 AC"
```

## 续做

```text
/resume plan=Plans/Epic/2026-08-18-Flutter组件化InputBar.md 进度=派生阶段 / Story ID
```

## 四、变更日志

| 日期 | 变更类型 | 影响阶段 | 重开切片 | 确认人 | 说明 |
|------|----------|----------|----------|--------|------|
| 2026-08-25 | 归档 | — | — | web | status → 已归档 |
