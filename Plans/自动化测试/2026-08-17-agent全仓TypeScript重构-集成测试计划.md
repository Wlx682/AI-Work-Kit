---
tags: [自动化测试, 集成测试计划, client-dev, TypeScript, DSH]
type: plan
category: 自动化测试
status: 已采纳
date: 2026-08-20
lifecycle_state: integration-test-plan
epic: Plans/Epic/2026-08-17-agent全仓TypeScript重构.md
story_index: Plans/功能开发/2026-08-17-agent全仓TypeScript重构.stories.json
target_commit: "582306a8675cea435ea33e53b8db82086947ff9f"
test_case_index: Plans/自动化测试/2026-08-17-agent全仓TypeScript重构-集成测试计划.cases.json
test_review: Plans/自动化测试/2026-08-17-agent全仓TypeScript重构-集成测试计划.review.json
relations:
  depends_on:
    - Plans/功能开发/2026-08-17-agent全仓TypeScript重构.md
    - Plans/功能开发/2026-08-17-agent全仓TypeScript重构-US-B5-002.tdd.json
    - Plans/技术方案/2026-08-17-智能体控制系统工程架构-v0.1.md
  dependents: []
  supersedes: []
  superseded_by: []
  conflicts: []
---

# 集成测试计划：agent 全仓 TypeScript 重构

## 一、测试策略

- 目标 commit：`582306a8675cea435ea33e53b8db82086947ff9f`；目标 tree：`b22e9a8f9913fb9b3faf8357839383b3e7abe389`。
- 范围：14 个 Scope Story 的全部 AC，覆盖 baseline/Oracle、生产 DSH、Learning Runtime、M001—M060、控制账本/命令、Safety/Watchdog、rehearsal 与 local cutover。
- 非目标：真实 production OS/IAM/network/certificate 部署验证；当前没有生产部署，本次 local decision 不外推为生产发布批准。
- 环境：macOS、Node 22.19.0、pnpm 11.7.0、DSH 0.1.0-rc.6、Cordis 4.0.1、SQLite fixtures；Python 源仅从 `python-baseline-v1` 审计，不在纯 TS HEAD 运行 pytest。
- 风险分级：生产入口/组合、Learning 隔离、控制/安全旁路、恢复、cutover tree/rollback 为 P0。

## 二、测试用例

| 用例 ID | 标题 | 关联 Story / AC | 优先级 | 类型 | 自动化 |
|---|---|---|---|---|---|
| IT-ATS-001 | baseline、Oracle 与回滚引用 | US-B0-001 / GWT-001—004、009—012 | P0 | baseline-contract | automated |
| IT-ATS-002 | Controlled DSH 组合与插件生命周期 | US-B1-001 / GWT-005—008 | P0 | production-runtime-lifecycle | automated |
| IT-ATS-003 | Learning Runtime 恢复与生产隔离 | US-B1-002 / GWT-013—014 | P0 | learning-isolation | automated |
| IT-ATS-004 | M001—M025 迁写语义 | US-B2-001/002 | P0 | legacy-semantic-parity | automated |
| IT-ATS-005 | M026—M060 运行/恢复/Team/工具/CLI | US-B2-003/004/005 | P0 | learning-runtime-recovery | automated |
| IT-ATS-006 | 控制账本与动态镜像 | US-B3-001 | P0 | control-ledger-replay | automated |
| IT-ATS-007 | 控制命令与现实回执 | US-B3-002 / GWT-019 | P0 | control-command-e2e | automated |
| IT-ATS-008 | Safety Executor 独立边界 | US-B4-001 / GWT-015—018 | P0 | safety-process-boundary | automated |
| IT-ATS-009 | Watchdog 与 recovery | US-B4-002 / GWT-020 | P0 | watchdog-recovery | automated |
| IT-ATS-010 | Rehearsal、local cutover、纯 TS 与 rollback | US-B5-001/002 / GWT-021—022 | P0 | release-cutover | automated |

## 三、需求与用例覆盖

| Story | AC | 覆盖用例 | 优先级 | 结论 |
|---|---|---|---|---|
| US-B0-001 | GWT-001—004、009—012 | IT-ATS-001 | P0 | 已覆盖 |
| US-B1-001 | GWT-005—008 | IT-ATS-002 | P0 | 已覆盖 |
| US-B1-002 | GWT-013—014 | IT-ATS-003 | P0 | 已覆盖 |
| US-B2-001/002 | M001—M025 | IT-ATS-004 | P0 | 已覆盖 |
| US-B2-003/004/005 | M026—M060 | IT-ATS-005 | P0 | 已覆盖 |
| US-B3-001 | Ledger/Projection | IT-ATS-006 | P0 | 已覆盖 |
| US-B3-002 | GWT-019 | IT-ATS-007 | P0 | 已覆盖 |
| US-B4-001 | GWT-015—018 | IT-ATS-008 | P0 | 已覆盖 |
| US-B4-002 | GWT-020 | IT-ATS-009 | P0 | 已覆盖 |
| US-B5-001/002 | GWT-021—022 | IT-ATS-010 | P0 | 已覆盖 |

## 四、执行 Suite

