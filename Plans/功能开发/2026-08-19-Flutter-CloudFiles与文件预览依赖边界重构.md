---
tags: [功能开发, 客户端, 用户故事, TDD, Flutter, CloudFiles, 架构重构]
type: plan
category: 功能开发
status: 进行中
date: 2026-08-20
lifecycle_state: integration-test-plan
epic: Plans/Epic/2026-08-19-Flutter-CloudFiles与文件预览依赖边界重构.md
requirement_plan: Plans/需求分析/2026-08-19-Flutter-CloudFiles与文件预览依赖边界重构.md
architecture_plan: Plans/技术方案/2026-08-19-Flutter-CloudFiles与文件预览依赖边界重构.md
story_index: Plans/功能开发/2026-08-19-Flutter-CloudFiles与文件预览依赖边界重构.stories.json
relations:
  depends_on:
    - Plans/需求分析/2026-08-19-Flutter-CloudFiles与文件预览依赖边界重构.md
    - Plans/需求排序/2026-08-19-Flutter-CloudFiles与文件预览依赖边界重构.md
    - Plans/技术方案/2026-08-19-Flutter-CloudFiles与文件预览依赖边界重构.md
    - Templates/客户端功能开发模板.md
    - Templates/用户故事拆分模板.md
  dependents:
    - Templates/Epic模板-client-dev.md
  supersedes: []
  superseded_by: []
  conflicts: []
---

# 功能故事开发：Flutter CloudFiles 与文件预览依赖边界重构

> client-dev 的交付单位是纵向用户故事。本轮是**不改变产品行为的架构重构**：每个故事让整条 Files 生产链保持可运行，并新增证明一条已闭合的依赖边界。故事真理源为 `.stories.json`，点数字段为 `story_points`，仅取 `1/2/3/5/8/13`，不换算工时。

## 一、开工门禁

| 输入 | 路径 | 要求 | 实况 |
|------|------|------|------|
| 需求 | `Plans/需求分析/2026-08-19-Flutter-CloudFiles与文件预览依赖边界重构.md` | 已采纳、P0=0 | ✅ |
| 排序 | `Plans/需求排序/2026-08-19-Flutter-CloudFiles与文件预览依赖边界重构.md` | 已采纳、团队确认 | ✅ |
| 架构 | `Plans/技术方案/2026-08-19-Flutter-CloudFiles与文件预览依赖边界重构.md` | 已采纳（`architecture_open=0`） | ✅ |

## 二、用户故事

7 个纵向故事 1:1 对齐已确认 Backlog CFR-001..007，按依赖顺序推进：不变量锁定 → 单向装配 → Runtime 分离 → Host 注入 → Preview 端口 → 消费者闭合 → 规则固化。

| Story ID | 用户能力 | 需求 | AC | 架构引用 | 依赖 | 优先级 | 故事点 | Scope | 子 Plan |
|----------|----------|------|----|----------|------|--------|--------|-------|---------|
| US-CFR-001 | 作为 Flutter 维护者/测试，我能用先红后绿的边界与不变量回归网锁定当前依赖违规与生产行为，以便后续每步重构都有可回退基线 | CFR-001 | AC-06, AC-08 | ADR-CFR-001 | — | P0 | 5 | false | `Plans/功能开发/2026-08-19-Flutter-CloudFiles与文件预览依赖边界重构-US-CFR-001.md` |
| US-CFR-002 | 作为 Flutter 维护者，我能让 Files 相关 composition 子模块不再反向 import `composition_root.dart`，以便依赖只指向叶子 primitive | CFR-002 | AC-02 | ADR-CFR-005 | US-CFR-001 | P0 | 5 | false | `Plans/功能开发/2026-08-19-Flutter-CloudFiles与文件预览依赖边界重构-US-CFR-002.md` |
| US-CFR-003 | 作为 Flutter 维护者，我能把 `CloudFilesRuntime` 拆成 App 私有运行时与 Feature 可见投影，以便鉴权/网络/平台不再泄漏给 Feature 且 owner 围栏不变 | CFR-003 | AC-03, AC-06 | ADR-CFR-001, ADR-CFR-003 | US-CFR-001, US-CFR-002 | P0 | 8 | false | `Plans/功能开发/2026-08-19-Flutter-CloudFiles与文件预览依赖边界重构-US-CFR-003.md` |
| US-CFR-004 | 作为终端用户，我能在 Files 页面浏览云盘/Workspace 且页面只消费 Host 注入的窄依赖，以便 Feature 零 `app/**` import 而浏览行为不变 | CFR-004 | AC-01, AC-04 | ADR-CFR-002, ADR-CFR-004 | US-CFR-003 | P0 | 8 | false | `Plans/功能开发/2026-08-19-Flutter-CloudFiles与文件预览依赖边界重构-US-CFR-004.md` |
| US-CFR-005 | 作为终端用户，我能由独立 FilePreview Feature 预览云盘、Workspace、AI 与附件文件，App 只装配 typed binding，以便模块归属清晰且平台行为不变 | CFR-005 | AC-05, AC-07 | ADR-CFR-004, ADR-CFR-008 | US-CFR-003, US-CFR-004 | P0 | 8 | false | `Plans/功能开发/2026-08-19-Flutter-CloudFiles与文件预览依赖边界重构-US-CFR-005.md` |
| US-CFR-006 | 作为 Flutter 维护者，我能把 Main/Projects/Download 等旧消费者迁到 App 内部能力并闭合运行时生命周期，以便旧大 Runtime 暴露面可安全收窄 | CFR-006 | AC-07, AC-08, AC-09 | ADR-CFR-003, ADR-CFR-005, ADR-CFR-006 | US-CFR-003, US-CFR-004, US-CFR-005 | P0 | 5 | false | `Plans/功能开发/2026-08-19-Flutter-CloudFiles与文件预览依赖边界重构-US-CFR-006.md` |
| US-CFR-007 | 作为后续开发者，我能读到"App composition 模块装配、root 只汇聚"的规则并有自动门禁防回退，以便新文件能力有明确装配入口 | CFR-007 | AC-10 | ADR-CFR-001, ADR-CFR-005 | US-CFR-001..006 | P1 | 3 | true | `Plans/功能开发/2026-08-19-Flutter-CloudFiles与文件预览依赖边界重构-US-CFR-007.md` |

