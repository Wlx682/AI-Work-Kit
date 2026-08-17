---
tags: [功能开发, 用户故事, TypeScript, DSH, LangGraph, 智能体]
type: plan
category: 功能开发
status: 进行中
date: 2026-08-17
lifecycle_state: story-development
epic: Plans/Epic/2026-08-17-agent全仓TypeScript重构.md
requirement_plan: Plans/需求分析/2026-08-17-agent全仓TypeScript重构.md
architecture_plan: Plans/技术方案/2026-08-17-智能体控制系统工程架构-v0.1.md
story_index: Plans/功能开发/2026-08-17-agent全仓TypeScript重构.stories.json
relations:
  depends_on:
    - Plans/需求排序/2026-08-17-agent全仓TypeScript重构.md
    - Plans/技术方案/2026-08-17-智能体控制系统工程架构-v0.1.md
  dependents:
    - Plans/代码重构/2026-08-17-agent控制系统工程落点-v0.1.md
  supersedes: []
  superseded_by: []
  conflicts: []
---

# 用户故事拆分：agent 全仓 TypeScript 重构

## 一、输入门禁

- 需求 Plan：已采纳，`p0_open=0`。
- Backlog：已采纳，顺序为 B0→B1→B2→B3→B4→B5。
- 架构：已采纳；DSH rc.6 唯一生产 Runtime、LangGraph.js 隔离 Learning Runtime、Safety 独立权限域、Ledger=SQLite WAL + Provider Port。

## 二、纵向故事索引

| 顺序 | Story ID | 可独立演示的用户能力 | AC/迁移语义 | 依赖 | 优先级 | 建议点数 | Epic Scope 建议 | 子 Plan |
|---:|---|---|---|---|---|---:|:---:|---|
| 1 | US-B0-001 | 维护者可冻结可重放基线并证明评估尺可靠 | GWT-001—004、009—012 | — | P0 | 8 | true | `Plans/功能开发/2026-08-17-agent全仓TypeScript重构-US-B0-001.md` |
| 2 | US-B1-001 | Runtime 维护者可启动固定 DSH 组合并可逆装卸控制插件 | GWT-005—008 | US-B0-001 | P0 | 8 | true（已完成） | `Plans/功能开发/2026-08-17-agent全仓TypeScript重构-US-B1-001.md` |
| 3 | US-B1-002 | 学习者可独立运行/恢复 LangGraph.js，生产入口会拒绝它 | GWT-013—014 | US-B0-001 | P0 | 8 | true（已完成） | `Plans/功能开发/2026-08-17-agent全仓TypeScript重构-US-B1-002.md` |
| 4 | US-B2-001 | 学习者可迁写并验证 Action/审批/unknown 语义 | M001—M011 | US-B1-002 | P0 | 8 | true | `Plans/功能开发/2026-08-17-agent全仓TypeScript重构-US-B2-001.md` |
| 5 | US-B2-002 | 维护者可验证 Definition、LLM JSON、Planning 与 Role 语义 | M012—M025 | US-B1-001, US-B1-002 | P0 | 8 | true | `Plans/功能开发/2026-08-17-agent全仓TypeScript重构-US-B2-002.md` |
| 6 | US-B2-003 | 学习者可运行、暂停、恢复、回放和 fork 单 Agent 会话 | M026—M037 | US-B2-001, US-B2-002 | P0 | 8 | true | `Plans/功能开发/2026-08-17-agent全仓TypeScript重构-US-B2-003.md` |
| 7 | US-B2-004 | 学习者可运行并恢复多角色 Team Learning Graph | M038—M043 | US-B2-003 | P0 | 5 | true | `Plans/功能开发/2026-08-17-agent全仓TypeScript重构-US-B2-004.md` |
| 8 | US-B2-005 | 学习者可通过结构化工具与 CLI 操作、暂停和恢复任务 | M044—M060 | US-B2-001, US-B2-003 | P0 | 8 | true | `Plans/功能开发/2026-08-17-agent全仓TypeScript重构-US-B2-005.md` |
| 9 | US-B3-001 | 监督者可从 SQLite 控制账本重放 DSH 运行动态镜像 | B3 Ledger/Projection AC | US-B1-001, US-B2-002 | P0 | 8 | true | `Plans/功能开发/2026-08-17-agent全仓TypeScript重构-US-B3-001.md` |
| 10 | US-B3-002 | 监督者可下发控制命令并查看分段回执与现实结果 | GWT-019 | US-B3-001 | P0 | 8 | true | `Plans/功能开发/2026-08-17-agent全仓TypeScript重构-US-B3-002.md` |
| 11 | US-B4-001 | Runtime 可经独立 Safety Executor 安全执行并对账现实效果 | GWT-015—018 | US-B3-002 | P0 | 8 | true | `Plans/功能开发/2026-08-17-agent全仓TypeScript重构-US-B4-001.md` |
| 12 | US-B4-002 | 运维者可由 Watchdog 证明权限组合并在失联时自动降级 | GWT-020 | US-B1-001, US-B4-001 | P0 | 5 | true | `Plans/功能开发/2026-08-17-agent全仓TypeScript重构-US-B4-002.md` |
| 13 | US-B5-001 | 发布负责人可运行完整 rehearsal 并看到每个阻断证据 | GWT-021—022（不执行删除） | US-B2-004, US-B2-005, US-B3-002, US-B4-002 | P0 | 8 | true | `Plans/功能开发/2026-08-17-agent全仓TypeScript重构-US-B5-001.md` |
| 14 | US-B5-002 | 发布负责人可在人工批准后一次切换并保留回滚基线 | GWT-021—022（cutover） | US-B5-001 | P0 | 5 | true | `Plans/功能开发/2026-08-17-agent全仓TypeScript重构-US-B5-002.md` |

