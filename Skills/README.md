# Skills 文件夹说明

## Obsidian 的 Skills ≠ Cursor 的 Skills

| | Obsidian `Skills/` | Cursor `.cursor/skills/` |
|--|-------------------|--------------------------|
| 格式 | 普通 `.md` 笔记 | `SKILL.md` + YAML frontmatter |
| 谁用 | 你在 Obsidian 里阅读、编辑 | Cursor Agent 自动匹配调用 |
| 怎么触发 | `@Skills/xxx.md` 手动引用 | 说「续做」「复盘」等触发词 |
| 存在意义 | 提示词版本管理、团队共享 | AI 无感调用 |

**推荐**：在 Obsidian 维护 `Skills/*.md`，与 `.cursor/skills/*/SKILL.md` 保持同步。

## 为什么在别的对话 @ 不到？

`@Skills/template_generator.md` **只能在打开 AI-Work-Kit 作为工作区时** 搜到。

在业务代码仓库里，用全局 Skill：`/template-generator`、`/resume`、`/feature-dev-assistant`、`/material-prep` 等。

## 多仓库

**不用记仓库路径。** 代码 = 当前 Cursor 工作区；**资料库** = AI-Work-Kit Vault 的 `Contexts/`（`/material-prep` 从代码仓提炼配置，写入 Vault，不写业务 `docs/`）。

## Skill 一览

| 文件 | 触发 | 用途 |
|------|------|------|
| [[resume_assistant]] | `/resume plan=Plans/... 进度=...` | 续做任意 plan |
| [[template_generator]] | `/template-generator` | 按模板开工 |
| [[requirement_analyst]] | `/requirement-analyst` | PRD 分析 |
| [[feature_dev_assistant]] | `/feature-dev-assistant` | 功能开发 |
| [[figma_ui_assistant]] | `/figma-ui-assistant` | 仅 UI |
| [[review_assistant]] | `/review-assistant 日报/周报` | 汇报 |
| [[learn_assistant]] | `/learn-assistant` | LLM 学习 |
| [[material_prep_assistant]] | `/material-prep` | 资料沉淀到 Contexts（PM 物料、对照表） |

## 快速示例

```
/resume plan=Plans/Bug排查/2026-06-10-API超时.md 进度=已完成抓包

/template-generator 任务类型=技术方案，平台=客户端，背景=设置页重构

/requirement-analyst 新分析，PRD=【链接】，模块=创建自动化任务

/feature-dev-assistant 新任务，模块=xxx，Figma=【链接】

/review-assistant 日报

/learn-assistant 新主题，题目=LLM基础与提示词入门

/material-prep 类型=收银台，参考=Claw，新App=namiWork
```
