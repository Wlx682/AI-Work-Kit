---
name: backlog-prioritization-assistant
description: 对已澄清需求按业务价值、紧迫度、风险验证价值和依赖排序，生成团队确认的有序 Backlog。用于 client-dev 的 prioritization 阶段，或用户说需求排序、Backlog 排序、排优先级、确认本轮先做什么；不做技术架构、故事点或 Story 拆分。
---

# Backlog 需求排序

输入：已采纳且 `p0_open: 0` 的 `Plans/需求分析/` Plan。
输出：`Plans/需求排序/YYYY-MM-DD-标题.md` 和同名 `.backlog.json`。

## 执行

1. 从需求 Plan 提取所有本轮候选需求及 AC，不丢 P0。
2. 分别填写 `business_value`、`urgency`、`dependencies`、`priority`、`reason`。
3. 价值与成本分离：本阶段禁止填写故事点、工时或个人产能。
4. AI 可以提出顺序；只有团队确认后才写 `confirmed: true`。
5. 运行 `python3 scripts/validate-client-dev.py backlog --plan Plans/需求排序/xxx.md`。
6. 通过后将 Plan `status` 设为 `已采纳`，最后一个 `skill_run` 写 `workflow_stage: prioritization`。

## 门禁

- 每项需求必须有标题、价值、紧迫度、依赖、优先级、排序依据和确认状态。
- `.backlog.json` 顶层必须 `confirmed: true`。
- 不换算故事点到小时，不做架构和用户故事拆分。

## 反馈

按 `Contexts/决策/Skill反馈协议.md` 写入排序 Plan，额外包含 `workflow_stage: prioritization`。