JSON 真理源：`story_index`。所有故事均为纵向能力；共享底座放入首个实际消费者。现有最小 TS/评估代码只能作为 Red/基线候选，必须在对应 Story 重新验收，不能把旧 Plan 的“已完成”直接继承为本 Epic Green。

## 三、拆分约束

- B0 先于任何大规模迁写；评估不可靠时后续 Story 全部 blocked。
- B1 分成生产 DSH 组合与 Learning Runtime 两条可独立演示路径，但生产入口和依赖图必须硬隔离。
- B2 按用户可观察行为和 Python 测试语义簇拆分，M001—M060 连续覆盖，无 waiver。
- B3 先交可重放动态镜像，再交控制命令闭环；SQLite driver 等文件级选择留给 Story implementation-design。
- B4 的同进程 mock 只能用于单测，不能充当独立身份、凭证、网络/IAM 和旁路证明。
- B5 rehearsal 与真实 cutover 分开；最终删除是独立破坏性 Story，未批准时不执行。

## 四、Scope 与故事点确认

- [x] 用户确认 14 个 Story 的边界和依赖
- [x] 用户确认建议故事点；没有 13 点 Story
- [x] 用户确认 14 个 P0 Story 全部属于本 Epic Scope，但严格按依赖顺序逐个实现
- [x] `.stories.json` 的 `scope_confirmed` 与每项 `estimate_confirmed` 均为 `true`

Scope 与故事点已由用户确认；`story-scope` 机械门禁通过后进入首个 Story 的 implementation-design，仍不得跳过 Red 测试直接开发。

**Scope 语义**：14 个 Story 全部属于已确认的 Epic Scope。`US-B0-001`、`US-B1-001` 与 `US-B1-002` 已完成并退出当前 implementation Scope；用户在 US-B1-002 完成后回复“继续任务”，因此当前只激活依赖已满足的 `US-B2-001`。其余 10 个未完成 Story 保持 `sprint_scope=false`，不因机械门禁误判为最终集成阶段而一次性扩张。

## 五、实现落点设计

当前 implementation Scope 为 `US-B2-001`：迁写 Action、审批、拒绝、unknown 与人工恢复语义，覆盖 `M001—M011`；`US-B1-002` 已完成并满足前置条件。具体文件落点、依赖方向与 Red 测试位置由本 Story 的 implementation-design 确认。

| Story | 实现落点 | 关键边界 | 状态 |
|---|---|---|---|
| US-B1-001 | `Plans/功能开发/2026-08-17-agent全仓TypeScript重构-US-B1-001.impl.json` | 不 fork DSH；`dsh-bridge + Cordis plugin + Bundles + controlled Profile`；指纹绑定真实 artifact/lock/source/dump | ✅ 已完成，提交 `738c9cf` |
| US-B1-002 | `Plans/功能开发/2026-08-17-agent全仓TypeScript重构-US-B1-002.impl.json` | 官方 SQLite checkpoint；跨进程 resume；Learning 环境 allowlist；production manifest 前置拒绝；无部署/反向依赖 | ✅ 已完成，提交 `27e5a1c` |
| US-B2-001 | `Plans/功能开发/2026-08-17-agent全仓TypeScript重构-US-B2-001.impl.json` | Lab 内 Action 纯状态机 + 共享序列化契约；M001—M011；不创建第二生产 Agent Loop，不提前实现 B4 Safety Executor | ✅ 已完成，提交 `bded643` |

探针已证明只锁根 `@deepseek-ai/dsh@0.1.0-rc.6` 会被上游 caret 依赖拉向尚不完整的 rc.7 并报 `ETARGET`。实现以根 `pnpm-workspace.yaml` wildcard override 固定完整 rc.6 闭包，保留最小 `allowBuilds`，没有 fork 或重写 DSH Agent Loop。

