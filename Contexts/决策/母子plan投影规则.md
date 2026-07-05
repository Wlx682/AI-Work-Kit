---
tags: [决策, 协议, Epic, WBS, 看板]
date: 2026-06-25
key_points:
  - 子 plan 是 WBS 状态/备注的唯一真理源，Epic 看板是只读投影
  - 看板状态三态：[x] 全完成 / [~] 部分（必须挂分项链接）/ [ ] 未开始
  - 禁止 [ ] + 备注 ✅ 这种半完成压扁；半完成必须用 [~] 显式表达
  - 子 plan 拆分切片（5→Mock/Http、6→a/b/c）时母 plan 必须同步拆或指针化
  - plan-gate-check.sh 校验 Epic 看板与子 plan 一致性，冲突即不通过
relations:
  depends_on:
    - Contexts/决策/Kit核心原则.md
    - Templates/模板约定.md
  dependents: []
  supersedes: []
  superseded_by: []
  conflicts: []
---

# 母子 plan 投影规则

> Epic 母 plan 与各子 plan（需求/方案/开发/测试/部署）之间状态与备注的真理源、状态机、门禁。  
> 本文件是 [[Contexts/决策/Kit核心原则]] §十 的细则展开。

---

## 一、为什么需要

Epic 母 plan 内的 WBS 看板与子 plan 的详细切片各自维护、各自演化，没有真理源约定时会出现「同一切片在两处状态不一致」的撒谎态。

**触发事件**（2026-06-25）：`Plans/Epic/2026-06-25-纳米P视频Web.md` WBS#5 写 `[ ] … （Mock ✅ · Http 待 WBS#10）`，而子 plan `Plans/功能开发/2026-06-25-纳米P视频Web.md` 写 `部分（6/8 Mock，缺 Effect/Payment）`。看板备注的 `Mock ✅` 把"6/8"压扁成"全完成"，Agent 读 Epic 单层就回报 WBS#5 完成。

根因：缺少「谁是真理源 / 半完成如何表达 / 粒度如何对齐 / 一致性谁校验」四项规则。本文件立此四规。

---

## 二、规则 01 · 单一真理源

| 字段 | 真理源 | 投影方 |
|------|--------|--------|
| WBS 切片状态（完成/进行/未开始） | **子 plan** §三 WBS 表 | Epic §三 WBS 看板 |
| 切片备注（卡点/分项/进度文字） | **子 plan** | Epic 看板**不得**写备注简写 |
| 切片验收 | **子 plan**（结合 Epic §二 阶段门禁） | Epic 看板仅复述符号 |

**硬规则**：

- Epic 看板内任何一行 WBS 的状态与备注，**必须**能在某个子 plan 内找到一对一对应行；找不到即视为脱节，门禁不通过。
- Epic 看板**不得**承载"子 plan 没写、由母 plan 独立判断"的状态。需要新增状态，先改子 plan。
- 母 plan 仅有一项例外可独立维护：跨子 plan 的**阶段门禁勾选**（Epic §二），它本就不属于任何单一子 plan。

---

## 三、规则 02 · 状态机三态

| 符号 | 含义 | 何时可用 |
|------|------|----------|
| `[x]` | 切片**全部分项**已完成且子 plan 标 ✅ | 子 plan 该切片每个分项均为 ✅ |
| `[~]` | 切片**部分完成 / 进行中** | 子 plan 该切片至少 1 项未完成；**必须**在同行内写明"分项见子 plan §X"或挂出 a/b/c 子项 |
| `[ ]` | 未开始 | 子 plan 该切片全部 ⬜ |

**硬规则**：

- 禁止 `[ ] 切片名 …（Mock ✅）` 这类「状态格未勾 + 备注里偷偷写完成」的压扁写法。半完成的合法表达只有 `[~]`。
- 禁止裸 `[~]`。`[~]` 必须配两选一：（a）在母 plan 同行拆出分项行（如 5a/5b）；（b）写 `分项见 [[子 plan]] §三`。
- 切片包含部分完成、部分未做的情况一律 `[~]`，不允许任由勾选人凭"感觉接近完成"标 `[x]`。

---

## 三·补 规则 02b · 子 plan WBS 状态的唯一格式 = fenced checklist

子 plan §三 的 WBS 切片状态**必须**写成 fenced 代码块内的 `[x] N. 描述`（与 Epic 全局切片号一致），**禁止用表格承载切片状态**。

