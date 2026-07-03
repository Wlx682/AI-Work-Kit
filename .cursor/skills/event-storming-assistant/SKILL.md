---
name: event-storming-assistant
description: 事件风暴工作坊。用于 client-dev 需求阶段第 1 步，先梳理领域事件墙、热点、角色-系统交互，再进入实例化需求。触发词：事件风暴、领域事件、事件墙、业务事件、WBS 1。
---

# 事件风暴助手

Vault：clone 后的 AI-Work-Kit 根目录  
模板：`Templates/事件风暴模板.md`  
Plan：`Plans/需求分析/YYYY-MM-DD-模块名.md`

## 执行

1. 读取 Epic 与已有需求输入；确认 `workflow: client-dev` 时对应 WBS 1。
2. 按 `Templates/事件风暴模板.md` 输出领域事件墙、热点与角色-系统交互。
3. 事件必须用过去式；每个关键事件尽量补触发命令、聚合/对象、上下游。
4. 热点表只保留会影响需求/方案/测试的分歧，标 P0/P1 或待确认。
5. 产出写入 `Plans/需求分析/`；如已有需求 plan，则追加「事件风暴」章节。
6. 完成后在 plan 末尾追加 `skill_run` YAML 块，协议见 `Contexts/决策/Skill反馈协议.md`。

## 汇报

```text
📌 当前阶段：[requirement / 事件风暴] | 产出：Plans/需求分析/xxx.md | 下一阶段：[spec-by-example-assistant] | 如需中断：/resume plan=Plans/需求分析/xxx.md
```

真理源：`Skills/event_storming_assistant.md`