### 5.1 US-B1-001 实现证据

- 代码提交：`738c9cfc0265345c76cca3f91ccca66ffc640031`。
- controlled Profile 组合指纹：`cfe884f04031d415cd465fb5a064288cce52fb0df0e37b75d21b8ded31cdd681`。
- 真实 Red→Green：6 组目标测试先失败后通过；漂移/启动逃逸、正常卸载、部分初始化失败回滚和 Learning 隔离均有自动化证据。
- 全量回归：TypeScript 46/46、Python 基线 60/60、typecheck、composition verify 和双 workspace frozen install 通过。
- 集成 smoke：校验完成后委托官方 DSH rc.6，真实 `--dump-config` 与 headless `--help` 成功。
- TDD 真理源：`Plans/功能开发/2026-08-17-agent全仓TypeScript重构-US-B1-001.tdd.json`。

### 5.2 US-B1-002 实现证据

- 代码提交：`27e5a1c2c114a7f7b2f70d26ebdf2c6f568c09c0`。
- Learning CLI 以两个真实进程完成 SQLite pause/resume，保持 thread、更新 runId 并记录 checkpoint lineage 与离线 transcript。
- Learning 子进程使用环境 allowlist；production launcher 在任何组合/runner 行为前拒绝 learning manifest。
- 首次依赖审计发现 `ini@1.3.0` high，固定到 `1.3.8` 后官方 registry 审计为无已知漏洞。
- DSH 组合显式重冻为 `e59e8be7e3e5b54458aa426292b5452217aef2ac49ce18e520f3009d2bceb31a`，真实 controlled Profile smoke 通过。
- 全量回归：TypeScript 52/52、Python 基线 60/60、typecheck、双 frozen install 与双 Runtime smoke 通过。
- TDD 真理源：`Plans/功能开发/2026-08-17-agent全仓TypeScript重构-US-B1-002.tdd.json`。

US-B1-002 已完成；当前 Scope 已按用户“继续任务”切换为唯一 `US-B2-001`，其余未完成 Story 未激活。

### 5.3 US-B2-001 实现证据

- 代码提交：`bded643f54700136681b0a819034c7d21fc1e65f`。
- 共享 `learning-action-session.v1` Schema 与判别联合；Learning Lab 以注入 port 实现 Action/审批/unknown/输入恢复，不依赖 DSH、Cordis、生产凭证或 Safety Executor。
- M001—M011 逐项具名 Red→Green→Refactor；定向 15/15，全量 TypeScript 66/66、Python 60/60、typecheck 通过。
- DSH 组合显式重冻为 `80f0fc8e…701e`，仅 contracts artifact 与总指纹变化，composition verify 通过。
- TDD 真理源：`Plans/功能开发/2026-08-17-agent全仓TypeScript重构-US-B2-001.tdd.json`。

US-B2-001 已完成；当前 Scope 暂时保留它供机械门禁验收，不自动激活 US-B2-002。

## 续做

```text
/resume plan=Plans/功能开发/2026-08-17-agent全仓TypeScript重构.md 进度=next-story-scope
```

```yaml
skill_run:
  skill: resume-assistant
  workflow_stage: story-development
  plan: Plans/功能开发/2026-08-17-agent全仓TypeScript重构.md
  date: 2026-08-17
  contexts_used:
    - path: Plans/Epic/2026-08-17-agent全仓TypeScript重构.md
      utility: high
      reason: "回放 Epic 确认前三个 Story 已完成、当前仍处于逐 Story 开发"
    - path: Plans/功能开发/2026-08-17-agent全仓TypeScript重构.stories.json
      utility: high
      reason: "识别已完成 US-B1-002 仍占滚动 Scope，并确定依赖已满足的下一 Story 是 US-B2-001"
    - path: Plans/功能开发/2026-08-17-agent全仓TypeScript重构-US-B1-002.tdd.json
      utility: high
      reason: "确认下一 Story 的 US-B1-002 前置已有完整 TDD 与提交证据"
  contexts_missing: []
  contexts_stale: []
  outcome: "从 next-story-scope 断点恢复，继续逐 Story 开发而非提前进入集成测试"
  utility: high
  reason: "恢复点与 Epic 3/14 的真实完成度一致，并避免重复开发已完成 Story"
```

