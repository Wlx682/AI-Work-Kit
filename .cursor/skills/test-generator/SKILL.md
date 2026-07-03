---
name: test-generator
description: 读 Epic+功能开发与需求验收标准，生成验收测试先行或回归测试 plan 到 Plans/自动化测试/，并回写 Epic plans.test + 对应 WBS。触发词：写测试、测试计划、验收测试先行、test-generator。
---

# 测试生成助手

模板：`Templates/自动化测试模板.md`  
输入：Epic `plans.development` + `Plans/需求分析/` AC  
产出：`Plans/自动化测试/`；frontmatter 保留 `lifecycle_state: test` 仅作兼容展示，阶段以 `workflow-gate.sh` 派生为准。

## 执行步骤

1. 读 Epic frontmatter `workflow:`、`plans.*` 与 WBS；运行 `workflow-gate.sh --workflow client-dev --epic <epic>` 确认当前是 `test-first` 或需要补测试。
2. 读功能开发主 plan + 需求 plan **验收标准**；在业务仓库定位被测模块。
3. 按模板输出 UT/IT 清单、AC 映射表、CI 命令。
4. Plan → `Plans/自动化测试/YYYY-MM-DD-模块名.md`；frontmatter 含 `epic:`、`lifecycle_state: test`。
5. **回写 Epic**（硬规则）：
   - frontmatter `plans.test: Plans/自动化测试/xxx.md`
   - §一 子 Plan 索引表 test 行
   - 验收测试先行阶段对应 WBS 4；开发回归测试对应 WBS 9（如实际用于后置测试，按 Epic WBS 注明）
6. 通过后 → 回到 `workflow-gate.sh` 获取下一阶段

## 门禁

- 开发 plan 须 `plan-gate-check.sh` 通过
- Epic `plans.test` 为空时本 Skill 负责填充；不通过修改 `lifecycle_state` 推进阶段

## 上下文汇报

```
📌 当前阶段：[test-first / 自动化测试] | 产出：Plans/自动化测试/xxx.md | Epic plans.test 已更新 | 下一阶段：[跑 workflow-gate 派生] | 中断：/resume plan=...
```

同步：`Skills/test_generator.md`

## 反馈回路（skill_run）

完成任务的最后一步**必须**输出 `skill_run` 反馈（协议：`Contexts/决策/Skill反馈协议.md`）：
追加到本次 自动化测试 plan（`Plans/自动化测试/`） **末尾**的 `## 反馈（skill_run）` 节（fenced ```yaml`，非裸 frontmatter）。
`contexts_used[].utility` 二选一：`high`（附一句话 `reason`）或 `not-needed`；必填 `skill: test-generator` / `plan` / `date` / `contexts_used` / `contexts_missing` / `contexts_stale`。缺则 `plan-gate-check.sh` 报失败。
