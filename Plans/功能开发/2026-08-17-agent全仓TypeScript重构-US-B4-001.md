---
tags: [功能开发, B4, Safety, ActionIntent]
type: plan
category: 功能开发
status: 已完成
date: 2026-08-17
lifecycle_state: story-development
parent: Plans/功能开发/2026-08-17-agent全仓TypeScript重构.md
requirement_plan: Plans/需求分析/2026-08-17-agent全仓TypeScript重构.md
architecture_plan: Plans/技术方案/2026-08-17-智能体控制系统工程架构-v0.1.md
story_id: US-B4-001
story_points: 8
sprint_scope: false
tdd_evidence: Plans/功能开发/2026-08-17-agent全仓TypeScript重构-US-B4-001.tdd.json
implementation_design: Plans/功能开发/2026-08-17-agent全仓TypeScript重构-US-B4-001.impl.json
---
# US-B4-001：经独立 Safety Executor 安全执行并对账现实效果

作为 Runtime，我想只提交 ActionIntent，由独立身份的 Executor 授权、幂等执行和核验效果，以便在无长期写凭证时完成受控现实动作。

覆盖 `GWT-015—018`。必须验证旁路拒绝、重复 Intent 去重和 `EFFECT_UNKNOWN` reconcile；同进程 mock 不构成生产证明。

## 当前 Scope

- `US-B3-002` 已完成并有提交与 TDD 证据；用户回复“继续”后，本轮只激活依赖已满足的 `US-B4-001`。
- `US-B4-002`、`US-B5-001`、`US-B5-002` 保持 `sprint_scope=false`；本 Story 不提前实现 Watchdog、recovery Profile 或最终 cutover。
- 用户已回复“继续”确认 implementation-design；本 Story 已在提交 `48f069d` 完成 Red→Green→Refactor→纵向 smoke。`US-B4-002` 尚未激活，也未进入最终集成测试。

## 实现落点设计草案

- 共享契约：新增独立于 Learning `action.ts` 的 `action-intent.v1` / `action-receipt.v1`，冻结 ActionIntent、最小 Lease、分段 receipt、统一错误与 `EFFECT_UNKNOWN`；unknown 不能表达成 succeeded/verified。
- 纯领域层：新增零 Cordis/DSH/HTTP/SQLite/环境变量依赖的 `packages/safety-domain`，只负责策略、Lease 绑定、canonical 幂等内容和 receipt 单调状态机。
- Runtime 客户端：新增 `plugins/safety-client` Cordis Service，仅持 ActionIntent endpoint，通过 HTTP over Unix Socket（跨主机为 mTLS HTTPS）提交/查询；受控 Profile 不依赖 Executor、策略、数据库或目标 adapter。
- 独立执行器：新增 `services/safety-executor` 独立进程，以 Provider Ports 隔离 Policy、Intent Store、Target Action、Effect Oracle 和 Reconcile Queue；策略、数据库及目标凭证只由该进程读取。
- 持久化与幂等：独立 SQLite WAL/FULL 在现实调用前持久化 canonical intent 与 `executing`；相同 key 同内容只返回旧执行引用，异内容冲突。执行中断或超时只追加 `effect_unknown` 和唯一 reconcile task，禁止自动重放现实写。
- 凭证/旁路：受控 DSH launcher 发现 Executor-only 策略、数据库或目标 token 即拒绝启动；纵向安全测试派生真实 Executor 子进程，目标 fixture 只接受 Executor 专属 token，Runtime 直连目标、越 scope/风险或尝试改策略均不得发生现实写。
- 组合与边界：只把 safety-client 纳入 controlled Bundle/Profile 和 Runtime composition fingerprint；Safety Executor 不成为可卸载 Cordis plugin。Watchdog、AuthorityAttestation 自动降级、recovery Profile 和最终生产 IAM/rehearsal 留给后续 Story。

## Red 设计

