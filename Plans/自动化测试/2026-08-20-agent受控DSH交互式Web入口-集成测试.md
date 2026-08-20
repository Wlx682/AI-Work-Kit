---
tags: [自动化测试, 集成测试, client-dev, DSH, Web]
type: plan
category: 自动化测试
status: 已完成
date: 2026-08-20
lifecycle_state: integration-test
epic: Plans/Epic/2026-08-20-agent受控DSH交互式Web入口.md
story_index: Plans/功能开发/2026-08-20-agent受控DSH交互式Web入口.stories.json
approved_test_plan: Plans/自动化测试/2026-08-20-agent受控DSH交互式Web入口-集成测试计划.md
target_commit: "74b945b22fffa14db2af0c50b9befbae123962bf"
integration_report: Plans/自动化测试/2026-08-20-agent受控DSH交互式Web入口-集成测试.integration.json
---
# 全量集成测试：agent 受控 DSH 交互式 Web 入口

## 一、进入门禁

- [x] US-CW-001 / US-CW-002 均已通过逐 Story TDD 门禁。
- [x] 测试计划审核通过，用例索引 SHA-256 `2974e119bd754f6f761b7651ec088e99ffad5f38fda09bed6b8d7bb9e6965289` 未漂移。
- [x] 代码目标固定为 `74b945b22fffa14db2af0c50b9befbae123962bf`。

## 二、结果

| Suite | 结果 | 证据 |
|---|---|---|
| controlled-web-runtime | passed | launcher/profile/HTTP/端口/信号/headless/release 聚焦测试全部通过 |
| all-typescript | passed | 73 files / 226 tests；typecheck 通过 |
| composition-and-supply-chain | passed | 双 lock verify、root/Web frozen install、headless/Web help 均为 exit 0 |

## 三、结论与边界

4 条审核用例、两个 Story 和 12 条 P0 AC 全部通过。受控 Web 可在 loopback 真实启动，headless 默认入口没有回退，失败关闭与发布门禁已闭合。

未读取用户 `DEEPSEEK_API_KEY`，所以真实模型多轮对话和会话恢复没有伪装为自动化通过；它们作为 AC-11/12 的 P1 人工冒烟，在用户本机配置凭证后执行。

## 反馈（skill_run）

```yaml
skill_run:
  skill: test-generator
  workflow_stage: integration-test
  plan: Plans/自动化测试/2026-08-20-agent受控DSH交互式Web入口-集成测试.md
  date: 2026-08-20
  contexts_used:
    - path: Plans/自动化测试/2026-08-20-agent受控DSH交互式Web入口-集成测试计划.md
      utility: high
      reason: "只执行已审核且绑定 target commit 的四条用例"
    - path: Plans/自动化测试/2026-08-20-agent受控DSH交互式Web入口-集成测试计划.review.json
      utility: high
      reason: "确认用例 hash 未漂移且零未解决意见"
    - path: Plans/功能开发/2026-08-20-agent受控DSH交互式Web入口.stories.json
      utility: high
      reason: "最终核对两个 Story 的完成状态与 12 条 P0 AC"
  contexts_missing: []
  contexts_stale: []
  outcome_status: pass
  friction: "Node 22 内置 SQLite 输出实验性警告，不影响测试结果"
  revisit_needed: false
```
