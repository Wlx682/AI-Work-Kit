---
tags: [工作流, bugfix]
type: plan
category: Bug排查
status: 已完成
date: 2026-08-20
workflow: bugfix
workflow_stage: reproduce
task_id: bugfix-2026-08-20-agent-Corepack启动嵌套pnpm失败
task_title: agent-Corepack启动嵌套pnpm失败
skill: feature-dev-assistant
---

# 复现与影响范围：agent-Corepack启动嵌套pnpm失败

**工作流**：`bugfix`
**阶段**：`reproduce` / 复现与影响范围
**推荐 Skill**：`feature-dev-assistant`
**存放路径**：`Plans/Bug排查/2026-08-20-复现-agent-Corepack启动嵌套pnpm失败.md`

---

## 一、输入

- 来源：用户在 `(base)` shell 执行 `corepack pnpm@11.7.0 start -- "分析当前仓库，运行测试，并告诉我最需要改进的三个地方"`，生命周期脚本报 `sh: pnpm: command not found`。
- 范围：复现无全局 pnpm shim 时，通过 Corepack 直接启动根 package scripts 的失败，并扫描同类脚本。
- 非目标：本阶段不修改代码，不处理 Node 版本或模型凭证问题。

## 二、阶段产出

- [x] Red 命令：`env PATH=/usr/local/bin:/usr/bin:/bin corepack pnpm@11.7.0 start -- "分析当前仓库，运行测试，并告诉我最需要改进的三个地方"`。
- [x] Red 结果：退出码 1，生命周期打印 `$ pnpm build:runtime ...` 后报 `sh: pnpm: command not found`。
- [x] 环境事实：外层 `corepack pnpm@11.7.0 --version` 可正常返回 `11.7.0`，失败只发生在 package script 再次解析裸 `pnpm` 时。
- [x] 影响范围：根 `package.json` 有 17 个脚本、18 次调用依赖裸 `pnpm`；其中 `evaluate:legacy-case` 有两层调用。
- [x] 预期：用户只需 Corepack，不要求全局激活 pnpm；`start/test/composition/release/evaluate` 等脚本都应一致可用。


## 三、完成门禁

- `childPlanExists`: True
- `skillRun`: True

> 完成阶段工作后，在本 plan 末尾追加 `skill_run`，再运行 `bash scripts/workflow-gate.sh --workflow bugfix --json`。

## 四、续做

```text
/resume plan=Plans/Bug排查/2026-08-20-复现-agent-Corepack启动嵌套pnpm失败.md 进度=【当前完成情况】
```

## 反馈（skill_run）

```yaml
skill_run:
  skill: feature-dev-assistant
  workflow_stage: reproduce
  plan: Plans/Bug排查/2026-08-20-复现-agent-Corepack启动嵌套pnpm失败.md
  date: 2026-08-20
  contexts_used:
    - path: /Users/wanglongxiang/git/agent/package.json
      utility: high
      reason: "确认根生命周期脚本共有 17 个脚本、18 次调用依赖 PATH 中的裸 pnpm"
    - path: /Users/wanglongxiang/.codex/attachments/462d57be-7fd3-4791-aae6-2eff94820682/pasted-text.txt
      utility: high
      reason: "给出 Corepack 可执行但嵌套 pnpm 不可解析的真实失败边界"
  contexts_missing: []
  contexts_stale: []
  outcome: "在无全局 pnpm shim 的受控 PATH 下稳定复现用户命令，退出码 1，锁定 17 个同类脚本"
  utility: high
  reason: "Red 精确区分了外层 Corepack 与脚本内裸 pnpm 的解析环境"
  outcome_status: pass
  revisit_needed: false
```
