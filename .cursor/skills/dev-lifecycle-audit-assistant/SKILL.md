---
name: dev-lifecycle-audit-assistant
description: >-
  审计 Epic 声称阶段 vs 子plan/WBS/门禁证据。正式词：开发流程审计、Epic审计、dev-lifecycle-audit。
  口语：检查Epic进度、审计版本状态、这个需求做完了吗、这个版本做的咋样了、真不真实；/dev-lifecycle-audit。
  不响应：日报周报→review-assistant；学习审计→learning-audit-assistant。
---

# 开发流程审计

## 触发条件

当用户说以下任一时执行 —— 包含口语化变体，PM 日常说法即可：

- **正式词**：「开发流程审计」「Epic 审计」「dev-lifecycle-audit」「检查 Epic 进度真实性」
- **口语变体**：「**检查 Epic 进度**」「**审计版本状态**」「**这个 Epic 做完了吗**」「**这个需求做完了吗**」「**这个版本做的咋样了**」「**真不真实**」
- `/dev-lifecycle-audit` 命令

**不响应（让位给其他 Skill）**：

- 「日报 / 周报 / 项目复盘」→ `review-assistant`
- 「学习进度审计」→ `learning-audit-assistant`
- 「需求变更影响」→ `change-impact-analysis`

## 执行

1. `./scripts/dev-lifecycle-audit-collect.sh Plans/Epic`
2. 五维度 A–E 交叉比对（见 `Skills/dev_lifecycle_audit_assistant.md`）
3. **写入** `Contexts/决策/YYYY-MM-DD-开发流程审计报告.md`
4. 回复路径 + summary + Epic 待办

同步：`Skills/dev_lifecycle_audit_assistant.md`
