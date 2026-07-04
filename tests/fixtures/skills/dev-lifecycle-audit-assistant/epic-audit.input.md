---
skill: dev-lifecycle-audit-assistant
case: epic-audit
---

# Dev Lifecycle Audit Assistant Smoke Input

## 输入

- 请审计 Plans/Epic/ 下试点 Epic 的阶段真实性。
- Epic 声称 lifecycle_state: development，但 plan-gate-check 返回 BLOCKED。
- 需求 plan 存在但技术方案 plan 缺 status: 已采纳。
- WBS 计数 wbs_done_total 与 lifecycle_state 不符。

## 要求

- 按五维度 A–E（Epic 元信息/需求/方案/WBS/测试部署）交叉比对。
- 给出每个 Epic 的 verdict 与最严重待办，写入审计报告。
- 以文件系统机械证据为准，不凭 frontmatter 声称下结论。