- 合计 **39 点**（P0×6 = 36，P1×1 = 3）；无 13 点故事，无需豁免。
- 交付 Scope（`epic_scope`）= 全部 7 故事；`sprint_scope` 单故事滚动，首个滚动故事为 US-CFR-001。
- 需求 AC-01..AC-10 全部被 Scope 故事覆盖（详见 `.stories.json` 与各子 Plan）。

### AC 覆盖矩阵

| 需求 AC | 由哪个故事闭合 |
|---|---|
| AC-01 Files→App import=0 | US-CFR-004 |
| AC-02 composition→root import=0 | US-CFR-002 |
| AC-03 App/Feature Runtime 职责分离 | US-CFR-003 |
| AC-04 Files 入口由 Host 注入窄依赖 | US-CFR-004 |
| AC-05 预览实现归独立 Feature、App 只装配 | US-CFR-005 |
| AC-06 owner 切换与迟到结果隔离 | US-CFR-001（基线）、US-CFR-003（拆分后不变） |
| AC-07 协议/签名/namespace/持久化/UI 不变 | US-CFR-005（预览）、US-CFR-006（全量 diff） |
| AC-08 Provider 生命周期无重复创建/释放 | US-CFR-001（基线）、US-CFR-006（闭合） |
| AC-09 旧生产消费者迁移落点关闭 | US-CFR-006 |
| AC-10 文档不再暗示 Provider 写进单一根文件 | US-CFR-007 |

## 三、当前进度快照（2026-08-21）

- 已有 CloudFiles/文件预览生产基线已完成：统一 Preview Planner/Coordinator/Launcher/Source、CloudFiles 三类文件、双端宿主预览、上传/下载/分享与多格式预览均有对应提交和测试。
- 上述成果是本轮“无产品行为变化”的重构基线，不等于 US-CFR-001..007 已完成。
- **US-CFR-001 已完成**：显式依赖边界 Red、默认债务快照、CloudFiles/Preview lifecycle 与 owner smoke 已形成 TDD 证据；生产代码未变。
- **US-CFR-002 已完成**：四个 Files composition 对 root import 归零，四个 primitive 叶子承接原 Provider 声明，root 保留兼容 export；TDD 与聚焦 smoke 已通过。
- **US-CFR-003 已完成**：CloudFilesAppRuntime / CloudFilesFeatureRuntime 类型与生产投影已拆分，AC-03/06、owner/lifecycle 与 Files 换代 smoke 已通过。
- **US-CFR-004 已完成**：Files→App 6 条 import 债务清零，FilesDestination 逐槽生产注入、SDK connection preparation、Overlay owner feed 与 57 项页面回归均通过，AC-01/04 PASS。
- **US-CFR-005 已完成**：27 个 Preview/Transfer 实现归位 Feature，App 仅保留 composition/navigation 与无凭据 binding；233 项最终定向回归和连接 iPhone 启动 smoke 通过，AC-05/07 PASS。
- **US-CFR-006 已完成**：旧 Runtime typedef 与下载 Feature 的 App 命名归零，CloudFiles/download runtime/manager 单实例与单次 dispose 通过，AC-07/08/09 PASS。
- **US-CFR-007 已完成**：正式架构文档、FilePreview 中性类型命名与 Feature/App 自动边界已固化，60/60 聚焦回归与 iPhone 启动 smoke 通过，AC-10 PASS。
- 7/7 个 Story 全部完成并通过逐故事 TDD 门禁；当前阶段滚动至 `integration-test-plan`。
- 当前待办：产出并审核集成测试计划，再执行 Android Phone/Pad/Fold 与 iPhone/iPad 完整矩阵。

## 四、实现落点设计（当前阶段）

每个 Scope Story 进入 TDD 前必须先完成代码落点设计：Story 子 Plan frontmatter 写 `implementation_design:`，JSON 明确代码证据、目标文件、分层边界、依赖方向和 Red 测试位置。

