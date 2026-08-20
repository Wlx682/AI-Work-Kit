---
tags: [功能开发, B5, Cutover, 删除]
type: plan
category: 功能开发
status: 已完成
date: 2026-08-17
lifecycle_state: story-development
parent: Plans/功能开发/2026-08-17-agent全仓TypeScript重构.md
requirement_plan: Plans/需求分析/2026-08-17-agent全仓TypeScript重构.md
architecture_plan: Plans/技术方案/2026-08-17-智能体控制系统工程架构-v0.1.md
story_id: US-B5-002
story_points: 5
sprint_scope: true
tdd_evidence: Plans/功能开发/2026-08-17-agent全仓TypeScript重构-US-B5-002.tdd.json
implementation_design: Plans/功能开发/2026-08-17-agent全仓TypeScript重构-US-B5-002.impl.json
---
# US-B5-002：人工批准后一次切换并保留回滚基线

作为发布负责人，我想在所有证据全绿且人工批准后一次删除 Python 并切换 DSH 入口，以便得到纯 TypeScript 工作树且仍能从 baseline 引用审计回滚。

覆盖 cutover 侧 `GWT-021—022`。这是独立破坏性 Story；实现与执行都需要当时的明确人工批准，任何红灯都保持 blocked。

## 当前 Scope

- `US-B5-001` 已完成并提交 `9739aec`，真实 rehearsal 的十个仓库内自动门禁全部 PASS；production deployment boundary 缺少 owner 签署，因此报告按设计保持 blocked。
- 用户已确认双阶段实现方案、仓库内最终生产入口目标 `pnpm start → scripts/runtime/launch-controlled.ts`，并授权为 baseline 创建 annotated tag；这仍不代表批准删除 Python 或执行 destructive cutover。
- 本 Story 必须先设计可验证的双阶段门禁：非破坏性 prepare/verify 与独立的 destructive apply；任何真实部署证据、人工签署或候选绑定不完整都停止在 blocked。

## 实现落点设计草案

- 独立契约：新增 `cutover-plan.v1`、`cutover-authorization.v1`、`cutover-result.v1`，不修改 B5-001 `cutoverAllowed=false` 的 rehearsal 契约。
- 两提交边界：先提交不删除 Python 的 contracts/domain/prepare/verify/manifest/tests/runbook；该提交形成新 candidate/composition 并重新 rehearsal。只有外部 deployment owner 与指定 reviewer 都签署后，才允许第二个单一 cutover commit。
- 非破坏性 prepare：要求 clean candidate、ready rehearsal、deployment evidence，按精确 44-path+before hash 清单用临时 Git index 计算 `expectedTargetTreeSha`，默认零 worktree 写。
- 最终 mutation：一次删除 44 个 Git-tracked `.py`，同一变更把根 `pnpm start` 指向 controlled DSH，并将 README 更新为纯 TS；definitions/prompts、baseline evidence、migration map 和 LangGraph.js Lab 保留。
- 完成判据：最终 committed tree 必须等于批准 tree，`git ls-files '*.py'` 为 0，TS tests/typecheck/composition/frozen install/audit/controlled+recovery smoke 全绿，production graph 无 Lab，baseline ref 仍可达，之后才生成 result。
- 现实缺口：当前无 deploy manifest/remote；本地 annotated tag `python-baseline-v1` 已精确指向 `3d0c7a3`。旧 rehearsal 的 deployment gate blocked 且会因 tooling 改变 composition；最终 deployment evidence 和 reviewer approval 不能由 AI 猜测。

## Red 设计

1. 契约 Red：plan/authorization/result 严格字段、candidate/tree/hash、精确 deletion entries、reviewer 和证据闭集；拒绝未知字段、重复/宽泛路径与 AI approved。
2. 领域 Red：ready rehearsal + deployment + approved authorization + plan/tree 全一致才 authorized；旧 blocked report、pending/rejected、任何漂移均 blocked。
3. Prepare Red：fake Git/File ports 证明默认零写，用临时 index 计算目标 tree；工作树脏、HEAD/hash/path 漂移全部在 mutation 前拒绝。
4. Cutover Red：批准主链路一次形成 0 tracked Python + DSH start + baseline 可达；中断/重复执行/入口或 tree 不匹配不得生成 completed result。
5. 隔离 Red：最终 production dependency/deploy graph 不 import Learning Lab，显式 `start:langgraph` 仍只作为 learning 入口。

## 停止条件

