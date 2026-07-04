---
skill: learning-audit-assistant
case: llm-route-audit
---

# Learning Audit Assistant Smoke Input

## 输入

- 请审计 Plans/学习/ 下 LLM 学习路线的真实完成度。
- 第 3 课 frontmatter 标 status: 已完成，但步骤复选框 0 勾选、无本课笔记。
- 第 1 课 status: 进行中，勾选与笔记证据相符。
- 概念卡在 学习/概念/ 下存在。

## 要求

- 按四类证据（声称状态/步骤勾选/概念卡/学习笔记）交叉比对。
- 每课给出一致性 verdict，写入审计报告。
- 交叉引用的笔记不算作本课笔记。
