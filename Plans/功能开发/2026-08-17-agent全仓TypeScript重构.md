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

**Scope 语义**：14 个 Story 全部属于已确认的 Epic Scope。前 10 个 Story（截至 `US-B3-002`）已完成；当前滚动 Scope 仍只记录刚完成的 `US-B3-002`，等待用户再次确认后才切换下一 Story。其余 4 个未完成 Story 保持 `sprint_scope=false`，不因机械门禁误判为最终集成阶段而一次性扩张。

## 五、实现落点设计

当前唯一滚动 Scope `US-B3-002` 已完成并提交；下一 Story 尚未激活，不进入最终集成测试。

| Story | 实现落点 | 关键边界 | 状态 |
|---|---|---|---|
| US-B1-001 | `Plans/功能开发/2026-08-17-agent全仓TypeScript重构-US-B1-001.impl.json` | 不 fork DSH；`dsh-bridge + Cordis plugin + Bundles + controlled Profile`；指纹绑定真实 artifact/lock/source/dump | ✅ 已完成，提交 `738c9cf` |
| US-B1-002 | `Plans/功能开发/2026-08-17-agent全仓TypeScript重构-US-B1-002.impl.json` | 官方 SQLite checkpoint；跨进程 resume；Learning 环境 allowlist；production manifest 前置拒绝；无部署/反向依赖 | ✅ 已完成，提交 `27e5a1c` |
| US-B2-001 | `Plans/功能开发/2026-08-17-agent全仓TypeScript重构-US-B2-001.impl.json` | Lab 内 Action 纯状态机 + 共享序列化契约；M001—M011；不创建第二生产 Agent Loop，不提前实现 B4 Safety Executor | ✅ 已完成，提交 `bded643` |
| US-B2-002 | `Plans/功能开发/2026-08-17-agent全仓TypeScript重构-US-B2-002.impl.json` | 共享 agent-definition；Lab 内注入式 JSON/Planning/Role；M012—M025；不引入模型 SDK或第二生产 Runtime | ✅ 已完成，提交 `5bcce5a` |
| US-B2-003 | `Plans/功能开发/2026-08-17-agent全仓TypeScript重构-US-B2-003.impl.json` | 原生 StateGraph/SQLite resume/replay/fork；steps-only safe fork；版本化 RunResult trace；M026—M037 | ✅ 已完成，提交 `b359c77` |
| US-B2-004 | `Plans/功能开发/2026-08-17-agent全仓TypeScript重构-US-B2-004.impl.json` | 显式 Team graph edges；逐节点 handoff 事件；精确 Action resume；retry limit；复用 RunResult/Trace；M038—M043 | ✅ 已完成，提交 `4931d32` |
| US-B2-005 | `Plans/功能开发/2026-08-17-agent全仓TypeScript重构-US-B2-005.impl.json` | 共享 MCP 结果契约；Learning-only 本地工具；raw CLI + single/team TUI；同 thread resume；TS terminal adapter；M044—M060 | ✅ 已完成，提交 `61b2fed` |
| US-B3-001 | `Plans/功能开发/2026-08-17-agent全仓TypeScript重构-US-B3-001.impl.json` | control-fact/projection 契约；rc.6 observer；flush durability；SQLite WAL/FULL Provider；确定性重放与损坏恢复 | ✅ 已完成，提交 `f52d855` |
| US-B3-002 | `Plans/功能开发/2026-08-17-agent全仓TypeScript重构-US-B3-002.impl.json` | command/receipt 契约；纯 waterfall；rc.6 pause/restrict/stop adapter；逐段 durable receipt；短路/unknown 失败关闭 | ✅ 已完成，提交 `27d1021` |

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

US-B1-002 完成后，Scope 曾按用户“继续任务”切换为唯一 `US-B2-001`；后续状态以当前 Scope 段和故事索引为准。

### 5.3 US-B2-001 实现证据

- 代码提交：`bded643f54700136681b0a819034c7d21fc1e65f`。
- 共享 `learning-action-session.v1` Schema 与判别联合；Learning Lab 以注入 port 实现 Action/审批/unknown/输入恢复，不依赖 DSH、Cordis、生产凭证或 Safety Executor。
- M001—M011 逐项具名 Red→Green→Refactor；定向 15/15，全量 TypeScript 66/66、Python 60/60、typecheck 通过。
- DSH 组合显式重冻为 `80f0fc8e…701e`，仅 contracts artifact 与总指纹变化，composition verify 通过。
- TDD 真理源：`Plans/功能开发/2026-08-17-agent全仓TypeScript重构-US-B2-001.tdd.json`。

US-B2-001 已完成并退出滚动 Scope；用户回复“继续”后，当前唯一 Scope 已切换为 US-B2-002。

### 5.4 US-B2-002 实现落点草案

- 新增纯 TS `packages/agent-definition`，共享版本化 Definition/Prompt、严格 loader、工具 allowlist 与默认角色资产；不依赖任何 Runtime 或工具执行器。
- `llm-json`、`planning`、`roles` 运行语义只迁入隔离的 LangGraph Learning Lab，通过注入 ports 离线验证，不新增 `packages/llm-adapter`、`packages/planning` 或生产 Agent Loop。
- `M012—M025` 的 migration target 对齐已采纳需求矩阵，并增加精确路径门禁；源测试、可观察语义和 migrate disposition 不变。
- 新 workspace package 会使根 lock 漂移；实现阶段须显式重冻并验证 production DSH 组合，其余生产 artifact 与 Provider 不得变化。
- 机器真理源：`Plans/功能开发/2026-08-17-agent全仓TypeScript重构-US-B2-002.impl.json`，用户回复“继续”后 `confirmed=true`。

### 5.5 US-B2-002 实现证据

- 代码提交：`5bcce5a76c30aa3304405c02cbb40558b60157bb`。
- 共享 `@agent/agent-definition` 提供版本化 Definition JSON/Prompt、严格字段与 semver 校验、工具 allowlist 和四个独立默认角色；零 DSH/Cordis/LangGraph/模型 SDK依赖。
- Learning Lab 通过注入 ports 实现外层 fence 解包、一次 JSON 修复、计划步骤入图前校验、能力不扩张与角色 definition 透传，不进入生产 launcher/Profile/Bundle。
- M012—M025 的 targetRed 已对齐已采纳矩阵；源测试、语义与 disposition 不变。定向 17/17、全量 TypeScript 82/82、Python 60/60、typecheck 和冻结安装通过。
- DSH 组合显式重冻为 `d1c52876…3083f`；仅 root lock SHA 与总指纹变化，DSH/Cordis/Profile/Provider/production artifacts/finalConfig 不变；真实 headless `--help` 通过。
- TDD 真理源：`Plans/功能开发/2026-08-17-agent全仓TypeScript重构-US-B2-002.tdd.json`。

US-B2-002 已完成并退出滚动 Scope；用户回复“继续”后，当前唯一 Scope 已切换为 US-B2-003。

### 5.6 US-B2-003 实现落点草案

- 现有 `graph.ts` 从 normalize/input 演示图升级为注入 ports 的真实单 Agent StateGraph；复用已完成的 Planning/Action/Definition，Runtime 不直接调用模型 SDK。
- `resume` 只在保存的 human interrupt 节点消费原始 session/proposal，不重新 advance Action；`recover` 只允许安全 checkpoint 的 `steps` patch，中断态禁止 fork。
- 新增版本化 `learning-run-result.v1` 契约、原子 trace store、checkpoint history/stateHash 和 CLI checkpoints/recover；trace 失败为 warning，checkpoint 失败不降级。
- `M026—M037` migration target 对齐已采纳的 runtime/recovery/persistence 三类测试，并增加精确路径门禁；源测试、语义和 disposition 不变。
- 机器真理源：`Plans/功能开发/2026-08-17-agent全仓TypeScript重构-US-B2-003.impl.json`，用户回复“继续”后已更新为 `confirmed=true`，开始创建 Red。

