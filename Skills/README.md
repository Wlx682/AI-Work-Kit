# Skills 文件夹说明

## Obsidian 的 Skills ≠ Cursor 的 Skills

| | Obsidian `Skills/` | Cursor `.cursor/skills/` |
|--|-------------------|--------------------------|
| 格式 | 普通 `.md` 笔记 | `SKILL.md` + YAML frontmatter |
| 谁用 | 你在 Obsidian 里阅读、编辑 | Cursor Agent 自动匹配调用 |
| 怎么触发 | `@Skills/xxx.md` 手动引用 | 说「续做」「复盘」等触发词 |
| 存在意义 | 提示词版本管理、团队共享、Obsidian 内编辑 | AI 无感调用 |

**推荐工作流：**

1. 在 Obsidian 里维护 `Skills/*.md`（人类友好）
2. `.cursor/skills/*/SKILL.md` 保持同步（AI 自动调用）
3. 改了一处，记得同步另一处（或只改 Obsidian，用 `@` 引用即可）

## 为什么在别的对话 @ 不到？

`@Skills/template_generator.md` **只能在你打开 AI-Work-Kit 文件夹作为工作区时** 才能搜到——`@` 只索引当前工作区里的文件。

在业务代码仓库里排查 bug 时，工作区是别的项目，所以 `@` 列表里没有知识库文件。

### 三种解决办法

| 方式 | 做法 | 适用 |
|------|------|------|
| **全局 Skill**（已配置） | 任意项目里说 `/template-generator` 或「用模板排查」 | 最省事 |
| **多根工作区** | Cursor `File → Add Folder to Workspace` 加上 AI-Work-Kit | 需要同时 @ 代码和笔记 |
| **只说触发词** | 不说 `@`，直接「按知识库排查模板，背景=…」 | 临时用一次 |

全局 Skill 位置：`~/.cursor/skills/template-generator/SKILL.md`（所有项目可用）

## 多仓库：要不要记仓库路径？

**不用。** 约定如下：

| 你打开的工作区 | 代码在哪搜 | 知识库在哪 |
|----------------|------------|------------|
| **业务代码项目**（推荐） | 自动 = 当前工作区根目录 | Skill 内读 AI-Work-Kit Vault 路径 |
| **AI-Work-Kit**（仅笔记） | 对话里加 `仓库=/path/to/项目` | 就是当前文件夹 |
| **多根工作区**（代码 + Kit） | 代码那个根目录 | AI-Work-Kit 那个根目录 |

触发词里**一般不用写** `仓库=ClawAI`；只有人坐在 Vault 里、又要搜别的仓库代码时才加。

## 三个核心 Skill

| 文件 | 触发词 | 用途 |
|------|--------|------|
| [[resume_assistant]] | 续做 | 读取 plan，从当前进度继续 |
| [[template_generator]] | 用模板 / 生成排查 | 按模板启动新任务 |
| [[review_assistant]] | **日报** / **周报** / 复盘 | `Contexts/日报/` · `Contexts/周报/` |
| [[requirement_analyst]] | 分析需求 / PRD / push 产品 | **先于开发**；逻辑/交互冲突 |
| [[feature_dev_assistant]] | 做功能 / 开发模块 / 新需求 | 需求通过后：方案+界面 plan |
| [[figma_ui_assistant]] | 仅 UI / 对稿 | 方案已有，只做界面 |
| [[learn_assistant]] | 学习 / 续学 / 考我 | LLM、提示词、Agent、MCP 学习 |

## 快速示例

```
@Skills/resume_assistant.md 续做，plan文件名=Bug排查/2026-06-10-API超时排查.md，当前进度=已完成抓包

@Skills/template_generator.md 任务类型=排查，背景=生产环境下单接口偶发超时

@Skills/review_assistant.md 复盘时间段=2026-06-01 至 2026-06-30

/figma-ui-assistant 新任务，Figma=【粘贴链接】，平台=iOS，页面=设置页

/learn-assistant 新主题，题目=提示词工程，目标=能写结构化 prompt 并举例 Skill

/requirement-analyst 新分析，PRD=【飞书链接】，模块=创建自动化任务
```
