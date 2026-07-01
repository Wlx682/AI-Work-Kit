---
tags: [决策, 原则, 工作流]
date: 2026-06-20
key_points:
  - 三层存储：Templates 长期 / Plans 做完删 / Contexts 跨任务
  - 写 Contexts 前须用户确认（除非用户说「存档到 Contexts」）
  - Epic 是业务唯一母 plan，子 plan 通过 frontmatter `epic:` 反向链接
  - 阶段门禁：plan-gate-check.sh 卡 status / lifecycle_state / 反馈块
  - 反馈回路：每个 Skill 完成必须输出 skill_run（见 §九）
  - Plan Mode：重任务先只读探索+共创方案再动手；副作用动作硬闸门在 settings.json ask（见 §十一）
  - 关系图谱：frontmatter `relations:` 含 5 类双向关系
  - 母子 plan 投影：子 plan 是 WBS 真理源；看板用 [x]/[~]/[ ] 三态，禁备注偷藏完成态（见 §十）
relations:
  depends_on: []
  dependents:
    - Contexts/决策/AI-Work-Kit工作流总览.md
    - Contexts/决策/AI-Work-Kit架构总览.md
    - Contexts/决策/Contexts漂移检测协议.md
    - Contexts/决策/Skill反馈协议.md
    - Contexts/决策/关系图谱协议.md
    - Contexts/决策/对话用词习惯.md
    - Contexts/决策/新手引导与最佳实践.md
    - Contexts/决策/母子plan投影规则.md
    - Templates/模板约定.md
  supersedes:
    - Contexts/决策/资料与代码仓库边界.md
  superseded_by: []
  conflicts: []

---
# Kit 核心原则

> **全库唯一真相源。** 其它文件只负责「怎么用」，不得与本文件矛盾。  
> 细则索引见本文 §六。

---

## 一、一句话

**Vault 存模板与通用规范；`Plans/` 只放当前任务；业务代码在独立仓库。**  
Agent 读 Contexts 是为了**补通用上下文**，不是为了记住某个已做完的需求。

---

## 二、三层存储

| 层 | 路径 | 放什么 | 生命周期 |
|----|------|--------|----------|
| **模板** | `Templates/` | 各类 plan 骨架 | 长期，随 Kit 演进 |
| **进行中** | `Plans/` | 当前 Epic、需求、方案、开发、测试、部署、排查、学习 | **做完就删** |
| **通用资料** | `Contexts/` | 跨任务仍成立的事实与规范 | 长期 |
| **源码** | 业务仓库 | 代码、工程 README | 按项目 |

**代码仓禁止**：功能 plan、PM 对照表、排查 plan、工作流实施方案（工程 README 除外）。  
判断：**「我的工作流资产」→ Vault；「这个仓库怎么跑」→ 可留代码仓。**

---

## 三、Contexts 放什么（通用 / 固定）

**判定**：换一个新模块、新 Epic，Agent 读了**不会**误以为是当前任务背景 → 可以进 Contexts。

| 适合 | 路径示例 |
|------|----------|
| 设计 / 协作规范 | `Contexts/Figma/项目设计规范.md` |
| 概念、学习路线 | `Contexts/LLM学习/` |
| 多 App / 长期 PM 对照 | `Contexts/收银台/` |
| 决策、边界、本原则 | `Contexts/决策/` |
| 日报 / 周报 | `Contexts/日报/`、`周报/` |
| 可复用踩坑（抽象成一条教训） | `Contexts/踩坑/`（可选） |

| **禁止** | 原因 |
|----------|------|
| Figma **链接** | 当次对话 / 当次 plan 提供 |
| 某功能的节点度量表、差异表 | 任务细节 → `Plans/` |
| 走查截图、真机验收图 | 任务证据 → `Plans/` 或删 |
| 某 Epic / 某版本的进度、WBS 结论 | → `Plans/Epic/` |
| 学习进度快照文件 | → `Plans/学习/` 勾选 + 笔记 |
| 「已完成功能清单」 | 易误导后续对话 |

