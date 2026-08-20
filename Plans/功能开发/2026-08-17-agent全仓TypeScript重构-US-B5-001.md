---
tags: [功能开发, B5, Rehearsal, Release]
type: plan
category: 功能开发
status: 已完成
date: 2026-08-17
lifecycle_state: story-development
parent: Plans/功能开发/2026-08-17-agent全仓TypeScript重构.md
requirement_plan: Plans/需求分析/2026-08-17-agent全仓TypeScript重构.md
architecture_plan: Plans/技术方案/2026-08-17-智能体控制系统工程架构-v0.1.md
story_id: US-B5-001
story_points: 8
sprint_scope: false
tdd_evidence: Plans/功能开发/2026-08-17-agent全仓TypeScript重构-US-B5-001.tdd.json
implementation_design: Plans/功能开发/2026-08-17-agent全仓TypeScript重构-US-B5-001.impl.json
---
# US-B5-001：运行完整 cutover rehearsal 并展示阻断证据

作为发布负责人，我想运行不执行删除的全量 rehearsal，并看到每个红灯及其证据，以便在不冒险切换的情况下判断候选是否 ready。

覆盖 rehearsal 侧 `GWT-021—022`。必须汇总 G-EQ、60 parity、lifecycle、fault、safety、隔离、回滚和人工状态。

## 当前 Scope

- `US-B2-004`、`US-B2-005`、`US-B3-002`、`US-B4-002` 均已完成并有提交/TDD 证据；用户再次回复“继续”后，本轮只激活依赖已满足的 `US-B5-001`。
- 本 Story 已完成并退出滚动 Scope；用户回复“继续”后，`US-B5-002` 成为唯一滚动 Scope，但尚未获得破坏性 cutover 批准。
- reviewer 未签署或任一门禁不全绿时，候选必须保持 blocked；AI 不得代填人工批准。

## 已实现边界

- 版本化报告：新增 `cutover-rehearsal.v1` 与 `deployment-boundary-evidence.v1`，固定候选 SHA、baseline/rollback、composition、gate receipts、输出 hash、deployment/human 状态和证据引用；B5-001 的 `cutoverAllowed` 永远为 false。
- 纯领域聚合：新增只依赖 contracts 的 `release-domain`，全部固定自动门禁 PASS 且真实 deployment evidence 与 fingerprint 一致时，只进入 `ready_for_human_review`；任一红灯/缺证即 blocked。
- 非破坏性 runner：`scripts/release` 只以代码内 allowlist argv 调用现有 G-EQ、60 parity、全仓测试、lifecycle、fault/safety、隔离、composition、recovery、audit 与 rollback 真源；外部不能注入任意命令。
- 证据收敛：修正 migration map 中 M005/M008/M009 的早期占位路径，并要求 60 条 targetRed 文件全部真实存在，禁止按数量伪造 parity。
- 生产边界：本地 UDS/fixture 不等于真实 OS/IAM/network/certificate 签署；未提供匹配 fingerprint 的 owner-signed deployment evidence 时，dashboard 明确红灯。
- 输出边界：报告原子写入、拒绝覆盖、绑定 candidate SHA 与 canonical hash；无论 ready/blocked，Python 文件和生产入口 hash 均不变，baseline rollbackRef 仍可解析。

## Red 设计

1. 契约 Red：严格字段、gate ID 闭集、evidence 必填、SHA/fingerprint/时间校验，以及任何输入都不能让 rehearsal report 获得 cutover 权限。
2. 领域 Red：全自动门禁全绿只到 ready-for-review；任一 fail/blocked/缺证、deployment 漂移或 human pending/rejected 都稳定失败关闭。
3. Parity Red：M001—M060 精确覆盖并逐一验证 targetRed 文件存在，修复 M005/M008/M009 漂移但不改变迁移语义或 disposition。
4. 纵向 Red：fake ports 证明固定 gate receipts、baseline/rollback/composition/evidence hash 完整，且不在 Vitest 内递归运行全仓测试。
5. 故障 Red：composition drift、命令失败、G-EQ/映射/deployment 缺证、reviewer pending 均生成 blocked dashboard，并证明 Python/生产入口零修改。

