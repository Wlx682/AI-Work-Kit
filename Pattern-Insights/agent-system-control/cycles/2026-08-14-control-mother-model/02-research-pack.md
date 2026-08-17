# 中文研究包

> AI 交付翻译式总结，不是全文逐字翻译；原文链接与定位只作为核验入口。

## 材料 1：钱学森《工程控制论》——先建模控制关系，再讨论装置

- 来源角色：控制理论的基础定义与工程建模方法。
- 要解决的问题：如何把自动控制实践中分散的技术成果提炼成可迁移的工程理论。
- 核心主张：研究控制系统应围绕输入、输出、反馈、扰动、误差、稳定性等关系展开，而不是从某一种具体控制装置出发。
- 机制/方法：先界定系统边界和目标，再描述系统运动、观测、反馈与控制；原书覆盖线性、非线性、随机输入、最优控制等不同条件，说明控制论不是单一公式。
- 关键证据：1954 年 McGraw-Hill 版书目和目录明确包含反馈伺服、随机输入、非线性和优化控制等主题。
- 局限与反方：语言模型不是可直接线性化的飞行器，不能由经典控制公式推出其语义输出必然收敛。
- 与本期问题的关系：启发我们先问“Agent 系统中什么是参考、状态、观测、扰动和控制输入”，而不是先画控制台功能。
- 需要你判断：是否接受“借用建模次序，不照搬数学结论”作为文章的理论边界？
- 原文核验入口：[Google Books 书目与目录](https://books.google.com/books/about/Engineering_Cybernetics.html?id=NfgvAAAAIAAJ)

## 材料 2：《工程控制论》第三版序言——理论必须被工程实践反复修订

- 来源角色：理论修订、适用边界与反方材料。
- 要解决的问题：初版理论如何面对二十五年后的计算机、人工智能、大系统和工程实践变化。
- 核心主张：技术科学来自实践又指导实践，但理论前提、命题客观含义和工程意义必须接受实际检验；内容会随工程技术发展而改变。
- 机制/方法：新增状态空间、系统辨识、能观测性、能控性、大系统、容错和自适应等内容，把系统性质本身也作为需要研究和测量的对象。
- 关键证据：序言明确指出工程实践是检验技术科学理论的最后标准；目录列有系统运动模型辨识、线性系统能观测性和能控性。
- 局限与反方：该材料不能直接证明 Agent 控制母模型有效，反而要求我们通过真实 Agent 任务校准状态变量和控制律。
- 与本期问题的关系：支持“系统模型也会失配”这一设计，因此 Agent、提示、工具或插件变化后，旧能力结论应失效并重新辨识。
- 需要你判断：文章是否应把“可辨识、会失配的模型”放在比“精确预测模型”更重要的位置？
- 原文核验入口：[科学出版社 PDF，第 14–16 页序言及目录](https://www.ecsponline.com/book/2018/yz/9787030300942-003007-curved-sam.pdf)

## 材料 3：DeepSeek Harness 架构与生命周期——运行时控制发生在多个接纳点

- 来源角色：近期 Agent Runtime 工程机制。
- 要解决的问题：如何让模型、工具、Session、Agent Loop、Sandbox 等能力可组合，并在 Turn/Step/Tool 生命周期中拦截和协调。
- 核心主张：DSH 是下层 Agent Runtime，不是上层控制系统。持久重放事实走 `session/event`，实时控制和状态走 `agent/*`；pre-step、request、tool 和 turn-stopping 是不同的运行时控制点，out-of-tree Cordis 插件可以在这些接缝采集事实和接纳控制。
- 机制/方法：Cordis 插件树提供共享上下文、服务、类型化事件和带 disposer 的注册 effect；Agent Loop 在消息认领、step 开始、模型请求、工具执行和 turn 停止前后发出不同事件。Profile、Bundle 与 Patch 决定实际加载组合。
- 关键证据：生命周期文档显示 follow-up 入队后还要经过 claim 和 pre-step；因此“命令已发送”与“命令进入模型输入”不是同一事实。
- 局限与反方：“Everything is a Plugin / no privileged core”不等于没有稳定 core API，也不等于插件天然不能承载安全能力。安全是否成立取决于 Agent 是否拥有配置权、卸载权、凭证和旁路能力；Cordis disposer 只撤销注册 effect，不能回滚文件、数据库或支付等外部副作用。
- 与本期问题的关系：DSH 承担下层 Agent Loop；DSH 控制插件承担 M2 的传感与接纳；框架无关控制面承担状态估计、偏差与监督决策；高权限 Safety Executor/Watchdog 承担不可旁路执行与降级。它同时支持把 `u_cmd` 与 `u_applied` 分账。
- 需要你判断：是否接受“DSH 是被控 Runtime 与控制接缝，不是控制系统本身”；生产控制是否必须记录命令被拦截、委托、短路、接纳、应用和效果验证？
- 原文核验入口：[Architecture](https://github.com/deepseek-ai/deepseek-harness/blob/47f943859bef60e4160492346772ded9b24f765a/docs/architecture.md)；[Agent lifecycle](https://github.com/deepseek-ai/deepseek-harness/blob/47f943859bef60e4160492346772ded9b24f765a/docs/agent-lifecycle.md)

## 材料 4：Session Projection 与 Goal——事实投影不等于状态估计，目标有效不等于允许续轮

- 来源角色：运行状态构造与长期任务控制机制。
- 要解决的问题：如何从事件日志稳定生成当前状态，以及如何管理同一 Session 内的持续目标。
- 核心主张：Session Projection 由同步纯函数折叠 committed events；Goal 的 durable phase 与 process-local activation 分离。
- 机制/方法：投影单元对相同事件前缀生成一致的 JSON 状态；Goal 具有稳定 ID、revision、phase 和 max rounds，而是否启动下一轮由另一个激活机制决定。
- 关键证据：官方文档明确要求投影函数同步和纯；Goal 文档明确写明 objective phase 与 continuation consumer 是否可开始下一轮是两个问题。
- 局限与反方：投影只能回答日志已经确定的事实，不能自动判断目标是否真的理解、证据是否充分、现实世界是否符合预期。
- 与本期问题的关系：由此拆出确定性 `ProjectionSnapshot` 与认识性 `StateEstimate`；控制面再把 Goal revision、phase、轮数和 activation/disarm 与授权主体、预算、有效期和撤销状态组合，派生 `ContinuationLease`。
- 原生/派生边界：DSH 原生提供 Goal 事实和进程激活机制，但没有原生的、带过期与撤销语义的 `ContinuationLease`；后者是本控制系统定义的跨 Runtime 契约。
- 需要你判断：是否接受“目标仍 active，但无有效继续授权时不得自动开始下一轮”？
- 原文核验入口：[Session projection](https://github.com/deepseek-ai/deepseek-harness/blob/47f943859bef60e4160492346772ded9b24f765a/docs/subsystems/session-projection.md)；[Goal subsystem](https://github.com/deepseek-ai/deepseek-harness/blob/47f943859bef60e4160492346772ded9b24f765a/docs/subsystems/goal.md)

## 材料 5：Web Agent GUI 事故复盘——内部成功不能替代外部世界正确

- 来源角色：真实失败案例与验收反例。
- 要解决的问题：为什么 Agent 完成了源码修改、构建、HTTP 200 和替代服务器验证，用户原页面仍没有被正确验收。
- 核心主张：多个局部合理动作如果没有共享同一个现实验收对象，内部流程可以全绿而任务仍失败。
- 机制/方法：复盘把当前 URL、运行模式变成模型可见且可由 shell 查询的信息；拒绝不正确的独立 Vite 服务器，并对生产刷新和 HMR 读取外部状态。
- 关键证据：Agent 不知道当前会话由哪个 URL、进程和源码目录承载，把源码编辑、构建成功、HTTP 200、替代服务器和用户现有页面当成了可互换事实。
- 局限与反方：这是单一 GUI 事故，不能证明所有 Agent 失败都源于世界模型缺口。
- 与本期问题的关系：说明观测对象必须包含工作世界身份和实际结果；工具成功只能进入 `ActionReceipt`，不能直接进入“任务完成”。
- 需要你判断：是否接受“高风险完成声明必须绑定独立的现实结果观测”？
- 原文核验入口：[Post-mortem 0003](https://github.com/deepseek-ai/deepseek-harness/blob/47f943859bef60e4160492346772ded9b24f765a/docs/postmortem/0003-web-agent-gui-feedback-loop.md)
