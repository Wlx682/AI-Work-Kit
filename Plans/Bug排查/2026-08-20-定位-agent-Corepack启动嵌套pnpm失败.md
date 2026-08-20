---
tags: [工作流, bugfix]
type: plan
category: Bug排查
status: 已完成
date: 2026-08-20
workflow: bugfix
workflow_stage: diagnose
task_id: bugfix-2026-08-20-agent-Corepack启动嵌套pnpm失败
task_title: agent-Corepack启动嵌套pnpm失败
skill: feature-dev-assistant
---

# 根因定位：agent-Corepack启动嵌套pnpm失败

**工作流**：`bugfix`
**阶段**：`diagnose` / 根因定位
**推荐 Skill**：`feature-dev-assistant`
**存放路径**：`Plans/Bug排查/2026-08-20-定位-agent-Corepack启动嵌套pnpm失败.md`

---

## 一、输入

- 来源：已完成的复现 Plan 与根 `package.json` scripts 清单。
- 范围：解释 Corepack 外层成功、生命周期内裸 pnpm 失败的因果链，并界定统一修复策略。
- 非目标：不要求用户执行 `corepack enable` 或全局安装 pnpm，不用环境配置掩盖仓库脚本缺陷。

## 二、阶段产出

- [x] 直接根因：`corepack pnpm@11.7.0 start` 只负责启动这一次 pnpm CLI；它不会承诺在子 shell PATH 中额外提供名为 `pnpm` 的全局 shim。
- [x] 触发点：根 `start` script 再执行 `pnpm build:runtime`，`sh` 独立按 PATH 查找裸命令，因此用户未启用 Corepack shim 时立即失败。
- [x] 系统性问题：17 个 package scripts 复制了同一假设，共有 18 次裸调用；`evaluate:legacy-case` 还嵌套了第二次 pnpm workspace 调用。
- [x] 修复原则：package script 内部直接执行 `tsx/node/vitest/tsc` 等由 pnpm 注入 `node_modules/.bin` 的项目二进制；构建直接调用既有 TypeScript 构建脚本，不再递归调用包管理器。
- [x] `evaluate:legacy-case` 可直接执行其唯一真实入口 `evaluation/cases/legacy-agent-definition-v1/src/run.ts`，无需 `--filter` 再路由一次。
- [x] 防回归：在现有 Controlled DSH 集成测试中创建只含 Node/Corepack、不含 pnpm shim 的临时 PATH，执行真实 `corepack pnpm@11.7.0 start -- --help`；另断言根 scripts 不含裸 pnpm。


## 三、完成门禁

- `childPlanExists`: True
- `skillRun`: True

> 完成阶段工作后，在本 plan 末尾追加 `skill_run`，再运行 `bash scripts/workflow-gate.sh --workflow bugfix --json`。

## 四、续做

```text
/resume plan=Plans/Bug排查/2026-08-20-定位-agent-Corepack启动嵌套pnpm失败.md 进度=【当前完成情况】
```

## 反馈（skill_run）

```yaml
skill_run:
  skill: feature-dev-assistant
  workflow_stage: diagnose
  plan: Plans/Bug排查/2026-08-20-定位-agent-Corepack启动嵌套pnpm失败.md
  date: 2026-08-20
  contexts_used:
    - path: /Users/wanglongxiang/git/agent/package.json
      utility: high
      reason: "定位生命周期子 shell 对裸 pnpm PATH shim 的隐式依赖"
    - path: /Users/wanglongxiang/git/agent/evaluation/cases/legacy-agent-definition-v1/package.json
      utility: high
      reason: "确认 workspace filter 可安全收敛为直接执行唯一 evaluate 入口"
    - path: /Users/wanglongxiang/git/agent/tests/integration/dsh-controlled-profile.spec.ts
      utility: high
      reason: "选定真实 Corepack 无 shim 启动回归的现有集成边界"
  contexts_missing: []
  contexts_stale: []
  outcome: "根因确定为 package scripts 递归调用裸 pnpm，而非 Corepack、插件树或用户环境损坏"
  utility: high
  reason: "修复范围从单一 start 扩展为全部 17 个受影响脚本并设计真实无 shim 回归"
  outcome_status: pass
  revisit_needed: false
```
