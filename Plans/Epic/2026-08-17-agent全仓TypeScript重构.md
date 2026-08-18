---
tags: [Epic, client-dev, 智能体, TypeScript, DSH, LangGraph]
type: plan
category: Epic
status: 进行中
date: 2026-08-17
epic_id: agent-full-typescript-restructure
workflow: client-dev
lifecycle_state: story-development
platform: 服务端与智能体Runtime
repo: /Users/wanglongxiang/git/agent
branch: codex/full-ts-restructure
p0_open: 0
plans:
  requirement: Plans/需求分析/2026-08-17-agent全仓TypeScript重构.md
  prioritization: Plans/需求排序/2026-08-17-agent全仓TypeScript重构.md
  architecture: Plans/技术方案/2026-08-17-智能体控制系统工程架构-v0.1.md
  development: Plans/功能开发/2026-08-17-agent全仓TypeScript重构.md
  integration_plan: Plans/自动化测试/2026-08-17-agent全仓TypeScript重构-集成测试计划.md
  integration: Plans/自动化测试/2026-08-17-agent全仓TypeScript重构-集成测试.md
relations:
  depends_on:
    - Plans/技术方案/2026-08-17-智能体控制系统工程架构-v0.1.md
    - Plans/代码重构/2026-08-17-agent控制系统工程落点-v0.1.md
  dependents: []
  supersedes: []
  superseded_by: []
  conflicts: []
---
# Epic：Agent 全仓 TypeScript 重构（client-dev）

**创建日期**：2026-08-17
**关联仓库**：`/Users/wanglongxiang/git/agent` · **分支**：`codex/full-ts-restructure`

> 最终目标是纯 TypeScript monorepo：DSH/Cordis 为唯一生产 Runtime，LangGraph.js 为隔离 Learning Runtime。开发内部按证据逐步完成，最终只做一次 cutover；未通过门禁前不删除 Python 基线。

## 一、阶段索引

| 阶段 | stage key | Plan | 状态 |
|---|---|---|---|
| 需求分析 | requirement | `Plans/需求分析/2026-08-17-agent全仓TypeScript重构.md` | ✅ 已采纳，P0=0 |
| 需求排序 | prioritization | `Plans/需求排序/2026-08-17-agent全仓TypeScript重构.md` | ✅ 已采纳，B0→B1→B2→B3→B4→B5 |
| 正式架构设计 | architecture | `Plans/技术方案/2026-08-17-智能体控制系统工程架构-v0.1.md` | ✅ 已采纳，ENG-012=SQLite WAL + Provider Port |
| 功能故事拆分与故事点 | story-split | `Plans/功能开发/2026-08-17-agent全仓TypeScript重构.md` | ✅ 14 个纵向 Story、点数与 Scope 已确认 |
| 实现落点设计 | implementation-design | 同上及动态故事子 Plan | ✅ US-B2-005 落点已确认 |
| 逐故事 TDD | story-development | 同上及动态故事子 Plan | 🟨 前 8 个 Story 已完成；等待确认下一滚动 Scope |
| 集成测试计划与审核 | integration-test-plan | `Plans/自动化测试/2026-08-17-agent全仓TypeScript重构-集成测试计划.md` | ⬜ |
| 全量集成测试 | integration-test | `Plans/自动化测试/2026-08-17-agent全仓TypeScript重构-集成测试.md` | ⬜ |

## 二、阶段门禁

| 阶段 | 退出条件 |
|---|---|
| requirement | 纯 TS 目标、双 Runtime 边界、迁移资产、失败停止条件和 cutover AC 已采纳，P0=0 |
| prioritization | B0—B5 Backlog 的价值、依赖、风险验证价值和优先级经确认 |
| architecture | 目标目录、模块边界、DSH seam、Schema、NFR、ADR 和影响矩阵已采纳 |
| story-split | 每个 Scope Story 是可演示纵切，覆盖 Python 60 tests 语义映射和 DSH 集成 |
| implementation-design | 每个 Scope Story 明确文件落点、依赖方向、Red 测试和删除保护 |
| story-development | 每个 Story 有真实 Red/Green/Refactor/smoke 和逐 AC 证据 |
| integration-test-plan | 覆盖 production DSH、Learning Runtime、插件生命周期、故障注入、60 tests parity、cutover rehearsal |
| integration-test | 全量证据与人工签署通过后才允许删除 Python 并完成一次 cutover |

