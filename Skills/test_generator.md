# test-generator · 测试生成与全量集成

client-dev 中只在全部 Scope 故事完成后执行 `integration-test`；其他 workflow 按各自蓝图执行。

读取 `.stories.json`、各故事 `tdd_evidence` 和需求 AC，生成跨故事路径、真实契约、错误恢复和全量回归 suite。集成报告必须与 Plan 的 `target_commit` 一致，所有 suite `exit_code: 0`。

门禁：`python3 scripts/validate-client-dev.py integration --plan Plans/自动化测试/xxx.md`。

通过后直接 Done，不创建发布、灰度或线上观察阶段。最后一个反馈增加 `workflow_stage: integration-test`。