1. 契约 Red：Intent/Receipt/Lease 闭集字段、版本化 Schema、stage/status 合法组合和 unknown 不得 verified。
2. 领域 Red：scope/risk/evidence/composition 策略拒绝、最小 Lease 绑定/过期、完整 receipt 链、跳段与终态保护。
3. 服务 Red：合法动作、policy denied 零 target call、重复 canonical intent 现实动作一次、同 key 异内容冲突、执行中断转 unknown/reconcile。
4. 持久化 Red：WAL/FULL、重开幂等、append-only receipt、崩溃后不盲重放和损坏失败关闭。
5. 纵向 Red：真实 Runtime client → UDS → 独立 Executor 子进程 → 凭证隔离目标 fixture → Effect Oracle；另以 bypass 与 timeout 故障注入覆盖 GWT-016/018。

机器真理源：`Plans/功能开发/2026-08-17-agent全仓TypeScript重构-US-B4-001.impl.json`；用户已回复“继续”确认文件落点、依赖方向、Red 与停止条件，当前 `confirmed=true`，进入 Red。

## 实现证据

- 代码提交：`48f069d3ad9252e0d764e817191e3839167c8984`。
- `action-intent.v1` / `action-receipt.v1`、纯 `safety-domain` 和严格 assertion 保证闭集字段、最小 Lease、单调 receipts 及 unknown 不得 verified；Learning action 契约保持隔离。
- `services/safety-executor` 是独立进程而非 Cordis plugin；本地 UDS 与 SQLite 均为 owner-only `0600`，跨主机服务端/客户端强制 mTLS + TLS 1.3。受控 Profile 只装 safety-client，不含 Executor、策略、数据库或目标 adapter。
- 真实子进程纵向测试中，Executor 独占 target token；Runtime 直连目标为 403、策略修改路由为 404、越 scope/composition/tool 为 denied 且现实写为 0。受控 launcher 检出 Executor-only 配置即拒绝启动。
- canonical idempotency 在 SQLite 重开后仍稳定；重复 Intent 现实写一次，同 key 异内容在顺序与 in-flight 并发场景均冲突。durable `executing/applied` 部分链重启后只转 `effect_unknown + reconcile`，不盲目重放。
- 目标 timeout 故障注入让现实写可能已发生但响应缺失；Executor 追加 unknown receipt 和唯一 reconcile task，重复提交不触发第二次 target 调用。
- Safety 目标 `22/22`、全仓 TypeScript `174/174`、Python `60/60`、typecheck、双 frozen install、官方 registry audit、composition verify 与受控 DSH smoke 全部通过。
- 受控组合保持 DSH `0.1.0-rc.6` / Cordis `4.0.1`，新指纹为 `134d29a14cff20f35f405a55edd770ded9a219e22194efcf8305b77f849ce324`。
- TDD 真理源：`Plans/功能开发/2026-08-17-agent全仓TypeScript重构-US-B4-001.tdd.json`。

续做：`/resume plan=Plans/功能开发/2026-08-17-agent全仓TypeScript重构.md 进度=next-story-scope`

## 反馈（skill_run）

