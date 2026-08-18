---
tags: [Epic, client-dev, Flutter, InputBar, 组件化]
type: plan
category: Epic
status: 进行中
date: 2026-08-18
epic_id: flutter-componentized-input-bar
workflow: client-dev
lifecycle_state: requirement
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
| 实现落点设计 | implementation-design | 同上及动态故事子 Plan | US-IB-001 已通过 |
| 逐故事 TDD | story-development | 同上及动态故事子 Plan | US-IB-001 已通过 |
| 集成测试计划与审核 | integration-test-plan | `Plans/自动化测试/2026-08-18-Flutter组件化InputBar-集成测试计划.md` | 待工作流派生 |
| 全量集成测试 | integration-test | `Plans/自动化测试/2026-08-18-Flutter组件化InputBar-集成测试.md` | 待工作流派生 |

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
| US-IB-001 | 按 iOS 架构实现 Flutter 组件化 InputBar 并接入聊天页 | P0 | 8 | true | — | 已完成 |

后续语音、附件、模型、Skill、媒体预览组件按独立纵向 Story 进入 Backlog，不在 US-IB-001 中伪完成。

## 四、变更记录

| 日期 | 变更 | 影响阶段 | 证据 | 确认人 |
|------|------|----------|------|--------|
| 2026-08-18 | 创建纯 Flutter 组件化 InputBar Epic；排除原生桥接 | requirement / architecture / development | 用户裁决、iOS 固定源码、InputBar 设计文档 | 用户 |

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

## 续做

```text
/resume plan=Plans/Epic/2026-08-18-Flutter组件化InputBar.md 进度=派生阶段 / Story ID
```
