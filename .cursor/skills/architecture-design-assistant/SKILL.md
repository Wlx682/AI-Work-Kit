---
name: architecture-design-assistant
description: 业务框架/技术方案设计。读 Plans/需求分析/ 真理源，产出 ER+API Schema+模块边界到 Plans/技术方案/。触发词：架构设计、技术方案、模块划分、architecture-design-assistant。
---

# 架构设计助手

Vault：AI-Work-Kit 根目录

必读：`Plans/需求分析/` 关联 plan（真理源）  
模板：`Templates/技术方案模板.md`  
产出：`Plans/客户端技术方案/` 或 `Plans/服务端技术方案/`

1. 门禁：需求 P0 闭环；缺边界/异常/验收 → 提醒用 `需求分析-带验收标准模板`  
2. **必输出**：模块边界、ER 图+字段、API Schema+错误码  
3. `lifecycle_state: architecture`；`status: 已采纳` 后 → `task-splitter`  
4. 每步结束：📌 当前阶段 / 下一阶段 / `/resume plan=`

同步：`Skills/architecture_design_assistant.md`
