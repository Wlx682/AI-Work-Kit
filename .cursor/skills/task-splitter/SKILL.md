---
name: task-splitter
description: 将技术方案拆为 5-10 原子任务，主 plan + 子任务 plan 写入 Plans/功能开发/。触发词：任务拆分、拆任务、task-splitter。
---

# 任务拆分助手

输入：`Plans/【客户端|服务端】技术方案/`（已采纳）  
产出：`Plans/功能开发/YYYY-MM-DD-模块.md` + `xxx-子任务NN-简述.md`

1. 读方案 + 需求真理源  
2. 5–10 原子任务，主 plan Checklist 双链子任务  
3. 子任务 `parent:` 链主 plan；`lifecycle_state: development`  
4. 实现：`/resume plan=子任务路径`

同步：`Skills/task_splitter.md`