## 三、动态用户故事看板

故事真理源：`Plans/功能开发/2026-08-17-agent全仓TypeScript重构.stories.json`。

| Story | 用户能力 | 优先级 | 建议点数 | Scope 建议 | 依赖 | 状态 |
|---|---|---|---:|:---:|---|---|
| US-B0-001 | 基线冻结与评估尺资格 | P0 | 8 | true | — | ✅ 已完成，`qualified=true` |
| US-B1-001 | DSH 固定组合与可逆插件 | P0 | 8 | true | US-B0-001 | ✅ 已完成，提交 `738c9cf` |
| US-B1-002 | LangGraph.js Learning Runtime 与隔离 | P0 | 8 | true | US-B0-001 | ✅ 已完成，提交 `27e5a1c` |
| US-B2-001 | Action/审批/unknown 语义 | P0 | 8 | true | US-B1-002 | ✅ 已完成，提交 `bded643` |
| US-B2-002 | Definition/LLM/Planning/Role 语义 | P0 | 8 | true | US-B1-001/002 | ✅ 已完成，提交 `5bcce5a` |
| US-B2-003 | 单 Agent 暂停/恢复/回放/fork | P0 | 8 | true | US-B2-001/002 | ✅ 已完成，提交 `b359c77` |
| US-B2-004 | Team Learning Graph | P0 | 5 | true | US-B2-003 | ✅ 已完成，提交 `4931d32` |
| US-B2-005 | 结构化工具与 CLI | P0 | 8 | true | US-B2-001/003 | ✅ 已完成，提交 `61b2fed` |
| US-B3-001 | SQLite Ledger 动态镜像 | P0 | 8 | true | US-B1-001/B2-002 | 等待前置证据 |
| US-B3-002 | 控制命令分段回执 | P0 | 8 | true | US-B3-001 | 等待前置证据 |
| US-B4-001 | Safety Executor 受控执行 | P0 | 8 | true | US-B3-002 | 等待前置证据 |
| US-B4-002 | Watchdog 组合证明与降级 | P0 | 5 | true | US-B1-001/B4-001 | 等待前置证据 |
| US-B5-001 | Cutover rehearsal | P0 | 8 | true | B2/B3/B4 完成 | 等待前置证据 |
| US-B5-002 | 人工批准后一次 cutover | P0 | 5 | true | US-B5-001 | 等待前置证据 |

## 四、已确认边界

- 整个最终工作树不保留 Python；
- DSH/Cordis 是唯一生产 Agent Loop，不 fork DSH；
- LangGraph.js 保留为学习 Runtime，不接生产凭证、部署或热切换；
- 先验证评估可靠性，允许 ABSTAIN/INVALID/blocked；
- 60 个 Python 测试必须逐项形成 TS 语义映射；
- 最终删除 Python 必须是独立 cutover 门禁，不由“目录看起来完成”替代。

## 五、变更记录

