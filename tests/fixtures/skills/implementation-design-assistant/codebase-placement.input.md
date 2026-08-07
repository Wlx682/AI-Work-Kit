---
skill: implementation-design-assistant
---

## 输入

client-dev 已完成 story-split，Scope Story 为 US-001「用户可以查看订单折扣」。

已有架构约束：Presentation 只能依赖 Domain，Domain 不依赖 Data/API。

现有代码证据：

- src/features/order/view.ts：订单页入口和同模块命名参考
- src/features/order/use-case.ts：Domain 用例命名和依赖方向参考
- tests/order-discount.test.ts：Red 测试应放在同一测试套件

请在写代码前产出 implementation_design JSON，并说明目标文件、命名依据、模块边界、依赖方向和 Red 测试位置。
