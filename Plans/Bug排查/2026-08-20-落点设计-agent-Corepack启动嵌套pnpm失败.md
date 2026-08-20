---
tags: [工作流, bugfix]
type: plan
category: Bug排查
status: 已完成
date: 2026-08-20
workflow: bugfix
workflow_stage: implementation-design
task_id: bugfix-2026-08-20-agent-Corepack启动嵌套pnpm失败
task_title: agent-Corepack启动嵌套pnpm失败
skill: implementation-design-assistant
implementation_design: Plans/Bug排查/2026-08-20-agent-Corepack启动嵌套pnpm失败.impl.json
---

# 修复落点设计（代码架构/目录/文件名）：agent-Corepack启动嵌套pnpm失败

**工作流**：`bugfix`
**阶段**：`implementation-design` / 修复落点设计（代码架构/目录/文件名）
**推荐 Skill**：`implementation-design-assistant`
**存放路径**：`Plans/Bug排查/2026-08-20-落点设计-agent-Corepack启动嵌套pnpm失败.md`

---

## 一、输入

- 来源：根因定位 Plan 与 `/Users/wanglongxiang/git/agent` 的 package scripts、评估入口、Controlled 集成测试和组合指纹实现。
- 范围：根脚本执行方式、无 shim 回归、最终 composition lock。
- 非目标：不新增全局安装步骤，不改变 DSH 插件或模型调用行为，不修改上游依赖。

## 二、阶段产出

- [x] 修复落点设计


## 修复落点设计

机器真理源：`Plans/Bug排查/2026-08-20-agent-Corepack启动嵌套pnpm失败.impl.json`。

- `package.json`：将 17 个脚本中的裸 `pnpm` 调用改为直接执行项目工具；构建入口为 `tsx scripts/runtime/build-production-packages.ts`，评估入口为 `tsx evaluation/cases/legacy-agent-definition-v1/src/run.ts`。
- `tests/integration/dsh-controlled-profile.spec.ts`：创建临时可执行目录，仅链接当前 Node 与其 Corepack JS，不链接 pnpm；执行真实 `corepack pnpm@11.7.0 start -- --help` 并断言无 `command not found`。
- 同一测试读取根 scripts，禁止再次出现裸 `pnpm` token。
- `profiles/controlled/composition.lock.json`：由于根 `package.json` 已纳入 `runtime-scripts` 哈希，Green 后重新冻结并验证。

## 三、完成门禁

- `childPlanExists`: True
- `sectionsPresent`: True
- `implementationDesignReady`: True
- `skillRun`: True

> 完成阶段工作后，在本 plan 末尾追加 `skill_run`，再运行 `bash scripts/workflow-gate.sh --workflow bugfix --json`。

## 四、续做

```text
/resume plan=Plans/Bug排查/2026-08-20-落点设计-agent-Corepack启动嵌套pnpm失败.md 进度=【当前完成情况】
```

## 反馈（skill_run）

```yaml
skill_run:
  skill: implementation-design-assistant
  workflow_stage: implementation-design
  plan: Plans/Bug排查/2026-08-20-落点设计-agent-Corepack启动嵌套pnpm失败.md
  date: 2026-08-20
  contexts_used:
    - path: Plans/Bug排查/2026-08-20-定位-agent-Corepack启动嵌套pnpm失败.md
      utility: high
      reason: "以 Corepack 与生命周期 PATH 的明确边界约束实现"
    - path: /Users/wanglongxiang/git/agent/package.json
      utility: high
      reason: "限定修复为根 scripts 中 17 个脚本里的 18 次裸 pnpm 调用"
    - path: /Users/wanglongxiang/git/agent/tests/integration/dsh-controlled-profile.spec.ts
      utility: high
      reason: "把用户命令放在现有真实 Controlled 启动集成边界回归"
    - path: /Users/wanglongxiang/git/agent/packages/dsh-bridge/src/composition.ts
      utility: high
      reason: "确认 package.json 修改会被既有 composition 完整性机制覆盖"
  contexts_missing: []
  contexts_stale: []
  outcome: "确定仅修改 package.json、现有集成测试和生成的 composition lock，不新增运行时抽象"
  utility: high
  reason: "落点同时覆盖真实失败、同类入口和生产组合完整性"
  outcome_status: pass
  revisit_needed: false
```
