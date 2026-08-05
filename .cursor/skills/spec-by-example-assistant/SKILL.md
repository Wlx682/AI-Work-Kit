---
name: spec-by-example-assistant
description: 实例化需求。用于 client-dev requirement 阶段，在事件风暴后输出 ≥10 组 Given-When-Then、反例、线框位与可测验收标准。触发词：实例化需求、GWT、Given-When-Then、验收标准。
---

# 实例化需求助手

Vault：clone 后的 AI-Work-Kit 根目录  
模板：`Templates/实例化需求模板.md`  
Plan：`Plans/需求分析/YYYY-MM-DD-模块名.md`

## 执行

1. 读取事件风暴结果、PRD、设计线索和现有需求 plan。
2. 至少写 10 组 Given-When-Then，覆盖主链路、边界、异常和反例。
3. 每条验收标准必须可测试，并能被后续 `test-generator` 映射。
4. 线框位只记录当前任务材料或草图说明；不要把任务专属链接沉淀到 Contexts。
5. 产出写入 `Plans/需求分析/`；如已有需求 plan，则追加「实例化需求」与「验收标准」章节。
6. 完成后在 plan 末尾追加 `skill_run` YAML 块，协议见 `Contexts/决策/Skill反馈协议.md`。

## 汇报

```text
📌 当前阶段：[requirement / 实例化需求] | 产出：Plans/需求分析/xxx.md | 下一阶段：[requirement-analyst 完成需求评审，然后 backlog-prioritization-assistant] | 如需中断：/resume plan=Plans/需求分析/xxx.md
```

真理源：`Skills/spec_by_example_assistant.md`
