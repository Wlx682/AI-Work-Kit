---
name: resume-assistant
description: 续做任意 plan。标准命令 /resume plan=Plans/... 进度=...。触发词：续做、/resume。
---

# 续做助手

解析 `/resume plan=Plans/相对路径 进度=...` → 读 plan → 输出已完成/下一步/验证。

1. 若 plan 含 `epic:`，先读 Epic 母 plan（workflow + plans 子 Plan 索引）；再跑 `scripts/workflow-gate.sh --workflow <name> --epic <epic>` 派生当前阶段。
2. **回放优先**：跑 `python3 scripts/workflow-status.py --workflow <name> --epic <epic>` 从事件流读门禁历史（最近门禁 pass/fail + 原因、连续判不过告警）；答「上次为何卡住」先读历史，别只凭当前快照猜。
3. 对 `Plans/功能开发/` plan，开发阶段先跑 `bash scripts/plan-gate-check.sh <plan> --stage development`；`BLOCKED` 时只建议补文档。
4. 按 `workflow-gate.sh` 的 `recommended_skill` 推荐下一步；`story-split` 走 `task-splitter`，`implementation-design` 走 `implementation-design-assistant`，`story-development` 读 `.stories.json` 中尚未完成的 Scope Story、Story 子 Plan、`implementation_design` 与 `tdd_evidence`。
5. 用户要改故事拆分、故事点或 Scope → 路由 `task-splitter` 或列待确认项；禁止擅自推荐 A/B/C 方案。

兼容 `续做，plan=分类/文件.md，进度=...`

同步：`Skills/resume_assistant.md`

## 反馈回路（skill_run）

完成任务的最后一步**必须**输出 `skill_run` 反馈（协议：`Contexts/决策/Skill反馈协议.md`）：
追加到本次 续做的目标 plan **末尾**的 `## 反馈（skill_run）` 节（fenced ```yaml`，非裸 frontmatter）。
`contexts_used[].utility` 二选一：`high`（附一句话 `reason`）或 `not-needed`；必填 `skill: resume-assistant` / `plan` / `date` / `contexts_used` / `contexts_missing` / `contexts_stale`。缺则 `plan-gate-check.sh` 报失败。
