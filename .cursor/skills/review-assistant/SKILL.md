---
name: review-assistant
description: >-
  日报/周报/项目复盘。日报类：日报、周报、今日/本周总结；复盘类：项目复盘、迭代回顾、月度复盘、本月回顾；/review、/review-assistant。
  不响应：考我/知识复盘→learn-assistant；Epic审计→dev-lifecycle-audit-assistant。
  日报→Contexts/日报/；周报→Contexts/周报/。
---

# 复盘助理

Vault：AI-Work-Kit 根目录

## 触发条件

当用户说以下任一时执行：

- **日报 / 周报类**：「日报」「周报」「今日总结」「本周总结」「整理今天/这周的工作」
- **项目复盘类**：「**项目复盘**」「**迭代回顾**」「**月度复盘**」「**本月回顾**」
- `/review-assistant` / `/review` 命令

**不响应（让位给其他 Skill）**：

- 「考我 / 知识复盘 / 复习课程」→ `learn-assistant`（学习场景的「复盘」）
- 「审计 Epic / 检查开发流程」→ `dev-lifecycle-audit-assistant`

| 模式 | 写入 |
|------|------|
| 日报 | `Contexts/日报/`；git 仅本人；**正文不写规则/元信息** |
| 周报 | `Contexts/周报/`；汇总日报 + 本人 git |
| 月度 | `Contexts/复盘/YYYY-MM.md` |

模板：`Templates/日报模板.md` · `Templates/周报模板.md` · `Templates/月度复盘模板.md`

同步：`Skills/review_assistant.md`
