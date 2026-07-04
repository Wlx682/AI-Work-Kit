---
tags: [决策, 架构, 运行时, 拓扑, 工作流]
date: 2026-07-05
status: 已采纳
key_points:
  - 本文是运行时视角：讲"一次任务在库里怎么跑起来"，与架构总览的抽象四层互补（总览讲咬合，本文讲数据流）
  - 四个角色：大脑（决策）/ 双手（执行）/ 门禁（保质量）/ 演进（自进化）
  - 两条贯穿机制：门禁=空间横切（每次写入都拦）、反馈回路=时间纵贯（跑得越久库越准）
  - Epic 只存不驱动：虚线反哺引擎派生阶段，自己不驱动流程
  - 抽象分层视角走 架构总览 §二；本文只画运行时拓扑不复述规则
relations:
  depends_on:
    - Contexts/决策/AI-Work-Kit架构总览.md
    - Contexts/决策/Kit核心原则.md
  dependents: []
  supersedes: []
  superseded_by: []
  conflicts: []

---
# AI-Work-Kit 运行时拓扑

> **本文定位**：一张浓缩整库灵魂的**运行时拓扑图**——一次任务在库里怎么跑起来，谁决策、谁干活、谁保质量、系统怎么进化。
> 抽象**分层**心智模型（四层如何咬合）走 [[Contexts/决策/AI-Work-Kit架构总览]] §二；本文只负责运行时**数据流**，不复述规则。两图互补：总览是静态分层，本文是动态跑起来。

---

## 一图流

```mermaid
flowchart TB
    USER(["🧑 自然语言意图"])

    subgraph BRAIN["🧠 控制层 · 谁在决策"]
        ROUTER["workflow-router<br/>自然语言入口 + 路由硬规则"]
        ENGINE["full-cycle 引擎<br/>读蓝图 client-dev / computer-mgmt"]
        ROUTER --> ENGINE
    end

    subgraph HANDS["✋ 执行层 · 谁在干活"]
        SKILLS["Skill 积木<br/>需求/架构/开发/测试/部署/学习…<br/>互斥锁 · 防越界"]
    end

    subgraph DATA["📚 数据/存储层 · 三层边界（宪法）"]
        direction LR
        PLANS["Plans/<br/>任务态·做完即删"]
        CTX["Contexts/<br/>通用态·跨任务"]
        TPL["Templates/<br/>模板态·长期骨架"]
    end

    EPIC[("Epic 数据上下文<br/>只存不驱动<br/>WBS 唯一真理源")]

    GATE{{"🚦 门禁 plan-gate-check.sh<br/>投影·反馈·看板·引用 四校验<br/>任一失败 = BLOCKED"}}

    subgraph EVOLVE["♻️ 演进层 · 系统怎么进化"]
        FEEDBACK["skill_run 反馈<br/>utility: high / not-needed"]
        LOOPS["vault-evolve 月度回路<br/>反馈·关系图谱·漂移·调度"]
        FEEDBACK --> LOOPS
    end

    USER --> ROUTER
    ENGINE -->|"派活·选阶段"| SKILLS
    SKILLS -->|"读写"| PLANS
    SKILLS -.->|"聚合只读投影"| EPIC
    EPIC -.->|"派生阶段事实"| ENGINE

    SKILLS ==>|"每次写入过闸"| GATE
    GATE ==>|"通过才落盘"| PLANS
    GATE -->|"查规范"| CTX
    TPL -->|"约束骨架"| PLANS

    SKILLS -->|"任务末尾吐一条"| FEEDBACK
    LOOPS -->|"月度报告修正"| CTX
    CTX -->|"宪法/协议约束一切写入"| GATE

    classDef brain fill:#e8f0fe,stroke:#4285f4,color:#111
    classDef hands fill:#fef7e0,stroke:#f9ab00,color:#111
    classDef data fill:#e6f4ea,stroke:#34a853,color:#111
    classDef evolve fill:#fce8e6,stroke:#ea4335,color:#111
    classDef gate fill:#fff,stroke:#111,stroke-width:2px,color:#111
    class ROUTER,ENGINE brain
    class SKILLS hands
    class PLANS,CTX,TPL,EPIC data
    class FEEDBACK,LOOPS evolve
    class GATE gate
```

---

## 怎么读（四个灵魂问题各走一条线）

1. **谁决策**（蓝）：用户意图 → `workflow-router` 按路由硬规则选 Skill → `full-cycle` 引擎读蓝图编排。Epic 用虚线**反哺**引擎派生阶段，但自己**不驱动**——「只存不驱动」是三层重构的核心。
2. **谁干活**（黄）：Skill 是唯一动手的层，读写 `Plans/`。互斥锁保证单阶段词不被劫持成全流程。
3. **谁保质量**（黑框 `🚦` = 贯穿机制①）：所有写入都得**过闸** `plan-gate-check.sh`——向左查 `Contexts/` 的协议规范，向上受 `Templates/` 骨架约束，四道校验任一失败即 BLOCKED。这是横向拦截。
4. **怎么进化**（红 = 贯穿机制②）：Skill 每次收工吐一条 `skill_run` 反馈 → `vault-evolve` 月度聚合 → 回流**修正 Contexts 的宪法/协议** → 协议又反过来收紧门禁。库自己体检、纠错、沉淀。

**两条贯穿机制的差异**一眼可见：门禁是**空间上的横切**（每次写入都拦），反馈回路是**时间上的纵贯**（跑得越久库越准）。

---

## 相关

- [[Contexts/决策/AI-Work-Kit架构总览]] — 抽象四层分层视角（本文的姐妹篇，讲咬合）
- [[Contexts/决策/Kit核心原则]] — 三层存储真相源
- [[Contexts/决策/AI-Work-Kit工作流总览]] — Skill 速查 + 看板 + 门禁
