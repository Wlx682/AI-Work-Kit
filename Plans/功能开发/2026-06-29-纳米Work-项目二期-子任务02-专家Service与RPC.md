---
tags: [功能开发, 子任务, 纳米Work项目二期]
type: plan
category: 功能开发
status: 草稿
date: 2026-06-29
epic: Plans/Epic/2026-06-29-纳米Work-项目二期-项目内专家团.md
parent: Plans/功能开发/2026-06-29-纳米Work-项目二期-项目内专家团.md
requirement_plan: Plans/需求分析/2026-06-29-纳米Work-项目二期-项目内专家团.md
architecture_plan: Plans/客户端技术方案/2026-06-29-纳米Work-项目二期-项目内专家团.md
lifecycle_state: development
skill: feature-dev-assistant
wbs: 5
relations:
  depends_on:
    - Plans/功能开发/2026-06-29-纳米Work-项目二期-子任务01-数据模型与云控.md
  dependents: []
  supersedes: []
  superseded_by: []
  conflicts: []
---

# 子任务 02：专家 Service 与 RPC

**WBS**：#5 | **依赖**：子任务01（模型）

## 目标

封装二期专家管理 RPC + Service 方法，UI 层只调 Service（DIP）。延续一期 `NMProjectsServiceProtocol` 的 DI 与错误处理。

1. **RPC 层**（`GatewayRPCClient+Projects.swift`）新增：
   - `projectExpertsList(projectId) -> {experts: [ExpertRow]}`
   - `projectExpertsAdd(projectId, agentIds:[String]) -> 完整列表`（1–20，幂等）
   - `projectExpertsRemove(projectId, agentIds:[String]) -> 完整列表`（移除不存在静默忽略）
   - `projectExpertsUpdate(projectId, agentIds:[String]) -> 完整列表`（全量覆盖，有序）
   - `projectCreate` **加 `expertAgentIds:[String]?`** 参数（≤20，未知静默过滤）
   - 数量上限**不在客户端校验**：超限由后端返回 `INVALID_REQUEST: EXPERT_LIMIT_EXCEEDED`
2. **Service 层**（`NMProjectsService` + `NMProjectsService+Experts.swift`，并 Protocol 加方法）：
   - 暴露上述增删查；错误经 `projectUserFacingMessage` 映射（`unknown agents`/`EXPERT_LIMIT_EXCEEDED`/`INVALID_EXPERT_TOKEN`）
   - **专家来源聚合**：`fetchAvailableExperts()` = 已雇佣（`GatewayAgentStore.installedAgents`/`myClawDisplayAgents`）+ 商店推荐（`NMClawHubRequestHandler.fetchAgentList`），供添加弹窗双 Tab。
3. **错误码处理**：`EXPERT_LIMIT_EXCEEDED` → Toast「专家数量已达上限」；`unknown agents` → Toast「部分专家不可用」。

## 验收

- [ ] 4 个 experts RPC 可调通（联调 mock 或真机）；projectCreate 带 expertAgentIds 成功
- [ ] 客户端不前置数量校验；超限错误正确映射 Toast
- [ ] Service 方法走 Protocol，可 mock 单测（对齐一期 Projects DI 风格）
- [ ] 编译通过

## 参考

- 契约：project.experts.list/add/remove/update、projects.create 扩展（技术方案 §API）
- 一期：`GatewayRPCClient+Projects.swift`、`NMProjectsService.swift`（DI/错误处理范式）

## 续做

```
/resume plan=Plans/功能开发/2026-06-29-纳米Work-项目二期-子任务03-创建专家区与图标弹窗.md
```
