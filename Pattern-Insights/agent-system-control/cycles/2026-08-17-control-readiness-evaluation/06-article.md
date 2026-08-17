# 智能体控制实践第一步：在一次性重写之前做一条可信评估闭环

当一个 Agent 已经能调用工具、修改文件、操作网页，团队很自然地把下一步定义为“上控制面”。但真正适合落下的第一刀，不是搬迁编排层，也不是先 fork 一个更完整的 Harness，而是在现有 Agent 外面做一条可信评估闭环：让“运行没有报错”和“现实结果真的成立”成为两个不同的判断。

因此，智能体控制实践的第一步，不是给 Agent 打分，而是先证明评估本身有资格产生控制证据。宁可引入人工，或者明确得到“不可评、证据不足”，也不能为了跑完流程强行得出一个通过结论。

## 错误评估为什么比没有评估更危险

没有评估时，团队至少知道自己在凭 Demo、经验和直觉决策。错误评估却会给直觉披上一层数据外衣：82 分、90% 成功率、连续三版上涨。到了权限评审或生产准入时，这些数字很容易被解释成“风险已经被量化”，进而成为扩大工具权限、减少人工确认或增加任务时长的依据。

问题是，Eval 并不是一支放在系统外面的中立温度计。任务怎样写、给了哪些工具、Harness 如何管理上下文、允许多少次重试、预算是多少、用什么判断成功，都会改变最后的分数。

