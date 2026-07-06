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

## 日常三步

```text
开始/启动… 或 自然语言或 workflow=client-dev   # 开始一件事（自然语言入口：workflow-router）
/status                           # 看当前卡点（人话摘要：当前 / 卡点 / 下一步 / 继续）
/resume plan=Plans/... 进度=...    # 续做
```

命令行等价：

```bash
python3 scripts/workflow-status.py --workflow client-dev --epic Plans/Epic/xxx.md
python3 scripts/workflow-status.py --workflow computer-mgmt
```

底层详情才看 `scripts/workflow-gate.sh --json`；日常优先看 `workflow-status.py`。

## License

团队内部使用；开源前检查 `Contexts/`、`Plans/` 敏感信息。