门禁：`python3 scripts/validate-client-dev.py implementation-design --plan Plans/功能开发/2026-08-19-Flutter-CloudFiles与文件预览依赖边界重构.md`

| Story ID | 落点设计 | 状态 |
|----------|----------|------|
| US-CFR-001 | `…-US-CFR-001.impl.json` | ✅ 已完成（2026-08-21） |
| US-CFR-002 | `…-US-CFR-002.impl.json` | ✅ 已完成（2026-08-21） |
| US-CFR-003 | `…-US-CFR-003.impl.json` | ✅ 已完成（2026-08-21） |
| US-CFR-004 | `…-US-CFR-004.impl.json` | ✅ 已完成（2026-08-21） |
| US-CFR-005 | `…-US-CFR-005.impl.json` | ✅ 已完成（归位 FilePreview Feature + typed binding） |
| US-CFR-006 | `…-US-CFR-006.impl.json` | ✅ 已完成（2026-08-21） |
| US-CFR-007 | `…-US-CFR-007.impl.json` | ✅ 已完成（2026-08-21） |

## 五、故事内部 TDD

每个故事独立执行：

```text
Red → Green → Refactor → integration smoke → 故事验收
```

边界测试、Runtime 字段测试、owner fencing 回归、生命周期测试、UI/Widget 回归都是故事内部实现步骤，不作为横向交付故事。证据写入各故事 `tdd_evidence` JSON。重构约束：任一故事若使生产行为回归，回滚该结构提交而非改协议/清缓存，状态保持 PARTIAL。

## 六、完成门禁

- [x] 所有 Scope 故事有团队确认的故事点（`estimate_confirmed`）
- [x] 所有 Scope 故事通过逐故事 TDD 门禁（Red/Green/Refactor/smoke/AC）
- [ ] 进入 `integration-test-plan`，产出结构化用例并经测试人员审核
- [ ] 审核通过后进入全量 `integration-test`

全量集成测试通过后直接 Done；本流程不含发布、灰度或线上观察。

## 七、待确认项

- 无阻断项。故事结构、依赖顺序与故事点已由用户于 2026-08-20 按提议确认。

## 八、US-CFR-003 实现落点设计

- 新建 `lib/features/files/cloud_files_feature_runtime.dart`，只定义 identity 与五组 domain owner/repository 投影；禁止 App、network/auth/signing、platform 与 Riverpod 类型。
- `lib/app/cloud_files_runtime.dart` 承载 App-private SessionSnapshot/Store 与 `CloudFilesAppRuntime`，生产 `cloud_files_providers.dart` 先构造 Feature Runtime 再注入 App Runtime。
- 复用现有 `isCurrentSnapshot`、Provider 与 onDispose，不改 owner equality、HTTP/签名、namespace、持久化或平台行为。
- `CloudFilesRuntime` 仅保留 App 侧临时兼容面，本 Story 不改 `features/files/**` 消费/import，不迁移 Main/Projects/Download。
- Red 锁在 Feature Runtime 字段/import 测试与 App Runtime provider 投影/owner/lifecycle 测试；详见 `…-US-CFR-003.impl.json`。

## 九、US-CFR-004 实现落点设计

- 新建 Files Feature dependency scope，提供 runtime state、Gateway lease、CloudDrive/Workspace Repository、附件能力和 retry slots；默认显式 unavailable 或 fail-fast，不创建 App/Fake 依赖。
- App `files_providers.dart` 构造并缓存 Cloud Feature runtime state、Gateway lease 和真实 Repository；`FilesDestination` 的子 `ProviderScope` 覆盖全部 slots，是唯一生产注入点。
- `files_page.dart` 与 AI/Workspace controllers 只消费 Feature 类型。现有动作 callback 先收窄为 typed item + `CloudFilesRuntimeIdentity` / `FilesGatewayLease`，平台实现继续留 App；正式 `FilesHostActions` typed port 留 US-CFR-005。
- `CloudBrowserController` 删除连接/App Provider 读取，CloudDrive connection preparation 进入 SDK/DataSource 并覆盖全部读写；原本地 generation、owner/item fence、目录/搜索/取消/分页语义保持。
- App preview launcher 改读 App concrete CloudDrive Repository，避免 Projects/attachment 依赖 Files 子 Scope；非 Files 消费者迁移仍留 US-CFR-006。
- Red 锁定 Files→App 6 条债务清零、dependency slots 默认、FilesDestination 逐槽生产覆盖、SDK preparation 和现有页面/Controller owner 回归；详见 `…-US-CFR-004.impl.json`。

## 反馈（skill_run）

