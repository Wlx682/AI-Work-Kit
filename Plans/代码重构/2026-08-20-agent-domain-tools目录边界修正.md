---
tags: [代码重构, 智能体, TypeScript, implementation-design]
type: plan
category: 代码重构
status: 已完成
date: 2026-08-20
lifecycle_state: implementation-design
codebase_root: /Users/wanglongxiang/git/agent
implementation_design: Plans/代码重构/2026-08-20-agent-domain-tools目录边界修正.impl.json
---
# Agent domain-tools 目录边界修正

## 结论

`plugins/domain-tools` 不是 Cordis 插件：它没有 Cordis 依赖、没有 Service/Effect 生命周期，也没有被任何生产 Profile 或 Bundle 装配。它只是依赖 `@agent/contracts` 的纯工具结果契约库，因此迁移到 `packages/domain-tools`。

其余一级目录边界清楚，不做大搬家：

- `packages/`：框架无关的契约、领域模型和适配边界；
- `plugins/`：由 Cordis 装配、可安装和释放的进程内插件；
- `services/`：Safety Executor、Watchdog 等独立权限/进程服务；
- `bundles/`、`profiles/`：Cordis 分发组合与运行配置；
- `labs/`：LangGraph.js 学习 Runtime，不进入生产组合。

## TDD 验收

- Red：目录边界测试能识别 `plugins/domain-tools` 没有 Cordis peer dependency；
- Green：迁移后目录边界、原输出契约、历史 M044 映射全部通过；
- Refactor：根 typecheck、全量测试、pnpm frozen install、controlled/controlled-web 组合校验通过；
- 不改变 `@agent/domain-tools` 包名与公开 API。

## TDD 证据

```yaml
tdd_evidence:
  red:
    command: "nvm exec 22.19.0 corepack pnpm@11.7.0 vitest run tests/acceptance/workspace-boundaries.spec.ts"
    exit_code: 1
    observed_at: "2026-08-20T22:03:52+08:00"
    reason: "测试只报告 domain-tools 没有 Cordis peer dependency，准确复现纯包误入 plugins"
  green:
    command: "CI=true nvm exec 22.19.0 corepack pnpm@11.7.0 vitest run tests/acceptance/workspace-boundaries.spec.ts packages/domain-tools/test/output-contract.spec.ts tests/acceptance/legacy-test-map.spec.ts"
    exit_code: 0
    observed_at: "2026-08-20T22:06:01+08:00"
    commit: a43f611
  refactor:
    command: "pnpm install --frozen-lockfile && pnpm typecheck && pnpm test && pnpm composition:verify && pnpm composition:web:verify"
    exit_code: 0
    result: "74 test files / 227 tests passed；两份组合指纹验证通过"
  acceptance:
    - ac: "plugins 只包含声明 Cordis peer dependency 的生命周期插件"
      pass: true
    - ac: "@agent/domain-tools API 和输出 schema 拒绝语义不变"
      pass: true
    - ac: "M044 历史测试证据指向实际存在的新路径"
      pass: true
```

## 反馈（skill_run）

```yaml
skill_run:
  skill: implementation-design-assistant
  workflow_stage: implementation-design
  plan: Plans/代码重构/2026-08-20-agent-domain-tools目录边界修正.md
  date: 2026-08-20
  contexts_used:
    - path: /Users/wanglongxiang/git/agent/plugins/domain-tools
      utility: high
      reason: "确认该目录只有纯 TypeScript 工具输出契约，不具备 Cordis 插件生命周期"
    - path: /Users/wanglongxiang/git/agent/profiles/controlled/cordis.patch.yml
      utility: high
      reason: "确认生产 Profile 从未装配 domain-tools，迁移不会改变运行组合"
  contexts_missing: []
  contexts_stale:
    - "原控制系统工程落点把 domain-tools 规划为 Plugin，但最终实现并未形成 Cordis 插件"
  outcome: "把 domain-tools 迁移到 packages，并增加 workspace 目录边界回归测试"
  utility: high
  reason: "目录名重新表达真实运行边界，避免把纯库误解成已接入生产的 Cordis 插件"
```

```yaml
skill_run:
  skill: feature-dev-assistant
  workflow_stage: refactor-development
  plan: Plans/代码重构/2026-08-20-agent-domain-tools目录边界修正.md
  date: 2026-08-20
  contexts_used:
    - path: Plans/代码重构/2026-08-20-agent-domain-tools目录边界修正.impl.json
      utility: high
      reason: "限定迁移文件、目录依赖规则和组合哈希风险，避免扩大重构范围"
    - path: /Users/wanglongxiang/git/agent/tests/acceptance/legacy-test-map.spec.ts
      utility: high
      reason: "确保移动后历史 M044 测试证据仍可执行"
  contexts_missing: []
  contexts_stale: []
  outcome: "完成 domain-tools 迁移、目录边界门禁、锁文件与受控组合证据刷新"
  utility: high
  reason: "Red→Green 证明迁移修复了真实目录异常，并通过全仓回归阻止行为变化"
```
