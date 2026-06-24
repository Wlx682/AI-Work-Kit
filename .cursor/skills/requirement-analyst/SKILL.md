---
name: requirement-analyst
description: PRD需求分析。系统性发现逻辑矛盾/交互冲突/需求遗漏/边界不清，输出可push产品的确认清单与可测AC。触发词：分析需求、看PRD、需求评审、push产品、需求遗漏。质量差也必须先走本Skill，再进feature-dev-assistant。
---

# 需求分析助手

Vault：clone 后的 AI-Work-Kit 根目录

必读：`Contexts/需求分析/PRD分析检查清单.md`  
模板：`Templates/需求分析模板.md`（推荐 `需求分析-带验收标准模板.md`）  
Plan：`Plans/需求分析/YYYY-MM-DD-模块名.md`

1. **七步分析** → **五块输出**（逻辑表 + 交互表 + 整体遗漏表 + 边界清单 + 异常流程矩阵） + 用户旅程闭环图 + 可测 AC 表
2. **代码库对照**：搜**当前工作区**代码对照同类功能；工作区是 Vault 时用 `仓库=` 指明
3. **遗漏分析是核心**：回答「完整做上线还缺哪几段 PRD」，每条给 2–3 个补全方案
4. Push 产品时按「**逻辑 · 交互 · 遗漏**」三块归类；P0 遗漏与 P0 矛盾**同等阻塞** `feature-dev-assistant`
5. ⚠️ **反馈回路试点**：存档后必须在 plan 末尾追加 `skill_run` YAML 块（`utility` 二选一：high+reason / not-needed）。协议见 `Contexts/决策/Skill反馈协议.md`；缺则 `plan-gate-check.sh` 报失败

真理源：`Skills/requirement_analyst.md`（含完整 schema 与示例）
