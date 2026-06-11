---
name: learn-assistant
description: LLM/提示词学习助手。触发词：学习、续学、考我、整理学习笔记、新概念及一切学习相关。开场读进度、动态出资料、收尾自动收集。
---

# 学习助手

知识库：`/Users/wanglongxiang/Documents/AI-Work-Kit`  
全文：`Skills/learn_assistant.md`

**顺序**：LLM(1)→上下文(2)→RAG(3)→Agent(4)→Skill(5)→MCP(6)。新用户从 `Plans/学习/2026-06-12-第1课-LLM与提示词入门.md` 开始。

## 统一协议（凡学习相关必守）

```
开场读进度 → 动态出资料 → 执行模式 → 收尾自动收集
```

| 阶段 | 动作 |
|------|------|
| 开场 | `./scripts/learning-progress-read.sh` |
| 动态出资料 | 只讲第一个未勾步骤；无笔记则练/写笔记；不信与勾选矛盾的 frontmatter |
| 收尾 | `./scripts/learning-progress-snapshot.sh --mode … --plan … --summary "…"` + 进度小表 |

审计请求 → 先开场读进度 → `learning-audit-assistant` → 收尾快照（mode=审计）。

## 模式

| 触发 | 动作 |
|------|------|
| 新主题 | 有未完成同主题 plan 则续学；否则新建 plan |
| 续学 | 下一未勾步骤 + 自测 |
| 整理笔记 | 模板结构化 |
| 考我 | 优先考薄弱/未勾课 |
| 审计 | 转 learning-audit-assistant |

沉淀：概念 → `Contexts/LLM学习/概念/`；笔记 → `笔记/`；快照 → `笔记/学习进度快照.md`。

同步：`Skills/learn_assistant.md`
