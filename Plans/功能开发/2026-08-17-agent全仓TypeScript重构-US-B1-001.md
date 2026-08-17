---
tags: [功能开发, B1, DSH, Cordis]
type: plan
category: 功能开发
status: 已完成
date: 2026-08-17
lifecycle_state: story-development
parent: Plans/功能开发/2026-08-17-agent全仓TypeScript重构.md
requirement_plan: Plans/需求分析/2026-08-17-agent全仓TypeScript重构.md
architecture_plan: Plans/技术方案/2026-08-17-智能体控制系统工程架构-v0.1.md
story_id: US-B1-001
story_points: 8
sprint_scope: false
tdd_evidence: Plans/功能开发/2026-08-17-agent全仓TypeScript重构-US-B1-001.tdd.json
implementation_design: Plans/功能开发/2026-08-17-agent全仓TypeScript重构-US-B1-001.impl.json
---
# US-B1-001：启动固定 DSH 组合并可逆装卸控制插件

需求真理源：`Plans/需求分析/2026-08-17-agent全仓TypeScript重构.md`。已采纳架构：`Plans/技术方案/2026-08-17-智能体控制系统工程架构-v0.1.md`。

## 一、用户故事与验收边界

作为 Runtime 维护者，我想启动精确 rc.6 的 DSH production Profile 并装卸一个 out-of-tree Cordis 控制插件，以便证明唯一生产 Runtime、组合指纹与 Effect 可逆性。

覆盖 `GWT-005—008`、ENG-002/003/004/006。初始化部分失败必须无残留；组合漂移必须阻断。

本 Story 不实现 Action/Approval、Agent Loop、SQLite Ledger、Safety Executor 或 Learning Runtime，也不 fork DSH。

| AC | 本 Story 要证明的事 |
|---|---|
| GWT-005 | DSH npm artifact、Cordis/工具链、Bundle 层、Provider、patch 与最终配置树都能被同一指纹重建 |
| GWT-006 | 任一受控输入漂移时返回 `COMPOSITION_MISMATCH`，且在 DSH 进程启动前停止 |
| GWT-007 | 生产 Cordis 插件装载后提供 Service/Event/Effect，卸载 Fiber 后全部撤销 |
| GWT-008 | 测试专用插件在初始化中途抛错时，Context 无残留且组合不得 Ready |

## 二、官方事实与本地实证

本设计不再把 DSH 当成普通 Agent 库。官方架构的稳定边界是：

- DSH 由 Cordis 插件树组成；Service、typed event 和 reversible effect 通过 Shared Context 协作；
- Profile 的组合顺序是 `package.json#dsh.profile.bundles` → Profile `cordis.patch.yml` → CLI `--patch`；
- Bundle 用 `package.json#dsh.bundle.patch` 分发 patch 层；
- Bundle 层顺序是语义契约，但普通 YAML 行顺序不是插件启动顺序；Fiber 由 service/inject 依赖激活；
- `ctx.effect()`、`ctx.on()` 和 `fiber.dispose()` 提供可逆生命周期；插件初始化失败时 Cordis 负责回收已登记 Effect。

已对 npm 包做了两组非产品探针：

1. 只声明 `@deepseek-ai/dsh@0.1.0-rc.6` 的安装失败，因为上游内部 `^0.1.0-rc.6` 尝试解析尚不完整的 `@deepseek-ai/dsh-app-boot@^0.1.0-rc.7`，返回 `ETARGET`；
2. 在根 `pnpm-workspace.yaml` 中对 `@deepseek-ai/dsh-*` 锁定 `0.1.0-rc.6`、Cordis 锁定 `4.0.1`，并显式审核 `allowBuilds` 后，`pnpm@11.7.0 install`、`dsh --version` 和 `dsh --profile headless --dump-config` 均成功，lock 中无 rc.7。

这不是“已经实现 B1”，只是证明可实施路径与必须的失败关闭门禁。

## 三、实现落点设计

机器真理源：`Plans/功能开发/2026-08-17-agent全仓TypeScript重构-US-B1-001.impl.json`。用户在门禁摘要后回复“继续”，当前 `confirmed=true`，允许进入 Red。

### 3.1 目标结构

```text
agent/
├─ packages/
│  ├─ contracts/src/runtime-composition.ts
│  └─ dsh-bridge/src/{composition,launcher}.ts
├─ plugins/runtime-composition/
├─ bundles/
│  ├─ control-base/
│  └─ control-production/
├─ profiles/controlled/
│  ├─ package.json
│  ├─ cordis.yml
│  ├─ cordis.patch.yml
│  ├─ pnpm-workspace.yaml
│  ├─ pnpm-lock.yaml
│  └─ composition.lock.json
├─ scripts/runtime/{freeze-composition,verify-composition}.ts
└─ tests/{acceptance,fault-injection,plugin-lifecycle,integration}/
```

`profiles/controlled` 按 DSH 官方 Profile 格式保持独立 pnpm workspace；根 workspace 管理 `packages/*`、`plugins/*`、`bundles/*`。Profile 依赖本地 out-of-tree 包，DSH 官方包仍由安装侧提供，不 vendor 源码。

