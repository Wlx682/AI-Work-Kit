---
tags: [ADR, 智能体开发, Checkpoint, Trace]
date: 2026-07-31
status: 已采纳
---

# ADR-002：Checkpoint与Trace分离

## 问题

运行状态和执行证据都包含过程数据，若只保存一种，容易误以为既能恢复又能审计。

## 决策

- Checkpoint保存Graph可继续执行的State和next nodes，按Thread组织。
- Trace保存一次Run发生的规范化事件和结果，按Run组织。
- Memory单独保存跨Run可复用经验。

## 后果

- Trace失败默认只产生warning，不自动破坏业务State。
- 不能仅凭Trace无条件恢复副作用工作流。
- 审计必需任务应在业务验收层把Trace失败升级。
- 生产环境需要为三类数据分别设计保留、权限与迁移。

## 证据

`checkpoint_store.py`、`trace_store.py`、`runtime.py`及`test_runtime.py`。

