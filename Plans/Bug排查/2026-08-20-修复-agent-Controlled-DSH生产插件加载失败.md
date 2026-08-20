---
tags: [工作流, bugfix]
type: plan
category: Bug排查
status: 已完成
date: 2026-08-20
workflow: bugfix
workflow_stage: fix
task_id: bugfix-2026-08-20-agent-Controlled-DSH生产插件加载失败
task_title: agent-Controlled-DSH生产插件加载失败
skill: feature-dev-assistant
---

# 修复实现：agent-Controlled-DSH生产插件加载失败

**工作流**：`bugfix`
**阶段**：`fix` / 修复实现
**推荐 Skill**：`feature-dev-assistant`
**存放路径**：`Plans/Bug排查/2026-08-20-修复-agent-Controlled-DSH生产插件加载失败.md`

---

## 一、输入

- 来源：已确认实现落点 `Plans/Bug排查/2026-08-20-agent-Controlled-DSH生产插件加载失败.impl.json`。
- 范围：九包生产构建、conditional exports、dist 组合指纹、plain Node Cordis 探针、release gate、运行态忽略规则和 README。
- 非目标：不注入 `tsx` 到 DSH 子进程；不调用用户真实 DeepSeek Key；不修改 DSH/Cordis 上游。

## 二、阶段产出

- [x] 新增集中 `build:runtime`：九个生产 package 逐包编译到自身 `dist/`，清理范围固定且无 emit error 才放行。
- [x] 九个 package 的 `exports.types` 保持源码类型真源，`exports.default` 切换为生产 JS。
- [x] composition fingerprint 递归纳入九包 dist、构建脚本和 plain Node 探针；新指纹 `08f1f80ca2745ad4313e4b722ba02abbea638d0285b87790b95346bef5125016`。
- [x] plain Node 探针真实挂载五个 Controlled Cordis 服务，退出码 0。
- [x] 用户原始 `pnpm start -- <task>` 路径已越过插件树；无 Key 时到达模型层并返回预期 `MISSING_CREDENTIAL`，不再出现 module/syntax 错误。
- [x] release `sixty_test_parity` 在纯 TS HEAD 改用冻结 baseline 校验，不再错误执行已删除的 Python pytest。
- [x] `.gitignore` 屏蔽 DSH session/settings/identity/credentials，防止真实运行污染或误提交。
- [x] README 补齐 Controlled 环境变量并修正 Learning `run/resume/tui` 用法。
- [x] 提交：`f5e988ebd59dbf8c3bac1d42bf9d1e012872ac53`（`fix(runtime): build controlled plugins for plain node`）。

### TDD 证据

- Red：目标提交 `582306a` 上真实启动退出 1，包含 `ERR_MODULE_NOT_FOUND` 与三组 `ERR_UNSUPPORTED_TYPESCRIPT_SYNTAX`。
- Green：`pnpm build:runtime && node scripts/runtime/probe-controlled-plugins.mjs` 退出 0，五服务 ready。
- Refactor：dist 纳入 composition，所有消费 runtime package 的入口先显式构建，构建产物不提交。
- 全量：69 个测试文件、214 条测试通过；typecheck 通过；baseline 5/5、legacy map 1/1、Oracle `qualified=true`；三套 frozen install 与 audit 0 漏洞；controlled/recovery help 通过。


## 三、完成门禁

- `childPlanExists`: True
- `skillRun`: True

> 完成阶段工作后，在本 plan 末尾追加 `skill_run`，再运行 `bash scripts/workflow-gate.sh --workflow bugfix --json`。

## 四、续做

```text
/resume plan=Plans/Bug排查/2026-08-20-修复-agent-Controlled-DSH生产插件加载失败.md 进度=【当前完成情况】
```

## 反馈（skill_run）

```yaml
skill_run:
  skill: feature-dev-assistant
  workflow_stage: fix
  plan: Plans/Bug排查/2026-08-20-修复-agent-Controlled-DSH生产插件加载失败.md
  date: 2026-08-20
  contexts_used:
    - path: Plans/Bug排查/2026-08-20-agent-Controlled-DSH生产插件加载失败.impl.json
      utility: high
      reason: "约束九包生产闭包、plain Node 探针和 dist 完整性边界"
    - path: /Users/wanglongxiang/git/agent/tests/integration/dsh-controlled-profile.spec.ts
      utility: high
      reason: "将用户真实失败路径固化为不经过 tsx 的自动回归"
    - path: /Users/wanglongxiang/git/agent/profiles/controlled/composition.lock.json
      utility: high
      reason: "冻结源码、构建工具、实际 dist 与 profile 的统一生产指纹"
  contexts_missing: []
  contexts_stale: []
  outcome: "提交 f5e988e 完成生产构建链，真实 Controlled DSH 已从插件树错误推进到正常模型凭证门禁"
  utility: high
  reason: "修复同时覆盖运行时、构建、完整性、release gate、回归和凭证文件卫生"
  outcome_status: pass
  revisit_needed: false
```
