---
tags: [决策, 协议, Epic, WBS, 看板]
date: 2026-06-25
key_points:
  - 子 plan 是 WBS 状态的唯一真理源；Epic §三 看板是从子 plan 事实单向派生渲染的产物，不得手写
  - 看板状态三态：[x] 全完成 / [~] 部分（必须挂分项链接）/ [ ] 未开始，由 render-epic-board.py 派生
  - 禁止 [ ] + 备注 ✅ 这种半完成压扁；半完成必须用 [~] 显式表达
  - 子 plan WBS 状态唯一格式 = fenced checklist `[x] N. 描述`，禁止用表格承载切片状态
  - pre-commit（render-epic-board.py --check）在提交时校验看板新鲜度，漂移即拦截；render --write 刷新
relations:
  depends_on:
    - Contexts/决策/Kit核心原则.md
    - Templates/模板约定.md
  dependents: []
  supersedes: []
  superseded_by: []
  conflicts: []
---

# 母子 plan 投影规则（派生渲染）

> Epic §三 WBS 看板与各子 plan（需求/方案/开发/测试/部署）之间的真理源、派生渲染机制、门禁。
> 本文件是 [[Contexts/决策/Kit核心原则]] §十 的细则展开。

> **演进（2026-07-06）**：从「双写 + 一致性校验」升级为「单向派生渲染」。Epic §三 看板不再手写、
> 不再有独立的 `validate-epic-projection.py` 一致性校验（曾因读错章节长期空转）与 PostToolUse hook；
> 改为 `scripts/render-epic-board.py` 从子 plan 事实派生看板标记，pre-commit 在提交时校验新鲜度。
> 消灭了「两份手写状态」这一漂移根源本身——没有第二份手写状态，就没有母子不一致。

---

## 一、为什么需要

Epic 母 plan 内的 WBS 看板与子 plan 的详细切片，若各自手写维护，会出现「同一切片在两处状态不一致」的撒谎态。

**触发事件**（2026-06-25）：`Plans/Epic/2026-06-25-纳米P视频Web.md` WBS#5 写 `[ ] … （Mock ✅ · Http 待 WBS#10）`，而子 plan 写 `部分（6/8 Mock，缺 Effect/Payment）`。看板备注把"6/8"压扁成"全完成"，Agent 读 Epic 单层就回报 WBS#5 完成。

**根本解法**（2026-07-06）：不是「校验两份是否一致」，而是「只保留一份手写事实（子 plan），Epic 看板从它派生」。这样从结构上就不可能漂移。

---

## 二、规则 01 · 单一真理源与派生

| 字段 | 真理源（唯一手写） | 派生方（自动渲染，禁手写） |
|------|--------|--------|
| WBS 切片状态（完成/进行/未开始） | **子 plan** §WBS fenced checklist | Epic §三 WBS 看板（`render-epic-board.py` 渲染） |
| 切片验收 | **子 plan**（结合 Epic §二 阶段门禁） | Epic 看板仅复述符号 |

**硬规则**：

- Epic §三 看板的每行 `[标记]` 由 `render-epic-board.py` 从子 plan 事实派生，**不得手写改动**。手改会被 pre-commit 的新鲜度校验拦截。
- 派生来源（防第三份真理源）：每个切片按其「归属 stage」的子 plan——若该子 plan 有 fenced `[N.]` checklist 行，直接采其状态（复用 `gate_parse.wbs_slice_status`，与 workflow-gate / kanban-server 同一读法）；否则回退到 stage 级完成度（由 `workflow-gate.sh --probe` 判定）。
- 母 plan 仅有一项例外可独立维护：跨子 plan 的**阶段门禁勾选**（Epic §二），它本就不属于任何单一子 plan。

---

## 三、规则 02 · 状态机三态

