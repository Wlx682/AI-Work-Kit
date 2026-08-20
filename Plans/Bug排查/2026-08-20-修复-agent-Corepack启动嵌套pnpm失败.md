---
tags: [工作流, bugfix]
type: plan
category: Bug排查
status: 已完成
date: 2026-08-20
workflow: bugfix
workflow_stage: fix
task_id: bugfix-2026-08-20-agent-Corepack启动嵌套pnpm失败
task_title: agent-Corepack启动嵌套pnpm失败
skill: feature-dev-assistant
---

# 修复实现：agent-Corepack启动嵌套pnpm失败

**工作流**：`bugfix`
**阶段**：`fix` / 修复实现
**推荐 Skill**：`feature-dev-assistant`
**存放路径**：`Plans/Bug排查/2026-08-20-修复-agent-Corepack启动嵌套pnpm失败.md`

---

## 一、输入

- 来源：已确认实现落点 `Plans/Bug排查/2026-08-20-agent-Corepack启动嵌套pnpm失败.impl.json`。
- 范围：根 package scripts、无全局 pnpm shim 集成回归、composition lock。
- 非目标：不修改或删除用户/其他任务生成的 `docs/plans/`，不调用真实模型任务。

## 二、阶段产出

- [x] Red：受控 PATH 中 Corepack 可运行，但用户原始 start 在 `pnpm build:runtime` 报 `pnpm: command not found`，退出码 1。
- [x] Green：17 个受影响脚本、18 次裸 pnpm 调用全部清除；构建、测试、启动和发布脚本直接执行项目工具。
- [x] `evaluate:legacy-case` 直接执行唯一源码入口，评估输出 reference PASS、负对照符合预期、`qualified=true`。
- [x] 自动回归：临时 package fixture 通过 Corepack 启动根 start script，PATH 只含 Node/Corepack 与系统目录，没有 pnpm shim；同时静态禁止 scripts 出现裸 pnpm。
- [x] 真实回归：真实仓库在同样无 pnpm PATH 下执行 `corepack pnpm@11.7.0 start -- --help`，构建九包并输出 `Answer one task`，退出码 0。
- [x] 修复测试竞态：自动用例不再在全量 Vitest 并发中清理共享 dist；真实插件挂载继续由原两条测试覆盖。
- [x] 最终 composition fingerprint：`11604f9f467b201249ed28d1576302b5bf34ab8817e471f80b4f2bade8bac3db`。
- [x] 全量：69 个测试文件、215 条测试通过；全量 TypeScript typecheck 通过；`git diff --check` 通过。
- [x] 提交：`5fc2ed3`（`fix(tooling): remove global pnpm shim dependency`）。


## 三、完成门禁

- `childPlanExists`: True
- `skillRun`: True

> 完成阶段工作后，在本 plan 末尾追加 `skill_run`，再运行 `bash scripts/workflow-gate.sh --workflow bugfix --json`。

## 四、续做

```text
/resume plan=Plans/Bug排查/2026-08-20-修复-agent-Corepack启动嵌套pnpm失败.md 进度=【当前完成情况】
```

## 反馈（skill_run）

```yaml
skill_run:
  skill: feature-dev-assistant
  workflow_stage: fix
  plan: Plans/Bug排查/2026-08-20-修复-agent-Corepack启动嵌套pnpm失败.md
  date: 2026-08-20
  contexts_used:
    - path: Plans/Bug排查/2026-08-20-agent-Corepack启动嵌套pnpm失败.impl.json
      utility: high
      reason: "约束修改为根 scripts、现有集成测试与生成的组合锁"
    - path: /Users/wanglongxiang/git/agent/package.json
      utility: high
      reason: "一次清除 17 个脚本内的全部裸 pnpm 依赖"
    - path: /Users/wanglongxiang/git/agent/tests/integration/dsh-controlled-profile.spec.ts
      utility: high
      reason: "固化 Corepack 有效但全局 pnpm shim 缺失的用户环境"
    - path: /Users/wanglongxiang/git/agent/profiles/controlled/composition.lock.json
      utility: high
      reason: "确保启动脚本变化进入生产组合完整性门禁"
  contexts_missing: []
  contexts_stale: []
  outcome: "提交 5fc2ed3 消除全部裸 pnpm 生命周期依赖，真实无 shim 启动退出 0，215 条测试通过"
  utility: high
  reason: "修复覆盖用户入口、全部同类脚本、评估命令、自动回归和生产指纹"
  outcome_status: pass
  revisit_needed: false
```
