---
tags: [情报源, follow, claude-code, agent]
description: 海外一手 AI 编程/Agent 资讯的长期关注名单，供 weekly-intel-digest 每周抓取
date: 2026-07-01
---

# 海外一手资讯 · Follow 名单

> 用途：`weekly-intel-digest` Skill 每周据此抓取最新英文原文 → 筛选 → 出中文导语 → 组周帖。
> 维护：新增/淘汰源在此改；每条注明「为什么值得长期看」。原则见 [[Contexts/决策/Kit核心原则]]。

## A. Anthropic 官方 · Claude Code 作者/布道者（一手）

| 人物 | 身份 | 主要平台 | 为什么长期看 |
|------|------|----------|--------------|
| Boris Cherny | Claude Code 原作者 | Twitter/X、个人博客、Anthropic Eng Blog | CC 设计意图与最佳实践的第一来源 |
| Cat Wu | Claude Code PM | Twitter/X、Anthropic | 功能路线、用法演示 |
| Fiona Fung | Claude Code 布道/DevRel | Twitter/X、YouTube | 实战工作流、cowork 案例 |
| Anthropic Engineering | 官方工程博客 | anthropic.com/engineering | subagents/hooks/MCP 权威文档 |

## B. 前沿观点 · Agent / 提示词（一手思想源）

| 人物/源 | 关注点 | 平台 |
|---------|--------|------|
| Andrej Karpathy | 提示词、Agent、LLM 系统观 | Twitter/X、YouTube、个人博客 |
| Armin Ronacher (mitsuhiko) | agentic coding、harness/循环、agent 工程一线判断 | 个人博客 lucumr.pocoo.org（可 DocShark 建库，第8期入选） |
| （待补）| Agent 论文 | arXiv cs.AI / cs.CL 每周新论文 |

## C. 对比 / 生态（Codex 等）

| 源 | 关注点 |
|----|--------|
| OpenAI Codex 官方文档/博客 | Codex CLI 用法，供 CC vs Codex 对比 |
| （待补）||

---

## 抓取渠道备注

- **官方文档站优先用 DocShark MCP**：`manage_library` 建库（如 anthropic.com/engineering、OpenAI 文档）→ `search_docs` 搜本周主题 → `get_doc_page` 取正文。适合结构化文档站。
- 我（Agent）还能用 **WebSearch/WebFetch** 抓公开博客、arXiv、YouTube 文字版——但本环境走第三方网关时二者可能不稳（WebSearch 区域限制、WebFetch 模型映射），失败即降级到 ⏸ 人工。
- Twitter/X 正文与零散个人博客单帖 → DocShark 不擅长，输出「⏸ 待人工：贴原推链接/正文」交接给你。
- **硬规则**：进入周帖的原文必须是**英文一手**；中文链接由**纳米Work**人工生成（Agent 不产出该链接）。
