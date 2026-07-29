# 代码合并助手

`merge-code-assistant` 服务 `merge-code` 无 Epic 轻量工作流，负责合并前预检、双边代码意图与业务冲突分析、开发者决策收敛、分支合并和结果验证。

## 适用

- “合代码”“合一下代码”“合并代码”
- “合分支”“merge 分支”
- “把这个分支合进去”
- “解决合并冲突”
- `workflow=merge-code`

## 边界

| 场景 | 处理 |
|------|------|
| 只看 diff 或审查 PR | 转 `code-review` |
| 还需要继续实现功能 | 转 `feature-dev-assistant` 或 `client-dev` |
| 工作树有用户改动 | 停止，不自动 stash、丢弃或覆盖 |
| rebase、squash、force push、远程合并或删分支 | 须仓库规则或用户明确授权 |
| 业务语义无法从证据确定 | 形成开发者决策项，未确认不进入合并 |

## 阶段

1. `preflight`：确认仓库、源/目标分支、SHA、merge-base、提交差异、合并策略和分析证据。
2. `intent-analysis`：分别还原两边的代码与业务意图，形成业务冲突矩阵；语义不确定项必须由开发者明确决策。
3. `merge`：按已采纳的冲突策略和开发者决策合入代码，把每个冲突/决策追到影响文件和验证用例。
4. `review`：交给 `code-review` 复核提交图、最终 diff、决策落实、组合场景测试和遗留风险。

## 业务语义硬门禁

- 必须同时分析源分支与目标分支，证据至少来自 diff/提交及调用方、测试、契约或关联需求中的适用项。
- 必须检查业务规则、状态机、数据/API 契约、权限、副作用、幂等并发、迁移、开关与回滚、跨模块组合场景。
- AI 只能自动处理有证据的机械冲突、等价变更或兼容并集。
- 需要选择产品行为、优先级、迁移顺序或风险取舍时，必须记录开发者结论、决策人和确认记录；未决策不得合并。
- 合并执行 plan 必须把所有冲突 ID 与决策 ID 映射到具体文件、落实方式和验证用例。

缺当前阶段 plan 时：

```bash
python3 scripts/workflow-plan-init.py --workflow merge-code --title <合并任务标题>
```

每阶段结束追加 `skill_run`，再运行 `bash scripts/workflow-gate.sh --workflow merge-code --json`。

## 工作流自身测试优先

任何 `merge-code` 蓝图、Skill、模板、门禁或校验器变更，都先运行：

```bash
python3 scripts/test-merge-code-workflow.py
```

这是 P0 专属回归，覆盖快进、重复合并、跨文件、同文件不同区块、权限位、同一行冲突、删除/修改、重命名/修改、重命名/重命名、二进制、同路径新增、文件/目录、脏工作树保护、无文本业务冲突及开发者决策追踪。P0 失败时停止同步或发布；通过后再跑通用 smoke 与多端一致性检查。
