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
- 「**全流程开发**」→ `full-cycle` 引擎（蓝图 manifest）
- 「**开发 / 写代码**」（方案已定）→ `feature-dev-assistant`

必读：`Plans/需求分析/` 关联 plan（真理源）  
模板：`Templates/技术方案模板.md`  
产出：`Plans/技术方案/`

1. 门禁：需求 P0 闭环；缺边界/异常/验收 → 提醒用 `需求分析-带验收标准模板`  
2. **必输出**：模块边界、ER 图+字段、API Schema+错误码  
3. frontmatter 可保留 `lifecycle_state: architecture` 作兼容展示；`status: 已采纳` 后由 `workflow-gate.sh` 派生下一阶段（通常进入 `test-first`）

同步：`Skills/architecture_design_assistant.md`

## 反馈回路（skill_run）

完成任务的最后一步**必须**输出 `skill_run` 反馈（协议：`Contexts/决策/Skill反馈协议.md`）：
追加到本次 技术方案 plan（`Plans/技术方案/`） **末尾**的 `## 反馈（skill_run）` 节（fenced ```yaml`，非裸 frontmatter）。
`contexts_used[].utility` 二选一：`high`（附一句话 `reason`）或 `not-needed`；必填 `skill: architecture-design-assistant` / `plan` / `date` / `contexts_used` / `contexts_missing` / `contexts_stale`。缺则 `plan-gate-check.sh` 报失败。
