---
tags: [功能开发, R4, Flutter, 子任务]
type: plan
category: 功能开发
status: 已完成
date: 2026-08-03
lifecycle_state: development
epic: Plans/Epic/2026-07-08-智能体开发.md
parent: Plans/功能开发/2026-08-03-R4Flutter学习工作台补全.md
含业务逻辑: 是
relations:
  depends_on:
    - Plans/需求分析/2026-08-03-R4Flutter学习工作台补全.md
    - Plans/技术方案/2026-08-03-R4Flutter学习工作台补全.md
    - Plans/功能开发/2026-08-03-R4Flutter学习工作台补全-子任务01-工作台导航状态.md
    - Plans/功能开发/2026-08-03-R4Flutter学习工作台补全-子任务02-学习路径推荐.md
  dependents: []
  supersedes: []
  superseded_by: []
  conflicts: []
---

# 子任务 03：练习Evidence闭环

## 一、需求分析（开工门禁）

- 需求：`Plans/需求分析/2026-08-03-R4Flutter学习工作台补全.md`
- 技术方案：`Plans/技术方案/2026-08-03-R4Flutter学习工作台补全.md`
- P0=0，覆盖 AC-S6-3。

## 二、原子目标

将现有节点面板 Evidence 能力抽为 PracticeView，绑定 Session，Eval 完成后进入 Review。

## 三、输入与输出

| 输入 | 输出 |
|------|------|
| S4b Flutter 工程、主 plan WBS、关联前置任务 | PracticeView、非空校验、Evidence/Eval 状态流和 widget/controller tests |

## 四、验收

- [x] PracticeView、非空校验、Evidence/Eval 状态流和 widget/controller tests
- [x] 专项测试通过且不破坏既有 Flutter/Agent 回归。

实现证据：

- Graph 只负责显式选择节点和创建 `LearningSession`，Evidence 输入从旧侧栏抽到独立深色响应式 PracticeView。
- Practice 问题绑定当前节点与 Session；空白答案在 API 调用前被拒绝，合法答案 trim 后记入 controller 并提交后端。
- Eval 成功后 destination 自动切到 Review，当前 Evidence、真实 score/reason 和 proposal 已可见，完整 Runtime timeline 留给子任务 04。
- Agent `122 tests OK`；Flutter analyze 无问题，`10 tests passed`，新增空白拦截、trim、自动 Review 与端到端 widget 状态流覆盖。

## 五、续做

```text
/resume plan=Plans/功能开发/2026-08-03-R4Flutter学习工作台补全-子任务04-复盘与进度视图.md 进度=子任务03已完成；独立 PracticeView、Session 绑定、非空 Evidence/Eval 与自动 Review 通过 Agent 122 tests、Flutter 10 tests；下一步补真实 Runtime timeline、决策结果与 Progress 统计
```

## 六、反馈（skill_run）

```yaml
skill_run:
  skill: feature-dev-assistant
  plan: Plans/功能开发/2026-08-03-R4Flutter学习工作台补全-子任务03-练习Evidence闭环.md
  date: 2026-08-03
  contexts_used:
    - path: Plans/技术方案/2026-08-03-R4Flutter学习工作台补全.md
      utility: high
      reason: "以共享 controller、API port 与五视图模块边界作为本子任务约束。"
    - path: Plans/需求分析/2026-08-03-R4Flutter学习工作台补全.md
      utility: high
      reason: "以 AC-S6-3 锁定 Practice 必须绑定 LearningSession，非空答案才产生 Evidence/Eval 并进入 Review。"
  contexts_missing: []
  contexts_stale: []
  outcome_status: pass
  friction: "旧 Graph 侧栏混合了节点选择、Evidence 和 Review；本切片重新明确 Graph 选择、Practice 提交、Review 消费的页面所有权。"
  revisit_needed: false
```
