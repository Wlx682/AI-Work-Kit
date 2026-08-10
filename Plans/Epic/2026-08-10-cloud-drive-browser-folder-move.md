---
tags: [Epic, client-dev, 敏捷]
type: plan
category: Epic
status: 进行中
date: 2026-08-10
epic_id: cloud-drive-browser-folder-move
workflow: client-dev
lifecycle_state: story-development
platform: 客户端
repo: namiwork-flutter
branch: dev
p0_open: 0
plans:
  requirement: Plans/需求分析/2026-08-10-cloud-drive-browser-folder-move.md
  prioritization: Plans/需求排序/2026-08-10-cloud-drive-browser-folder-move.md
  architecture: Plans/技术方案/2026-08-10-cloud-drive-browser-folder-move.md
  development: Plans/功能开发/2026-08-10-cloud-drive-browser-folder-move.md
  integration_plan: Plans/自动化测试/2026-08-10-cloud-drive-browser-folder-move-集成测试计划.md
  integration: Plans/自动化测试/2026-08-10-cloud-drive-browser-folder-move-集成测试.md
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

# Epic：个人云盘浏览、新建文件夹与移动（client-dev）

**创建日期**：2026-08-10  
**关联仓库**：`namiwork-flutter` · **分支**：`dev`

> 目标是完成 `BUS-046`、`BUS-048`、`BUS-053` 的完整产品能力。任务 ID 仅用于计划和证据，不进入源码技术命名。

## 一、阶段索引

| 阶段 | stage key | Plan | 状态 |
|------|-----------|------|------|
| 需求分析 | requirement | `Plans/需求分析/2026-08-10-cloud-drive-browser-folder-move.md` | 已完成 |
| 需求排序 | prioritization | `Plans/需求排序/2026-08-10-cloud-drive-browser-folder-move.md` | 已完成 |
| 正式架构设计 | architecture | `Plans/技术方案/2026-08-10-cloud-drive-browser-folder-move.md` | 已完成 |
| 功能故事拆分与故事点 | story-split | `Plans/功能开发/2026-08-10-cloud-drive-browser-folder-move.md` | 已完成 |
| 实现落点设计 | implementation-design | 同上及动态故事子 Plan | 已完成 |
| 逐故事 TDD | story-development | 同上及动态故事子 Plan | 进行中 |
| 集成测试计划与审核 | integration-test-plan | `Plans/自动化测试/2026-08-10-cloud-drive-browser-folder-move-集成测试计划.md` | 待开始 |
| 全量集成测试 | integration-test | `Plans/自动化测试/2026-08-10-cloud-drive-browser-folder-move-集成测试.md` | 待开始 |

## 二、阶段门禁

| 阶段 | 退出条件 |
|------|----------|
| requirement | 固定双端源码、MAP/PRE、产品入口、UI/动效、错误恢复和生产接线范围已反向查漏；P0=0 |
| prioritization | 三张正式任务的顺序、依赖和本轮 Scope 已确认 |
| architecture | 模块、模型、真实 Cloud SDK/Repository、路由/DI 串行接线、缓存和 NFR 已采纳 |
| story-split | 每个 Scope 故事纵向可演示验收，有故事点、AC 和架构引用 |
| implementation-design | 每个故事有代码证据、目标文件、依赖边界和 Red 测试位置；技术命名无任务 ID |
| story-development | Red/Green/Refactor、视觉与动效实现、冒烟和 AC 证据齐全 |
| integration-test-plan | 每个 Story/AC 有结构化用例，测试审核通过且版本一致 |
| integration-test | 真实生产接线、全量回归及适用设备证据达到任务完成门禁 |

## 三、动态用户故事看板

故事真理源：`Plans/功能开发/2026-08-10-cloud-drive-browser-folder-move.stories.json`。

| Story | 用户能力 | 优先级 | 点数 | Scope | 依赖 | 状态 |
|-------|----------|--------|------|-------|------|------|
| US-001 | 浏览、搜索并进入个人云盘目录 | P0 | 8 | true | Cloud HTTP 生产接线 | 进行中 |
| US-002 | 当前目录新建文件夹 | P0 | 5 | true | US-001、policy/reconcile 接线 | 进行中 |
| US-003 | 选择目标目录并移动 | P0 | 8 | true | US-001/002、move/reconcile 接线 | 进行中 |

## 四、当前事实与恢复说明

- Flutter 仓库当前已有个人云盘浏览的 `sdk / repository / controller / page` 阶段实现与部分测试。
- `BUS-048`、`BUS-053` 当前源码中尚未找到对应纵向产品实现。
- 05 与 Kanban 将三张任务保持为 `PARTIAL / 王龙祥`，不得因 contract、Fake 或骨架存在升级为完成。
- 上一轮未提交源码和临时 Plan 已被工作区清理；本 Epic 以当前 `dev` 的文件事实重新建立，不复用失效的测试结论。

## 五、变更记录

| 日期 | 变更 | 影响阶段 | 证据 | 确认人 |
|------|------|----------|------|--------|
| 2026-08-10 | 从当前仓库事实恢复 Epic | 全阶段 | 05 三张 `PARTIAL` 卡、当前源码与固定原生基线 | 王龙祥 |
| 2026-08-10 | 完成三张 Story 的领域状态机、Fake 与独立 UI；保持生产接线缺口 | story-development | Cloud Drive 目标测试、三档 Widget Test、命名门禁 | 王龙祥 |

## 续做

```text
/resume plan=Plans/Epic/2026-08-10-cloud-drive-browser-folder-move.md 进度=派生阶段
```

## 反馈（skill_run）

```yaml
skill_run:
  skill: template-generator
  plan: Plans/Epic/2026-08-10-cloud-drive-browser-folder-move.md
  date: 2026-08-10
  contexts_used:
    - path: Contexts/决策/Skill反馈协议.md
      utility: high
      reason: "按统一协议记录恢复 Epic 的模板生成反馈"
  contexts_missing: []
  contexts_stale: []
  outcome_status: pass
  revisit_needed: false
```
