---
tags: [功能开发, B0, 可信评估]
type: plan
category: 功能开发
status: 已完成
date: 2026-08-17
lifecycle_state: story-development
parent: Plans/功能开发/2026-08-17-agent全仓TypeScript重构.md
requirement_plan: Plans/需求分析/2026-08-17-agent全仓TypeScript重构.md
architecture_plan: Plans/技术方案/2026-08-17-智能体控制系统工程架构-v0.1.md
story_id: US-B0-001
story_points: 8
sprint_scope: false
tdd_evidence: Plans/功能开发/2026-08-17-agent全仓TypeScript重构-US-B0-001.tdd.json
implementation_design: Plans/功能开发/2026-08-17-agent全仓TypeScript重构-US-B0-001.impl.json
---
# US-B0-001：冻结可重放基线并证明评估尺可靠

## 一、需求分析

需求真理源：`Plans/需求分析/2026-08-17-agent全仓TypeScript重构.md`，覆盖 `GWT-001—004`、`GWT-009—012`。

## 二、技术方案

已采纳架构：`Plans/技术方案/2026-08-17-智能体控制系统工程架构-v0.1.md`，遵循 ENG-003/008/009 与 B0 需求影响矩阵。

## 三、用户故事与 AC

作为系统维护者，我想冻结 Python 基线、60 tests、资产与真实任务证据，并用正例、负例、unknown 和坏环境校准评估尺，以便后续迁写建立在可信事实之上。

覆盖 `GWT-001—004`、`GWT-009—012`。故事包含 Baseline Manifest、Migration Matrix、Case 资格、人工签署引用和失败停止；不包含生产 DSH 组合实现。

## 实现落点设计

设计真理源：`Plans/功能开发/2026-08-17-agent全仓TypeScript重构-US-B0-001.impl.json`。

### 已读取代码证据

- 根 `package.json` 已有 TypeScript/Vitest/评估命令，但 Node/TS 版本与已采纳基线存在漂移，B0 只记录事实，不在本 Story 接入 DSH；
- `evaluation-domain/qualify-case.ts` 当前只把一个负对照纳入 `qualified`，而 Case 测试在函数外另行断言禁止副作用和坏环境；实现时必须让资格结果本身绑定全部强制控制证据；
- 当前 HEAD 为 `3d0c7a3fa5aea600d4d0a9b5c5dde012b8e9b5c4`，工作树只有 Case 签署三处未提交变更；冻结工具必须显式区分 baseline commit 与当前工作树；
- Python 仍有 60 tests，TS 当前有 20 tests；B0 生成映射和证据，不伪造 60 个 TS Green。

### 文件落点

| 动作 | 文件 | 目的 |
|---|---|---|
| 修改 | `package.json` | 增加 `baseline:freeze`、`baseline:verify`、`verify:legacy-test-map` 命令 |
| 新建 | `packages/contracts/src/baseline.ts`、`packages/contracts/schemas/baseline-manifest.v1.json` | 定义 baseline SHA、工作树、测试、资产、工具链、证据引用与失败原因契约 |
| 新建 | `scripts/baseline/freeze.ts` | 对显式 commit 采集 Git、pytest、资产 hash、dirty tree 和环境事实；任一必需证据缺失时非零退出 |
| 新建 | `migration/legacy-test-map.json` | 固化 M001—M060 的 node ID、TS 目标、语义和处置，不记录虚假 Green |
| 新建 | `tests/acceptance/baseline-manifest.spec.ts`、`legacy-test-map.spec.ts` | 验证 0/0、脏树、不可解析 SHA、缺日志、缺映射和重复 ID 均阻断 |
| 修改 | `packages/evaluation-domain/src/qualify-case.ts` 及测试 | 资格输入改为多个必需负对照与坏环境控制，任一缺失/结论错误都不能 `qualified=true` |
| 修改 | `evaluation/cases/legacy-agent-definition-v1/src/run.ts`、`case.json` 与测试 | 生成完整证据 bundle digest；review 必须绑定 bundle hash，Schema/fixture 变化使签署失效 |
| 新建 | `docs/runbooks/baseline-freeze.md` | 记录冻结、重放、重新签署和停止条件，不把生成目录冒充证据 |

### 模块与依赖

`scripts/baseline → contracts`，`evaluation case → evaluation-domain + evaluation-oracles → contracts`。`contracts` 不 import Git、pytest、DSH、Cordis 或文件系统；冻结脚本不写业务判定，资格领域层不执行 shell。

### Red 测试顺序

1. `baseline-manifest.spec.ts`：0 个 Python tests、缺 pytest 日志、SHA 不可解析或工作树污染时拒绝冻结；
2. `legacy-test-map.spec.ts`：M001—M060 缺失、重复、waiver 无人工证据时失败；
3. `qualify-case.spec.ts`：第二负对照 PASS、坏环境非 INVALID、证据缺失或 review bundle hash 漂移时不资格化；
4. `legacy Case qualification.spec.ts`：完整证据稳定重放后才允许 `qualified=true`，fixture 变化后必须重新签署。

