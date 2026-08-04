---
tags: [功能开发, Flutter, LLM, GGUF, 本地模型]
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

# 子任务 08：本地模型 Runtime 与 GGUF 接入

## 一、需求分析（开工门禁）

- 需求：`Plans/需求分析/2026-08-04-Flutter版劳动仲裁生成式智能助手App.md`
- 方案：`Plans/技术方案/2026-08-04-Flutter版劳动仲裁生成式智能助手App.md`
- 结论：承接生成式增强版本的本地 LLM 能力；不改变 P0 确定性计算和法条权威边界。

## 二、输入与输出

| 输入 | 输出 |
|------|------|
| `LlmClient`、`LocalLlmService`、GGUF 模型配置、模型状态契约 | 可替换的本地推理 Runtime、模型生命周期状态、加载失败恢复和可观测运行结果 |

## 三、范围与边界

- 只接本地模型，不接云端 LLM/API，不把案情发送到网络。
- 模型权重不提交到代码仓库；通过模型 manifest、路径注入和校验结果接入。
- Runtime 负责加载、推理、超时、卸载和失败状态；不负责赔偿金额、法条结论或 Agent 业务规则。
- Android 设备验证按当前用户范围暂缓；先完成平台无关 adapter、fake backend 和 iOS 可验证路径。

## 四、实施与验收

- [ ] 将 `LocalLlmService` 抽象为可注入 backend，补齐 GGUF load/complete/unload 生命周期。
- [ ] 扩展 `ModelRuntimeStatus` 覆盖 missing/loading/ready/loadFailed/unloaded，并保留用户可读错误信息。
- [ ] 增加模型 manifest、路径存在性、上下文长度、内存/超时和资源释放策略。
- [ ] `LocalLlmClient` 在 Runtime ready 时返回真实 completion/JSON 提取；不可用时显式降级，不吞异常。
- [ ] 使用 fake backend 覆盖成功、路径缺失、加载失败、推理超时、卸载后再次加载和无网络约束。
- [x] 已完成可注入 backend、loading/ready/loadFailed/unloaded 状态、JSON 提取接缝和 fake backend 基础测试。
- [ ] 真实 flutter_llama/llama.cpp FFI backend、模型 manifest 校验和真机性能验证仍待实现。

## 五、验收标准

- 模型不存在或加载失败时，确定性报告、法条检索和文书生成继续可用。
- 模型 ready 时能完成一次受 schema 约束的本地 JSON 提取；金额字段不能覆盖计算器结果。
- 推理超时/内存异常会释放 Runtime，并暴露可诊断状态，不导致 App 崩溃。
- 测试不下载真实大模型权重，不访问云端；真实 GGUF 只在具备模型文件的设备上做手工/集成验证。

## 六、依赖与续做

- 依赖：子任务 02、本地 `LlmClient` 契约；与子任务 09 的 Prompt/Agent 编排联调。
- 代码仓库：`/Users/wanglongxiang/git/labor_assistant`
- 续做：`/resume plan=Plans/功能开发/2026-08-04-Flutter版劳动仲裁生成式智能助手App-子任务08-本地模型Runtime与GGUF接入.md 进度=实现`

## 七、反馈（skill_run）

```yaml
skill_run:
  skill: task-splitter
  plan: Plans/功能开发/2026-08-04-Flutter版劳动仲裁生成式智能助手App-子任务08-本地模型Runtime与GGUF接入.md
  date: 2026-08-04
  contexts_used:
    - path: Plans/技术方案/2026-08-04-Flutter版劳动仲裁生成式智能助手App.md
      utility: high
      reason: 用于承接 LlmClient、LocalLlmService、GGUF 生命周期和 ADR-003 的本地优先边界。
    - path: Plans/自动化测试/2026-08-04-Flutter版劳动仲裁生成式智能助手App.md
      utility: high
      reason: 用于把模型加载失败、超时和确定性降级转成可执行测试契约。
    - path: Contexts/决策/Skill原子契约.md
      utility: high
      reason: 用于保持 Runtime 与 Agent 编排、UI 展示的职责边界。
  contexts_missing:
    - 可提交到测试环境的真实 GGUF 权重与 Android SDK/设备；不阻塞计划拆分。
  contexts_stale: []
  outcome_status: pass
  friction: "现有代码只有 notInstalled 占位 Runtime，真实 flutter_llama/FFI backend 需在本子任务实现。"
  revisit_needed: false
```

```yaml
skill_run:
  skill: resume-assistant
  plan: Plans/功能开发/2026-08-04-Flutter版劳动仲裁生成式智能助手App-子任务08-本地模型Runtime与GGUF接入.md
  date: 2026-08-04
  contexts_used:
    - path: Plans/Epic/2026-08-04-Flutter版劳动仲裁生成式智能助手App.md
      utility: high
      reason: 用于恢复 7d 模型 Runtime 子任务的依赖和本轮执行顺序。
    - path: Plans/技术方案/2026-08-04-Flutter版劳动仲裁生成式智能助手App.md
      utility: high
      reason: 用于落实 LlmClient、Runtime 生命周期和 P0 降级 ADR。
    - path: Contexts/决策/Skill反馈协议.md
      utility: high
      reason: 用于追加本次续做反馈。
  contexts_missing:
    - 真实 GGUF 权重和 native backend；当前 fake backend 契约已先落地。
  contexts_stale: []
  outcome_status: partial
  friction: "Runtime 契约、状态机和测试接缝已完成；真实 flutter_llama/FFI backend 尚未接入。"
  revisit_needed: true
```

```yaml
skill_run:
  skill: feature-dev-assistant
  plan: Plans/功能开发/2026-08-04-Flutter版劳动仲裁生成式智能助手App-子任务08-本地模型Runtime与GGUF接入.md
  date: 2026-08-04
  contexts_used:
    - path: Plans/技术方案/2026-08-04-Flutter版劳动仲裁生成式智能助手App.md
      utility: high
      reason: 用于按 ADR-003 将本地推理做成可替换 Runtime，不让模型覆盖确定性规则。
    - path: Plans/自动化测试/2026-08-04-Flutter版劳动仲裁生成式智能助手App.md
      utility: high
      reason: 用于验证 Runtime 生命周期、失败状态、JSON 接缝和降级行为。
  contexts_missing:
    - 真实 GGUF 权重和 native backend。
  contexts_stale: []
  outcome_status: partial
  friction: "完成 Runtime 状态机、可注入 backend 和 4 项测试；真实 native 推理仍是下一步。"
  revisit_needed: true
```