- final ready rehearsal、deployment owner evidence、cutover reviewer approved authorization、plan SHA/target tree 任一缺失或漂移。
- 未确认真实生产入口或 baseline 长期引用策略；需要 AI 代签、修改 pending/rejected 或把裸 SHA 暂时可达冒充受保护 ref。
- 工作树不干净、HEAD 不等于 plan candidate、44 个删除目标任一 hash 不同或出现未登记 Python 文件。
- 需要使用 glob/宽泛递归删除，或删除 definitions/prompts、baseline/migration evidence、TS Learning Lab 等白名单外资产。
- 用户尚未在看到 exact plan hash/tree、44-path 清单、入口变更和 rollback ref 后明确批准 destructive apply。

机器真理源：`Plans/功能开发/2026-08-17-agent全仓TypeScript重构-US-B5-002.impl.json`；用户已确认，当前 `confirmed=true`，进入非破坏性 tooling Red。已创建 baseline annotated tag，但仍未创建授权文件、删除 Python 或切换默认入口。

## Tooling TDD 证据

- 非破坏性 tooling 已提交为 `eedd1be73f7ec6a04a3016e3646af4b3c2f0bb9f`：独立 cutover plan/authorization/result 契约、纯失败关闭判定、固定 44-path manifest、临时 Git index target-tree 计算、prepare/verify CLI 与 runbook。
- Red 为 4 个文件、5 个测试失败（缺契约/判定/prepare）；Green/Refactor 后目标 9/9、全仓 TypeScript 211/211、Python baseline 60/60、typecheck、composition、三处 frozen install、registry audit、controlled/recovery smoke 全通过。
- annotated tag `python-baseline-v1` 精确解析到 `3d0c7a3fa5aea600d4d0a9b5c5dde012b8e9b5c4`；新 composition fingerprint 为 `455f7fe5f282d5cd8022f6c52e85ce3dd4814faaac1bdacab55bd7fd917fc8be`。
- final rehearsal 报告 SHA-256 为 `41e62b2d087ce639541b7002ed4b9541eaa060e9c8f383eeb9eef3e6262947f3`：十个仓库内 gate PASS，`deployment_boundary=blocked(DEPLOYMENT_EVIDENCE_MISSING)`，human review pending，`cutoverAllowed=false`。
- 当前仍有 44 个 tracked `.py`，根 `start` 未设置；tooling CLI 仅支持 `prepare|verify`，刻意没有 destructive apply。

下一步需 production deployment owner 提供绑定 candidate `eedd1be` 与 composition `455f7fe5…` 的 evidence，重跑得到 ready rehearsal 后才能生成 exact plan；随后仍需指定 human reviewer authorization 和用户对 exact plan 的最终破坏性批准。

续做：`/resume plan=Plans/功能开发/2026-08-17-agent全仓TypeScript重构-US-B5-002.md 进度=deployment-evidence`

## 2026-08-20 变更影响：改为本地仓库直接切换

- 用户明确说明“目前还没有部署，全都在本地”，并要求“直接切换”。原 production deployment evidence 前提不适用于当前环境，不能继续把不存在的 OS/IAM/network/certificate 记录当成必填，也不能伪造签署。
- 需求影响：GWT-021 增加 `local_repository` 适用分支；自动门禁、baseline、精确删除清单、target tree、人工批准和切换后验证均不降级。
- 架构影响：新增 ENG-012；本次批准只覆盖本地 Git 工作树，不等于未来 production deploy approval。
- 代码影响：rehearsal/plan/authorization contract 增加显式 boundary decision union；prepare 接受经用户确认的 local decision，仍拒绝缺决定、candidate/composition 漂移或任何自动门禁失败。
- 执行影响：允许删除 manifest 登记的 44 个 `.py`，同一 cutover 设置根 `pnpm start` 并替换 README；保留 `python-baseline-v1`、baseline evidence、migration map、definitions/prompts 与 LangGraph.js Learning Lab。
- 变更状态：用户已确认，进入 Red→Green→单一 destructive cutover；未来若部署必须重新走 production boundary evidence。

## Cutover 完成证据

