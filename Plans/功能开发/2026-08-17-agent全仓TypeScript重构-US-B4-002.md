---
tags: [功能开发, B4, Watchdog, Recovery]
type: plan
category: 功能开发
status: 已完成
date: 2026-08-17
lifecycle_state: story-development
parent: Plans/功能开发/2026-08-17-agent全仓TypeScript重构.md
requirement_plan: Plans/需求分析/2026-08-17-agent全仓TypeScript重构.md
architecture_plan: Plans/技术方案/2026-08-17-智能体控制系统工程架构-v0.1.md
story_id: US-B4-002
story_points: 5
sprint_scope: false
tdd_evidence: Plans/功能开发/2026-08-17-agent全仓TypeScript重构-US-B4-002.tdd.json
implementation_design: Plans/功能开发/2026-08-17-agent全仓TypeScript重构-US-B4-002.impl.json
---
# US-B4-002：Watchdog 证明权限组合并在失联时自动降级

作为运维者，我想由独立 Watchdog 观察心跳、水位、组合与旁路证明，以便证明不完整时自动停止受控写并进入 read-only/recovery。

覆盖 `GWT-020`。普通 Profile/Patch/插件不得重新开放高权限写能力。

## 当前 Scope

- `US-B4-001` 已完成并有提交 `48f069d` 与 TDD 证据；用户回复“继续”后，本轮只激活依赖已满足的 `US-B4-002`。
- `US-B5-001` 已在用户再次回复“继续”后成为当前滚动 Scope；`US-B5-002` 保持 `sprint_scope=false`。
- 本 Story 已完成并提交 `72546b8`，现已退出滚动 Scope；后续 rehearsal 不改变本 Story 的完成事实。

## 实现落点设计草案

- 版本化证明契约：新增 `authority-attestation.v1`、`attestation-receipt.v1` 与 `watchdog-probe.v1`，冻结 Runtime/Executor 心跳、活动运行水位、composition fingerprint、凭证/旁路证明、短 TTL、降级原因和证据引用；缺失或 unknown 不能表达成可写。
- 纯领域判定：在 `safety-domain` 新增 authority gate 纯函数；只有 heartbeat、活动水位、composition、旁路证明全部 fresh 才产生 trusted，idle run 不因没有业务事件误判为停滞。
- 独立 Watchdog：新增 `services/watchdog` 独立进程，通过窄 Ports 读取 Runtime/Executor 只读 probes 和 owner-only 旁路证据，再把同一短时 attestation 分别投递 Runtime gate 与 Safety Executor；它不进入 Cordis Bundle/Profile，也不能执行现实动作。
- 双端失败关闭：Runtime 新增可逆 `plugins/authority-gate`，初始/过期/降级时让 `safety-client.submit` 本地返回 `WATCHDOG_DEGRADED`，但 query/evaluation 保持可用；独立 Executor 在 policy/Lease/target apply 前再次检查自己的最新证明，Runtime 卸载或绕过插件仍不能产生现实写。
- 水位与组合：authority-gate 只通过现有 `runtimeComposition.identity()` 与 `controlLedger.project(runId).throughSequence` 形成探针，不向 Watchdog 暴露数据库或写 Provider；组合不匹配立即降级。
- Recovery：新增固定 `profiles/recovery` 与独立 launcher，只含 DSH base/headless 的只读恢复闭包，不装 safety-client、control-supervisor、Watchdog、Executor 或现实写 Provider，并拒绝任意 `--profile/--patch` 覆盖。
- 组合边界：authority contract/gate 和受控 Bundle/Profile 进入 composition fingerprint；独立 Watchdog 服务本体不成为 Cordis provider。Watchdog-only identity/evidence 配置不得进入 Runtime 环境。

## Red 设计

1. 契约 Red：trusted/degraded、TTL、反向时间、fingerprint、reasonCodes、probe 与未知字段严格拒绝。
2. 领域 Red：healthy 放行；Runtime/Executor 失联、active 水位停滞、composition 漂移、旁路缺证和证明过期全部 `WATCHDOG_DEGRADED`；idle 水位稳定不误报。
3. Runtime/Executor 双门禁 Red：authority-gate 初始只读、过期自动只读、dispose 后 safety-client 不能 Ready；绕过 Runtime gate 直连 Executor 仍在 target 前拒绝。
4. Watchdog 服务 Red：双 probe + 旁路证据全绿才续签；任一 sink/probe 失败均降级，旧 trusted 不能无限续命。
5. 纵向故障 Red：真实派生独立 Watchdog 与 Executor，注入心跳失联/水位停滞后证明 Runtime mode=read_only、Executor 返回 degraded、目标新增写为 0；recovery Profile 可启动且无写入口。

