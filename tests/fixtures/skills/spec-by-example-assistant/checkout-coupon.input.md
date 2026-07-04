---
skill: spec-by-example-assistant
case: checkout-coupon
---

# Spec By Example Smoke Input

## 输入

- 事件风暴已产出：券已展示、券已选择、价格已刷新、订单已提交等事件。
- 场景：收银台优惠券选择与价格刷新，覆盖主链路、边界、异常、反例。
- 边界：无可用券、券叠加达上限、券刚好过期临界点。
- 异常：优惠券接口超时、价格接口与本地不一致。

## 要求

- 至少写 10 组 Given-When-Then，含反例。
- 每条验收标准可测试，能被 test-generator 映射。
- 线框位只记录当前任务材料，不沉淀到 Contexts。
