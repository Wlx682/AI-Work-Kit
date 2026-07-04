# 日报周报 Skill

> 从 `review-assistant` 拆分而来（单一职责：日报/周报/月度复盘）。代码审查见 `code_review.md`。

## 触发条件

当用户说以下任一时执行：

- **日报 / 周报类**：「日报」「周报」「今日总结」「本周总结」「整理今天/这周的工作」
- **项目复盘类**：「项目复盘」「迭代回顾」「月度复盘」「本月回顾」
- `/report-assistant` / `/report` 命令

**不响应（让位给其他 Skill）**：

- 「Code Review / review diff / 审查 PR」→ `code-review`
- 「考我 / 知识复盘 / 复习课程」→ `learn-assistant`
- 「审计 Epic / 检查开发流程」→ `dev-lifecycle-audit-assistant`

## 三种模式

| 模式 | 触发 | 输出存放 |
|------|------|----------|
| 日报 | 日报、今日总结、整理今天的工作 | `Contexts/日报/YYYY-MM-DD.md` |
| 周报 | 周报、本周总结、整理这周的工作 | `Contexts/周报/YYYY-MM-DD至YYYY-MM-DD.md` |
| 月度复盘 | 复盘、月度总结、本月回顾 | `Contexts/复盘/YYYY-MM.md`（可选） |

## 本人 Git 筛选（必守）

- **只统计本人提交**，不列他人 commit。
- 作者匹配：`git log --author="wanglongxiang"`（邮箱常为 `wanglongxiang@360.cn`）；若曾用中文名则加 `--author="王龙祥"`。
- 仓库当天仅有他人提交 → **该仓库不列入**。
- 本人无 commit 但有 Cursor plan / Kit 工作 → 写在「Cursor（plan / 未合入）」，不冒充代码提交。

## 正文规范（必守）

- **只写工作内容**：做了什么、产出在哪、明日接续。
- **不要写**：统计规则、作者筛选、`git log` 用法、生成命令、存放路径等元信息。
- 某仓库当天没你的事 → **整段不写**。
- 章节编号用 **一、二、三…**（从一起）。

## 模式 A：日报

1. 日期默认今天。
2. 扫 `~/git/*`：`git log --author=wanglongxiang`（+王龙祥）；只列本人有 commit 或未提交改动的仓库。
3. 扫 Kit 当日 `Plans/`、学习、协作产出。
4. 按 `Templates/日报模板.md` 生成 → 写入 `Contexts/日报/YYYY-MM-DD.md`。

## 模式 B：周报

1. 时间段：默认本周一至今天；或用户指定。
2. 汇总 `Contexts/日报/` 该时段日报，无日报的日期不列。
3. `git log --since --until --author=wanglongxiang` 统计本人 commit，按主题合并。
4. 扫描本周 `Plans/`、`Contexts/`、Skill/模板变更、学习进度。
5. 按 `Templates/周报模板.md` 生成 → 写入 `Contexts/周报/起始日至结束日.md`。

## 模式 C：月度复盘

1. 搜索该月 `Plans/`、`Contexts/`、日报、周报材料。
2. 分类顺利 / 踩坑；统计续做、模板、材料复用。
3. 按 `Templates/月度复盘模板.md` 输出 → 可选 `Contexts/复盘/YYYY-MM.md`。

## 反馈

`utility` 只能是 `high` 或 `not-needed`。产出在 `Contexts/` 而非 plan，追加到 `Contexts/决策/孤立反馈记录.md` 顶部（`plan: orphan`）；协议见 `Contexts/决策/Skill反馈协议.md`。
