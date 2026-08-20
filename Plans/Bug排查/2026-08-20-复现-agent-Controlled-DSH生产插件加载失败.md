---
tags: [工作流, bugfix]
type: plan
category: Bug排查
status: 已完成
date: 2026-08-20
workflow: bugfix
workflow_stage: reproduce
task_id: bugfix-2026-08-20-agent-Controlled-DSH生产插件加载失败
task_title: agent-Controlled-DSH生产插件加载失败
skill: feature-dev-assistant
---

# 复现与影响范围：agent-Controlled-DSH生产插件加载失败

**工作流**：`bugfix`
**阶段**：`reproduce` / 复现与影响范围
**推荐 Skill**：`feature-dev-assistant`
**存放路径**：`Plans/Bug排查/2026-08-20-复现-agent-Controlled-DSH生产插件加载失败.md`

---

## 一、输入

- 来源：用户执行 `corepack pnpm@11.7.0 start -- "分析当前仓库…"` 后的完整终端日志；原始附件 `/Users/wanglongxiang/.codex/attachments/462d57be-7fd3-4791-aae6-2eff94820682/pasted-text.txt`。
- 范围：复现 Controlled DSH 从启动器进入真实 Cordis 插件树时的加载失败，并确认失败发生在模型调用前。
- 非目标：本阶段不修改业务代码、不通过 `NODE_OPTIONS=--import tsx` 绕过、不验证真实 DeepSeek 请求。

## 二、阶段产出

- [x] Node `22.19.0`、pnpm `11.7.0`、目标提交 `582306a8675cea435ea33e53b8db82086947ff9f` 上稳定复现。
- [x] Red 命令使用临时 ledger/socket 和假 API key，退出码为 `1`；代码工作树保持干净。
- [x] 首个失败为 `plugins/control-ledger/src/index.ts` 导入不存在的 `projection.js`（源码实际为 `.ts`）。
- [x] 并行失败包含 control-supervisor、authority-gate、safety-client 的 `ERR_UNSUPPORTED_TYPESCRIPT_SYNTAX` 参数属性错误。
- [x] 影响范围：真实任务入口不可用；`--help`、Vitest 和 `tsx` smoke 不能覆盖 plain Node/Cordis 动态加载路径。

### Red 证据

- 命令：为 `DEEPSEEK_API_KEY`、ledger、authority socket、run id、safety socket 注入临时值后运行 `nvm exec 22.19.0 corepack pnpm@11.7.0 start -- 'Controlled DSH plugin boot probe'`。
- 时间：2026-08-20。
- 退出码：`1`。
- 日志：`/var/folders/tg/g2t7zz792zd2tt6p0qq0l9jn9xwb8z/T/tmp.3va3KmtQK9/stderr.log`。
- 判定：稳定 Red，且仅发生在真实插件树导入阶段，尚未到模型请求。


## 三、完成门禁

- `childPlanExists`: True
- `skillRun`: True

> 完成阶段工作后，在本 plan 末尾追加 `skill_run`，再运行 `bash scripts/workflow-gate.sh --workflow bugfix --json`。

## 四、续做

```text
/resume plan=Plans/Bug排查/2026-08-20-复现-agent-Controlled-DSH生产插件加载失败.md 进度=【当前完成情况】
```

## 反馈（skill_run）

```yaml
skill_run:
  skill: feature-dev-assistant
  workflow_stage: reproduce
  plan: Plans/Bug排查/2026-08-20-复现-agent-Controlled-DSH生产插件加载失败.md
  date: 2026-08-20
  contexts_used:
    - path: /Users/wanglongxiang/.codex/attachments/462d57be-7fd3-4791-aae6-2eff94820682/pasted-text.txt
      utility: high
      reason: "提供真实用户启动失败的完整 Cordis 聚合错误与四个底层原因"
    - path: /Users/wanglongxiang/git/agent/packages/dsh-bridge/src/composition.ts
      utility: high
      reason: "确认 DSH 子进程由 plain Node 启动且没有 TypeScript 转译钩子"
  contexts_missing: []
  contexts_stale: []
  outcome: "在干净目标提交上稳定复现真实插件树启动失败，确认不是命令或 API Key 问题"
  utility: high
  reason: "把用户现场错误转成可重复 Red，避免继续用 --help 产生假绿"
  outcome_status: pass
  revisit_needed: false
```