### 停止条件

- 不能稳定复现 60 个 Python tests；
- 实际 baseline SHA、资产或工作树状态无法追溯；
- 资格函数仍可在任一强制控制失败时返回 true；
- 新 evidence bundle 与当前人工签署不一致且尚未重新确认。

- [x] 用户已确认文件落点与 Red 顺序，`.impl.json confirmed=true`。

## TDD 实现结果

- Red：四组新测试分别因冻结器、迁移账本、多控制资格和 bundle digest 尚不存在而失败；
- Green/Refactor：TypeScript `28/28`、Python `60/60`、全量 typecheck 通过；
- 基线：提交 `3d0c7a3fa5aea600d4d0a9b5c5dde012b8e9b5c4` 已在名为 `agent` 的干净 detached worktree 重放并冻结；
- 实现提交：`02d77b5be47f2837dfe8d06c91dfcbf6da5edb87`；人工签署提交：`e3fae6ba4c34fd9e41a4f148aa2aae72a69ef6ee`；
- 当前 Case bundle：`3ad17826cb0a4175bba96bed82209ad855435d405e6db2de036a9143a066432c`；用户明确批准后重复运行保持同一摘要，资格结果为 `qualified=true`。

### 人工门禁结果

1. [x] 用户确认 `migration/legacy-test-map.json` 中 M001—M060 的可观察语义与目标 Red 落点；机器校验与冻结 manifest 的 60 个 node id 一一对应；
2. [x] 用户批准完整 bundle SHA-256；摘要已绑定到 `review.evidenceBundleSha256`，重放得到参考解 PASS、两项负对照 FAIL、坏环境 INVALID、最终 `qualified=true`。

TDD 证据：`Plans/功能开发/2026-08-17-agent全仓TypeScript重构-US-B0-001.tdd.json`。

续做：`/resume plan=Plans/功能开发/2026-08-17-agent全仓TypeScript重构.md 进度=next-story-scope`

## 反馈（skill_run）

```yaml
skill_run:
  skill: implementation-design-assistant
  workflow_stage: implementation-design
  plan: Plans/功能开发/2026-08-17-agent全仓TypeScript重构-US-B0-001.md
  date: 2026-08-17
  contexts_used:
    - path: Plans/需求分析/2026-08-17-agent全仓TypeScript重构.md
      utility: high
      reason: "把 GWT-001—004、009—012 与 M001—M060 的停止条件转成 Red 文件"
    - path: Plans/技术方案/2026-08-17-智能体控制系统工程架构-v0.1.md
      utility: high
      reason: "保持 contracts 纯净、技术/现实分账、四态评估和人工签署约束"
    - path: /Users/wanglongxiang/git/agent/packages/evaluation-domain/src/qualify-case.ts
      utility: high
      reason: "发现 qualified 当前只消费一个负对照，完整 Case 控制证据尚未成为领域不变量"
    - path: /Users/wanglongxiang/git/agent/evaluation/cases/legacy-agent-definition-v1/src/run.ts
      utility: high
      reason: "确认正例、两个负例和坏环境已执行，但 review 尚未绑定完整 evidence bundle digest"
  contexts_missing: []
  contexts_stale: []
  outcome: "用户确认首个评估 Story 的文件级实现契约；baseline/migration 证据链与完整 Case 控制资格 Red 获准进入开发"
  utility: high
  reason: "先修复评估资格可能只检查单个负对照的可信度缺口，再决定是否允许后续 Runtime 迁写"
```

```yaml
skill_run:
  skill: feature-dev-assistant
  workflow_stage: story-development
  plan: Plans/功能开发/2026-08-17-agent全仓TypeScript重构-US-B0-001.md
  date: 2026-08-17
  contexts_used:
    - path: Plans/功能开发/2026-08-17-agent全仓TypeScript重构-US-B0-001.impl.json
      utility: high
      reason: "按已确认落点完成 baseline contract、冻结器、迁移账本和完整 Case bundle 资格化"
    - path: /Users/wanglongxiang/git/agent/evidence/baselines/3d0c7a3fa5aea600d4d0a9b5c5dde012b8e9b5c4/baseline-manifest.v1.json
      utility: high
      reason: "提供干净 detached worktree 上真实 60/60 Python 基线和资产指纹"
    - path: /Users/wanglongxiang/git/agent/migration/legacy-test-map.json
      utility: high
      reason: "将 M001—M060 与冻结 node id 一一绑定，保留语义与目标 Red 位置"
    - path: /Users/wanglongxiang/git/agent/evaluation/cases/legacy-agent-definition-v1/src/run.ts
      utility: high
      reason: "生成并稳定重放包含全部强制控制的 canonical evidence bundle"
  contexts_missing: []
  contexts_stale: []
  outcome: "用户确认 M001—M060 语义并批准完整 evidence bundle；重放 qualified=true，US-B0-001 完成"
  utility: high
  reason: "首次把 60 项旧基线、多个负对照、坏环境和人工签名绑定成可审计且失败关闭的证据链"
```
