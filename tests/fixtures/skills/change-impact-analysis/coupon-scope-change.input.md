---
skill: change-impact-analysis
case: coupon-scope-change
---

# Change Impact Analysis Smoke Input

## 输入

- 需求变了：收银台优惠券从「单选」改为「可叠加多张」。
- 已有产物：技术方案、功能开发、自动化测试 plan 均已成稿。
- 变更点：价格重算逻辑、券可用性校验、选择弹窗交互。
- 诉求：先看这次改动会波及哪些 plan / 代码 / 测试，再决定回退到哪一阶段。
- 约束：本次只做影响分析，不重做全新需求分析。

## 要求

- 输出影响范围报告：上游需求、下游代码与测试的连锁影响。
- 标明哪些 plan 需重写、哪些回归测试受影响。
- 结尾附 skill_run 反馈块（plan: orphan）。