| 日期 | 变更 | 影响阶段 | 证据 | 确认人 |
|---|---|---|---|---|
| 2026-08-17 | 创建完整重构 Epic 与专用分支 | 全流程 | 用户要求重新开分支按步骤改造 | wanglongxiang |
| 2026-08-17 | 完成 22 组实例化需求并同步真实 P0 数 | requirement | 需求 Plan `p0_open=4`，禁止看板误报可开工 | Codex |
| 2026-08-17 | 完成 60/60 Python tests 语义迁移登记 | requirement | pytest 采集 60 个 node ID；全部 `migrate`，无 waiver | Codex |
| 2026-08-17 | 固定并验证 DSH npm rc.6 基线 | requirement | 最小 out-of-tree Cordis hook 插件 typecheck 通过；CLI `0.1.0-rc.6` | Codex |
| 2026-08-17 | 确认 Safety Executor v0.1 边界并签署 Case v1 | requirement | 用户确认独立权限域；Case 正例/负例/坏环境重放后 `qualified=true` | wanglongxiang |
| 2026-08-17 | 确认 B0→B1→B2→B3→B4→B5 Backlog 顺序 | prioritization | Backlog 全局与六项需求均 `confirmed=true`，机械门禁通过 | wanglongxiang |
| 2026-08-17 | 补齐正式架构交接契约 | architecture | API Schema、实体字段、错误码、非功能约束、ADR、B0—B5 影响矩阵已通过格式门禁；ENG-012 待确认 | Codex |
| 2026-08-17 | 确认 ENG-012 并采纳正式架构 | architecture | Control Ledger v0.1=SQLite WAL 单写者 + Provider Port；架构 Plan `status=已采纳` | wanglongxiang |
| 2026-08-17 | 生成全 Epic 纵向 Story 草案 | story-split | 14 个 Story 覆盖 GWT-001—022、M001—M060 与 B0—B5；点数/Scope 未自动确认 | Codex |
| 2026-08-17 | 确认 14 个 Story、点数与 Epic Scope | story-split | `.stories.json` 全局 `scope_confirmed=true`，逐项 `estimate_confirmed=true` | wanglongxiang |
| 2026-08-17 | 生成 US-B0-001 实现落点草案 | implementation-design | 识别 Case qualification 只消费单负对照的可信度缺口；设计 baseline/test-map/evidence bundle Red | Codex |
| 2026-08-17 | 完成 US-B0-001 Red→Green→Refactor 与基线实证 | story-development | 代码 `02d77b5`；干净提交基线 Python 60/60、TS 28/28、typecheck 通过；新 Case bundle 等待人工签署 | Codex |
| 2026-08-17 | 人工确认 B0 迁移语义并签署完整 Case bundle | story-development | 用户确认 M001—M060；批准 bundle `3ad17826…432c`；提交 `e3fae6b` 重放 `qualified=true` | wanglongxiang |
| 2026-08-17 | 激活 US-B1-001 为下一 implementation Scope | story-development | 用户在明确建议激活 US-B1-001 后回复“继续”；US-B0-001 前置门禁已通过 | wanglongxiang |
| 2026-08-17 | 完成 US-B1-001 实现落点草案 | implementation-design | 实证单锁 dsh rc.6 会漂向不完整 rc.7；设计 wildcard override、最小 allowBuilds、双 lock/真实 dump 指纹和 6 组 Red | Codex |
| 2026-08-17 | 确认 US-B1-001 实现落点 | implementation-design | 用户在四项门禁摘要后回复“继续”；`.impl.json confirmed=true` | wanglongxiang |
| 2026-08-17 | 完成 US-B1-001 Red→Green→Refactor 与官方 DSH smoke | story-development | 代码 `738c9cf`；组合指纹 `cfe884f…d681`；TS 46/46、Python 60/60、typecheck、verify、frozen install 与 controlled Profile smoke 通过 | Codex |
| 2026-08-17 | 激活 US-B1-002 为下一 implementation Scope | story-split | 用户在明确提示激活 LangGraph.js Learning Runtime Story 后回复“jixu”；其余未完成 Story 未扩张 | wanglongxiang |
| 2026-08-17 | 完成 US-B1-002 实现落点草案 | implementation-design | 设计官方 SQLite 跨进程恢复、Learning 环境 allowlist、production role gate、依赖/部署/凭证反例与 4 组 Red；待人工确认 | Codex |
| 2026-08-17 | 确认 US-B1-002 实现落点 | implementation-design | 用户在四项门禁摘要后回复“继续”；`.impl.json confirmed=true` | wanglongxiang |
| 2026-08-17 | 完成 US-B1-002 Red→Green→Refactor 与双 Runtime smoke | story-development | 代码 `27e5a1c`；跨进程 SQLite resume、凭证/部署隔离和 production role gate 通过；TS 52/52、Python 60/60；审计 0 已知漏洞；DSH 指纹 `e59e8be7…ceb31a` | Codex |
| 2026-08-17 | 激活 US-B2-001 为下一 implementation Scope | story-development | 用户回复“继续任务”；US-B1-002 前置门禁已通过；其余未完成 Story 未扩张 | wanglongxiang |
| 2026-08-17 | 确认 US-B2-001 实现落点 | implementation-design | 用户在共享契约、Learning Action 状态机、M001—M011 Red 与生产边界摘要后回复“继续” | wanglongxiang |
| 2026-08-17 | 完成 US-B2-001 Red→Green→Refactor | story-development | 代码 `bded643`；M001—M011 定向 15/15、TS 66/66、Python 60/60、typecheck 与组合 `80f0fc8e…701e` 通过 | Codex |
| 2026-08-17 | 激活 US-B2-002 为下一 implementation Scope | story-split | 用户在 US-B2-001 完成后回复“继续”；US-B1-001/002 前置门禁已通过；其余未完成 Story 未扩张 | wanglongxiang |
| 2026-08-17 | 完成 US-B2-002 实现落点草案 | implementation-design | 设计共享 agent-definition 与 Learning-only llm-json/planning/roles，逐项覆盖 M012—M025；待人工确认 | Codex |
| 2026-08-17 | 确认 US-B2-002 实现落点 | implementation-design | 用户在共享 Definition、Learning-only JSON/Planning/Role、M012—M025 Red 与组合保护摘要后回复“继续” | wanglongxiang |
| 2026-08-17 | 完成 US-B2-002 Red→Green→Refactor | story-development | 代码 `5bcce5a`；M012—M025 定向 17/17、TS 82/82、Python 60/60、typecheck、冻结安装与组合 `d1c52876…3083f` 通过 | Codex |
| 2026-08-17 | 激活 US-B2-003 为下一 implementation Scope | story-split | 用户在 US-B2-002 完成后回复“继续”；US-B2-001/002 前置门禁已通过；其余未完成 Story 未扩张 | wanglongxiang |
| 2026-08-17 | 完成 US-B2-003 实现落点草案 | implementation-design | 设计单 Agent 原生 StateGraph、精确 resume、safe fork、版本化 trace 与 M026—M037 Red；待人工确认 | Codex |
| 2026-08-17 | 确认 US-B2-003 实现落点并进入 Red | story-development | 用户回复“继续”，确认文件边界、依赖方向、Red 与停止条件；Scope 保持仅 US-B2-003 | wanglongxiang |
| 2026-08-17 | 完成 US-B2-003 Red→Green→Refactor | story-development | 代码 `b359c77`；M026—M037 定向 15/15、TS 94/94、Python 60/60、typecheck、冻结安装与组合 `f699e623…45b39` 通过 | Codex |
| 2026-08-18 | 激活 US-B2-004 为下一 implementation Scope | story-split | 用户在 US-B2-003 完成后回复“继续”；前置 TDD/提交证据通过；其余 7 条未完成 Story 未扩张 | wanglongxiang |
| 2026-08-18 | 完成 US-B2-004 实现落点草案 | implementation-design | 设计显式 Team graph edges、逐节点 handoff、精确 Action resume、retry limit 与 M038—M043 单一 Red 真源；待人工确认 | Codex |
| 2026-08-18 | 确认 US-B2-004 实现落点并进入 Red | story-development | 用户回复“继续”，确认文件边界、依赖方向、Red 与停止条件；Scope 保持仅 US-B2-004 | wanglongxiang |
| 2026-08-18 | 完成 US-B2-004 Red→Green→Refactor | story-development | 代码 `4931d32`；M038—M043 Team 6/6、TS 100/100、Python 60/60、typecheck、冻结安装和生产组合 `f699e623…45b39` 通过 | Codex |
| 2026-08-18 | 激活 US-B2-005 为下一 implementation Scope | story-split | 用户在 US-B2-004 完成后回复“继续”；前置 TDD/提交证据通过；其余 6 条未完成 Story 未扩张 | wanglongxiang |
| 2026-08-18 | 完成并确认 US-B2-005 实现落点 | implementation-design | 设计共享 MCP 结果契约、Learning-only 工具、single/team CLI、TS terminal adapter 与 M044—M060 Red；用户回复“继续”确认 | wanglongxiang |
| 2026-08-18 | 完成 US-B2-005 Red→Green→Refactor | story-development | 代码 `61b2fed`；M044—M060 目标 18/18、TS 120/120、Python 60/60、typecheck、冻结安装与生产组合 `2467ba28…bbdd3` 通过 | Codex |

