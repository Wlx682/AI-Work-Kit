---
skill: architecture-design-assistant
case: coupon-module-arch
---

# Architecture Design Assistant Smoke Input

## 输入

- 系统架构设计：收银台优惠券选择子系统（客户端 + 服务端）。
- 需求真理源：`Plans/需求分析/2026-07-收银台优惠券.md`，P0 已闭环，含边界与验收。
- 范围：优惠券列表拉取、可用性校验、选中后价格重算、异常态兜底。
- 依赖：价格服务、优惠券服务、用户券包表。
- 约束：方案未定，需给出模块边界、ER 图、接口契约；不写实现代码。

## 要求

- 必须输出模块边界、数据模型（ER 图 + 字段）、API Schema + 错误码。
- 不套空模板骨架，需填充真实设计内容。
- 结尾附 skill_run 反馈块。
