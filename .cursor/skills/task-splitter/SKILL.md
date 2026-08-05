---
name: task-splitter
description: 将已排序需求和已采纳架构拆成可独立演示、验收的纵向用户故事，为每个故事给出故事点并确认本轮 Scope。触发词：Story 拆分、用户故事拆分、拆用户故事、故事点、Scope、task-splitter；不再按 Domain/Data/UI 横向拆成交付任务。
---

# 用户故事拆分与故事点

输入：已采纳需求、已确认 Backlog、已采纳架构。
输出：`Plans/功能开发/YYYY-MM-DD-标题.md`、`.stories.json` 和故事子 Plan。

## 执行

1. 从用户价值拆故事：每个故事必须可独立演示、独立验收，`vertical_slice: true`。
2. UI、Domain、Data/API、异常和测试属于故事内部步骤；共享底座归入首个消费者或显式 enabler。
3. 每个故事填写 AC、架构引用、依赖、优先级、`story_points`、`sprint_scope`。
4. 点数只用 `1/2/3/5/8/13`，由 AI 提议、团队确认；禁止换算小时。
5. 13 点故事进入 Scope 前必须继续拆分，或填写团队确认的 `estimate_waiver`。
6. P0 AC 必须至少由一个 Scope 故事覆盖。
7. 运行 `python3 scripts/validate-client-dev.py story-scope --plan Plans/功能开发/xxx.md`。
8. 最后一个 `skill_run` 增加 `workflow_stage: story-split`。

## 禁止擅自下结论

- 信息不足或故事边界不清时列出待确认项，不替产品确定 Scope。
- Epic/故事结构变更须有用户确认或已批准的重构 Plan。

## 反馈

按 `Contexts/决策/Skill反馈协议.md` 写入主 Plan，额外包含 `workflow_stage: story-split`。
