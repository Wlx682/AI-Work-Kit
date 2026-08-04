---
tags: [功能开发, Flutter, Agent, LLM, Prompt]
type: plan
category: 功能开发
status: 进行中
date: 2026-08-04
lifecycle_state: development
epic: Plans/Epic/2026-08-04-Flutter版劳动仲裁生成式智能助手App.md
parent: Plans/功能开发/2026-08-04-Flutter版劳动仲裁生成式智能助手App.md
requirement_plan: Plans/需求分析/2026-08-04-Flutter版劳动仲裁生成式智能助手App.md
p0_open: 0
含业务逻辑: 是
---

# 子任务 09：Agent 增强编排与工具契约

## 一、需求分析（开工门禁）

- 需求：`Plans/需求分析/2026-08-04-Flutter版劳动仲裁生成式智能助手App.md`
- 方案：`Plans/技术方案/2026-08-04-Flutter版劳动仲裁生成式智能助手App.md`
- 结论：把当前确定性 `AgentEngine` 骨架扩展为可插拔的本地模型 Agent；金额、法条和文书工具仍由确定性模块负责。

## 二、输入与输出

| 输入 | 输出 |
|------|------|
| `AgentEngine`、`LlmClient`、`EvaluateLaborCaseWorkflow`、`LawRetriever`、`TemplateFiller` | Prompt/JSON Schema、结构化字段提取、缺字段追问、工具调用编排、步骤 trace 与确定性 fallback |

## 三、范围与边界

- LLM 只负责案情理解、参数提取、语言组织和解释，不能生成或覆盖赔偿金额、法条来源和文书核心事实。
- 工具注册表至少包含确定性赔偿计算、法条检索、报告组装和文书生成；每个工具定义输入 schema、输出 schema 和错误类型。当前已注册 `calculate_compensation`、`retrieve_law`、`evaluate_case` 和 `generate_document`，均复用既有确定性工作流。
- 缺字段追问有最大轮数、超时、取消和低置信度出口；模型输出 JSON 不合法时回退到字段校验和确定性报告。
- 本任务不实现 UI 像素对稿、云端模型和多领域 Agent；Android 真机验证按当前用户范围暂缓。

## 四、实施与验收

- [ ] 建立 `PromptCatalog` 与版本化 JSON Schema，覆盖案情字段、缺字段和文书改写请求。
- [ ] 增加结构化 `AgentExtractionResult`（字段值、置信度、缺失字段、来源和原始 trace）。
- [ ] 将 `AgentEngine` 的步骤编排改为显式状态机/工具调用序列，保留可回放 trace。
- [ ] 实现缺字段追问、最大轮数、超时、取消、非法 JSON 和模型不可用 fallback。
- [ ] 增加模型可用时的报告润色/文书动态改写入口，但输出必须经过领域校验和原文事实约束。
- [x] 已完成 Prompt/JSON Schema、结构化提取、有限追问、工具注册、非法输出 fallback、trace 和 `AgentEngine.runEnhanced` 入口。
- [x] 已接入 `calculate_compensation`、`retrieve_law`、`evaluate_case` 和 `generate_document`：编排器注入已校验案件参数，工具输出均来自确定性 Domain/Data 工作流，模型不能覆盖金额、法条或核心事实。
- [ ] 真实 Runtime 驱动的报告润色和文书改写仍待接入；文书保存/分享继续由 `DocumentWorkflow` 管理。

## 五、验收标准

- 完整案情可由 schema 提取并进入既有评估工作流；缺工资/日期等关键字段时只追问或返回校验错误，不生成精确金额。
- Agent 调用计算器和法条检索工具时，报告金额与引用仍来自工具结果，模型不能覆盖。
- 模型不可用、输出格式错误、工具异常或达到追问上限时，返回可解释的确定性报告和步骤 trace。
- 同一输入在 fake LLM 下可重复测试；所有 prompt、schema、工具调用和 fallback 都有单元/集成断言。

## 六、依赖与续做

- 依赖：子任务 01、02、06、08；可与子任务 05 的 UI 状态接缝联调。
- 代码仓库：`/Users/wanglongxiang/git/labor_assistant`
- 续做：`/resume plan=Plans/功能开发/2026-08-04-Flutter版劳动仲裁生成式智能助手App-子任务09-Agent增强编排与工具契约.md 进度=实现`

## 七、反馈（skill_run）

```yaml
skill_run:
  skill: task-splitter
  plan: Plans/功能开发/2026-08-04-Flutter版劳动仲裁生成式智能助手App-子任务09-Agent增强编排与工具契约.md
  date: 2026-08-04
  contexts_used:
    - path: Plans/技术方案/2026-08-04-Flutter版劳动仲裁生成式智能助手App.md
      utility: high
      reason: 用于承接 AgentEngine、Prompt/JSON Schema、工具边界和 LLM 不得覆盖金额/法条的架构契约。
    - path: Plans/自动化测试/2026-08-04-Flutter版劳动仲裁生成式智能助手App.md
      utility: high
      reason: 用于把模型输出错误、追问上限、工具异常和确定性 fallback 转成测试场景。
    - path: Contexts/决策/Skill原子契约.md
      utility: high
      reason: 用于保持 Agent 编排只消费 Domain/Data 工具，不把业务规则复制进 prompt。
  contexts_missing:
    - 真实 GGUF 权重和最终 Prompt 评测集；不阻塞计划拆分，后续进入模型 Spike 验收。
  contexts_stale: []
  outcome_status: pass
  friction: "现有 AgentEngine 只有正则提取和固定步骤，增强编排需要新增 schema、工具调用和可回放 trace。"
  revisit_needed: false
```

```yaml
skill_run:
  skill: feature-dev-assistant
  plan: Plans/功能开发/2026-08-04-Flutter版劳动仲裁生成式智能助手App-子任务09-Agent增强编排与工具契约.md
  date: 2026-08-04
  contexts_used:
    - path: Plans/技术方案/2026-08-04-Flutter版劳动仲裁生成式智能助手App.md
      utility: high
      reason: 用于落实 AgentEngine、Prompt/JSON Schema、工具权威边界和 LLM fallback 契约。
    - path: Plans/自动化测试/2026-08-04-Flutter版劳动仲裁生成式智能助手App.md
      utility: high
      reason: 用于验证结构化提取、追问上限、工具调用、非法 JSON 和可回放 trace。
  contexts_missing:
    - 真实 GGUF 权重和最终 Prompt 评测集。
  contexts_stale: []
  outcome_status: partial
  friction: "Agent 契约、四个确定性工具和增强入口已落地并通过测试；真实模型驱动润色/改写仍待完成。"
  revisit_needed: true
```

```yaml
skill_run:
  skill: feature-dev-assistant
  plan: Plans/功能开发/2026-08-04-Flutter版劳动仲裁生成式智能助手App-子任务09-Agent增强编排与工具契约.md
  date: 2026-08-04
  contexts_used:
    - path: Plans/技术方案/2026-08-04-Flutter版劳动仲裁生成式智能助手App.md
      utility: high
      reason: 用于将确定性评估工作流作为 Agent 工具权威来源，避免模型重算金额或编造法条。
    - path: Plans/自动化测试/2026-08-04-Flutter版劳动仲裁生成式智能助手App.md
      utility: high
      reason: 用于把工具参数注入、序列化输入、报告输出和失败边界转成可重复测试。
  contexts_missing:
    - 真实 GGUF 权重和最终 Prompt 评测集。
  contexts_stale: []
  outcome_status: partial
  friction: "四个确定性工具已接入并有工具级测试；真实 Runtime 驱动润色/改写仍待实现。"
  revisit_needed: true
```
