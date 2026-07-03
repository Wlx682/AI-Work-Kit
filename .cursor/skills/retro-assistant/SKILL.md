---
name: retro-assistant
description: 团队回顾与流程改进。用于 client-dev retro 阶段，输出事实回顾、根因、至少 1 条行动项，并标记可沉淀结论。触发词：团队回顾、复盘、流程改进、retro、WBS 15。
---

# 团队回顾助手

Vault：clone 后的 AI-Work-Kit 根目录  
模板：`Templates/团队回顾模板.md`  
Plan：`Plans/最佳实践/YYYY-MM-DD-模块名.md`

## 执行

1. 读取 Epic、各阶段 plan、变更日志和发布/监控结果。
2. 只记录事实与证据，不把一次性任务细节直接写入 Contexts。
3. 至少产出 1 条行动项，必须包含 Owner、截止日、验收方式。
4. 若发现可复用结论，只列为「候选 Contexts 更新」，写 Contexts 前须用户确认。
5. 产出写入 `Plans/最佳实践/` 或当前 Epic 附属回顾 plan。
6. 完成后在 plan 末尾追加 `skill_run` YAML 块，协议见 `Contexts/决策/Skill反馈协议.md`。

## 汇报

```text
📌 当前阶段：[retro / 团队回顾] | 产出：Plans/最佳实践/xxx.md | 下一个阶段：[done] | 如需中断：/resume plan=Plans/最佳实践/xxx.md
```

真理源：`Skills/retro_assistant.md`