## 续做

```text
/resume plan=Plans/功能开发/2026-08-17-agent全仓TypeScript重构.md 进度=next-story-scope
```

## 反馈（skill_run）

```yaml
skill_run:
  skill: template-generator
  workflow_stage: requirement
  plan: Plans/Epic/2026-08-17-agent全仓TypeScript重构.md
  date: 2026-08-17
  contexts_used:
    - path: Templates/Epic模板-client-dev.md
      utility: high
      reason: "提供 client-dev Epic 阶段索引、门禁和动态故事骨架"
    - path: Plans/技术方案/2026-08-17-智能体控制系统工程架构-v0.1.md
      utility: high
      reason: "提供纯 TS、DSH 生产、LangGraph.js 学习 Runtime 和一次 cutover 边界"
  contexts_missing: []
  contexts_stale: []
  outcome: "创建 Agent 全仓 TypeScript 重构 Epic，并绑定 codex/full-ts-restructure 分支"
  utility: high
  reason: "把此前零散故事重新纳入完整 client-dev 生命周期，避免再次把过渡态当最终结构"
```

```yaml
skill_run:
  skill: feature-dev-assistant
  workflow_stage: story-development
  plan: Plans/Epic/2026-08-17-agent全仓TypeScript重构.md
  date: 2026-08-17
  contexts_used:
    - path: Plans/功能开发/2026-08-17-agent全仓TypeScript重构-US-B0-001.md
      utility: high
      reason: "同步首个可信评估 Story 的完成状态、提交与人工验收结果"
    - path: Plans/功能开发/2026-08-17-agent全仓TypeScript重构-US-B0-001.tdd.json
      utility: high
      reason: "证明八项 AC、人工门禁和集成 smoke 均已通过"
  contexts_missing: []
  contexts_stale: []
  outcome: "Epic 的 B0 可信评估阶段完成，保持 story-development 并等待下一 implementation Scope 确认"
  utility: high
  reason: "Epic 看板与代码、TDD 证据和用户签署保持一致，且没有自动扩大后续 Scope"
```

