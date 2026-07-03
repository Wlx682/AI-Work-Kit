# 实例化需求助手 Skill

用于 `client-dev` 蓝图需求阶段第 2 步：把事件风暴结果转成可测的 Given-When-Then 场景、验收标准和线框/状态位。

## 触发时机

- 用户说「实例化需求」「GWT」「Given-When-Then」「验收标准」
- Epic WBS 指向 2「实例化需求」
- `full-cycle` 门禁推荐 `spec-by-example-assistant`

## 输入

- 事件风暴章节或 plan
- PRD、设计稿/线框、用户补充
- 需求分析规范：`Contexts/需求分析/需求分析规范.md`

## 输出

输出到 `Plans/需求分析/YYYY-MM-DD-模块名.md`。如果已有需求 plan，则追加「实例化需求」与「验收标准」章节。

必须包含：

- 核心规则与反例
- 至少 10 组 Given-When-Then
- 主链路、边界、异常、权限、空态、重复提交等覆盖
- 线框/交互草图位
- 可被 `test-generator` 映射的验收标准

## 执行规则

1. 每条 GWT 必须可观察、可验证。
2. 主链路不足 10 条时，用边界和反例补齐，不凑无意义场景。
3. P0 不确定项进入待确认问题，不得伪装成验收标准。
4. 完成后追加 `skill_run` 反馈块。

## 反馈

`utility` 只能是 `high` 或 `not-needed`。有 plan 时追加到 plan 末尾；协议见 `Contexts/决策/Skill反馈协议.md`。
