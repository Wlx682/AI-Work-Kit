# AI-Work-Kit

Obsidian 知识库 + Cursor / Claude / Codex Skill：模板开工、Epic 闭环、plan 续做。

## 可运行代码

- [`agent/`](agent/README.md)：通用智能体底座。
- [`knowledge_graph_learning/`](knowledge_graph_learning/README.md)：R4 知识图谱驱动学习产品（Python 后端 + Flutter 客户端）。
- `.runtime/`：本地运行数据，已忽略；`tmp/` 只保留实验和静态原型。

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
合代码… 或 workflow=merge-code                  # 双边业务意图分析、开发者决策、合并与验证
/status                           # 看当前卡点（人话摘要：当前 / 卡点 / 下一步 / 继续）
/resume plan=Plans/... 进度=...    # 续做
```

命令行等价：

```bash
python3 scripts/workflow-status.py --workflow client-dev --epic Plans/Epic/xxx.md
python3 scripts/workflow-status.py --workflow merge-code
python3 scripts/test-merge-code-workflow.py             # P0：真实 Git 文件合并场景回归
python3 scripts/workflow-status.py --workflow computer-mgmt
```

底层详情才看 `scripts/workflow-gate.sh --json`；日常优先看 `workflow-status.py`。

`workflow-install.py apply` 只用于电脑/Kit 首次安装或环境修复。`workflow-install.py check` 首次运行会缓存工具、Skill、Hook 与全局指令等静态检查；后续任务命中同一环境指纹时只检查端口等运行时状态，环境变化或传入 `--refresh` 才全量重检。`workflow-status.py` 按任务运行，`workflow-plan-init.py` 仅在当前阶段 Plan 缺失时运行。

## License

团队内部使用；开源前检查 `Contexts/`、`Plans/` 敏感信息。
