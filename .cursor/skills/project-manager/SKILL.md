---
name: project-manager
description: >-
  trigger: internal_only — 状态机与编排说明，不对用户暴露自然语言触发。
  历史编排草案，仅显式 /project-manager 救急。
  用户说全流程/启动项目一律路由 full-cycle 引擎。
---

# 项目经理 Skill（长期 / Agent 化）

> **trigger: internal_only** — 本 Skill **不对用户直接暴露**自然语言触发词；仅显式 `/project-manager` 命令救急。新流程以 `full-cycle` 引擎 + 蓝图 manifest 为准。
>
> **执行入口已迁移至 `full-cycle` 引擎**（开场自动 boot 看板）。本文仅作历史编排草案参考。

所有「全流程开发 / 帮我开发 XX 模块 / 启动项目」类用户输入 → **一律路由到** `workflow-router`，由 `.workflows/blueprints/*.json` 选择工作流；本 Skill 不响应。

> **目标态**：用户一句话，AI 按 Workflow 自动串联各阶段 Skill；遇阻塞写入 `Plans/阻塞问题/` 并在 `Contexts/` 记录决策。

## 状态机（与 full-cycle workflow 对齐）

```
Requirement → Architecture → Development → Test → Deploy
     ↑_______________|（变更 / Bugfix 回流）
```

## 自动编排逻辑

1. **Requirement**：若无 `Plans/需求分析/` → 调用 `requirement-analyst`（带验收标准模板）
2. **Architecture**：P0 闭环 → `architecture-design-assistant`
3. **Development**：方案已采纳 → `task-splitter` → 逐子任务 `feature-dev-assistant` / `/resume`
4. **Test**：开发完成 → `test-generator`
5. **Deploy**：测试通过 → `deployment-assistant`
6. **阻塞**：无法自动决策 → `Plans/阻塞问题/YYYY-MM-DD-简述.md` + 询问用户

## 每步必输出（上下文汇报）

```
📌 当前阶段：[阶段名] | 正在执行：[Skill名] | 下一个阶段：[...] | 如需中断：/resume plan=xxx
```

同步：`Skills/project_manager.md`

## 反馈回路（skill_run）

完成任务的最后一步**必须**输出 `skill_run` 反馈（协议：`Contexts/决策/Skill反馈协议.md`）：
本 Skill internal_only、不直接对用户执行（救急场景无 plan 时），故追加到 `Contexts/决策/孤立反馈记录.md` **顶部**（倒序，`plan: orphan`）。
`contexts_used[].utility` 二选一：`high`（附一句话 `reason`）或 `not-needed`；必填 `skill: project-manager` / `plan` / `date` / `contexts_used` / `contexts_missing` / `contexts_stale`。喂 `feedback-aggregate → vault-evolve` 进化链。
