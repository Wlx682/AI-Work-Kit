---
tags: [功能开发, R4, GoldenTask, Eval, Replay]
type: plan
category: 功能开发
status: 已采纳
date: 2026-08-03
workflow: learning-loop
lifecycle_state: development
epic: Plans/Epic/2026-07-08-智能体开发.md
parent: Plans/学习循环/2026-08-02-学习实践-智能体开发-09-R4知识图谱驱动学习系统.md
含业务逻辑: 是
relations:
  depends_on:
    - Plans/需求分析/2026-08-03-GoldenLearningTaskSuiteManifest.md
    - Plans/技术方案/2026-08-03-GoldenLearningTaskSuiteManifest.md
    - Plans/学习循环/2026-08-02-学习实践-智能体开发-09-R4知识图谱驱动学习系统.md
  dependents: []
  supersedes: []
  superseded_by: []
  conflicts: []
---

# 功能开发：Golden Learning Task Suite Manifest

## 一、需求分析（开工门禁）

| 项 | 内容 |
|----|------|
| 需求分析 plan | `Plans/需求分析/2026-08-03-GoldenLearningTaskSuiteManifest.md` |
| 技术方案 plan | `Plans/技术方案/2026-08-03-GoldenLearningTaskSuiteManifest.md` |
| 分析结论 | ✅ P0=0，可开发 |

## 二、背景与目标

第三十二刀已经支持传入 `run_references` 执行持久化 batch regression，但调用方仍需临时组装引用。本切片将 suite 定义持久化，让调用方只凭 `suite_id` 重跑回归。

非目标：不接 CLI/HTTP、不引入数据库、不改变单任务 report 与 batch report 判定规则。

## 三、契约

```text
GoldenLearningTaskSuiteManifest
  ├── suite_id
  └── run_references[]
        ├── task_id
        └── run_id

suite_id
  → load manifest
  → load GoldenLearningTask + RunResult
  → replay graph operations
  → build task reports
  → save task reports + batch report
```

## 四、错误边界

| 场景 | 预期 error_code |
|------|-----------------|
| manifest 缺失 | `GOLDEN_LEARNING_TASK_SUITE_MANIFEST_NOT_FOUND` |
| manifest 为空 | `EMPTY_GOLDEN_LEARNING_TASK_SUITE_MANIFEST` |
| task_id 重复 | `DUPLICATE_GOLDEN_LEARNING_TASK_REFERENCE` |
| run_id 重复 | `DUPLICATE_GOLDEN_LEARNING_RUN_REFERENCE` |

## 五、实施切片

| # | 输入 | 输出 | 覆盖 AC | 验收 | 依赖 |
|---|------|------|---------|------|------|
| 1 | AC-S2、现有 batch runner | manifest dataclass 与验证测试 | AC-S2 | RED 覆盖空/重复引用 | S1 |
| 2 | manifest schema | JSON repository save/load | AC-S2 | 往返相等 | 1 |
| 3 | repository manifest | suite_id batch runner | AC-S2 | 仅凭 suite_id 生成并保存报告 | 2 |
| 4 | 缺失/坏输入 | 明确 ContractApiResult 错误码 | AC-S2 | 负向测试通过 | 2,3 |
| 5 | 完整实现 | 模块与 agent/tests 回归 | AC-S2 | 全量测试通过 | 1–4 |

```text
[x] 1. manifest schema 与 RED 测试
[x] 2. repository save/load
[x] 3. suite_id batch runner
[x] 4. 错误码边界
[x] 5. 全量回归与父 plan 回写
```

## 六、验收

- [x] manifest 可 JSON 往返保存。
- [x] 空 manifest、重复 task_id、重复 run_id 被拒绝。
- [x] manifest 缺失返回专用错误码。
- [x] 仅凭 suite_id 可执行真实 trace/replay batch regression。
- [x] `agent.tests.test_learning_contracts` 66 tests 与 `agent/tests` 109 tests 全量通过。

## 续做

```text
/resume plan=Plans/学习循环/2026-08-02-学习实践-智能体开发-09-R4知识图谱驱动学习系统.md 进度=S2 Suite Manifest 已完成，下一步进入 S3 Agent Runtime 与角色/工具接入
```

## 反馈（skill_run）

```yaml
skill_run:
  skill: feature-dev-assistant
  plan: Plans/功能开发/2026-08-03-GoldenLearningTaskSuiteManifest.md
  date: 2026-08-03
  contexts_used:
    - path: Plans/学习循环/2026-08-02-学习实践-智能体开发-09-R4知识图谱驱动学习系统.md
      utility: high
      reason: "承接系统开发线 AC-S2、第三十二刀 batch runner 与开发优先调度事实。"
    - path: Plans/Epic/2026-07-08-智能体开发.md
      utility: high
      reason: "确认本功能挂载 learning-loop 智能体开发 Epic，属于 R4 practice。"
    - path: Contexts/决策/Kit核心原则.md
      utility: high
      reason: "按测试先行与 Gate 原则创建功能子 plan，并在代码前执行 development 门禁。"
  contexts_missing: []
  contexts_stale: []
  outcome_status: partial
  friction: "新建功能 plan 的 development 门禁要求先存在 skill_run，先以 partial 开工反馈通过文档门禁。"
  revisit_needed: false
```

```yaml
skill_run:
  skill: feature-dev-assistant
  plan: Plans/功能开发/2026-08-03-GoldenLearningTaskSuiteManifest.md
  date: 2026-08-03
  contexts_used:
    - path: Plans/需求分析/2026-08-03-GoldenLearningTaskSuiteManifest.md
      utility: high
      reason: "以 AC-S2-1–AC-S2-5 锁定 manifest 往返、suite_id 重跑与缺失/空/重复边界。"
    - path: Plans/技术方案/2026-08-03-GoldenLearningTaskSuiteManifest.md
      utility: high
      reason: "按 Manifest Contract、JsonLearningRepository 与 Suite Runner API 边界完成最小实现。"
    - path: Plans/学习循环/2026-08-02-学习实践-智能体开发-09-R4知识图谱驱动学习系统.md
      utility: high
      reason: "回写第三十三刀、S2 完成事实、66/109 测试结果与 S3 下一续点。"
  contexts_missing: []
  contexts_stale: []
  outcome_status: pass
  revisit_needed: false
```
