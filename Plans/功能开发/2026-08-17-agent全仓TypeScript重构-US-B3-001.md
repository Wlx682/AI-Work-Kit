---
tags: [功能开发, B3, Ledger, SQLite]
type: plan
category: 功能开发
status: 已完成
date: 2026-08-17
lifecycle_state: story-development
parent: Plans/功能开发/2026-08-17-agent全仓TypeScript重构.md
requirement_plan: Plans/需求分析/2026-08-17-agent全仓TypeScript重构.md
architecture_plan: Plans/技术方案/2026-08-17-智能体控制系统工程架构-v0.1.md
story_id: US-B3-001
story_points: 8
sprint_scope: false
tdd_evidence: Plans/功能开发/2026-08-17-agent全仓TypeScript重构-US-B3-001.tdd.json
implementation_design: Plans/功能开发/2026-08-17-agent全仓TypeScript重构-US-B3-001.impl.json
---
# US-B3-001：从 SQLite 控制账本重放 DSH 运行动态镜像

作为监督者，我想按稳定序号查看并重放 DSH 控制事实，以便从不可变事实重建动态镜像，而不是相信运行时自报状态。

覆盖 append-only、幂等、durable commit、稳定 sequence、projection state hash 与损坏恢复；遵循 ENG-012 Provider Port。

## 一、输入

- 父 Plan：`Plans/功能开发/2026-08-17-agent全仓TypeScript重构.md`。
- 需求 Plan：`Plans/需求分析/2026-08-17-agent全仓TypeScript重构.md`，Story AC 为 `AC-B3-APPEND/REPLAY/IDEMPOTENCY/DURABILITY`。
- 架构 Plan：`Plans/技术方案/2026-08-17-智能体控制系统工程架构-v0.1.md`，约束为 `ENG-006/008/012`。

## 当前 Scope

- 用户在 `US-B2-005` 完成后回复“继续”，因此本轮只激活 `US-B3-001`。
- 前置 `US-B1-001`、`US-B2-002` 均已完成并有 TDD/提交证据；其余 5 个未完成 Story 保持 `sprint_scope=false`。
- 用户已确认实现落点设计；本 Story 已完成 Red→Green→Refactor 与 integration smoke，后续 Story 仍未激活。

## 实现落点设计草案

机器真理源：`Plans/功能开发/2026-08-17-agent全仓TypeScript重构-US-B3-001.impl.json`；用户回复“继续”后当前 `confirmed=true`。

- 事实边界：新增纯 TS `control-fact.v1` 与 `dsh-runtime-projection.v1`；ControlFact 使用独立连续 sequence，DSH session seq/type 只进入 `sourceRefs`，不复制或改写 Session Log。
- DSH 接入：`packages/dsh-bridge` 归一化 rc.6 的 `session/event`、`session/flush` 与 agent lifecycle/status；Ledger 插件不直接依赖上游 payload。
- Durable 边界：`session/event` 只进入内存 pending buffer；只有 awaited `session/flush` 内的 SQLite `WAL + synchronous=FULL` 批量事务成功后，事实才对 query/replay 可见。
- 幂等/序号：相同 idempotency key + 相同 canonical 内容返回原事实且不增序号；同 key 不同内容冲突失败，不覆盖历史。
- Projection：按事实前缀纯函数重建动态镜像，canonical SHA-256 生成 stateHash；projection cache 损坏可重建，control facts/quick_check 损坏失败关闭并保留原库。
- 范围控制：本 Story 不实现 B3-002 的控制命令/receipt waterfall，也不提前实现 Safety Executor、Supervisor 策略或生产控制 UI。

### 计划 Red

1. `sqlite-provider.spec.ts`：append-only、稳定 sequence、幂等冲突、事务重开 durability、事实损坏失败关闭。
2. `projection.spec.ts`：前缀顺序、确定性 stateHash、unknown 保守投影、cache 损坏重建。
3. `control-observer.spec.ts`：真实 rc.6 SessionEvent 归一化、flush 边界和 listener cleanup。
4. `dsh-integration.spec.ts`：Cordis event → pending → flush → SQLite 重开 → replay/projection 的纵向闭环。

## TDD 完成证据

- 代码提交：`f52d855aa4e6a2ce962bf936c6fc26ffd5ffab46`。
- Red：4 个新增套件在 control-ledger、control-observer 和 DSH peer 尚不存在时以模块缺失失败，原因只来自本 Story 未实现。
- Green：SQLite Provider、确定性投影、真实 rc.6 观察器与 Cordis→flush→SQLite→restart 纵向闭环 `6/6` 通过。
- Refactor：补齐纯契约 Schema、agent lifecycle/status、畸形缓存重建和事实 canonical 完整性；目标 `10/10`、全仓 TypeScript `130/130` 通过。
- Integration smoke：冻结安装、全仓 typecheck、Python `60/60`、composition verify 与真实生产 DSH headless `--help` 通过。
- 组合显式重冻为 `c6fc9778…eea20`；DSH rc.6、Cordis 4.0.1、Profile provider 与 finalConfig 未漂移。
- TDD 真理源：`Plans/功能开发/2026-08-17-agent全仓TypeScript重构-US-B3-001.tdd.json`。

