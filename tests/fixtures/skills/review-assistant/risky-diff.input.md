---
skill: review-assistant
case: risky-diff
---

# Review Assistant Smoke Input

## 输入

- 审查范围：价格计算模块 diff。
- 风险：优惠券为空时仍访问 `coupon.id`；主线程同步请求价格接口；缺少回归测试。
- 文件：
  - `CheckoutPriceViewModel.swift`
  - `CouponRepository.swift`

## 要求

- Findings first。
- 按严重级排序。
- 问题必须带文件或行号。
- 如果没有阻塞问题，也要说明测试缺口。
