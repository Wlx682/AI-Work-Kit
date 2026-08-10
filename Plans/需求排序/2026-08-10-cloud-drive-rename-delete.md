---
tags: [需求排序, Backlog, 敏捷]
type: plan
category: 需求排序
status: 已采纳
date: 2026-08-10
lifecycle_state: prioritization
epic: Plans/Epic/2026-08-10-cloud-drive-rename-delete.md
requirement_plan: Plans/需求分析/2026-08-10-cloud-drive-rename-delete.md
backlog_index: Plans/需求排序/2026-08-10-cloud-drive-rename-delete.backlog.json
relations:
  depends_on:
    - Plans/需求分析/2026-08-10-cloud-drive-rename-delete.md
    - Templates/模板约定.md
  dependents:
    - Templates/Epic模板-client-dev.md
  supersedes: []
  superseded_by: []
  conflicts: []

---
# 需求排序：cloud-drive-rename-delete

## 排序原则

- 价值、紧迫度、风险验证价值、前置依赖分别记录；故事点不在本阶段填写。
- AI 给建议，团队确认后 `confirmed: true` 才成为门禁事实。

## 需求排序

| 需求 ID | 标题 | 业务价值 | 紧迫度 | 依赖 | 初始优先级 | 排序依据 | 已确认 |
|---------|------|----------|--------|------|------------|----------|--------|
| BUS-052 | 个人云盘文件重命名 | high | high | 已有个人云盘浏览底座 | P0 | 先用可逆的单项目 mutation 落实名称校验、单飞、owner fence、结果未知对账和分页/搜索失效 | true |
| BUS-054 | 个人云盘文件永久删除 | high | high | BUS-052 共享 mutation 结果收敛与失效机制 | P0 | 删除不可恢复，复用已验证机制后再接入危险确认，降低一致性风险 | true |

对应 JSON 索引：`backlog_index`。字段契约由 `scripts/validate-client-dev.py backlog` 校验。

## 团队确认

- [x] 用户已要求继续迁移文件 Tab，并以前序看板分配确认本轮范围
- [x] 开发依赖已核对：两项均依赖现有个人云盘浏览底座
- [x] 本轮排序已确认：先重命名、后永久删除

## 续做

```text
/resume plan=Plans/需求排序/2026-08-10-cloud-drive-rename-delete.md 进度=排序已采纳，进入架构设计
```

## 反馈（skill_run）

```yaml
skill_run:
  skill: backlog-prioritization-assistant
  workflow_stage: prioritization
  plan: Plans/需求排序/2026-08-10-cloud-drive-rename-delete.md
  date: 2026-08-10
  contexts_used:
    - path: Contexts/需求分析/需求分析产出标准.md
      utility: high
      reason: "确认需求已采纳、P0 清零且验收边界足以进入有序 Backlog"
  contexts_missing: []
  contexts_stale: []
  outcome_status: pass
  revisit_needed: false
```
