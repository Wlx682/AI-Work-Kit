---
tags: [功能开发, UI, DSH, 控制插件]
type: plan
category: 功能开发
status: 已完成
date: 2026-08-21
lifecycle_state: ui-development
codebase_root: /Users/wanglongxiang/git/agent
requirement_plan: Plans/需求分析/2026-08-17-agent可信评估资格门禁.md
---
# Agent 控制插件 DSH Web 五独立栏目

## 用户确认 Scope

- 在 DSH Web“设置”中先建立五个独立栏目：控制账本、控制监督、权限门禁、安全执行、可信评估。
- 可信评估复用现有页面；另外四栏本轮只做插件内置 WebUI、说明与只读空态。
- 本轮不接 Host Remote、不读数据库、不增加授权或执行操作。

## 实现边界

```text
control-ledger      → Host + settings.section（控制账本）
control-supervisor  → Host + settings.section（控制监督）
authority-gate      → Host + settings.section（权限门禁）
safety-client       → Host + settings.section（安全执行）
evaluation          → Host/Remote + settings.section（可信评估）
```

每个业务插件都是一个独立 DSH Profile layer，并在同一包中声明 `dsh.bundle` 与 `dsh.client`。不创建 `control-suite`，也不再维护重复的 `*-ui` 包。

## 验收

- [x] 五个业务插件均可直接安装到 Web Profile，无额外 UI 包。
- [x] DSH 最终 Web 启动清单只包含五个 `@agent/plugin-*` 业务模块。
- [x] 设置导航真实显示五个独立栏目，四个新栏目具有诚实空态。
- [x] 相关编译、验收测试、集成测试和类型检查通过。
- [x] UI 自检完成。

## 实现结果

- `control-ledger`、`control-supervisor`、`authority-gate`、`safety-client`、`evaluation` 的 `package.json` 同时声明 Cordis Host bundle 与 DSH Web client。
- Web Profile 已从 10 个 Host/UI 包收敛为 5 个业务插件；旧 `*-ui` 目录移入本机废纸篓，可恢复。
- 四个控制栏目保持只读空态；可信评估通过既有 Evaluation Remote 读取报告。所有页面均不提供授权或执行按钮。

## 验证记录

| 验证 | 结果 |
|---|---|
| UI/集成定向测试 | 3 files / 7 tests passed |
| TypeScript | 13 个 tsconfig 通过 |
| 本地 Web Profile | 依赖与 bundle 均只有 5 个 `@agent/plugin-*` 包 |
| 浏览器实测 | 5 个导航按钮、5 个标题、4 个诚实空态及 Evaluation 空报告状态均可见 |
| 浏览器控制台 | error 0 |

浏览器验收截图：`/var/tmp/dsh-five-plugin-sections-20260821.png`。

全仓测试执行期间，代码仓库中并行出现尚未完成的 `evolution` / `evolution-ui` Red 骨架；它们不属于本 Plan，未修改、未删除。本 Plan 的相关测试与集成测试已独立通过。

## UI 自检

- 自检得分：9/10。
- 布局、间距、圆角、颜色和字体均复用 DSH 官方 Settings 容器与 `--dsw-*` 主题变量。
- 五栏选中态、四栏空态和 Evaluation 空报告状态均在真实浏览器中验证。
- 已接受差异：本任务没有 Figma 源稿，无法进行设计稿截图逐像素对比；以官方 DSH Settings 运行页面为视觉基线。

## 反馈（skill_run）

```yaml
skill_run:
  skill: figma-ui
  workflow_stage: ui-development
  plan: Plans/功能开发/2026-08-21-agent控制插件DSH-Web五独立栏目.md
  date: 2026-08-21
  contexts_used:
    - path: /Users/wanglongxiang/git/agent/node_modules/.pnpm/@deepseek-ai+dsh-client-ui-settings-plugin-inventory@0.1.0-rc.6_4ec66e64d9355b7da8c0f395569f1afb/node_modules/@deepseek-ai/dsh-client-ui-settings-plugin-inventory/lib/client.js
      utility: high
      reason: "复用官方 Settings section 注册方式、主题变量和宿主布局"
    - path: /Users/wanglongxiang/git/agent/plugins/evaluation/client.js
      utility: high
      reason: "统一五个插件的栏目顺序、只读边界和 Evaluation Remote 页面"
  contexts_missing:
    - "无 Figma 设计稿；以官方 DSH Settings 实际页面作为视觉基线"
  contexts_stale: []
  outcome: "五个业务插件各自在同一包内提供 Host 与 WebUI，DSH Settings 实测显示五个独立栏目"
  utility: high
  reason: "消除了 Host/UI 双包安装复杂度，并完成真实页面与控制台验收"
  outcome_status: pass
  revisit_needed: false
```