| 符号 | 含义 | 派生条件 |
|------|------|----------|
| `[x]` | 切片已完成 | 子 plan 该切片 fenced 行为 `[x]`，或该 stage 已通过门禁 |
| `[~]` | 切片部分完成 / 进行中 | 子 plan 该切片 fenced 行为 `[~]` |
| `[ ]` | 未开始 | 子 plan 该切片 fenced 行为 `[ ]`，或该 stage 尚未开始 |

**硬规则**：

- 半完成的合法表达只有子 plan 里的 `[~]`；派生后 Epic 看板同步显示 `[~]`。
- 带后缀切片（6a/6b）不自动派生改写（与 `kanban-server.toggle_slice` 拒绝子项一致），需人工在 Epic 维护并保持与子 plan 对齐。

---

## 三·补 规则 02b · 子 plan WBS 状态的唯一格式 = fenced checklist

子 plan 的 WBS 切片状态**必须**写成 fenced 代码块内的 `[x] N. 描述`（与 Epic 全局切片号一致），**禁止用表格承载切片状态**。

| | 合法 | 非法 |
|---|------|------|
| 形态 | ` ``` ` 内 `[x] 6. Domain 实现` | `\| 6 \| Domain \| ✅ \|` |

**为什么**（2026-07-05 踩坑）：`gate_parse.wbs_slice_status`（门禁）、`kanban-server`（看板）、`render-epic-board`（派生）三处都要按切片号定位状态行。表格首列同为数字，会产生两类歧义：（a）同一子 plan 多张表首列都有 `5`，撞上错的一张；（b）跨子 plan 同号被误当 Epic 切片。fenced `[x] N.` 是模板既定形态、无歧义，故立为**唯一权威源**。

**硬规则**：

- 三处解析器（`gate_parse` / `kanban-server` / `render-epic-board`）均**只认 fenced checklist**。旧 plan 用表格的须迁移为 fenced（2026-07-06 已迁移首页测试子 plan §七）。
- 输入输出/拆分说明等**非状态**表可保留，但不得作为状态判定来源。

---

## 四、规则 03 · 粒度对齐

当子 plan 把母 plan 的某一切片拆成更细分项（如 `#6 → 6a 首页 / 6b 视频生成`），母 plan §三看板须保留对应的 a/b/c 分项行（派生不自动改写后缀行）。**禁止**母 plan 单行内塞分项简写（如 `Mock ✅ · Http 待 #10`）。

---

## 五、规则 04 · pre-commit 新鲜度门禁

`scripts/render-epic-board.py` 是唯一的看板派生/校验入口，三种模式：

| 模式 | 行为 |
|------|------|
| （无参数） | dry-run：打印派生后的 §三，不落盘 |
| `--write` | 从子 plan 派生并写回 Epic §三 |
| `--check` | 校验：§三 与派生不一致（漂移）退出 1；一致退出 0；基础设施失败退出 2（放行不阻断） |

`scripts/pre-commit-relations.sh`（安装为 `.git/hooks/pre-commit`）在提交时：暂存区含 Epic 或带 `epic:` 字段的子 plan → 回扫其 Epic 跑 `--check`，漂移即拦截 commit，提示跑 `--write` 刷新。

> ⚠️ **不得**在 `plan-gate-check.sh` 里调用 `render-epic-board.py`：后者会跑 `workflow-gate.sh`，而 development 阶段的 `planGateCheck` 又回调 `plan-gate-check.sh`，形成无限递归。派生渲染的唯一门禁入口是 pre-commit。

单独运行：

```bash
python3 scripts/render-epic-board.py Plans/Epic/xxx.md            # dry-run 预览
python3 scripts/render-epic-board.py Plans/Epic/xxx.md --write    # 刷新看板
python3 scripts/render-epic-board.py Plans/Epic/xxx.md --check    # 校验新鲜度
```

---

## 六、相关

- [[Contexts/决策/Kit核心原则]] §十
- [[Templates/模板约定]]
- [[Contexts/决策/AI-Work-Kit工作流总览]]
- [[Contexts/决策/Skill反馈协议]]
