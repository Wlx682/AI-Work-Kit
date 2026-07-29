---
tags: [review, iOS, ClawChat, 多网关, merge]
date: 2026-07-28
status: 修改后通过
---

# Code Review：NMChatNetworkHandler 多网关合并

**创建日期**：2026-07-28
**PR/分支**：`feature/0728/enterprice` 合入 `feature/0720/enterprice`
**审查范围**：`NMChatNetworkHandler` 冲突及 develop 新增 runtime/history/checkpoint/workflow 链路的多网关影响

---

## 一、Findings

### 阻塞 1：Runtime 创建链路丢失页面注入的项目 Gateway

- **位置**
  - `NAMIWork/Features/ClawChat/NMChatViewController.swift:747`
  - `NAMIWork/Features/ClawChat/Network/NMChatRuntimeRegistry.swift:22`
  - `NAMIWork/Features/ClawChat/Network/NMChatRuntimeRegistry.swift:61`
- **证据**
  - `NMChatViewController.init(config:gateway:)` 收到了项目 `gateway`，但调用 `acquire(config:)` 时没有传入。
  - `NMChatRuntime` 随后通过 `NMChatNetworkHandler(viewModel:agentId:)` 使用默认参数，实际绑定到 `NMPersonalChatGatewayAccess.shared`。
  - Runtime 索引的 Gateway 身份也来自 `GatewayService.shared.cacheStableID`，不是页面注入的连接池 Access。
- **影响**
  - 企业协作项目的历史、发送、事件监听、checkpoint 和 swarm runtime 可能全部误走个人 Gateway。
  - `NMChatNetworkHandler` 本身即便把冲突合对，也会被上游组合根覆盖为错误依赖。
- **建议**
  - `NMChatRuntimeRegistry.acquire`、`NMChatRuntime.init` 显式接收 `NMChatGatewayAccess`。
  - 用注入 Access 的稳定身份构建 runtime key，并用同一个 Access 创建 `NMChatNetworkHandler`、绑定 `NMSwarmNetworkCoordinator.gateway`。
  - 缓存命中时同时校验 Gateway 身份，禁止同 sessionId 跨 Gateway 复用 runtime。

### 阻塞 2：自动合并保留全局个人 Gateway 通知，会误清理池化项目会话

- **位置**：`NAMIWork/Features/ClawChat/Network/NMChatNetworkHandler.swift:274`
- **证据**
  - 自动合并后的 Handler 已注入 `gateway`，但仍订阅 `GatewayService.activeGatewayDidChange` 和 `GatewayService.activeGatewayConnectionDidChange`。
  - 冲突中的 ours `activeGatewayDidChange()` 会 teardown 当前会话、清消息并重新 bootstrap。
- **影响**
  - 用户切换个人龙虾或个人连接状态变化时，所有仍存活的项目 Handler 都可能收到同一个全局通知并被错误重置。
- **建议**
  - 删除 Handler 对两个 `GatewayService` 全局通知的直接订阅。
  - 连接状态只采用 enterprise 的 `gateway.eventDispatcher` 按 `gatewayKey + handlerId` 精准回调。
  - Gateway 身份切换需要由 `NMChatGatewayAccess` 增加独立的身份变化信号，或在状态回调中比较该 Access 的 `manager.stableID`；不能重新回退到全局通知。

### 阻塞 3：冲突区不能整段选 ours 或 theirs

- **位置**：`NAMIWork/Features/ClawChat/Network/NMChatNetworkHandler.swift:571`
- **正确合并语义**
  - 保留 theirs 的入口：`handleGatewayConnectionStateChanged(_ state:)`。
  - 合入 ours 的连接世代失效逻辑：`advanceHistoryConnectionEpoch()`、`historyLoader.invalidateHistorySourceForGatewayChange()`、`workflowCoordinator.connectionEpochDidChange()`。
  - 不保留 ours 直接读取 `GatewayService.shared.activeConnectionState` 的实现。
  - ours 的 `liveCheckpointController`、runtime identity、workflow identity 清理逻辑只在“当前注入 Access 的稳定身份确实变化”时执行，不能由任意个人 Gateway 通知触发。
- **原因**
  - theirs 解决多 Gateway 状态路由；ours 解决旧异步响应、checkpoint 和 workflow 恢复跨连接世代污染。两边语义都需要。

### 高 1：HistoryLoader 新增的身份围栏仍以个人 active Gateway 为真相源

- **位置**
  - `NAMIWork/Features/ClawChat/Network/SubHandlers/NMChatHistoryLoader.swift:200`
  - `NAMIWork/Features/ClawChat/Network/SubHandlers/NMChatHistoryLoader.swift:925`
  - `NAMIWork/Features/ClawChat/Network/SubHandlers/NMChatHistoryLoader.swift:1333`