### 5.7 US-B2-003 实现证据

- 代码提交：`b359c774b6dacddf050463a06634332362986dcc`。
- 共享 `learning-run-result.v1` 契约承载 paused/completed/failed、事件序列、checkpoint、warning 与 recovery lineage；Learning Trace 按 runId 原子持久化，不冒充生产 Ledger。
- 单 Agent Graph 使用真实 StateGraph + SqliteSaver；input/approval/UNKNOWN 从原 checkpoint session/proposal 恢复，human node 重入不会再次 advance 已提交 Action。
- replay 从选定历史 checkpoint 建立 native branch head；fork 只允许非空 `steps`，任何 human-interrupt checkpoint 和保护字段 patch 均失败关闭。
- M026—M037 targetRed 对齐 runtime/recovery/persistence 真源；定向 `15/15`、全仓 TypeScript `94/94`、Python `60/60`、typecheck、冻结安装和真实双 Runtime smoke 通过。
- DSH 组合显式重冻为 `f699e623…45b39`；仅 contracts artifact 与总指纹变化，DSH rc.6、Cordis 4.0.1、Profile/Provider/finalConfig 不变。
- TDD 真理源：`Plans/功能开发/2026-08-17-agent全仓TypeScript重构-US-B2-003.tdd.json`。

US-B2-003 已完成并退出滚动 Scope；用户回复“继续”后，当前唯一 Scope 已切换为 US-B2-004。

### 5.8 US-B2-004 实现落点草案

- 新增与单 Agent 并列的 Team StateGraph，risk adjustment、review rejection、retry exhaustion 和 human interrupt 均由显式条件边表达。
- 复用四角色 Definition 与 Learning Action session；`prepare_action` 负责推进并 checkpoint，`interrupt_for_human` 只恢复精确 proposal，防止 Action 重放。
- 每个节点追加结构化 TeamVisit，RunEvent 必须保留发生节点对应的 handoff/action payload；继续复用 `learning-run-result.v1` 与 LearningTraceStore，不新增共享持久契约。
- `M038—M043` 统一落在已采纳的 `labs/runtimes/langgraph-ts/test/team-runtime.spec.ts`；同步修正 migration map 漂移。Team CLI 属于 US-B2-005，本 Story 不修改 `cli.ts`。
- 机器真理源：`Plans/功能开发/2026-08-17-agent全仓TypeScript重构-US-B2-004.impl.json`；用户回复“继续”后已更新为 `confirmed=true`，进入 Red。

### 5.9 US-B2-004 实现证据

- 代码提交：`4931d3285256388c5cfb0ec73ac087db86a7a851`。
- Team Runtime 使用真实 StateGraph + SqliteSaver；UNKNOWN/approval 从原 checkpoint session/proposal 恢复，`startAction` 不重启。
- risk adjustment、review rejection、retry exhaustion 与 human interrupt 均有显式 graph edge；TeamVisit 把逐节点 handoff/action payload 投影到 RunEvent。
- `maxRetries=0` 首次 rejection 直接保留 partial outcome，不进入 `revise_plan`；trace 写失败只追加 warning。
- `M038—M043` targetRed 已统一到 `team-runtime.spec.ts`；定向 Team `6/6`、全仓 TypeScript `100/100`、Python `60/60`、typecheck、冻结安装与真实 DSH smoke 通过。
- 生产组合指纹保持 `f699e623…45b39`；未修改共享 RunResult Schema、单 Agent Runtime 或 CLI，也未引入生产依赖。
- TDD 真理源：`Plans/功能开发/2026-08-17-agent全仓TypeScript重构-US-B2-004.tdd.json`。

US-B2-004 已完成并退出滚动 Scope；用户回复“继续”后，当前唯一 Scope 已切换为 US-B2-005。

### 5.10 US-B2-005 实现落点草案

- 共享 `packages/contracts` 承载纯 TS MCP text content、structuredContent 与 outputSchema 子集校验；`plugins/domain-tools` 只约束未来项目特有工具，不复制生产 DSH 原生 `fs/shell` Provider。
- 旧 `read_file/write_file/list_directory/run_shell/get_current_time` 只迁入隔离 Learning Lab 的 `tools.ts`；成功结果执行后立即校验，显式错误不伪造 structuredContent，shell timeout 表达为 unknown/不可判定。
- 保留现有 raw JSON `run/resume/checkpoints/recover` 协议，新增 `tool` 与交互 `tui`；controller 仅保存 paused RunResult，并用原 `threadId + parentRunId` 恢复 single/team Runtime。
- 旧 curses 机制改为可注入 line/ANSI-fullscreen TS TerminalAdapter；Unicode 不按 code unit 截断，提交日志捕获异常后必须恢复 console/stdout，避免污染机器可读输出。
- `--team` 使用无模型、无凭证的离线 Team ports 实际启动；CLI/TUI 不做 API key 预检，不接 production Profile、Bundle、Provider 或 Safety Executor。
- `M044—M047` 精确落在已采纳的 `tools.spec.ts` 与 `plugins/domain-tools/test/output-contract.spec.ts`；`M048—M060` 全部落在 `cli.spec.ts`，同步修正 migration map 漂移。
- 机器真理源：`Plans/功能开发/2026-08-17-agent全仓TypeScript重构-US-B2-005.impl.json`；用户回复“继续”后已更新为 `confirmed=true`，进入 Red。

### 5.11 US-B2-005 实现证据

- 代码提交：`61b2fed7b1f0e848bc44ce2d9b55c381f0bdf591`。
- 纯 contracts 提供 MCP text content、successful/error result 与失败关闭的 outputSchema 子集 validator；domain-tools 只依赖 contracts，未实现通用 `fs/shell/time`。
- 五个通用工具只存在于 Learning Lab；成功结果带 schema-valid structuredContent，显式错误不伪造 structuredContent，shell timeout 抛 ActionExecutionUnknown。
- raw JSON CLI 保持兼容；新增 `tool`、single/team `tui`、line/ANSI-fullscreen adapter、interrupt-aware decision 与同 `threadId + parentRunId` 恢复。
- `M044—M060` targetRed 对齐已采纳矩阵；目标语义 `18/18`、全仓 TypeScript `120/120`、Python `60/60`、typecheck、冻结安装和真实双 Runtime smoke 通过。
- 生产组合显式重冻为 `2467ba28…bbdd3`；仅 root lock、contracts artifact 与总指纹变化，DSH/Cordis/Profile/Provider/finalConfig 不变。
- TDD 真理源：`Plans/功能开发/2026-08-17-agent全仓TypeScript重构-US-B2-005.tdd.json`。

US-B2-005 已完成并退出滚动 Scope；用户回复“继续”后，当前唯一 Scope 已切换为 US-B3-001。

### 5.12 US-B3-001 实现落点草案

- 纯 contracts 新增 `control-fact.v1` 与 `dsh-runtime-projection.v1`；DSH rc.6 原生事件只由 `dsh-bridge` 归一化，control-ledger 不复制 Session Log。
- `session/event` 只进入 pending buffer，`session/flush` 才通过 SQLite WAL/FULL 批量事务形成 durable boundary；Provider Port 隔离具体 SQLite 实现。
- `(runId, sequence)` 由事务稳定分配；相同幂等键只有 canonical 内容相同才重放成功，冲突不覆盖、不消耗序号。
- Projection 是事实前缀纯函数并用 canonical SHA-256 生成 stateHash；缓存可重建，事实库损坏失败关闭。
- Red 覆盖 SQLite、projection、DSH observer 和 Cordis→flush→重开→replay 的纵向闭环；当前不提前实现 B3-002/Safety Executor。
- 机器真理源：`Plans/功能开发/2026-08-17-agent全仓TypeScript重构-US-B3-001.impl.json`；用户已确认，`confirmed=true`。

### 5.13 US-B3-001 实现证据

