---
name: implementation-design-assistant
description: 基于需求/Story/bug 根因和现有代码库，写代码前规划文件目录、文件名、模块边界、依赖方向与 Red 测试位置。触发词：实现落点设计、代码落点、文件目录规划、文件名规划、写代码前看架构、/implementation-design。client-dev 中位于 story-split 后、story-development 前；bugfix 中位于 diagnose 后、fix 前。
---

# 代码落点设计

职责：只读需求、Story、bug 根因和现有代码，产出实现落点契约；不写业务实现代码。

## 位置

- `client-dev`：`story-split` → `implementation-design` → `story-development`
- `bugfix`：`diagnose` → `implementation-design` → `fix`

## 执行

1. 读取需求/架构/Story 或 bug 定位 Plan。
2. 搜索现有代码和测试，确认目录、命名、分层和依赖方向。
3. 产出 `implementation_design` JSON，并写回目标 Plan：
   - client-dev：Scope Story 子 Plan frontmatter 写 `implementation_design:`，主 Plan 写 `## 实现落点设计`。
   - bugfix：落点设计 Plan frontmatter 写 `implementation_design:`，正文写 `## 修复落点设计`。
4. 找不到代码证据时写 `codebase_available: false` 或 `blocked_questions`，禁止猜目录/文件名。
5. 运行校验：
   - client-dev：`python3 scripts/validate-client-dev.py implementation-design --plan Plans/功能开发/父Plan.md`
   - bugfix：`python3 scripts/validate-implementation-design.py --plan Plans/Bug排查/xxx.md`
6. 最后一个 `skill_run` 写 `workflow_stage: implementation-design`。

## JSON 必填

- `codebase_available`
- `codebase_read`
- `target_files.modify/create`
- `module_boundary.layer`
- `module_boundary.dependency_rule`
- `tests.red`
- `risks`
- `blocked_questions`
- `confirmed`

同步：`Skills/implementation_design_assistant.md`