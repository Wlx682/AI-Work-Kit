# 阅读队列

首批材料的中文导读见：[02a-reading-guides.md](./02a-reading-guides.md)。

| 优先级 | 材料 | 作者/机构 | 日期 | 类型 | 为什么读 | 支持/挑战 | 状态 |
|---|---|---|---|---|---|---|---|
| 1 | [How Do Practitioners Build SE Agents? Insights from a Mixed-Methods Study](https://arxiv.org/abs/2607.10856) | Lyu 等 | 2026-07-12（v2：2026-07-25） | 近期一手实证；20 名访谈 + 80 名问卷 | 最贴近本期假设：实现变便宜后，瓶颈转向需求、协调、审查与评估；评估开始驱动迭代，规格成为可测试、可版本化产物，并出现适应性维护 | 支持“双环、产物评估与进化”；同时挑战评估信号天然可信的假设 | 已读 |
| 2 | [Research Update: Algorithmic vs. Holistic Evaluation](https://metr.org/blog/2025-08-12-research-update-towards-reconciling-slowdown-with-time-horizons/) | METR / David Rein | 2025-08-13 | 真实大型代码库实验；18 个任务 | 对比自动测试与人工整体审查：通过测试的产物仍可能因测试覆盖、文档、格式和可维护性而不可合并，可用于定义“所有输入输出产物为何要被评估” | 支持多维产物评估；挑战单一自动判定和固定评估规则 | 已读 |
| 3 | [SlopCodeBench: Benchmarking How Coding Agents Degrade Over Long-Horizon Iterative Tasks](https://arxiv.org/abs/2603.24755) | Orlanski 等 | 2026-03-25（v2：2026-05-07） | 长周期迭代基准；15 个 Agent | 直接观察规格逐步演化时的跨轮次质量：结构侵蚀和冗余随迭代增长；显式质量提示改善初值却未降低退化率 | 支持跨轮次趋势评估与进化环；反驳“把规则一次写清就够了” | 待选 |
| 4 | [AgentSpec: Customizable Runtime Enforcement for Safe and Reliable LLM Agents](https://arxiv.org/abs/2503.18666) | Wang、Poskitt、Sun | 2025-03-24；ICSE 2026 | 同行评审论文；运行时约束 DSL | 用“触发器—谓词—强制动作”把 Agent 行为约束变为运行时可执行规则，最接近“让智能体系统像代码一样可断言”的现有实现 | 支持系统断言的技术可行性；反例边界是它主要覆盖预先已知的安全约束，不能自动发现“任务完成但目标错误” | 待选 |
| 5 | [Real-Time Detection and Repair of LLM Agent Failures](https://arxiv.org/abs/2608.02464) | Sunny Dubey | 2026-08-03 | 最新预印本；2,823 条 Agent 轨迹 | 从逐步遥测、时序变化检测和确定性验证中实时发现失败，并在输出前回滚重跑；直接研究低成本快速失败闭环 | 支持“快速失败先于自动进化”和趋势检测；同时显示监控必须按部署校准、存在误报，对看似合理的错误仍需要外部参照 | 待读 |

## 选材说明

- 先保留 5 份，分别承担：近期工作流实证、真实评估案例、长期迭代失败、可执行系统断言、实时失败检测与修复。
- 摘要只用于决定阅读顺序，不视为已读或已掌握。
- 首批建议精读 1 和 2：一份建立工作流全景，一份具体拆开“产物评估”的可信度问题。

## 背景补充（不计入 5 份核心材料）

- [State of AI-assisted Software Development 2025](https://dora.dev/research/2025/dora-report/)：支持“AI 放大现有组织系统”的宏观背景，但对系统可断言性的机制过于间接。
- [MIT 16.06 Principles of Automatic Control](https://ocw.mit.edu/courses/16-06-principles-of-automatic-control-fall-2012/pages/lecture-notes/)：用于校准 PID、微分与噪声放大的控制论类比。
