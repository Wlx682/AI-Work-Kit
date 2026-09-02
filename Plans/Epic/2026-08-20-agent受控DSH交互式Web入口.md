---
tags: [Epic, client-dev, DSH, Controlled, Web]
type: plan
category: Epic
status: 已归档
date: 2026-08-20
epic_id: agent-controlled-dsh-web
workflow: client-dev
lifecycle_state: done
platform: 服务端与智能体Runtime/Web
repo: /Users/wanglongxiang/git/agent
branch: codex/controlled-web
p0_open: 0
plans:
  requirement: Plans/需求分析/2026-08-20-agent受控DSH交互式Web入口.md
  prioritization: Plans/需求排序/2026-08-20-agent受控DSH交互式Web入口.md
  architecture: Plans/技术方案/2026-08-20-agent受控DSH交互式Web入口.md
  development: Plans/功能开发/2026-08-20-agent受控DSH交互式Web入口.md
  integration_plan: Plans/自动化测试/2026-08-20-agent受控DSH交互式Web入口-集成测试计划.md
  integration: Plans/自动化测试/2026-08-20-agent受控DSH交互式Web入口-集成测试.md
relations:
  depends_on:
    - Plans/Epic/2026-08-17-agent全仓TypeScript重构.md
    - Plans/技术方案/2026-08-17-智能体控制系统工程架构-v0.1.md
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

# Epic：Agent 受控 DSH 交互式 Web 入口（client-dev）

**创建日期**：2026-08-20
**关联仓库**：`/Users/wanglongxiang/git/agent` · **分支**：`codex/controlled-web`

> 在保留 `controlled-headless` 自动化入口的同时，新增基于 DSH Web App 的受控交互入口；复用现有 Ledger、Supervisor、Authority Gate、Safety 与 composition 完整性机制，不修改官方 Web UI。

## 一、阶段索引

| 阶段 | stage key | Plan | 状态 |
|------|-----------|------|------|
| 需求分析 | requirement | `Plans/需求分析/2026-08-20-agent受控DSH交互式Web入口.md` | ✅ |
| 需求排序 | prioritization | `Plans/需求排序/2026-08-20-agent受控DSH交互式Web入口.md` | ✅ |
| 正式架构设计 | architecture | `Plans/技术方案/2026-08-20-agent受控DSH交互式Web入口.md` | ✅ |
| 功能故事拆分与故事点 | story-split | `Plans/功能开发/2026-08-20-agent受控DSH交互式Web入口.md` | ✅ |
| 实现落点设计 | implementation-design | 同上及动态故事子 Plan | ✅ |
| 逐故事 TDD | story-development | 同上及动态故事子 Plan | ✅ |
| 集成测试计划与审核 | integration-test-plan | `Plans/自动化测试/2026-08-20-agent受控DSH交互式Web入口-集成测试计划.md` | ✅ |
| 全量集成测试 | integration-test | `Plans/自动化测试/2026-08-20-agent受控DSH交互式Web入口-集成测试.md` | ✅ |

## 二、阶段门禁

| 阶段 | 退出条件 |
|------|----------|
| requirement | 交互入口、headless 共存、控制能力、失败关闭、安全边界和可测 AC 已采纳，P0=0 |
| prioritization | Web 启动闭环、受控插件闭环、会话/审批闭环的依赖和优先级已确认 |
| architecture | Profile、启动器、端口/进程、组合指纹、会话与控制插件边界已采纳 |
| story-split | 每个 Scope Story 可独立启动和验收，有故事点、AC 和架构引用 |
| implementation-design | Scope Story 有代码证据、目标文件、分层边界和 Red 测试位置 |
| story-development | Scope Story 具备 Red/Green/Refactor、真实 Web smoke 和逐 AC 证据 |
| integration-test-plan | Headless 不回退、Controlled Web、门禁/Safety、会话与组合漂移均有用例并审核通过 |
| integration-test | 当前目标 commit 的全量集成、真实 Web 启动和回归报告通过，随后 Done |

## 三、动态用户故事看板

故事真理源：`Plans/功能开发/2026-08-20-agent受控DSH交互式Web入口.stories.json`；点数字段为 `story_points`。

| Story | 用户能力 | 优先级 | 点数 | Scope | 依赖 | 状态 |
|-------|----------|--------|------|-------|------|------|
| US-CW-001 | 一条命令打开控制插件完整的受控 DSH Web | P0 | 8 | true | — | 已完成 |
| US-CW-002 | 验证 Web 失败关闭且 headless 不回退 | P0 | 5 | true | US-CW-001 | 已完成 |

> 故事卡片由看板从 `.stories.json` 与子 Plan 派生；禁止把 Profile、启动器、测试分别作为交付故事。

## 四、变更记录

| 日期 | 变更 | 影响阶段 | 证据 | 确认人 |
|------|------|----------|------|--------|
| 2026-08-20 | 创建独立 Epic，不重开已归档 TypeScript 重构 Scope | 全流程 | 用户要求完善受控 DSH 交互能力 | wanglongxiang |
| 2026-08-20 | 双 Story TDD、测试审核与全量集成完成 | Done | commit `74b945b`；73 files / 226 tests；双组合 verify | Codex |

## 续做

```text
/resume plan=Plans/Epic/2026-08-20-agent受控DSH交互式Web入口.md 进度=done
```

## 反馈（skill_run）

```yaml
skill_run:
  skill: test-generator
  workflow_stage: integration-test
  plan: Plans/Epic/2026-08-20-agent受控DSH交互式Web入口.md
  date: 2026-08-20
  contexts_used:
    - path: Plans/自动化测试/2026-08-20-agent受控DSH交互式Web入口-集成测试.md
      utility: high
      reason: "以已审核计划的四条用例和全量回归作为 Done 证据"
    - path: Plans/功能开发/2026-08-20-agent受控DSH交互式Web入口.stories.json
      utility: high
      reason: "确认两个 Story、13 点与 12 条 P0 AC 全部完成"
  contexts_missing: []
  contexts_stale: []
  outcome: "受控 DSH Web 双入口、失败关闭、发布门禁与集成测试全部完成，workflow 派生为 done"
  utility: high
  reason: "代码、Story TDD、审核用例和 workflow gate 四类证据一致"
  outcome_status: pass
  revisit_needed: false
```

## 四、变更日志

| 日期 | 变更类型 | 影响阶段 | 重开切片 | 确认人 | 说明 |
|------|----------|----------|----------|--------|------|
| 2026-08-25 | 归档 | — | — | web | status → 已归档 |
