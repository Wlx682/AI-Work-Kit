---
skill: material-prep-assistant
case: cashier-config-table
---

# Material Prep Assistant Smoke Input

## 输入

- 资料类型：收银台接入配置对照表。
- 参考 App：Claw（已上线，取现值）。
- 待补充 App：namiWork（新接入，值待补充）。
- 代码路径：业务仓库工作区，grep `NMPaymentManager.registerPayment()` 取现值。

## 要求

- 只保留外部部门申请且写代码或 ASC 的字段。
- 未知值写「待补充」或「待收银台部门提供」，不猜。
- 产出到 Contexts/ 分类目录，不写业务仓库 docs/。
