---
tags: [Epic, client-dev, 敏捷, 模板]
type: plan
category: Epic
status: 草稿
date: {{date}}
epic_id: {{title-kebab}}
workflow: client-dev
lifecycle_state: requirement
platform: 客户端
repo: 【业务仓库名】
branch: 【feature/xxx】
p0_open: 0
plans:
  requirement: Plans/需求分析/{{date}}-{{title}}.md
  prioritization: Plans/需求排序/{{date}}-{{title}}.md
  architecture: Plans/技术方案/{{date}}-{{title}}.md
  development: Plans/功能开发/{{date}}-{{title}}.md
  integration_plan: Plans/自动化测试/{{date}}-{{title}}-集成测试计划.md
  integration: Plans/自动化测试/{{date}}-{{title}}-集成测试.md
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

# Epic：{{title}}（client-dev）

**创建日期**：{{date}}
**关联仓库**：【】 · **分支**：【】

> Epic 只聚合子 Plan 路径和动态用户故事摘要，不驱动阶段。真实阶段由 `.workflows/blueprints/client-dev.json` 与 `workflow-gate.sh` 根据文件事实派生。

## 一、阶段索引

| 阶段 | stage key | Plan | 状态 |
|------|-----------|------|------|
| 需求分析 | requirement | `Plans/需求分析/{{date}}-{{title}}.md` | ⬜ |
| 需求排序 | prioritization | `Plans/需求排序/{{date}}-{{title}}.md` | ⬜ |
| 正式架构设计 | architecture | `Plans/技术方案/{{date}}-{{title}}.md` | ⬜ |
| 功能故事拆分与故事点 | story-split | `Plans/功能开发/{{date}}-{{title}}.md` | ⬜ |
| 实现落点设计 | implementation-design | 同上及动态故事子 Plan | ⬜ |
| 逐故事 TDD | story-development | 同上及动态故事子 Plan | ⬜ |
| 集成测试计划与审核 | integration-test-plan | `Plans/自动化测试/{{date}}-{{title}}-集成测试计划.md` | ⬜ |
| 全量集成测试 | integration-test | `Plans/自动化测试/{{date}}-{{title}}-集成测试.md` | ⬜ |

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

故事真理源：`Plans/功能开发/{{date}}-{{title}}.stories.json`；点数字段为 `story_points`。

| Story | 用户能力 | 优先级 | 点数 | Scope | 依赖 | 状态 |
|-------|----------|--------|------|-------|------|------|
| US-001 | 【】 | P0 | 5 | true | — | 待开发 |

> 故事卡片由看板从 `.stories.json` 与子 Plan 派生；禁止把 UI、Domain、Data/API 分别作为交付故事。故事点不换算工时或个人绩效。

## 四、变更记录

| 日期 | 变更 | 影响阶段 | 证据 | 确认人 |
|------|------|----------|------|--------|
| {{date}} | 创建 Epic | — | — | 【】 |

## 续做

```text
/resume plan=Plans/Epic/{{date}}-{{title}}.md 进度=【派生阶段 / Story ID】
```