**Figma 实现**：读 **MCP 节点**，度量表写在 **Plans**；禁止靠截图估像素。  
**Contexts/Figma/** 只保留**规范与 MCP 说明**，不存走查记录目录。

---

## 四、Plans 放什么（任务 / 临时）

**判定**：离开这个 plan，对别的任务没价值，或会带偏上下文 → 只放 Plans。

| 类型 | 目录 |
|------|------|
| Epic 母 plan | `Plans/Epic/` |
| 需求 / 方案 / 开发 / 测试 / 部署 | 对应 `Plans/【分类】/` |
| Bug / 重构 | `Plans/Bug排查/`、`代码重构/` |
| 学习 | `Plans/学习/` |
| 走查记录、度量表、截图 | **同任务 plan 内或同目录**，不另建 Contexts |

文件名：`YYYY-MM-DD-标题.md`（见 [[Templates/模板约定]]）。

---

## 五、任务结束怎么办

1. **默认**：删 plan（Epic 及其子 plan 一并删）。
2. **可选**：从中提炼**一条**可复用结论 → 更新现有 Contexts 规范或 `Contexts/踩坑/`（**须用户确认**）。
3. **禁止**：把整份走查、度量表、截图归档进 Contexts「备查」。

学习线：DoD 满足后 plan 可删；概念卡 / 笔记留在 `Contexts/LLM学习/`（属通用知识）。

---

## 六、文档分工（别重复写规则）

| 文档 | 只写什么 |
|------|----------|
| **本文** | 放什么、不放什么、做完怎么办 |
| [[Templates/模板约定]] | 文件名、YAML、`status`、`epic:`、续做格式、Epic 字段 |
| [[Contexts/决策/AI-Work-Kit工作流总览]] | Skill 怎么用、Epic 阶段、看板、门禁命令 |
| [[Contexts/决策/新手引导与最佳实践]] | 3 张地图：入门 / 全流程 / 决策树 |
| [[Contexts/决策/母子plan投影规则]] | Epic 看板与子 plan 的真理源、状态机、投影门禁 |
| [[索引]] | 目录速查、模板清单 |
| `.cursorrules` / [[CLAUDE.md]] | Agent 常驻：目录索引 + Skill 触发词 |
| `Skills/*.md` | 单次任务步骤（引用本文，不另定存放规则） |

**新增规则**：只改本文 + `模板约定`（若涉及 YAML）；其它文件只加链接，不复制长段原则。

---

## 七、工作流概要（细节见工作流总览）

| 场景 | 入口 |
|------|------|
| 新模块 / 含业务逻辑 | `/full-cycle` → `Plans/Epic/` |
| 续做 | `/resume plan=Plans/... 进度=...` |
| Bug / 学习 / 纯 UI 小改 | 对应 Skill（见 `.cursorrules`） |
| 写代码前 | `plan-gate-check.sh` 通过 |

新功能**禁止**无 Epic 建 `Plans/功能开发/` 主 plan（纯 UI ≤1 人日例外见 [[Templates/模板约定]]）。

---

## 八、写回与确认

- 改 **Plans**：按 Skill 流程直接写。
- 改 **Contexts**：默认**先问用户**（用户说「存档到 Contexts」除外）。
- 学习收尾：`learning-progress-snapshot.sh` 仅 **stdout**，不写 Contexts 文件。

---

## 九、反馈回路（必读）

> 协议全文：[[Contexts/决策/Skill反馈协议]]。本节只立硬规则，细节不复述。

每个 Skill 完成任务时**必须**输出 `skill_run` YAML 块：
- 有 plan → 追加到 plan 末尾
- 无 plan → 追加到 `Contexts/决策/孤立反馈记录.md` 顶部

`utility` 二选一：`high`（必给一句话理由）/ `not-needed`。
`scripts/plan-gate-check.sh` 校验存在性与字段合法性；缺则视为任务未完成。
`scripts/feedback-aggregate.py` 月度聚合 → 输入月度复盘。

**试点**：`requirement-analyst`，2026-06-24 起；通过后推至全部 Skill。

---

## 十、母子 plan 投影（必读）

> 协议全文：[[Contexts/决策/母子plan投影规则]]。本节只立硬规则，细节不复述。

- **真理源单边化**：WBS 切片状态与备注的唯一真理源是**子 plan**；Epic §三 WBS 看板是只读投影，不得承载子 plan 没有的状态或冲突简写。
- **状态三态**：`[x]` 全完成 / `[~]` 部分（必须挂分项行或 `分项见 [[子 plan]] §X` 指针）/ `[ ]` 未开始。禁止 `[ ] + 备注 ✅` 这类半完成压扁写法。
- **粒度对齐**：子 plan 一旦拆切片（如 5→Mock/Http、6→a/b/c），母 plan 必须同步拆行或指针化，不得在备注里塞分项简写。
- **门禁校验**：`scripts/plan-gate-check.sh` 应增加 Epic 看板 ↔ 子 plan 一致性校验；状态映射或备注冲突即不通过。

---

## 十一、Plan Mode（必读）

> 横切通则,所有 Skill 与单阶段入口默认继承,不在各 Skill 重复写。

Plan Mode 不是审批闸门,是**先想后做**的三件事:

- **只读探索**:复杂功能 / 架构 / 重构 / 陌生代码 / Bug 排查,动手前先进 Plan Mode 只读分析(禁改文件),把上下文与意图搞清楚再说。
- **共创方案**:在 Plan Mode 内与用户**迭代方案到满意**,批准后才落 `Plans/` 文件、才动手。Plan Mode 管「批准前临场讨论」,`Plans/` 文件管「批准后持久载体」——两者互补,不重复。
- **拆解归 task-splitter**:任务拆解仍走 `task-splitter` + WBS + 看板(持久、跨会话),Plan Mode 不重复做拆解。

**有副作用动作的硬闸门在 harness,不靠本文软约束**:`git commit/push/reset/rm`、`rm`、`sudo` 等已在 `~/.claude/settings.json` `permissions.ask`,执行前强制询问。文档只立"先想后做"的意图,真正拦截靠 settings。

---

## 相关

- [[Contexts/决策/Skill反馈协议]]
- [[Contexts/决策/母子plan投影规则]]
- [[Contexts/决策/资料与代码仓库边界]] → 指向本文（兼容旧链接）
- [[Contexts/决策/AI-Work-Kit工作流总览]]
- [[Templates/模板约定]]