```yaml
skill_run:
  skill: task-splitter
  workflow_stage: story-split
  plan: Plans/功能开发/2026-08-19-Flutter-CloudFiles与文件预览依赖边界重构.md
  date: 2026-08-20
  contexts_used:
    - path: Plans/技术方案/2026-08-19-Flutter-CloudFiles与文件预览依赖边界重构.md
      utility: high
      reason: "按 ADR-CFR-001..006 与实施顺序把重构切成 7 个可独立验收的边界里程碑，1:1 对齐 Backlog"
    - path: Plans/需求分析/2026-08-19-Flutter-CloudFiles与文件预览依赖边界重构.md
      utility: high
      reason: "用 AC-01..10 与 GWT 实例化需求确定每个故事的验收锚点与 AC 覆盖矩阵"
    - path: Plans/需求排序/2026-08-19-Flutter-CloudFiles与文件预览依赖边界重构.md
      utility: high
      reason: "沿用 CFR-001..007 的价值/优先级/依赖顺序，保证故事优先级与 P0/P1 一致"
    - path: Templates/用户故事拆分模板.md
      utility: high
      reason: "落实纵向切分、故事点 1/2/3/5/8/13、13 点豁免与 Scope 确认门禁"
    - path: Templates/客户端功能开发模板.md
      utility: high
      reason: "对齐主 Plan 结构、story_index 字段与实现落点/TDD/完成门禁章节"
  contexts_missing: []
  contexts_stale: []
  outcome_status: pass
  friction: ""
  revisit_needed: false
```

```yaml
skill_run:
  skill: resume-assistant
  plan: Plans/功能开发/2026-08-19-Flutter-CloudFiles与文件预览依赖边界重构.md
  date: 2026-08-20
  contexts_used:
    - path: Contexts/决策/2026-08-20-开发流程审计报告.md
      utility: high
      reason: "按提交、生产 import 和门禁证据区分已完成 CloudFiles/Preview 基线与尚未落地的第二轮依赖边界收口"
    - path: Plans/Epic/2026-08-19-Flutter-CloudFiles与文件预览依赖边界重构.md
      utility: high
      reason: "对齐 Epic 当前 lifecycle、7 个 Story 看板与 US-CFR-001 滚动 Scope"
  contexts_missing: []
  contexts_stale: []
  outcome_status: partial
  friction: "当前 implementation-design 门禁仍缺 US-CFR-001 implementation_design 路径"
  revisit_needed: false
```

```yaml
skill_run:
  skill: feature-dev-assistant
  workflow_stage: story-development
  plan: Plans/功能开发/2026-08-19-Flutter-CloudFiles与文件预览依赖边界重构.md
  date: 2026-08-21
  contexts_used:
    - path: Plans/功能开发/2026-08-19-Flutter-CloudFiles与文件预览依赖边界重构-US-CFR-001.impl.json
      utility: high
      reason: "按机器落点完成当前滚动 Story 的 test-only TDD 闭环"
    - path: Plans/功能开发/2026-08-19-Flutter-CloudFiles与文件预览依赖边界重构-US-CFR-001.md
      utility: high
      reason: "同步 AC-06/AC-08、测试结果与未运行项，作为 Story 完成真理源"
    - path: Contexts/决策/Skill反馈协议.md
      utility: high
      reason: "满足 story-development 阶段最后 skill_run 门禁"
  contexts_missing: []
  contexts_stale: []
  outcome_status: pass
  friction: "Files 全文件存在与本 Story 无关的既有 Golden 0.11% 差异；相关 owner/preview smoke 已独立通过"
  revisit_needed: false
```

```yaml
skill_run:
  skill: implementation-design-assistant
  workflow_stage: implementation-design
  plan: Plans/功能开发/2026-08-19-Flutter-CloudFiles与文件预览依赖边界重构.md
  date: 2026-08-21
  contexts_used:
    - path: Plans/功能开发/2026-08-19-Flutter-CloudFiles与文件预览依赖边界重构-US-CFR-001.md
      utility: high
      reason: "将当前滚动 Story 的代码证据、目标测试文件、Red 命令与生命周期风险固化为机器契约"
    - path: Plans/技术方案/2026-08-19-Flutter-CloudFiles与文件预览依赖边界重构.md
      utility: high
      reason: "保持 Provider graph 留 App、Feature 不感知 App 与 owner/lifecycle 不变量"
    - path: Contexts/决策/Skill反馈协议.md
      utility: high
      reason: "补齐 workflow-gate 要求的 implementation-design 阶段反馈"
  contexts_missing: []
  contexts_stale: []
  outcome_status: pass
  revisit_needed: false
```

```yaml
skill_run:
  skill: resume-assistant
  workflow_stage: story-development
  plan: Plans/功能开发/2026-08-19-Flutter-CloudFiles与文件预览依赖边界重构.md
  date: 2026-08-21
  contexts_used:
    - path: Plans/Epic/2026-08-19-Flutter-CloudFiles与文件预览依赖边界重构.md
      utility: high
      reason: "以 workflow-status 推导的 story-development 恢复 US-CFR-003，忽略已完成前置 Story"
    - path: Plans/功能开发/2026-08-19-Flutter-CloudFiles与文件预览依赖边界重构-US-CFR-003.impl.json
      utility: high
      reason: "确认已通过 implementation-design 门禁后再开始 Red，不扩 Scope"
    - path: Contexts/决策/Skill反馈协议.md
      utility: high
      reason: "按续作协议写入完成事实和 US-CFR-004 恢复点"
  contexts_missing: []
  contexts_stale: []
  outcome_status: pass
  friction: "当前 Flutter 工作树同时含 US-CFR-001/002 未提交改动，验收需以定向路径和 tdd_evidence 隔离故事边界"
  revisit_needed: false
```