本 Story 已完成并退出滚动 Scope；用户回复“继续”后只切换到 `US-B3-002`，不会自动进入集成测试。

续做：`/resume plan=Plans/功能开发/2026-08-17-agent全仓TypeScript重构.md 进度=next-story-scope`

## 反馈（skill_run）

```yaml
skill_run:
  skill: implementation-design-assistant
  workflow_stage: implementation-design
  plan: Plans/功能开发/2026-08-17-agent全仓TypeScript重构-US-B3-001.md
  date: 2026-08-18
  contexts_used:
    - path: Plans/技术方案/2026-08-17-智能体控制系统工程架构-v0.1.md
      utility: high
      reason: "落实 ENG-006/008/012、ControlFact/Projection 数据约束与 SQLite WAL Provider Port"
    - path: Plans/功能开发/2026-08-17-agent全仓TypeScript重构.stories.json
      utility: high
      reason: "确认 US-B3-001 是唯一滚动 Scope，且 US-B1-001/US-B2-002 依赖已满足"
    - path: Contexts/决策/Skill反馈协议.md
      utility: high
      reason: "约束实现落点阶段的反馈字段与写入位置"
  contexts_missing: []
  contexts_stale: []
  outcome_status: pass
  revisit_needed: false
```

## 反馈（skill_run）

```yaml
skill_run:
  skill: resume-assistant
  workflow_stage: story-development
  plan: Plans/功能开发/2026-08-17-agent全仓TypeScript重构-US-B3-001.md
  date: 2026-08-18
  contexts_used:
    - path: Plans/功能开发/2026-08-17-agent全仓TypeScript重构-US-B3-001.impl.json
      utility: high
      reason: "读取并确认用户批准的 Control Ledger 文件落点、durable 边界、Red 与停止条件"
    - path: Plans/功能开发/2026-08-17-agent全仓TypeScript重构-US-B3-001.md
      utility: high
      reason: "确认当前唯一 Scope 为 US-B3-001，前置已满足且保持 8 点纵向边界"
    - path: Contexts/决策/Skill反馈协议.md
      utility: high
      reason: "约束续做阶段的反馈字段与写入位置"
  contexts_missing: []
  contexts_stale: []
  outcome_status: pass
  revisit_needed: false
```

## 反馈（skill_run）

```yaml
skill_run:
  skill: feature-dev-assistant
  workflow_stage: story-development
  plan: Plans/功能开发/2026-08-17-agent全仓TypeScript重构-US-B3-001.md
  date: 2026-08-18
  contexts_used:
    - path: Plans/功能开发/2026-08-17-agent全仓TypeScript重构-US-B3-001.tdd.json
      utility: high
      reason: "汇总真实 Red、Green、Refactor、integration smoke、四项 AC 与提交证据"
    - path: /Users/wanglongxiang/git/agent/packages/dsh-bridge/src/control-observer.ts
      utility: high
      reason: "按 rc.6 typed events 归一化 session 与 agent 信号，并把 durable 边界严格放在 session/flush"
    - path: /Users/wanglongxiang/git/agent/plugins/control-ledger/src/sqlite-provider.ts
      utility: high
      reason: "实现 WAL/FULL、连续 sequence、canonical 幂等、事实完整性与失败关闭的 Provider"
    - path: /Users/wanglongxiang/git/agent/plugins/control-ledger/src/projection.ts
      utility: high
      reason: "实现事实前缀的保守纯投影、canonical stateHash 与可重建缓存"
    - path: Plans/技术方案/2026-08-17-智能体控制系统工程架构-v0.1.md
      utility: high
      reason: "持续约束 ENG-006/008/012、事实/投影分离、SQLite 单写者与 Provider Port"
  contexts_missing: []
  contexts_stale: []
  outcome: "US-B3-001 已完成并提交 f52d855；主计划保持逐 Story 开发，等待确认下一滚动 Scope"
  utility: high
  reason: "四项 AC 均有真实 rc.6、Cordis flush、SQLite 重开和全仓回归证据"
  outcome_status: pass
  friction: "composition artifact 集合新增后旧 lock 按预期失配；已通过显式 --write 重冻并再次 composition verify"
  revisit_needed: false
```
