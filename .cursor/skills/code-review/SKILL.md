---
name: code-review
description: >-
  代码审查（Findings-first）。触发：Code Review、review 这个 diff、审查 PR、UI 复核、回归复核，或 workflow review 阶段；/code-review、/review。
  不响应：日报/周报/复盘→report-assistant；Epic 审计→dev-lifecycle-audit-assistant。
  产出：Findings-first 审查结论，写入 Plans/代码重构/ 或调用方 plan。
---

# 代码审查助手

Vault：AI-Work-Kit 根目录

## 触发条件

当输入是 diff / PR / 分支，或用户说以下任一时执行：

- 「Code Review」「review 这个 diff」「审查 PR」「UI 复核」「回归复核」
- workflow 的 review 阶段
- `/code-review` / `/review` 命令

**不响应（让位给其他 Skill）**：

- 「日报 / 周报 / 项目复盘 / 月度复盘」→ `report-assistant`
- 「审计 Epic / 检查开发流程」→ `dev-lifecycle-audit-assistant`

模板：`Templates/Code-Review模板.md`
契约：`Contexts/决策/Skill原子契约.md`
同步：`Skills/code_review.md`

## 输出规则（Findings-first）

写入 `Plans/代码重构/` 或调用方 plan：

1. Findings first：问题列表在前，摘要在后。
2. 按严重级排序：阻塞 / 高 / 中 / 建议。
3. 每个问题尽量给文件和行号；无法定位时说明证据来源。
4. 没发现问题也要明确说“未发现阻塞问题”，并补充测试缺口或残余风险。
5. 不使用日报、周报、项目复盘模板。

## `merge-code` 复核附加规则

当调用方是 `merge-code` 的 `review` 阶段时，先读取同一任务的 `合并意图分析` 与 `代码合并` plan，再审查最终 diff。除通用检查外，必须逐项确认：

1. 源分支和目标分支的每个意图在最终代码中都能找到，任何被舍弃或改变的意图都有开发者决策依据。
2. `业务冲突矩阵` 中每个冲突 ID、`开发者决策清单` 中每个决策 ID，都能追到 `决策落实记录` 的具体文件与验证用例。
3. 实现没有偏离开发者结论；AI 不能在合并阶段自行改变已确认的业务选择。
4. 不只看两边原有测试，还要检查跨模块组合场景、状态转换、数据/API 契约、副作用、幂等并发、迁移及回滚。
5. 发现新业务冲突、未落实决策、缺组合验证或无法证明两边意图同时成立时，按“阻塞”输出，并退回 `intent-analysis` 或 `merge`，不得给出通过结论。

Smoke test：

```bash
python3 scripts/skill-smoke-test.py code-review tests/fixtures/skills/code-review/risky-diff.input.md
```

## 原子契约

| 字段 | 要求 |
|------|------|
| 输入 | diff、PR、分支、审查范围 |
| 输出 | Findings-first review 结论（写入 `Plans/代码重构/` 或调用方 plan） |
| 门禁 | 有严重级、文件/行号、测试缺口/残余风险 |
| 越界 | 需要实现修复时转功能开发或 bugfix 流程 |
| smoke | `python3 scripts/skill-smoke-test.py code-review tests/fixtures/skills/code-review/risky-diff.input.md` |

## 反馈回路（skill_run）

完成任务的最后一步按 `Contexts/决策/Skill反馈协议.md` 收口：
有调用方 plan 时追加到 plan 末尾；无 plan 时只写孤立反馈的 `## 待整理` 或 `## 已归位`，不保留完整过程小票。
`contexts_used[].utility` 二选一：`high`（附一句话 `reason`）或 `not-needed`；必填 `skill: code-review` / `plan` / `date` / `contexts_used` / `contexts_missing` / `contexts_stale`。
