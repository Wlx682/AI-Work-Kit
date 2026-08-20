---
tags: [功能开发, 客户端, 用户故事, TDD, Flutter, CloudFiles, 架构重构]
type: plan
category: 功能开发
status: 进行中
date: 2026-08-20
lifecycle_state: implementation-design
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
| US-CFR-001 | 作为 Flutter 维护者/测试，我能用先红后绿的边界与不变量回归网锁定当前依赖违规与生产行为，以便后续每步重构都有可回退基线 | CFR-001 | AC-06, AC-08 | ADR-CFR-001 | — | P0 | 5 | true | `Plans/功能开发/2026-08-19-Flutter-CloudFiles与文件预览依赖边界重构-US-CFR-001.md` |
| US-CFR-002 | 作为 Flutter 维护者，我能让 Files 相关 composition 子模块不再反向 import `composition_root.dart`，以便依赖只指向叶子 primitive | CFR-002 | AC-02 | ADR-CFR-005 | US-CFR-001 | P0 | 5 | false | `Plans/功能开发/2026-08-19-Flutter-CloudFiles与文件预览依赖边界重构-US-CFR-002.md` |
| US-CFR-003 | 作为 Flutter 维护者，我能把 `CloudFilesRuntime` 拆成 App 私有运行时与 Feature 可见投影，以便鉴权/网络/平台不再泄漏给 Feature 且 owner 围栏不变 | CFR-003 | AC-03, AC-06 | ADR-CFR-001, ADR-CFR-003 | US-CFR-001, US-CFR-002 | P0 | 8 | false | `Plans/功能开发/2026-08-19-Flutter-CloudFiles与文件预览依赖边界重构-US-CFR-003.md` |
| US-CFR-004 | 作为终端用户，我能在 Files 页面浏览云盘/Workspace 且页面只消费 Host 注入的窄依赖，以便 Feature 零 `app/**` import 而浏览行为不变 | CFR-004 | AC-01, AC-04 | ADR-CFR-002, ADR-CFR-004 | US-CFR-003 | P0 | 8 | false | `Plans/功能开发/2026-08-19-Flutter-CloudFiles与文件预览依赖边界重构-US-CFR-004.md` |
| US-CFR-005 | 作为终端用户，我能预览/下载云盘与 Workspace 文件，且预览实现留在 App、Feature 只经 typed port 发意图，以便平台行为与取消/失败恢复不变 | CFR-005 | AC-05, AC-07 | ADR-CFR-004 | US-CFR-003, US-CFR-004 | P0 | 5 | false | `Plans/功能开发/2026-08-19-Flutter-CloudFiles与文件预览依赖边界重构-US-CFR-005.md` |
| US-CFR-006 | 作为 Flutter 维护者，我能把 Main/Projects/Download 等旧消费者迁到 App 内部能力并闭合运行时生命周期，以便旧大 Runtime 暴露面可安全收窄 | CFR-006 | AC-07, AC-08, AC-09 | ADR-CFR-003, ADR-CFR-005, ADR-CFR-006 | US-CFR-003, US-CFR-004, US-CFR-005 | P0 | 5 | false | `Plans/功能开发/2026-08-19-Flutter-CloudFiles与文件预览依赖边界重构-US-CFR-006.md` |
| US-CFR-007 | 作为后续开发者，我能读到"App composition 模块装配、root 只汇聚"的规则并有自动门禁防回退，以便新文件能力有明确装配入口 | CFR-007 | AC-10 | ADR-CFR-001, ADR-CFR-005 | US-CFR-001..006 | P1 | 3 | false | `Plans/功能开发/2026-08-19-Flutter-CloudFiles与文件预览依赖边界重构-US-CFR-007.md` |

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
| AC-05 预览实现留 App、Feature 经 port | US-CFR-005 |
| AC-06 owner 切换与迟到结果隔离 | US-CFR-001（基线）、US-CFR-003（拆分后不变） |
| AC-07 协议/签名/namespace/持久化/UI 不变 | US-CFR-005（预览）、US-CFR-006（全量 diff） |
| AC-08 Provider 生命周期无重复创建/释放 | US-CFR-001（基线）、US-CFR-006（闭合） |
| AC-09 旧生产消费者迁移落点关闭 | US-CFR-006 |
| AC-10 文档不再暗示 Provider 写进单一根文件 | US-CFR-007 |

## 三、当前进度快照（2026-08-20）

- 已有 CloudFiles/文件预览生产基线已完成：统一 Preview Planner/Coordinator/Launcher/Source、CloudFiles 三类文件、双端宿主预览、上传/下载/分享与多格式预览均有对应提交和测试。
- 上述成果是本轮“无产品行为变化”的重构基线，不等于 US-CFR-001..007 已完成。
- 当前滚动 Scope 为 **US-CFR-001**，正在进入实现落点设计；现状违规锚点已经识别，但 `.impl.json` 和本 Epic 专属 Red/Green 证据尚未生成。
- US-CFR-002..007 仍按依赖顺序等待；逐故事 TDD、集成测试计划审核和全量集成测试尚未开始。
- 当前最严重待办：完成 US-CFR-001 实现落点 JSON，明确源码证据、测试文件、已知 Red 基线与 owner/lifecycle 绿基线，再通过 implementation-design 门禁。

## 四、实现落点设计（当前阶段）

每个 Scope Story 进入 TDD 前必须先完成代码落点设计：Story 子 Plan frontmatter 写 `implementation_design:`，JSON 明确代码证据、目标文件、分层边界、依赖方向和 Red 测试位置。

门禁：`python3 scripts/validate-client-dev.py implementation-design --plan Plans/功能开发/2026-08-19-Flutter-CloudFiles与文件预览依赖边界重构.md`

| Story ID | 落点设计 | 状态 |
|----------|----------|------|
| US-CFR-001 | `…-US-CFR-001.impl.json` | 进行中（待创建） |
| US-CFR-002 | `…-US-CFR-002.impl.json` | 待设计 |
| US-CFR-003 | `…-US-CFR-003.impl.json` | 待设计 |
| US-CFR-004 | `…-US-CFR-004.impl.json` | 待设计 |
| US-CFR-005 | `…-US-CFR-005.impl.json` | 待设计 |
| US-CFR-006 | `…-US-CFR-006.impl.json` | 待设计 |
| US-CFR-007 | `…-US-CFR-007.impl.json` | 待设计 |

## 五、故事内部 TDD

每个故事独立执行：

```text
Red → Green → Refactor → integration smoke → 故事验收
```

边界测试、Runtime 字段测试、owner fencing 回归、生命周期测试、UI/Widget 回归都是故事内部实现步骤，不作为横向交付故事。证据写入各故事 `tdd_evidence` JSON。重构约束：任一故事若使生产行为回归，回滚该结构提交而非改协议/清缓存，状态保持 PARTIAL。

## 六、完成门禁

- [x] 所有 Scope 故事有团队确认的故事点（`estimate_confirmed`）
- [ ] 所有 Scope 故事通过逐故事 TDD 门禁（Red/Green/Refactor/smoke/AC）
- [ ] 进入 `integration-test-plan`，产出结构化用例并经测试人员审核
- [ ] 审核通过后进入全量 `integration-test`

全量集成测试通过后直接 Done；本流程不含发布、灰度或线上观察。

## 七、待确认项

- 无阻断项。故事结构、依赖顺序与故事点已由用户于 2026-08-20 按提议确认。

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

## 续做

```text
/resume plan=Plans/功能开发/2026-08-19-Flutter-CloudFiles与文件预览依赖边界重构.md 进度=实现落点设计（US-CFR-001）
```
