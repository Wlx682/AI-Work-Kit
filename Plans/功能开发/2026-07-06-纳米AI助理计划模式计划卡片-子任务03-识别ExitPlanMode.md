---
tags: [功能开发, 客户端, 子任务, 计划模式]
type: plan
category: 功能开发
status: 已完成
date: 2026-07-06
lifecycle_state: development
parent: Plans/功能开发/2026-07-06-纳米AI助理计划模式计划卡片.md
含业务逻辑: 是
relations:
  depends_on:
    - Plans/功能开发/2026-07-06-纳米AI助理计划模式计划卡片-子任务02-命令与CellVM.md
  dependents: []
  supersedes: []
  superseded_by: []
  conflicts: []
---

# 子任务03：识别 `ExitPlanMode` → 插卡命令

**parent**：[[2026-07-06-纳米AI助理计划模式计划卡片]]
**覆盖 AC**：AC1, AC1-反
**依赖**：T02（命令 + CellVM 已就位）

## 输入
- 方案 §5.3 识别契约：内层 `stream=tool`, `name=="ExitPlanMode"`, `phase` start/result, `data.toolCallId`, `data.args.plan`。
- `nami_panel` 拆包已由 `NMChatServerEventRouter.handleNamiPanelEvent`（`Network/SubHandlers/NMChatServerEventRouter.swift:312`）完成，识别落在统一 tool 分支，**不碰 Router**。
- 落点：`NMChatCommandProcessor.processAgentEvent` 的 `case "tool"`（`Command/NMChatCommandProcessor.swift:278`），旁边 `if name == "swarm_plan"`（:288）是同款先例。
- 插卡执行：`NMChatViewModel.applyCommand`（`ViewModel/NMChatViewModel.swift`）。

## 步骤
1. 在 `NMChatCommandProcessor` tool 分支的 `phase=="start"` 判定**之前**加：
   ```swift
   if name == "ExitPlanMode" {
       if let cmds = processExitPlanModeTool(agentEvent: agentEvent, phase: phase) { return cmds }
   }
   ```
   （result 分支同 swarm_plan 写法，在 `phase=="result"` 里也加一支）
2. 新增 `processExitPlanModeTool(agentEvent:phase:)`：
   - `phase=="start"`：取 `data.args.plan`（stringValue）、`toolCallId`；结束当前 thinking/text（`currentThinkingCellId=nil; currentTextCellId=nil`）；返回 `[.removeLoading, .insertPlanCard(messageId: planCardCellId, runId, toolCallId, planMarkdown, timestamp)]`。plan 为空则返回 nil 退化为普通 tool。
   - `phase=="result"`：返回 `[.updatePlanCardState(toolCallId: toolCallId, state: .consumed)]`。
3. 在 `NMChatViewModel.applyCommand` 实现三条命令：
   - `insertPlanCard`：`isLatest` 处理——遍历现有 `NMChatPlanCardCellVM`，把 `pending` 的翻 `disabled`（旧卡失效，AC2-反基座）；再 append 新 CellVM（isLatest=true）。
   - `updatePlanCardState`：按 toolCallId 找卡，`updateState`，加入 `updatedItemIds`。
   - `updatePlanCardMarkdown`：按 messageId 找卡，`updateMarkdown`。

## 输出
- Processor 新增 `processExitPlanModeTool` + tool 分支两处挂钩；ViewModel 三条命令落地。

## 验收
- [ ] `xcodebuild build` 通过。
- [ ] AC1：mode=plan 会话收到 ExitPlanMode(start) → 插入计划卡片（可用日志/单测断言命令序列）。
- [ ] AC1-反：非 ExitPlanMode 的 tool（如普通工具）**不**走计划卡片分支，仍普通 tool 渲染。
- [ ] plan 为空时退化为普通 tool（回滚兜底）。

## 不做
- 不做 Cell 渲染（T04）、不做按钮交互（T05）。
