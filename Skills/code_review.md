# 代码审查 Skill

> 从 `review-assistant` 拆分而来（单一职责：只做代码审查）。日报/周报/复盘见 `report_assistant.md`。

## 触发条件

当输入是 diff / PR / 分支，或用户说以下任一时执行：

- 「Code Review」「review 这个 diff」「审查 PR」「UI 复核」「回归复核」
- workflow 的 review 阶段
- `/code-review` / `/review` 命令

**不响应（让位给其他 Skill）**：

- 「日报 / 周报 / 项目复盘 / 月度复盘」→ `report-assistant`
- 「考我 / 知识复盘 / 复习课程」→ `learn-assistant`
- 「审计 Epic / 检查开发流程」→ `dev-lifecycle-audit-assistant`

## 输出规则（Findings-first）

写入 `Plans/代码重构/` 或调用方 plan：

1. Findings first：问题列表在前，摘要在后。
2. 按严重级排序：阻塞 / 高 / 中 / 建议。
3. 每个问题尽量给文件和行号；无法定位时说明证据来源。
4. 没发现问题也要明确说“未发现阻塞问题”，并补充测试缺口或残余风险。
5. 不使用日报、周报、项目复盘模板。

模板：`Templates/Code-Review模板.md`

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

## 反馈

`utility` 只能是 `high` 或 `not-needed`。有调用方 plan 时追加到 plan 末尾，否则追加到 `Contexts/决策/孤立反馈记录.md` 顶部；协议见 `Contexts/决策/Skill反馈协议.md`。
