---
tags: [需求排序, Backlog, TypeScript, DSH, LangGraph]
type: plan
category: 需求排序
status: 已采纳
date: 2026-08-17
lifecycle_state: prioritization
epic: Plans/Epic/2026-08-17-agent全仓TypeScript重构.md
requirement_plan: Plans/需求分析/2026-08-17-agent全仓TypeScript重构.md
backlog_index: Plans/需求排序/2026-08-17-agent全仓TypeScript重构.backlog.json
relations:
  depends_on:
    - Plans/需求分析/2026-08-17-agent全仓TypeScript重构.md
    - Templates/模板约定.md
  dependents:
    - Plans/技术方案/2026-08-17-智能体控制系统工程架构-v0.1.md
  supersedes: []
  superseded_by: []
  conflicts: []
---

# 需求排序：agent全仓TypeScript重构

## 排序原则

- 价值、紧迫度、风险验证价值、前置依赖分别记录；本阶段不填写故事点、工时或个人产能。
- “评估优先”落实为第一项先冻结可信基线与评估准绳，后续每一批都先有可失败的门禁再扩实现。
- B0—B5 都是最终 cutover 的必要条件，均保持 P0；排序代表实施先后，不代表后项可以省略。
- AI 只提出顺序；团队确认后 `confirmed: true` 才成为门禁事实。

## 已确认 Backlog 顺序

| 顺序 | 需求 ID | 标题 | 业务价值 | 紧迫度 | 依赖 | 优先级 | 排序依据 | 已确认 |
|---:|---|---|---|---|---|---|---|:---:|
| 1 | B0 | 可信基线与评估准绳冻结 | high | high | — | P0 | 先固定 baseline SHA、60 tests、资产、真实 transcript、Case/Oracle/负对照和回滚引用；准绳不能区分正确、错误和坏环境时停止，不开始大规模迁写 | true |
| 2 | B1 | 双 TypeScript Runtime 可评价基座 | high | high | B0 | P0 | 先建立可被同一准绳检查的 pnpm workspace、固定 DSH rc.6 生产组合与隔离 LangGraph.js Learning Runtime；只做可评价基座，不把目录创建当迁移完成 | true |
| 3 | B2 | 可信评估驱动的行为与 60 tests 语义迁写 | high | high | B0, B1 | P0 | 逐项 Red→Green 迁写 Definition、Tools、Capabilities 和 Runtime 行为；G-EQ、四态评估或人工证据不可靠时允许阻断，不强制 PASS | true |
| 4 | B3 | 可重放控制闭环 | high | medium | B1, B2 | P0 | 在 Runtime 与评估语义稳定后接入 control-domain、append-only ledger、observer、supervisor 和 outcome-feedback，避免先固化错误事件模型 | true |
| 5 | B4 | 独立安全执行与故障隔离 | high | high | B1, B2, B3 | P0 | Safety Executor 风险高但依赖 B3 的 ActionIntent/Receipt 契约；按已确认的独立身份/凭证域落地，并以旁路、幂等、未知效果和 Watchdog 故障注入证明不可绕过 | true |
| 6 | B5 | 全量验收与一次 cutover | high | medium | B0, B1, B2, B3, B4 | P0 | 只有全量评估、60 tests parity、插件生命周期、故障注入、rehearsal 和人工签署全绿后，才一次性删除 Python；任一失败保持基线 | true |

对应机器索引：`Plans/需求排序/2026-08-17-agent全仓TypeScript重构.backlog.json`。

## P1 归属

Control Ledger 首版 Provider 不单独改变 B0—B5 的价值顺序。它作为 B3 的架构期决策：先冻结 append-only、稳定序号、幂等、重放和删除证明契约，再在正式架构阶段选择 Provider；未选择时不得开始 B3 的持久化实现。

## 团队确认

- [x] 用户确认“B0 先校准评估 → B1 可评价基座 → B2 逐项迁写 → B3 控制闭环 → B4 安全执行 → B5 一次 cutover”的顺序
- [x] 开发确认 B0—B5 依赖没有遗漏
- [x] 本轮排序已经团队确认，Backlog 全局与逐项 `confirmed=true`

## 当前门禁

排序已由用户确认。`validate-client-dev.py backlog` 必须通过后才能进入正式架构阶段。

## 续做

```text
/resume plan=Plans/Epic/2026-08-17-agent全仓TypeScript重构.md 进度=architecture
```

## 反馈（skill_run）

```yaml
skill_run:
  skill: backlog-prioritization-assistant
  workflow_stage: prioritization
  plan: Plans/需求排序/2026-08-17-agent全仓TypeScript重构.md
  date: 2026-08-17
  contexts_used:
    - path: Plans/需求分析/2026-08-17-agent全仓TypeScript重构.md
      utility: high
      reason: "提供已采纳且 P0=0 的 B0—B5 范围、22 组 GWT、60/60 迁移矩阵和可信评估停止条件"
    - path: Plans/代码重构/2026-08-17-agent控制系统工程落点-v0.1.md
      utility: high
      reason: "核对 B0—B5 的工程依赖与一次 cutover 边界，但不在排序阶段做文件级实现设计"
    - path: Plans/技术方案/2026-08-17-智能体控制系统工程架构-v0.1.md
      utility: high
      reason: "核对 DSH 生产、LangGraph.js 学习、控制闭环与 Safety Executor 的前后依赖"
  contexts_missing:
    - "团队对建议 Backlog 顺序的明确确认"
  contexts_stale: []
  outcome: "生成 B0—B5 有序 Backlog 草案；坚持先校准评估、再建立可评价基座和逐项迁写，当前 confirmed=false 等待团队确认"
  utility: high
  reason: "把评估可靠性变成第一实施条件，并保留人工排序门禁，避免为了推进流程自动确认"
```

```yaml
skill_run:
  skill: backlog-prioritization-assistant
  workflow_stage: prioritization
  plan: Plans/需求排序/2026-08-17-agent全仓TypeScript重构.md
  date: 2026-08-17
  contexts_used:
    - path: Plans/需求分析/2026-08-17-agent全仓TypeScript重构.md
      utility: high
      reason: "确认需求已采纳、P0=0，且 B0—B5 没有遗漏任何 cutover 必要条件"
    - path: Plans/需求排序/2026-08-17-agent全仓TypeScript重构.backlog.json
      utility: high
      reason: "同步用户确认到机器可校验的全局与逐项 confirmed 字段"
    - path: Plans/Epic/2026-08-17-agent全仓TypeScript重构.md
      utility: high
      reason: "核对 prioritization 退出条件并推进 client-dev 生命周期"
  contexts_missing: []
  contexts_stale: []
  outcome: "用户确认 B0→B1→B2→B3→B4→B5 顺序；排序 Plan 已采纳，Backlog 全局与六项需求均 confirmed=true"
  utility: high
  reason: "人工确认与机器索引一致，排序门禁可被独立重放验证"
```
