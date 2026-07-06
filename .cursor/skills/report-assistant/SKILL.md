---
name: report-assistant
description: >-
  日报/周报/月度复盘。触发：日报、周报、今日/本周总结、整理今天/这周的工作；项目复盘、迭代回顾、月度复盘、本月回顾；/report、/report-assistant。
  不响应：Code Review→code-review；考我/知识复盘→learn-assistant；Epic 审计→dev-lifecycle-audit-assistant。
  日报→Contexts/日报/；周报→Contexts/周报/；月度→Contexts/复盘/。
---

# 日报周报助手

Vault：AI-Work-Kit 根目录

## 触发条件

当用户说以下任一时执行：

- **日报 / 周报类**：「日报」「周报」「今日总结」「本周总结」「整理今天/这周的工作」
- **项目复盘类**：「项目复盘」「迭代回顾」「月度复盘」「本月回顾」
- `/report-assistant` / `/report` 命令

**不响应（让位给其他 Skill）**：

- 「Code Review / review diff / 审查 PR」→ `code-review`
- 「考我 / 知识复盘 / 复习课程」→ `learn-assistant`
- 「审计 Epic / 检查开发流程」→ `dev-lifecycle-audit-assistant`

| 模式 | 触发 | 写入 |
|------|------|------|
| 日报 | 日报、今日总结、整理今天的工作 | `Contexts/日报/YYYY-MM-DD.md` |
| 周报 | 周报、本周总结、整理这周的工作 | `Contexts/周报/YYYY-MM-DD至YYYY-MM-DD.md` |
| 月度 | 复盘、月度总结、本月回顾 | `Contexts/复盘/YYYY-MM.md` |

模板：`Templates/日报模板.md` · `Templates/周报模板.md` · `Templates/月度复盘模板.md`
契约：`Contexts/决策/Skill原子契约.md`
同步：`Skills/report_assistant.md`

## 本人 Git 筛选（必守）

- **只统计本人提交**，不列他人 commit。
- 作者匹配：`git log --author="wanglongxiang"`（邮箱常为 `wanglongxiang@360.cn`）；若曾用中文名则加 `--author="王龙祥"`。
- 仓库当天/当周仅有他人提交 → **该仓库不列入**。
- 本人无 commit 但有 Cursor plan / Kit 工作 → 写在「Cursor（plan / 未合入）」，不冒充代码提交。

## 正文规范（必守）

- **只写工作内容**：做了什么、产出在哪、明日接续。
- **不要写**：统计规则、作者筛选、`git log` 用法、生成命令、存放路径、「不列入」「他人提交」等元信息。
- 某仓库当天没你的事 → **整段不写**，不必解释为什么没写。
- 章节编号用 **一、二、三…**（从一起），不用「零、」或阿拉伯 `0.`。

## 模式 A：日报

1. 日期默认今天。
2. 扫 `~/git/*`：`git log --author=wanglongxiang`（+王龙祥）；**只列本人**有 commit 或未提交改动的仓库。
3. 扫 Kit 当日 `Plans/`、学习、协作产出。
4. 按 `Templates/日报模板.md` 生成 → **写入** `Contexts/日报/YYYY-MM-DD.md`。

## 模式 B：周报

1. **时间段**：默认本周一 00:00 至今天；或用户指定 `时间段=起始 至 结束`。
2. **汇总日报**：读 `Contexts/日报/` 该时段日报，填「日报索引」；无日报的日期不列。
3. **扫描代码仓库**：`git log --since --until --author=wanglongxiang` 统计本人 commit，按主题合并，不逐条堆 hash，不列他人提交。
4. **扫描 Kit**：本周 `Plans/`、`Contexts/`（除日报/周报自身）、Skill/模板变更、学习进度。
5. 按 `Templates/周报模板.md` 生成 → **写入** `Contexts/周报/起始日至结束日.md`。
6. 回复：文件路径 + 一周摘要 + 下周 P0。

## 模式 C：月度复盘

1. 搜索 `Plans/`、`Contexts/`、`Contexts/日报/`、`Contexts/周报/` 该月材料。
2. 分类顺利 / 踩坑；统计续做、模板、材料复用。
3. 按 `Templates/月度复盘模板.md` 输出 → 可选 `Contexts/复盘/YYYY-MM.md`。材料不足时请用户补充主要任务。

## 沉淀原则

| 类型 | 路径 | 规则 |
|------|------|------|
| 日报 | `Contexts/日报/` | 每天一篇，长期沉淀 |
| 周报 | `Contexts/周报/` | 每周一篇，引用日报；无变化仓库不列 |
| 月度 | `Contexts/复盘/` | 可引用本周报 + 日报 |

不替代 `Plans/` 进行中任务。

## 反馈回路（skill_run）

完成任务的最后一步按 `Contexts/决策/Skill反馈协议.md` 收口：
本 Skill 产出日报/周报/复盘（`Contexts/`）而非 plan；未归位候选写入孤立反馈 `## 待整理`，已归位结论只写 `## 已归位` 摘要，不保留完整过程小票。
`contexts_used[].utility` 二选一：`high`（附一句话 `reason`）或 `not-needed`；必填 `skill: report-assistant` / `plan` / `date` / `contexts_used` / `contexts_missing` / `contexts_stale`。
