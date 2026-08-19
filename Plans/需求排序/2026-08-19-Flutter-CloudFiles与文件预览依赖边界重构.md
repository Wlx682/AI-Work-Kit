---
tags: [需求排序, Backlog, 敏捷]
type: plan
category: 需求排序
status: 已采纳
date: 2026-08-19
lifecycle_state: prioritization
epic: Plans/Epic/2026-08-19-Flutter-CloudFiles与文件预览依赖边界重构.md
requirement_plan: Plans/需求分析/2026-08-19-Flutter-CloudFiles与文件预览依赖边界重构.md
backlog_index: Plans/需求排序/2026-08-19-Flutter-CloudFiles与文件预览依赖边界重构.backlog.json
relations:
  depends_on:
    - Plans/需求分析/2026-08-19-Flutter-CloudFiles与文件预览依赖边界重构.md
    - Templates/模板约定.md
  dependents:
    - Templates/Epic模板-client-dev.md
  supersedes: []
  superseded_by: []
  conflicts: []
---

# 需求排序：Flutter CloudFiles 与文件预览依赖边界重构

## 排序原则

- 先验证最可能造成行为回退的风险，再调整依赖边界。
- 先消除 composition 对聚合根的反向依赖，再拆 Runtime，避免把循环搬到新类型。
- 先建立 App/Feature 能力边界，再迁移页面和文件预览；最后关闭剩余生产消费者。
- 价值、紧迫度、风险验证价值和依赖分别记录；本阶段不估故事点、工时或个人产能。
- 本 Epic 的 P0 表示“完成本轮无行为变更重构所必需”，不是产品事故等级。

## 需求排序

| 需求 ID | 标题 | 业务价值 | 紧迫度 | 依赖 | 初始优先级 | 排序依据 | 已确认 |
|---|---|---|---|---|---|---|---|
| CFR-001 | 锁定依赖边界与行为不变量 | high | high | 已采纳需求与现有生产链 | P0 | 先让 Feature→App、composition→root、owner fencing、生命周期和预览行为的回退可被测试捕获 | true |
| CFR-002 | 建立单向 App composition 装配链 | high | high | CFR-001 | P0 | 先切断子装配模块对聚合根的反向依赖，后续 Runtime 拆分才不会复制环 | true |
| CFR-003 | 分离 App 内部运行时与 Feature 能力投影 | high | high | CFR-001、CFR-002 | P0 | 这是阻止 client/auth/platform 继续泄漏给 Feature 的核心能力边界 | true |
| CFR-004 | 由 App host 向 Files 注入窄依赖 | high | high | CFR-003 | P0 | 完成 Files Feature 去 App import，并闭合真实页面生产入口 | true |
| CFR-005 | 通过窄预览端口保持 App 侧平台实现 | high | high | CFR-003、CFR-004 | P0 | 预览跨下载、缓存、平台，必须在不泄漏 Runtime 的同时保持现有行为 | true |
| CFR-006 | 迁移剩余生产消费者并闭合生命周期 | high | medium | CFR-003、CFR-004、CFR-005 | P0 | Main、Projects 等旧消费者与资源释放未闭合时只能算 PARTIAL | true |
| CFR-007 | 固化 Provider 装配规则与回归门禁 | medium | medium | CFR-001 至 CFR-006 | P1 | 澄清“App composition 模块装配、root 只汇聚”，防止后续重新集中到根 | true |

对应 JSON 索引：`Plans/需求排序/2026-08-19-Flutter-CloudFiles与文件预览依赖边界重构.backlog.json`。

## 团队确认

- [x] 用户已明确要求对 CloudFiles 与文件预览 Provider 边界进行重构，并先完成计划和架构设计。
- [x] 已核对依赖顺序：不变量 → 单向装配 → Runtime 分离 → Host/Preview 注入 → 消费者闭合 → 规则固化。
- [x] 本轮 Scope 明确排除产品行为、协议、签名、缓存 namespace、持久化迁移和无关 InputBar 改动。
- [x] 本轮排序已确认，可进入架构设计；尚未授权 Story 开发或源码修改。

## 续做

```text
/resume plan=Plans/需求排序/2026-08-19-Flutter-CloudFiles与文件预览依赖边界重构.md 进度=排序已采纳，进入架构设计
```

## 反馈（skill_run）

```yaml
skill_run:
  skill: backlog-prioritization-assistant
  workflow_stage: prioritization
  plan: Plans/需求排序/2026-08-19-Flutter-CloudFiles与文件预览依赖边界重构.md
  date: 2026-08-19
  contexts_used:
    - path: Plans/需求分析/2026-08-19-Flutter-CloudFiles与文件预览依赖边界重构.md
      utility: high
      reason: 从已采纳且 P0 清零的需求、边界、异常矩阵和 AC 提取本轮完整候选项。
    - path: Contexts/需求分析/需求分析产出标准.md
      utility: high
      reason: 确认排序没有丢失生产入口、失败恢复、owner fencing 与可测验收。
    - path: Contexts/决策/Skill反馈协议.md
      utility: high
      reason: 按统一协议记录排序技能的输入、产出与状态。
  contexts_missing: []
  contexts_stale: []
  outcome_status: pass
  revisit_needed: false
```
