# AI-Work-Kit · Claude Code 项目说明

> 与 Cursor 共用同一份 Obsidian 知识库。完整集成步骤见 [[Contexts/Claude-Code集成AI-Work-Kit]]。

## 角色

你是我的 AI 开发助手，使用 Obsidian 知识库 **AI-Work-Kit** 辅助工作。

## 多仓库

- **知识库 Vault**：本仓库（AI-Work-Kit）。
- **代码仓库**：Claude Code 当前工作目录；不要假设固定项目名。
- 工作区仅是 AI-Work-Kit 时，向用户索要业务代码路径，或请其在业务仓库另开 Claude Code 会话。

## 知识库结构

| 路径 | 用途 |
|------|------|
| `Plans/Bug排查/` | 排查类 plan |
| `Plans/客户端技术方案/`、`Plans/服务端技术方案/` | 技术方案 plan |
| `Plans/代码重构/` | 重构类 plan |
| `Plans/需求分析/` | PRD 分析（P0 闭环后再开发） |
| `Plans/功能开发/` | 功能/模块开发 plan |
| `Contexts/需求分析/` | PRD 检查清单、问题模式 |
| `Contexts/Figma/` | 设计规范（不存 Figma URL） |
| `Contexts/` | 会议、调研、踩坑、决策、PM 物料 |
| `Contexts/LLM学习/` | LLM/Agent/Skill/MCP 概念与笔记 |
| `Plans/学习/` | 进行中的学习计划 |
| `Templates/` | 任务模板 |
| `Skills/` | 人类可读 Skill（对话中 `@Skills/xxx.md` 引用） |
| `.claude/skills/` | Claude Code 自动 Skill（可选，从 `.cursor/skills/` 同步） |

## 使用规则

1. 用户说「查一下」「参考之前的」「根据计划」→ 优先搜 `Plans/`、`Contexts/`；若 enquire MCP 可用则先语义检索。
2. 回答或写代码前，涉及已知信息（错误码、历史决策）→ 先读笔记并注明路径。
3. plan 中 `[[双向链接]]` 指向的 Contexts 笔记一并读取。
4. 写回笔记前须经用户确认（除非用户明确说「存档到 Contexts」）。

## Skill 调用（与 Cursor 命令对齐）

| 用户说法 | 执行 | 说明 |
|----------|------|------|
| 续做、`/resume` | `resume-assistant` | `/resume plan=Plans/【分类】/xxx.md 进度=...` |
| 用模板、排查/方案/review | `template-generator` | 方案区分客户端/服务端平台 |
| 日报、今日总结 | `review-assistant` 日报 | git **仅本人** `--author=wanglongxiang`（+王龙祥）；**写入** `Contexts/日报/YYYY-MM-DD.md` |
| 周报、本周总结 | `review-assistant` 周报 | **写入** `Contexts/周报/` |
| 复盘、月度总结 | `review-assistant` 月度 | 可引用日报/周报 |
| 分析需求、看 PRD | `requirement-analyst` | plan → `Plans/需求分析/` |
| 做功能、新需求 | `feature-dev-assistant` | 须有关联需求分析或用户声明 PRD 无 P0 |
| 做界面、Figma | `figma-ui-assistant` | Figma 链接由用户当次提供 |
| 学习、续学、考我 | `learn-assistant` | 读 `Contexts/LLM学习/学习路线-LLM与提示词.md` |
| 准备资料、PM 物料 | `material-prep-assistant` | 写 `Contexts/{分类}/`，不写业务仓库 docs |

在 Claude Code 中：说触发词，或 `@Skills/resume_assistant.md` 等显式引用。

## MCP（enquire，可选）

- 配置：项目根 `.mcp.json`（见 `.mcp.json.example`）。
- 用户说「知识库里有没有…」→ 优先 `obsidian_search`，再按 Skill 流程续做或开工。

## 输出要求

- 知识库无相关信息 → 明确说明，再补充通用知识。
- 任务结束 → 提醒更新 `Plans/` 勾选或沉淀 `Contexts/`。
- 续做 → 输出：已完成 / 下一步 / 可能原因 / 验证方法。

## 常用入口

- 索引：`索引.md`
- 快速开始：`分享包-快速开始.md`
- Claude 集成：`Contexts/Claude-Code集成AI-Work-Kit.md`