- 本地 decision tooling 提交：`9eff2b2b50cb5a65c43933223aee6a4ac8f14454`；composition：`e65f84dd26c6f1ce6c067b4eeb453d54173965af4fd79714e264ed54efbad765`。
- Final rehearsal：11/11 gate PASS；报告 SHA-256 `55a1d23e0d65d9bb4db5ba7f9770d7b9cd3254b1cda91c79f42b1b560bf5f6e8`。
- Exact plan：SHA-256 `508f18f4858de8c976c7199ff4272120268d058002d4bd101f549df54e67c40f`；expected target tree `b22e9a8f9913fb9b3faf8357839383b3e7abe389`；verify=`authorized`。
- Cutover commit：`582306a8675cea435ea33e53b8db82086947ff9f`，commit tree 精确等于批准 tree；44 个 tracked Python 已删除，根 `pnpm start` 已指向 controlled DSH，README 已切换纯 TS。
- 切换后 TypeScript 213/213、typecheck、composition、三处 frozen install、registry audit、默认 start 与 recovery smoke 全绿；`python-baseline-v1` 仍精确指向 `3d0c7a3`。
- TDD 真理源：`Plans/功能开发/2026-08-17-agent全仓TypeScript重构-US-B5-002.tdd.json`。本 Story 已完成；保留为最终 Scope marker 供阶段门禁验证，下一阶段不再开发新 Story。

## 反馈（skill_run）

```yaml
skill_run:
  skill: task-splitter
  workflow_stage: story-split
  plan: Plans/功能开发/2026-08-17-agent全仓TypeScript重构-US-B5-002.md
  date: 2026-08-20
  contexts_used:
    - path: Plans/功能开发/2026-08-17-agent全仓TypeScript重构-US-B5-001.tdd.json
      utility: high
      reason: "确认 rehearsal Story 已完成并有提交、十个自动门禁和失败关闭证据，B5-002 前置依赖满足"
    - path: Plans/功能开发/2026-08-17-agent全仓TypeScript重构.stories.json
      utility: high
      reason: "把唯一滚动 Scope 从已完成 B5-001 切换到最后一条 B5-002，其余 Story 不扩张"
    - path: Plans/技术方案/2026-08-17-智能体控制系统工程架构-v0.1.md
      utility: high
      reason: "保持最终删除是独立破坏性门禁，Scope 激活不构成 cutover 批准"
  contexts_missing:
    - "匹配最终候选 SHA/composition 的真实 production deployment boundary owner 签署"
    - "实现设计确认后的独立破坏性 cutover 批准"
  contexts_stale: []
  outcome: "只激活 US-B5-002 进入 implementation-design；未删除 Python、未改生产入口、未执行 cutover"
  utility: high
  reason: "最后一条纵向 Story 已按依赖激活，同时保留证据签署与破坏性执行的人工边界"
  outcome_status: pass
  revisit_needed: false
```

```yaml
skill_run:
  skill: feature-dev-assistant
  workflow_stage: story-development
  plan: Plans/功能开发/2026-08-17-agent全仓TypeScript重构-US-B5-002.md
  date: 2026-08-20
  contexts_used:
    - path: Plans/功能开发/2026-08-17-agent全仓TypeScript重构-US-B5-002.impl.json
      utility: high
      reason: "按用户确认的双阶段边界只实现非破坏性 tooling，并保留最终删除的再次审批门禁"
    - path: Plans/功能开发/2026-08-17-agent全仓TypeScript重构-US-B5-001.tdd.json
      utility: high
      reason: "继承 immutable rehearsal 契约与 cutoverAllowed=false 不变量，并在新 candidate 上重跑完整门禁"
    - path: Plans/需求分析/2026-08-17-agent全仓TypeScript重构.md
      utility: high
      reason: "落实 GWT-021/022 的全绿、指定 reviewer、缺证不改工作树和入口"
  contexts_missing:
    - "绑定 candidate eedd1be 与 composition 455f7fe5 的 production deployment owner evidence"
    - "ready rehearsal 后的指定 human reviewer authorization 与 exact plan destructive apply 批准"
  contexts_stale: []
  outcome: "非破坏性 cutover tooling 已通过 TDD 并提交；final rehearsal 十个内部 gate PASS，deployment boundary 缺证而正确 blocked，未删除 Python 或切入口"
  utility: high
  reason: "把破坏性切换前的计划、证据绑定、人工授权和失败关闭变成可执行机械门禁"
  outcome_status: pass
  revisit_needed: true
```