- 代码提交：`f52d855aa4e6a2ce962bf936c6fc26ffd5ffab46`。
- 纯 contracts 定义 `control-fact.v1` 与 `dsh-runtime-projection.v1`；`dsh-bridge` 归一化真实 rc.6 session/agent typed events。
- `session/event` 只缓冲，awaited `session/flush` 才提交 WAL/FULL 事务；重开 SQLite 后事实序号与投影 hash 稳定。
- canonical 幂等内容相同返回旧事实，不同内容冲突；投影缓存可重建，事实 canonical 或数据库损坏失败关闭。
- 目标 `10/10`、全仓 TypeScript `130/130`、Python `60/60`、typecheck、冻结安装、composition verify 与生产 DSH smoke 通过。
- 组合指纹：`c6fc9778847046bdec236342030b9d68c62aa4dd408819ed262a9f806e3eea20`。
- TDD 真理源：`Plans/功能开发/2026-08-17-agent全仓TypeScript重构-US-B3-001.tdd.json`。

### 5.14 US-B3-002 实现落点草案

- `packages/contracts` 冻结 command/receipt v1；`packages/control-domain` 只实现五段单调 waterfall 与完成判定，均不得依赖 Cordis、DSH、SQLite 或环境变量。
- `packages/dsh-bridge` 封装 rc.6 的 `agent/pre-step`、`Agent.cancel()/whenIdle()` 和 agent-scoped `tools.restrict()`；pause/stop 使用可撤销 barrier，restrict 不冒充安全权限边界。
- 新增 `plugins/control-supervisor`，将每段 receipt 通过现有 Control Ledger 的窄 `appendFacts` 端口单独 durable commit；使用私有 continuation proof 识别 waterfall 短路。
- 相同 canonical command 幂等返回旧链；同 ID 异内容冲突；部分链、stale basis、live agent 缺失、接纳点不匹配或 verify unknown 均不得补写 `effect_verified`。
- ledger + supervisor 显式进入 controlled Bundle/Profile；`AGENT_CONTROL_LEDGER_PATH` 缺失时失败关闭，不写仓库或隐式临时目录。
- Red 覆盖契约、纯领域、真实 DSH adapter shape、Supervisor 反例及 Cordis→SQLite 重开纵向闭环；当前不实现 B4 Safety Executor、Watchdog、HTTP 或现实写。
- 机器真理源：`Plans/功能开发/2026-08-17-agent全仓TypeScript重构-US-B3-002.impl.json`；用户已回复“继续”确认，当前 `confirmed=true`，进入 Red。

### 5.15 US-B3-002 实现证据

- 代码提交：`27d1021cd6fac88358e5e50c72f49d7cdb40d113`。
- 版本化 command/receipt 契约和纯 waterfall 领域包不依赖框架；重放 receipt 再次做运行时闭集校验，未知状态不能混成成功。
- pause/stop 使用 rc.6 pre-step barrier + cancel/whenIdle；restrict 只核验 agent-scoped 工具可见面，未引入 Safety Executor、Watchdog、HTTP、凭证或现实写。
- Supervisor 逐段 durable append，并用私有 continuation proof 检测真实 Cordis waterfall 短路；幂等冲突、stale basis、部分链和 effect unknown 均失败关闭。
- ledger + supervisor 已进入 controlled Bundle/Profile，数据库路径显式注入；组合指纹重冻为 `a3a376cb…e4a6e18`。
- 目标 `33/33`、全仓 TypeScript `152/152`、Python `60/60`、typecheck、双 frozen install、官方 registry audit、composition verify 与受控 DSH smoke 全部通过。
- TDD 真理源：`Plans/功能开发/2026-08-17-agent全仓TypeScript重构-US-B3-002.tdd.json`。

## 反馈（skill_run）

```yaml
skill_run:
  skill: resume-assistant
  workflow_stage: implementation-design
  plan: Plans/功能开发/2026-08-17-agent全仓TypeScript重构.md
  date: 2026-08-18
  contexts_used:
    - path: Plans/Epic/2026-08-17-agent全仓TypeScript重构.md
      utility: high
      reason: "回放 client-dev 门禁，确认仍处于逐 Story 开发而非集成测试"
    - path: Plans/功能开发/2026-08-17-agent全仓TypeScript重构.stories.json
      utility: high
      reason: "确认下一条依赖满足的 Story 为 US-B3-001，并将其设为唯一滚动 Scope"
    - path: Contexts/决策/Skill反馈协议.md
      utility: high
      reason: "约束续做任务的反馈字段与写入位置"
  contexts_missing: []
  contexts_stale: []
  outcome_status: pass
  revisit_needed: false
```

```yaml
skill_run:
  skill: feature-dev-assistant
  workflow_stage: story-development
  plan: Plans/功能开发/2026-08-17-agent全仓TypeScript重构.md
  date: 2026-08-18
  contexts_used:
    - path: Plans/功能开发/2026-08-17-agent全仓TypeScript重构-US-B3-001.tdd.json
      utility: high
      reason: "汇总 SQLite 控制账本的真实 Red、Green、Refactor、integration smoke 与四项 AC"
    - path: /Users/wanglongxiang/git/agent/plugins/control-ledger/src/sqlite-provider.ts
      utility: high
      reason: "实现 append-only、连续序号、canonical 幂等、WAL/FULL durability 与损坏失败关闭"
    - path: /Users/wanglongxiang/git/agent/packages/dsh-bridge/src/control-observer.ts
      utility: high
      reason: "使用 rc.6 typed session/agent 信号，并以 awaited session/flush 作为唯一 durable ack"
    - path: /Users/wanglongxiang/git/agent/plugins/control-ledger/src/projection.ts
      utility: high
      reason: "从不可变事实前缀确定性重放 DSH 动态镜像与 stateHash"
  contexts_missing: []
  contexts_stale: []
  outcome: "US-B3-001 已完成并提交 f52d855；未自动激活 US-B3-002，也未提前进入最终集成测试"
  utility: high
  reason: "控制事实账本已通过真实 DSH/Cordis/SQLite 纵向 TDD 和全仓回归"
  outcome_status: pass
  friction: "组合身份锁因新增受控 artifact 正常失配；已显式重冻至 c6fc9778…eea20 并验证"
  revisit_needed: false
```

```yaml
skill_run:
  skill: resume-assistant
  workflow_stage: implementation-design
  plan: Plans/功能开发/2026-08-17-agent全仓TypeScript重构.md
  date: 2026-08-18
  contexts_used:
    - path: Plans/Epic/2026-08-17-agent全仓TypeScript重构.md
      utility: high
      reason: "回放 Epic 阶段，确认仍在逐 Story TDD 而非最终集成测试"
    - path: Plans/功能开发/2026-08-17-agent全仓TypeScript重构-US-B3-001.md
      utility: high
      reason: "确认前一 Story 已完成并有真实提交/TDD 证据，可以退出滚动 Scope"
    - path: Plans/功能开发/2026-08-17-agent全仓TypeScript重构-US-B3-002.md
      utility: high
      reason: "恢复到依赖已满足的下一条 P0 Story，并停在 implementation-design"
  contexts_missing: []
  contexts_stale: []
  outcome: "从已完成 US-B3-001 恢复到 US-B3-002 implementation-design，没有跳转集成测试"
  utility: high
  reason: "恢复点由前置完成证据、依赖顺序和用户继续指令共同确定"
  outcome_status: pass
  revisit_needed: false
```

```yaml
skill_run:
  skill: task-splitter
  workflow_stage: story-split
  plan: Plans/功能开发/2026-08-17-agent全仓TypeScript重构.md
  date: 2026-08-18
  contexts_used:
    - path: Plans/功能开发/2026-08-17-agent全仓TypeScript重构-US-B3-001.md
      utility: high
      reason: "已完成 Story 退出当前 implementation Scope"
    - path: Plans/功能开发/2026-08-17-agent全仓TypeScript重构-US-B3-002.md
      utility: high
      reason: "保持 GWT-019 的 8 点纵向边界并设为唯一滚动 Scope"
    - path: Plans/需求分析/2026-08-17-agent全仓TypeScript重构.md
      utility: high
      reason: "保持已确认的 B3 控制回执验收边界，不扩张 B4/B5"
  contexts_missing: []
  contexts_stale: []
  outcome: "只激活 US-B3-002；其余 4 个未完成 Story 保持未激活"
  utility: high
  reason: "US-B3-002 前置已完成且能独立设计，不触发最终集成阶段"
  outcome_status: pass
  revisit_needed: false
```

