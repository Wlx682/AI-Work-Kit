# 事件风暴助手 Skill

用于 `client-dev` 蓝图 `requirement` 阶段的第一个活动：在写验收标准和方案之前，用领域事件墙对齐业务范围、角色、热点与系统边界。

## 触发时机

- 用户说「事件风暴」「领域事件」「事件墙」「业务事件」
- `workflow-gate` 当前阶段为 `requirement`，并推荐 `event-storming-assistant`
- `workflow-gate` 门禁推荐 `event-storming-assistant`

## 输入

- Epic：`Plans/Epic/xxx.md`
- PRD、口头需求、会议记录或已有需求 plan
- 可选：设计草图、业务流程说明

## 输出

输出到 `Plans/需求分析/YYYY-MM-DD-模块名.md`。如果已有需求 plan，则追加「事件风暴」章节。

必须包含：

- 领域事件墙：事件、触发命令、聚合/对象、上下游
- 热点与分歧：问题、类型、决策人、截止时间
- 角色-系统交互：角色、命令、系统行为、结果事件、异常
- 进入实例化需求的输出清单

## 执行规则

1. 事件用过去式命名，避免写成操作按钮或页面名。
2. 先抓主链路，再补边界、异常、补偿和取消链路。
3. 任何会影响方案、测试或 UI 的分歧都进入热点表。
4. 不把任务专属链接或截图沉淀进 Contexts。
5. 完成后追加 `skill_run` 反馈块。

## 反馈

`utility` 只能是 `high` 或 `not-needed`。有 plan 时追加到 plan 末尾；协议见 `Contexts/决策/Skill反馈协议.md`。
