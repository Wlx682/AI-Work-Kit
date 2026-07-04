---
tags: [学习/概念, mcp]
---

# 概念：MCP（Model Context Protocol）

> **学习顺序：第 6 课。** 先完成 [[提示词工程]] → [[RAG]] → [[Agent]] → [[Skill]] 再读本卡。

## 一句话

AI 客户端和外部工具之间的**标准插头**——让 Agent 能搜笔记、读 API、开浏览器等，而不用每家各写一套。

## 解决什么问题

| 没有 MCP | 有 MCP |
|----------|--------|
| 你手动 `@` 文件 | Agent 自己 search |
| 每个集成单独配置 | 统一 `mcp.json` |
| 能力难复用 | 社区有 Obsidian、Figma、Git 等 server |

## 你 Kit 里的 MCP

- **enquire-mcp**：搜 Obsidian Vault（混合检索）
- 配置：`.cursor/mcp.json`
- 详解：[[MCP进阶指南]]

## MCP vs Skill

| MCP | Skill |
|-----|-------|
| 提供**工具**（搜索、读文件） | 提供**流程**（先搜啥、再输出啥格式） |
| 像「手」 | 像「SOP」 |
| 通常要配置 server | 通常是 markdown |

**最佳组合**：Skill 里写「先 `obsidian_search`，再按模板输出」。

## 自测

- [ ] 能解释 MCP 在「查历史排查」场景的作用
- [ ] 能在 Cursor 里找到 enquire 是否绿灯

## 延伸

- [[RAG]] · [[Agent]] · [[MCP进阶指南]]