```yaml
skill_run:
  skill: task-splitter
  workflow_stage: story-split
  plan: Plans/功能开发/2026-08-17-agent全仓TypeScript重构.md
  date: 2026-08-17
  contexts_used:
    - path: Plans/功能开发/2026-08-17-agent全仓TypeScript重构.stories.json
      utility: high
      reason: "把唯一当前 implementation Scope 从已完成 US-B1-002 切换为 US-B2-001"
    - path: Plans/功能开发/2026-08-17-agent全仓TypeScript重构-US-B2-001.md
      utility: high
      reason: "保持 Action、审批、unknown 与人工恢复的 8 点纵向 Story 边界"
    - path: Plans/需求排序/2026-08-17-agent全仓TypeScript重构.md
      utility: high
      reason: "保持用户确认的 B0→B1→B2→B3→B4→B5 顺序和依赖"
  contexts_missing: []
  contexts_stale: []
  outcome: "用户回复‘继续任务’后只激活 US-B2-001；US-B1-002 退出滚动 Scope，其余未完成 Story 未扩张"
  utility: high
  reason: "下一 Story 的唯一前置已满足，单 Story Scope 可独立设计与验收"
```

```yaml
skill_run:
  skill: implementation-design-assistant
  workflow_stage: implementation-design
  plan: Plans/功能开发/2026-08-17-agent全仓TypeScript重构.md
  date: 2026-08-17
  contexts_used:
    - path: Plans/功能开发/2026-08-17-agent全仓TypeScript重构-US-B2-001.impl.json
      utility: high
      reason: "固化 M001—M011 的共享契约、Learning Action 状态机、Red 测试与停止条件"
    - path: /Users/wanglongxiang/git/agent/capabilities/act.py
      utility: high
      reason: "提取审批、unknown、人工恢复、虚拟输入和不可信工具输出的旧行为基线"
    - path: /Users/wanglongxiang/git/agent/migration/legacy-test-map.json
      utility: high
      reason: "发现旧 packages/agent-loop 目标与已采纳 Learning Lab 矩阵漂移，纳入落点修正"
    - path: Plans/技术方案/2026-08-17-智能体控制系统工程架构-v0.1.md
      utility: high
      reason: "约束 ENG-008/009/011，禁止为迁移 Action 语义创建第二生产 Runtime"
  contexts_missing:
    - "用户对 US-B2-001 实现落点四项边界的确认"
  contexts_stale: []
  outcome: "US-B2-001 落点草案完成并停在 confirmed=false；未创建业务代码或 Red 测试"
  utility: high
  reason: "把 Learning 行为迁移与未来 production Safety Executor 分开，避免架构边界倒退"
```

```yaml
skill_run:
  skill: feature-dev-assistant
  workflow_stage: story-development
  plan: Plans/功能开发/2026-08-17-agent全仓TypeScript重构.md
  date: 2026-08-17
  contexts_used:
    - path: Plans/功能开发/2026-08-17-agent全仓TypeScript重构-US-B0-001.tdd.json
      utility: high
      reason: "汇总真实 Red、Green、Refactor、smoke、逐 AC 与人工门禁证据"
    - path: /Users/wanglongxiang/git/agent/evidence/baselines/3d0c7a3fa5aea600d4d0a9b5c5dde012b8e9b5c4/baseline-manifest.v1.json
      utility: high
      reason: "证明显式旧提交在干净 worktree 上收集并通过 60/60 Python 测试"
    - path: /Users/wanglongxiang/git/agent/evaluation/cases/legacy-agent-definition-v1/case.json
      utility: high
      reason: "记录用户批准的完整 bundle SHA-256 与人工 review 引用"
  contexts_missing: []
  contexts_stale: []
  outcome: "US-B0-001 完成并通过 story-development 门禁；当前 Scope 不自动扩展，等待确认下一 Story"
  utility: high
  reason: "可信评估底座先于 Runtime 改造闭环完成，后续可用真实基线和失败关闭的资格门禁推进"
```

```yaml
skill_run:
  skill: task-splitter
  workflow_stage: story-split
  plan: Plans/功能开发/2026-08-17-agent全仓TypeScript重构.md
  date: 2026-08-17
  contexts_used:
    - path: Plans/功能开发/2026-08-17-agent全仓TypeScript重构.stories.json
      utility: high
      reason: "把当前 implementation Scope 从已完成 B0 精确切换到单一 US-B1-001"
    - path: Plans/功能开发/2026-08-17-agent全仓TypeScript重构-US-B0-001.tdd.json
      utility: high
      reason: "确认 US-B1-001 的唯一前置 Story 已通过自动化与人工证据门禁"
    - path: Plans/需求排序/2026-08-17-agent全仓TypeScript重构.md
      utility: high
      reason: "保持已确认的 B0→B1→B2→B3→B4→B5 顺序"
  contexts_missing: []
  contexts_stale: []
  outcome: "用户续做确认后只激活 US-B1-001；US-B0-001 退出当前 Scope，其余未完成 Story 仍未激活"
  utility: high
  reason: "修正机械门禁因单 Story Scope 完成而过早进入最终集成的状态，同时不扩大开发范围"
```

