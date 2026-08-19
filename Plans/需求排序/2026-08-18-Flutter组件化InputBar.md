---
tags: [需求排序, Backlog, Flutter, InputBar]
type: plan
category: 需求排序
status: 已采纳
date: 2026-08-18
lifecycle_state: prioritization
epic: Plans/Epic/2026-08-18-Flutter组件化InputBar.md
requirement_plan: Plans/需求分析/2026-08-18-Flutter组件化InputBar.md
backlog_index: Plans/需求排序/2026-08-18-Flutter组件化InputBar.backlog.json
relations:
  depends_on:
    - Plans/需求分析/2026-08-18-Flutter组件化InputBar.md
  dependents:
    - Plans/技术方案/2026-08-18-Flutter组件化InputBar.md
  supersedes: []
  superseded_by: []
  conflicts: []
---

# 需求排序：Flutter 组件化 InputBar

## 排序原则

- 先修正会阻塞所有组件的数据真值，再闭合用户点名的选择/上传链，最后接入能力组件和完整发送。
- 业务价值、紧迫度、风险和依赖分开记录；本阶段不填写故事点或工时。

## 有序 Backlog

| 顺序 | 需求 ID | 标题 | 价值 | 紧迫度 | 依赖 | 优先级 | 排序依据 | 已确认 |
|---:|---|---|---|---|---|---|---|---|
| 1 | REQ-IB-001 | InputBar 中心契约与 5 类生产组件组合 | high | high | — | P0 | 已有底座可复用，但完成定义必须绑定真实生产消费者 | true |
| 2 | REQ-IB-002 | Slate 文档、Flutter 编辑投影与 @专家 | high | high | 001 | P0 | 当前 `TextEditingValue` 是 @ 功能的结构性阻塞，先消除错误真值 | true |
| 3 | REQ-IB-003 | 相机、相册、本地文件与云盘选择 | high | high | 001 | P0 | 用户明确指出缺失；也是上传与预览的唯一真实入口 | true |
| 4 | REQ-IB-004 | MediaPreview 与 owner-bound 文件上传 | high | high | 001、003 | P0 | pending/uploading/success/failed、重试、删除、预览必须形成闭环 | true |
| 5 | REQ-IB-005 | Model、Skill 组件与选择快照 | high | low | 001、外部数据契约 | P1 | 不由 InputBar 抢先定义 Agent/Skill 公共模型；对应模块契约稳定后再做投影和生产接线 | true |
| 6 | REQ-IB-006 | 完整输入快照进入 Chat durable 发送 | high | high | 002..005 | P0 | 只有 prompt、成功附件与 options 一起进入同一 delivery 才算生产闭环 | true |

## 团队确认

- [x] 用户明确否定“基础文本即完成”，点名 Slate/@、缺失组件、文件/照片选择和上传。
- [x] 用户最终明确移除 `NMNewTextAndVoiceComponent`、Voice 与 AIGC；组件范围为 Slate Text、FileInput、MediaPreview、Model、Skill。
- [x] 用户明确 AgentSummary/Skill 等跨业务数据结构后置；文件选择、上传、媒体预览属于 InputBar，优先继续。
- [x] 六项均进入当前 Epic Scope；实现可分 Story，但不能再把具体组件延期为未排期 Backlog。

## 反馈（skill_run）

```yaml
skill_run:
  skill: backlog-prioritization-assistant
  workflow_stage: prioritization
  plan: Plans/需求排序/2026-08-18-Flutter组件化InputBar.md
  date: 2026-08-19
  contexts_used:
    - path: Plans/需求分析/2026-08-18-Flutter组件化InputBar.md
      utility: high
      reason: "提取全部 P0 AC，并把用户点名的选择和上传排在装饰性工作之前"
    - path: Plans/Epic/2026-08-18-Flutter组件化InputBar.md
      utility: high
      reason: "沿变更影响确认旧 US-IB-001 只是底座，7 项生产能力均需纳入本 Epic"
  contexts_missing: []
  contexts_stale: []
  outcome_status: pass
  revisit_needed: false
```

## 续做

```text
/resume plan=Plans/需求排序/2026-08-18-Flutter组件化InputBar.md 进度=进入 architecture
```
