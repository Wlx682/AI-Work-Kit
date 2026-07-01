---
name: weekly-intel-digest
description: >-
  海外一手 AI 编程/Agent 资讯周报。抓取 follow 名单最新英文原文→按评分标准筛选→出中文导语→套周帖模板→交接纳米Work翻译。
  触发词：找CC文章、周报选题、海外资讯、整理分享帖、claude code 分享、/intel、/weekly-intel-digest。
  不响应：项目日报/复盘→review-assistant；课程化学习→learn-assistant。
---

# 海外资讯周报助手

知识库：`/Users/wanglongxiang/git/AI-Work-Kit`
原则：[[Contexts/决策/Kit核心原则]] · 全文：`Skills/weekly_intel_digest.md`

## 触发条件

- 「找 CC/Codex 文章」「周报选题」「海外资讯」「整理分享帖」「Claude Code 分享」
- `/intel` / `/weekly-intel-digest`

**不响应**：项目日报/复盘 → `review-assistant`；课程化学习 → `learn-assistant`；PM 物料 → `material-prep-assistant`。

## 必读资产

- [[Contexts/情报源/follow名单]]、[[Contexts/情报源/筛选评分标准]]、[[Contexts/情报源/周帖模板]]、[[Contexts/情报源/已发去重清单]]

## 执行协议（五步）

```
1. 开场读资产（follow名单+评分标准+去重清单）
2. 抓取：遍历 follow 名单，WebSearch/WebFetch 拉本周最新英文原文
3. 筛选打分：按评分标准算分、去重，输出候选表交你终审
4. 加工组装：套周帖模板，写中文导语，生成「⏸ 待纳米Work」交接清单
5. 收尾：草稿存 Plans/情报周报/，发布后追加去重清单、删 plan
```

## 硬规则

1. 原文必须英文一手；传播链接必须纳米Work中文链接，缺一不发。
2. 不接受小红书/抖音/纯视频独立传播。
3. 每篇必写「技术看点 + 通用看点」双视角（技术为主，产品设计运营也参与）。
4. **纳米Work 中文链接 Agent 生成不了** → 输出 ⏸ 交接清单交人工。

## 反馈回路

结束输出 `skill_run` YAML：有 plan 追加末尾，无 plan 追加 `Contexts/决策/孤立反馈记录.md` 顶部。
