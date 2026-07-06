---
tags: [决策, 协议, 反馈回路, 工作流]
date: 2026-06-24
status: 已采纳
key_points:
  - 写入位置：有 plan 则追加到 plan 末尾；无 plan 且未归位则写入 Contexts/决策/孤立反馈记录.md 的「待整理」
  - 无 plan 但已当场归位则只在 Contexts/决策/孤立反馈记录.md 的「已归位」补一行摘要
  - 格式必须 fenced ```yaml 代码块，不用裸 --- frontmatter 避免双 fm 冲突
  - utility 字段二选一：high（必须附 reason 一句话）或 not-needed
  - 必填字段：skill / plan / date / contexts_used / contexts_missing / contexts_stale
  - 校验由 scripts/validate-skill-run.py 执行，plan-gate-check.sh 对所有 plan 全量强制
  - 月度聚合：scripts/feedback-aggregate.py，挂到月度复盘模板 §六
relations:
  depends_on:
    - Contexts/决策/Kit核心原则.md
  dependents:
    - Contexts/决策/Skill原子契约.md
  supersedes: []
  superseded_by: []
  conflicts: []

---
# Skill 反馈协议

> **全库唯一定义**：每个 Skill 完成任务时如何输出反馈数据，由 `scripts/feedback-aggregate.py` 聚合，月度复盘消费。
> 与 [[Contexts/决策/Kit核心原则]] 的“反馈闭环原则”联动；任何 Skill 修改不得违反本协议。

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
| 任务无 plan，且产生了尚未归位的规则/模板/脚本候选 | 写入 `Contexts/决策/孤立反馈记录.md` 的 `## 待整理` |
| 任务无 plan，但反馈已当场归位（已写入规则/脚本/审计报告） | 不进入 `## 待整理`；只在 `Contexts/决策/孤立反馈记录.md` 的 `## 已归位` 补一行摘要 |

**`Contexts/决策/孤立反馈记录.md`** 只保留两个一级区：`## 待整理` 和 `## 已归位`。`待整理` 放仍需决策/落地的候选；`已归位` 放一句话摘要，指向最终承载位置。

**已归位例外**：如果本次反馈只是执行小票（例如“我用了某审计报告来更新某结论”），且真正结论已经写入长期文件、模板、Skill 或自动化脚本，则不要再把这张小票放进 `待整理`，也不要保留完整过程 YAML。只在 `已归位` 保留一句摘要，指向最终承载位置。目标是让知识库保存“以后怎么用”，而不是保存“这次我怎么操作”。

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
  # ↓ 可选：本次执行质量/流程信号（扁平键，供 evolution 优化流程，非 Contexts 健康度）
  outcome_status: pass                  # 可选：pass | blocked | partial —— 这次任务到底成没成
  friction: "figma 验证子Agent 拿不到聊天内截图，需先落盘"  # 可选：哪个环节掉链子，一句话；无则省略
  verdict_score: 3.5                    # 可选：0-10，对接对抗验证裁决分；无验证环节则省略
  revisit_needed: false                 # 可选：是否需回退上一阶段 true | false
  revisit_reason: ""                    # 可选：revisit_needed=true 时填一句话
```
````

**执行质量字段的设计意图**：原有字段监测「Contexts 引用健康度」；`outcome_status` / `friction` / `verdict_score` / `revisit_*` 监测「这次任务/流程本身的质量」，让 `workflow-evolution-assistant` 能识别「哪个 Skill/阶段失败率高、哪里反复卡点、验证分是否走低、哪个阶段常返工」，从而建议流程调整——而非只改 Contexts。**全部可选、扁平键**（不嵌套，兼容零依赖解析器；不增加填表负担）；填了才参与聚合。

**孤立反馈记录格式**（无 plan 时写入 `Contexts/决策/孤立反馈记录.md`）：

- `## 待整理`：只写仍需处理的候选，标题用 `### 进化候选：...` 或 `### 待整理：...`，正文保留证据、归位方向、验收方式；不要写已完成的过程留痕。
- `## 已归位`：每条一行摘要，格式 `- **YYYY-MM-DD** 事项已归位：落点 + 验证方式`；不保留完整 skill_run YAML。

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
| `outcome_status` | 若填，**三选一**：`pass` / `blocked` / `partial` | `validate-skill-run.py` |
| `verdict_score` | 若填，0-10 数字 | `validate-skill-run.py` |
| `revisit_needed` | 若填，布尔 `true` / `false` | `validate-skill-run.py` |
| `friction` / `revisit_reason` | 可选字符串；无则省略 | — |

**执行质量字段全部可选**：不填不报错（旧 plan、无流程信号的一次性任务不受影响）。一旦填了则按上表约束校验取值域，防脏数据。字段扁平（不嵌套），兼容零依赖解析器。

**`utility` 二选一的设计意图**：四选一会催生 `medium` 类垃圾数据。强制 Agent 表态：要么 high（必给理由），要么 not-needed（说明"我看了但没用上"或"我没读但默认列表里"）。

---

## 五、聚合规则（feedback-aggregate.py 月度执行）

| 输出分组 | 触发条件 |
|---------|----------|
| **本月热点 Contexts** | `utility=high` 累计 ≥ 3 次 |
| **冷却候选** | 最近 90 天内无任何 `utility=high` 引用 |
| **漂移告警** | `contexts_stale` 同一 path 累计 ≥ 2 次 |
| **补全候选** | `contexts_missing` 同语义（去重后）累计 ≥ 2 次 |
| **失败热点** | 同一 `skill` 的 `outcome_status` ∈ {blocked, partial} 累计 ≥ 2 次 |
| **返工热点** | 同一 `skill` 的 `revisit_needed=true` 累计 ≥ 2 次 |
| **卡点清单** | 所有非空 `friction`（按 skill 归组，供人工读） |

聚合脚本扫描范围：所有 `Plans/**/*.md` + `Contexts/决策/孤立反馈记录.md`。
输出文件：`Contexts/决策/反馈聚合-YYYY-MM.md`（与月度复盘同月）。

---

## 六、全量强制约定

| 项 | 值 |
|---|---|
| 生效范围 | 所有写入 `Plans/**/*.md` 的 Skill 任务 |
| 生效时间 | 2026-07-03 起 |
| 机械门禁 | `bash scripts/plan-gate-check.sh <plan.md>` 默认要求 `skill_run` 存在且合法 |
| 无 plan 任务 | 未归位候选写入孤立反馈 `## 待整理`；已归位只写 `## 已归位` 一行摘要 |
| 已归位例外 | 反馈结论已写入规则/脚本/审计报告时，不写完整过程小票，只在孤立反馈 `## 已归位` 补摘要 |
| 历史 plan | 不主动补旧账；下次续做或过门禁时补齐 |

---

## 七、相关

- [[Contexts/决策/Kit核心原则]]
- [[Templates/月度复盘模板]]（消费聚合报告）
- `scripts/plan-gate-check.sh`（结构校验）
- `scripts/feedback-aggregate.py`（聚合）