```yaml
skill_run:
  skill: implementation-design-assistant
  workflow_stage: implementation-design
  plan: Plans/功能开发/2026-08-17-agent全仓TypeScript重构.md
  date: 2026-08-18
  contexts_used:
    - path: Plans/需求分析/2026-08-17-agent全仓TypeScript重构.md
      utility: high
      reason: "落实 GWT-019 的接纳点、五段回执和 unknown 不得完成"
    - path: Plans/技术方案/2026-08-17-智能体控制系统工程架构-v0.1.md
      utility: high
      reason: "约束纯领域、DSH bridge、Supervisor、Ledger Provider 与 B4 Safety 的依赖方向"
    - path: Plans/功能开发/2026-08-17-agent全仓TypeScript重构-US-B3-002.md
      utility: high
      reason: "固化当前唯一 Story 的文件落点、Red、风险与停止条件"
    - path: Contexts/决策/Skill反馈协议.md
      utility: high
      reason: "按有 Plan 任务协议记录待确认的实现门禁"
  contexts_missing:
    - "用户对 US-B3-002 文件落点、依赖方向、Red 与停止条件的确认"
  contexts_stale: []
  outcome: "US-B3-002 落点草案完成并停在 confirmed=false；未创建 Red、业务代码或 B4 Safety Executor"
  utility: high
  reason: "把 pause/restrict/stop 的真实框架 seam、逐段 durability 和失败关闭反例落到可验证文件"
  outcome_status: pass
  revisit_needed: false
```

```yaml
skill_run:
  skill: feature-dev-assistant
  workflow_stage: story-development
  plan: Plans/功能开发/2026-08-17-agent全仓TypeScript重构.md
  date: 2026-08-18
  contexts_used:
    - path: Plans/功能开发/2026-08-17-agent全仓TypeScript重构-US-B3-001.tdd.json
      utility: high
      reason: "汇总 SQLite 控制账本的真实 Red、Green、Refactor、integration smoke 与四项 AC"
    - path: /Users/wanglongxiang/git/agent/plugins/control-ledger/src/sqlite-provider.ts
      utility: high
      reason: "实现 append-only、连续序号、canonical 幂等、WAL/FULL durability 与损坏失败关闭"
    - path: /Users/wanglongxiang/git/agent/packages/dsh-bridge/src/control-observer.ts
      utility: high
      reason: "使用 rc.6 typed session/agent 信号，并以 awaited session/flush 作为唯一 durable ack"
    - path: /Users/wanglongxiang/git/agent/plugins/control-ledger/src/projection.ts
      utility: high
      reason: "从不可变事实前缀确定性重放 DSH 动态镜像与 stateHash"
    - path: Plans/技术方案/2026-08-17-智能体控制系统工程架构-v0.1.md
      utility: high
      reason: "持续约束 ENG-006/008/012、Provider Port 与 facts/projection 真理边界"
  contexts_missing: []
  contexts_stale: []
  outcome: "US-B3-001 已完成并提交 f52d855；未自动激活 US-B3-002，也未提前进入最终集成测试"
  utility: high
  reason: "控制事实账本已通过真实 DSH/Cordis/SQLite 纵向 TDD 和全仓回归"
  outcome_status: pass
  friction: "组合身份锁因新增受控 artifact 正常失配；已显式重冻至 c6fc9778…eea20 并验证"
  revisit_needed: false
```

```yaml
skill_run:
  skill: feature-dev-assistant
  workflow_stage: story-development
  plan: Plans/功能开发/2026-08-17-agent全仓TypeScript重构.md
  date: 2026-08-18
  contexts_used:
    - path: Plans/功能开发/2026-08-17-agent全仓TypeScript重构-US-B3-001.tdd.json
      utility: high
      reason: "汇总 SQLite 控制账本的真实 Red、Green、Refactor、integration smoke 与四项 AC"
    - path: /Users/wanglongxiang/git/agent/plugins/control-ledger/src/sqlite-provider.ts
      utility: high
      reason: "实现 append-only、连续序号、canonical 幂等、WAL/FULL durability 与损坏失败关闭"
    - path: /Users/wanglongxiang/git/agent/packages/dsh-bridge/src/control-observer.ts
      utility: high
      reason: "使用 rc.6 typed session/agent 信号，并以 awaited session/flush 作为唯一 durable ack"
    - path: /Users/wanglongxiang/git/agent/plugins/control-ledger/src/projection.ts
      utility: high
      reason: "从不可变事实前缀确定性重放 DSH 动态镜像与 stateHash"
    - path: Plans/技术方案/2026-08-17-智能体控制系统工程架构-v0.1.md
      utility: high
      reason: "持续约束 ENG-006/008/012、Provider Port 与 facts/projection 真理边界"
  contexts_missing: []
  contexts_stale: []
  outcome: "US-B3-001 已完成并提交 f52d855；未自动激活 US-B3-002，也未提前进入最终集成测试"
  utility: high
  reason: "控制事实账本已通过真实 DSH/Cordis/SQLite 纵向 TDD 和全仓回归"
  outcome_status: pass
  friction: "组合身份锁因新增受控 artifact 正常失配；已显式重冻至 c6fc9778…eea20 并验证"
  revisit_needed: false
```

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

```yaml
skill_run:
  skill: resume-assistant
  workflow_stage: implementation-design
  plan: Plans/功能开发/2026-08-17-agent全仓TypeScript重构.md
  date: 2026-08-17
  contexts_used:
    - path: Plans/Epic/2026-08-17-agent全仓TypeScript重构.md
      utility: high
      reason: "确认前 4 个 Story 已完成，Epic 仍处于逐 Story 开发而非集成测试"
    - path: Plans/功能开发/2026-08-17-agent全仓TypeScript重构.stories.json
      utility: high
      reason: "识别已完成 US-B2-001 仍占滚动 Scope，并确定下一条依赖已满足 Story 为 US-B2-002"
    - path: Plans/功能开发/2026-08-17-agent全仓TypeScript重构-US-B2-001.tdd.json
      utility: high
      reason: "确认 US-B2-001 已有完整 TDD 与提交证据，可以安全退出当前 Scope"
  contexts_missing: []
  contexts_stale: []
  outcome: "从 next-story-scope 断点恢复，确认继续推进 US-B2-002 而非提前进入集成测试"
  utility: high
  reason: "恢复点与 Epic 4/14 的真实完成度一致，并纠正门禁推导与滚动 Scope 元数据不一致"
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
      reason: "将唯一当前 implementation Scope 从已完成 US-B2-001 切换为 US-B2-002"
    - path: Plans/功能开发/2026-08-17-agent全仓TypeScript重构-US-B2-002.md
      utility: high
      reason: "保持 Definition、LLM JSON、Planning、Role 与 M012—M025 的 8 点纵向边界"
    - path: Plans/需求排序/2026-08-17-agent全仓TypeScript重构.md
      utility: high
      reason: "保持已确认的 B0→B1→B2→B3→B4→B5 顺序和依赖"
  contexts_missing: []
  contexts_stale: []
  outcome: "用户回复‘继续’后只激活 US-B2-002；US-B2-001 退出滚动 Scope，其余未完成 Story 未扩张"
  utility: high
  reason: "US-B1-001/002 前置均已完成，单 Story Scope 可独立设计与验收"
```