```yaml
skill_run:
  skill: resume-assistant
  workflow_stage: implementation-design
  plan: Plans/Epic/2026-08-17-agent全仓TypeScript重构.md
  date: 2026-08-17
  contexts_used:
    - path: Plans/功能开发/2026-08-17-agent全仓TypeScript重构.stories.json
      utility: high
      reason: "恢复时确认当前唯一 implementation Scope 为 US-B1-001，不误进最终集成"
    - path: Plans/功能开发/2026-08-17-agent全仓TypeScript重构-US-B0-001.tdd.json
      utility: high
      reason: "确认 B1 的 B0 可信评估前置已有 qualified=true 和人工签署"
    - path: Plans/功能开发/2026-08-17-agent全仓TypeScript重构-US-B1-001.md
      utility: high
      reason: "从已激活 Story 的 implementation-design 断点继续，而非重做已完成 B0"
  contexts_missing:
    - "用户对 US-B1-001 实现落点门禁的确认"
  contexts_stale: []
  outcome: "已恢复到 US-B1-001 implementation-design，完成草案和上游安装风险实证，按门禁暂停于人工确认"
  utility: high
  reason: "准确继承已签署 B0 和当前 B1 Scope，避免重复工作或越过落点确认写代码"
```

```yaml
skill_run:
  skill: feature-dev-assistant
  workflow_stage: story-development
  plan: Plans/Epic/2026-08-17-agent全仓TypeScript重构.md
  date: 2026-08-17
  contexts_used:
    - path: Plans/功能开发/2026-08-17-agent全仓TypeScript重构-US-B1-001.md
      utility: high
      reason: "同步固定 DSH 组合与 Cordis 可逆插件 Story 的完成状态和逐 AC 验收"
    - path: Plans/功能开发/2026-08-17-agent全仓TypeScript重构-US-B1-001.tdd.json
      utility: high
      reason: "证明 Red、Green、Refactor、集成 smoke、组合指纹和代码提交均已闭环"
  contexts_missing: []
  contexts_stale: []
  outcome: "Epic 已完成 US-B0-001 与 US-B1-001，保持逐故事推进并等待激活 US-B1-002"
  utility: high
  reason: "看板与真实代码、测试和用户门禁一致，没有把单 Story 完成误报为整个系统完成"
```

