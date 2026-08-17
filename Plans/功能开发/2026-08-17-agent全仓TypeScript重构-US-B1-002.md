---
tags: [功能开发, B1, LangGraph, Learning-Runtime]
type: plan
category: 功能开发
status: 已完成
date: 2026-08-17
lifecycle_state: story-development
parent: Plans/功能开发/2026-08-17-agent全仓TypeScript重构.md
requirement_plan: Plans/需求分析/2026-08-17-agent全仓TypeScript重构.md
architecture_plan: Plans/技术方案/2026-08-17-智能体控制系统工程架构-v0.1.md
story_id: US-B1-002
story_points: 8
sprint_scope: false
tdd_evidence: Plans/功能开发/2026-08-17-agent全仓TypeScript重构-US-B1-002.tdd.json
implementation_design: Plans/功能开发/2026-08-17-agent全仓TypeScript重构-US-B1-002.impl.json
---
# US-B1-002：独立运行和恢复 LangGraph.js Learning Runtime

需求真理源：`Plans/需求分析/2026-08-17-agent全仓TypeScript重构.md`。已采纳架构：`Plans/技术方案/2026-08-17-智能体控制系统工程架构-v0.1.md`。

作为学习者，我想从独立 CLI 运行并恢复 LangGraph.js StateGraph，同时生产 launcher 拒绝 learning manifest，以便保留学习价值而不形成第二生产 Runtime。

覆盖 `GWT-013—014`、ENG-001/002/011。必须包含依赖图、部署图与凭证隔离反例。

## 当前 Scope

- 用户在 US-B1-001 完成且明确提示下一步激活本 Story 后回复“jixu”，因此本轮只激活 `US-B1-002`。
- `US-B0-001` 前置条件已完成；本 Story 不依赖 US-B1-001，但必须复用其稳定 `RuntimeRole` 契约，不能导入 production DSH bridge、Cordis 插件、controlled Profile 或生产凭证。
- 下一阶段仅做实现落点设计和 Red 测试规划；未经确认不开始 Green，也不激活 US-B2 系列。

## 实现落点设计草案

机器真理源：`Plans/功能开发/2026-08-17-agent全仓TypeScript重构-US-B1-002.impl.json`。用户在四项门禁摘要后回复“继续”，当前 `confirmed=true`，允许进入 Red。

### 目标运行链

```text
start:langgraph
  → Lab launcher（环境 allowlist，剥离 HOME/DSH_HOME/密钥/NODE_OPTIONS）
    → Learning CLI run/resume
      → LearningRuntime
        → LangGraph.js StateGraph + interrupt/Command
        → 官方 SqliteSaver + offline JSONL transcript

start:dsh
  → dsh-bridge manifest role gate
    → composition verify
      → official DSH controlled Profile
```

Learning transcript 只记录离线学习事实，不伪造 DSH Session Log，也不写生产 Control Ledger。

### 关键落点

- 在 `labs/runtimes/langgraph-ts/` 内新增 `runtime.ts`、`transcript.ts`、`cli.ts`、`launcher.ts` 和不可部署的 learning manifest；
- 使用精确 `@langchain/langgraph-checkpoint-sqlite@1.0.3`，关闭首个 runtime 后由新实例/新进程恢复同一 thread；
- `packages/dsh-bridge/src/launcher.ts` 在读取组合、凭证或调用 runner 前先做 `assertProductionRuntime`；
- 扩展依赖扫描到 production packages、plugins、bundles、profiles 和 controlled launcher；
- 使用假生产密钥做子进程观测，不能只凭源码中“没写密钥名”宣称隔离；
- 根 lock 与 dsh-bridge 变化后必须显式重冻并复验 DSH 组合，不能让 verify 自动治愈漂移。

### Red 顺序

1. `runtime-resume.spec.ts`：当前无 SQLite checkpointer/interrupt/resume/transcript，必须 Red；
2. `cli.spec.ts`：当前 CLI 无 run/resume 协议，不能由第二个进程恢复，必须 Red；
3. `learning-runtime-isolation.spec.ts`：当前生产 launcher 未接收/拒绝 learning manifest，部署扫描不完整，必须 Red；
4. `learning-credential-isolation.spec.ts`：当前没有环境 allowlist launcher，无法证明子进程看不到假生产密钥，必须 Red。

### 停止条件

- 只能通过 MemorySaver 同进程模拟恢复；
- Learning 子进程仍继承生产密钥、`HOME`、`DSH_HOME` 或 `NODE_OPTIONS`；
- 生产依赖图、Profile、Bundle 或部署入口 import Lab；
- `better-sqlite3` 需要超出单包 `allowBuilds` 的权限；
- 根 lock 变化带来 DSH/Cordis 漂移，或重冻后真实 DSH smoke 失败；
- 必须实现生产 LangGraph Adapter 或双 Runtime 热切换才能 Green。

## 实现前人工门禁

- [x] 确认使用官方 SQLite checkpointer，必须证明新进程/新实例恢复，不接受内存模拟；
- [x] 确认 Learning launcher 使用环境 allowlist，剥离生产凭证和 HOME/DSH_HOME/NODE_OPTIONS；
- [x] 确认 production launcher 在任何组合/runner 行为前以 `RUNTIME_ROLE_DENIED` 拒绝 learning manifest；
- [x] 确认上述 4 组 Red、单包 `better-sqlite3` build 白名单与 DSH 组合重冻门禁。

## TDD 实现结果

