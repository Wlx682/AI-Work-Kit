---
name: weekly-intel-digest
description: >-
  海外一手 AI 编程/Agent 资讯周报（双卷分离：人类卷=技术博客水准文章 + AI卷=进化信号）。follow 名单只是种子源，不是唯一来源；可从官方文档、工程博客、研究/概念文章、社区一手长文中寻找智能体/AI 编程方向的高价值内容，优先关注 agent 开发、app 开发新范式、AI 原生开发工具链与产品构建方式。DocShark 可用时优先抓官方文档站，不可用则降级 Web/人工贴原文→评分筛选→按写作规范出人类卷→Agent 直接产炫酷 .html 网页（过浏览器自检）交纳米Work 只上传CDN出短链→skill_run 反哺进化链。
  触发词：找CC文章、周报选题、海外资讯、整理分享帖、claude code 分享、/intel、/weekly-intel-digest。
  不响应：项目日报/复盘→report-assistant；课程化学习→learn-assistant。
---

# 海外资讯周报助手

知识库：`/Users/wanglongxiang/git/AI-Work-Kit`
原则：[[Contexts/决策/Kit核心原则]] · **全文（执行以此为准）：`Skills/weekly_intel_digest.md`**

## 触发条件

- 「找 CC/Codex 文章」「周报选题」「海外资讯」「整理分享帖」「Claude Code 分享」
- `/intel` / `/weekly-intel-digest`

**不响应**：项目日报/复盘 → `report-assistant`；课程化学习 → `learn-assistant`；PM 物料 → `material-prep-assistant`。

## 必读资产

- [[Contexts/情报源/follow名单]]（种子源/源健康参考，不是唯一来源）、[[Contexts/情报源/筛选评分标准]]、[[Contexts/情报源/周帖模板]]、[[Contexts/情报源/已发去重清单]]

## 执行协议（八步 · 双卷分离，详见全文）

```
1. 读资产（follow名单作为种子源+评分标准+去重清单）
2. 抓取：先从 follow 种子源、官方文档/engineering blog、研究/概念文章、社区一手长文扩展候选；优先关注 agent 开发、app 开发新范式、AI 原生 IDE/框架/工具链、端到端产品构建方式；官方源有 DocShark 则建库→search_docs→get_doc_page；无 DocShark 则降级 Web 搜索/浏览；X/博客抓不到→⏸人工贴链接
3. 硬门槛过滤（非英文一手/纯视频/近8周已发→淘汰）
4. 筛选打分（按评分标准，输出候选表交终审，**每期只选1篇最高分深挖**）
5. 去重确认（比对已发去重清单）
6. 组装人类卷：**每期只写1篇**，产出纯净正文 `.md`(从标题开始·无提示词/注释/元说明);达深度标准(讲机制+前因后果+对照+落地复用),过自查清单(无YAML)
7. 生成AI卷：同名 .meta.yaml 写 skill_run，能力缺口→contexts_missing + 源健康自检
8. 生成炫酷网页：**Agent 直接产同名 `.html` 自渲染成品**(遵 Contexts/规范/炫酷建站规范：内嵌mermaid.js自渲染+渐进增强+深色科技感+**关键数字主角化(特大字/独占卡/count-up)**+**流式栅格auto-fit动态适配**),并用本地浏览器过自检(图全SVG/console0报错/正文全可见/**375·768·1440三宽度无横溢出**)
9. 收尾：三文件存 Plans/情报周报/(.md正文 + .html网页 + .meta.yaml);交用户把 `.html` 给纳米Work→它**只上传CDN+返回短链**,不再生成网页;发布后追加去重清单、删 plan
```

## 硬规则（详见全文）

1. 原文必须英文一手；对外网页由 **Agent 产 `.html` → 纳米Work 传CDN出短链**（遵 Contexts/规范/炫酷建站规范）。
2. 不接受小红书/抖音/纯视频独立传播。
3. 每篇必含「技术看点 + 通用看点」双视角（融入行文，不在正文声明给谁看）。
4. **人类卷正文纯净**（四段结构主题→想法→结论→复用各用#### ；禁emoji/段子；**图示优先·每篇≥2张图**·大白话；正文不写对文章本身的要求/元说明）。
5. **网页 Agent 产·纳米Work 只托管**：Agent 直接产自渲染 `.html`（内嵌mermaid.js+浏览器自检），纳米Work 上传CDN返回短链，不改内容。
6. 进化萃取强制：每期 .meta.yaml 必须含 contexts_missing；通常至少一项，确实无缺口则写 [] 并在 notes 说明；源连续3期无入选→source_stale_warning。

## 反馈回路

skill_run 写入独立 `.meta.yaml`（人类卷不含 YAML），喂 `feedback-aggregate → vault-evolve`。无 plan 则追加 `Contexts/决策/孤立反馈记录.md`。