- **证据**
  - 历史 source 校验、向上翻页、异步响应提交围栏仍读取 `GatewayService.shared.activeNode/cacheStableID`。
- **影响**
  - 项目 Gateway 的正常响应可能被当成旧响应丢弃；翻页可能直接请求个人 RPC；checkpoint/history scope 可能记到错误 Gateway。
- **建议**
  - 所有请求源、响应围栏、paging scope、cache scope 统一来自 `handler.gateway.manager/rpc` 及其稳定身份。
  - 缓存允许离线预载时，也必须按 runtime 注入 Gateway 身份查找，禁止用全局个人 cacheStableID 兜底。

### 高 2：Checkpoint 与 Runtime Registry 的 Gateway scope 仍是全局个人身份

- **位置**
  - `NAMIWork/Features/ClawChat/Network/Cache/NMChatLiveCheckpointController.swift:886`
  - `NAMIWork/Features/ClawChat/Network/NMChatRuntimeRegistry.swift:189`
  - `NAMIWork/Features/ClawChat/Swarm/NMSwarmLiveCheckpointController.swift:876`
- **影响**
  - 不同 Gateway 下相同 sessionId 可能复用或覆盖彼此 runtime/checkpoint；恢复时可能把项目 A 的流式快照挂到个人或项目 B。
- **建议**
  - 抽出统一的 `NMChatGatewayIdentity`（建议至少包含 `gatewayKey + stableID`），供 Handler、History、Runtime、主会话 checkpoint、Swarm checkpoint 共用。

### 高 3：Swarm Coordinator 默认个人 Gateway，runtime 创建后未绑定页面 Gateway

- **位置**
  - `NAMIWork/Features/ClawChat/Network/NMChatRuntimeRegistry.swift:32`
  - `NAMIWork/Features/ClawChat/Swarm/NMSwarmNetworkCoordinator.swift:38`
- **影响**
  - 主会话即使走项目 Gateway，Worker 历史和 checkpoint 仍可能走个人 Gateway。
- **建议**
  - Runtime 创建时立即注入同一个 Gateway Access；不要依赖 Swarm Tab 打开后再临时绑定。

### 中：Workflow 当前明确禁用 project session，可暂不扩展项目 Gateway，但边界应显式

- **位置**
  - `NAMIWork/Features/ClawChat/Workflow/NMWorkflowSessionCoordinator.swift:373`
  - `NAMIWork/Features/ClawChat/Workflow/NMWorkflowSessionCoordinator.swift:1152`
- **证据**
  - Coordinator 的生产 transport 和 capability 仍读取 `GatewayService.shared`。
  - `supportsWorkflow` 明确对 `project:` sessionKey 返回 false。
- **结论**
  - 若产品约束仍是“企业项目会话不支持 Workflow”，本轮不必把 capability registry 改成多 Gateway 字典；但应在 Handler 的能力通知入口先按 session 支持范围短路，并记录该限制。
  - 若未来项目会话也支持 Workflow，则 `NMWorkflowCapabilityRegistry`、环境能力刷新、RPC transport 都必须改为按注入 Gateway 分桶，不能只改 Handler。

### 建议：默认 sessionKey 常量可以保留

- `GatewayService.mainClawSessionKey` 是静态协议常量，不是当前连接实例；它与 `activeRPC/activeNode/activeConnectionState` 不同，不构成本次多 Gateway 泄漏。
- 项目入口仍应保证传入非空的项目 sessionKey，避免错误回退到个人主会话 key。

---

## 二、推荐合并顺序

1. 先修组合根：`NMChatViewController → NMChatRuntimeRegistry → NMChatRuntime → Handler/Swarm` 全链传入同一个 `NMChatGatewayAccess`。
2. 再解决 `NMChatNetworkHandler` 冲突：以 enterprise 的按 Gateway 状态回调为骨架，合入 develop 的 connection epoch、checkpoint、workflow 失效语义。
3. 统一 History/Checkpoint/Runtime 的 Gateway identity 来源，清除项目链路中的 `GatewayService.shared.active*`。
4. 解决 `NMChatHistoryLoader`、`NMSwarmHistoryLoader`、`NMSwarmNetworkCoordinator` 三个伴随冲突。
5. 补多 Gateway 隔离测试后再进行编译与回归验证。

---

## 三、最小测试矩阵

- 同时保活个人 Gateway A 与项目 Gateway B；项目 B 收发和事件只命中 B。
- 个人 A 断开、重连或切换时，项目 B 页面不 teardown、不清屏、不重绑 runtime。
- 项目 B 重连时，B 的 history connection epoch 递增，A 不受影响。
- 相同 sessionId 分别存在于 A/B 时，runtime、history cache、主/Swarm checkpoint 不串桶。
- 项目 B 向上翻页、终态 reload、Swarm Worker reload 都只调用 B 的 RPC。
- 页面销毁后流式 runtime 继续持有原 Gateway B，再次进入可命中同一个 B runtime。
- project session 不触发 Workflow RPC；个人 session 的 Workflow 恢复保持现有行为。

