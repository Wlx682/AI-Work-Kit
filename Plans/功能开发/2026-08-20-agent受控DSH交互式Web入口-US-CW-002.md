---
tags: [功能开发, 用户故事, TDD, DSH, 安全门禁]
type: plan
category: 功能开发
status: 已完成
date: 2026-08-20
lifecycle_state: story-development
parent: Plans/功能开发/2026-08-20-agent受控DSH交互式Web入口.md
requirement_plan: Plans/需求分析/2026-08-20-agent受控DSH交互式Web入口.md
architecture_plan: Plans/技术方案/2026-08-20-agent受控DSH交互式Web入口.md
story_id: US-CW-002
story_points: 5
sprint_scope: true
implementation_design: Plans/功能开发/2026-08-20-agent受控DSH交互式Web入口-US-CW-002.impl.json
tdd_evidence: Plans/功能开发/2026-08-20-agent受控DSH交互式Web入口-US-CW-002.tdd.json
---
# US-CW-002：验证受控 Web 失败关闭且 headless 不回退

作为维护者，我要让受控 Web 在组合漂移、端口冲突、公网绑定时失败关闭，并证明停止后释放端口且原 headless 入口不回退，以便长期安全维护双入口。

## 验收标准

- AC-03：`start` / `start:dsh` 仍为一次性 headless，不加载 Web host。
- AC-05：组合漂移在绑定端口前阻断。
- AC-09/10：端口冲突与 `0.0.0.0` 明确失败，不影响原监听者。
- AC-13：SIGTERM/SIGINT 后进程退出、端口释放、持久化数据保留。
- AC-14：文档只把 `start:dsh:web` 标记为受控 Web 入口。

## 故事边界

包含：失败关闭集成测试、headless 回归、release rehearsal 与使用文档。
不含：公网部署、鉴权网关、修改官方 DSH Web 产品功能。

## 架构引用

- ADR-CW-001..006。

## 实现落点设计

- 失败关闭复用 launcher 前置校验，不把策略散落到 shell 脚本。
- 真实进程测试覆盖端口冲突、外网绑定、信号退出与端口释放。
- 原 controlled lock、help 和一次性 headless 任务继续作为回归证据。

## 反馈（skill_run）

```yaml
skill_run:
  skill: implementation-design-assistant
  workflow_stage: implementation-design
  plan: Plans/功能开发/2026-08-20-agent受控DSH交互式Web入口-US-CW-002.md
  date: 2026-08-20
  contexts_used:
    - path: Plans/需求分析/2026-08-20-agent受控DSH交互式Web入口.md
      utility: high
      reason: "用 AC-03/05/09/10/13/14 明确失败关闭和 headless 回归的真实进程测试边界"
  contexts_missing: []
  contexts_stale: []
  outcome_status: pass
  friction: "长驻 Web 测试必须保证 finally 清理子进程，避免污染后续测试端口"
  revisit_needed: false
```

## 依赖

- US-CW-001。

## TDD 结果

- Red：在 Story 1 提交 `d9d596b` 上，release gate 因 README、Web verify 和 controlled-web supply-chain 门禁缺失而失败。
- Green：提交 `ca059a2`、`74b945b` 补齐公网/漂移/端口/信号/headless 反例、文档与发布排练。
- Refactor：失败关闭逻辑集中在 launcher，测试只从 unit/真实进程/release 三层观察，不复制安全策略。

## 反馈（skill_run）

```yaml
skill_run:
  skill: feature-dev-assistant
  workflow_stage: story-development
  plan: Plans/功能开发/2026-08-20-agent受控DSH交互式Web入口-US-CW-002.md
  date: 2026-08-20
  contexts_used:
    - path: Plans/功能开发/2026-08-20-agent受控DSH交互式Web入口-US-CW-002.impl.json
      utility: high
      reason: "用 drift、端口冲突、loopback、信号与 headless 回归闭合失败关闭边界"
  contexts_missing: []
  contexts_stale: []
  outcome_status: pass
  friction: "端口冲突测试必须保留原 listener，并在 finally 中关闭临时资源"
  revisit_needed: false
```

## 续做

```text
/resume plan=Plans/功能开发/2026-08-20-agent受控DSH交互式Web入口-US-CW-002.md 进度=implementation-design
```
