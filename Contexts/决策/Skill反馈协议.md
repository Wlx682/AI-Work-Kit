---
tags: [决策, 协议, 反馈回路, 工作流]
date: 2026-06-24
status: 已采纳
key_points:
  - 写入位置：有 plan 则追加到 plan 末尾；无 plan 则追加到 Contexts/决策/孤立反馈记录.md 顶部
  - 格式必须 fenced ```yaml 代码块，不用裸 --- frontmatter 避免双 fm 冲突
  - utility 字段二选一：high（必须附 reason 一句话）或 not-needed
  - 必填字段：skill / plan / date / contexts_used / contexts_missing / contexts_stale
  - 校验由 scripts/validate-skill-run.py 执行，门禁在 plan-gate-check.sh
  - 月度聚合：scripts/feedback-aggregate.py，挂到月度复盘模板 §六
relations:
  depends_on:
    - Contexts/决策/Kit核心原则.md
  dependents: []
  supersedes: []
  superseded_by: []
  conflicts: []
---

# Skill 反馈协议

> **全库唯一定义**：每个 Skill 完成任务时如何输出反馈数据，由 `scripts/feedback-aggregate.py` 聚合，月度复盘消费。
> 与 [[Contexts/决策/Kit核心原则]] §九 联动；任何 Skill 修改不得违反本协议。

---

## 一、为什么需要

没有这一层，整个 Vault 是单向写入系统：你不知道哪个 Contexts 文件被频繁引用、哪个长期睡死、哪些内容**应该有但缺失**、哪些与现网已脱钩。反馈回路 = Vault 的心跳监测。

---

## 二、何时输出

**强制时机**：每个 Skill 完成任务的最后一步。
**强制写入位置**：

| 场景 | 写到哪 |
|------|--------|
| 任务对应 plan 存在 | 该 plan 文件**末尾**追加 `skill_run` YAML 块 |
| 任务无 plan（如 `template-generator` 一次性输出、`learn-assistant` 续读不写 plan）| `Contexts/决策/孤立反馈记录.md` 顶部追加一条 |

**`Contexts/决策/孤立反馈记录.md`** 倒序排列（最新在上），每条独立 YAML 节，便于 `feedback-aggregate.py` 同一脚本扫描。

---

## 三、YAML Schema（强制结构）

> **写入格式**：fenced ` ```yaml ... ``` ` 代码块，**不**用裸 `--- ... ---`（避免被解析为第二段 frontmatter）。
> **位置**：plan 文件末尾追加一节 `## 反馈（skill_run）`，节内嵌 yaml 代码块。

````markdown
## 反馈（skill_run）

```yaml
skill_run:
  skill: requirement-analyst            # 必填：dash-form 名称，与 .cursor/skills/<name>/ 一致
  plan: Plans/需求分析/2026-06-24-xxx.md  # 必填：本次 plan 路径；无 plan 时填 "orphan"
  date: 2026-06-24                      # 必填：YYYY-MM-DD
  contexts_used:                        # 必填：本次实际引用的 Contexts 文件清单，按 utility 倒序
    - path: Contexts/需求分析/需求分析规范.md
      utility: high                     # 二选一: high | not-needed
      reason: "对照 §3.1-3.6 扫遗漏类别"  # utility=high 必填一句话理由；utility=not-needed 时省略
    - path: Contexts/需求分析/示例-创建自动化任务-PRD问题模式.md
      utility: high
      reason: "对照已知问题模式定位本次 PRD 漏洞"
    - path: Contexts/Figma/Figma界面开发最佳实践.md
      utility: not-needed               # 本次未读但 Skill 默认列表里 → 显式标 not-needed
  contexts_missing:                     # 可选：本次 PRD 涉及但 Contexts 没覆盖的主题（候选新建）
    - "埋点规范对照表（同类功能埋点字段标准）"
    - "灰度发布配置流程"
  contexts_stale:                       # 可选：本次发现 Contexts 与代码/现网脱钩的文件
    - path: Contexts/收银台/MSPay收银台配置对照表.md
      reason: "代码已上 v2 接口，文档仍 v1"
```
````

**孤立反馈记录格式**（无 plan 时写入 `Contexts/决策/孤立反馈记录.md`）：每条独立 `## 日期-skill` 标题 + 同样 yaml 代码块，倒序排列。

---

## 四、字段约束（硬规则）

| 字段 | 规则 | 校验位置 |
|------|------|----------|
| `skill` | dash-form；必须等于 `.cursor/skills/` 下某目录名 | `plan-gate-check.sh` |
| `plan` | 必须是仓库内真实路径或字符串 `"orphan"` | `plan-gate-check.sh` |
| `date` | YYYY-MM-DD；无校验业务含义 | — |
| `contexts_used[].utility` | **二选一**：`high` 或 `not-needed`；禁止 `medium` / `low` / `unknown` 等 | `plan-gate-check.sh` |
| `contexts_used[].reason` | `utility=high` 时**必填**且非空字符串 | `plan-gate-check.sh` |
| `contexts_used[].path` | 必须是仓库内真实存在的 `.md` 路径 | `plan-gate-check.sh` |
| `contexts_missing[]` | 字符串数组，每项 < 80 字符；可为空数组或省略 | — |
| `contexts_stale[].path` | 必须是仓库内真实路径 | `plan-gate-check.sh` |
| `contexts_stale[].reason` | 必填非空，说明脱钩证据 | `plan-gate-check.sh` |

**`utility` 二选一的设计意图**：四选一会催生 `medium` 类垃圾数据。强制 Agent 表态：要么 high（必给理由），要么 not-needed（说明"我看了但没用上"或"我没读但默认列表里"）。

---

## 五、聚合规则（feedback-aggregate.py 月度执行）

| 输出分组 | 触发条件 |
|---------|----------|
| **本月热点 Contexts** | `utility=high` 累计 ≥ 3 次 |
| **冷却候选** | 最近 90 天内无任何 `utility=high` 引用 |
| **漂移告警** | `contexts_stale` 同一 path 累计 ≥ 2 次 |
| **补全候选** | `contexts_missing` 同语义（去重后）累计 ≥ 2 次 |

聚合脚本扫描范围：所有 `Plans/**/*.md` + `Contexts/决策/孤立反馈记录.md`。
输出文件：`Contexts/决策/反馈聚合-YYYY-MM.md`（与月度复盘同月）。

---

## 六、试点期约定

| 项 | 值 |
|---|---|
| 试点 Skill | `requirement-analyst` |
| 试点周期 | 2026-06-24 起 / 至少 3 次真实任务，或 2 周（孰先达成）|
| 通过标准 | 试点期所有执行均通过 `plan-gate-check.sh` 校验，无手动补救 |
| 通过后 | 反馈章节推至全部 17 个 Skill |

---

## 七、相关

- [[Contexts/决策/Kit核心原则]] §九（反馈回路）
- [[Templates/月度复盘模板]]（消费聚合报告）
- `scripts/plan-gate-check.sh`（结构校验）
- `scripts/feedback-aggregate.py`（聚合）
