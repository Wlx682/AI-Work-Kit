---
tags: [学习/概念, skill]
---

# 概念：Skill（技能 / 可复用指令）

> **学习顺序：第 5 课。** 先理解 [[Agent]] 和 [[提示词工程]]。

## 一句话

把**某类任务的成功 prompt + 步骤 + 输出格式**打包，下次一条命令重复用。

## 三层（你的 Kit）

| 层 | 位置 | 谁触发 |
|----|------|--------|
| 人类可读 | `Skills/*.md` | 你 `@` 引用 |
| Agent 自动 | `.cursor/skills/*/SKILL.md` | `/skill` 或触发词 |
| 项目常驻 | `.cursorrules` | 打开 Vault 即生效 |

Obsidian **没有** Skill API；`Skills/` 只是约定好的 markdown。

## SKILL.md 典型结构

```yaml
---
name: resume-assistant
description: 续做时读取 plan…触发词：续做
---
# 步骤 1…2…3…
```

## 设计 Skill 的原则

1. **单一场景** — 续做、模板、复盘、学习 分开  
2. **写清输入** — plan 路径、进度、背景  
3. **写清输出格式** — 已完成/下一步/验证  
4. **和模板配合** — Skill 调流程，Templates 定结构  

## 对照学习

打开 [[Skills/resume_assistant]] 和 `.cursor/skills/resume-assistant/SKILL.md` 对比异同。

## 延伸

- [[提示词工程]] · [[MCP]] · [[Skills/README]]
