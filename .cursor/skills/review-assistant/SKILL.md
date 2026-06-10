---
name: review-assistant
description: 月度复盘助理。当用户说"复盘"并提供时间段时，汇总 Plans/ 和 Contexts/ 笔记，分类顺利/踩坑任务并输出改进行动。触发词：复盘、月度总结、本月回顾。
---

# 复盘助理

## 步骤

1. 搜索 `Plans/` 和 `Contexts/` 中该时段笔记（文件名日期或内容）。
2. 与用户提供的任务清单交叉核对。
3. 分类：顺利任务（AI 有效）/ 踩坑任务（AI 添乱或无效）。
4. 统计：续做次数、模板使用、材料复用（用户提供的或从笔记推断）。
5. 输出：适合 AI 的场景 + 需谨慎场景 + 至少 3 条改进行动。

## 输出格式

见 `Templates/月度复盘模板.md` 手动填写区，或 `Skills/review_assistant.md`。

材料不足时，请用户列出 5-10 个主要任务并标注 AI 使用情况。

同步维护：`Skills/review_assistant.md`
