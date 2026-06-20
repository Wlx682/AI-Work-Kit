---
name: resume-assistant
description: 续做任意 plan。标准命令 /resume plan=Plans/... 进度=...。触发词：续做、/resume。
---

# 续做助手

解析 `/resume plan=Plans/相对路径 进度=...` → 读 plan → 输出已完成/下一步/验证。

1. 若 plan 含 `epic:`，先读 Epic 母 plan（WBS + lifecycle_state）。
2. 对 `Plans/功能开发/` plan，开发阶段先跑 `bash scripts/plan-gate-check.sh <plan> --stage development`；`BLOCKED` 时只建议补文档。
3. 按 lifecycle_state 推荐 Skill（requirement → architecture → development → test → deploy）。

兼容 `续做，plan=分类/文件.md，进度=...`

同步：`Skills/resume_assistant.md`