```yaml
skill_run:
  skill: task-splitter
  workflow_stage: story-split
  plan: Plans/Epic/2026-08-17-agent全仓TypeScript重构.md
  date: 2026-08-17
  contexts_used:
    - path: Plans/功能开发/2026-08-17-agent全仓TypeScript重构.stories.json
      utility: high
      reason: "同步唯一当前 Scope=US-B1-002，并让已完成 US-B1-001 退出 sprint_scope"
    - path: Plans/功能开发/2026-08-17-agent全仓TypeScript重构-US-B1-002.md
      utility: high
      reason: "同步 Learning Runtime 的独立运行、恢复和生产拒绝验收边界"
  contexts_missing: []
  contexts_stale: []
  outcome: "Epic 继续处于逐 Story 开发，当前只激活 US-B1-002 并进入 implementation-design"
  utility: high
  reason: "纠正单 Story Scope 完成引发的集成阶段误判，保持 14 条 Story 的真实推进顺序"
```

```yaml
skill_run:
  skill: implementation-design-assistant
  workflow_stage: implementation-design
  plan: Plans/Epic/2026-08-17-agent全仓TypeScript重构.md
  date: 2026-08-17
  contexts_used:
    - path: Plans/功能开发/2026-08-17-agent全仓TypeScript重构-US-B1-002.md
      utility: high
      reason: "同步 Learning Runtime 当前 Scope 的落点、Red、停止条件与未确认门禁"
    - path: Plans/功能开发/2026-08-17-agent全仓TypeScript重构-US-B1-002.impl.json
      utility: high
      reason: "将跨进程恢复和生产隔离方案作为机器可校验的开发前契约"
  contexts_missing:
    - "用户对 US-B1-002 实现落点四项门禁的确认"
  contexts_stale: []
  outcome: "Epic 保持 implementation-design；US-B1-002 未经确认不进入开发"
  utility: high
  reason: "忠实呈现真实阻断状态，避免把已写方案误报为已实现 Learning Runtime"
```

```yaml
skill_run:
  skill: feature-dev-assistant
  workflow_stage: story-development
  plan: Plans/Epic/2026-08-17-agent全仓TypeScript重构.md
  date: 2026-08-17
  contexts_used:
    - path: Plans/功能开发/2026-08-17-agent全仓TypeScript重构-US-B1-002.md
      utility: high
      reason: "同步 Learning Runtime 跨进程恢复、生产隔离、供应链修复和逐 AC 完成状态"
    - path: Plans/功能开发/2026-08-17-agent全仓TypeScript重构-US-B1-002.tdd.json
      utility: high
      reason: "证明四组 Red、Green、Refactor、双 Runtime smoke 和代码提交已闭环"
  contexts_missing: []
  contexts_stale: []
  outcome: "Epic 已完成前三个 Story，保持逐 Story 推进并等待激活 US-B2-001"
  utility: high
  reason: "Epic 看板与真实代码、测试、供应链审计和用户门禁一致，没有误报全量系统完成"
```

```yaml
skill_run:
  skill: resume-assistant
  workflow_stage: implementation-design
  plan: Plans/Epic/2026-08-17-agent全仓TypeScript重构.md
  date: 2026-08-18
  contexts_used:
    - path: Plans/功能开发/2026-08-17-agent全仓TypeScript重构-US-B2-003.tdd.json
      utility: high
      reason: "证明第 6 条 Story 已真实完成，可恢复到依赖就绪的 US-B2-004"
    - path: Plans/功能开发/2026-08-17-agent全仓TypeScript重构.stories.json
      utility: high
      reason: "确认当前唯一 Scope 已切换为 US-B2-004，仍有 8 条 Story 未完成"
  contexts_missing: []
  contexts_stale: []
  outcome: "Epic 从 US-B2-003 完成态恢复到 US-B2-004 落点设计，未进入集成测试"
  utility: high
  reason: "让 Epic 声称阶段与真实 Story/TDD 证据保持一致"
```