## 反馈（skill_run）

```yaml
skill_run:
  skill: task-splitter
  workflow_stage: story-split
  plan: Plans/功能开发/2026-08-17-agent全仓TypeScript重构.md
  date: 2026-08-17
  contexts_used:
    - path: Plans/需求分析/2026-08-17-agent全仓TypeScript重构.md
      utility: high
      reason: "把 22 组 GWT 与 M001—M060 语义矩阵完整映射到纵向 Story"
    - path: Plans/需求排序/2026-08-17-agent全仓TypeScript重构.md
      utility: high
      reason: "保持用户确认的 B0→B1→B2→B3→B4→B5 依赖顺序"
    - path: Plans/技术方案/2026-08-17-智能体控制系统工程架构-v0.1.md
      utility: high
      reason: "约束 DSH/Learning 隔离、SQLite Ledger、Safety 权限域和一次 cutover 的故事边界"
    - path: /Users/wanglongxiang/git/agent
      utility: high
      reason: "确认已有最小 TS/评估代码只能作为本 Epic 的重验候选，不能直接继承完成状态"
  contexts_missing:
    - "用户对 14 个 Story 边界、建议点数和 Epic Scope 的明确确认"
  contexts_stale: []
  outcome: "生成 14 个可独立演示验收的纵向 Story 草案，覆盖 B0—B5、GWT-001—022 与 M001—M060；未自动确认 Scope 或点数"
  utility: high
  reason: "把整个系统拆成按风险推进的用户能力，同时避免横向底座任务和超大 13 点 Story"
```

```yaml
skill_run:
  skill: task-splitter
  workflow_stage: story-split
  plan: Plans/功能开发/2026-08-17-agent全仓TypeScript重构.md
  date: 2026-08-17
  contexts_used:
    - path: Plans/功能开发/2026-08-17-agent全仓TypeScript重构.stories.json
      utility: high
      reason: "将用户确认同步到全局 Scope 与 14 个 Story 的点数确认字段"
    - path: Plans/Epic/2026-08-17-agent全仓TypeScript重构.md
      utility: high
      reason: "推进 client-dev 从 story-split 到 implementation-design，并保持 US-B0-001 为首个 Story"
    - path: Plans/技术方案/2026-08-17-智能体控制系统工程架构-v0.1.md
      utility: high
      reason: "确认所有 Scope Story 仍受已采纳架构、评估优先和一次 cutover 约束"
  contexts_missing: []
  contexts_stale: []
  outcome: "用户确认 14 个纵向 Story、5/8 点估算与完整 Epic Scope；主 Plan 已采纳，所有 estimate_confirmed=true"
  utility: high
  reason: "人工确认与 JSON 机器索引一致，P0 AC、GWT-001—022 和 M001—M060 均有 Scope Story 承接"
```

```yaml
skill_run:
  skill: implementation-design-assistant
  workflow_stage: implementation-design
  plan: Plans/功能开发/2026-08-17-agent全仓TypeScript重构.md
  date: 2026-08-17
  contexts_used:
    - path: Plans/功能开发/2026-08-17-agent全仓TypeScript重构.stories.json
      utility: high
      reason: "区分已确认的全 Epic Scope 与当前只激活 US-B0-001 的 implementation Scope"
    - path: Plans/需求分析/2026-08-17-agent全仓TypeScript重构.md
      utility: high
      reason: "落实评估优先、证据不足允许停止且不得为完成系统强推的需求约束"
    - path: /Users/wanglongxiang/git/agent
      utility: high
      reason: "确认当前已有评估骨架、60 个 Python 测试和三处未提交 Case 签署变更，后续落点必须基于真实代码"
  contexts_missing: []
  contexts_stale: []
  outcome: "在已确认的 14-Story Epic Scope 内只激活并完成 US-B0-001 实现落点确认，后续 13 个 Story 仍等待前置证据"
  utility: high
  reason: "当前门禁只要求设计 US-B0-001，既可继续推进，又保留评估失败时停止整个迁移的能力"
```

```yaml
skill_run:
  skill: feature-dev-assistant
  workflow_stage: story-development
  plan: Plans/功能开发/2026-08-17-agent全仓TypeScript重构.md
  date: 2026-08-17
  contexts_used:
    - path: Plans/功能开发/2026-08-17-agent全仓TypeScript重构-US-B0-001.tdd.json
      utility: high
      reason: "汇总真实 Red、Green、Refactor、smoke、逐 AC 与人工门禁证据"
    - path: /Users/wanglongxiang/git/agent/evidence/baselines/3d0c7a3fa5aea600d4d0a9b5c5dde012b8e9b5c4/baseline-manifest.v1.json
      utility: high
      reason: "证明显式旧提交在干净 worktree 上收集并通过 60/60 Python 测试"
    - path: /Users/wanglongxiang/git/agent/evaluation/cases/legacy-agent-definition-v1/case.json
      utility: high
      reason: "记录用户批准的完整 bundle SHA-256 与人工 review 引用"
  contexts_missing: []
  contexts_stale: []
  outcome: "US-B0-001 完成并通过 story-development 门禁；当前 Scope 不自动扩展，等待确认下一 Story"
  utility: high
  reason: "可信评估底座先于 Runtime 改造闭环完成，后续可用真实基线和失败关闭的资格门禁推进"
```

