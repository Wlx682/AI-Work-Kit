---
name: nfr-assistant
description: 非功能验证。用于 client-dev verify 阶段，检查性能、安全、可访问性、稳定性并形成放行结论。触发词：非功能验证、性能检查、安全检查、可访问性、NFR、WBS 11。
---

# 非功能验证助手

Vault：clone 后的 AI-Work-Kit 根目录  
模板：`Templates/非功能验证模板.md`  
Plan：`Plans/非功能验证/YYYY-MM-DD-模块名.md`

## 执行

1. 读取 Epic、需求验收标准、技术方案、功能开发 plan 和测试结果。
2. 按项目实际列出性能、安全、可访问性、稳定性门槛。
3. 记录验证证据：命令、日志、截图说明或人工核对结论。
4. P0/P1 风险必须给处置与 Owner；未闭环时不得建议进入发布。
5. 产出写入 `Plans/非功能验证/`，必要时回写 Epic 的 WBS 11 状态。
6. 完成后在 plan 末尾追加 `skill_run` YAML 块，协议见 `Contexts/决策/Skill反馈协议.md`。

## 汇报

```text
📌 当前阶段：[verify / 非功能验证] | 产出：Plans/非功能验证/xxx.md | 下一阶段：[review-assistant] | 如需中断：/resume plan=Plans/非功能验证/xxx.md
```

真理源：`Skills/nfr_assistant.md`
