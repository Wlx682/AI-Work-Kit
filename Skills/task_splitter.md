# task-splitter · 用户故事拆分与故事点

读取已采纳需求、已确认 Backlog 和已采纳架构，拆成可独立演示、独立验收的纵向用户故事。输出主 Plan、`.stories.json` 与故事子 Plan。

## 规则

- 每个故事必须 `vertical_slice: true`，覆盖 AC 并引用架构决策。
- UI、Domain、Data/API、异常和测试属于故事内部步骤，不作为横向交付故事。
- 故事点限 `1/2/3/5/8/13`，由 AI 提议、团队确认；禁止换算小时。
- 13 点故事进入 Scope 前必须继续拆分，或留下团队确认的 `estimate_waiver`。
- P0 AC 必须至少由一个 Scope 故事覆盖。

门禁：`python3 scripts/validate-client-dev.py story-scope --plan Plans/功能开发/xxx.md`。

最后一个反馈增加 `workflow_stage: story-split`。信息不足时列待确认项，禁止替产品确定 Scope。
