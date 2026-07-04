---
skill: event-storming-assistant
case: checkout-coupon
---

# Event Storming Smoke Input

## 输入

- workflow: client-dev，WBS 1 需求阶段第 1 步。
- 场景：收银台优惠券模块，从进入收银台到提交订单。
- 参与角色：用户、收银台系统、优惠券服务、价格服务。
- 已知分歧：多券叠加规则、过期券是否上墙、价格不一致的兜底事件。

## 要求

- 输出领域事件墙、热点与分歧、角色-系统交互。
- 事件用过去式，关键事件补触发命令与聚合/对象。
- 只梳理事件，不写 Given-When-Then 场景。
