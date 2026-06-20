---
name: change-impact-analysis
description: 需求变更时反向查找关联 plan，输出影响报告并标记 pending-change。触发词：需求变更、改scope、change-impact-analysis。
---

# 变更影响分析

扫描：技术方案、功能开发、自动化测试、部署 plan（双链/grep）

1. 输出影响报告：哪些 plan/代码/测试需重写  
2. 用户确认后：`status: pending-change`  
3. P0 变更 → 回需求/架构；小改 → `/resume` 子任务

同步：`Skills/change_impact_analysis.md`