## 停止条件

- 需要删除、移动或改写 `.py` 文件，修改生产入口，创建/移动 baseline tag，或执行真实 cutover。
- 需要 AI 代填 production OS/IAM/network/certificate 签署或最终 cutover reviewer 决定。
- 无法复用现有门禁真源，只能人工硬编码 PASS；或 runner 必须接受任意 shell 命令。
- 需要 fork/vendoring DSH、升级 rc.6/Cordis 4.0.1 或引入新的发布/命令执行框架。
- 无法保证报告原子、拒绝覆盖、绑定候选 SHA，或无法证明 blocked rehearsal 对 Python/入口零修改。

机器真理源：`Plans/功能开发/2026-08-17-agent全仓TypeScript重构-US-B5-001.impl.json`；用户已回复“继续吧”确认文件落点、固定 gate、blocked 语义和非破坏性停止条件，实现已按 `confirmed=true` 完成。

## TDD 完成证据

- 代码提交：`9739aec319fee03ea17c3f6754b6cc7a93291adb`。
- 新增 `cutover-rehearsal.v1` / `deployment-boundary-evidence.v1` 严格契约、纯 `release-domain` 与固定命令 runner；外部参数不能注入 shell 或切换动作。
- 真实演练绑定干净 candidate、baseline/rollback 和组合指纹；G-EQ、60 parity、lifecycle、fault、safety、Learning isolation、composition、recovery、rollback、supply-chain 十个自动门禁全部 PASS。
- 缺真实 production OS/IAM/network/certificate 签署时，`deployment_boundary=blocked`、`cutoverAllowed=false`；Python 保留、生产入口未改、破坏性动作列表为空。
- 目标 `11/11`、全仓 TypeScript `202/202`、Python `60/60`、typecheck、三处 frozen install、官方 registry audit、composition 与 controlled/recovery smoke 全部通过。
- 演练报告 SHA-256：`936281d511bca9ac41c56666b32b45ce5bd6c34a12d398a33bde5fcbf5c554a2`；组合指纹：`244278a1a69fdf512abc4bc23cffb3fc18bb539a8da677c3bb3392c1bf6fceab`。
- TDD 真理源：`Plans/功能开发/2026-08-17-agent全仓TypeScript重构-US-B5-001.tdd.json`。

续做：本 Story 已完成并退出滚动 Scope；`US-B5-002` 已进入 implementation-design，删除 Python、生产入口切换和最终人工批准均未执行。

## 反馈（skill_run）

```yaml
skill_run:
  skill: task-splitter
  workflow_stage: story-split
  plan: Plans/功能开发/2026-08-17-agent全仓TypeScript重构-US-B5-001.md
  date: 2026-08-20
  contexts_used:
    - path: Plans/功能开发/2026-08-17-agent全仓TypeScript重构-US-B4-002.md
      utility: high
      reason: "确认 Watchdog/双端门禁/recovery 已完成并有提交与 TDD 证据，B5-001 的最后前置依赖已满足"
    - path: Plans/功能开发/2026-08-17-agent全仓TypeScript重构.stories.json
      utility: high
      reason: "确认下一条依赖满足的纵向 Story 是 US-B5-001，点数 8 且 US-B5-002 仍不在滚动 Scope"
    - path: Plans/技术方案/2026-08-17-智能体控制系统工程架构-v0.1.md
      utility: high
      reason: "保持 rehearsal 与真实 cutover 分离，任一红灯不得删除 Python 或切换生产入口"
  contexts_missing: []
  contexts_stale: []
  outcome: "只激活 US-B5-001；US-B4-002 退出滚动 Scope，US-B5-002 未扩张"
  utility: high
  reason: "将看板当前 Story 对齐到依赖已满足的 rehearsal 纵向切片，同时保留人工 cutover 边界"
  outcome_status: pass
  revisit_needed: false
```

