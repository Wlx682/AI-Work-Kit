# AI-Work-Kit

Obsidian 知识库 + Cursor / Claude / Codex Skill：模板开工、Epic 闭环、plan 续做。

## 读文档（按顺序）

1. **[Kit 核心原则](Contexts/决策/Kit核心原则.md)** — 真理源（放哪 / 不放哪 / 做完怎么办）
2. **[新手引导与最佳实践](Contexts/决策/新手引导与最佳实践.md)** — 3 张地图（入门 / 全流程 / 决策树）
3. **[工作流总览](Contexts/决策/AI-Work-Kit工作流总览.md)** — Skill 速查 + 看板 + 门禁
4. **[模板约定](Templates/模板约定.md)** — YAML / Epic 字段 / 续做格式
5. **[索引](索引.md)** — 目录速查

## 安装

1. Obsidian + Cursor 打开本仓库  
2. 可选 MCP：`cp .cursor/mcp.json.example .cursor/mcp.json`  
3. 全局 Skill：`./scripts/sync-agent-skills.sh --sync`（部署到 Claude / Codex；Cursor 可继续 `cp -r .cursor/skills/* ~/.cursor/skills/`）
4. Claude Code：见 [集成说明](Contexts/Claude-Code集成AI-Work-Kit.md)
5. Codex：根目录已内置 `AGENTS.md`；执行同步脚本后会生成 `.codex/skills/` 并部署到 `~/.codex/skills/`

## 三条命令

```text
/full-cycle 模块=XX          # 新需求（自然语言入口：workflow-router）
/resume plan=Plans/... 进度=...   # 续做
/review-assistant 日报        # 日报 → Contexts/日报/
```

## License

团队内部使用；开源前检查 `Contexts/`、`Plans/` 敏感信息。
