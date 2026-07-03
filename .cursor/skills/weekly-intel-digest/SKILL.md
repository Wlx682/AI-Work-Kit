---
name: weekly-intel-digest
description: >-
  海外一手 AI 编程/Agent 资讯周报（双卷分离：人类卷=技术博客水准文章 + AI卷=进化信号）。DocShark 可用时优先抓官方文档站，不可用则降级 Web/人工贴原文→评分筛选→按写作规范出人类卷→交接纳米Work生成链接→skill_run 反哺进化链。
  触发词：找CC文章、周报选题、海外资讯、整理分享帖、claude code 分享、/intel、/weekly-intel-digest。
  不响应：项目日报/复盘→review-assistant；课程化学习→learn-assistant。
---

# 海外资讯周报助手

知识库：`/Users/wanglongxiang/git/AI-Work-Kit`
原则：[[Contexts/决策/Kit核心原则]] · **全文（执行以此为准）：`Skills/weekly_intel_digest.md`**

## 触发条件

- 「找 CC/Codex 文章」「周报选题」「海外资讯」「整理分享帖」「Claude Code 分享」
- `/intel` / `/weekly-intel-digest`

**不响应**：项目日报/复盘 → `review-assistant`；课程化学习 → `learn-assistant`；PM 物料 → `material-prep-assistant`。

## 必读资产

- [[Contexts/情报源/follow名单]]、[[Contexts/情报源/筛选评分标准]]、[[Contexts/情报源/周帖模板]]、[[Contexts/情报源/已发去重清单]]

## 执行协议（八步 · 双卷分离，详见全文）

```
1. 读资产（follow名单+评分标准+去重清单）
2. 抓取：官方源有 DocShark 则建库→search_docs→get_doc_page；无 DocShark 则降级 Web 搜索/浏览；X/博客抓不到→⏸人工贴链接
3. 硬门槛过滤（非英文一手/纯视频/近8周已发→淘汰）
4. 筛选打分（按评分标准，输出候选表交终审，**每期只选1篇最高分深挖**）
5. 去重确认（比对已发去重清单）
6. 组装人类卷：**每期只写1篇**，产出纯净正文 `.md`(从标题开始·无提示词/注释/元说明) + 同名 `.prompt.md`(给纳米Work的生成指令);达深度标准(讲机制+前因后果+对照+落地复用),过自查清单(无YAML)
7. 生成AI卷：同名 .meta.yaml 写 skill_run，能力缺口→contexts_missing + 源健康自检
8. 收尾：三文件存 Plans/情报周报/(.md正文 + .prompt.md提示词 + .meta.yaml);交用户把两个.md给纳米Work智能体→按.prompt.md生成可访问web链接;发布后追加去重清单、删 plan
```

## 硬规则（详见全文）

1. 原文必须英文一手；传播用纳米Work生成的可公开web链接。
2. 不接受小红书/抖音/纯视频独立传播。
3. 每篇必含「技术看点 + 通用看点」双视角（融入行文，不在正文声明给谁看）。
4. **人类卷正文纯净·提示词分离**（四段结构主题→想法→结论→复用各用#### ；禁emoji/段子；**图示优先·每篇≥2张图**·大白话；正文不写对文章本身的要求/元说明）。
5. **纳米Work web链接**：正文 `.md` 与提示词 `.prompt.md` 分两个文件；用户把两个 .md 给纳米Work智能体，按 .prompt.md 生成可访问URL。
6. 进化萃取强制：每期 .meta.yaml 必须含 contexts_missing；通常至少一项，确实无缺口则写 [] 并在 notes 说明；源连续3期无入选→source_stale_warning。

## 反馈回路

skill_run 写入独立 `.meta.yaml`（人类卷不含 YAML），喂 `feedback-aggregate → vault-evolve`。无 plan 则追加 `Contexts/决策/孤立反馈记录.md`。
