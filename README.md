# AI-Work-Kit

个人 / 团队的 **Obsidian 知识库 + Cursor Skill** 协作框架：模板开工、plan 续做、需求分析、功能开发、Figma 1:1 还原、LLM 学习路线。

## 快速开始

1. **Clone** 本仓库，Obsidian `Open folder as vault` 打开根目录
2. **Cursor** 打开同一文件夹（或在业务代码仓库里用全局 `/skill`）
3. 复制 MCP 配置（可选）：
   ```bash
   cp .cursor/mcp.json.example .cursor/mcp.json
   # 编辑 --vault 为你的 AI-Work-Kit 绝对路径
   ```
4. 全局 Skill（任意代码项目可用）：
   ```bash
   cp -r .cursor/skills/* ~/.cursor/skills/
   ```
5. 阅读：`索引.md` · `分享包-快速开始.md`

## 目录

| 路径 | 说明 |
|------|------|
| `Templates/` | 排查、方案、功能开发、需求分析等模板 |
| `Skills/` | 人类可读的 Skill 提示词（`@` 引用） |
| `.cursor/skills/` | Cursor Agent 自动 Skill |
| `Contexts/` | 长期沉淀：规范、调研、LLM 概念 |
| `Plans/` | 进行中的任务（个人 plan 默认不提交，见 `.gitignore`） |

## 常用 Skill

| 命令 | 场景 |
|------|------|
| `/requirement-analyst` | PRD 分析（逻辑 / 交互 / 遗漏） |
| `/feature-dev-assistant` | 功能开发（需求 + 方案 + 界面） |
| `/figma-ui-assistant` | 仅 UI 子任务 |
| `/template-generator` | 排查、技术方案 |
| `/resume-assistant` | 续做 plan |
| `/learn-assistant` | LLM / 提示词学习 |

## 多仓库

- **知识库** = 本仓库（Vault）
- **代码** = 当前 Cursor 工作区，无需在 Skill 里写死仓库路径

## 文档

- [分享方案](分享方案-AI知识库与Cursor协作.md)
- [MCP 进阶指南](MCP进阶指南.md)
- [学习路线](学习路线-LLM与提示词.md)

## License

Private / 团队内部使用请自行约定；开源发布前请检查 `Contexts/` 与 `Plans/` 是否含敏感信息。