```yaml
skill_run:
  skill: implementation-design-assistant
  workflow_stage: implementation-design
  plan: Plans/功能开发/2026-08-17-agent全仓TypeScript重构.md
  date: 2026-08-17
  contexts_used:
    - path: Plans/功能开发/2026-08-17-agent全仓TypeScript重构-US-B1-001.impl.json
      utility: high
      reason: "统一记录 DSH 组合指纹、Cordis 可逆插件、6 组 Red 与失败停止条件"
    - path: /Users/wanglongxiang/git/agent/pnpm-workspace.yaml
      utility: high
      reason: "确认依赖锁定和 install script 审核必须位于 pnpm v11 workspace 真理源"
    - path: Plans/功能开发/2026-08-17-agent全仓TypeScript重构-US-B1-001.md
      utility: high
      reason: "汇总已核对的官方 Profile/Bundle/plugin 语义和本地 DSH 适配边界"
  contexts_missing: []
  contexts_stale: []
  outcome: "用户确认 US-B1-001 实现落点，当前允许进入 6 组 Red，但仍受上游不兼容停止条件约束"
  utility: high
  reason: "在写代码前识别出上游 rc.7 解析漂移和 install script 风险，避免把不可重放的安装当成 Green"
```

```yaml
skill_run:
  skill: feature-dev-assistant
  workflow_stage: story-development
  plan: Plans/功能开发/2026-08-17-agent全仓TypeScript重构.md
  date: 2026-08-17
  contexts_used:
    - path: Plans/功能开发/2026-08-17-agent全仓TypeScript重构-US-B1-001.tdd.json
      utility: high
      reason: "汇总六组真实 Red、Green、Refactor、官方 DSH smoke 和 GWT-005—008 逐项证据"
    - path: /Users/wanglongxiang/git/agent/profiles/controlled/composition.lock.json
      utility: high
      reason: "绑定 DSH/Cordis/toolchain、双 lock、本地源码、Bundle/Profile 与真实最终配置"
    - path: /Users/wanglongxiang/git/agent/docs/runbooks/dsh-composition.md
      utility: high
      reason: "固化组合冻结、校验、受控启动和漂移恢复的运维入口"
  contexts_missing: []
  contexts_stale: []
  outcome: "US-B1-001 已完成并提交 738c9cf；主计划保持 story-development，等待确认下一 Story Scope"
  utility: high
  reason: "生产 DSH 组合从概念边界落为可重放、可失败关闭、可逆卸载的真实工程切片"
```

```yaml
skill_run:
  skill: resume-assistant
  workflow_stage: story-split
  plan: Plans/功能开发/2026-08-17-agent全仓TypeScript重构.md
  date: 2026-08-17
  contexts_used:
    - path: Plans/Epic/2026-08-17-agent全仓TypeScript重构.md
      utility: high
      reason: "回放 Epic 阶段索引，识别机械门禁把单 Story 完成误判为全量集成入口"
    - path: Plans/功能开发/2026-08-17-agent全仓TypeScript重构.stories.json
      utility: high
      reason: "确认 14 条 Epic Scope 中只有 US-B1-001 仍被标为当前实现 Scope"
    - path: Plans/功能开发/2026-08-17-agent全仓TypeScript重构-US-B1-001.tdd.json
      utility: high
      reason: "确认上一 Story 已有完整 Red、Green、Refactor、smoke 与逐 AC 证据，可退出当前 Scope"
  contexts_missing: []
  contexts_stale: []
  outcome: "从 next-story-scope 断点恢复，确认应继续逐 Story 推进而非提前进入集成测试计划"
  utility: high
  reason: "避免机械工作流状态掩盖尚有 12 条未完成 Story 的真实进度"
```