## 停止条件

- 需要 fork/vendoring DSH、升级固定 rc.6/Cordis 4.0.1 或引入未经审计的运行时框架依赖。
- 无法在独立 Executor 的 Lease/target 前验证 fresh AuthorityAttestation，只能依赖可卸载 Runtime 插件。
- Recovery Profile 仍包含 safety-client/control-supervisor/现实写 Provider，或允许未记录 profile/patch overlay。
- 需要提前执行 B5 rehearsal、删除 Python、切换生产入口或把本地 UDS fixture 冒充真实生产 IAM/网络签署。

机器真理源：`Plans/功能开发/2026-08-17-agent全仓TypeScript重构-US-B4-002.impl.json`；实现已按 `confirmed=true` 完成，TDD 真理源为 `Plans/功能开发/2026-08-17-agent全仓TypeScript重构-US-B4-002.tdd.json`。

## 实现证据

- 代码提交：`72546b8bed912da8e5e06a299475c671c9856d27`。
- 新增版本化 AuthorityAttestation/Receipt/Probe 契约与纯 authority 判定；只有 fresh 心跳、活动水位、冻结组合和完整旁路证明才可写。
- 独立 Watchdog 不进入 Cordis Profile；Runtime authority-gate 与独立 Executor 在现实写前分别失败关闭，任一 sink 或严格回执失败都转 degraded。
- 故障注入证明心跳失联、水位停滞和 Watchdog 退出后新增现实写为 0；idle 水位稳定不误报。
- 固定 recovery Profile 可启动且无现实写 Provider，拒绝任意 profile/patch overlay；独立锁不再解析 DSH rc.7。
- 目标 `25/25`、全仓 TypeScript `192/192`、Python `60/60`、typecheck、三处 frozen install、官方 registry audit、composition verify 与 controlled/recovery 双 smoke 全部通过。
- 组合指纹：`99ddf6cdc298937bb60ce7707aee8afe302b715e3e61b872ccf4a84235826516`。
- TDD 真理源：`Plans/功能开发/2026-08-17-agent全仓TypeScript重构-US-B4-002.tdd.json`。

续做：当前滚动 Scope 已切换到 `US-B5-001`；本 Story 无剩余开发任务。

## 反馈（skill_run）

```yaml
skill_run:
  skill: task-splitter
  workflow_stage: story-split
  plan: Plans/功能开发/2026-08-17-agent全仓TypeScript重构-US-B4-002.md
  date: 2026-08-20
  contexts_used:
    - path: Plans/功能开发/2026-08-17-agent全仓TypeScript重构-US-B4-001.md
      utility: high
      reason: "确认 Safety Executor、幂等与效果核验已经完成，Watchdog 可在其上建立独立证明门禁"
    - path: Plans/技术方案/2026-08-17-智能体控制系统工程架构-v0.1.md
      utility: high
      reason: "确认下一条依赖满足的纵向 Story 是 US-B4-002，并维持 GWT-020/ENG-007/009 边界"
  contexts_missing: []
  contexts_stale: []
  outcome: "只激活 US-B4-002；US-B4-001 退出滚动 Scope，B5 两条 Story 未扩张"
  utility: high
  reason: "将看板当前 Story 与真实滚动 Scope 对齐，同时继续阻止误入最终集成测试"
  outcome_status: pass
  revisit_needed: false
```

```yaml
skill_run:
  skill: resume-assistant
  workflow_stage: implementation-design
  plan: Plans/功能开发/2026-08-17-agent全仓TypeScript重构-US-B4-002.md
  date: 2026-08-20
  contexts_used:
    - path: Plans/Epic/2026-08-17-agent全仓TypeScript重构.md
      utility: high
      reason: "回放当前仍为逐 Story TDD，B4-002 未完成是下一工作项而非集成测试入口"
    - path: Plans/功能开发/2026-08-17-agent全仓TypeScript重构-US-B4-001.md
      utility: high
      reason: "核验前置 Story 的提交、TDD 和独立 Executor 边界均已完成"
    - path: Plans/功能开发/2026-08-17-agent全仓TypeScript重构-US-B4-002.md
      utility: high
      reason: "续接当前唯一 Scope、GWT-020 和 implementation-design 停止条件"
  contexts_missing: []
  contexts_stale: []
  outcome: "从 US-B4-001 完成态恢复并切换到 US-B4-002 implementation-design；未创建 Red 或业务代码"
  utility: high
  reason: "依据事件/文件事实选择下一条依赖满足 Story，未把全局未完成提示误当成当前 Story 报错"
  outcome_status: pass
  revisit_needed: false
```

