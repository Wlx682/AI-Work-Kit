---
name: learning-audit-assistant
description: 审计 Plans/学习 声称状态 vs 复选框/概念卡/笔记证据，写审计报告。触发词：审计学习进度、learning-audit、学习审计、检查学习完成度。
---

# 学习进度审计

对齐 Claude Code workflow：`.claude/workflows/learning-audit.js`

## 执行

1. 运行 `./scripts/learning-audit-collect.sh Plans/学习` 获取 status 与复选框计数。
2. 对 `Plans/学习/` 每课 **分别** 读 plan：双链概念卡、练习是否填写、笔记是否存在（交叉引用不算）。
3. 按 `Skills/learning_audit_assistant.md` 的 verdict 规则判定每课一致性。
4. **写入** `Contexts/LLM学习/笔记/YYYY-MM-DD-学习进度审计报告.md`（结构见 Skill 全文）。
5. 回复：路径 + 一句话 summary。

## verdict

- 已完成 + 0 勾选或无本课笔记 → 严重矛盾
- 进行中/未开始 + 证据相符 → 一致
- 其余 → 轻微偏差

同步：`Skills/learning_audit_assistant.md`

## 反馈回路（skill_run）

完成任务的最后一步**必须**输出 `skill_run` 反馈（协议：`Contexts/决策/Skill反馈协议.md`）：
本 Skill 产出审计报告（`Contexts/LLM学习/笔记/`）而非 plan，故追加到 `Contexts/决策/孤立反馈记录.md` **顶部**（倒序，`plan: orphan`）。
`contexts_used[].utility` 二选一：`high`（附一句话 `reason`）或 `not-needed`；必填 `skill: learning-audit-assistant` / `plan` / `date` / `contexts_used` / `contexts_missing` / `contexts_stale`。喂 `feedback-aggregate → vault-evolve` 进化链。
