---
name: change-impact-analysis
description: >-
  需求变更影响分析（口语优先）。口语：需求变了、改个东西、Scope调整、临时改一下、这个不做了/加一个、PRD又改了。
  正式：需求变更、改scope、变更影响；/change-impact-analysis。
  不响应：Epic审计→dev-lifecycle-audit；全新需求→requirement-analyst。
---

# 变更影响分析

## 触发条件（口语前置）

当用户说以下任一时执行 —— 口语化说法优先匹配：

- **口语优先**：「**需求变了**」「**改个东西**」「**Scope 调整**」「**临时改一下**」「**这个不做了 / 加一个**」「**PRD 又改了**」
- **正式词**：「需求变更」「改 scope」「变更影响」「变更影响分析」
- `/change-impact-analysis` 命令

**不响应（让位给其他 Skill）**：

- 「开发流程审计 / 检查 Epic 进度」→ `dev-lifecycle-audit-assistant`
- 「重新做需求分析（全新需求）」→ `requirement-analyst`
- 「重新设计架构（方案级重写）」→ `architecture-design-assistant`

扫描：技术方案、功能开发、自动化测试、部署 plan（双链/grep）

1. 输出影响报告：哪些 plan/代码/测试需重写  
2. 用户确认后：`status: pending-change`  
3. P0 变更 → 回需求/架构；小改 → `/resume` 子任务

同步：`Skills/change_impact_analysis.md`

## 反馈回路（skill_run）

完成任务的最后一步**必须**输出 `skill_run` 反馈（协议：`Contexts/决策/Skill反馈协议.md`）：
本 Skill 产出影响报告而非独立 plan（无对应 plan 时），故追加到 `Contexts/决策/孤立反馈记录.md` **顶部**（倒序，`plan: orphan`）。
`contexts_used[].utility` 二选一：`high`（附一句话 `reason`）或 `not-needed`；必填 `skill: change-impact-analysis` / `plan` / `date` / `contexts_used` / `contexts_missing` / `contexts_stale`。喂 `feedback-aggregate → vault-evolve` 进化链。