```yaml
skill_run:
  skill: implementation-design-assistant
  workflow_stage: implementation-design
  plan: Plans/功能开发/2026-08-17-agent全仓TypeScript重构-US-B4-001.md
  date: 2026-08-20
  contexts_used:
    - path: Plans/需求分析/2026-08-17-agent全仓TypeScript重构.md
      utility: high
      reason: "落实 GWT-015—018 与已确认的 Safety Executor v0.1 独立进程、凭证、UDS/mTLS、Lease、幂等和 unknown 边界"
    - path: Plans/技术方案/2026-08-17-智能体控制系统工程架构-v0.1.md
      utility: high
      reason: "约束 ENG-007/008/010、ActionIntent API/状态机、Runtime→Executor→Reality 单向依赖与后续 Watchdog 边界"
    - path: Plans/功能开发/2026-08-17-agent全仓TypeScript重构-US-B3-002.md
      utility: high
      reason: "确认前置五段控制回执与 durable ledger 已完成，同时避免把 DSH tools.restrict 冒充生产安全权限"
    - path: Contexts/决策/Skill反馈协议.md
      utility: high
      reason: "按有 Plan 任务协议记录落点门禁与待确认上下文"
  contexts_missing:
    - "用户对 US-B4-001 文件落点、依赖方向、Red 与停止条件的确认"
  contexts_stale: []
  outcome: "US-B4-001 已切为唯一滚动 Scope，独立 Safety Executor 落点完成并停在 confirmed=false；未创建 Red、业务代码或集成测试产物"
  utility: high
  reason: "把同进程 mock 排除在验收证据外，并将凭证隔离、幂等一次执行与 effect unknown reconcile 落到可验证文件和进程边界"
  outcome_status: pass
  revisit_needed: false
```

```yaml
skill_run:
  skill: resume-assistant
  workflow_stage: story-development
  plan: Plans/功能开发/2026-08-17-agent全仓TypeScript重构-US-B4-001.md
  date: 2026-08-20
  contexts_used:
    - path: Plans/Epic/2026-08-17-agent全仓TypeScript重构.md
      utility: high
      reason: "确认 Epic 仍处于逐 Story TDD，当前只完成 US-B4-001 而不跳转最终集成测试"
    - path: Plans/功能开发/2026-08-17-agent全仓TypeScript重构-US-B4-001.md
      utility: high
      reason: "读取当前唯一 Scope、已确认落点、GWT-015—018 与停止条件"
    - path: Plans/技术方案/2026-08-17-智能体控制系统工程架构-v0.1.md
      utility: high
      reason: "保持独立进程/身份/凭证、UDS/mTLS 与后续 Watchdog/AuthorityAttestation 边界"
  contexts_missing: []
  contexts_stale: []
  outcome: "用户回复‘继续’后确认 US-B4-001 落点门禁，并从 implementation-design 恢复到 Red"
  utility: high
  reason: "开发严格继承了凭证隔离、canonical 幂等、独立效果核验和 unknown 禁止盲重试的边界"
  outcome_status: pass
  revisit_needed: false
```

```yaml
skill_run:
  skill: feature-dev-assistant
  workflow_stage: story-development
  plan: Plans/功能开发/2026-08-17-agent全仓TypeScript重构-US-B4-001.md
  date: 2026-08-20
  contexts_used:
    - path: Plans/需求分析/2026-08-17-agent全仓TypeScript重构.md
      utility: high
      reason: "逐项验收 GWT-015—018 的合法执行、旁路拒绝、幂等一次写和 effect unknown reconcile"
    - path: Plans/技术方案/2026-08-17-智能体控制系统工程架构-v0.1.md
      utility: high
      reason: "守住 ENG-007/008/010、独立权限域、版本化 API、UDS/mTLS 与 Watchdog 后续边界"
    - path: Plans/功能开发/2026-08-17-agent全仓TypeScript重构-US-B3-002.md
      utility: high
      reason: "继承已完成的控制回执与 composition 事实，同时不把 tools.restrict 冒充 Safety 权限"
    - path: Plans/功能开发/2026-08-17-agent全仓TypeScript重构-US-B4-001.md
      utility: high
      reason: "记录真实 Red、Green、Refactor、跨进程 smoke、提交和四条 AC 证据"
  contexts_missing: []
  contexts_stale: []
  outcome: "US-B4-001 已完成并提交 48f069d；未自动激活 US-B4-002，也未进入最终集成测试"
  utility: high
  reason: "独立 Executor、凭证旁路、持久幂等、效果核验与 timeout reconcile 均有真实子进程和目标侧调用证据"
  outcome_status: pass
  friction: "根 Vitest 原先未包含 services/**/*.spec.ts；已纳入测试发现，防止独立 Executor Red 静默漏扫"
  revisit_needed: false
```
