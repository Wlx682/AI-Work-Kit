---
name: task-splitter
description: 将技术方案拆为 5-10 原子任务，主 plan + 子任务 plan 写入 Plans/功能开发/。触发词：任务拆分、拆任务、task-splitter。
---

# 任务拆分助手

输入：`Plans/技术方案/`（已采纳）  
产出：`Plans/功能开发/YYYY-MM-DD-模块.md` + `xxx-子任务NN-简述.md`

契约：`Contexts/决策/Skill原子契约.md`

1. 读方案 + 需求真理源  
2. 5–10 原子任务，主 plan Checklist 双链子任务；§五实施切片表必须保留「覆盖 AC」列  
3. 子任务 `parent:` 链主 plan；`lifecycle_state: development`  
4. 实现：`/resume plan=子任务路径`

「覆盖 AC」列填写需求验收标准 ID，多个用英文逗号分隔，如 `AC1, AC2, AC1-反`；无覆盖填 `—`。P0 AC 必须至少被一个功能开发任务覆盖。

## ✋ 禁止擅自下结论（硬规则）

- 拆解与 WBS 修订时，**禁止**输出「我推荐方案 A/B/C」式单方面定论。
- 信息不足或拆分边界不清 → **暂停**，列出待确认项找用户；或建议先走 `requirement-analyst` 闭环 P0。
- Epic WBS 表结构变更须经本 Skill 产出 plan **或**用户书面确认后再写回 Epic。

同步：`Skills/task_splitter.md`

## 原子契约

| 字段 | 要求 |
|------|------|
| 输入 | 已采纳技术方案、Epic 或明确目标范围 |
| 输出 | 5-10 个原子任务，必要时写主 plan 与子任务 plan |
| 门禁 | 每个任务有输入、输出、验收、依赖；不混职责 |
| 越界 | WBS 方案不明确时请求用户确认，不擅自推荐 A/B/C |
| smoke | `python3 scripts/skill-smoke-test.py task-splitter tests/fixtures/skills/task-splitter/checkout-tech-plan.input.md` |

## 反馈回路（skill_run）

完成任务的最后一步**必须**输出 `skill_run` 反馈（协议：`Contexts/决策/Skill反馈协议.md`）：
追加到本次 拆分产出的主 plan（`Plans/功能开发/`） **末尾**的 `## 反馈（skill_run）` 节（fenced ```yaml`，非裸 frontmatter）。
`contexts_used[].utility` 二选一：`high`（附一句话 `reason`）或 `not-needed`；必填 `skill: task-splitter` / `plan` / `date` / `contexts_used` / `contexts_missing` / `contexts_stale`。缺则 `plan-gate-check.sh` 报失败。
