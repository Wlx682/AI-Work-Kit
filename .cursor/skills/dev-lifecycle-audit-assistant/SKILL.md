---
name: dev-lifecycle-audit-assistant
description: >-
  审计 Epic 声称阶段 vs 子plan/Story/Scope/门禁证据。正式词：开发流程审计、Epic审计、dev-lifecycle-audit。
  口语：检查Epic进度、审计版本状态、这个需求做完了吗、这个版本做的咋样了、真不真实；/dev-lifecycle-audit。
  不响应：日报周报→report-assistant；需求变更影响→change-impact-analysis。
---

# 开发流程审计

## 触发条件

当用户说以下任一时执行 —— 包含口语化变体，PM 日常说法即可：

- **正式词**：「开发流程审计」「Epic 审计」「dev-lifecycle-audit」「检查 Epic 进度真实性」
- **口语变体**：「**检查 Epic 进度**」「**审计版本状态**」「**这个 Epic 做完了吗**」「**这个需求做完了吗**」「**这个版本做的咋样了**」「**真不真实**」
- `/dev-lifecycle-audit` 命令

**不响应（让位给其他 Skill）**：

- 「日报 / 周报 / 项目复盘」→ `report-assistant`
- 「需求变更影响」→ `change-impact-analysis`

## 执行

1. `./scripts/dev-lifecycle-audit-collect.sh Plans/Epic`
2. 五维度 A–E 交叉比对（见 `Skills/dev_lifecycle_audit_assistant.md`）；测试维度必须区分 `integration-test-plan` 的用例审核证据与 `integration-test` 的执行报告，执行不得绕过审核或引用漂移版本
3. **写入** `Contexts/决策/YYYY-MM-DD-开发流程审计报告.md`
4. 回复路径 + summary + Epic 待办

同步：`Skills/dev_lifecycle_audit_assistant.md`

## 反馈回路（skill_run）

完成任务的最后一步按 `Contexts/决策/Skill反馈协议.md` 收口：
本 Skill 产出审计报告（`Contexts/决策/`）而非 plan；未归位候选写入孤立反馈 `## 待整理`，已归位结论只写 `## 已归位` 摘要，不保留完整过程小票。
`contexts_used[].utility` 二选一：`high`（附一句话 `reason`）或 `not-needed`；必填 `skill: dev-lifecycle-audit-assistant` / `plan` / `date` / `contexts_used` / `contexts_missing` / `contexts_stale`。喂 `feedback-aggregate → vault-evolve` 进化链。
