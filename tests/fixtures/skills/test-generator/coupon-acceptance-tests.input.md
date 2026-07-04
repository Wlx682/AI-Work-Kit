---
skill: test-generator
case: coupon-acceptance-tests
---

# Test Generator Smoke Input

## 输入

- Epic：`Plans/Epic/2026-07-收银台优惠券.md`，`plans.development` 已就绪。
- 需求验收标准：AC1 券可用则展示、AC2 不可用置灰、AC3 选中后价格重算。
- 被测模块：优惠券可用性校验器、价格重算 UseCase。
- 当前阶段：test-first，需补验收测试先行 plan。
- 工具：客户端 XCTest / 服务端 go test。

## 要求

- 按模板输出测试范围、用例映射（链 AC）、单元/集成清单、CI 命令。
- 用例必须映射到验收标准 AC。
- 结尾附 skill_run 反馈块。
