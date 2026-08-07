# test-generator · 集成测试计划、审核与执行

client-dev 中在全部 Scope 故事完成后分两阶段执行：`integration-test-plan` 产出可审核用例，`integration-test` 只执行已审核的计划。其他 workflow 按各自蓝图执行。

## integration-test-plan

1. 若当前阶段 Plan 缺失，先执行 `python3 scripts/workflow-plan-init.py --workflow client-dev --epic Plans/Epic/xxx.md`。
2. 读取 `.stories.json`、各 Story `tdd_evidence`、需求 AC、架构风险和历史回归范围。
3. 写入 `test_case_index` JSON；每条用例须有 ID、Story/AC 引用、优先级、类型、前置条件、测试数据、步骤、预期结果、suite 和自动化状态。
4. 提交测试人员审核。审核证据 `test_review` JSON 必须记录 `approved=true`、审核人、时间、`target_commit`、用例索引 SHA-256 和未解决意见数。
5. 审核后用例索引变更会使审核失效，必须重新送审。
6. 门禁：`python3 scripts/validate-client-dev.py test-plan --plan Plans/自动化测试/xxx-集成测试计划.md`。
7. 最后一个反馈增加 `workflow_stage: integration-test-plan`。

## integration-test

1. 仅消费 `approved_test_plan`指向的已审核计划，不得边执行边静默改用例。
2. 冻结 `target_commit`，按已审核用例执行跨 Story 路径、真实契约、错误恢复和全量回归 suite。
3. 集成报告必须与 Plan 的 `target_commit` 一致，所有 suite `exit_code: 0`。
4. 执行中如需新增或重大修改用例，退回 `integration-test-plan` 重新审核。
5. 门禁：`python3 scripts/validate-client-dev.py integration --plan Plans/自动化测试/xxx-集成测试.md`。
6. 最后一个反馈增加 `workflow_stage: integration-test`。
7. 通过后直接 Done，不创建发布、灰度或线上观察阶段。
