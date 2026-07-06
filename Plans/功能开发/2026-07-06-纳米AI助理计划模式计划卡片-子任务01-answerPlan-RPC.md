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
    - Plans/功能开发/2026-07-06-纳米AI助理计划模式计划卡片.md
  dependents: []
  supersedes: []
  superseded_by: []
  conflicts: []
---

# 子任务01：新增 `chat.answerPlan` RPC

**parent**：[[2026-07-06-纳米AI助理计划模式计划卡片]]
**覆盖 AC**：AC2, AC3, AC4（底层通道）
**依赖**：无（基座，可与 T02 并行）

## 输入
- 接口文档（飞书 docx Hh2rdLmLSo4cgyxiTALc69pJncf `chat.answerPlan`）：
  `params = { requestId, approve: Bool, feedback: String }`，成功 `{ ok: true }`。
- 现有先例：`abortChat`（`NAMIWork/Core/Services/GatewayCore/Connection/GatewayRPCClient.swift:1221`）。

## 步骤
1. 在 `GatewayRPCClient.swift` 紧邻 `abortChat`/`injectChat` 处新增：
   ```swift
   /// chat.answerPlan —— 计划卡片审批。approve=true 开始执行；approve=false + feedback 打回重规划。
   /// requestId = 计划卡片 ExitPlanMode 的 toolCallId。
   func answerPlan(requestId: String, approve: Bool, feedback: String? = nil) async throws {
       var params: [String: Any] = ["requestId": requestId, "approve": approve]
       if let feedback { params["feedback"] = feedback }  // approve=true 时不带
       _ = try await session.request(
           method: "chat.answerPlan",
           paramsJSON: try encodeParamsJSON(params),
           timeoutSeconds: 15)
   }
   ```
2. 日志用 `BRSfSimpleLog(format: "[PlanCard] answerPlan requestId=\(requestId) approve=\(approve)")`（不记 feedback 明文，仅记长度/是否为空）。

## 输出
- `GatewayRPCClient.swift` 新增 `answerPlan(requestId:approve:feedback:)`。

## 验收
- [ ] `xcodebuild build`（见 CLAUDE.md 编译验证命令）通过。
- [ ] 方法签名与接口文档字段一致（requestId/approve/feedback）；approve=true 不带 feedback。
- [ ] 日志不落 feedback 明文。

## 不做
- 不在此任务接 UI；调用点在 T05/T06。
