---
tags: [功能开发, R4, AgentRuntime, LangGraph]
type: plan
category: 功能开发
status: 已采纳
date: 2026-08-03
lifecycle_state: development
epic: Plans/Epic/2026-07-08-智能体开发.md
parent: Plans/学习循环/2026-08-02-学习实践-智能体开发-09-R4知识图谱驱动学习系统.md
含业务逻辑: 是
relations:
  depends_on:
    - Plans/需求分析/2026-08-03-LearningAgentRuntime角色工具接入.md
    - Plans/技术方案/2026-08-03-LearningAgentRuntime角色工具接入.md
    - Plans/学习循环/2026-08-02-学习实践-智能体开发-09-R4知识图谱驱动学习系统.md
  dependents: []
  supersedes: []
  superseded_by: []
  conflicts: []
---

# 功能开发：Learning Agent Runtime 角色与工具接入

## 一、需求分析（开工门禁）

| 项 | 内容 |
|----|------|
| 需求分析 plan | `Plans/需求分析/2026-08-03-LearningAgentRuntime角色工具接入.md` |
| 技术方案 plan | `Plans/技术方案/2026-08-03-LearningAgentRuntime角色工具接入.md` |
| 分析结论 | ✅ P0=0，可开发 |

## 二、背景与目标

完成父 plan S3 的最小 Runtime 接入：四角色受控串联；图谱写操作先暂停、人工批准后恢复；所有节点与终态进入 RunResult Trace。

非目标：真实 LLM、HTTP、Flutter、完整 LearningSession 生命周期、动态角色路由。

## 三、架构概要

| 模块/类 | 职责 |
|---------|------|
| `LearningRuntimeRoles` | 注入四个无副作用角色 |
| `LearningRuntimeTools` | 注入经批准后才可执行的图谱写工具 |
| `LearningAgentRuntime` | LangGraph 状态图、run/resume、checkpoint、Trace、失败终态 |

接口契约：`Plans/技术方案/2026-08-03-LearningAgentRuntime角色工具接入.md`。

## 四、实施切片

| # | 输入 | 输出 | 覆盖 AC | 验收 | 依赖 |
|---|------|------|---------|------|------|
| 1 | AC-S3 | 无提案/暂停/恢复/拒绝/失败 RED 测试 | AC-S3-1~5 | 测试先红 | — |
| 2 | 测试与方案 | `LearningAgentRuntime` 状态图和注入端口 | AC-S3-1~4 | 专项测试通过 | 1 |
| 3 | 异常样例 | 输出校验、失败 Trace、checkpoint history | AC-S3-2/5 | 负向测试通过 | 2 |
| 4 | 完整实现 | agent 全量回归与父 plan 回写 | AC-S3 | 全量测试通过 | 1–3 |

```text
[x] 1. RED 测试
[x] 2. Runtime 与角色/工具端口
[x] 3. interrupt/resume/checkpoint/失败收口
[x] 4. 全量回归与父 plan 回写
```

## 五、验收

- [x] 四角色调用顺序和 Trace 可验证。
- [x] 有提案时暂停且写工具未调用。
- [x] 批准后写一次；拒绝时零次。
- [x] 角色/工具异常以 `run failed` 收口。
- [x] SQLite 新 Runtime 实例可从同一 checkpoint 恢复。
- [x] 专项 8 tests、`agent/tests` 全量 117 tests 通过。

## 续做

```text
/resume plan=Plans/学习循环/2026-08-02-学习实践-智能体开发-09-R4知识图谱驱动学习系统.md 进度=S3 已完成；LearningAgentRuntime 专项 8 tests、agent/tests 117 tests OK；下一步进入 S4a Flutter 核心页面信息架构与交互原型
```

## 反馈（skill_run）

```yaml
skill_run:
  skill: feature-dev-assistant
  plan: Plans/功能开发/2026-08-03-LearningAgentRuntime角色工具接入.md
  date: 2026-08-03
  contexts_used:
    - path: Plans/技术方案/2026-08-03-LearningAgentRuntime角色工具接入.md
      utility: high
      reason: "依据独立学习 Runtime、注入角色端口和写工具人工确认边界实施。"
    - path: Contexts/决策/Kit核心原则.md
      utility: high
      reason: "先建 AC/失败测试并通过 development gate 后再写实现。"
  contexts_missing: []
  contexts_stale: []
  outcome_status: pass
  friction: "开发 plan 的门禁要求开工前已有 skill_run；已在测试与实现完成后将结果更新为 pass。"
  revisit_needed: false
```