[OpenAI 对可信评估的总结](https://openai.com/index/trustworthy-third-party-evaluations-foundations/)把这个问题说得很直接：对长轨迹 Agent 而言，Harness、工具和预算可能决定一种能力是否会在评估中出现。评估报告如果没有说明自己想支持什么主张、测了哪套配置、怎样检查坏题和 Reward Hacking，分数就很容易被过度解释。

这意味着，控制系统若直接消费一个未经验证的 Eval 分数，状态估计从第一步就可能是错的。之后的风险判断、权限收缩和继续授权即使逻辑严密，也只是在错误证据上稳定运行。

## DSH 的一次事故，暴露了“参照错误”

DeepSeek Harness 的一份 [Web Agent GUI 事故复盘](https://github.com/deepseek-ai/deepseek-harness/blob/47f943859bef60e4160492346772ded9b24f765a/docs/postmortem/0003-web-agent-gui-feedback-loop.md)提供了一个很具体的例子。

Agent 修改 GUI 后，成功完成了构建，看到一个 Vite 服务返回 HTTP 200，后来又启动并验证了另一个端口上的完整服务。从局部过程看，每一步都有“成功证据”。但用户真正关心的是自己正在使用的那个页面有没有发生变化。Agent 不知道当前页面的确切 URL、进程和运行模式，也没有在原页面上做外部验收。

于是，构建成功、HTTP 可达、Boot Manifest 存在、替代服务正常，这些事实可以同时成立，却没有一个能够证明目标世界已经按要求改变。

这类失败不能简单归因于“模型不够聪明”。真正的问题是评估对象和参照物错了：把内部过程回执当成外部结果，把另一个服务当成当前服务，把超时退出当成正确的回归失败。只要参照错误，再精确的自动评分也只会精确地判错。

所以，一项评估在开始测 Agent 之前，至少要先证明两件事：正确方案能够通过，已知错误机制确实会失败。缺少其中任何一个，所谓基线都可能只是一个自洽的假阳性装置。

## 先看现有 agent 项目：为什么它应该成为基线，而不是目标 Runtime

现有 `agent` 项目并不是空壳。它已经有版本化的 `AgentDefinition`、统一的 `RunEvent/RunResult`、JSON Trace、SQLite Checkpoint、人工审批、工具输出 Schema 校验，以及“工具效果未知”后的人工恢复分支。现有 60 个测试也全部通过。这些能力足以成为重写前的行为基线。

但它还不能直接回答“任务是否真的完成”。当前 `RunResult.succeeded` 的核心语义近似于：没有异常，而且没有停在人工审批点。

```text
succeeded = error is None && not paused
```

这对 Runtime 很合理，它表达的是“这次运行在技术上结束了”；但如果评估器直接复用它，就会产生危险的偷换：工具返回成功、模型正常结束，不等于文件、网页或业务对象已经变成目标状态。

项目随后做了一个更激进但更清晰的工程选择：整个目标态一次性改为 TypeScript，同时保留两个 Runtime。DSH/Cordis 是唯一生产默认 Runtime；现有 Python/LangGraph 的行为、定义和 60 个测试迁写成 TypeScript/LangGraph.js Learning Runtime。旧 Python 不再通过 Adapter 进入新系统，只在独立 tag/worktree 中保存迁写证据。

这并不意味着可以跳过评估。恰恰相反，第一条 TypeScript 纵切必须直接落在 DSH 的 evaluation Profile 上：

~~~mermaid
flowchart LR
    C["EvaluationCase<br/>任务、参照、故障种子"] --> Q["Qualification<br/>先证明评估可用"]
    Q --> D["DSH evaluation Profile<br/>固定 Bundle/Patch/Provider"]
    D --> P["Cordis evaluation plugin"]
    P --> S["DSH Session Log<br/>技术执行证据"]
    S --> X["TechnicalExecution"]
    X --> O["OutcomeOracle<br/>观察外部真实状态"]
    O --> V["PASS / FAIL<br/>ABSTAIN / INVALID"]
    V --> E["EvaluationReport<br/>配置指纹、证据、人工裁决"]
~~~

依赖方向变成 `evaluation plugin → evaluation-domain → contracts`，以及 `evaluation plugin → dsh-bridge → DSH/Cordis`。`evaluation-domain` 不认识 SessionEvent 或 Cordis Context；只有薄薄的 `dsh-bridge` 读取 DSH 原生类型。版本化 JSON Schema 仍然存在，但用途是持久化、跨进程和重放，不再为 Python/TypeScript 互通服务。

## 第一刀代码具体落在哪里

第一版只需要增加一个纵向切片，不建设通用 Eval 平台：

```text
agent/
├── packages/
│   ├── contracts/
│   │   ├── src/evaluation.ts
│   │   └── schemas/evaluation-report.v1.json
│   ├── evaluation-domain/src/
│   │   ├── models.ts
│   │   ├── qualify-case.ts
│   │   └── evaluate.ts
│   └── dsh-bridge/src/session.ts
├── plugins/evaluation/src/
│   ├── index.ts
│   └── oracles/file-state.ts
├── profiles/evaluation/cordis.patch.yml
└── tests/
    ├── qualification/evaluation-verdict.spec.ts
    ├── plugin-lifecycle/evaluation-plugin.spec.ts
    └── acceptance/legacy-task-parity.spec.ts
```

通用接口只暴露评估真正需要的最小语义：

```ts
export interface TechnicalExecution {
  executionId: string;
  technicalStatus: "completed" | "paused" | "failed" | "unknown";
  sessionRef: string;
  evidenceRefs: readonly string[];
}
```

`technicalStatus` 仍然不是 PASS/FAIL。`dsh-bridge` 从 Session Log、Agent 生命周期和工具结果投影出它；Profile、Bundle、Patch、Provider 和关键监听器顺序进入 `RuntimeManifest.compositionFingerprint`，避免组合改变后复用旧报告。

旧 Python 的价值不再是成为生产 Provider，而是提供不可变的迁写样本。LangGraph.js Learning Runtime 用 `StateGraph`、checkpoint、`interrupt`/`Command` 和 streaming 重建同类行为；它可以用同一 Case 和 Oracle 生成离线对照报告，但不能进入生产依赖图或热切换。

领域模型先保持克制：

```ts
type EvaluationVerdict = "pass" | "fail" | "abstain" | "invalid";

interface EvaluationReport {
  caseId: string;
  sessionRef: string;
  configFingerprint: string;
  verdict: EvaluationVerdict;
  evidence: readonly EvidenceRef[];
  reason: string;
}
```

`OutcomeOracle` 是这一刀最关键的接缝。它不问模型“你完成了吗”，也不只看工具返回值，而是观察任务声明的真实对象。例如文件任务可以比较目标文件的存在性、内容和 diff；网页任务必须检查用户实际页面对应的 URL、进程和 DOM；数据库任务检查业务记录和不变量。

```ts
const execution = await deriveExecutionFromSession(sessionRef);
const observation = await oracle.observe({ evaluationCase, execution });

const verdict = observation.invalid
  ? "invalid"
  : observation.unavailable
    ? "abstain"
    : observation.violatesReference
      ? "fail"
      : "pass";
```

这里最重要的 Red 测试，不是“Agent 能完成一个正常任务”，而是证明评估能推翻 Runtime 的假成功：

```ts
it("DSH technical success cannot override external failure", async () => {
  const execution = completedExecution();
  const oracle = fileStateOracle({ expected: "new", actual: "old" });

  const report = await evaluate({ execution, oracle });

  expect(execution.technicalStatus).toBe("completed");
  expect(report.verdict).toBe("fail");
});
```

还要先固定三颗反例：正确参考解必须得到 PASS；“工具返回成功但文件未变化”必须得到 FAIL；工具效果未知且没有外部证据时必须得到 ABSTAIN。若 Oracle 路径错误、环境失效，或者正确解也无法通过，则该 Case 必须是 INVALID，而不是给 Agent 记一次失败。

这组测试一旦写不出来，就说明成功标准仍不够具体，应该停下来补人工验收，而不是继续扩建控制面。

## “靠谱”不等于百分之百自动、百分之百正确

没有任何现实评估能保证永远正确。开放式研究、设计决策和复杂操作也往往没有唯一答案。靠谱评估真正需要做到的是：明确这份证据能支持什么决策，不能支持什么决策；证据不足时，系统知道自己不能下结论。

为此，Eval 不应只有通过和失败两种结果。

| 结果 | 含义 | 能否进入控制决策 |
|---|---|---|
| PASS | 参照有效、证据充分，Agent 满足当前任务和约束 | 可，但仅限已声明的配置与风险等级 |
| FAIL | 参照有效、证据充分，Agent 明确违反结果或约束 | 可，用于定位缺口和限制自主权 |
| ABSTAIN | 证据不足、专家分歧或自动评分器置信不足 | 不可；进入人工裁决或补证据 |
| INVALID | 题目、环境、参照或评分器失效 | 不可；本次结果作废并修复 Eval |

ABSTAIN 和 INVALID 不是系统异常，而是防止伪精度的安全出口。它们也不能成为拖延借口：每一次不可评都要记录原因、缺失证据、责任人和重新评估条件。持续过高的不可评比例，说明评估体系尚未就绪，而不是 Agent 表现良好。

[Anthropic 的 Agent Eval 实践](https://www.anthropic.com/engineering/demystifying-evals-for-ai-agents)建议为任务准备可通过的参考方案，组合程序、模型与人工评分器，并用人工判断持续校准模型评分器。这里的人不是自动化失败的补丁，而是测量系统最初的基准。

## 评估 Agent 之前，先过六道资格检查

把这一步称为 Evaluation Qualification，会比“搭 Eval 平台”更准确。它不是另一个大系统，而是一条很窄的资格链。

~~~mermaid
stateDiagram-v2
    [*] --> Claim: 声明要支持的决策
    Claim --> Config: 固定被测配置
    Config --> Reference: 验证任务与参照
    Reference --> Sensitivity: 正确解通过 / 错误解失败
    Sensitivity --> Calibration: 校准程序、模型与人工评分器
    Calibration --> Qualified: 证据充分
    Reference --> Invalid: 题目或参照失效
    Sensitivity --> Invalid: 无法识别已知错误
    Calibration --> Abstain: 分歧或置信不足
    Abstain --> Human: 人工裁决 / 补充证据
    Human --> Calibration
    Invalid --> Claim: 修订评估设计
    Qualified --> AgentEval: 才开始评估 Agent
    AgentEval --> [*]
~~~

第一道资格是 **Decision Claim**：先写清楚这轮结果准备用来做什么。是比较两个 Runtime，在固定条件下判断谁更稳定；还是决定一个 Agent 能否从只读进入可逆写入；抑或只是寻找当前能力上限？不同主张需要不同任务、预算和 Harness。不能用“最大能力”分数直接批准生产权限。

第二道资格是 **Config Identity**：固定模型版本、系统提示词、Harness、工具集合、权限、上下文策略、重试、环境和预算。对于 DSH，这意味着 Profile、Bundle、插件组合和关键 Patch 也是被测配置的一部分。任何关键配置改变，都要明确哪些旧证据失效，不能只保留一个模型名称。

第三道资格是 **Reference Validity**：参照不一定是唯一标准答案，但必须是可检查的。它可以是数据库中的最终状态、当前页面的真实变化、业务不变量、禁止行为、专家共识区间，或者一组可接受方案。若连两位领域专家都无法就“什么算成功”形成稳定判断，这个任务暂时不适合自动出分。

第四道资格是 **Failure Sensitivity**：使用参考解、错误解和已知事故种子验证 Eval。正确方案必须能过；工具假成功、目标错位、权限越界等已知错误必须能失败。DSH 的 GUI 事故就可以成为一颗固定 Failure Seed：若新的评估仍把替代服务 HTTP 200 判成原页面修改成功，它就不具备参考价值。

第五道资格是 **Grader Calibration**：程序评分器负责确定性事实，模型评分器负责开放语义，人工负责建立 Gold Set 和处理边界分歧。自动评分只能覆盖已经证明可自动判断的区域。需要关注的不是 LLM Judge 跑了多少条，而是它相对人工基准的误判类型、分歧率和适用边界。

第六道资格是 **Uncertainty Exit**：把 ABSTAIN、INVALID 和人工升级做成协议。一个必须全量出分的系统，最终一定会把环境故障、参考缺失和专家分歧压成伪精确数字。

只有六道资格都留下可审计证据，这组 Eval 才能进入 Qualified Registry，开始测 Agent。

## 第一轮运行，只做一个合格的小闭环

这一步不需要建设通用评估平台。范围越大，越难知道错误来自 Agent 还是 Eval 本身。

第一轮可以只选一个固定版本的 Agent、一类高价值任务和少量可逆工具。甚至可以先从 4 个 Case 开始，不用为了凑数量扩到 12–20 个，但必须覆盖四种不同用途：

- 正常任务，证明参考方案和基本结果能够被稳定识别；
- 边界任务，验证该拒绝、询问或转人工时不会强行继续；
- 已知故障种子，验证工具假成功、陈旧证据、目标错位等机制会被抓住；
- 恢复任务，验证失败后能否停下、补证据、回到检查点或交给人。

真正的停止条件不是“跑满多少条”，而是评估者能够解释每一类任务为什么存在、它支持什么决策、什么情况下结论失效。

运行顺序也很重要。先让参考方案、错误方案和人工标注集通过评估资格检查；再在同一个 EvaluationConfig 下重复运行 Agent。Agent 有随机性，一次成功不能代表可靠性。面向生产的任务通常更关心连续一致成功，而不是多试几次总能碰到一次成功。

评估报告应把两组数据分开：

- **Agent 表现：** 外部结果、约束遵守、恢复能力、重复稳定性、时延和成本；
- **评估可信度：** 参照覆盖、人工一致性、评分器误判、不可评比例、坏题比例和配置新鲜度。

低可信度下的高分不能扩大自主权。高可信度下的失败，反而是最有价值的改造输入。

## 人工参与不是退步，而是在建立测量基准

很多团队把“人工介入”理解为 Eval 不够先进，于是急于让 LLM Judge 覆盖全部任务。这样做容易把人工成本藏进后续事故，而不是消除它。

在第一阶段，人工至少承担三种不可替代的工作：领域专家定义什么结果真正有业务价值；两位以上评审者暴露成功标准中的歧义；争议样本帮助校准自动评分器的边界。随着 Gold Set 和分歧模式积累，确定性检查和模型评分器才可以逐步接管稳定区域。

[NIST 正在推进的 Agentic AI Evaluation Probes](https://www.nist.gov/programs-projects/building-evaluation-probes-agentic-ai)也采用了类似方向：Probe 不只给分，还返回结构化结论、理由和证据映射，并可在流程中或事后运行。当前项目主要聚焦事实落地性，尚不能直接替代生产控制评估，但它说明了一个重要原则：评估结论必须带着证据链进入系统，而不是只留下一个结果字段。

人工辅助的目标不是让所有任务最后都有分，而是帮助系统更准确地知道哪些区域已经可以自动判断，哪些区域仍应保留人工责任。

## 什么时候才允许进入下一步

完成第一轮后，不应交付一个“Agent 健康分”，而应交付六类可审计产物：

1. 版本化的 EvaluationConfig，说明到底测了哪套系统；
2. Qualified Eval Registry，记录哪些任务和评分器已通过资格检查；
3. Evidence Matrix，分别展示 Agent 表现与评估可信度；
4. Failure Corpus，保存真实事故与已知错误机制；
5. Human Adjudication Log，记录专家分歧和裁决理由；
6. Re-evaluation Trigger，规定模型、Harness、工具、权限或环境变化后哪些证据必须重跑。

这些产物仍不能证明 Agent 已经“安全”。它们只回答一个更克制的问题：当前证据是否足以进入下一阶段的小规模实验。

下一阶段也不是直接放开生产权限，而是按证据成熟度逐级推进：先影子运行，再只读，再允许可逆写入，最后才讨论高权限或不可逆动作。每一级的自主权，都不能超过当前 Eval 能够可靠支持的范围。

## 这会不会让实践变慢

最强的反对意见是：评估永远无法完美，模型和 Harness 又在持续变化。如果先验证题目、参照、评分器，再验证 Agent，团队可能陷入无限递归。

这个反对意见成立一半。我们确实不应等到拥有“完整评估平台”才行动。[Benchmark Lottery](https://arxiv.org/abs/2107.07002)已经提醒我们，任务和指标的选择会改变排名；再大的题库也不会自动变得中立。

但由此得出的结论不该是跳过评估，而是让决策权限与证据成熟度匹配。低风险、可逆任务可以接受较轻的参照和更多人工；高风险、不可逆动作需要外部真值、评分器校准和恢复验证。配置变化时，也只重评受到影响的证据，而不是从零重建全部体系。

真正拖慢实践的，往往不是前面多花几天验证 Eval，而是几个月后发现所有历史分数都测错了对象，无法解释一次优化为何有效，也无法证明一次回归是否已经修复。

## 第一项控制，不是暂停 Agent

上一篇讨论的是：智能体生产系统真正要控制的，是 Agent 在什么信息、能力、权限和恢复条件下可以继续改变世界。

把这个判断推进到实践，第一项控制并不是先给 Runtime 加一个暂停命令，而是控制什么证据有资格进入决策。未经资格检查的评估，不得为 Agent 扩权；证据不足时，系统必须停在“不知道”，把判断交还给人。

这看起来比一个漂亮的总分慢，也不够自动化。但只有从这里开始，后面的状态估计、风险判断和继续授权才不是建立在沙地上。

评估不是为了证明 Agent 已经准备好了。评估首先要证明：当它说“准备好了”时，我们有理由相信。

## 参考资料

- [Anthropic：Demystifying evals for AI agents](https://www.anthropic.com/engineering/demystifying-evals-for-ai-agents)
- [OpenAI：A shared playbook for trustworthy third party evaluations](https://openai.com/index/trustworthy-third-party-evaluations-foundations/)
- [NIST：Building Evaluation Probes into Agentic AI](https://www.nist.gov/programs-projects/building-evaluation-probes-agentic-ai)
- [DeepSeek Harness：Post-mortem 0003](https://github.com/deepseek-ai/deepseek-harness/blob/47f943859bef60e4160492346772ded9b24f765a/docs/postmortem/0003-web-agent-gui-feedback-loop.md)
- [Google SRE：Testing for Reliability](https://sre.google/sre-book/testing-reliability/)
- [Principles of Chaos Engineering](https://principlesofchaos.org/)
- [The Benchmark Lottery](https://arxiv.org/abs/2107.07002)
