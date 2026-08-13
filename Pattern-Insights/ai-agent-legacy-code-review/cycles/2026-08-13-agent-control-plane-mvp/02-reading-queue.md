# 阅读队列

> 本页是 AI 的选源与证据索引，不是给用户的默认阅读任务。用户默认阅读 `02-research-pack.md` 中文研究包；以下原文链接仅作按需核验入口。

| 优先级 | 材料 | 作者/机构 | 日期 | 类型/角色 | 为什么读 | 支持/挑战 | 状态 |
|---|---|---|---|---|---|---|---|
| P0 | [How we monitor internal coding agents for misalignment](https://openai.com/index/how-we-monitor-internal-coding-agents-misalignment/) | OpenAI | 2026-04 | 生产实践 / 监控边界 | 暴露监控召回、延迟、串谋、同步阻断、隐私和可靠性仍未解决，适合压力测试“监控自然带来控制”。 | 支持监控进入真实部署；挑战单一监控器和异步告警成为承重控制层。 | 已转译到 `02g` |
| P0 | [Artificial Intelligence Risk Management Framework: Generative Artificial Intelligence Profile](https://nvlpubs.nist.gov/nistpubs/ai/NIST.AI.600-1.pdf) | NIST | 2024-07 | 官方框架 / 治理边界 | 核验持续监控、第三方依赖、漂移、隐私、事故预案和人工 fallback。 | 支持生命周期治理；挑战“只建设动态镜像就足够”。 | 已转译到 `02g` |
| P1 | [The impact of human oversight on discrimination in AI-supported decision-making](https://op.europa.eu/en/publication-detail/-/publication/68b91f8f-cf0a-11ef-be2a-01aa75ed71a1/language-en) | European Commission JRC | 2024 | 大样本研究 / 人类监督反例 | 检验“交给人类审批”是否天然可靠；覆盖 1,411 名借贷和招聘专业人员。 | 挑战形式化 human-in-the-loop；支持把人的能力和负载纳入状态。 | 已转译到 `02g` |
| P1 | [LLM Agents Can Be Choice-Supportive Biased Evaluators](https://doi.org/10.1609/aaai.v39i25.34843) | Zhuang 等 | 2025 | AAAI 论文 / 共同模式故障 | 检验 Agent 兼任评估器时是否会支持自己的初始选择。 | 挑战同源模型互评；支持按故障域独立性而非评估器数量计强度。 | 已转译到 `02g` |
| P0 | [Engineering Cybernetics](https://books.google.com/books/about/Engineering_Cybernetics.html?id=nX3QAAAAMAAJ) | H. S. Tsien | 1954 | 专著 / 邻近理论基础 | 从反馈、误差、扰动、不确定性、稳定性和控制设计重新定义智能体系统问题，检验“详尽监控 → 精细控制”的第一性逻辑。 | 支持可观测与状态估计对控制的基础作用；不能把后来形成的现代状态空间术语或综合集成研讨厅直接写成该书原义。 | 用户已深读；AI 已核验并形成 `02c` 映射 |
| P1 | [Engineering cybernetics: 60 years in the making](https://doi.org/10.1007/s11768-014-0031-3) | Zhiqiang Gao | 2014 | 回顾论文 / 原著机制边界 | 核验《工程控制论》对系统模型未知、不可预测变化和内外部扰动的前瞻讨论。 | 支持“不应假定被控系统性质已知”；论文自身带有主动扰动抑制理论的解释视角。 | 已核验并形成 `02c` 映射 |
| P0 | [Turning Interaction History into Execution State: A Runtime Layer for Long-Horizon Coding Agents](https://arxiv.org/abs/2608.00808) | Zehao Wang 等 | 2026-08-01 | 论文 / 显式执行状态 | `Ledger` 把原始交互历史蒸馏为“观察过、修改过、尝试过”的确定性执行状态，并在模型行动前 inform、命令执行前 govern。它直接检验 `Evidence` 是否应升级为运行时账本，而不是事后日志。 | 支持独立运行时层；但主要证明状态治理和效率改善，没有证明系统能判断业务目标是否真的完成。 | 已转译总结 |
| P0 | [Context-to-Execution Integrity for LLM Agents](https://arxiv.org/abs/2607.06000) | Igor Santos-Grueiro | 2026-07-07 | 论文 / 精确行动授权 | `CXI` 把不可信上下文与工具执行权分开，要求字段授权、精确副作用授权和调用授权绑定到同一个 action manifest。它直接检验 `ActionIntent + 行动代理` 的边界。 | 支持确定性执行门；挑战在于单作者预印本、受控评估与真实遗留代码场景之间仍有距离。 | 已转译总结 |
| P1 | [LangGraph Interrupts](https://docs.langchain.com/oss/python/langgraph/interrupts) | LangChain | 持续更新；2026-08-13 检索 | 官方文档 / 检查点与恢复 | 展示运行时如何保存图状态、无限期暂停、经外部输入恢复，并强调 interrupt 前副作用必须幂等。它可用于区分 `Checkpoint`、审批决定与普通 trace。 | 支持“中断是持久状态，不是弹窗”；但框架只提供机制，不替系统定义何时中断、恢复后哪些证据仍有效。 | 已转译总结 |
| P0 | [Building self-improving tax agents with Codex](https://openai.com/index/building-self-improving-tax-agents-with-codex/) | OpenAI × Thrive Holdings | 2026-05-27 | 生产案例 / 受控进化 | 真实生产系统把源材料、字段溯源、提交结果和专家修正串成证据，再把反复出现且经审查的问题转成有明确成功条件的任务。它验证 `EvolutionCandidate` 不应自动修改线上系统。 | 强支持“生产必须主动制造证据”和“进化候选需人工/评估治理”；但领域高度结构化，不能直接外推到所有开放编码任务。 | 已转译总结 |
| P1 | [Evaluating chain-of-thought monitorability](https://openai.com/index/evaluating-chain-of-thought-monitorability/) | OpenAI | 2025-12-18 | 研究 / 反方与监控边界 | 研究表明监控推理过程通常比只看行动和结果更有效，但监控能力会受模型、训练方式、推理预算和场景影响，而且仍不完美。它用于反驳“记录完整轨迹就足以判断正确”。 | 挑战单一证据账本或单监控器成为承重控制层；支持 `unknown`、外部结果验证和纵深防御。 | 已转译总结 |
| P0 | [Mathematical Description of Linear Dynamical Systems](https://doi.org/10.1137/0301010) | R. E. Kalman | 1963 | 原始论文 / 可观测与可控的形式边界 | 核验输入输出、内部状态、可观测性和可控性为何是不同问题。 | 支持动态状态镜像；直接挑战“看见系统就等于能控制系统”。 | 已转译总结 |
| P0 | [An Introduction to Cybernetics](https://ashby.info/Ashby-Introduction-to-Cybernetics.pdf) | W. Ross Ashby | 1956 | 原著 / 必要多样性 | 核验控制器的响应种类与通信容量如何限制其能压缩的扰动结果种类。 | 支持精细控制需要足够干预手段；挑战只增加采集维度、不增加控制权和降级模式的方案。 | 已转译总结 |
| P0 | [Every Good Regulator of a System Must Be a Model of That System](https://ashby.info/Ashby-Mechanisms_of_intelligence.pdf) | Roger C. Conant、W. Ross Ashby | 1970 | 原始论文 / 调节器模型 | 核验高效控制器为何必须包含与控制目标相适配的被控系统模型。 | 支持动态系统镜像成为控制器内部模型；挑战把仪表盘或原始日志直接当作系统模型。 | 已转译总结 |
| P0 | [Engineering a Safer World](https://doi.org/10.7551/mitpress/8179.001.0001) / [STPA Handbook](https://psas.scripts.mit.edu/home/get_file.php?name=STPA_handbook.pdf) | Nancy Leveson 等 | 2012 / 持续维护 | 专著与方法手册 / 系统安全 | 把复杂事故从部件故障问题改写为安全约束未被正确实施的控制问题。 | 支持监控整个社会技术控制结构；挑战只监控 Agent、模型或代码组件。 | 已转译总结 |
| P0 | [Safety Assurance Approach for Intelligent Aircraft Systems](https://ntrs.nasa.gov/api/citations/20180006312/downloads/20180006312.pdf) / [Architecting Safer Autonomous Aviation Systems](https://ntrs.nasa.gov/api/citations/20220016762/downloads/fnpw-SSS2023-final.pdf?attachment=true) | NASA 等 | 2018 / 2023 | 安全架构 / 运行时保障 | 核验面对不可完全验证的复杂功能时，监控器、切换器与安全替代通道如何组成 Runtime Assurance。 | 支持快速确定性安全环；挑战监控器与被监控 Agent 共用不可信输入、模型或执行通道。 | 已转译总结 |

## 中文研究包编排顺序

### 第一组：Agent 工程机制

1. 先解释 `Ledger`，建立“聊天历史不等于执行状态”。
2. 接入 Tax AI 生产案例，说明证据如何进入受控进化。
3. 用 `CXI` 收紧行动授权边界。
4. 用 LangGraph 区分暂停恢复与外部副作用补偿。
5. 用 monitorability 作为反方，说明完整轨迹仍不能证明任务正确。

### 第二组：控制论与安全架构

1. 用 Kalman 区分可观测、可控和状态模型。
2. 用 Ashby 的必要多样性检验控制器是否拥有足够的干预手段。
3. 用 Conant–Ashby 检验动态镜像能否称为面向控制目的的系统模型。
4. 用 STAMP 把事故解释为约束、时机、反馈与过程模型失效。
5. 用 NASA Runtime Assurance 检验快速安全环和独立替代通道。

## AI 导航结论（待用户批注，不视为主张）

- 五份材料没有给出一个现成的“完成门禁”，反而共同留下了这个架构空位：状态账本知道发生了什么，行动门知道能否执行，检查点知道怎样暂停和恢复，结果评估知道后来是否真的成功，但仍需要一个独立协议把这些证据汇总成 `pass / fail / unknown`。
- `Evidence` 需要拆成两层：运行中的 `ExecutionLedger` 维护当前有效事实，完成判断使用不可变的 `EvidencePacket`。否则运行状态更新和审计证据会相互污染。
- `Checkpoint` 也需要拆成两个概念：恢复游标只保证“从哪里继续”，补偿计划才回答“已经发生的副作用怎样撤销或对冲”。
- 进化环的输入不应是所有异常，而应是经归因、聚类和人工/规则复核后形成的 `EvolutionCandidate`；这与 Tax AI 案例中“不自动把一次修正变成任务”一致。
- 不能让同一模型既生成方案、又解释轨迹、再批准自己的完成声明。即便使用模型监控，也必须保留确定性证据、外部结果和 `unknown` 退路。
