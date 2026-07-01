---
name: weekly-intel-digest
description: >-
  海外一手 AI 编程/Agent 资讯周报。抓取 follow 名单最新英文原文 → 按评分标准筛选 → 出中文导语 → 套周帖模板 → 交接纳米Work翻译。
  触发词：找CC文章、周报选题、海外资讯、整理分享帖、claude code 分享、/intel、/weekly-intel-digest。
  不响应：项目日报/复盘→review-assistant；课程化学习→learn-assistant。
---

# 海外资讯周报助手 Skill

知识库：`/Users/wanglongxiang/git/AI-Work-Kit`
原则：[[Contexts/决策/Kit核心原则]]（Plans 临时 · Contexts 固定 · 做完删 plan）

## 触发条件

- 「**找 CC/Codex 文章**」「**周报选题**」「**海外资讯**」「**整理分享帖**」「**Claude Code 分享**」
- `/intel` / `/weekly-intel-digest`

**不响应（让位）**：项目日报/迭代复盘 → `review-assistant`；课程化 LLM 学习 → `learn-assistant`；PM 通用物料 → `material-prep-assistant`。

## 必读资产（长期资产在 Contexts/情报源/）

- [[Contexts/情报源/follow名单]] —— 抓谁
- [[Contexts/情报源/筛选评分标准]] —— 怎么挑
- [[Contexts/情报源/周帖模板]] —— 怎么排版
- [[Contexts/情报源/已发去重清单]] —— 别重复

## 能力边界（先说清楚我能/不能）

| 环节 | Agent 能做 | 人工节点 |
|------|-----------|----------|
| 抓取 | ✅ WebSearch/WebFetch 拉英文原文、arXiv、官方文档 | Twitter/X 抓不全时贴链接 |
| 筛选 | ✅ 按评分标准打分去重 | 你终审选 1–3 篇 |
| 中文导语 | ✅ 写技术看点/通用看点/导语 | — |
| **纳米Work 中文链接** | ❌ 生成不了该产品链接 | ⏸ 你把英文原文丢进纳米Work回填 |
| 发帖 | ⚠️ 平台已定「先攒不自动发」 | 你贴到频道 |

## 执行协议（每期五步）

```
1. 开场读资产 → follow名单 + 评分标准 + 去重清单
2. 抓取     → 遍历 follow 名单，WebSearch/WebFetch 拉本周最新英文原文（每源 1–3 条候选）
3. 筛选打分 → 按评分标准算分，过滤已发过的，输出候选表（分数+理由）交你终审
4. 加工组装 → 选定后套周帖模板，写中文导语，生成「⏸ 待纳米Work」交接清单
5. 收尾     → 草稿存 Plans/情报周报/YYYY-MM-DD-第N期.md；发布后追加去重清单一行、删 plan
```

## 产物位置

- **每期草稿（临时）**：`Plans/情报周报/YYYY-MM-DD-第N期.md`，发完即删（符合「做完删 plan」）。
- **长期沉淀**：去重清单追加、follow 名单增补淘汰、优质模板迭代 → `Contexts/情报源/`。

## 硬规则

1. 进入周帖的原文**必须英文一手**；传播链接**必须**是纳米Work中文链接，二者缺一不发。
2. 不接受小红书/抖音/纯视频独立传播。
3. 面向技术为主、产品设计运营也参与 → 每篇必写「技术看点 + 通用看点」双视角。
4. 写 Contexts/情报源/ 下资产前，若非「增补去重清单/follow名单」这类既定动作，须用户确认（遵 CLAUDE.md 规则 2）。

## 反馈回路（遵 CLAUDE.md 规则 5）

任务结束输出 `skill_run` YAML 块：有 plan 追加到 plan 末尾，无 plan 追加到 `Contexts/决策/孤立反馈记录.md` 顶部。
