---
name: architecture-design-assistant
description: >-
  系统架构/模块边界/ER图/数据模型/API Schema（侧重内容设计，非模板骨架）。
  触发词：系统架构设计、模块边界划分、ER图设计、数据模型、接口契约、技术方案（系统级）、/arch、/architecture-design-assistant。
  不响应：生成技术方案模板/套模板→template-generator；全流程→full-cycle；写代码→feature-dev-assistant。
---

# 架构设计助手

Vault：AI-Work-Kit 根目录

## 触发条件（侧重「内容」）

当用户说以下任一时执行 —— 关键词偏 **系统设计内容**，与「生成模板骨架」区分开：

- 「**系统架构设计**」「**模块边界划分**」「**ER 图设计**」「**数据模型**」「**接口契约 / API Schema**」「**技术方案（系统级）**」
- `/architecture-design-assistant` / `/arch` 命令

**不响应（让位给其他 Skill）**：

- 「**生成技术方案模板**」「**套用方案模板**」（只要骨架）→ `template-generator`
- 「**全流程开发**」→ `full-cycle-assistant`
- 「**开发 / 写代码**」（方案已定）→ `feature-dev-assistant`

必读：`Plans/需求分析/` 关联 plan（真理源）  
模板：`Templates/技术方案模板.md`  
产出：`Plans/客户端技术方案/` 或 `Plans/服务端技术方案/`

1. 门禁：需求 P0 闭环；缺边界/异常/验收 → 提醒用 `需求分析-带验收标准模板`  
2. **必输出**：模块边界、ER 图+字段、API Schema+错误码  
3. `lifecycle_state: architecture`；`status: 已采纳` 后 → `task-splitter`

同步：`Skills/architecture_design_assistant.md`
