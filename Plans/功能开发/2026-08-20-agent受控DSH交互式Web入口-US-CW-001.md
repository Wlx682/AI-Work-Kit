---
tags: [功能开发, 用户故事, TDD, DSH, Web]
type: plan
category: 功能开发
status: 已完成
date: 2026-08-20
lifecycle_state: story-development
parent: Plans/功能开发/2026-08-20-agent受控DSH交互式Web入口.md
requirement_plan: Plans/需求分析/2026-08-20-agent受控DSH交互式Web入口.md
architecture_plan: Plans/技术方案/2026-08-20-agent受控DSH交互式Web入口.md
story_id: US-CW-001
story_points: 8
sprint_scope: true
implementation_design: Plans/功能开发/2026-08-20-agent受控DSH交互式Web入口-US-CW-001.impl.json
tdd_evidence: Plans/功能开发/2026-08-20-agent受控DSH交互式Web入口-US-CW-001.tdd.json
---
# US-CW-001：一条命令打开控制插件完整的受控 DSH Web

作为本地开发者，我要用 `start:dsh:web` 打开官方 DSH Web，并确定五个生产控制插件与独立组合指纹已经验证，以便在不绕过受控组合的前提下进行多轮交互。

## 验收标准

- AC-01：输出 loopback URL，HTTP 首页可访问。
- AC-02：最终配置同时包含 Web Surface 与五个控制插件。
- AC-04：Web 与 headless 使用各自稳定且不冒充的组合身份。
- AC-06/07/08：启动前拒绝 profile、patch 和 Executor-only secret 覆盖。
- AC-11/12（P1、非本轮自动门禁）：官方 Web 保留凭证错误呈现与会话恢复能力；真实模型多轮对话留给持有凭证的人工冒烟，不读取用户 secret 代测。

## 故事边界

包含：受控 Web profile、独立 lock、可枚举 ProfileSpec、实时前台 runner、启动脚本和基础 HTTP 冒烟。
不含：自研 TUI/Web、改变默认 headless 入口、开放公网监听。

## 架构引用

- ADR-CW-001..006。

## 实现落点设计

- 契约层把 profile 身份收紧为 `controlled | controlled-web`，不接受任意字符串。
- dsh-bridge 用枚举 ProfileSpec 共享采集/校验，但 Web 使用可实时继承 stdio 的前台 runner。
- `profiles/controlled-web` 独立冻结 Web bundle、控制 bundles 与 lock。
- Red 从契约、启动参数和真实 HTTP 首页三层建立。

## 反馈（skill_run）

```yaml
skill_run:
  skill: implementation-design-assistant
  workflow_stage: implementation-design
  plan: Plans/功能开发/2026-08-20-agent受控DSH交互式Web入口-US-CW-001.md
  date: 2026-08-20
  contexts_used:
    - path: Plans/技术方案/2026-08-20-agent受控DSH交互式Web入口.md
      utility: high
      reason: "把双 profile、独立 lock、foreground runner 和 manifest 注入 ADR 映射到现有代码路径"
  contexts_missing: []
  contexts_stale: []
  outcome_status: pass
  friction: "现有 NodeDshRunner 直到子进程退出才返回，Web 必须新增可测试的前台进程边界"
  revisit_needed: false
```

## 依赖

无。

## TDD 结果

- Red：在功能前提交 `fd2b485` 上运行 launcher 契约，因 `controlled-web` spec 与前台 launcher 不存在而失败。
- Green：提交 `d9d596b` 交付独立 profile/lock、实时 URL、HTTP 200 和 SIGTERM 端口释放。
- Refactor：ProfileSpec 共享采集器，headless 与 Web 仅在枚举 spec 和 runner 生命周期上分叉。

## 反馈（skill_run）

```yaml
skill_run:
  skill: feature-dev-assistant
  workflow_stage: story-development
  plan: Plans/功能开发/2026-08-20-agent受控DSH交互式Web入口-US-CW-001.md
  date: 2026-08-20
  contexts_used:
    - path: Plans/功能开发/2026-08-20-agent受控DSH交互式Web入口-US-CW-001.impl.json
      utility: high
      reason: "实现严格遵循 profile 闭集、独立 lock、前台 runner 和真实 HTTP Red 位置"
  contexts_missing: []
  contexts_stale: []
  outcome_status: pass
  friction: "官方 Web 会生成 storages/workspace.json，已将 storages/ 纳入 gitignore"
  revisit_needed: false
```

## 续做

```text
/resume plan=Plans/功能开发/2026-08-20-agent受控DSH交互式Web入口-US-CW-001.md 进度=implementation-design
```