```yaml
skill_run:
  skill: resume-assistant
  workflow_stage: story-development
  plan: Plans/功能开发/2026-08-17-agent全仓TypeScript重构-US-B4-002.md
  date: 2026-08-20
  contexts_used:
    - path: Plans/功能开发/2026-08-17-agent全仓TypeScript重构-US-B4-002.md
      utility: high
      reason: "续接用户已确认的 implementation-design、GWT-020、Red 与停止条件"
    - path: Plans/技术方案/2026-08-17-智能体控制系统工程架构-v0.1.md
      utility: high
      reason: "持续约束独立 Watchdog、双端失败关闭、短 TTL 和 read-only recovery"
  contexts_missing: []
  contexts_stale: []
  outcome: "恢复并完成 US-B4-002；未自动激活 B5，也未进入最终集成测试"
  utility: high
  reason: "从已确认落点继续完成真实 Red→Green→Refactor、跨进程故障验收和提交"
  outcome_status: pass
  revisit_needed: false
```

```yaml
skill_run:
  skill: implementation-design-assistant
  workflow_stage: implementation-design
  plan: Plans/功能开发/2026-08-17-agent全仓TypeScript重构-US-B4-002.md
  date: 2026-08-20
  contexts_used:
    - path: Plans/需求分析/2026-08-17-agent全仓TypeScript重构.md
      utility: high
      reason: "落实 GWT-020 与 P0-3 对心跳、水位、组合、凭证旁路证明和 read-only 降级的约束"
    - path: Plans/技术方案/2026-08-17-智能体控制系统工程架构-v0.1.md
      utility: high
      reason: "落实 ENG-007/009、AuthorityAttestation API、WATCHDOG_DEGRADED 与独立 recovery Profile"
    - path: Plans/功能开发/2026-08-17-agent全仓TypeScript重构-US-B4-001.md
      utility: high
      reason: "在已完成的 Safety Executor/Runtime client/凭证隔离上设计不可绕过的双端 authority gate"
    - path: Contexts/决策/Skill反馈协议.md
      utility: high
      reason: "按有 Plan 任务协议记录落点门禁与用户待确认项"
  contexts_missing:
    - "用户对 US-B4-002 文件落点、双端失败关闭、Red 与停止条件的确认"
  contexts_stale: []
  outcome: "US-B4-002 落点草案完成并停在 confirmed=false；未创建 Red、Watchdog 实现、recovery Profile 或最终集成产物"
  utility: high
  reason: "把独立 Watchdog、短 TTL 证明、活动水位、Runtime/Executor 双门禁与 read-only recovery 落到可验证文件和进程边界"
  outcome_status: pass
  revisit_needed: false
```

```yaml
skill_run:
  skill: feature-dev-assistant
  workflow_stage: story-development
  plan: Plans/功能开发/2026-08-17-agent全仓TypeScript重构-US-B4-002.md
  date: 2026-08-20
  contexts_used:
    - path: Plans/需求分析/2026-08-17-agent全仓TypeScript重构.md
      utility: high
      reason: "逐项验收 GWT-020 的心跳、水位、组合、旁路证明和失联降级"
    - path: Plans/技术方案/2026-08-17-智能体控制系统工程架构-v0.1.md
      utility: high
      reason: "落实 ENG-007/009、AuthorityAttestation、双端门禁与固定 recovery Profile"
    - path: Plans/功能开发/2026-08-17-agent全仓TypeScript重构-US-B4-001.md
      utility: high
      reason: "复用已完成的独立 Safety Executor、持久幂等和现实写计数边界"
    - path: Plans/功能开发/2026-08-17-agent全仓TypeScript重构-US-B4-002.tdd.json
      utility: high
      reason: "记录真实 Red、Green、Refactor、全仓回归、提交与 GWT-020 验收证据"
  contexts_missing: []
  contexts_stale: []
  outcome: "US-B4-002 已完成并提交 72546b8；B5 未自动激活，未进入最终集成测试"
  utility: high
  reason: "独立 Watchdog、严格证明回执、活动水位、Runtime/Executor 双门禁与无写 recovery 均有可执行证据"
  outcome_status: pass
  friction: "recovery 独立 workspace 的重复 DSH 直接依赖曾解析到 rc.7；移除重复依赖后复用根工作区固定 rc.6，可冻结安装且无版本漂移"
  revisit_needed: false
```
