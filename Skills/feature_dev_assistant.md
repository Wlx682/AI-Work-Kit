# feature-dev-assistant · 逐用户故事 TDD 开发

在已确认架构、Scope 和实现落点设计下实现一个纵向用户故事。每个故事必须执行：

```text
Red → Green → Refactor → integration smoke → 故事验收
```

证据写入故事 Plan 的 `tdd_evidence` JSON，包括命令、退出码、时间、commit 和逐 AC 结果。Red 必须先失败且说明失败仅因尚未实现；Green、Refactor 和 integration smoke 必须通过。

门禁：先通过 `python3 scripts/validate-client-dev.py implementation-design --plan Plans/功能开发/父Plan.md`，再用 `python3 scripts/validate-client-dev.py story-development --plan Plans/功能开发/父Plan.md --story-id US-xxx` 验收当前 Story。`workflow-gate.sh` 不传 `--story-id`，继续按整个 Epic Scope 判断能否退出 story-development。

纯 UI 步骤仍使用 `figma-ui`，但归属于当前用户故事。主 Plan 最后一个反馈增加 `workflow_stage: story-development`。
