---
tags: [功能开发, 用户故事, 故事点, 敏捷]
type: plan
category: 功能开发
status: 已完成
date: 2026-08-20
lifecycle_state: story-development
epic: Plans/Epic/2026-08-20-agent受控DSH交互式Web入口.md
requirement_plan: Plans/需求分析/2026-08-20-agent受控DSH交互式Web入口.md
architecture_plan: Plans/技术方案/2026-08-20-agent受控DSH交互式Web入口.md
story_index: Plans/功能开发/2026-08-20-agent受控DSH交互式Web入口.stories.json
relations:
  depends_on:
    - Templates/模板约定.md
    - Templates/客户端功能开发模板.md
  dependents:
    - Templates/客户端功能开发模板.md
  supersedes: []
  superseded_by: []
  conflicts: []

---
# 用户故事拆分：agent受控DSH交互式Web入口

## 一、输入门禁

- 需求排序：`Plans/需求排序/2026-08-20-agent受控DSH交互式Web入口.md`，已采纳。
- 架构方案：`Plans/技术方案/2026-08-20-agent受控DSH交互式Web入口.md`，已采纳。

## 二、纵向故事索引

| Story ID | 用户能力 | AC | 架构引用 | 依赖 | 优先级 | 故事点 | Scope | 子 Plan |
|----------|----------|----|----------|------|--------|--------|-------|---------|
| US-CW-001 | 开发者一条命令打开控制插件完整的受控 DSH Web | AC-01/02/04/06/07/08 | ADR-CW-001..006 | — | P0 | 8 | true | `Plans/功能开发/2026-08-20-agent受控DSH交互式Web入口-US-CW-001.md` |
| US-CW-002 | 维护者验证 Web 失败关闭且 headless 不回退 | AC-03/05/09/10/13/14 | ADR-CW-001..006 | US-CW-001 | P0 | 5 | true | `Plans/功能开发/2026-08-20-agent受控DSH交互式Web入口-US-CW-002.md` |

JSON 真理源：`story_index`。每个故事必须 `vertical_slice: true`，故事点限 `1/2/3/5/8/13`；13 点进入 Scope 前须继续拆分或留下团队确认的豁免。

## 三、拆分规则

- 一个故事交付一个可演示、可验收的用户能力。
- UI、Domain、Data/API 和测试是故事内部步骤，不作为横向交付故事。
- 共享底座归入首个消费故事，或标记为有明确消费者的 enabler。
- 禁止 `estimated_hours` 等故事点换工时字段。

## 四、Scope 确认

- [x] 所有 P0 AC 至少由一个 Scope 故事覆盖
- [x] 所有 Scope 故事已有团队确认的故事点
- [x] 13 点故事已拆分或豁免（本轮无 13 点故事）
- [x] `scope_confirmed: true`

## 实现落点设计

| Story | 契约/领域落点 | 适配器/入口落点 | Red 证据 |
|---|---|---|---|
| US-CW-001 | `runtime-composition` profile 闭集、`ControlledProfileSpec` | `controlled-web` profile、foreground launcher、`start:dsh:web` | contract + launcher + HTTP smoke |
| US-CW-002 | 启动覆盖/密钥/公网绑定失败关闭 | drift/port/signal/headless 回归、README 与 release gate | fault-injection + real process regression |

详细契约：
- `Plans/功能开发/2026-08-20-agent受控DSH交互式Web入口-US-CW-001.impl.json`
- `Plans/功能开发/2026-08-20-agent受控DSH交互式Web入口-US-CW-002.impl.json`

## 反馈（skill_run）

```yaml
skill_run:
  skill: task-splitter
  workflow_stage: story-split
  plan: Plans/功能开发/2026-08-20-agent受控DSH交互式Web入口.md
  date: 2026-08-20
  contexts_used:
    - path: Plans/需求分析/2026-08-20-agent受控DSH交互式Web入口.md
      utility: high
      reason: "用 14 条 AC 保证所有 P0 安全边界均由纵向 Story 承接"
    - path: Plans/技术方案/2026-08-20-agent受控DSH交互式Web入口.md
      utility: high
      reason: "依据双 profile、独立锁和前台 runner 划分两个纵向能力"
  contexts_missing: []
  contexts_stale: []
  outcome_status: pass
  friction: "无"
  revisit_needed: false
```

## 反馈（skill_run）

```yaml
skill_run:
  skill: implementation-design-assistant
  workflow_stage: implementation-design
  plan: Plans/功能开发/2026-08-20-agent受控DSH交互式Web入口.md
  date: 2026-08-20
  contexts_used:
    - path: Plans/技术方案/2026-08-20-agent受控DSH交互式Web入口.md
      utility: high
      reason: "将 ProfileSpec、独立 lock、foreground runner 与 Red 测试映射到精确代码路径"
  contexts_missing: []
  contexts_stale: []
  outcome_status: pass
  friction: "Web 长驻进程不能复用缓冲到退出的 runner"
  revisit_needed: false
```

## 反馈（skill_run）

```yaml
skill_run:
  skill: feature-dev-assistant
  workflow_stage: story-development
  plan: Plans/功能开发/2026-08-20-agent受控DSH交互式Web入口.md
  date: 2026-08-20
  contexts_used:
    - path: Plans/技术方案/2026-08-20-agent受控DSH交互式Web入口.md
      utility: high
      reason: "按双 profile、独立 lock、foreground runner 与身份注入完成两个纵向 Story 的 TDD 闭环"
  contexts_missing: []
  contexts_stale: []
  outcome_status: pass
  friction: "真实 Web 冒烟要求为控制插件提供本地 ledger/socket 路径；测试使用临时目录且不读取用户 API Key"
  revisit_needed: false
```

## 续做

```text
/resume plan=Plans/自动化测试/2026-08-20-agent受控DSH交互式Web入口-集成测试.md 进度=Done
```
