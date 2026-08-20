---
tags: [功能开发, B3, Supervisor, Receipt]
type: plan
category: 功能开发
status: 已完成
date: 2026-08-17
lifecycle_state: story-development
parent: Plans/功能开发/2026-08-17-agent全仓TypeScript重构.md
requirement_plan: Plans/需求分析/2026-08-17-agent全仓TypeScript重构.md
architecture_plan: Plans/技术方案/2026-08-17-智能体控制系统工程架构-v0.1.md
story_id: US-B3-002
story_points: 8
sprint_scope: false
tdd_evidence: Plans/功能开发/2026-08-17-agent全仓TypeScript重构-US-B3-002.tdd.json
implementation_design: Plans/功能开发/2026-08-17-agent全仓TypeScript重构-US-B3-002.impl.json
---
# US-B3-002：下发控制命令并查看分段回执与现实结果

作为监督者，我想发出 pause/restrict/stop 并查看 intercepted 到 effect_verified 的分段回执，以便区分命令已收到、已应用和现实效果已验证。

覆盖 `GWT-019`。Waterfall 被短路、接纳点不匹配或外部结果未知时不得宣称命令完成。

## 当前 Scope

- 用户在 `US-B3-001` 完成后回复“继续”，因此本轮只激活 `US-B3-002`。
- 前置 `US-B3-001` 已完成并有提交与 TDD 证据；其余 4 个未完成 Story 保持 `sprint_scope=false`。
- 本 Story 已在提交 `27d1021` 完成 Red→Green→Refactor→纵向 smoke；用户后续回复“继续”后，本 Story 已退出滚动 Scope，唯一 Scope 切换为 `US-B4-001`，仍未进入最终集成测试。

## 实现落点设计草案

- 共享契约：在 `packages/contracts` 新增版本化 `control-command.v1` / `control-receipt.v1`，冻结 pause、restrict、stop 的预期接纳点和回执状态；unknown 不能表达成 verified。
- 纯领域层：新增零 Cordis/DSH/SQLite 依赖的 `packages/control-domain`，只负责 `intercepted → delegated → admitted → applied → effect_verified` 单调 waterfall、完成判定与失败关闭。
- 运行时适配：在 `packages/dsh-bridge` 使用 DSH rc.6 的 `agent/pre-step`、`Agent.cancel()`、`whenIdle()` 与 agent-scoped `tools.restrict()`；pause/stop 同时持有可撤销 pre-step barrier，插件卸载必须清理。
- 监督插件：新增 `plugins/control-supervisor`，逐段调用 Control Ledger 的窄 `appendFacts` 端口形成 durable receipts；用 innermost 私有 Symbol continuation proof 检测 Cordis waterfall 短路。
- 受控组合：将 ledger + supervisor 显式加入 controlled Bundle/Profile，生产账本路径只接受 `AGENT_CONTROL_LEDGER_PATH`，缺失即失败关闭。
- 边界：`tools.restrict()` 只是 Agent 可见工具面的过滤，不是 IAM/凭证/安全权限证明；本 Story 不实现 ActionIntent、Lease、Safety Executor、Watchdog、HTTP 或现实写。

## Red 设计

1. 契约 Red：三类 command、固定接纳点、条件字段、JSON 可序列化与非法状态失败关闭。
2. 领域 Red：完整五段链、跳段、重复、短路、unknown、接纳点不匹配。
3. DSH adapter Red：真实 waterfall shape 下 pause 保留 inbox、stop 丢弃 inbox、restrict 可见面与 disposer、agent 缺失、dispose 清理。
4. Supervisor Red：幂等、同 ID 异内容冲突、stale basis、外层 listener 短路、verify unknown 不得完成。
5. 纵向 Red：Cordis → supervisor → DSH adapter → SQLite 五段事实 → 重开数据库后回执一致。

机器真理源：`Plans/功能开发/2026-08-17-agent全仓TypeScript重构-US-B3-002.impl.json`；用户已回复“继续”确认，当前 `confirmed=true`，进入 Red。

## 实现证据

- 代码提交：`27d1021cd6fac88358e5e50c72f49d7cdb40d113`。
- `control-command.v1` / `control-receipt.v1` 具备闭集类型、JSON Schema 与运行时失败关闭校验；纯 `control-domain` 不依赖 Cordis、DSH、SQLite 或环境变量。
- pause/stop 通过 rc.6 `agent/pre-step` barrier + `Agent.cancel()/whenIdle()` 核验；restrict 只核验 agent-scoped 工具可见面，明确不冒充安全权限证明。
- Supervisor 对每段 receipt 单独 durable append；真实 Cordis listener 不调用或替换 `next()` 时，私有 continuation proof 阻止伪成功。
- 相同 canonical command 幂等返回旧链，同 ID 异内容冲突；stale basis、部分链、接纳点错误、live agent 缺失与 effect unknown 均不得 `completed=true`。
- ledger + supervisor 已进入 controlled Bundle/Profile；数据库路径由 `AGENT_CONTROL_LEDGER_PATH` 显式注入，组合指纹为 `a3a376cbcfbce0a61b09dc34332e0d61291cdf928fcffa54f3da7bf64e4a6e18`。
- 目标回归 `33/33`、全仓 TypeScript `152/152`、Python `60/60`、typecheck、双 frozen install、官方 registry audit、composition verify 和受控 DSH smoke 均通过。
- TDD 真理源：`Plans/功能开发/2026-08-17-agent全仓TypeScript重构-US-B3-002.tdd.json`。