| Suite | 用例 | 命令 |
|---|---|---|
| baseline-and-evaluation | IT-ATS-001 | `pnpm baseline:verify && pnpm verify:legacy-test-map && pnpm evaluate:legacy-case` |
| all-typescript | IT-ATS-002—009 | `pnpm test && pnpm typecheck` |
| release-cutover | IT-ATS-010 | `pnpm composition:verify && pnpm install --frozen-lockfile && pnpm --dir profiles/controlled install --frozen-lockfile && pnpm --dir profiles/recovery install --frozen-lockfile && pnpm audit --prod --registry=https://registry.npmjs.org && pnpm start -- --help && pnpm start:dsh:recovery -- --help`，并机械核对 tree/.py/tag |

## 五、测试审核

- [x] Scope 内 14 个 Story / AC 均有结构化用例覆盖。
- [x] P0 主路径、反例、故障、恢复、安全旁路与 cutover 回滚已列入审核范围。
- [x] 环境、数据和执行命令已明确。
- [x] 测试人员已审核用例索引、target commit 与 SHA-256。
- [x] `test_review` 已记录审核人、时间和未解决意见数 0。

审核已通过：目标 commit 为 `582306a8675cea435ea33e53b8db82086947ff9f`，用例索引 SHA-256 为 `2c396550dcef63533055b18ab89f97be84119f81729b2904c3d952875c92de71`，未解决意见为 0。后续只允许执行这份冻结计划；若目标提交或用例索引发生漂移，必须退回本阶段重新审核。

```text
python3 scripts/validate-client-dev.py test-plan --plan Plans/自动化测试/2026-08-17-agent全仓TypeScript重构-集成测试计划.md
```

## 反馈（skill_run）

```yaml
skill_run:
  skill: test-generator
  workflow_stage: integration-test-plan
  plan: Plans/自动化测试/2026-08-17-agent全仓TypeScript重构-集成测试计划.md
  date: 2026-08-20
  contexts_used:
    - path: Plans/功能开发/2026-08-17-agent全仓TypeScript重构.stories.json
      utility: high
      reason: "覆盖 14 个 Story 的全部 AC，并确认最后 Story 已完成"
    - path: Plans/功能开发/2026-08-17-agent全仓TypeScript重构-US-B5-002.tdd.json
      utility: high
      reason: "冻结 local cutover commit/tree、纯 TS 状态、baseline rollback 与切换后回归"
    - path: Plans/技术方案/2026-08-17-智能体控制系统工程架构-v0.1.md
      utility: high
      reason: "覆盖生产 DSH、Learning 隔离、控制/安全边界和 ENG-012 local-only 约束"
  contexts_missing:
    - "测试人员对 case index SHA-256、target commit 和 10 条 P0 用例的正式审核"
  contexts_stale: []
  outcome: "已生成 10 条 P0 集成测试用例，覆盖 14 个 Story/全部 AC；计划保持草稿，等待测试审核"
  utility: high
  reason: "Story 全部完成后才进入计划阶段，且未擅自把用例标记为已审核或执行集成测试"
  outcome_status: pass
  revisit_needed: true
```

```yaml
skill_run:
  skill: resume-assistant
  workflow_stage: integration-test-plan
  plan: Plans/自动化测试/2026-08-17-agent全仓TypeScript重构-集成测试计划.md
  date: 2026-08-20
  contexts_used:
    - path: Plans/Epic/2026-08-17-agent全仓TypeScript重构.md
      utility: high
      reason: "重放 client-dev 当前阶段，确认仍由测试审核门禁阻塞"
    - path: Plans/自动化测试/2026-08-17-agent全仓TypeScript重构-集成测试计划.md
      utility: high
      reason: "从尚未审核的测试计划继续，未跳过 plan review"
  contexts_missing: []
  contexts_stale: []
  outcome: "目标 commit/tree 未漂移，恢复到 integration-test-plan 审核动作"
  utility: high
  reason: "避免把之前 Story TDD 的通过状态误当成集成测试计划已审核"
  outcome_status: pass
  revisit_needed: false
```

```yaml
skill_run:
  skill: test-generator
  workflow_stage: integration-test-plan
  plan: Plans/自动化测试/2026-08-17-agent全仓TypeScript重构-集成测试计划.md
  date: 2026-08-20
  contexts_used:
    - path: Plans/功能开发/2026-08-17-agent全仓TypeScript重构.stories.json
      utility: high
      reason: "人工复核 14 个 Story 的 33 条 AC 与结构化用例逐项精确覆盖"
    - path: Plans/自动化测试/2026-08-17-agent全仓TypeScript重构-集成测试计划.cases.json
      utility: high
      reason: "冻结 10 个 P0 自动化用例及其最终 SHA-256"
    - path: Plans/自动化测试/2026-08-17-agent全仓TypeScript重构-集成测试计划.review.json
      utility: high
      reason: "记录审核人、时间、目标 commit、用例哈希和零未解决意见"
  contexts_missing: []
  contexts_stale: []
  outcome: "补齐 controlled/recovery profile 的冻结安装与真实启动冒烟后，测试计划审核通过"
  utility: high
  reason: "审核在执行前完成，且把恢复路径从文字预期落实为可复现命令"
  outcome_status: pass
  revisit_needed: false
```
