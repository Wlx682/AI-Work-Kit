# 复盘助理 Skill

## 触发条件

当用户说以下任一时执行：

- **日报 / 周报类**：「日报」「周报」「今日总结」「本周总结」「整理今天/这周的工作」
- **项目复盘类**：「**项目复盘**」「**迭代回顾**」「**月度复盘**」「**本月回顾**」
- **代码审查类**：「Code Review」「review 这个 diff」「审查 PR」「UI 复核」「回归复核」或 workflow review 阶段
- `/review-assistant` / `/review` 命令

**不响应（让位给其他 Skill）**：

- 「考我 / 知识复盘 / 复习课程」→ `learn-assistant`（学习场景的「复盘」）
- 「审计 Epic / 检查开发流程」→ `dev-lifecycle-audit-assistant`

## 本人 Git 筛选（必守）

- **只统计本人提交**，不列他人 commit。
- 作者匹配：`git log --author="wanglongxiang"`（邮箱常为 `wanglongxiang@360.cn`）；若曾用中文名则加 `--author="王龙祥"`。
- 仓库今日仅有他人提交 → **该仓库不列入**（不写「别人提交了啥」）。
- 本人无 commit 但有 Cursor plan / Kit 工作 → 写在「Cursor（plan / 未合入）」，不冒充代码提交。

### 日报 / 周报正文规范（必守）

- **只写工作内容**：做了什么、产出在哪、明日接续。
- **不要写**：统计规则、作者筛选、`git log` 用法、生成命令、存放路径、「不列入」「他人提交」等元信息。
- 某仓库当天没你的事 → **整段不写**，不必解释为什么没写。
- 章节编号用 **一、二、三…**（从一起），不用「零、」或阿拉伯 `0.`。

## 三种模式

| 模式 | 触发 | 输出存放 |
|------|------|----------|
| **日报** | 日报、今日总结、整理今天的工作 | `Contexts/日报/YYYY-MM-DD.md` |
| **周报** | 周报、本周总结、整理这周的工作 | `Contexts/周报/YYYY-MM-DD至YYYY-MM-DD.md` |
| **月度复盘** | 复盘、月度总结、本月回顾 | `Contexts/复盘/YYYY-MM.md`（可选） |
| **Code Review** | diff、PR、分支、UI 复核、回归复核 | `Plans/代码重构/` 或调用方 plan |

---

## 模式 A：日报

1. 日期默认今天。
2. 扫 `~/git/*`：`git log --author=wanglongxiang`（+王龙祥）；**只列本人**有 commit 或未提交改动的仓库。
3. 扫 Kit 当日 `Plans/`、学习、协作产出。
4. 按 `Templates/日报模板.md` 生成 → **写入** `Contexts/日报/YYYY-MM-DD.md`。

```
/review-assistant 日报
/review-assistant 日报，日期=2026-06-10
```

---

## 模式 B：周报

1. **时间段**：
   - 默认 **本周一 00:00 至今天**（本地日期）
   - 或用户指定：`周报，时间段=2026-06-03 至 2026-06-09`
2. **汇总日报**：读取 `Contexts/日报/` 该时段内已有日报，填入「日报索引」；**无日报的日期不列**。
3. **扫描代码仓库**：`~/git/*` 用 `git log --since --until --author=wanglongxiang` 统计**本人**本周 commit
   - **只列本人有 commit 的仓库**；按主题合并，不逐条堆 hash；**不列他人提交**
   - 未提交改动：仅本人有则注明
4. **扫描 Kit**：本周 `Plans/`、`Contexts/`（除日报/周报自身）、Skill/模板变更、学习进度。
5. 按 `Templates/周报模板.md` 生成 → **写入** `Contexts/周报/起始日至结束日.md`。
6. 回复：文件路径 + 一周摘要 + 下周 P0。

```
/review-assistant 周报

/review-assistant 周报，时间段=2026-06-03 至 2026-06-09
```

---

## 模式 C：月度复盘

1. 搜索 `Plans/`、`Contexts/`、`Contexts/日报/`、`Contexts/周报/` 该月材料。
2. 分类顺利 / 踩坑；统计续做、模板、材料复用。
3. 按 `Templates/月度复盘模板.md` 输出 → 可选 `Contexts/复盘/YYYY-MM.md`。

```
/review-assistant 复盘时间段=2026-06-01 至 2026-06-30
```

材料不足时，请用户补充主要任务。

---

## 模式 D：Code Review

当输入是 diff / PR / 分支 / workflow review 阶段时，按代码审查模式输出：

1. Findings first：问题列表在前，摘要在后。
2. 按严重级排序：阻塞 / 高 / 中 / 建议。
3. 每个问题尽量给文件和行号；无法定位时说明证据来源。
4. 没发现问题也要明确说“未发现阻塞问题”，并补充测试缺口或残余风险。
5. 不使用日报、周报、项目复盘模板。

Smoke test：

```bash
python3 scripts/skill-smoke-test.py review-assistant tests/fixtures/skills/review-assistant/risky-diff.input.md
```

## 原子契约

| 字段 | 要求 |
|------|------|
| 输入 | diff、PR、分支、审查范围；或日报/周报材料 |
| 输出 | Findings-first review 结论；或日报/周报/复盘文件 |
| 门禁 | 代码审查有严重级、文件/行号、测试风险；日报周报正文不含元信息 |
| 越界 | 需要实现修复时转功能开发或 bugfix 流程 |
| smoke | `python3 scripts/skill-smoke-test.py review-assistant tests/fixtures/skills/review-assistant/risky-diff.input.md` |

---

## 沉淀原则

| 类型 | 路径 | 规则 |
|------|------|------|
| 日报 | `Contexts/日报/` | 每天一篇，长期沉淀 |
| 周报 | `Contexts/周报/` | 每周一篇，引用日报；无变化仓库不列 |
| 月度 | `Contexts/复盘/` | 可引用本周报 + 日报 |

不替代 `Plans/` 进行中任务。
