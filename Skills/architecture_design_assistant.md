# architecture-design-assistant · 正式架构设计

client-dev 中位于需求排序之后、故事拆分之前，是正式必经阶段。

输入：已采纳需求 Plan 与已确认的 `Plans/需求排序/` Backlog。
输出：`Plans/技术方案/`。

必须包含模块边界、ER/数据模型、状态机、API Schema 与错误码、非功能约束、ADR、需求影响矩阵。架构决定系统如何组织，但不得把交付任务拆成 Domain/Data/UI。

需求 P0 未闭环或排序未确认时阻塞；`status: 已采纳` 后进入 `story-split`。最后一个反馈增加 `workflow_stage: architecture`。
