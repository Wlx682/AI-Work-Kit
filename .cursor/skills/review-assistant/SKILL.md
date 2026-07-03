---
name: review-assistant
description: >-
  日报/周报/项目复盘。日报类：日报、周报、今日/本周总结；复盘类：项目复盘、迭代回顾、月度复盘、本月回顾；/review、/review-assistant。
  不响应：考我/知识复盘→learn-assistant；Epic审计→dev-lifecycle-audit-assistant。
  日报→Contexts/日报/；周报→Contexts/周报/；Code Review→Findings-first。
---

# 复盘助理

Vault：AI-Work-Kit 根目录

## 触发条件

当用户说以下任一时执行：

- **日报 / 周报类**：「日报」「周报」「今日总结」「本周总结」「整理今天/这周的工作」
- **项目复盘类**：「**项目复盘**」「**迭代回顾**」「**月度复盘**」「**本月回顾**」
- **代码审查类**：「Code Review」「review 这个 diff」「审查 PR」「UI 复核」「回归复核」或 workflow review 阶段
- `/review-assistant` / `/review` 命令

**不响应（让位给其他 Skill）**：

- 「考我 / 知识复盘 / 复习课程」→ `learn-assistant`（学习场景的「复盘」）
- 「审计 Epic / 检查开发流程」→ `dev-lifecycle-audit-assistant`

| 模式 | 写入 |
|------|------|
| 日报 | `Contexts/日报/`；git 仅本人；**正文不写规则/元信息** |
| 周报 | `Contexts/周报/`；汇总日报 + 本人 git |
| 月度 | `Contexts/复盘/YYYY-MM.md` |
| Code Review | `Plans/代码重构/` 或调用方 plan；Findings-first，不写日报口径 |

模板：`Templates/日报模板.md` · `Templates/周报模板.md` · `Templates/月度复盘模板.md`
代码审查模板：`Templates/Code-Review模板.md`
契约：`Contexts/决策/Skill原子契约.md`

同步：`Skills/review_assistant.md`

## Code Review 模式

当输入是 diff / PR / 分支 / workflow review 阶段时，按代码审查模式输出：

1. Findings first：问题列表在前，摘要在后。
2. 按严重级排序：阻塞 / 高 / 中 / 建议。
3. 每个问题尽量给文件和行号；无法定位时说明证据来源。
4. 没发现问题也要明确说“未发现阻塞问题”，并补充测试缺口或残余风险。
5. 不使用日报、周报、项目复盘模板。

Smoke test：

```bash
python3 scripts/skill-smoke-test.py review-assistant tests/fixtures/skills/review-assistant/risky-diff.input.md
```

## 原子契约

| 字段 | 要求 |
|------|------|
| 输入 | diff、PR、分支、审查范围；或日报/周报材料 |
| 输出 | Findings-first review 结论；或日报/周报/复盘文件 |
| 门禁 | 代码审查有严重级、文件/行号、测试风险；日报周报正文不含元信息 |
| 越界 | 需要实现修复时转功能开发或 bugfix 流程 |
| smoke | `python3 scripts/skill-smoke-test.py review-assistant tests/fixtures/skills/review-assistant/risky-diff.input.md` |

## 反馈回路（skill_run）

完成任务的最后一步**必须**输出 `skill_run` 反馈（协议：`Contexts/决策/Skill反馈协议.md`）：
本 Skill 产出日报/周报/复盘（`Contexts/`）而非 plan，故追加到 `Contexts/决策/孤立反馈记录.md` **顶部**（倒序，`plan: orphan`）。
`contexts_used[].utility` 二选一：`high`（附一句话 `reason`）或 `not-needed`；必填 `skill: review-assistant` / `plan` / `date` / `contexts_used` / `contexts_missing` / `contexts_stale`。喂 `feedback-aggregate → vault-evolve` 进化链。
