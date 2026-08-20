---
tags: [自动化测试, 集成测试计划, client-dev, DSH, Web]
type: plan
category: 自动化测试
status: 已采纳
date: 2026-08-20
lifecycle_state: integration-test-plan
epic: Plans/Epic/2026-08-20-agent受控DSH交互式Web入口.md
story_index: Plans/功能开发/2026-08-20-agent受控DSH交互式Web入口.stories.json
target_commit: "74b945b22fffa14db2af0c50b9befbae123962bf"
test_case_index: Plans/自动化测试/2026-08-20-agent受控DSH交互式Web入口-集成测试计划.cases.json
test_review: Plans/自动化测试/2026-08-20-agent受控DSH交互式Web入口-集成测试计划.review.json
---
# 集成测试计划：agent 受控 DSH 交互式 Web 入口

## 一、测试策略

- 冻结目标：`74b945b22fffa14db2af0c50b9befbae123962bf`。
- 范围：两个 Scope Story 的 12 条 P0 AC；真实 HTTP、双组合、参数/secret 逃逸、漂移、端口、信号、headless 和 release gate。
- 环境：macOS，Node 22.19.0，pnpm 11.7.0，DSH 0.1.0-rc.6，loopback 临时端口/目录。
- 非目标：不读取用户 API Key，不代做 AC-11/12 的真实模型多轮人工冒烟，不开放公网。

## 二、测试用例

| ID | 能力 | Story / AC | Suite |
|---|---|---|---|
| IT-CW-001 | 受控 Web 组合、URL 与 HTTP UI | US-CW-001 / AC-01/02/04 | controlled-web-runtime |
| IT-CW-002 | profile/patch/secret 逃逸失败关闭 | US-CW-001 / AC-06/07/08 | controlled-web-security |
| IT-CW-003 | 漂移、端口、公网 host、信号生命周期 | US-CW-002 / AC-05/09/10/13 | controlled-web-failure-lifecycle |
| IT-CW-004 | headless 不回退与发布入口冻结 | US-CW-002 / AC-03/14 | controlled-web-release |

## 三、需求与用例覆盖

| Story | AC | 用例 | 结论 |
|---|---|---|---|
| US-CW-001 | AC-01/02/04 | IT-CW-001 | 已覆盖 |
| US-CW-001 | AC-06/07/08 | IT-CW-002 | 已覆盖 |
| US-CW-002 | AC-05/09/10/13 | IT-CW-003 | 已覆盖 |
| US-CW-002 | AC-03/14 | IT-CW-004 | 已覆盖 |

## 四、执行 Suite

```text
nvm exec 22.19.0 corepack pnpm@11.7.0 test
nvm exec 22.19.0 corepack pnpm@11.7.0 typecheck
nvm exec 22.19.0 corepack pnpm@11.7.0 composition:verify
nvm exec 22.19.0 corepack pnpm@11.7.0 composition:web:verify
nvm exec 22.19.0 corepack pnpm@11.7.0 install --frozen-lockfile
nvm exec 22.19.0 corepack pnpm@11.7.0 --dir profiles/controlled-web install --frozen-lockfile
nvm exec 22.19.0 corepack pnpm@11.7.0 start -- --help
nvm exec 22.19.0 corepack pnpm@11.7.0 start:dsh:web -- --help
```

## 五、测试审核

- [x] 两个 Story 的全部 P0 AC 有结构化用例。
- [x] 真实进程测试均使用临时目录与 loopback 空闲端口并在 finally 清理。
- [x] target commit、用例索引 hash 和未解决意见数已冻结。
- [x] 测试审核通过后才执行最终集成报告。

## 反馈（skill_run）

```yaml
skill_run:
  skill: test-generator
  workflow_stage: integration-test-plan
  plan: Plans/自动化测试/2026-08-20-agent受控DSH交互式Web入口-集成测试计划.md
  date: 2026-08-20
  contexts_used:
    - path: Plans/功能开发/2026-08-20-agent受控DSH交互式Web入口.stories.json
      utility: high
      reason: "用两个 Story 的 12 条 P0 AC 建立四组可执行集成用例"
    - path: Plans/功能开发/2026-08-20-agent受控DSH交互式Web入口-US-CW-001.tdd.json
      utility: high
      reason: "复核真实 HTTP、双组合和启动逃逸的 Story 证据"
    - path: Plans/功能开发/2026-08-20-agent受控DSH交互式Web入口-US-CW-002.tdd.json
      utility: high
      reason: "复核失败生命周期、headless 和 release 边界"
  contexts_missing: []
  contexts_stale: []
  outcome_status: pass
  friction: "真实模型多轮对话需要用户凭证，明确留在 P1 人工冒烟而不伪造自动通过"
  revisit_needed: false
```
