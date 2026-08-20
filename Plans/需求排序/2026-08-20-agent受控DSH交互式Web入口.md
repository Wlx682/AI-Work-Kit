---
tags: [需求排序, Backlog, 敏捷]
type: plan
category: 需求排序
status: 已采纳
date: 2026-08-20
lifecycle_state: prioritization
epic: Plans/Epic/2026-08-20-agent受控DSH交互式Web入口.md
requirement_plan: Plans/需求分析/2026-08-20-agent受控DSH交互式Web入口.md
backlog_index: Plans/需求排序/2026-08-20-agent受控DSH交互式Web入口.backlog.json
relations:
  depends_on:
    - Templates/模板约定.md
  dependents:
    - Templates/Epic模板-client-dev.md
  supersedes: []
  superseded_by: []
  conflicts: []

---
# 需求排序：agent受控DSH交互式Web入口

## 排序原则

- 价值、紧迫度、风险验证价值、前置依赖分别记录；故事点不在本阶段填写。
- AI 给建议，团队确认后 `confirmed: true` 才成为门禁事实。

## 需求排序

| 需求 ID | 标题 | 业务价值 | 紧迫度 | 依赖 | 初始优先级 | 排序依据 | 已确认 |
|---------|------|----------|--------|------|------------|----------|--------|
| CW1 | 冻结受控 Web Profile 与独立组合身份 | high | high | — | P0 | 先验证官方 Web 与控制插件的统一生产树，阻止裸 Web 被误当受控入口 | true |
| CW2 | 提供 Verified Controlled Web 启动与本地交互 | high | high | CW1 | P0 | 组合身份成立后才开放 URL、HTTP 与持续会话入口 | true |
| CW3 | 失败关闭、生命周期与双入口回归 | high | high | CW1、CW2 | P0 | 漂移/覆盖/secret/端口/host 反例与 headless 回归必须共同放行 | true |
| CW4 | 使用文档与真实模型人工 Smoke | medium | medium | CW2、CW3 | P1 | 自动化不读取用户 Key；文档明确生产入口，真实对话由本地人工验证 | true |

对应 JSON 索引：`backlog_index`。字段契约由 `scripts/validate-client-dev.py backlog` 校验。

## 团队确认

- [x] 产品意图：用户已确认完善受控交互能力，双入口和不绕门禁属于前述对话已确认边界
- [x] 开发依赖：Profile/组合身份 → Verified 启动 → 失败关闭与回归 → 人工 Smoke
- [x] 本轮排序已确认；P0 为 CW1—CW3，CW4 不阻断自动集成 Done

## 续做

```text
/resume plan=Plans/需求排序/2026-08-20-agent受控DSH交互式Web入口.md 进度=完成团队确认并运行backlog门禁
```

## 反馈（skill_run）

```yaml
skill_run:
  skill: backlog-prioritization-assistant
  workflow_stage: prioritization
  plan: Plans/需求排序/2026-08-20-agent受控DSH交互式Web入口.md
  date: 2026-08-20
  contexts_used:
    - path: Plans/需求分析/2026-08-20-agent受控DSH交互式Web入口.md
      utility: high
      reason: "从 14 条 AC 提取 Profile/组合、启动交互、失败关闭和人工 Smoke 四组需求"
    - path: Plans/Epic/2026-08-17-agent全仓TypeScript重构.md
      utility: high
      reason: "把已完成 headless 与控制闭环作为依赖基线而非本轮重做项"
  contexts_missing: []
  contexts_stale: []
  outcome: "CW1→CW2→CW3→CW4 Backlog 已确认；前三项 P0，真实模型人工 Smoke 为 P1"
  utility: high
  reason: "顺序确保任何可访问 Web 都已经受组合指纹和控制插件约束"
  outcome_status: pass
  revisit_needed: false
```