```yaml
skill_run:
  skill: implementation-design-assistant
  workflow_stage: implementation-design
  plan: Plans/功能开发/2026-08-17-agent全仓TypeScript重构-US-B5-001.md
  date: 2026-08-20
  contexts_used:
    - path: Plans/需求分析/2026-08-17-agent全仓TypeScript重构.md
      utility: high
      reason: "落实 GWT-021 rehearsal 前提、GWT-022 失败关闭、Cutover Gate Dashboard 与独立人工门禁"
    - path: Plans/技术方案/2026-08-17-智能体控制系统工程架构-v0.1.md
      utility: high
      reason: "落实 ENG-005/009/011，保持 rehearsal 与真实删除/入口切换分离"
    - path: Plans/功能开发/2026-08-17-agent全仓TypeScript重构-US-B4-002.md
      utility: high
      reason: "继承已完成的 Watchdog/双端 Safety/recovery 证据，并保留真实 production IAM/network 仍待 B5 签署的边界"
    - path: Contexts/决策/Skill反馈协议.md
      utility: high
      reason: "按有 Plan 任务协议记录落点门禁与待确认项"
  contexts_missing:
    - "用户对 US-B5-001 文件落点、固定 gate、blocked 语义与非破坏性停止条件的确认"
  contexts_stale: []
  outcome: "US-B5-001 落点草案完成并停在 confirmed=false；未创建 Red、rehearsal runner、报告或执行任何删除/入口切换"
  utility: high
  reason: "把全量证据汇总、真实 deployment 缺证、人工边界和零破坏约束落到可验证文件与命令端口"
  outcome_status: pass
  revisit_needed: false
```

```yaml
skill_run:
  skill: resume-assistant
  workflow_stage: story-development
  plan: Plans/功能开发/2026-08-17-agent全仓TypeScript重构-US-B5-001.md
  date: 2026-08-20
  contexts_used:
    - path: Plans/功能开发/2026-08-17-agent全仓TypeScript重构-US-B5-001.impl.json
      utility: high
      reason: "续接用户已确认的固定门禁、不可变报告、真实部署缺证与零破坏停止条件"
    - path: Plans/需求分析/2026-08-17-agent全仓TypeScript重构.md
      utility: high
      reason: "逐项验收 GWT-021-REHEARSAL 与 GWT-022 的 ready/blocked 语义"
  contexts_missing: []
  contexts_stale: []
  outcome: "从已确认 implementation-design 恢复并完成 US-B5-001；未激活或执行破坏性 cutover"
  utility: high
  reason: "保持 rehearsal、真实部署签署、最终人工批准和生产切换四者边界"
  outcome_status: pass
  revisit_needed: false
```

```yaml
skill_run:
  skill: feature-dev-assistant
  workflow_stage: story-development
  plan: Plans/功能开发/2026-08-17-agent全仓TypeScript重构-US-B5-001.md
  date: 2026-08-20
  contexts_used:
    - path: Plans/需求分析/2026-08-17-agent全仓TypeScript重构.md
      utility: high
      reason: "验收完整 rehearsal、每门证据展示与任一缺证失败关闭"
    - path: Plans/技术方案/2026-08-17-智能体控制系统工程架构-v0.1.md
      utility: high
      reason: "落实 rehearsal 与一次性真实 cutover 分离、baseline 回滚和 Learning 隔离"
    - path: Plans/功能开发/2026-08-17-agent全仓TypeScript重构-US-B5-001.tdd.json
      utility: high
      reason: "记录真实 Red、Green、全仓回归、提交、不可变演练报告和 blocked 非破坏性验收"
  contexts_missing: []
  contexts_stale: []
  outcome: "US-B5-001 已完成并提交 9739aec；十个自动门禁全绿，真实 deployment boundary 缺证按设计 blocked，B5-002 未激活"
  utility: high
  reason: "完整 rehearsal 已可复跑且不会删除 Python、改变生产入口或授权 cutover"
  outcome_status: pass
  friction: "首次真实演练的精简 PATH 缺少 pnpm shim，G-EQ 正确失败关闭；补齐既有工具链路径后新报告通过全部自动门禁，旧报告未覆盖"
  revisit_needed: false
```
