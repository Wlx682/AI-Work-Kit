---
tags: [功能开发, B2, Tools, CLI]
type: plan
category: 功能开发
status: 已完成
date: 2026-08-17
lifecycle_state: story-development
parent: Plans/功能开发/2026-08-17-agent全仓TypeScript重构.md
story_id: US-B2-005
story_points: 8
sprint_scope: true
tdd_evidence: Plans/功能开发/2026-08-17-agent全仓TypeScript重构-US-B2-005.tdd.json
implementation_design: Plans/功能开发/2026-08-17-agent全仓TypeScript重构-US-B2-005.impl.json
---
# US-B2-005：通过结构化工具与 CLI 操作、暂停和恢复任务

作为学习者，我想通过 TS CLI 查看结构化工具结果、审批原因、warning 并恢复同一 thread，以便完整保留原 TUI/工具的可观察语义。

覆盖 `M044—M060`。工具 schema 错误不能包装成成功；CLI 必须支持中文、结构化 unknown resolution 和可操作错误。

## 当前 Scope

- 用户在 `US-B2-004` 完成后回复“继续”，因此本轮只激活 `US-B2-005`。
- 前置 `US-B2-001`、`US-B2-003` 均已完成并有 TDD/提交证据；其余 6 个未完成 Story 保持 `sprint_scope=false`。
- 用户已确认落点；`US-B2-005` 已完成 Red→Green→Refactor 与 integration smoke，且没有激活 `US-B3-001`。

续做：`/resume plan=Plans/功能开发/2026-08-17-agent全仓TypeScript重构.md 进度=next-story-scope`

## 实现落点设计草案

机器真理源：`Plans/功能开发/2026-08-17-agent全仓TypeScript重构-US-B2-005.impl.json`；用户回复“继续”后已更新为 `confirmed=true`，允许进入 Red。

- 工具契约：在纯 TS `packages/contracts` 增加 MCP text content、structuredContent 与 outputSchema 子集校验；`plugins/domain-tools` 只用该契约约束未来项目特有工具，不迁入通用 `fs/shell/time`。
- Learning 工具：五个旧本地工具只迁写到 `labs/runtimes/langgraph-ts/src/tools.ts`，作为隔离离线适配器；成功结果执行后立即校验，显式错误保留 MCP error 形状，shell timeout 进入 unknown/不可判定。
- CLI/TUI：保留现有 raw JSON 命令，增加 `tool` 与交互 `tui`；`tui.ts` 用窄 RuntimePort 统一 single/team，controller 只保存 paused result，并用原 `threadId + parentRunId` 恢复。
- 终端边界：旧 Python curses 不逐行翻译，改为可注入 line/ANSI-fullscreen TerminalAdapter；宽字符按完整 JS 字符串传递，提交期日志捕获必须 `try/finally` 还原，不污染 raw JSON stdout。
- Red：M044—M047 落在已采纳的 `tools.spec.ts` 与 `domain-tools/test/output-contract.spec.ts`；M048—M060 全部落在 `cli.spec.ts`，并修正 migration map 漂移。
- Team/凭证：`--team` 通过离线默认 Team ports 实际启动，不接模型 SDK、API key 或生产 DSH Profile；Learning 启动不做密钥预检。

文件落点、依赖方向、Red 与停止条件已经用户确认；当前进入 `feature-dev-assistant`，严格先创建 Red。

## TDD 完成证据

- 代码提交：`61b2fed7b1f0e848bc44ce2d9b55c381f0bdf591`。
- Red：迁移路径门禁先通过；`tools.ts`、`tui.ts` 与 `domain-tools/src/index.ts` 尚不存在时，三组目标测试以模块缺失失败，原因只来自本 Story 未实现。
- Green：共享结果契约、domain-tools、Learning tools 与 CLI 目标共 `22/22` 通过；其中 M044—M060 目标语义 `18/18`。
- Refactor：共享 outputSchema validator 下沉纯 contracts；通用工具只留 Learning Lab；single/team controller、line/fullscreen adapter 与 raw JSON 命令保持分层。
- Integration smoke：TypeScript `120/120`、Python `60/60`、全仓 typecheck、冻结安装、真实 Learning help/tool/Team TUI 与生产 DSH headless `--help` 通过。
- 组合显式重冻为 `2467ba28…bbdd3`；仅 root lock、contracts artifact 与总指纹变化，DSH/Cordis/Profile/Provider/finalConfig 保持不变。
- TDD 真理源：`Plans/功能开发/2026-08-17-agent全仓TypeScript重构-US-B2-005.tdd.json`。

本 Story 已完成；继续保持为当前滚动 Scope，等待用户确认后再切换到 `US-B3-001`，不会自动进入集成测试。
