---
tags: [功能开发, 智能体开发, R3, runtime]
type: plan
category: 功能开发
status: 已采纳
date: 2026-07-17
workflow: learning-loop
lifecycle_state: development
epic: Plans/Epic/2026-07-08-智能体开发.md
requirement_plan: Plans/需求分析/2026-07-17-Orchestrator最小RuntimeAdapter.md
relations:
  depends_on:
    - Plans/学习循环/2026-07-17-学习-智能体开发-08-R3生产化.md
    - Templates/模板约定.md
  dependents: []
  supersedes: []
  superseded_by: []
  conflicts: []
---

# 功能开发：Orchestrator 最小 Runtime Adapter

**创建日期**：2026-07-17  
**状态**：已采纳  
**所属 Epic**：`Plans/Epic/2026-07-08-智能体开发.md`

## 一、需求分析

需求来源：[Orchestrator 最小 Runtime Adapter 需求分析](../需求分析/2026-07-17-Orchestrator最小RuntimeAdapter.md)。该记录已采纳，`p0_open=0`；本次是学习型技术重构，没有产品 PRD。

## 二、目标与边界

把单智能体 `Orchestrator` 的一次执行包装成结构化 runtime：每次运行具备唯一 ID、阶段事件、成功或失败结果。保持 `planning`、`act`、`reviewing`、世界模型、安全与记忆的业务策略不变；不迁移 Team/A2A，也不引入第三方依赖。

## 三、实施切片

- [x] 1. 定义标准库 `RunEvent`、`RunResult` 和 `Runtime`。
- [x] 2. 为 Orchestrator 增加 `run_with_trace()`，保留 `run()` 的文本结果兼容性。
- [x] 3. 在记忆、规划、预测、步骤、反思和沉淀边界发出结构化事件。
- [x] 4. 让单智能体 CLI 消费 `RunResult` 的失败状态。
- [x] 5. 添加离线单测覆盖重规划 trace 与运行失败。
- [x] 6. 运行测试和静态导入检查。

## 四、验收标准

| 验收项 | 标准 |
|--------|------|
| 向后兼容 | `Orchestrator.run()` 仍返回最终文本结果。 |
| 可观察性 | 每次 run 有唯一 ID，事件可按 sequence 回放。 |
| 可评估性 | 规划、反思、步骤和运行终态均有结构化事件。 |
| 失败收口 | 业务异常转换为带错误事件的 `RunResult`。 |
| 无外部依赖 | 只使用 Python 标准库。 |

## 五、实现与验证

| 产物 | 说明 |
|------|------|
| `agent/runtime.py` | 标准库 `Runtime`、`RunEvent`、`RunResult`。 |
| `agent/orchestrator.py` | 新增 `run_with_trace()`；各业务边界发出事件，`run()` 保留旧返回值。 |
| `agent/main.py` | 单智能体 CLI 消费 `RunResult` 的失败状态。 |
| `agent/tests/test_runtime.py` | 离线覆盖重规划 trace 和规划失败。 |

验证结果：`python3 -m unittest discover -s agent/tests -v` 通过 2 项；`python3 -m compileall -q agent` 通过。

## 续做

```text
/resume plan=Plans/功能开发/2026-07-17-Orchestrator最小RuntimeAdapter.md 进度=最小 runtime adapter 已通过离线验证；下一步为 R3 trace 持久化或 eval harness
```

## 反馈（skill_run）

```yaml
skill_run:
  skill: feature-dev-assistant
  plan: Plans/功能开发/2026-07-17-Orchestrator最小RuntimeAdapter.md
  date: 2026-07-17
  contexts_used:
    - path: Plans/学习循环/2026-07-17-学习-智能体开发-08-R3生产化.md
      utility: high
      reason: "定义了 Orchestrator 第一刀迁移的运行时边界与验收。"
    - path: Plans/Epic/2026-07-08-智能体开发.md
      utility: high
      reason: "提供了 R3 的历史架构与 Epic 归属。"
  contexts_missing: []
  contexts_stale: []
```