```yaml
skill_run:
  skill: implementation-design-assistant
  workflow_stage: implementation-design
  plan: Plans/功能开发/2026-08-17-agent全仓TypeScript重构.md
  date: 2026-08-17
  contexts_used:
    - path: Plans/功能开发/2026-08-17-agent全仓TypeScript重构-US-B2-002.impl.json
      utility: high
      reason: "固化共享 agent-definition、Learning-only llm-json/planning/roles、M012—M025 Red 与停止条件"
    - path: /Users/wanglongxiang/git/agent/core/definition.py
      utility: high
      reason: "提取严格 Definition、Prompt context、semver 与工具 allowlist 的旧行为基线"
    - path: /Users/wanglongxiang/git/agent/capabilities/planning.py
      utility: high
      reason: "提取执行能力显式传入、计划步骤校验与风险调整不扩权语义"
    - path: /Users/wanglongxiang/git/agent/migration/legacy-test-map.json
      utility: high
      reason: "发现 M012—M025 的旧 packages/llm-adapter、packages/planning 与已采纳 Learning Lab 矩阵漂移"
    - path: Plans/技术方案/2026-08-17-智能体控制系统工程架构-v0.1.md
      utility: high
      reason: "约束共享 Domain 纯 TS、DSH 唯一生产循环和 LangGraph.js Learning Runtime 隔离"
  contexts_missing:
    - "用户对 US-B2-002 实现落点、依赖方向、Red 与停止条件的确认"
  contexts_stale: []
  outcome: "US-B2-002 落点草案完成并停在 confirmed=false；未创建业务代码或 Red 测试"
  utility: high
  reason: "让两个 Runtime 共享策略资产，同时把 JSON/Planning/Role 行为迁移限定在隔离 Learning Lab"
```

```yaml
skill_run:
  skill: resume-assistant
  workflow_stage: story-development
  plan: Plans/功能开发/2026-08-17-agent全仓TypeScript重构.md
  date: 2026-08-17
  contexts_used:
    - path: Plans/功能开发/2026-08-17-agent全仓TypeScript重构-US-B2-002.impl.json
      utility: high
      reason: "读取用户刚确认的文件落点、依赖边界、Red 与停止条件"
    - path: Plans/功能开发/2026-08-17-agent全仓TypeScript重构-US-B2-002.md
      utility: high
      reason: "确认当前唯一 Scope、8 点 Story 与 M012—M025 验收边界"
    - path: Plans/Epic/2026-08-17-agent全仓TypeScript重构.md
      utility: high
      reason: "保持 Epic 处于逐 Story TDD 且不提前进入集成测试"
  contexts_missing: []
  contexts_stale: []
  outcome: "用户回复‘继续’后确认 US-B2-002 落点门禁，并从 implementation-design 恢复到 Red"
  utility: high
  reason: "开发严格继承已确认 Scope 与双 Runtime 边界，没有扩到 B2-003 或生产第二循环"
```

```yaml
skill_run:
  skill: feature-dev-assistant
  workflow_stage: story-development
  plan: Plans/功能开发/2026-08-17-agent全仓TypeScript重构.md
  date: 2026-08-17
  contexts_used:
    - path: Plans/功能开发/2026-08-17-agent全仓TypeScript重构-US-B2-002.tdd.json
      utility: high
      reason: "汇总真实 Red、Green、Refactor、integration smoke、逐 M012—M025 与提交证据"
    - path: /Users/wanglongxiang/git/agent/packages/agent-definition/src/definition.ts
      utility: high
      reason: "实现共享严格 Definition/Prompt 资产加载、semver 与失败关闭语义"
    - path: /Users/wanglongxiang/git/agent/labs/runtimes/langgraph-ts/src/planning.ts
      utility: high
      reason: "实现 Learning-only 计划步骤校验与执行能力不扩张边界"
    - path: /Users/wanglongxiang/git/agent/profiles/controlled/composition.lock.json
      utility: high
      reason: "证明新增 workspace 包后生产组合仅 root lock SHA 与总指纹按预期重冻"
  contexts_missing: []
  contexts_stale: []
  outcome: "US-B2-002 已完成并提交 5bcce5a；主计划保持逐 Story 开发，等待确认下一 Scope"
  utility: high
  reason: "M012—M025 有真实 Red→Green→Refactor 与全量回归，且共享资产和 Learning 行为没有形成第二生产 Runtime"
```

```yaml
skill_run:
  skill: resume-assistant
  workflow_stage: implementation-design
  plan: Plans/功能开发/2026-08-17-agent全仓TypeScript重构.md
  date: 2026-08-17
  contexts_used:
    - path: Plans/Epic/2026-08-17-agent全仓TypeScript重构.md
      utility: high
      reason: "确认 Epic 仍处于逐 Story TDD，前 5/14 Story 完成且不得提前进入集成测试"
    - path: Plans/功能开发/2026-08-17-agent全仓TypeScript重构.stories.json
      utility: high
      reason: "确认 US-B2-002 已完成、下一依赖就绪 Story 为 US-B2-003"
    - path: Plans/功能开发/2026-08-17-agent全仓TypeScript重构-US-B2-001.tdd.json
      utility: high
      reason: "确认 US-B2-003 的 Runtime 前置已有完整 TDD 证据"
    - path: Plans/功能开发/2026-08-17-agent全仓TypeScript重构-US-B2-002.tdd.json
      utility: high
      reason: "确认 US-B2-003 的 Definition、Planning 与 Role 前置已有完整 TDD 证据"
  contexts_missing: []
  contexts_stale: []
  outcome: "从 US-B2-002 完成态恢复到下一 Story US-B2-003 的实现落点设计，没有跳转集成测试"
  utility: high
  reason: "恢复点由 Story 依赖和 TDD 证据共同决定，避免阶段推进与实际故事完成度脱节"
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
      reason: "把滚动实现 Scope 从已完成 US-B2-002 单独切换到 US-B2-003"
    - path: Plans/功能开发/2026-08-17-agent全仓TypeScript重构-US-B2-003.md
      utility: high
      reason: "保持单 Agent 会话运行、暂停、恢复、回放和 fork 的 8 点纵向边界"
    - path: Plans/需求排序/2026-08-17-agent全仓TypeScript重构.md
      utility: high
      reason: "保持已确认的 B0→B1→B2→B3→B4→B5 顺序和依赖"
  contexts_missing: []
  contexts_stale: []
  outcome: "只激活 US-B2-003；US-B2-002 退出滚动 Scope，其余未完成 Story 未扩张"
  utility: high
  reason: "US-B2-001/002 前置均已完成，US-B2-003 可独立设计并在确认后进入 TDD"
```

```yaml
skill_run:
  skill: implementation-design-assistant
  workflow_stage: implementation-design
  plan: Plans/功能开发/2026-08-17-agent全仓TypeScript重构.md
  date: 2026-08-17
  contexts_used:
    - path: Plans/功能开发/2026-08-17-agent全仓TypeScript重构-US-B2-003.impl.json
      utility: high
      reason: "固化共享 RunResult 契约、Learning Runtime、恢复/fork、Trace 与 M026—M037 Red 落点"
    - path: /Users/wanglongxiang/git/agent/tests/test_runtime.py
      utility: high
      reason: "提取旧 Runtime 的会话、暂停恢复、Trace、错误返回和 fork 行为基线"
    - path: /Users/wanglongxiang/git/agent/labs/runtimes/langgraph-ts/src/runtime.ts
      utility: high
      reason: "识别当前 Learning Runtime 仅有 run/resume/transcript，尚缺历史、恢复、fork 和结构化失败"
    - path: /Users/wanglongxiang/git/agent/migration/legacy-test-map.json
      utility: high
      reason: "发现 M026—M037 的采纳测试路径与现有迁移映射存在漂移并纳入 Red 校正"
    - path: Plans/技术方案/2026-08-17-智能体控制系统工程架构-v0.1.md
      utility: high
      reason: "约束共享契约纯 TS、LangGraph.js 仅作 Learning Runtime 且不得形成第二生产循环"
  contexts_missing:
    - "用户对 US-B2-003 实现落点、依赖方向、Red 与停止条件的确认"
  contexts_stale: []
  outcome: "US-B2-003 落点草案完成并停在 confirmed=false；未创建业务代码或 Red 测试"
  utility: high
  reason: "把单 Agent 运行、恢复、回放、fork 与 Trace 语义落实到可验证文件和测试边界"
```

