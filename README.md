# AI-Work-Kit

Obsidian 知识库 + Cursor / Claude Skill：模板开工、Epic 闭环、plan 续做。

## 读文档（按顺序）

1. **[Kit 核心原则](Contexts/决策/Kit核心原则.md)** — 放哪、删不删（全库唯一真相源）
2. **[快速开始](分享包-快速开始.md)** — 5 分钟 + Case
3. **[工作流总览](Contexts/决策/AI-Work-Kit工作流总览.md)** — Skill、看板、门禁
4. **[模板约定](Templates/模板约定.md)** — YAML、续做格式
5. **[索引](索引.md)** — 目录速查

## 安装

1. Obsidian + Cursor 打开本仓库  
2. 可选 MCP：`cp .cursor/mcp.json.example .cursor/mcp.json`  
3. 全局 Skill：`cp -r .cursor/skills/* ~/.cursor/skills/`  
4. Claude Code：见 [集成说明](Contexts/Claude-Code集成AI-Work-Kit.md)

## 三条命令

```text
/full-cycle 模块=XX          # 新需求
/resume plan=Plans/... 进度=...   # 续做
/review-assistant 日报        # 日报 → Contexts/日报/
```

## License

团队内部使用；开源前检查 `Contexts/`、`Plans/` 敏感信息。
