---
tags: [功能开发, R4, Flutter, DeepSeek, 子任务]
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
    - Plans/功能开发/2026-08-03-R4真实DeepSeek学习智能接入-子任务02-动态图谱与推荐.md
    - Plans/功能开发/2026-08-03-R4真实DeepSeek学习智能接入-子任务03-Tutor学习活动.md
    - Plans/功能开发/2026-08-03-R4真实DeepSeek学习智能接入-子任务04-真实评估与提案.md
  dependents: []
  supersedes: []
  superseded_by: []
  conflicts: []
---

# 子任务 05：Flutter 动态工作台

## 一、需求分析（开工门禁）

- 需求：`Plans/需求分析/2026-08-03-R4真实DeepSeek学习智能接入.md`
- 技术方案：`Plans/技术方案/2026-08-03-R4真实DeepSeek学习智能接入.md`
- P0=0；覆盖 AC-S7-3、AC-S7-6。

## 二、原子目标

Flutter 消费真实 activity/evaluation/graph DTO，使用通用拓扑布局展示任意节点集合；删除固定 goal、题目、Tutor 文案、slug 坐标、Vincent/等级/连续天数。

## 三、输入、输出与验收

| 输入 | 输出 | 覆盖 AC |
|------|------|---------|
| 子任务02–04 API、现有五视图 | 动态 models/controller/views/layout、错误态、widget tests | AC-S7-3, AC-S7-6 |

- [x] 动态拓扑网格按 node id 布局，10 个测试节点位置唯一，无 slug 坐标表。
- [x] Practice/Graph 只展示 API activity；空 goal 输入无预填主题。
- [x] 删除 Vincent、Explorer/Lv.8、12 days 等无后端来源展示。
- [x] Review 展示 DeepSeek reason/gaps；Flutter analyze、13 tests（live 1 skipped）、Web build 通过。

## 续做

`/resume plan=Plans/功能开发/2026-08-03-R4真实DeepSeek学习智能接入-子任务06-在线闭环验收.md 进度=子任务05完成；Flutter动态activity/布局/去假数据，analyze+13 tests+Web build通过`

## 反馈（skill_run）

```yaml
skill_run:
  skill: feature-dev-assistant
  plan: Plans/功能开发/2026-08-03-R4真实DeepSeek学习智能接入-子任务05-Flutter动态工作台.md
  date: 2026-08-03
  contexts_used:
    - path: Plans/需求分析/2026-08-03-R4真实DeepSeek学习智能接入.md
      utility: high
      reason: "实现动态 activity/eval 展示、拓扑网格和零假用户/固定内容的 Flutter 工作台。"
  contexts_missing: []
  contexts_stale: []
  outcome_status: pass
  revisit_needed: false
```