### 3.2 模块边界

```text
controlled Profile
  → ordered DSH/local Bundles
    → runtime-composition Cordis plugin
      → @agent/contracts

controlled launcher → @agent/dsh-bridge → official dsh CLI
```

- `contracts` 只定义持久化契约和 `COMPOSITION_MISMATCH`，不 import DSH/Cordis/文件系统；
- `dsh-bridge` 吸收 DSH rc 版本差异，只负责 Profile 组合、指纹校验和启动委托，不实现 Agent Loop；
- `runtime-composition` 是单职责 out-of-tree Cordis 插件，对后续 Ledger/Watchdog 提供“当前运行时组合身份”；
- Learning Runtime 继续与 production DSH 依赖图隔离。

### 3.3 组合指纹

`composition.lock.json` 至少绑定：

- DSH 官方 repository、npm `0.1.0-rc.6` 与 registry integrity；
- Cordis `4.0.1`、Node `22.19.0`、pnpm `11.7.0`、TypeScript `6.0.3`；
- 根 `pnpm-lock.yaml` 和 Profile `pnpm-lock.yaml` 的 SHA-256；
- `dsh-base → dsh-headless → control-base → control-production` 的 Bundle 层顺序；
- Bundle/Profile patch hash 与显式 Provider 选择；
- 真实 `dsh --profile controlled --dump-config` 的完整输出 hash；
- 对除自身指纹字段外的 canonical manifest 计算的总 SHA-256。

`freeze --write` 是显式更新动作；默认 verify 不会自动重写 lock 来“治愈”漂移。受控 launcher 必须先 verify，后委托官方 CLI，且禁止未纳入指纹的 `--patch`。

### 3.4 依赖与构建治理

在 `pnpm@11.7.0` 下，override 的真理源是根 `pnpm-workspace.yaml`，不写入已不生效的 `package.json#pnpm.overrides`。根级 wildcard override 锁定所有 `@deepseek-ai/dsh-*` 为 rc.6，并将 Cordis 锁定 4.0.1。

`allowBuilds` 只接受已审核包：`esbuild`、`node-pty`、`koffi`、`@deepseek-ai/dsh-subprocess-local`；`@google/genai`、`protobufjs`、`node-addon-require-builtin` 显式禁止。若安装需要全局放开 scripts，本 Story 停止。

## 四、Red 测试顺序

1. `dsh-composition.spec.ts`：当前无 rc.6 安装闭包、controlled Profile 与 composition lock，必须 Red；
2. `composition-drift.spec.ts`：分别篡改 artifact、lock、Bundle 层、Provider、patch 和 dump，期望 `COMPOSITION_MISMATCH` 且 DSH 未被启动；
3. `runtime-composition.spec.ts`：装载真生产插件后观测 Service/Event/Effect，dispose 后全部消失；
4. `partial-failure.spec.ts`：测试专用失败插件注册部分 Effect 后抛错，验证 Fiber 自动回滚；不向生产插件添加伪故障开关；
5. `dsh-controlled-profile.spec.ts`：真实执行 `--dump-config` 与 `headless --help`。`--help` 用于无模型凭证的树启动 smoke，不冒充模型请求成功；
6. `learning-runtime-isolation.spec.ts`：防止 Learning Runtime 通过新 bridge/plugin/Profile 获得生产能力。

## 五、停止条件

出现任一情况，保持 Red/记录 `UPSTREAM_INCOMPATIBLE` 并停止：

- 任一 `@deepseek-ai/dsh-*` 解析为非 rc.6，或 Cordis 非 4.0.1；
- 安装需要放开未审核 install script；
- 真实 CLI 不能稳定生成 final config dump；
- 插件初始化失败后仍有 Service/listener/Effect 残留；
- verify 失败后 launcher 仍可进入 DSH；
- 只有 fork DSH、重写 Agent Loop 或伪造模型成功才能让测试 Green。

## 六、人工门禁

- [x] 确认不 fork DSH，采用 `dsh-bridge + runtime-composition 插件 + 两层 Bundle + controlled Profile`；
- [x] 确认指纹语义：绑定 artifact、双 lock、Bundle 层顺序、Provider、patch 和真实 dump，不伪造 YAML 行启动顺序；
- [x] 确认 6 组 Red 顺序；
- [x] 确认 rc.6 wildcard override 与最小 `allowBuilds` 白名单；仍失败就停止，不强行完成。

## 七、TDD 实现结果

- 代码提交：`738c9cfc0265345c76cca3f91ccca66ffc640031`；分支：`codex/full-ts-restructure`。
- 组合指纹：`cfe884f04031d415cd465fb5a064288cce52fb0df0e37b75d21b8ded31cdd681`。
- Red：6 组目标测试均先因 bridge/plugin/Profile/lock 尚不存在而失败，不是环境伪失败。
- Green：6 组目标套件全部通过；漂移与启动逃逸共覆盖 12 个用例。
- Refactor：把本地 bridge、插件、Bundle、Profile 与运行脚本源码 hash 纳入指纹，避免 workspace link 掩盖代码漂移。
- 全量回归：TypeScript `16 files / 46 tests`、Python 基线 `60/60`、typecheck、双 workspace frozen install 与 composition verify 均通过。
- 集成 smoke：校验后委托官方 DSH `0.1.0-rc.6`，真实 controlled Profile 的 `--dump-config` 和 headless `--help` 均成功。

