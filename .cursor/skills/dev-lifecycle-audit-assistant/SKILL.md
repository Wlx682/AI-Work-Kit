---
name: dev-lifecycle-audit-assistant
description: 审计 Plans/Epic 声称阶段 vs 子 plan/WBS/门禁证据，写开发流程审计报告。触发词：开发流程审计、Epic审计、dev-lifecycle-audit。
---

# 开发流程审计

对齐 Claude workflow：`.claude/workflows/dev-lifecycle-audit.js`

## 执行

1. `./scripts/dev-lifecycle-audit-collect.sh Plans/Epic`
2. 五维度 A–E 交叉比对（见 `Skills/dev_lifecycle_audit_assistant.md`）
3. **写入** `Contexts/决策/YYYY-MM-DD-开发流程审计报告.md`
4. 回复路径 + summary + Epic 待办

同步：`Skills/dev_lifecycle_audit_assistant.md`
