---
tags: [工作流, bugfix]
type: plan
category: Bug排查
status: 已完成
date: 2026-08-20
workflow: bugfix
workflow_stage: implementation-design
task_id: bugfix-2026-08-20-agent-Controlled-DSH生产插件加载失败
task_title: agent-Controlled-DSH生产插件加载失败
skill: implementation-design-assistant
implementation_design: Plans/Bug排查/2026-08-20-agent-Controlled-DSH生产插件加载失败.impl.json
---

# 修复落点设计（代码架构/目录/文件名）：agent-Controlled-DSH生产插件加载失败

**工作流**：`bugfix`
**阶段**：`implementation-design` / 修复落点设计（代码架构/目录/文件名）
**推荐 Skill**：`implementation-design-assistant`
**存放路径**：`Plans/Bug排查/2026-08-20-落点设计-agent-Controlled-DSH生产插件加载失败.md`

---

## 一、输入

- 来源：根因定位 Plan 与 `/Users/wanglongxiang/git/agent` 真实生产闭包。
- 范围：生产 JS 构建、runtime exports、组合完整性、plain Node 插件探针、release gate 和使用文档。
- 非目标：不修改 DSH/Cordis 上游；不把 `tsx` 注入子进程；不在自动测试中调用真实 DeepSeek API。

## 二、阶段产出

- [x] 修复落点设计


## 修复落点设计

机器真理源：`Plans/Bug排查/2026-08-20-agent-Controlled-DSH生产插件加载失败.impl.json`。

- 构建：新增一个集中脚本，以固定九包白名单逐包调用 TypeScript 编译器，清理范围仅限对应 `dist/`。
- 包契约：`exports.types` 保持指向 `src/index.ts`，`exports.default` 指向 `dist/index.js`；开发类型真源与生产运行真源明确分离。
- 完整性：composition artifact 展开并哈希每个 `dist/` 下的生成 JS，任何缺失、陈旧或篡改都会阻断启动。
- Red/Green：修复前真实启动 Red 已固定；Green 使用 `.mjs` plain Node 探针 import 并挂载 runtime-composition → control-ledger → control-supervisor → authority-gate → safety-client。
- 启动：`test`、`start`、`start:dsh`、composition freeze/verify 在消费 runtime package 前显式构建，不依赖 npm 隐式 pre-script。
- 发布：rehearsal 增加 plain Node 探针，防止再次用 `--help` 假绿。
- 文档：补齐本地 ledger/socket/API Key 环境变量，Learning CLI 使用 `run/resume/tui` 子命令。

## 三、完成门禁

- `childPlanExists`: True
- `sectionsPresent`: True
- `implementationDesignReady`: True
- `skillRun`: True

> 完成阶段工作后，在本 plan 末尾追加 `skill_run`，再运行 `bash scripts/workflow-gate.sh --workflow bugfix --json`。

## 四、续做

```text
/resume plan=Plans/Bug排查/2026-08-20-落点设计-agent-Controlled-DSH生产插件加载失败.md 进度=【当前完成情况】
```

## 反馈（skill_run）

```yaml
skill_run:
  skill: implementation-design-assistant
  workflow_stage: implementation-design
  plan: Plans/Bug排查/2026-08-20-落点设计-agent-Controlled-DSH生产插件加载失败.md
  date: 2026-08-20
  contexts_used:
    - path: Plans/Bug排查/2026-08-20-定位-agent-Controlled-DSH生产插件加载失败.md
      utility: high
      reason: "以 plain Node、源码直出和假绿 smoke 三段根因约束修复边界"
    - path: /Users/wanglongxiang/git/agent/packages/dsh-bridge/src/composition.ts
      utility: high
      reason: "把实际加载的 dist 产物纳入既有组合指纹而不另造完整性机制"
    - path: /Users/wanglongxiang/git/agent/tests/integration/dsh-controlled-profile.spec.ts
      utility: high
      reason: "在现有 Controlled Profile 集成测试层补充 plain Node 插件挂载"
  contexts_missing: []
  contexts_stale: []
  outcome: "确认九包集中构建、conditional exports、dist 指纹与 plain Node Cordis 探针的完整修复落点"
  utility: high
  reason: "修复覆盖首错、深层依赖、完整性和漏测机制，而非单点语法改写"
  outcome_status: pass
  revisit_needed: false
```