```yaml
skill_run:
  skill: resume-assistant
  workflow_stage: story-development
  plan: Plans/功能开发/2026-08-17-agent全仓TypeScript重构.md
  date: 2026-08-17
  contexts_used:
    - path: Plans/功能开发/2026-08-17-agent全仓TypeScript重构-US-B2-003.impl.json
      utility: high
      reason: "读取并确认用户已批准的文件落点、依赖边界、M026—M037 Red 与停止条件"
    - path: Plans/功能开发/2026-08-17-agent全仓TypeScript重构-US-B2-003.md
      utility: high
      reason: "确认当前唯一 Scope 为 US-B2-003，前置已满足且仍保持 8 点纵向边界"
    - path: Plans/Epic/2026-08-17-agent全仓TypeScript重构.md
      utility: high
      reason: "保持 Epic 处于逐 Story TDD，不提前进入集成测试或激活后续 Story"
  contexts_missing: []
  contexts_stale: []
  outcome: "用户回复‘继续’后确认 US-B2-003 落点门禁，并从 implementation-design 恢复到 Red"
  utility: high
  reason: "开发将严格继承已确认的单 Agent Learning Runtime、安全恢复和 Trace 边界"
```

```yaml
skill_run:
  skill: feature-dev-assistant
  workflow_stage: story-development
  plan: Plans/功能开发/2026-08-17-agent全仓TypeScript重构.md
  date: 2026-08-17
  contexts_used:
    - path: Plans/功能开发/2026-08-17-agent全仓TypeScript重构-US-B2-003.tdd.json
      utility: high
      reason: "汇总真实 Red、Green、Refactor、integration smoke、逐 M026—M037 与提交证据"
    - path: /Users/wanglongxiang/git/agent/labs/runtimes/langgraph-ts/src/runtime.ts
      utility: high
      reason: "实现结构化 run/resume/history/recover、原生 SQLite checkpoint、事件归一化和 warning 语义"
    - path: /Users/wanglongxiang/git/agent/labs/runtimes/langgraph-ts/src/recovery.ts
      utility: high
      reason: "集中实现 steps-only patch、中断态 fork 禁止和稳定 stateHash"
    - path: /Users/wanglongxiang/git/agent/packages/contracts/src/learning-run.ts
      utility: high
      reason: "提供版本化 Learning RunResult、RunEvent、Checkpoint 与 recovery lineage 共享契约"
    - path: Plans/技术方案/2026-08-17-智能体控制系统工程架构-v0.1.md
      utility: high
      reason: "持续约束 LangGraph.js 只作隔离 Learning Runtime，生产仍唯一委托 DSH/Cordis"
  contexts_missing: []
  contexts_stale: []
  outcome: "US-B2-003 已完成并提交 b359c77；主计划保持逐 Story 开发，等待确认下一滚动 Scope"
  utility: high
  reason: "M026—M037 有真实 Red→Green→Refactor、SQLite 跨实例恢复、安全 fork 与全量回归证据"
  outcome_status: pass
  friction: "LangGraph.js 1.4.10 回放历史 checkpoint 需先以 updateState 建立分支头，再移除 checkpoint_id 从最新分支继续执行"
  revisit_needed: false
```

```yaml
skill_run:
  skill: resume-assistant
  workflow_stage: implementation-design
  plan: Plans/功能开发/2026-08-17-agent全仓TypeScript重构.md
  date: 2026-08-18
  contexts_used:
    - path: Plans/Epic/2026-08-17-agent全仓TypeScript重构.md
      utility: high
      reason: "确认 Epic 仍处于逐 Story TDD，前 6/14 Story 完成且不得提前进入集成测试"
    - path: Plans/功能开发/2026-08-17-agent全仓TypeScript重构.stories.json
      utility: high
      reason: "确认 US-B2-003 已完成且依赖就绪的下一条 Story 为 US-B2-004"
    - path: Plans/功能开发/2026-08-17-agent全仓TypeScript重构-US-B2-003.tdd.json
      utility: high
      reason: "确认 Team Graph 的单 Agent Runtime、Action resume 与 Trace 前置已有完整 TDD/提交证据"
  contexts_missing: []
  contexts_stale: []
  outcome: "从 US-B2-003 完成态恢复到 US-B2-004 implementation-design，没有跳转集成测试"
  utility: high
  reason: "恢复点由 Story 依赖、TDD 证据和用户继续指令共同决定，避免阶段与实际完成度脱节"
```

```yaml
skill_run:
  skill: task-splitter
  workflow_stage: story-split
  plan: Plans/功能开发/2026-08-17-agent全仓TypeScript重构.md
  date: 2026-08-18
  contexts_used:
    - path: Plans/功能开发/2026-08-17-agent全仓TypeScript重构.stories.json
      utility: high
      reason: "把唯一滚动 implementation Scope 从已完成 US-B2-003 切换到 US-B2-004"
    - path: Plans/功能开发/2026-08-17-agent全仓TypeScript重构-US-B2-004.md
      utility: high
      reason: "保持 Team Learning Graph 的 5 点纵向边界和 M038—M043 验收范围"
    - path: Plans/需求排序/2026-08-17-agent全仓TypeScript重构.md
      utility: high
      reason: "保持已确认的 B0→B1→B2→B3→B4→B5 顺序和依赖"
  contexts_missing: []
  contexts_stale: []
  outcome: "只激活 US-B2-004；US-B2-003 退出滚动 Scope，其余 7 条未完成 Story 未扩张"
  utility: high
  reason: "US-B2-003 前置已完成，US-B2-004 可独立设计且不触发最终集成阶段"
```

```yaml
skill_run:
  skill: implementation-design-assistant
  workflow_stage: implementation-design
  plan: Plans/功能开发/2026-08-17-agent全仓TypeScript重构.md
  date: 2026-08-18
  contexts_used:
    - path: Plans/功能开发/2026-08-17-agent全仓TypeScript重构-US-B2-004.impl.json
      utility: high
      reason: "固化 Team Graph 节点/边、角色能力、事件 handoff、精确 resume、retry 与 M038—M043 Red 落点"
    - path: /Users/wanglongxiang/git/agent/tests/test_team_graph_runtime.py
      utility: high
      reason: "提取旧 Team Runtime 六项可观察语义、phase 顺序和 handoff 证据"
    - path: /Users/wanglongxiang/git/agent/orchestration/team_graph.py
      utility: high
      reason: "确认 risk/review 条件边、attempt 上限、Action checkpoint 与 human resolve 的旧行为基线"
    - path: /Users/wanglongxiang/git/agent/labs/runtimes/langgraph-ts/src/roles.ts
      utility: high
      reason: "识别现有四角色 Definition 可复用以及 adjust/revise/resolve 的最小能力缺口"
    - path: Plans/技术方案/2026-08-17-智能体控制系统工程架构-v0.1.md
      utility: high
      reason: "约束 DSH 唯一生产 Runtime、LangGraph.js Team 只留在隔离 Learning Lab"
  contexts_missing:
    - "用户对 US-B2-004 文件落点、依赖方向、Red 与停止条件的确认"
  contexts_stale: []
  outcome: "US-B2-004 落点草案完成并停在 confirmed=false；未创建 Red、业务代码或 Team CLI"
  utility: high
  reason: "把多角色路由、handoff、精确恢复和重试语义落实到可验证文件与测试边界"
```