```yaml
skill_run:
  skill: task-splitter
  workflow_stage: story-split
  plan: Plans/功能开发/2026-08-17-agent全仓TypeScript重构.md
  date: 2026-08-17
  contexts_used:
    - path: Plans/功能开发/2026-08-17-agent全仓TypeScript重构.stories.json
      utility: high
      reason: "把当前 implementation Scope 从已完成 US-B1-001 精确切换到单一 US-B1-002"
    - path: Plans/功能开发/2026-08-17-agent全仓TypeScript重构-US-B1-002.md
      utility: high
      reason: "保持 Learning Runtime 独立运行/恢复和生产拒绝的纵向验收边界"
    - path: Plans/技术方案/2026-08-17-智能体控制系统工程架构-v0.1.md
      utility: high
      reason: "约束 LangGraph.js 仅作学习 Runtime，不接生产凭证、部署或热切换"
  contexts_missing: []
  contexts_stale: []
  outcome: "用户回复 jixu 后只激活 US-B1-002；已完成 US-B1-001 退出 Scope，其余未完成 Story 保持未激活"
  utility: high
  reason: "把双 Runtime 架构的学习侧作为下一条可独立演示 Story，同时不扩大到 B2 迁移"
```

```yaml
skill_run:
  skill: implementation-design-assistant
  workflow_stage: implementation-design
  plan: Plans/功能开发/2026-08-17-agent全仓TypeScript重构.md
  date: 2026-08-17
  contexts_used:
    - path: Plans/功能开发/2026-08-17-agent全仓TypeScript重构-US-B1-002.impl.json
      utility: high
      reason: "统一记录 SQLite 持久恢复、Learning 凭证隔离、production role gate、4 组 Red 与失败停止条件"
    - path: /Users/wanglongxiang/git/agent/labs/runtimes/langgraph-ts/package.json
      utility: high
      reason: "确认现有 LangGraph.js 固定版本与官方 SQLite checkpointer 新依赖边界"
    - path: /Users/wanglongxiang/git/agent/packages/dsh-bridge/src/composition.ts
      utility: high
      reason: "识别根 lock/dsh-bridge 变化必须触发受审计的生产组合重冻与真实 DSH smoke"
  contexts_missing:
    - "用户对 US-B1-002 实现落点四项门禁的确认"
  contexts_stale: []
  outcome: "US-B1-002 实现落点草案完成；当前停在 confirmed=false，不进入 Red 或业务实现"
  utility: high
  reason: "把学习价值和生产隔离同时做成可运行、可故障注入的工程证据，而不是目录约定"
```

```yaml
skill_run:
  skill: feature-dev-assistant
  workflow_stage: story-development
  plan: Plans/功能开发/2026-08-17-agent全仓TypeScript重构.md
  date: 2026-08-17
  contexts_used:
    - path: Plans/功能开发/2026-08-17-agent全仓TypeScript重构-US-B1-002.tdd.json
      utility: high
      reason: "汇总四组真实 Red、Green、Refactor、双 Runtime smoke、供应链审计和 GWT-013/014 证据"
    - path: /Users/wanglongxiang/git/agent/labs/runtimes/langgraph-ts/runtime.manifest.json
      utility: high
      reason: "固化 learning/langgraph、offline、credentials=none 和 deployable=false 边界"
    - path: /Users/wanglongxiang/git/agent/profiles/controlled/composition.lock.json
      utility: high
      reason: "证明 Learning 依赖与 production role gate 变化后 DSH 组合已重新资格化"
  contexts_missing: []
  contexts_stale: []
  outcome: "US-B1-002 已完成并提交 27e5a1c；主计划保持逐 Story 开发，等待确认下一 Scope"
  utility: high
  reason: "跨进程 checkpoint 恢复、凭证隔离和生产拒绝都有真实可执行证据，且没有扩张为双生产 Runtime"
```

```yaml
skill_run:
  skill: resume-assistant
  workflow_stage: story-development
  plan: Plans/功能开发/2026-08-17-agent全仓TypeScript重构.md
  date: 2026-08-17
  contexts_used:
    - path: Plans/Epic/2026-08-17-agent全仓TypeScript重构.md
      utility: high
      reason: "确认前三个 Story 已完成且当前仍处于逐 Story 开发"
    - path: Plans/功能开发/2026-08-17-agent全仓TypeScript重构.stories.json
      utility: high
      reason: "识别滚动 Scope 断点并确定下一 Story 为 US-B2-001"
    - path: Plans/功能开发/2026-08-17-agent全仓TypeScript重构-US-B1-002.tdd.json
      utility: high
      reason: "确认 US-B2-001 的唯一前置已有完整 TDD 证据"
  contexts_missing: []
  contexts_stale: []
  outcome: "从 next-story-scope 断点恢复，继续逐 Story 开发而非提前进入集成测试"
  utility: high
  reason: "恢复点与 Epic 3/14 的真实完成度一致"
```

