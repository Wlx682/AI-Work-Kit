---
tags: [代码重构, 智能体, LangGraph, DSH, implementation-design]
type: plan
category: 代码重构
status: 已完成
date: 2026-08-20
lifecycle_state: implementation-design
codebase_root: /Users/wanglongxiang/git/agent
implementation_design: Plans/代码重构/2026-08-20-agent学习定义归位labs.impl.json
---
# Agent 学习定义归位 labs

## 用户裁决

当前 `@agent/agent-definition` 只服务 LangGraph.js 学习 Runtime，迁移到 `labs/shared/agent-definition`。生产 DSH 不复用该包；以后以独立 Agent Preset/Cordis 插件开发生产智能体。

同时删除顶层旧 `definitions/`、`prompts/` 副本。冻结 Python 基线仍由 evidence manifest、旧 commit/tag 和 evaluation fixtures 保留，不改变历史证据。

## 验收

- 生产 `packages/plugins/services/bundles/profiles/scripts` 不依赖学习定义；
- LangGraph Runtime 仍通过 `@agent/agent-definition` 加载定义；
- 顶层不存在重复的 `definitions/`、`prompts/`；
- M012-M016、M024 映射、类型检查、全量测试和两份 DSH 组合校验通过。

## TDD 证据

```yaml
tdd_evidence:
  red:
    command: "CI=true nvm exec 22.19.0 corepack pnpm@11.7.0 vitest run tests/acceptance/workspace-boundaries.spec.ts"
    exit_code: 1
    observed_at: "2026-08-20T22:19:28+08:00"
    reason: "仅报告 definitions/、prompts/、packages/agent-definition 三处学习定义越界"
  green:
    command: "CI=true nvm exec 22.19.0 corepack pnpm@11.7.0 vitest run tests/acceptance/workspace-boundaries.spec.ts labs/shared/agent-definition/test/*.spec.ts tests/acceptance/legacy-test-map.spec.ts labs/runtimes/langgraph-ts/test/roles.spec.ts labs/runtimes/langgraph-ts/test/team-runtime.spec.ts"
    exit_code: 0
    observed_at: "2026-08-20T22:22:32+08:00"
    result: "7 test files / 18 tests passed"
    commit: 15a41fb
  refactor:
    command: "pnpm install --frozen-lockfile && pnpm typecheck && pnpm test && pnpm composition:verify && pnpm composition:web:verify"
    exit_code: 0
    result: "74 test files / 228 tests passed；CLI/Web 组合验证通过"
  acceptance:
    - ac: "学习定义只位于 labs/shared/agent-definition"
      pass: true
    - ac: "生产 workspace 不依赖 @agent/agent-definition"
      pass: true
    - ac: "LangGraph Runtime 定义加载行为不变"
      pass: true
    - ac: "顶层 definitions/prompts 重复副本已删除"
      pass: true
```

## 反馈（skill_run）

```yaml
skill_run:
  skill: implementation-design-assistant
  workflow_stage: implementation-design
  plan: Plans/代码重构/2026-08-20-agent学习定义归位labs.md
  date: 2026-08-20
  contexts_used:
    - path: /Users/wanglongxiang/git/agent/packages/agent-definition
      utility: high
      reason: "确认包的当前消费者和可无行为迁移的完整资产边界"
    - path: /Users/wanglongxiang/git/agent/bundles/control-base/cordis.patch.yml
      utility: high
      reason: "确认生产 DSH 当前未装配 agent-definition，迁入 labs 符合实际边界"
    - path: /Users/wanglongxiang/git/agent/node_modules/@deepseek-ai/dsh/config/agent-presets/standard/agent.cordis.yml
      utility: high
      reason: "确认未来生产智能体应使用 DSH Agent Preset 的 Cordis 组合，而非学习 JSON loader"
  contexts_missing: []
  contexts_stale:
    - "旧工程落点把 agent-definition 视为双 Runtime 共享资产，但当前生产 DSH 没有消费者"
  outcome: "确认学习定义迁到 labs/shared，生产 DSH 智能体以后独立开发"
  utility: high
  reason: "消除学习资产看似已被生产 DSH 使用的误导，并保留未来原生 Agent Preset 边界"
```

```yaml
skill_run:
  skill: feature-dev-assistant
  workflow_stage: refactor-development
  plan: Plans/代码重构/2026-08-20-agent学习定义归位labs.md
  date: 2026-08-20
  contexts_used:
    - path: Plans/代码重构/2026-08-20-agent学习定义归位labs.impl.json
      utility: high
      reason: "限制迁移只影响学习包、workspace 和证据路径，不把学习定义装入 DSH 生产组合"
    - path: /Users/wanglongxiang/git/agent/tests/acceptance/workspace-boundaries.spec.ts
      utility: high
      reason: "用可执行门禁固定生产与学习定义边界"
  contexts_missing: []
  contexts_stale: []
  outcome: "agent-definition 迁入 labs/shared，删除顶层旧副本并保持 LangGraph 行为与 DSH 组合验证通过"
  utility: high
  reason: "用户选择的 Lab-only 边界已由 Red→Green 和全仓回归证明"
```
