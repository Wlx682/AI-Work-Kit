---
name: test-generator
description: 生成并执行测试计划。client-dev 中在全部 Scope Story 完成后，先在 integration-test-plan 产出用例并经测试审核，再在 integration-test 执行已审核计划和全量回归；其他 workflow 保持蓝图声明的测试模式。触发词：写测试、测试计划、测试审核、集成测试、全量回归、test-generator。
---

# 集成测试计划、审核与全量集成

普通测试用 `Templates/自动化测试模板.md`；client-dev 的计划阶段用 `Templates/集成测试计划模板.md`，执行阶段用 `Templates/集成测试模板.md`。

## client-dev

1. 运行 workflow gate；任一 Scope Story 未完成时不得进入测试计划。
2. 当前为 `integration-test-plan` 时，读取 Story/AC/TDD/架构风险，产出结构化 `test_case_index` JSON。每条用例必须有 ID、Story/AC 引用、优先级、前置条件、数据、步骤、预期结果、suite 和自动化状态。
3. 计划必须交由测试人员审核；`test_review` 记录审核人、时间、target commit、用例索引 SHA-256 和未解决意见数。用例变更后必须重审。
4. 运行 `python3 scripts/validate-client-dev.py test-plan --plan Plans/自动化测试/xxx-集成测试计划.md`，反馈标记 `workflow_stage: integration-test-plan`。
5. 当前为 `integration-test` 时，只执行 `approved_test_plan` 指向的已审核用例，冻结同一 `target_commit`，写入 `integration_report` JSON。
6. 报告必须 `all_scope_stories_completed: true`，commit 与已审核计划一致，所有 suite `exit_code: 0`。新增或重大修改用例时退回计划阶段重审。
7. 运行 `python3 scripts/validate-client-dev.py integration --plan Plans/自动化测试/xxx-集成测试.md`，反馈标记 `workflow_stage: integration-test`。
8. 通过后直接 Done；不创建发布、灰度或线上观察阶段。

## 兼容边界

- 非 client-dev 请求继续按对应蓝图和现有自动化测试模板执行。
- 不通过修改 `lifecycle_state` 推进阶段。
