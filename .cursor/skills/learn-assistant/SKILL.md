---
name: learn-assistant
description: >-
  LLM/提示词学习助手（限定课程化路线）。触发词：学习路线、继续课程、续学、LLM学习、考我课程、考我（范围=XX）、整理学习笔记（路线内）、/learn、/learn-assistant。
  不响应：学一下代码规范/整理业务笔记→普通对话；日报周报→review-assistant。
  开场读进度、动态出资料、收尾自动收集。
---

# 学习助手

知识库：`/Users/wanglongxiang/Documents/AI-Work-Kit`  
原则：[[Contexts/决策/Kit核心原则]] · 全文：`Skills/learn_assistant.md`

## 触发条件（限定域）

当用户说以下任一时执行 —— **限定课程化 / 路线化的学习场景**，不响应宽泛的「学一下」「了解一下」：

- 「**学习路线**」「**继续课程**」「**续学**」「**LLM 学习**」「**考我课程**」「**考我（范围=XX）**」「**新主题（课程）**」「**整理学习笔记（路线内）**」
- `/learn-assistant` / `/learn` 命令

**不响应（让位给其他 Skill）**：

- 「学习一下你们的代码规范 / 整理业务笔记 / 整理文档」→ 普通对话或 `review-assistant`
- 「项目复盘 / 日报 / 周报」→ `review-assistant`
- 「审计学习进度」→ 仍由本 Skill 开场读进度，再转 `learning-audit-assistant`

**顺序**：LLM(1)→上下文(2)→RAG(3)→Agent(4)→Skill(5)→MCP(6)→评估(7)→综合(8)。

## 统一协议（凡学习相关必守）

```
开场读进度 → 动态出资料 → 执行模式 → 收尾自动收集
```

| 阶段 | 动作 |
|------|------|
| 开场 | `./scripts/learning-progress-read.sh` |
| 动态出资料 | 只讲第一个未勾步骤；无笔记则练/写笔记 |
| 收尾 | `./scripts/learning-progress-snapshot.sh …` + 进度小表 |

同步：`Skills/learn_assistant.md`