| | 合法 | 非法 |
|---|------|------|
| 形态 | ` ``` ` 内 `[x] 6. Domain 实现` | `\| 6 \| Domain \| ✅ \|` |

**为什么**（2026-07-05 踩坑）：`gate_parse.wbs_slice_status`（门禁）与 `kanban-server`（看板）、`validate-epic-projection`（投影校验）三处都要按切片号定位状态行。表格首列同为数字，会产生两类歧义：（a）同一子 plan 多张表（输入输出表 vs 状态表）首列都有 `5`，解析器撞上错的一张；（b）跨子 plan 同号（技术方案的"实施阶段 1-6"、测试的用例号）被误当 Epic 切片。fenced `[x] N.` 是模板既定形态、无歧义，故立为**唯一权威源**。

**硬规则**：

- 三处解析器（`gate_parse` / `kanban-server` / `validate-epic-projection`）均**只认 fenced checklist**，不再读表格。旧 plan 用表格的须迁移为 fenced。
- 输入输出/拆分说明等**非状态**表可保留，但不得作为状态判定来源。
- 看板派生仅对 development 阶段切片从功能开发子 plan 取值（该阶段按约定沿用 Epic 全局切片号）；其余阶段与查无该号时回退 Epic 字面量，避免误匹配。

---

## 四、规则 03 · 粒度对齐

当子 plan 把母 plan 的某一切片拆成更细分项（如 `#5 → 5a Mock / 5b Http`、`#6 → 6a 首页 / 6b 视频生成 / 6c 特效`），母 plan **必须**二选一同步：

1. **同步拆**：Epic §三 WBS 看板也拆出 5a/5b 或 6a/6b/6c 同名行，每行独立状态符号。
2. **指针化**：保留母 plan 单行，但状态用 `[~]`，行内文字只写 `分项见 [[子 plan]] §三`，**不写**任何状态简写如 ✅。

**禁止**：母 plan 单行内塞分项简写（如 `Mock ✅ · Http 待 #10`）。这是本次撒谎态的直接成因。

---

## 五、规则 04 · 门禁一致性校验

`scripts/plan-gate-check.sh` 在跑 Epic plan 或任何带 `epic:` frontmatter 的子 plan 时，**会**额外执行以下校验（**已实现**于 `scripts/validate-epic-projection.py`，规则 A–E 与下表一一对应）：

| 校验项 | 不通过条件 |
|--------|------------|
| 状态映射 | Epic 看板某行 `[x]` 但子 plan 同切片任一分项非 ✅ |
| 状态映射 | Epic 看板某行 `[ ]` 但子 plan 同切片任一分项已 ✅ |
| 状态映射 | Epic 看板某行 `[~]` 但既无 a/b/c 分项行、也无"分项见 [[…]]" 指针 |
| 备注一致 | Epic 看板行内出现 `✅` / `完成` / `done` 等完成态字眼，但同切片在子 plan 仍有未完成分项 |
| 粒度对齐 | 子 plan 拆出分项（如 6a/6b/6c），但母 plan 既未拆行也未指针化 |

实现：`scripts/validate-epic-projection.py`（与 `validate-skill-run.py` 同级）解析母 plan §三 看板与各子 plan §三 WBS 表，比对状态符号与备注关键字；命中任一规则输出 `BLOCKED:epic-projection:<原因>` 并以退出码 1 失败，由 `plan-gate-check.sh` 在门禁阶段调用。路由：plan 在 `Plans/Epic/` 或带 `epic:` 字段才校验，其余跳过。

单独运行：

```bash
python3 scripts/validate-epic-projection.py Plans/Epic/xxx.md
python3 scripts/validate-epic-projection.py --require Plans/功能开发/xxx.md   # 强制要求有 epic 链接
```

---

## 六、应用到本次事件的修正

| 位置 | 改前 | 改后（合法形态） |
|------|------|------------------|
| Epic §三 WBS 看板 第 5 行 | `[ ] 5. Data 层 / API 对接（Mock ✅ · Http 待 WBS#10）` | `[~] 5. Data 层 / API 对接（分项见 [[Plans/功能开发/2026-06-25-纳米P视频Web]] §三）` |
| Epic §三 WBS 看板 第 6 行 | `[ ] 6. UI 骨架（1:1 · figma-ui）— 6a 首页骨架 ✅ · 6b 生视频进行中` | 同步拆为 `[x] 6a 首页 UI` / `[~] 6b 视频生成 UI` / `[ ] 6c 特效玩法 UI` 三行 |

修正何时执行：等用户在本次根因讨论收尾后另行授权再改 Epic plan；本规则文件本身不直接改 plan。

---

## 七、相关

- [[Contexts/决策/Kit核心原则]] §十
- [[Templates/模板约定]]
- [[Contexts/决策/AI-Work-Kit工作流总览]]
- [[Contexts/决策/Skill反馈协议]]
