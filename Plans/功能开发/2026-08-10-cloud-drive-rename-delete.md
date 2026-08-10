---
tags: [功能开发, 用户故事, 故事点, 敏捷]
type: plan
category: 功能开发
status: 已采纳
date: 2026-08-10
lifecycle_state: story-split
epic: Plans/Epic/2026-08-10-cloud-drive-rename-delete.md
requirement_plan: Plans/需求分析/2026-08-10-cloud-drive-rename-delete.md
architecture_plan: Plans/技术方案/2026-08-10-cloud-drive-rename-delete.md
story_index: Plans/功能开发/2026-08-10-cloud-drive-rename-delete.stories.json
relations:
  depends_on:
    - Plans/需求分析/2026-08-10-cloud-drive-rename-delete.md
    - Plans/需求排序/2026-08-10-cloud-drive-rename-delete.md
    - Plans/技术方案/2026-08-10-cloud-drive-rename-delete.md
    - Templates/模板约定.md
    - Templates/客户端功能开发模板.md
  dependents:
    - Templates/客户端功能开发模板.md
  supersedes: []
  superseded_by: []
  conflicts: []

---
# 用户故事拆分：cloud-drive-rename-delete

## 一、输入门禁

- 需求排序：`Plans/需求排序/2026-08-10-cloud-drive-rename-delete.md`，已采纳。
- 架构方案：`Plans/技术方案/2026-08-10-cloud-drive-rename-delete.md`，已采纳。

## 二、纵向故事索引

| Story ID | 用户能力 | AC | 架构引用 | 依赖 | 优先级 | 故事点 | Scope | 子 Plan |
|----------|----------|----|----------|------|--------|--------|-------|---------|
| US-001 | 用户可安全重命名当前个人云盘项目 | GWT-001..009,015..018 | ADR-002/003/004/005 | 已有浏览底座 | P0 | 8 | true | `Plans/功能开发/2026-08-10-cloud-drive-rename-delete-US-001.md` |
| US-002 | 用户确认后可永久删除当前个人云盘项目 | GWT-010..018 | ADR-001/002/003/004 | US-001 | P0 | 5 | true | `Plans/功能开发/2026-08-10-cloud-drive-rename-delete-US-002.md` |

JSON 真理源：`story_index`。每个故事必须 `vertical_slice: true`，故事点限 `1/2/3/5/8/13`；13 点进入 Scope 前须继续拆分或留下团队确认的豁免。

## 三、拆分规则

- 一个故事交付一个可演示、可验收的用户能力。
- UI、Domain、Data/API 和测试是故事内部步骤，不作为横向交付故事。
- 共享底座归入首个消费故事，或标记为有明确消费者的 enabler。
- 禁止 `estimated_hours` 等故事点换工时字段。

## 四、Scope 确认

- [x] 所有 P0 AC 至少由一个 Scope 故事覆盖
- [x] 用户已要求继续迁移文件 Tab，本轮两个已分配能力均进入 Scope
- [x] 故事点按不确定性确认：重命名 8，永久删除 5；不换算工时
- [x] 无 13 点故事
- [x] `scope_confirmed: true`

## 实现落点设计

| Story | 设计文件 | 代码落点摘要 | Red 测试位置 | 状态 |
|---|---|---|---|---|
| US-001 | `Plans/功能开发/2026-08-10-cloud-drive-rename-delete-US-001.impl.json` | core rename 契约 + rename 四层 + runtime/browser/l10n 接线 | rename controller/dialog、personal cloud client、adapter | 已确认 |
| US-002 | `Plans/功能开发/2026-08-10-cloud-drive-rename-delete-US-002.impl.json` | core permanentDelete 契约 + deletion 四层 + runtime/browser/l10n 接线 | deletion controller/dialog、personal cloud client、adapter | 已确认 |

依赖方向固定为 Browser intent → Feature Presentation → Application → Domain Repository → Data Adapter → Core client；两个 Feature 不互相 import。共享宿主和 core 契约按 Story 顺序串行接线。

## 续做

```text
/resume plan=Plans/功能开发/2026-08-10-cloud-drive-rename-delete.md 进度=进入implementation-design实现落点设计
```

## 反馈（skill_run）

```yaml
skill_run:
  skill: task-splitter
  workflow_stage: story-split
  plan: Plans/功能开发/2026-08-10-cloud-drive-rename-delete.md
  date: 2026-08-10
  contexts_used:
    - path: Contexts/需求分析/需求分析产出标准.md
      utility: high
      reason: "确保两个纵向故事覆盖全部 P0 AC、反例和异常恢复"
  contexts_missing: []
  contexts_stale: []
  outcome_status: pass
  revisit_needed: false
```

```yaml
skill_run:
  skill: implementation-design-assistant
  workflow_stage: implementation-design
  plan: Plans/功能开发/2026-08-10-cloud-drive-rename-delete.md
  date: 2026-08-10
  contexts_used:
    - path: Contexts/决策/测试先行原则.md
      utility: high
      reason: "在业务代码前固定两个纵向 Story 的文件落点、依赖方向与 Red 测试命令"
  contexts_missing: []
  contexts_stale: []
  outcome_status: pass
  revisit_needed: false
```
