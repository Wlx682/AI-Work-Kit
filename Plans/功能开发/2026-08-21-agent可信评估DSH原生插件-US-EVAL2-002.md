---
tags: [功能开发, 用户故事, TDD, DSH, WebUI]
type: plan
category: 功能开发
status: 已完成
date: 2026-08-21
lifecycle_state: story-development
parent: Plans/功能开发/2026-08-21-agent可信评估DSH原生插件.md
requirement_plan: Plans/需求分析/2026-08-17-agent可信评估资格门禁.md
architecture_plan: Plans/技术方案/2026-08-21-agent可信评估DSH原生插件架构-v0.2.md
story_id: US-EVAL2-002
story_points: 5
sprint_scope: true
implementation_design: Plans/功能开发/2026-08-21-agent可信评估DSH原生插件-US-EVAL2-002.impl.json
tdd_evidence: Plans/功能开发/2026-08-21-agent可信评估DSH原生插件-US-EVAL2-002.tdd.json
---
# US-EVAL2-002：在 DSH Web 设置中查看可信评估与四源证据

作为 DSH Web 使用者，我要在“设置 → 可信评估”看到四态、技术/现实分账和四插件证据，以便诊断而不被绿色状态误导为已扩权。

## 验收标准

- AC-06：Host 提供只读报告投影 Remote。
- AC-07：Browser 插件注册 `settings.section`，含四态与四源证据。
- AC-08：页面无授权按钮、不直连 SQLite/Socket，插件可独立安装与卸载。

## TDD 结果

- Red：Typert 依赖和 UI 插件包均不存在，Remote/UI 测试失败。
- Green：Host 只读 Remote 标记与 `settings.section` 页面测试通过。
- Refactor：补齐官方 Web Profile layer 安装与 dump-config 冒烟。

## 反馈（skill_run）

```yaml
skill_run:
  skill: figma-ui
  workflow_stage: ui-development
  plan: Plans/功能开发/2026-08-21-agent可信评估DSH原生插件-US-EVAL2-002.md
  date: 2026-08-21
  contexts_used:
    - path: Plans/功能开发/2026-08-21-agent可信评估DSH原生插件-US-EVAL2-002.impl.json
      utility: high
      reason: "把 UI 限定为 Remote 只读投影与 DSH settings.section"
  contexts_missing:
    - "无 Figma 稿，沿用 DSH 官方设置页面的 CSS 变量和可访问状态"
  contexts_stale: []
  outcome_status: pass
  friction: "Browser artifact 使用 DSH ModuleLoader 格式，Host 代码仍独立 TypeScript 构建"
  revisit_needed: false
```

## 续做

```text
/resume plan=Plans/功能开发/2026-08-21-agent可信评估DSH原生插件-US-EVAL2-002.md 进度=等待 US-EVAL2-001
```