```yaml
skill_run:
  skill: feature-dev-assistant
  workflow_stage: story-development
  plan: Plans/功能开发/2026-08-19-Flutter-CloudFiles与文件预览依赖边界重构.md
  date: 2026-08-21
  contexts_used:
    - path: Plans/功能开发/2026-08-19-Flutter-CloudFiles与文件预览依赖边界重构-US-CFR-003.impl.json
      utility: high
      reason: "按已确认落点拆分 App/Feature Runtime，保留增量兼容边界"
    - path: Plans/功能开发/2026-08-19-Flutter-CloudFiles与文件预览依赖边界重构-US-CFR-003.tdd.json
      utility: high
      reason: "以 Red/Green/Refactor/smoke/AC 及未运行项作为 US-CFR-003 完成真理源"
    - path: Contexts/决策/Skill反馈协议.md
      utility: high
      reason: "保证主 Plan 最后 skill_run 精确对应 story-development 门禁"
  contexts_missing: []
  contexts_stale: []
  outcome_status: pass
  friction: "impact selector 未登记新 Feature Runtime 路径，本次用专用边界测试与 Files owner smoke 人工解析 unresolved impact"
  revisit_needed: false
```

```yaml
skill_run:
  skill: resume-assistant
  plan: Plans/功能开发/2026-08-19-Flutter-CloudFiles与文件预览依赖边界重构.md
  date: 2026-08-20
  contexts_used:
    - path: Plans/Epic/2026-08-19-Flutter-CloudFiles与文件预览依赖边界重构.md
      utility: high
      reason: "从 Epic 母 plan 读 workflow/lifecycle_state 与子 Plan 索引，派生 story-split 为当前阶段并确认授权拆分"
    - path: Contexts/决策/Skill反馈协议.md
      utility: high
      reason: "按协议在目标 plan 末尾追加合法 skill_run 反馈，避免 plan-gate-check 失败"
  contexts_missing: []
  contexts_stale: []
  outcome_status: pass
  friction: ""
  revisit_needed: false
```

```yaml
skill_run:
  skill: resume-assistant
  workflow_stage: implementation-design
  plan: Plans/功能开发/2026-08-19-Flutter-CloudFiles与文件预览依赖边界重构.md
  date: 2026-08-21
  contexts_used:
    - path: Plans/Epic/2026-08-19-Flutter-CloudFiles与文件预览依赖边界重构.md
      utility: high
      reason: "以 Epic 最新 lifecycle、阶段索引和变更记录为准，避免按 2026-08-19 的旧线程停点重复 Story 拆分"
    - path: Plans/功能开发/2026-08-19-Flutter-CloudFiles与文件预览依赖边界重构-US-CFR-001.md
      utility: high
      reason: "完成当前滚动 Story 的实现落点契约并确定只改 test/** 的下一阶段边界"
    - path: Contexts/决策/Skill反馈协议.md
      utility: high
      reason: "补齐本次续作的最终反馈与可恢复继续点"
  contexts_missing: []
  contexts_stale: []
  outcome_status: pass
  friction: "初始线程记录停在 story-split，但 Epic 已于 2026-08-20 推进；本次以最新 plan 回放纠正"
  revisit_needed: false
```

```yaml
skill_run:
  skill: feature-dev-assistant
  workflow_stage: story-development
  plan: Plans/功能开发/2026-08-19-Flutter-CloudFiles与文件预览依赖边界重构.md
  date: 2026-08-21
  contexts_used:
    - path: Plans/功能开发/2026-08-19-Flutter-CloudFiles与文件预览依赖边界重构-US-CFR-001.impl.json
      utility: high
      reason: "按机器契约闭合 US-CFR-001，并在机械验收后滚动 Scope"
    - path: Plans/功能开发/2026-08-19-Flutter-CloudFiles与文件预览依赖边界重构-US-CFR-001.md
      utility: high
      reason: "确认 Story 状态、AC 与 tdd_evidence 均已完成"
    - path: Contexts/决策/Skill反馈协议.md
      utility: high
      reason: "保持主 Plan 最后 story-development 反馈可被工作流读取"
  contexts_missing: []
  contexts_stale: []
  outcome_status: pass
  revisit_needed: false
```

## 续做

```text
/resume plan=Plans/功能开发/2026-08-19-Flutter-CloudFiles与文件预览依赖边界重构.md 进度=implementation-design（US-CFR-006）
```

## 反馈（skill_run）

