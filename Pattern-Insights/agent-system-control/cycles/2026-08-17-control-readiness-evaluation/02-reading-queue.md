# 阅读队列

| 优先级 | 材料 | 作者/机构 | 日期 | 类型 | 为什么读 | 支持/挑战 | 状态 |
|---|---|---|---|---|---|---|---|
| P0 | Demystifying evals for AI agents | Anthropic | 2026-01-09 | 近期实践/机制 | 建立 task、trial、grader、transcript、outcome、eval harness 与 agent harness 的共同词汇，并观察从零开始的 Eval 路线 | 支持早做评估、评估整套 Agent；挑战单次成功与单一评分 | 已读相关全文 |
| P0 | A shared playbook for trustworthy third party evaluations | OpenAI | 2026-05-29 | 测量有效性/Harness 边界 | 核验 Harness、工具、预算和有效性检查如何改变评估结论 | 支持“配置是被测对象”；挑战把模型能力当固定常数 | 已读相关章节 |
| P0 | Web agent GUI feedback-loop postmortem | DeepSeek Harness | 固定提交 47f9438 | 真实失败案例 | 观察内部流程成功、HTTP 200 和替代服务为何不能证明用户当前页面已改变 | 支持外部结果验收、运行时身份和反事实测试 | 已读 |
| P0 | Building Evaluation Probes into Agentic AI | NIST ITL | 2026 | 评估探针/审计轨迹 | 观察 Eval 如何嵌入 Agent 工作流并生成机器可读证据链 | 支持在线/离线探针与可追溯证据；范围暂限事实落地性 | 已读 |
| P1 | Testing for Reliability + Principles of Chaos Engineering | Google SRE / Chaos Engineering Community | 经典实践 | 邻近领域迁移 | 从系统可靠性学习配置核验、重复试验、稳态、真实扰动和爆炸半径控制 | 支持故障注入与受控对照；挑战只测正常路径 | 已读相关章节 |
| P0 | The Benchmark Lottery | Dehghani 等 / Google Research、DeepMind | 2021-07-14 | 反方/测量批判 | 检查题目选择、聚合分数和 Benchmark 状态如何改变算法排名 | 挑战统一总分和通用排行榜；要求先声明评估主张 | 已读摘要、引言与结论相关段落 |
