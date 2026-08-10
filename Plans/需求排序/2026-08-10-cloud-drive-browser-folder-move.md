---
tags: [需求排序, Backlog, 云盘]
type: plan
category: 需求排序
status: 已采纳
date: 2026-08-10
lifecycle_state: prioritization
epic: Plans/Epic/2026-08-10-cloud-drive-browser-folder-move.md
requirement_plan: Plans/需求分析/2026-08-10-cloud-drive-browser-folder-move.md
backlog_index: Plans/需求排序/2026-08-10-cloud-drive-browser-folder-move.backlog.json
relations:
  depends_on:
    - Plans/需求分析/2026-08-10-cloud-drive-browser-folder-move.md
  dependents: []
  supersedes: []
  superseded_by: []
  conflicts: []
---

# 需求排序：个人云盘浏览、新建文件夹与移动

## 排序原则

- 先验证个人云盘 provider、owner、目录/搜索/分页真值；新建和移动均依赖这份目录能力。
- 创建用于验证 mutation、名称 policy 与单目录失效；移动再扩展到目标目录选择、非法目标和双目录对账。
- 三张卡都是用户本轮明确选择的 Scope，排序只决定实现顺序，不删除任何 P0 AC。

## 需求排序

| 需求 ID | 标题 | 业务价值 | 紧迫度 | 依赖 | 初始优先级 | 排序依据 | 已确认 |
|---------|------|----------|--------|------|------------|----------|--------|
| BUS-046 | 个人云盘文件浏览 | high | high | Cloud HTTP/owner adapter | P0 | 当前 Flutter provider 语义错误；目录真值是其余两卡共同前置 | true |
| BUS-048 | 新建云盘文件夹 | high | high | BUS-046 的当前目录与失效合同 | P0 | 用较小 mutation 先验证 single-flight、policy 和刷新闭环 | true |
| BUS-053 | 个人云盘文件移动 | high | high | BUS-046 目录选择；BUS-048 可复用弹层内新建 | P0 | 交互和恢复最复杂，需在目录真值稳定后完成 | true |

## 团队确认

- [x] 用户已在看板截图中确认三张任务由王龙祥负责。
- [x] 用户“先按照这个开发”“继续”确认三张卡均在本轮 Scope。
- [x] 依赖顺序与 05/MAP/PRE、iOS 固定源码一致；本阶段未填写故事点或工时。

## 反馈（skill_run）

```yaml
skill_run:
  skill: backlog-prioritization-assistant
  workflow_stage: prioritization
  plan: Plans/需求排序/2026-08-10-cloud-drive-browser-folder-move.md
  date: 2026-08-10
  contexts_used:
    - path: Contexts/需求分析/需求分析规范.md
      utility: high
      reason: "以已闭环的用户事件和依赖确定浏览→创建→移动顺序"
  contexts_missing: []
  contexts_stale: []
  outcome_status: pass
  revisit_needed: false
```
