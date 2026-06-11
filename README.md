# AI-Work-Kit

个人 / 团队的 **Obsidian 知识库 + Cursor Skill** 协作框架：模板开工、plan 续做、需求分析、功能开发、Figma 1:1 还原、LLM 学习、**PM 资料沉淀**。

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
5. 阅读：`索引.md` · `分享包-快速开始.md` · `Templates/模板约定.md`
6. **Claude Code**（可选）：`cd AI-Work-Kit && claude` · 见 `Contexts/Claude-Code集成AI-Work-Kit.md` · 根目录 `CLAUDE.md`

## 目录

| 路径 | 说明 |
|------|------|
| `Templates/` | 任务模板（见 `模板约定.md`） |
| `Skills/` | 人类可读的 Skill 提示词（`@` 引用） |
| `.cursor/skills/` | Cursor Agent 自动 Skill |
| `Contexts/` | 长期沉淀：规范、学习、日报、**PM 物料对照表**、MCP 指南 |
| `Plans/` | 进行中的任务（纳入仓库同步；做完可归档或删） |

**顶层只保留入口文档**（索引、README、分享包、落地计划）；学习路线与 MCP 指南在 `Contexts/`。

## 常用 Skill

| 命令 | 场景 |
|------|------|
| `/requirement-analyst` | PRD 分析 |
| `/feature-dev-assistant` | 功能开发（需求 + 方案 + 界面） |
| `/figma-ui-assistant` | 仅 UI 子任务 |
| `/template-generator` | 排查、技术方案、review |
| `/resume plan=Plans/... 进度=...` | 续做 plan |
| `/review-assistant 日报` | 今日 → `Contexts/日报/` |
| `/review-assistant 周报` | 本周 → `Contexts/周报/` |
| `/learn-assistant` | LLM / 提示词学习 |
| `/material-prep` | PM 物料 / 配置对照表 → `Contexts/` |

## 文档

- [分享方案](分享方案-AI知识库与Cursor协作.md)
- [MCP 进阶指南](Contexts/MCP进阶指南.md)
- [学习路线](Contexts/LLM学习/学习路线-LLM与提示词.md)
- [收银台配置对照表](Contexts/收银台/MSPay收银台配置对照表.md)（示例）
- [模板约定](Templates/模板约定.md)

## License

Private / 团队内部使用请自行约定；开源发布前请检查 `Contexts/` 与 `Plans/` 是否含敏感信息。