```yaml
skill_run:
  skill: resume-assistant
  workflow_stage: story-development
  plan: Plans/功能开发/2026-08-19-Flutter-CloudFiles与文件预览依赖边界重构.md
  date: 2026-08-21
  contexts_used:
    - path: Plans/Epic/2026-08-19-Flutter-CloudFiles与文件预览依赖边界重构.md
      utility: high
      reason: "通过最新事件流与动态看板恢复 US-CFR-002 story-development，而非受 Epic 旧 lifecycle hint 误导"
    - path: Plans/功能开发/2026-08-19-Flutter-CloudFiles与文件预览依赖边界重构-US-CFR-002.impl.json
      utility: high
      reason: "确认落点门禁已通过后续做 Red→Green→Refactor，不扩大到 US-CFR-003 Runtime 拆分"
    - path: Contexts/决策/Skill反馈协议.md
      utility: high
      reason: "按续作协议记录事件流回放、阶段推进与下一恢复点"
  contexts_missing: []
  contexts_stale: []
  outcome_status: pass
  friction: "Epic lifecycle_state 文本滞后于子 Plan/事件流；以 workflow-status 与子 Plan 为准恢复并在完成后同步"
  revisit_needed: false
```

```yaml
skill_run:
  skill: feature-dev-assistant
  workflow_stage: story-development
  plan: Plans/功能开发/2026-08-19-Flutter-CloudFiles与文件预览依赖边界重构.md
  date: 2026-08-21
  contexts_used:
    - path: Plans/功能开发/2026-08-19-Flutter-CloudFiles与文件预览依赖边界重构-US-CFR-002.impl.json
      utility: high
      reason: "按已确认文件落点整体迁移原 Provider 声明，完成四条边界的 Red/Green 闭环"
    - path: Plans/功能开发/2026-08-19-Flutter-CloudFiles与文件预览依赖边界重构-US-CFR-002.tdd.json
      utility: high
      reason: "固化边界、Provider lifecycle、owner 换代、下载/预览 smoke 及 NOT_RUN 设备围栏证据"
    - path: Contexts/决策/Skill反馈协议.md
      utility: high
      reason: "保证主 Plan 最后 story-development 反馈可被机械门禁和月度聚合读取"
  contexts_missing: []
  contexts_stale: []
  outcome_status: pass
  friction: "permission Widget 测试的 SharedPreferencesAsyncPlatform 既有初始化失败已单独复跑并隔离，未影响本 Story 主链通过"
  revisit_needed: false
```

```yaml
skill_run:
  skill: resume-assistant
  workflow_stage: implementation-design
  plan: Plans/功能开发/2026-08-19-Flutter-CloudFiles与文件预览依赖边界重构.md
  date: 2026-08-21
  contexts_used:
    - path: Plans/Epic/2026-08-19-Flutter-CloudFiles与文件预览依赖边界重构.md
      utility: high
      reason: "恢复 US-CFR-003 为唯一滚动 Scope，确认前置 Story 和架构裁决已闭合"
    - path: Plans/功能开发/2026-08-19-Flutter-CloudFiles与文件预览依赖边界重构-US-CFR-003.md
      utility: high
      reason: "只补齐当前 Story 缺失的 implementation_design，不重做 US-CFR-001/002 或跨入后续 Story"
    - path: Contexts/决策/Skill反馈协议.md
      utility: high
      reason: "记录本次续作阶段和可恢复的下一 TDD 起点"
  contexts_missing: []
  contexts_stale: []
  outcome_status: pass
  friction: "工作流事件已可推导 story-development，Epic lifecycle hint 需与子 Plan 同步"
  revisit_needed: false
```

```yaml
skill_run:
  skill: implementation-design-assistant
  workflow_stage: implementation-design
  plan: Plans/功能开发/2026-08-19-Flutter-CloudFiles与文件预览依赖边界重构.md
  date: 2026-08-21
  contexts_used:
    - path: Plans/功能开发/2026-08-19-Flutter-CloudFiles与文件预览依赖边界重构-US-CFR-003.impl.json
      utility: high
      reason: "将 Runtime 拆分目标文件、依赖方向、兼容 seam、Red 测试和风险固化为机器契约"
    - path: Plans/技术方案/2026-08-19-Flutter-CloudFiles与文件预览依赖边界重构.md
      utility: high
      reason: "以 ADR-CFR-003 和 Feature Runtime schema 锁定字段可见性，不放宽网络/鉴权/平台边界"
    - path: Contexts/决策/Skill反馈协议.md
      utility: high
      reason: "保证主 Plan 最后 skill_run 精确对应 implementation-design 阶段"
  contexts_missing: []
  contexts_stale: []
  outcome_status: pass
  friction: "需通过 App 侧临时别名/兼容构造保留现有消费者，并明确由 US-CFR-004/006 后续删除"
  revisit_needed: false
```

```yaml
skill_run:
  skill: resume-assistant
  workflow_stage: story-development
  plan: Plans/功能开发/2026-08-19-Flutter-CloudFiles与文件预览依赖边界重构.md
  date: 2026-08-21
  contexts_used:
    - path: Plans/Epic/2026-08-19-Flutter-CloudFiles与文件预览依赖边界重构.md
      utility: high
      reason: "以 workflow-status 推导的 story-development 恢复 US-CFR-003，忽略已完成前置 Story"
    - path: Plans/功能开发/2026-08-19-Flutter-CloudFiles与文件预览依赖边界重构-US-CFR-003.impl.json
      utility: high
      reason: "确认已通过 implementation-design 门禁后再开始 Red，不扩 Scope"
    - path: Contexts/决策/Skill反馈协议.md
      utility: high
      reason: "按续作协议写入完成事实和 US-CFR-004 恢复点"
  contexts_missing: []
  contexts_stale: []
  outcome_status: pass
  friction: "当前 Flutter 工作树同时含 US-CFR-001/002 未提交改动，验收需以定向路径和 tdd_evidence 隔离故事边界"
  revisit_needed: false
```