```yaml
skill_run:
  skill: resume-assistant
  workflow_stage: implementation-design
  plan: Plans/功能开发/2026-08-17-agent全仓TypeScript重构-US-B5-002.md
  date: 2026-08-20
  contexts_used:
    - path: Plans/Epic/2026-08-17-agent全仓TypeScript重构.md
      utility: high
      reason: "回放 Epic 仍在逐 Story TDD，最后一条 B5-002 未完成而非已进入最终集成测试"
    - path: Plans/功能开发/2026-08-17-agent全仓TypeScript重构-US-B5-001.tdd.json
      utility: high
      reason: "确认 rehearsal 前置完成，但 deployment boundary 与 human review 仍阻断最终 cutover"
    - path: Plans/功能开发/2026-08-17-agent全仓TypeScript重构.stories.json
      utility: high
      reason: "恢复并只激活最后一条 US-B5-002 为当前滚动 Scope"
  contexts_missing:
    - "最终 production deployment boundary owner 签署"
    - "指定 cutover reviewer authorization 与破坏性执行批准"
  contexts_stale: []
  outcome: "恢复最后一条 Story 并推进到 implementation-design；未进入 Red、未删除 Python、未切生产入口"
  utility: high
  reason: "依据完成证据和 Story 依赖继续，未把用户‘继续’扩大解释为破坏性授权"
  outcome_status: pass
  revisit_needed: false
```

```yaml
skill_run:
  skill: implementation-design-assistant
  workflow_stage: implementation-design
  plan: Plans/功能开发/2026-08-17-agent全仓TypeScript重构-US-B5-002.md
  date: 2026-08-20
  contexts_used:
    - path: Plans/需求分析/2026-08-17-agent全仓TypeScript重构.md
      utility: high
      reason: "落实 GWT-021-CUTOVER 全绿+指定 reviewer 才切换，以及 GWT-022 任一缺证保持不变"
    - path: Plans/技术方案/2026-08-17-智能体控制系统工程架构-v0.1.md
      utility: high
      reason: "落实 ENG-001/002/005/009/011 的纯 TS、DSH 唯一生产、一次 cutover 与 baseline/Learning 边界"
    - path: Plans/功能开发/2026-08-17-agent全仓TypeScript重构-US-B5-001.tdd.json
      utility: high
      reason: "继承候选、自动门禁、blocked deployment 与零破坏 rehearsal 证据"
    - path: Contexts/决策/Skill反馈协议.md
      utility: high
      reason: "按有 Plan 任务协议记录待确认设计、缺失证据与停止条件"
  contexts_missing:
    - "真实生产入口归属与匹配新 candidate/composition 的 deployment evidence"
    - "baseline durable ref 策略、指定 reviewer approved authorization 和最终 destructive apply 批准"
  contexts_stale: []
  outcome: "US-B5-002 落点草案完成并停在 confirmed=false；精确登记 44 个删除目标，未创建 Red/tooling/授权或执行切换"
  utility: high
  reason: "把最终一次切换拆为可审计 tooling、外部证据、人工授权、精确 mutation 和 committed-tree 验证"
  outcome_status: pass
  revisit_needed: false
```

```yaml
skill_run:
  skill: feature-dev-assistant
  workflow_stage: story-development
  plan: Plans/功能开发/2026-08-17-agent全仓TypeScript重构-US-B5-002.md
  date: 2026-08-20
  contexts_used:
    - path: Plans/功能开发/2026-08-17-agent全仓TypeScript重构-US-B5-002.impl.json
      utility: high
      reason: "按已确认的双阶段边界完成非破坏性 tooling，不越过最终删除审批"
    - path: Plans/功能开发/2026-08-17-agent全仓TypeScript重构-US-B5-001.tdd.json
      utility: high
      reason: "继承 rehearsal 不授权 cutover 的不变量，并在新 candidate 上重跑全部固定 gate"
    - path: Plans/需求分析/2026-08-17-agent全仓TypeScript重构.md
      utility: high
      reason: "落实 GWT-021/022 的外部签署、指定 reviewer 与缺证不写边界"
  contexts_missing:
    - "绑定 candidate eedd1be 与 composition 455f7fe5 的 production deployment owner evidence"
    - "ready rehearsal 后的 human reviewer authorization 与 exact plan destructive apply 批准"
  contexts_stale: []
  outcome: "tooling commit eedd1be 已通过 TDD；final rehearsal 十个内部 gate PASS，deployment boundary 缺证而正确 blocked，44 个 Python 与默认入口均保持不变"
  utility: high
  reason: "cutover 前的精确清单、target tree、证据绑定与人工授权已成为失败关闭的机械门禁"
  outcome_status: pass
  revisit_needed: true
```

