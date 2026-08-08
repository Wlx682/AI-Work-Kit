---
name: template-generator
description: >-
  按模板生成 plan 骨架（侧重格式，非系统设计内容）。
  触发词：生成[XX]模板、套用模板、给我一个[XX]骨架、起个plan模板、/template-generator。
  不响应：系统架构/ER图/模块边界（要内容）→architecture-design-assistant；PRD评审→requirement-analyst；开发功能→feature-dev-assistant。
---

# 模板生成器

约定：`Templates/模板约定.md`

## 触发条件（侧重「格式」）

当用户说以下任一时执行 —— 关键词偏 **要骨架 / 套模板**，与「设计系统内容」区分开：

- 「**生成 [XX] 模板**」「**套用模板**」「**给我一个 [XX] 骨架**」「**起个 plan 模板**」
- `/template-generator` 命令

**不响应（让位给其他 Skill）**：

- 「系统架构设计 / 模块边界 / ER 图」（要内容不要骨架）→ `architecture-design-assistant`
- 「需求分析 / PRD 评审」→ `requirement-analyst`
- 「开发功能 / 实现模块」→ `feature-dev-assistant`

## 任务类型 → 模板

| 类型 | 模板 | 存放 |
|------|------|------|
| 排查 | `Templates/排查问题模板.md` | `Plans/Bug排查/` |
| Epic（client-dev） | `Templates/Epic模板-client-dev.md` | `Plans/Epic/` |
| Epic（learning-loop） | `Templates/Epic模板-learning-loop.md` | `Plans/Epic/` |
| 技术方案 | `Templates/技术方案模板.md` | `Plans/技术方案/` |
| 功能开发 | `Templates/客户端功能开发模板.md` | `Plans/功能开发/` |
| 仅 UI | 同上（含业务逻辑=否） | `Plans/功能开发/` |

续做格式：`/resume plan=Plans/【分类】/xxx.md 进度=...`

`workflow-router` 推荐创建 Epic 时，必须使用蓝图 `startup.createEpicTemplate` 指定的模板生成 `Plans/Epic/xxx.md`，再执行 `bash scripts/workflow-board-boot.sh --epic Plans/Epic/xxx.md`。

同步：`Skills/template_generator.md`

## 反馈回路（skill_run）

完成任务的最后一步按 `Contexts/决策/Skill反馈协议.md` 收口：
本 Skill 只产骨架、一次性输出、通常不落地成型 plan；未归位候选写入孤立反馈 `## 待整理`，已归位结论只写 `## 已归位` 摘要，不保留完整过程小票。
`contexts_used[].utility` 二选一：`high`（附一句话 `reason`）或 `not-needed`；必填 `skill: template-generator` / `plan` / `date` / `contexts_used` / `contexts_missing` / `contexts_stale`。喂 `feedback-aggregate → vault-evolve` 进化链。