```yaml
skill_run:
  skill: feature-dev-assistant
  workflow_stage: story-development
  plan: Plans/功能开发/2026-08-19-Flutter-CloudFiles与文件预览依赖边界重构.md
  date: 2026-08-21
  contexts_used:
    - path: Plans/功能开发/2026-08-19-Flutter-CloudFiles与文件预览依赖边界重构-US-CFR-003.impl.json
      utility: high
      reason: "按已确认落点拆分 App/Feature Runtime，保留增量兼容边界"
    - path: Plans/功能开发/2026-08-19-Flutter-CloudFiles与文件预览依赖边界重构-US-CFR-003.tdd.json
      utility: high
      reason: "以 Red/Green/Refactor/smoke/AC 及未运行项作为 US-CFR-003 完成真理源"
    - path: Contexts/决策/Skill反馈协议.md
      utility: high
      reason: "保证主 Plan 最后 skill_run 精确对应 story-development 门禁"
  contexts_missing: []
  contexts_stale: []
  outcome_status: pass
  friction: "impact selector 未登记新 Feature Runtime 路径，本次用专用边界测试与 Files owner smoke 人工解析 unresolved impact"
  revisit_needed: false
```

```yaml
skill_run:
  skill: resume-assistant
  workflow_stage: implementation-design
  plan: Plans/功能开发/2026-08-19-Flutter-CloudFiles与文件预览依赖边界重构.md
  date: 2026-08-21
  contexts_used:
    - path: Plans/Epic/2026-08-19-Flutter-CloudFiles与文件预览依赖边界重构.md
      utility: high
      reason: "通过事件流与当前 Scope 恢复 US-CFR-004 implementation-design，确认 US-CFR-001..003 已完成"
    - path: Plans/功能开发/2026-08-19-Flutter-CloudFiles与文件预览依赖边界重构-US-CFR-004.md
      utility: high
      reason: "以当前 Story 的 AC-01/04、Scope 和生产入口要求限制本次只做落点设计"
    - path: Contexts/决策/Skill反馈协议.md
      utility: high
      reason: "记录恢复阶段、工作树隔离事实和下一 story-development 起点"
  contexts_missing: []
  contexts_stale: []
  outcome_status: pass
  friction: "Flutter 工作树包含 US-CFR-001..003 累积改动，本轮保持只读并把新增产物限制在 AI plan 仓库"
  revisit_needed: false
```

```yaml
skill_run:
  skill: implementation-design-assistant
  workflow_stage: implementation-design
  plan: Plans/功能开发/2026-08-19-Flutter-CloudFiles与文件预览依赖边界重构.md
  date: 2026-08-21
  contexts_used:
    - path: Plans/技术方案/2026-08-19-Flutter-CloudFiles与文件预览依赖边界重构.md
      utility: high
      reason: "以 ADR-CFR-002/004、Provider 归属和 Gateway 边界锁定 App host→Feature slot 单向依赖"
    - path: Plans/功能开发/2026-08-19-Flutter-CloudFiles与文件预览依赖边界重构-US-CFR-004.impl.json
      utility: high
      reason: "将目标文件、模块规则、Red 命令、owner 风险和后续 Story 边界固化为机器契约"
    - path: Contexts/决策/Skill反馈协议.md
      utility: high
      reason: "保证主 Plan 最后 skill_run 对齐 implementation-design 门禁"
  contexts_missing: []
  contexts_stale: []
  outcome_status: pass
  friction: "需要兼顾用户希望 UI 与插件保持同一产品入口，同时确保平台实现只存在 App、Files Feature 只拿窄契约"
  revisit_needed: false
```

```yaml
skill_run:
  skill: resume-assistant
  workflow_stage: story-development
  plan: Plans/功能开发/2026-08-19-Flutter-CloudFiles与文件预览依赖边界重构.md
  date: 2026-08-21
  contexts_used:
    - path: Plans/Epic/2026-08-19-Flutter-CloudFiles与文件预览依赖边界重构.md
      utility: high
      reason: "以 workflow-status、当前 Scope 与子 Plan 恢复 US-CFR-004 story-development"
    - path: Plans/功能开发/2026-08-19-Flutter-CloudFiles与文件预览依赖边界重构-US-CFR-004.impl.json
      utility: high
      reason: "确认 implementation-design 已闭合后只执行当前 Story TDD，不跨入 US-CFR-005/006"
    - path: Contexts/决策/Skill反馈协议.md
      utility: high
      reason: "记录当前完成事实和 US-CFR-005 implementation-design 恢复点"
  contexts_missing: []
  contexts_stale: []
  outcome_status: pass
  friction: "累积工作树触发额外真网络/支付围栏，需区分本 Story 聚焦测试与 Epic 里程碑设备矩阵"
  revisit_needed: false
```