```yaml
skill_run:
  skill: resume-assistant
  workflow_stage: story-development
  plan: Plans/功能开发/2026-08-17-agent全仓TypeScript重构-US-B5-002.md
  date: 2026-08-20
  contexts_used:
    - path: Plans/Epic/2026-08-17-agent全仓TypeScript重构.md
      utility: high
      reason: "回放确认当前仍是最后一条 US-B5-002，未误进 integration-test-plan"
    - path: Plans/功能开发/2026-08-17-agent全仓TypeScript重构-US-B5-002.impl.json
      utility: high
      reason: "恢复 tooling candidate、composition、final rehearsal 与外部门禁停点"
    - path: /Users/wanglongxiang/git/agent/packages/contracts/schemas/deployment-boundary-evidence.v1.json
      utility: high
      reason: "确认仓库只有 owner evidence Schema，没有真实签署实例"
  contexts_missing:
    - "production deployment owner 提供的 deployment-boundary-evidence.v1 实例，必须绑定 candidate eedd1be73f7ec6a04a3016e3646af4b3c2f0bb9f 与 composition 455f7fe5f282d5cd8022f6c52e85ce3dd4814faaac1bdacab55bd7fd917fc8be"
    - "ready rehearsal 后指定 human reviewer 的 cutover-authorization.v1 与用户对 exact plan 的最终 destructive apply 批准"
  contexts_stale: []
  outcome: "回放 Epic、Story、代码仓库与任务临时目录；candidate/tag 未漂移，但未发现 owner 签署 evidence，因此未重跑伪 ready rehearsal、未生成 plan、未删除 Python 或切换入口"
  utility: high
  reason: "准确恢复到真实外部门禁并验证证据确实缺失，避免把用户‘继续’误当成 owner 签署或破坏性批准"
  outcome_status: pass
  revisit_needed: true
```

```yaml
skill_run:
  skill: change-impact-analysis
  workflow_stage: story-development
  plan: Plans/功能开发/2026-08-17-agent全仓TypeScript重构-US-B5-002.md
  date: 2026-08-20
  contexts_used:
    - path: Plans/需求分析/2026-08-17-agent全仓TypeScript重构.md
      utility: high
      reason: "把无生产部署的适用性裁决归位到 GWT-021/022，而不是伪造 deployment evidence"
    - path: Plans/技术方案/2026-08-17-智能体控制系统工程架构-v0.1.md
      utility: high
      reason: "新增 local_repository boundary decision，明确不得外推为未来生产发布批准"
    - path: Plans/功能开发/2026-08-17-agent全仓TypeScript重构-US-B5-002.impl.json
      utility: high
      reason: "保留 44-path、baseline、target tree 与一次切换边界，只替换不适用的 production 前提"
  contexts_missing: []
  contexts_stale:
    - "原实现落点中 production deployment evidence 对当前全本地环境的必填假设"
  outcome: "用户确认当前无部署并直接本地切换；需求、架构和 Story 增加 local_repository 分支，生产 evidence 不再误用，其余 P0 cutover 门禁不降级"
  utility: high
  reason: "消除不存在生产环境时的假门禁，同时明确未来真实部署必须重新取证"
  outcome_status: pass
  revisit_needed: false
```

```yaml
skill_run:
  skill: feature-dev-assistant
  workflow_stage: story-development
  plan: Plans/功能开发/2026-08-17-agent全仓TypeScript重构-US-B5-002.md
  date: 2026-08-20
  contexts_used:
    - path: Plans/功能开发/2026-08-17-agent全仓TypeScript重构-US-B5-002.impl.json
      utility: high
      reason: "按精确 44-path manifest、expected tree、baseline tag 和一次 cutover 契约执行"
    - path: Plans/需求分析/2026-08-17-agent全仓TypeScript重构.md
      utility: high
      reason: "验收 GWT-021-CUTOVER 主链路与 GWT-022 所有失败关闭反例"
    - path: Plans/技术方案/2026-08-17-智能体控制系统工程架构-v0.1.md
      utility: high
      reason: "落实纯 TypeScript、DSH 唯一根入口、Learning 隔离、baseline 回滚与 local-only 边界"
  contexts_missing: []
  contexts_stale: []
  outcome: "US-B5-002 完成：local decision tooling 9eff2b2、final rehearsal 11/11、plan 508f18f4、tree b22e9a8f、cutover commit 582306a；tracked Python=0，根 start=controlled DSH，切换后 TS 213/213 与全部回归通过"
  utility: high
  reason: "最后一条 Story 完成可审计的本地纯 TypeScript 切换，且未把本地批准冒充生产部署批准"
  outcome_status: pass
  revisit_needed: false
```
