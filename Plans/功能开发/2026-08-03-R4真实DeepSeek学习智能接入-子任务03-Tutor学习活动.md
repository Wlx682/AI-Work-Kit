---
tags: [功能开发, R4, DeepSeek, 子任务]
type: plan
category: 功能开发
status: 已完成
date: 2026-08-03
lifecycle_state: development
epic: Plans/Epic/2026-07-08-智能体开发.md
parent: Plans/功能开发/2026-08-03-R4真实DeepSeek学习智能接入.md
含业务逻辑: 是
relations:
  depends_on:
    - Plans/功能开发/2026-08-03-R4真实DeepSeek学习智能接入-子任务01-学习智能端口.md
  dependents: []
  supersedes: []
  superseded_by: []
  conflicts: []
---

# 子任务 03：Tutor 学习活动

## 一、需求分析（开工门禁）

- 需求：`Plans/需求分析/2026-08-03-R4真实DeepSeek学习智能接入.md`
- 技术方案：`Plans/技术方案/2026-08-03-R4真实DeepSeek学习智能接入.md`
- P0=0；覆盖 AC-S7-3。

## 二、原子目标

启动 session 时调用真实 Tutor，为当前动态节点返回独立 `LearningActivity(content, insight, question, rubric)`；不改变 LearningSession 持久化生命周期。

## 三、输入、输出与验收

| 输入 | 输出 | 覆盖 AC |
|------|------|---------|
| 子任务01、session API | activity DTO、HTTP schema、Tutor trace 与测试 | AC-S7-3 |

- [x] activity 全字段来自 DeepSeek 且与 node 绑定。
- [x] 模型失败不返回本地固定题目、不创建 session。
- [x] LearningActivity 按 session 独立持久化，不破坏既有 session contract。
- [x] Agent 全量 137 tests 通过。

## 续做

`/resume plan=Plans/功能开发/2026-08-03-R4真实DeepSeek学习智能接入-子任务04-真实评估与提案.md 进度=子任务03完成；真实activity与session持久化通过137个Agent tests`

## 反馈（skill_run）

```yaml
skill_run:
  skill: feature-dev-assistant
  plan: Plans/功能开发/2026-08-03-R4真实DeepSeek学习智能接入-子任务03-Tutor学习活动.md
  date: 2026-08-03
  contexts_used:
    - path: Plans/技术方案/2026-08-03-R4真实DeepSeek学习智能接入.md
      utility: high
      reason: "以独立 activity DTO 保持业务 session 与生成内容职责分离，并持久化同题评估上下文。"
  contexts_missing: []
  contexts_stale: []
  outcome_status: pass
  revisit_needed: false
```