```yaml
skill_run:
  skill: resume-assistant
  workflow_stage: story-development
  plan: Plans/功能开发/2026-08-17-agent全仓TypeScript重构.md
  date: 2026-08-18
  contexts_used:
    - path: Plans/功能开发/2026-08-17-agent全仓TypeScript重构-US-B2-004.impl.json
      utility: high
      reason: "读取并确认用户已批准的 Team Graph 文件落点、依赖边界、M038—M043 Red 与停止条件"
    - path: Plans/功能开发/2026-08-17-agent全仓TypeScript重构-US-B2-004.md
      utility: high
      reason: "确认当前唯一 Scope 为 US-B2-004，前置已满足且仍保持 5 点纵向边界"
    - path: Plans/Epic/2026-08-17-agent全仓TypeScript重构.md
      utility: high
      reason: "保持 Epic 处于逐 Story TDD，不提前进入集成测试或激活 US-B2-005"
  contexts_missing: []
  contexts_stale: []
  outcome: "用户回复‘继续’后确认 US-B2-004 落点门禁，并从 implementation-design 恢复到 Red"
  utility: high
  reason: "开发将严格继承已确认的 Team 路由、handoff、恢复和 Learning-only 边界"
```

```yaml
skill_run:
  skill: feature-dev-assistant
  workflow_stage: story-development
  plan: Plans/功能开发/2026-08-17-agent全仓TypeScript重构.md
  date: 2026-08-18
  contexts_used:
    - path: Plans/功能开发/2026-08-17-agent全仓TypeScript重构-US-B2-004.tdd.json
      utility: high
      reason: "汇总真实 Red、Green、Refactor、integration smoke、逐 M038—M043 与提交证据"
    - path: /Users/wanglongxiang/git/agent/labs/runtimes/langgraph-ts/src/team-graph.ts
      utility: high
      reason: "实现显式 Team 路由、attempt/retry reducer、逐节点 handoff 和精确 human resume"
    - path: /Users/wanglongxiang/git/agent/labs/runtimes/langgraph-ts/src/team-runtime.ts
      utility: high
      reason: "实现 Team run/resume/history、原生 SQLite checkpoint、RunResult 事件与 trace warning"
    - path: /Users/wanglongxiang/git/agent/labs/runtimes/langgraph-ts/test/team-runtime.spec.ts
      utility: high
      reason: "逐项证明 UNKNOWN、精确 proposal、risk/review edges、handoff、retry limit 与 trace warning"
    - path: Plans/技术方案/2026-08-17-智能体控制系统工程架构-v0.1.md
      utility: high
      reason: "持续约束 LangGraph.js Team 只作隔离 Learning Runtime，生产仍唯一委托 DSH/Cordis"
  contexts_missing: []
  contexts_stale: []
  outcome: "US-B2-004 已完成并提交 4931d32；主计划保持逐 Story 开发，等待确认下一滚动 Scope"
  utility: high
  reason: "M038—M043 有真实 Red→Green→Refactor、精确 Action 恢复、显式图边、持久 handoff 与全量回归证据"
  outcome_status: pass
  friction: "Team 事件不能只从最终 handoffs 数组重建；通过 checkpointed TeamVisit 保留每个节点的 phase 与 payload 关联"
  revisit_needed: false
```

```yaml
skill_run:
  skill: resume-assistant
  workflow_stage: implementation-design
  plan: Plans/功能开发/2026-08-17-agent全仓TypeScript重构.md
  date: 2026-08-18
  contexts_used:
    - path: Plans/功能开发/2026-08-17-agent全仓TypeScript重构-US-B2-004.tdd.json
      utility: high
      reason: "确认 US-B2-004 已完成真实 TDD 并提交 4931d32，不再把已完成 Story 留作当前工作项"
    - path: Plans/功能开发/2026-08-17-agent全仓TypeScript重构.stories.json
      utility: high
      reason: "确认依赖已满足的下一条未完成 Story 是 US-B2-005，后续六条仍不得展开"
    - path: Plans/Epic/2026-08-17-agent全仓TypeScript重构.md
      utility: high
      reason: "确认 Epic 仍处于逐 Story TDD，不应进入最终集成测试"
  contexts_missing: []
  contexts_stale: []
  outcome: "从 US-B2-004 完成态恢复到 US-B2-005 implementation-design，没有跳转集成测试"
  utility: high
  reason: "恢复点由完成证据、依赖和用户继续指令共同确定"
```

```yaml
skill_run:
  skill: task-splitter
  workflow_stage: story-split
  plan: Plans/功能开发/2026-08-17-agent全仓TypeScript重构.md
  date: 2026-08-18
  contexts_used:
    - path: Plans/功能开发/2026-08-17-agent全仓TypeScript重构.stories.json
      utility: high
      reason: "把唯一滚动 implementation Scope 从已完成 US-B2-004 切换到 US-B2-005"
    - path: Plans/功能开发/2026-08-17-agent全仓TypeScript重构-US-B2-005.md
      utility: high
      reason: "保持结构化工具与 CLI 的 8 点纵向边界和 M044—M060 验收范围"
    - path: Plans/需求排序/2026-08-17-agent全仓TypeScript重构.md
      utility: high
      reason: "保持已确认的 B0→B1→B2→B3→B4→B5 顺序和依赖"
  contexts_missing: []
  contexts_stale: []
  outcome: "只激活 US-B2-005；US-B2-004 退出滚动 Scope，其余 6 条未完成 Story 未扩张"
  utility: high
  reason: "US-B2-005 前置已完成且可独立设计，不触发最终集成阶段"
```

```yaml
skill_run:
  skill: implementation-design-assistant
  workflow_stage: implementation-design
  plan: Plans/功能开发/2026-08-17-agent全仓TypeScript重构.md
  date: 2026-08-18
  contexts_used:
    - path: Plans/功能开发/2026-08-17-agent全仓TypeScript重构-US-B2-005.impl.json
      utility: high
      reason: "固化共享 MCP 结果契约、Learning-only 工具、single/team CLI、terminal adapter 与 M044—M060 Red 落点"
    - path: /Users/wanglongxiang/git/agent/tests/test_tool_results.py
      utility: high
      reason: "提取成功/错误 structuredContent、outputSchema 与 shell timeout 四项旧行为基线"
    - path: /Users/wanglongxiang/git/agent/tests/test_tui.py
      utility: high
      reason: "提取格式、decision、Team/fullscreen、Unicode、日志、错误和同 thread 恢复十三项旧行为基线"
    - path: /Users/wanglongxiang/git/agent/labs/runtimes/langgraph-ts/src/cli.ts
      utility: high
      reason: "识别现有 raw JSON 命令的兼容边界和交互 CLI/TUI 缺口"
    - path: Plans/技术方案/2026-08-17-智能体控制系统工程架构-v0.1.md
      utility: high
      reason: "约束通用 fs/shell 留给生产 DSH Provider，迁移实现只进入隔离 Learning Lab"
  contexts_missing:
    - "用户对 US-B2-005 文件落点、依赖方向、Red 与停止条件的确认"
  contexts_stale: []
  outcome: "US-B2-005 落点草案完成并停在 confirmed=false；未创建 Red、业务代码或生产工具 Provider"
  utility: high
  reason: "把工具结果、终端交互和恢复语义落实到可验证文件，同时守住 ENG-010/011 边界"
```

```yaml
skill_run:
  skill: resume-assistant
  workflow_stage: story-development
  plan: Plans/功能开发/2026-08-17-agent全仓TypeScript重构.md
  date: 2026-08-18
  contexts_used:
    - path: Plans/功能开发/2026-08-17-agent全仓TypeScript重构-US-B2-005.impl.json
      utility: high
      reason: "读取并确认用户已批准的工具契约、Learning-only 工具、CLI/TUI 文件落点、Red 与停止条件"
    - path: Plans/功能开发/2026-08-17-agent全仓TypeScript重构-US-B2-005.md
      utility: high
      reason: "确认当前唯一 Scope 为 US-B2-005，前置已满足且仍保持 8 点纵向边界"
    - path: Plans/Epic/2026-08-17-agent全仓TypeScript重构.md
      utility: high
      reason: "保持 Epic 处于逐 Story TDD，不提前进入集成测试或激活 US-B3-001"
  contexts_missing: []
  contexts_stale: []
  outcome: "用户回复‘继续’后确认 US-B2-005 落点门禁，并从 implementation-design 恢复到 Red"
  utility: high
  reason: "开发将严格继承 ENG-010/011、同 thread 恢复和 M044—M060 精确测试边界"
```