```yaml
skill_run:
  skill: task-splitter
  workflow_stage: story-split
  plan: Plans/Epic/2026-08-17-agent全仓TypeScript重构.md
  date: 2026-08-18
  contexts_used:
    - path: Plans/功能开发/2026-08-17-agent全仓TypeScript重构.stories.json
      utility: high
      reason: "同步唯一当前 Scope=US-B2-004，并让已完成 US-B2-003 退出 sprint_scope"
    - path: Plans/功能开发/2026-08-17-agent全仓TypeScript重构-US-B2-004.md
      utility: high
      reason: "同步 Team Learning Graph 的 5 点边界和 M038—M043 验收范围"
  contexts_missing: []
  contexts_stale: []
  outcome: "Epic 继续处于逐 Story 开发，仅 US-B2-004 进入 implementation-design"
  utility: high
  reason: "单 Story Scope 切换不会被误判为全量集成条件成立"
```

```yaml
skill_run:
  skill: implementation-design-assistant
  workflow_stage: implementation-design
  plan: Plans/Epic/2026-08-17-agent全仓TypeScript重构.md
  date: 2026-08-18
  contexts_used:
    - path: Plans/功能开发/2026-08-17-agent全仓TypeScript重构-US-B2-004.md
      utility: high
      reason: "同步当前 Team Story 的边界、状态和未确认门禁"
    - path: Plans/功能开发/2026-08-17-agent全仓TypeScript重构-US-B2-004.impl.json
      utility: high
      reason: "将显式路由、handoff、精确恢复、retry 与 Red 作为机器可校验开发前契约"
  contexts_missing:
    - "用户对 US-B2-004 实现落点四项门禁的确认"
  contexts_stale: []
  outcome: "Epic 保持 implementation-design；前 6 条 Story 完成，US-B2-004 未经确认不进入 Red"
  utility: high
  reason: "忠实呈现等待人工确认而非业务报错，也没有提前推进集成阶段"
```

```yaml
skill_run:
  skill: feature-dev-assistant
  workflow_stage: story-development
  plan: Plans/Epic/2026-08-17-agent全仓TypeScript重构.md
  date: 2026-08-18
  contexts_used:
    - path: Plans/功能开发/2026-08-17-agent全仓TypeScript重构-US-B2-004.md
      utility: high
      reason: "同步 Team Learning Graph Story 的完成状态、提交和逐 AC 验收"
    - path: Plans/功能开发/2026-08-17-agent全仓TypeScript重构-US-B2-004.tdd.json
      utility: high
      reason: "证明 Red、Green、Refactor、集成 smoke、生产组合不变与代码提交均已闭环"
  contexts_missing: []
  contexts_stale: []
  outcome: "Epic 已完成前 7 个 Story，保持逐 Story 推进并等待激活下一条滚动 Scope"
  utility: high
  reason: "看板与真实代码、测试和用户门禁一致，没有把 Team Story 完成误报为全量系统完成"
```

```yaml
skill_run:
  skill: feature-dev-assistant
  workflow_stage: story-development
  plan: Plans/Epic/2026-08-17-agent全仓TypeScript重构.md
  date: 2026-08-18
  contexts_used:
    - path: Plans/功能开发/2026-08-17-agent全仓TypeScript重构-US-B2-005.md
      utility: high
      reason: "同步结构化工具与 CLI Story 的完成状态、提交和逐 AC 验收"
    - path: Plans/功能开发/2026-08-17-agent全仓TypeScript重构-US-B2-005.tdd.json
      utility: high
      reason: "证明 Red、Green、Refactor、双 Runtime smoke、组合重冻与代码提交均已闭环"
  contexts_missing: []
  contexts_stale: []
  outcome: "Epic 已完成前 8 个 Story，保持逐 Story 推进并等待激活 US-B3-001"
  utility: high
  reason: "看板与真实代码、测试和人工门禁一致，没有把 B2 完成误报为全量系统完成"
```