- 代码提交：`27e5a1c2c114a7f7b2f70d26ebdf2c6f568c09c0`。
- Red：4 组目标测试全部先因 runtime/launcher/manifest/role gate 尚不存在而失败。
- Green：4 组目标套件、8 个测试通过；包括关闭首个 Runtime 后由新实例及第二个真实进程恢复 SQLite checkpoint。
- Learning child：Node `22.19.0`；环境 allowlist；假模型密钥、AWS key、生产 token、`HOME/DSH_HOME/NODE_OPTIONS` 均不可见。
- Production gate：learning manifest 在组合读取和 runner 调用前返回 `RUNTIME_ROLE_DENIED`。
- 依赖/部署：production packages/plugins/bundles/Profile/entry 对 Lab 零依赖；Lab 对 DSH/Cordis/Profile 零依赖，manifest 明示 offline、credentials=none、deployable=false。
- 供应链：首次官方审计发现 `ini@1.3.0` high；固定覆盖到 `1.3.8` 后审计为无已知漏洞。
- DSH 组合显式重冻并验证，最终指纹：`e59e8be7e3e5b54458aa426292b5452217aef2ac49ce18e520f3009d2bceb31a`。
- 全量回归：TypeScript `19 files / 52 tests`、Python 基线 `60/60`、typecheck、双 frozen install、DSH/Learning smoke 全部通过。

### AC 验收

- [x] GWT-013：Learning CLI 使用原生 StateGraph + interrupt/Command + 官方 SqliteSaver，跨进程恢复同一 thread，并记录 checkpoint lineage 与离线 transcript。
- [x] GWT-014：production launcher 前置拒绝 Learning manifest，生产依赖/部署不引用 Lab，Learning 子进程不持生产凭证。

机器证据：`Plans/功能开发/2026-08-17-agent全仓TypeScript重构-US-B1-002.tdd.json`。

续做：`/resume plan=Plans/功能开发/2026-08-17-agent全仓TypeScript重构.md 进度=next-story-scope`

## 反馈（skill_run）

```yaml
skill_run:
  skill: implementation-design-assistant
  workflow_stage: implementation-design
  plan: Plans/功能开发/2026-08-17-agent全仓TypeScript重构-US-B1-002.md
  date: 2026-08-17
  contexts_used:
    - path: Plans/需求分析/2026-08-17-agent全仓TypeScript重构.md
      utility: high
      reason: "把 GWT-013/014 的真实 checkpoint 恢复、offline transcript、角色拒绝与隔离反例转为文件级 Red"
    - path: Plans/技术方案/2026-08-17-智能体控制系统工程架构-v0.1.md
      utility: high
      reason: "维持 DSH 唯一生产、Learning Lab 无部署/凭证/反向依赖的 ENG-001/002/011 边界"
    - path: /Users/wanglongxiang/git/agent/labs/runtimes/langgraph-ts/src/graph.ts
      utility: high
      reason: "确认当前只有一次性 normalize StateGraph，不具备可持久恢复的 Story 能力"
    - path: /Users/wanglongxiang/git/agent/packages/dsh-bridge/src/launcher.ts
      utility: high
      reason: "定位 RUNTIME_ROLE_DENIED 必须先于组合读取和 runner 调用的生产门禁"
    - path: /Users/wanglongxiang/git/agent/tests/test_runtime.py
      utility: high
      reason: "提取新 runtime 实例恢复同 thread/不同 run/checkpoint 的旧行为证据，但不提前承诺全部 B2 parity"
  contexts_missing:
    - "用户对 SQLite 持久恢复、环境 allowlist、production role gate、4 组 Red 和原生构建白名单的确认"
  contexts_stale: []
  outcome: "完成 US-B1-002 文件级实现落点草案；confirmed=false，停在写代码前人工门禁"
  utility: high
  reason: "用跨进程恢复和假密钥观测替代概念性隔离，避免为完成 Story 强行把内存模拟当可靠证据"
```

```yaml
skill_run:
  skill: feature-dev-assistant
  workflow_stage: story-development
  plan: Plans/功能开发/2026-08-17-agent全仓TypeScript重构-US-B1-002.md
  date: 2026-08-17
  contexts_used:
    - path: Plans/功能开发/2026-08-17-agent全仓TypeScript重构-US-B1-002.impl.json
      utility: high
      reason: "约束官方 SQLite 跨进程恢复、环境 allowlist、production role gate、4 组 Red 与停止条件"
    - path: /Users/wanglongxiang/git/agent/labs/runtimes/langgraph-ts/src/runtime.ts
      utility: high
      reason: "实现原生 StateGraph checkpoint、thread/run/checkpoint lineage 和新实例 resume"
    - path: /Users/wanglongxiang/git/agent/labs/runtimes/langgraph-ts/src/launcher.ts
      utility: high
      reason: "证明 Learning 子进程使用环境 allowlist，不继承生产密钥或用户凭证目录"
    - path: /Users/wanglongxiang/git/agent/packages/dsh-bridge/src/launcher.ts
      utility: high
      reason: "证明 learning manifest 在任何组合/runner 行为前被生产入口拒绝"
    - path: /Users/wanglongxiang/git/agent/profiles/controlled/composition.lock.json
      utility: high
      reason: "记录依赖与 dsh-bridge 变化后重新资格化的生产 DSH 组合指纹"
  contexts_missing: []
  contexts_stale: []
  outcome: "US-B1-002 完成真实 Red→Green→Refactor→双 Runtime smoke，提交 27e5a1c；当前 Scope 不自动扩展"
  utility: high
  reason: "Learning Runtime 的学习价值和生产隔离均由跨进程、故障注入、凭证观测和真实 DSH 回归证明"
```