### AC 验收

- [x] GWT-005：artifact、双 lock、本地源码、Bundle 顺序、Provider、patch 与真实最终配置共同绑定到一个指纹。
- [x] GWT-006：任一受控输入漂移均返回 `COMPOSITION_MISMATCH`，且 DSH runner 未启动；额外 patch/profile 参数被拒绝。
- [x] GWT-007：生产插件的 Service/Event/Effect 在 Fiber dispose 后全部撤销。
- [x] GWT-008：初始化中途失败由 Cordis 自动回滚，无 Service/listener/Effect 残留且不进入 Ready。

机器证据：`Plans/功能开发/2026-08-17-agent全仓TypeScript重构-US-B1-001.tdd.json`。

续做：`/resume plan=Plans/功能开发/2026-08-17-agent全仓TypeScript重构.md 进度=next-story-scope`

## 反馈（skill_run）

```yaml
skill_run:
  skill: implementation-design-assistant
  workflow_stage: implementation-design
  plan: Plans/功能开发/2026-08-17-agent全仓TypeScript重构-US-B1-001.md
  date: 2026-08-17
  contexts_used:
    - path: Plans/需求分析/2026-08-17-agent全仓TypeScript重构.md
      utility: high
      reason: "将 GWT-005—008 的组合漂移、可逆卸载与部分失败转为文件级 Red"
    - path: Plans/技术方案/2026-08-17-智能体控制系统工程架构-v0.1.md
      utility: high
      reason: "维持 DSH 生产、Learning 隔离、dsh-bridge seam 与不 fork 边界"
    - path: /Users/wanglongxiang/git/agent/package.json
      utility: high
      reason: "确认当前 Node/TypeScript 与已采纳基线漂移，并定位 DSH CLI 脚本落点"
    - path: /Users/wanglongxiang/git/agent/pnpm-workspace.yaml
      utility: high
      reason: "确认 pnpm v11 override、workspace 新包和 allowBuilds 都必须在此治理"
    - path: /Users/wanglongxiang/git/agent/pnpm-lock.yaml
      utility: high
      reason: "结合官方 DSH Profile/Bundle 文档，定位实际依赖闭包和未锁定风险"
    - path: /Users/wanglongxiang/git/agent/packages/contracts/src/runtime-role.ts
      utility: high
      reason: "结合官方 Cordis Service/inject/Effect/Fiber 语义，确保组合身份仍属于 production=dsh 稳定契约"
  contexts_missing: []
  contexts_stale: []
  outcome: "用户确认 US-B1-001 实现落点；dsh-bridge/Bundle/Profile、指纹、6 组 Red、wildcard override 与失败停止门禁获准进入开发"
  utility: high
  reason: "实现前就暴露了一个会让组合不可重放的真实上游版本漂移，避免以虚假安装成功推进后续系统"
```

```yaml
skill_run:
  skill: feature-dev-assistant
  workflow_stage: story-development
  plan: Plans/功能开发/2026-08-17-agent全仓TypeScript重构-US-B1-001.md
  date: 2026-08-17
  contexts_used:
    - path: Plans/功能开发/2026-08-17-agent全仓TypeScript重构-US-B1-001.impl.json
      utility: high
      reason: "约束不 fork DSH、受控组合指纹、Cordis 可逆生命周期、6 组 Red 和失败停止条件"
    - path: /Users/wanglongxiang/git/agent/profiles/controlled/composition.lock.json
      utility: high
      reason: "记录真实 DSH artifact、双 lock、本地源码、Bundle/Profile patch 和最终配置指纹"
    - path: /Users/wanglongxiang/git/agent/tests/fault-injection/composition-drift.spec.ts
      utility: high
      reason: "证明组合漂移和启动参数逃逸在进入官方 DSH runner 前失败关闭"
    - path: /Users/wanglongxiang/git/agent/tests/plugin-lifecycle/runtime-composition.spec.ts
      utility: high
      reason: "证明生产 Cordis 插件的 Service/Event/Effect 可逆卸载"
    - path: /Users/wanglongxiang/git/agent/tests/plugin-lifecycle/partial-failure.spec.ts
      utility: high
      reason: "证明插件初始化中途失败后 Cordis 自动清理全部已登记效应"
  contexts_missing: []
  contexts_stale: []
  outcome: "US-B1-001 完成真实 Red→Green→Refactor→smoke，提交 738c9cf；当前 Scope 不自动扩展"
  utility: high
  reason: "把官方 DSH 组合、Cordis 可逆插件和失败关闭指纹做成可运行证据，而不是仅停留在架构概念"
```
