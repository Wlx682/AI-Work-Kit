---
tags: [工作流, bugfix]
type: plan
category: Bug排查
status: 已完成
date: 2026-08-20
workflow: bugfix
workflow_stage: regression
task_id: bugfix-2026-08-20-agent-Corepack启动嵌套pnpm失败
task_title: agent-Corepack启动嵌套pnpm失败
skill: code-review
---

# 回归与复核：agent-Corepack启动嵌套pnpm失败

**工作流**：`bugfix`
**阶段**：`regression` / 回归与复核
**推荐 Skill**：`code-review`
**存放路径**：`Plans/Bug排查/2026-08-20-回归-agent-Corepack启动嵌套pnpm失败.md`

---

## 一、输入

- 来源：实现提交 `5fc2ed3`、用户原始 Corepack 启动日志、实现落点设计和最终 diff。
- 范围：findings-first 审查脚本语义、无 shim 环境、跨平台测试、组合完整性和全量回归。
- 非目标：不审查或提交并行出现的用户文件 `docs/plans/monitoring-query-and-agentctl-development-plan.md`，不进行真实模型计费调用。

## 二、阶段产出

- [x] 审查发现（中）：首版回归在 Windows 需要创建 Node/Corepack 符号链接，可能被本机权限策略拒绝。已在 `fd2b485` 改为直接调用已安装 Corepack；Unix 仅为 shebang 链接临时 Node，Windows 使用系统 shell 执行 `.cmd`。
- [x] 未发现剩余阻断、高或中等级问题。
- [x] 根 scripts 静态检查：17 个脚本中的 18 次裸 pnpm 调用已归零。
- [x] 真实无 shim 验证：Node 22.19.0、PATH 不含 pnpm，`corepack pnpm@11.7.0 start -- --help` 构建九包、输出 `Answer one task`、退出码 0。
- [x] 评估语义复核：`evaluate:legacy-case` 直接入口运行成功，reference PASS、负对照符合预期、`qualified=true`。
- [x] 组合门禁：最终 fingerprint `11604f9f467b201249ed28d1576302b5bf34ab8817e471f80b4f2bade8bac3db` 验证通过。
- [x] 自动回归：目标 3/3；全量 69 个测试文件、215 条测试通过；全量 TypeScript typecheck 通过；`git diff --check` 通过。
- [x] 提交：`5fc2ed3`（产品修复）与 `fd2b485`（跨平台测试审查修正）。
- [x] 残余风险：当前在 macOS 实机验证；Windows 分支已消除符号链接权限依赖并通过类型检查，但没有 Windows 主机执行证据。


## 三、完成门禁

- `childPlanExists`: True
- `skillRun`: True

> 完成阶段工作后，在本 plan 末尾追加 `skill_run`，再运行 `bash scripts/workflow-gate.sh --workflow bugfix --json`。

## 四、续做

```text
/resume plan=Plans/Bug排查/2026-08-20-回归-agent-Corepack启动嵌套pnpm失败.md 进度=【当前完成情况】
```

## 反馈（skill_run）

```yaml
skill_run:
  skill: code-review
  workflow_stage: regression
  plan: Plans/Bug排查/2026-08-20-回归-agent-Corepack启动嵌套pnpm失败.md
  date: 2026-08-20
  contexts_used:
    - path: /Users/wanglongxiang/git/agent/package.json
      utility: high
      reason: "逐项确认 17 个根脚本不再依赖全局 pnpm shim且保持原入口语义"
    - path: /Users/wanglongxiang/git/agent/tests/integration/dsh-controlled-profile.spec.ts
      utility: high
      reason: "发现并修正 Windows 符号链接权限风险，复核临时目录清理与并发隔离"
    - path: /Users/wanglongxiang/git/agent/profiles/controlled/composition.lock.json
      utility: high
      reason: "确认 package scripts 修复已冻结到生产组合指纹"
    - path: Plans/Bug排查/2026-08-20-agent-Corepack启动嵌套pnpm失败.impl.json
      utility: high
      reason: "逐项对照目标文件、测试位置、依赖边界和已声明风险"
  contexts_missing: []
  contexts_stale: []
  outcome: "中等级跨平台测试问题已在 fd2b485 修正；无剩余阻断项，真实无 shim 启动与 215 条测试均通过"
  utility: high
  reason: "审查补齐了 Windows 测试可执行性，同时确认产品修复、组合完整性与回归证据一致"
  outcome_status: pass
  revisit_needed: false
```
