---
name: feature-dev-assistant
description: 在已确认架构和 Scope 下实现一个纵向用户故事，并完成 Red→Green→Refactor→故事验收的 TDD 闭环。触发词：开发用户故事、实现这个故事、开始写代码、功能开发、/dev；纯 UI 仍转 figma-ui，全流程入口转 workflow-router。
---

# 逐用户故事 TDD 开发

输入：带 `story_id/story_points/sprint_scope` 的用户故事子 Plan、需求 AC 和架构引用。
输出：故事实现、测试、故事 Plan 与 `tdd_evidence` JSON。

## 执行

1. 确认故事是 Scope 内的纵向用户能力；UI 子任务按 `figma-ui` 规则执行，但仍归属于当前故事。
2. **Red**：先从 AC 写测试并运行，保存命令、非零退出码、时间和“仅因尚未实现”的原因。
3. **Green**：最小实现使同一测试通过，保存命令、零退出码和 commit。
4. **Refactor**：重构后再次运行并保持通过。
5. 合并前运行 `integration_smoke`，避免等到最终阶段才首次集成。
6. 把全部证据写到 Plan 的 `tdd_evidence` JSON；AC 必须逐条 `pass: true`。
7. 运行 `python3 scripts/validate-client-dev.py story-development --plan Plans/功能开发/父Plan.md`。
8. 故事完成后 `status: 已完成`；主 Plan 最后一个 `skill_run` 写 `workflow_stage: story-development`。

## 边界

- checklist、代码存在或 skill_run 不能替代可执行 Red/Green/Refactor 证据。
- 不在单故事阶段宣告全量集成完成。
