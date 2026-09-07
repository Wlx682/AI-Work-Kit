# Claude Code 集成

Claude Code 在本仓库读取根目录 `CLAUDE.md`，项目原则与 Cursor、Codex 共用 `AGENTS.md`。

项目 Skill 的唯一真理源是 `Skills/*/SKILL.md`。同步项目内三个入口：

```bash
python3 scripts/sync-skills.py --sync
```

需要部署到用户级目录时显式增加 `--global`。MCP 仍通过 `.mcp.json` 配置；知识库路径指向本仓库即可。