```yaml
skill_run:
  skill: feature-dev-assistant
  workflow_stage: story-development
  plan: Plans/功能开发/2026-08-17-agent全仓TypeScript重构.md
  date: 2026-08-18
  contexts_used:
    - path: Plans/功能开发/2026-08-17-agent全仓TypeScript重构-US-B2-005.tdd.json
      utility: high
      reason: "汇总真实 Red、Green、Refactor、integration smoke、逐 M044—M060 与提交证据"
    - path: /Users/wanglongxiang/git/agent/packages/contracts/src/tool-result.ts
      utility: high
      reason: "实现共享 MCP text/structured result 与失败关闭的 outputSchema 子集校验"
    - path: /Users/wanglongxiang/git/agent/labs/runtimes/langgraph-ts/src/tools.ts
      utility: high
      reason: "实现只属于 Learning Lab 的五个结构化本地工具和 shell timeout unknown 语义"
    - path: /Users/wanglongxiang/git/agent/labs/runtimes/langgraph-ts/src/tui.ts
      utility: high
      reason: "实现 single/team controller、同 thread resume、结果渲染和 line/fullscreen terminal adapter"
    - path: Plans/技术方案/2026-08-17-智能体控制系统工程架构-v0.1.md
      utility: high
      reason: "持续约束生产通用工具使用 DSH Provider，Learning CLI 不进入 Profile/Bundle 或持有凭证"
  contexts_missing: []
  contexts_stale: []
  outcome: "US-B2-005 已完成并提交 61b2fed；主计划保持逐 Story 开发，等待确认下一滚动 Scope"
  utility: high
  reason: "M044—M060 有真实工具/终端/跨进程证据，且生产 Runtime 边界与组合身份可复核"
  outcome_status: pass
  friction: "根 Vitest 原先漏扫 plugins/**/*.spec.ts；已纳入测试发现，防止 domain-tools Red 静默跳过"
  revisit_needed: false
```

```yaml
skill_run:
  skill: resume-assistant
  workflow_stage: implementation-design
  plan: Plans/功能开发/2026-08-17-agent全仓TypeScript重构.md
  date: 2026-08-18
  contexts_used:
    - path: Plans/Epic/2026-08-17-agent全仓TypeScript重构.md
      utility: high
      reason: "回放 client-dev 门禁，确认仍处于逐 Story 开发而非集成测试"
    - path: Plans/功能开发/2026-08-17-agent全仓TypeScript重构.stories.json
      utility: high
      reason: "确认下一条依赖满足的 Story 为 US-B3-001，并将其设为唯一滚动 Scope"
    - path: Contexts/决策/Skill反馈协议.md
      utility: high
      reason: "约束续做任务的反馈字段与写入位置"
  contexts_missing: []
  contexts_stale: []
  outcome_status: pass
  revisit_needed: false
```

```yaml
skill_run:
  skill: feature-dev-assistant
  workflow_stage: story-development
  plan: Plans/功能开发/2026-08-17-agent全仓TypeScript重构.md
  date: 2026-08-18
  contexts_used:
    - path: Plans/功能开发/2026-08-17-agent全仓TypeScript重构-US-B3-001.tdd.json
      utility: high
      reason: "汇总 SQLite 控制账本的真实 Red、Green、Refactor、integration smoke 与四项 AC"
    - path: /Users/wanglongxiang/git/agent/plugins/control-ledger/src/sqlite-provider.ts
      utility: high
      reason: "实现 append-only、连续序号、canonical 幂等、WAL/FULL durability 与损坏失败关闭"
    - path: /Users/wanglongxiang/git/agent/packages/dsh-bridge/src/control-observer.ts
      utility: high
      reason: "使用 rc.6 typed session/agent 信号，并以 awaited session/flush 作为唯一 durable ack"
    - path: /Users/wanglongxiang/git/agent/plugins/control-ledger/src/projection.ts
      utility: high
      reason: "从不可变事实前缀确定性重放 DSH 动态镜像与 stateHash"
  contexts_missing: []
  contexts_stale: []
  outcome: "US-B3-001 已完成并提交 f52d855；未自动激活 US-B3-002，也未提前进入最终集成测试"
  utility: high
  reason: "控制事实账本已通过真实 DSH/Cordis/SQLite 纵向 TDD 和全仓回归"
  outcome_status: pass
  friction: "组合身份锁因新增受控 artifact 正常失配；已显式重冻至 c6fc9778…eea20 并验证"
  revisit_needed: false
```

```yaml
skill_run:
  skill: implementation-design-assistant
  workflow_stage: implementation-design
  plan: Plans/功能开发/2026-08-17-agent全仓TypeScript重构.md
  date: 2026-08-18
  contexts_used:
    - path: Plans/需求分析/2026-08-17-agent全仓TypeScript重构.md
      utility: high
      reason: "落实 GWT-019 的接纳点、五段回执和 unknown 不得完成"
    - path: Plans/技术方案/2026-08-17-智能体控制系统工程架构-v0.1.md
      utility: high
      reason: "约束纯领域、DSH bridge、Supervisor、Ledger Provider 与 B4 Safety 的依赖方向"
    - path: Plans/功能开发/2026-08-17-agent全仓TypeScript重构-US-B3-002.md
      utility: high
      reason: "固化当前唯一 Story 的文件落点、Red、风险与停止条件"
    - path: Contexts/决策/Skill反馈协议.md
      utility: high
      reason: "按有 Plan 任务协议记录待确认的实现门禁"
  contexts_missing:
    - "用户对 US-B3-002 文件落点、依赖方向、Red 与停止条件的确认"
  contexts_stale: []
  outcome: "US-B3-002 落点草案完成并停在 confirmed=false；未创建 Red、业务代码或 B4 Safety Executor"
  utility: high
  reason: "把 pause/restrict/stop 的真实框架 seam、逐段 durability 和失败关闭反例落到可验证文件"
  outcome_status: pass
  revisit_needed: false
```

```yaml
skill_run:
  skill: feature-dev-assistant
  workflow_stage: story-development
  plan: Plans/功能开发/2026-08-17-agent全仓TypeScript重构.md
  date: 2026-08-18
  contexts_used:
    - path: Plans/需求分析/2026-08-17-agent全仓TypeScript重构.md
      utility: high
      reason: "逐项验收 GWT-019 的唯一命令、预期接纳点、五段回执和效果核验"
    - path: Plans/技术方案/2026-08-17-智能体控制系统工程架构-v0.1.md
      utility: high
      reason: "持续约束 ENG-006/008/012、typed Cordis event、Provider Port 与 B4 Safety 隔离"
    - path: Plans/功能开发/2026-08-17-agent全仓TypeScript重构-US-B3-001.md
      utility: high
      reason: "复用已完成的 append-only Control Ledger、WAL/FULL durability 与重放边界"
    - path: Plans/功能开发/2026-08-17-agent全仓TypeScript重构-US-B3-002.md
      utility: high
      reason: "汇总真实 Red、Green、Refactor、纵向 smoke、提交和完成证据"
  contexts_missing: []
  contexts_stale: []
  outcome: "US-B3-002 已完成并提交 27d1021；未自动激活 B4，也未进入最终集成测试"
  utility: high
  reason: "三类控制命令的五段 durable receipt、短路证明与 unknown 失败关闭均有可执行证据"
  outcome_status: pass
  friction: "默认 npmmirror registry 不提供 audit endpoint；改用官方 npm registry 后确认无已知漏洞"
  revisit_needed: false
```