续做：`/resume plan=Plans/功能开发/2026-08-17-agent全仓TypeScript重构.md 进度=next-story-scope`

## 反馈（skill_run）

```yaml
skill_run:
  skill: implementation-design-assistant
  workflow_stage: implementation-design
  plan: Plans/功能开发/2026-08-17-agent全仓TypeScript重构-US-B3-002.md
  date: 2026-08-18
  contexts_used:
    - path: Plans/需求分析/2026-08-17-agent全仓TypeScript重构.md
      utility: high
      reason: "落实 GWT-019 的唯一命令、预期接纳点、五段回执和外部结果未知不得完成"
    - path: Plans/技术方案/2026-08-17-智能体控制系统工程架构-v0.1.md
      utility: high
      reason: "约束 contracts/domain/framework 隔离、版本化 JSON Schema、SQLite Provider Port 与 B4 Safety 边界"
    - path: Plans/功能开发/2026-08-17-agent全仓TypeScript重构-US-B3-001.md
      utility: high
      reason: "复用已完成的 durable Control Ledger 与 projection，而不另建第二套事实存储"
    - path: Contexts/决策/Skill反馈协议.md
      utility: high
      reason: "按有 Plan 任务协议记录落点门禁与待确认上下文"
  contexts_missing:
    - "用户对 US-B3-002 文件落点、依赖方向、Red 与停止条件的确认"
  contexts_stale: []
  outcome: "US-B3-002 落点草案完成并停在 confirmed=false；未创建 Red、业务代码或 B4 Safety Executor"
  utility: high
  reason: "将控制回执闭环拆成可验证的契约、纯领域、DSH adapter、Supervisor 与 Ledger 持久化边界"
  outcome_status: pass
  revisit_needed: false
```

```yaml
skill_run:
  skill: resume-assistant
  workflow_stage: story-development
  plan: Plans/功能开发/2026-08-17-agent全仓TypeScript重构-US-B3-002.md
  date: 2026-08-18
  contexts_used:
    - path: Plans/Epic/2026-08-17-agent全仓TypeScript重构.md
      utility: high
      reason: "确认 Epic 仍处于逐 Story TDD，不能跳到最终集成测试"
    - path: Plans/功能开发/2026-08-17-agent全仓TypeScript重构-US-B3-002.md
      utility: high
      reason: "确认当前唯一 Scope、GWT-019 纵向边界与待确认落点"
    - path: Plans/技术方案/2026-08-17-智能体控制系统工程架构-v0.1.md
      utility: high
      reason: "保持 Control Supervisor、Ledger、DSH bridge 与 B4 Safety 的依赖隔离"
  contexts_missing: []
  contexts_stale: []
  outcome: "用户回复‘继续’后确认 US-B3-002 落点门禁，并从 implementation-design 恢复到 Red"
  utility: high
  reason: "开发将严格继承逐段 durable receipt、waterfall 短路检测与 unknown 不得完成的边界"
  outcome_status: pass
  revisit_needed: false
```

```yaml
skill_run:
  skill: feature-dev-assistant
  workflow_stage: story-development
  plan: Plans/功能开发/2026-08-17-agent全仓TypeScript重构-US-B3-002.md
  date: 2026-08-18
  contexts_used:
    - path: Plans/需求分析/2026-08-17-agent全仓TypeScript重构.md
      utility: high
      reason: "逐项验收 GWT-019 的三类命令、五段回执和效果核验"
    - path: Plans/技术方案/2026-08-17-智能体控制系统工程架构-v0.1.md
      utility: high
      reason: "守住 ENG-006/008/012、typed Cordis event、SQLite Provider 与 B4 Safety 边界"
    - path: Plans/功能开发/2026-08-17-agent全仓TypeScript重构-US-B3-001.md
      utility: high
      reason: "复用已完成的 append-only Control Ledger、WAL/FULL durability 与重放语义"
    - path: Plans/功能开发/2026-08-17-agent全仓TypeScript重构-US-B3-002.md
      utility: high
      reason: "记录真实 Red、Green、Refactor、smoke、提交与 GWT-019 完成证据"
  contexts_missing: []
  contexts_stale: []
  outcome: "US-B3-002 已完成并提交 27d1021；未自动激活 B4，也未进入最终集成测试"
  utility: high
  reason: "pause/restrict/stop 的五段 durable receipt、短路证明与 unknown 失败关闭均有自动化纵向证据"
  outcome_status: pass
  friction: "默认 npmmirror registry 不提供 audit endpoint；改用官方 npm registry 后确认无已知漏洞"
  revisit_needed: false
```
