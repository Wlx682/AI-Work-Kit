---
tags: [功能开发, B2, Definition, Planning, Roles]
type: plan
category: 功能开发
status: 已完成
date: 2026-08-17
lifecycle_state: story-development
parent: Plans/功能开发/2026-08-17-agent全仓TypeScript重构.md
story_id: US-B2-002
story_points: 8
sprint_scope: false
tdd_evidence: Plans/功能开发/2026-08-17-agent全仓TypeScript重构-US-B2-002.tdd.json
implementation_design: Plans/功能开发/2026-08-17-agent全仓TypeScript重构-US-B2-002.impl.json
---
# US-B2-002：迁写 Definition、LLM JSON、Planning 与 Role 语义

作为维护者，我想用共享 TS Definition/Prompt 契约和 Learning Runtime 验证 JSON、规划及角色边界，以便两个 Runtime 使用一致资产但各自采用原生编排机制。

覆盖 `M012—M025`。定义引用未知工具、非法版本或非字符串步骤时失败关闭；风险调整不得扩权。

## 当前 Scope

- 用户在 `US-B2-001` 完成后回复“继续”，因此本轮只激活 `US-B2-002`。
- 前置 `US-B1-001`、`US-B1-002` 均已完成并有 TDD 证据；其余未完成 Story 保持 `sprint_scope=false`。
- 当前只进入 implementation-design；未经落点门禁确认，不创建 Red 测试或业务实现，也不激活 `US-B2-003`。

## 实现落点设计草案

机器真理源：`Plans/功能开发/2026-08-17-agent全仓TypeScript重构-US-B2-002.impl.json`。用户在四项落点门禁摘要后回复“继续”，当前 `confirmed=true`，允许进入 Red。

- 共享 Definition：新增纯 TS `packages/agent-definition`，承载版本化 Definition JSON、Prompt、严格 loader、工具 allowlist 与默认角色资产；不依赖 DSH、Cordis、LangGraph、模型 SDK 或工具执行器。
- Learning 行为：在 `labs/runtimes/langgraph-ts` 新增注入 port 的 `llm-json.ts`、`planning.ts`、`roles.ts`，完成一次 JSON 修复、计划步骤校验、能力不扩张与角色 definition 透传；不创建第二生产 Runtime。
- Red：按已采纳矩阵在 Definition 3 组、Learning Lab 3 组与 migration map 验收中逐项覆盖 `M012—M025`。
- 组合保护：新增 workspace 包会改变根 lock；实现阶段必须证明 DSH rc.6、Cordis 4.0.1、Profile/Bundle/Provider 不变后显式重冻 production composition。

落点、依赖方向、Red 和停止条件已由用户确认；开发必须按 Red→Green→Refactor 执行且不得扩大到下一 Story。

## TDD 完成证据

- 代码提交：`5bcce5a76c30aa3304405c02cbb40558b60157bb`。
- Red：7 个目标测试文件先以新模块不存在和 M012—M025 旧迁移路径失败，`exit_code=1`。
- Green/Refactor：共享 `@agent/agent-definition` 与 Learning-only `llm-json/planning/roles` 完成；定向 17/17 通过。
- Integration smoke：TypeScript 82/82、Python 60/60、全仓 typecheck、冻结安装、DSH composition verify 与真实 headless `--help` 通过。
- 组合指纹：`d1c52876f3cdab22bff9e1419642a83b78a444747fc1639fd0052fda42c3083f`；仅根 lock SHA 与总指纹变化，生产 Profile/Provider/artifact/finalConfig 不变。
- TDD 真理源：`Plans/功能开发/2026-08-17-agent全仓TypeScript重构-US-B2-002.tdd.json`。

本 Story 已完成并退出当前滚动 Scope；用户回复“继续”后，下一条 `US-B2-003` 已单独激活。

续做：`/resume plan=Plans/功能开发/2026-08-17-agent全仓TypeScript重构.md 进度=next-story-scope`