---

## 四、结论

- [ ] 通过
- [x] 修改后通过
- [ ] 需讨论

当前不能通过简单的 `ours/theirs` 选择完成合并。`NMChatNetworkHandler` 的 enterprise 抽象方向正确，但 develop 新增的 Runtime、History identity、Checkpoint 与 Workflow 生命周期需要逐项判断并适配；其中 Runtime Gateway 注入断链、全局通知误触发、History 全局身份引用为阻塞项。

---

## 五、关联材料

- 项目协作入口：`NNamiWork/CLAUDE.md`
- Gateway 架构：`NNamiWork/docs/claude/gateway.md`
- Chat 数据链路：`NNamiWork/docs/claude/chat-data-to-ui-pipeline.md`

## 六、合并后复核（2026-07-28）

- 原 16 个未决冲突已全部逐块解决，`git diff --name-only --diff-filter=U` 为空。
- Chat 组合根已保持 `NMChatGatewayAccess` 显式注入；`pushChatResolved` 补齐漏传的 `gateway` 参数，离线历史缓存检查改按注入 Access 的 `stableID` 分桶。
- 项目详情模型拉取 Agent 模型时改用注入 Gateway 的 `connectionState/rpc`，不再回读个人 active Gateway。
- 企业知识缓存改用 `tenantID + idaasUID` 的独立 scope；个人项目仍沿用个人 Gateway stableID，避免共享项目数据写入个人缓存桶。
- `NMChatNetworkHandler`、History、Runtime、主/Swarm checkpoint 与 Swarm coordinator 的多 Gateway 静态复核未发现个人 active Gateway 回退。
- 工程文件通过 `plutil -lint`，全部本次暂存 Swift 文件通过 `swiftc -parse`，JSON 唯一键和新增三语文案校验通过，`git diff --cached --check` 通过。
- 遵仓库约定未执行 `xcodebuild`、XCTest 或真机回归，因此结论是“静态合并修改后通过”，不等同于编译或运行验证通过。

---

## 反馈（skill_run）

```yaml
skill_run:
  skill: change-impact-analysis
  plan: Plans/代码重构/2026-07-28-NMChatNetworkHandler多网关合并审查.md
  date: 2026-07-28
  contexts_used:
    - path: Contexts/决策/Skill反馈协议.md
      utility: high
      reason: "用于收口跨 Handler、History、Runtime、Checkpoint 与 Swarm 的影响范围"
  contexts_missing:
    - "多 Gateway 变更影响扫描清单"
  contexts_stale: []
  outcome_status: pass
  revisit_needed: true
  revisit_reason: "需在实际冲突解决后复核全局 Gateway 引用是否清零"
```

```yaml
skill_run:
  skill: code-review
  plan: Plans/代码重构/2026-07-28-NMChatNetworkHandler多网关合并审查.md
  date: 2026-07-28
  contexts_used:
    - path: Contexts/决策/Skill原子契约.md
      utility: high
      reason: "按 findings-first、严重级、行号和测试缺口完成审查门禁"
    - path: Contexts/决策/Skill反馈协议.md
      utility: high
      reason: "按无调用方 plan 的审查产物要求记录反馈"
  contexts_missing:
    - "Chat 多 Gateway 依赖注入与缓存分桶长期规范"
  contexts_stale: []
  outcome_status: pass
  revisit_needed: true
  revisit_reason: "阻塞项修复后需要重新审查冲突结果"
```

```yaml
skill_run:
  skill: code-review
  plan: Plans/代码重构/2026-07-28-NMChatNetworkHandler多网关合并审查.md
  date: 2026-07-28
  contexts_used:
    - path: Plans/功能开发/2026-07-27-项目模块重构-子任务04-Chat作用域隔离.md
      utility: high
      reason: "复核 Chat Gateway 显式注入、runtime/history/checkpoint 分桶和项目入口边界"
    - path: Plans/技术方案/2026-07-28-企业项目对话与任务入口Web对齐.md
      utility: high
      reason: "复核 iPhone/iPad 项目入口、会话绑定与知识缓存不得回退个人作用域"
    - path: Contexts/决策/Skill原子契约.md
      utility: high
      reason: "按 findings-first 与证据门禁记录静态复核结论"
    - path: Contexts/决策/Skill反馈协议.md
      utility: high
      reason: "记录本次冲突合并审查的验证证据与未执行项"
  contexts_missing:
    - "可脱离完整 Xcode build 的 Swift 跨文件类型检查脚本"
  contexts_stale: []
  outcome_status: pass
  revisit_needed: true
  revisit_reason: "仍需按项目约定由用户触发编译/XCTest，并进行真机双 Gateway 并存回归"
```
