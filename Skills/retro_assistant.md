# 团队回顾助手 Skill

用于 `client-dev` 蓝图 retro 阶段：交付后回顾事实、根因和行动项，把可复用改进进入反馈回路。

## 触发时机

- 用户说「团队回顾」「复盘」「流程改进」「retro」
- Epic WBS 指向 15「团队回顾与流程改进」
- `full-cycle` 门禁推荐 `retro-assistant`

## 输入

- Epic 与各阶段子 plan
- 发布检查、监控反馈、变更日志
- 团队口头反馈

## 输出

输出到 `Plans/最佳实践/YYYY-MM-DD-模块名.md` 或当前 Epic 附属回顾 plan。

必须包含：

- 各阶段事实回顾
- 卡点与根因
- 至少 1 条行动项，含 Owner、截止日、验收方式
- 可沉淀结论候选

## 执行规则

1. 区分事实、解释和行动项。
2. 写 Contexts 前必须用户确认；只在回顾 plan 里列候选。
3. 行动项没有 Owner 和截止日则不算完成。
4. 完成后追加 `skill_run` 反馈块。

## 反馈

`utility` 只能是 `high` 或 `not-needed`。有 plan 时追加到 plan 末尾；协议见 `Contexts/决策/Skill反馈协议.md`。