```yaml
skill_run:
  skill: task-splitter
  workflow_stage: story-split
  plan: Plans/功能开发/2026-08-17-agent全仓TypeScript重构.md
  date: 2026-08-17
  contexts_used:
    - path: Plans/功能开发/2026-08-17-agent全仓TypeScript重构.stories.json
      utility: high
      reason: "将唯一当前 implementation Scope 切换到 US-B2-001"
    - path: Plans/功能开发/2026-08-17-agent全仓TypeScript重构-US-B2-001.md
      utility: high
      reason: "保持 Action、审批、unknown 与人工恢复的 8 点纵向边界"
    - path: Plans/需求排序/2026-08-17-agent全仓TypeScript重构.md
      utility: high
      reason: "保持 B0→B1→B2→B3→B4→B5 的已确认顺序"
  contexts_missing: []
  contexts_stale: []
  outcome: "只激活 US-B2-001；US-B1-002 退出滚动 Scope，其余未完成 Story 未扩张"
  utility: high
  reason: "下一 Story 的唯一前置已满足，可独立设计与验收"
```

```yaml
skill_run:
  skill: implementation-design-assistant
  workflow_stage: implementation-design
  plan: Plans/功能开发/2026-08-17-agent全仓TypeScript重构.md
  date: 2026-08-17
  contexts_used:
    - path: Plans/功能开发/2026-08-17-agent全仓TypeScript重构-US-B2-001.impl.json
      utility: high
      reason: "固化 M001—M011 的共享契约、Learning Action 状态机、Red 与停止条件"
    - path: /Users/wanglongxiang/git/agent/capabilities/act.py
      utility: high
      reason: "提取审批、unknown、人工恢复、虚拟输入和不可信输出的旧行为基线"
    - path: /Users/wanglongxiang/git/agent/migration/legacy-test-map.json
      utility: high
      reason: "发现旧 packages/agent-loop 目标与已采纳 Learning Lab 矩阵漂移"
    - path: Plans/技术方案/2026-08-17-智能体控制系统工程架构-v0.1.md
      utility: high
      reason: "约束 ENG-008/009/011，禁止创建第二生产 Runtime"
  contexts_missing:
    - "用户对 US-B2-001 实现落点四项边界的确认"
  contexts_stale: []
  outcome: "US-B2-001 落点草案完成并停在 confirmed=false；未创建业务代码或 Red 测试"
  utility: high
  reason: "把 Learning 行为迁移与未来 production Safety Executor 分离"
```

```yaml
skill_run:
  skill: resume-assistant
  workflow_stage: implementation-design
  plan: Plans/功能开发/2026-08-17-agent全仓TypeScript重构.md
  date: 2026-08-17
  contexts_used:
    - path: Plans/功能开发/2026-08-17-agent全仓TypeScript重构-US-B2-001.impl.json
      utility: high
      reason: "读取用户刚确认的代码落点、Red、依赖边界和停止条件"
    - path: Plans/功能开发/2026-08-17-agent全仓TypeScript重构-US-B2-001.md
      utility: high
      reason: "确认当前唯一 Scope、8 点 Story 与 M001—M011 验收边界"
    - path: Plans/Epic/2026-08-17-agent全仓TypeScript重构.md
      utility: high
      reason: "保持 Epic 处于逐 Story 开发且不提前进入集成测试"
  contexts_missing: []
  contexts_stale: []
  outcome: "用户回复‘继续’后确认 US-B2-001 落点门禁，并从 implementation-design 恢复到 Red"
  utility: high
  reason: "开发严格继承已确认 Scope 与架构边界，没有扩到 B2-002/B4"
```

```yaml
skill_run:
  skill: feature-dev-assistant
  workflow_stage: story-development
  plan: Plans/功能开发/2026-08-17-agent全仓TypeScript重构.md
  date: 2026-08-17
  contexts_used:
    - path: Plans/功能开发/2026-08-17-agent全仓TypeScript重构-US-B2-001.tdd.json
      utility: high
      reason: "汇总真实 Red、Green、Refactor、integration smoke、逐 M001—M011 与提交证据"
    - path: /Users/wanglongxiang/git/agent/labs/runtimes/langgraph-ts/src/action.ts
      utility: high
      reason: "实现 Learning-only Action 状态机、审批/unknown/输入恢复和不可信输出边界"
    - path: /Users/wanglongxiang/git/agent/packages/contracts/schemas/learning-action-session.v1.json
      utility: high
      reason: "固化跨 checkpoint 的版本化 Action session，且与 future production ActionIntent/Receipt 分离"
    - path: /Users/wanglongxiang/git/agent/profiles/controlled/composition.lock.json
      utility: high
      reason: "证明共享 contracts 变更后生产组合已显式重冻并通过 verify"
  contexts_missing: []
  contexts_stale: []
  outcome: "US-B2-001 已完成并提交 bded643；主计划保持逐 Story 开发，等待确认下一 Scope"
  utility: high
  reason: "M001—M011 有真实 Red→Green→Refactor 与全量回归，且未创建第二生产 Runtime"
```
