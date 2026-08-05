---
name: test-generator
description: 生成并执行测试计划。client-dev 中只在全部 Scope 故事完成后负责 integration-test 全量集成测试和回归报告；其他 workflow 保持各自蓝图声明的测试模式。触发词：写测试、测试计划、集成测试、全量回归、test-generator。
---

# 测试生成与全量集成

普通测试用 `Templates/自动化测试模板.md`；client-dev 用 `Templates/集成测试模板.md`。

## client-dev

1. 运行 workflow gate，确认当前为 `integration-test`；任一 Scope 故事未完成时不得继续。
2. 读取 `.stories.json`、各故事 `tdd_evidence` 和需求 AC。
3. 设计跨故事核心路径、真实契约、错误恢复和全量回归 suite。
4. 冻结 `target_commit`，执行测试并写 `integration_report` JSON。
5. 报告必须 `all_scope_stories_completed: true`，commit 与 Plan 一致，所有 suite `exit_code: 0`。
6. 运行 `python3 scripts/validate-client-dev.py integration --plan Plans/自动化测试/xxx.md`。
7. 最后一个 `skill_run` 增加 `workflow_stage: integration-test`。
8. 通过后直接 Done；不创建发布、灰度或线上观察阶段。

## 兼容边界

- 非 client-dev 请求继续按对应蓝图和现有自动化测试模板执行。
- 不通过修改 `lifecycle_state` 推进阶段。
