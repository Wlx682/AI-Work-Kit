---
name: project-manager
description: >-
  项目经理状态机与全流程编排说明（需求→架构→开发→测试→部署，含变更/Bugfix 回流）。
  执行入口已迁移至 full-cycle-assistant；本 Skill 仅做阶段推荐 + 手动确认，不全自动写代码。
  触发词：项目经理、/project-manager、阶段推荐、状态机、编排说明。
---

# 项目经理 Skill（长期 / Agent 化）

> **执行入口已迁移至 `full-cycle-assistant`**（开场自动 boot 看板）。本文保留状态机与编排说明。

当用户说「帮我开发 XX 模块」「全流程开发」「/project-manager」时，**优先** `@Skills/full_cycle_assistant.md` 或 `.cursor/skills/full-cycle-assistant/`。

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

## 前置条件（当前为草案 Skill）

- P0 资产就绪：`architecture-design-assistant`、`task-splitter`、`test-generator`、`deployment-assistant`
- Workflow：`.claude/workflows/full-cycle.js`
- 至少 1 次 P2 小功能全流程试点通过

## 触发示例

```
/project-manager 帮我开发支付模块，PRD=【飞书链接】，平台=服务端
```

**注意**：在试点完成前，本 Skill 仅做**阶段推荐 + 手动确认**，不全自动写代码。

---

同步：`Skills/project_manager.md`
