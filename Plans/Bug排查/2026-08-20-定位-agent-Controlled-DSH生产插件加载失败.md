---
tags: [工作流, bugfix]
type: plan
category: Bug排查
status: 已完成
date: 2026-08-20
workflow: bugfix
workflow_stage: diagnose
task_id: bugfix-2026-08-20-agent-Controlled-DSH生产插件加载失败
task_title: agent-Controlled-DSH生产插件加载失败
skill: feature-dev-assistant
---

# 根因定位：agent-Controlled-DSH生产插件加载失败

**工作流**：`bugfix`
**阶段**：`diagnose` / 根因定位
**推荐 Skill**：`feature-dev-assistant`
**存放路径**：`Plans/Bug排查/2026-08-20-定位-agent-Controlled-DSH生产插件加载失败.md`

---

## 一、输入

- 来源：复现 Plan `Plans/Bug排查/2026-08-20-复现-agent-Controlled-DSH生产插件加载失败.md` 与代码仓 `/Users/wanglongxiang/git/agent`。
- 范围：定位为何 Vitest/typecheck/composition/help 全绿但真实 Controlled DSH 插件树启动失败，并界定正式修复闭包。
- 非目标：不把 `tsx` 注入 DSH 子进程作为生产修复；不修改 DSH 上游包。

## 二、阶段产出

- [x] 根因一：Controlled Profile 中 5 个本地 Cordis 插件的 package `exports` 直接指向 `src/*.ts`，生产加载器没有消费正式 JavaScript 产物。
- [x] 根因二：`NodeDshRunner` 直接 spawn `node_modules/.bin/dsh`；父进程由 `tsx` 启动不等于子进程继承 TypeScript 转译器，子进程实际使用 Node 22 strip-only TypeScript。
- [x] 根因三：源码采用 tsc/bundler 风格 `.js` 相对导入和参数属性；前者在无 emit 时找不到对应 `.ts`，后者需要转换而 Node strip-only 明确不支持。
- [x] 深层影响不仅是报错列出的四个插件：生产闭包还包含 contracts、control-domain、safety-domain、dsh-bridge、runtime-composition；只改首批错误会继续在下游失败。
- [x] 漏测原因：Vitest/tsx 会转译源码；`dsh --help` 不加载插件树；`--dump-config` 只组合配置，不导入插件实现，因此现有 smoke 是假绿。
- [x] 正式修复必须提供可部署 JS 构建产物、让 runtime exports 指向产物、启动前构建或校验产物，并新增真正 boot Cordis 插件树的无模型回归探针。

### 根因链

```text
pnpm start (tsx parent)
  → NodeDshRunner spawn dsh (plain Node child)
  → Cordis 根据 profile 动态 import @agent/plugin-*
  → package exports 命中 src/index.ts
  → Node strip-only 无法解析 projection.js→projection.ts，也无法转换参数属性
  → plugin tree failed before model invocation
```

### 修复闭包

- 基础包：`@agent/contracts`、`@agent/control-domain`、`@agent/safety-domain`、`@agent/dsh-bridge`。
- Cordis 插件：runtime-composition、control-ledger、control-supervisor、authority-gate、safety-client。
- 启动/验证：根 package scripts、构建 tsconfig、composition lock、真实 boot probe、README 使用说明。


## 三、完成门禁

- `childPlanExists`: True
- `skillRun`: True

> 完成阶段工作后，在本 plan 末尾追加 `skill_run`，再运行 `bash scripts/workflow-gate.sh --workflow bugfix --json`。

## 四、续做

```text
/resume plan=Plans/Bug排查/2026-08-20-定位-agent-Controlled-DSH生产插件加载失败.md 进度=【当前完成情况】
```

## 反馈（skill_run）

```yaml
skill_run:
  skill: feature-dev-assistant
  workflow_stage: diagnose
  plan: Plans/Bug排查/2026-08-20-定位-agent-Controlled-DSH生产插件加载失败.md
  date: 2026-08-20
  contexts_used:
    - path: /Users/wanglongxiang/git/agent/packages/dsh-bridge/src/composition.ts
      utility: high
      reason: "证明 DSH 由 plain Node 子进程启动，父进程 tsx 不参与插件加载"
    - path: /Users/wanglongxiang/git/agent/profiles/controlled/package.json
      utility: high
      reason: "确定生产插件闭包及必须加载的五个本地 Cordis 插件"
    - path: /Users/wanglongxiang/git/agent/tsconfig.base.json
      utility: high
      reason: "确认全仓当前 noEmit，仅做类型检查，没有生产 JavaScript 构建产物"
  contexts_missing: []
  contexts_stale: []
  outcome: "根因锁定为生产加载 plain Node 与源码直出契约冲突；修复必须覆盖完整九包运行时闭包和真实 boot 测试"
  utility: high
  reason: "避免只改首个 projection.js 错误后继续暴露参数属性或更深依赖失败"
  outcome_status: pass
  revisit_needed: false
```