```yaml
skill_run:
  skill: change-impact-analysis
  workflow_stage: implementation-design
  plan: Plans/功能开发/2026-08-19-Flutter-CloudFiles与文件预览依赖边界重构.md
  date: 2026-08-21
  contexts_used:
    - path: Contexts/决策/2026-08-21-文件预览归位Feature-变更影响.md
      utility: high
      reason: "将 AC、ADR、US-CFR-005/006、源码与测试受影响范围收敛为已确认变更"
    - path: Plans/需求分析/2026-08-19-Flutter-CloudFiles与文件预览依赖边界重构.md
      utility: high
      reason: "区分需修订的 AC-05 与仍保持不变的协议/owner/UI 验收约束"
  contexts_missing: []
  contexts_stale: []
  outcome_status: pass
  revisit_needed: false
```

```yaml
skill_run:
  skill: implementation-design-assistant
  workflow_stage: implementation-design
  plan: Plans/功能开发/2026-08-19-Flutter-CloudFiles与文件预览依赖边界重构.md
  date: 2026-08-21
  contexts_used:
    - path: Plans/功能开发/2026-08-19-Flutter-CloudFiles与文件预览依赖边界重构-US-CFR-005.md
      utility: high
      reason: "将用户确认的 FilePreview Feature 归位拆成当前 Story 的文件、分层、依赖和 Red 落点"
    - path: Plans/技术方案/2026-08-19-Flutter-CloudFiles与文件预览依赖边界重构.md
      utility: high
      reason: "使用修订后 ADR-CFR-004/008 锁定 App→Feature 单向装配"
  contexts_missing: []
  contexts_stale: []
  outcome_status: pass
  revisit_needed: false
```

```yaml
skill_run:
  skill: feature-dev-assistant
  workflow_stage: story-development
  plan: Plans/功能开发/2026-08-19-Flutter-CloudFiles与文件预览依赖边界重构.md
  date: 2026-08-21
  contexts_used:
    - path: Plans/功能开发/2026-08-19-Flutter-CloudFiles与文件预览依赖边界重构-US-CFR-004.impl.json
      utility: high
      reason: "按落点完成 Host→Feature 单向注入、零 App import、Gateway preparation 与 owner route guard"
    - path: Plans/功能开发/2026-08-19-Flutter-CloudFiles与文件预览依赖边界重构-US-CFR-004.tdd.json
      utility: high
      reason: "以 Red/Green/Refactor、AC-01/04、聚焦回归和 NOT_RUN 围栏作为 Story 完成真理源"
    - path: Contexts/决策/Skill反馈协议.md
      utility: high
      reason: "保证主 Plan 最后 skill_run 对齐 story-development 门禁"
  contexts_missing: []
  contexts_stale: []
  outcome_status: pass
  friction: "根 Navigator Overlay 不继承 Files 子 ProviderScope；引入无凭证 route owner feed 后保持 UI/插件同一 App 入口且 Feature 不接触平台实现"
  revisit_needed: false
```

```yaml
skill_run:
  skill: feature-dev-assistant
  workflow_stage: story-development
  plan: Plans/功能开发/2026-08-19-Flutter-CloudFiles与文件预览依赖边界重构.md
  date: 2026-08-21
  contexts_used:
    - path: Plans/功能开发/2026-08-19-Flutter-CloudFiles与文件预览依赖边界重构-US-CFR-005.impl.json
      utility: high
      reason: "按修订架构把 Preview/Transfer 生产实现归位 Feature，并让 App 只保留装配与路由"
    - path: Plans/功能开发/2026-08-19-Flutter-CloudFiles与文件预览依赖边界重构-US-CFR-005.tdd.json
      utility: high
      reason: "记录 27 文件 Red、233 项 focused Green、scoped analyze 与 iPhone 启动 smoke"
  contexts_missing: []
  contexts_stale: []
  outcome_status: pass
  friction: "累积工作树含前四个 Story；以专用边界测试、Feature 路径与 TDD JSON 隔离本 Story"
  revisit_needed: false
```

```yaml
skill_run:
  skill: feature-dev-assistant
  workflow_stage: story-development
  plan: Plans/功能开发/2026-08-19-Flutter-CloudFiles与文件预览依赖边界重构.md
  date: 2026-08-21
  contexts_used:
    - path: Plans/功能开发/2026-08-19-Flutter-CloudFiles与文件预览依赖边界重构-US-CFR-007.impl.json
      utility: high
      reason: "按最终落点固化文档、类型命名与边界门禁"
    - path: Plans/功能开发/2026-08-19-Flutter-CloudFiles与文件预览依赖边界重构-US-CFR-007.tdd.json
      utility: high
      reason: "以 60/60 Green、scoped analyze、AC-10 和 iPhone smoke 作为 7/7 Story 收口证据"
  contexts_missing: []
  contexts_stale: []
  outcome_status: pass
  friction: "完整设备矩阵与真网络高风险围栏属集成里程碑，本阶段保持 NOT_RUN 而不伪成已通过"
  revisit_needed: false
```
