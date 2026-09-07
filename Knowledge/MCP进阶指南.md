# MCP 进阶指南

MCP 用来让 AI 读取外部事实或执行明确操作，不承担任务编排和决策。

## 本库检索

当笔记路径已知时直接读取文件；只有不知道材料在哪里、需要语义搜索或反向链接时才使用 Obsidian MCP。检索结果只是候选证据，使用前仍需打开原文确认。

enquire-mcp 的项目配置示例见 `.cursor/mcp.json.example` 和 `.mcp.json.example`：

```bash
npx -y @oomkapwn/enquire-mcp setup --vault "/你的路径/AI-Work-Kit"
npx -y @oomkapwn/enquire-mcp index --vault "/你的路径/AI-Work-Kit"
```

默认关闭写能力。确需让 MCP 写文件时，由人明确授权目标范围；不要因为工具可写就扩大任务。

## 判断

- 工具返回值需要用原始页面、文件或命令结果复核。
- 不同时开启多个功能重叠的 Obsidian MCP。
- Vault 使用明确的绝对路径。
- 密钥放在环境变量或系统凭据中，不写入 `Knowledge/`。
