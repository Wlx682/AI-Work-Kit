---
tags: [Epic, 工作流, 模板]
type: plan
category: Epic
status: 草稿
date: {{date}}
epic_id: {{title-kebab}}
lifecycle_state: requirement
platform: 客户端
repo: 【业务仓库名】
branch: 【feature/xxx】
含业务逻辑: 是
p0_open: 0
plans:
  requirement: Plans/需求分析/{{date}}-{{title}}.md
  architecture: Plans/客户端技术方案/{{date}}-{{title}}.md
  development: Plans/功能开发/{{date}}-{{title}}.md
  test: null
  deploy: null
---

# Epic：{{title}}

**创建日期**：{{date}}  
**存放路径**：`Plans/Epic/{{date}}-{{title}}.md`  
**状态**：草稿 | 进行中 | 评审中 | 已采纳 | 搁置  
**lifecycle_state**：requirement | architecture | development | test | deploy | done  
**关联仓库**：【】 · 分支：【】

> 母 plan：编排子 plan、WBS 看板、阶段门禁与变更日志。子 plan 通过 frontmatter `epic:` 反向链接本文。

---

## 一、子 Plan 索引

| 阶段 | 路径 | status | lifecycle_state |
|------|------|--------|-----------------|
| 需求分析 | `Plans/需求分析/{{date}}-{{title}}.md` | ⬜ | requirement |
| 技术方案 | `Plans/客户端技术方案/{{date}}-{{title}}.md` | ⬜ | architecture |
| 功能开发 | `Plans/功能开发/{{date}}-{{title}}.md` | ⬜ | development |
| 自动化测试 | — | ⬜ | test |
| 部署 | — | ⬜ | deploy |
| Bug 排查 | — | — | — |

---

## 二、阶段门禁

| 阶段 | 进入条件 | 退出条件 | 阻塞项 |
|------|----------|----------|--------|
| 需求分析 | PRD 可用 | 需求 plan `status: 已采纳` 且 `p0_open: 0` | P0 未闭环 |
| 技术方案 | 需求已采纳 | 方案 `status: 已采纳`（含业务逻辑时必填） | 缺模块边界 / API 契约 |
| 功能开发 | 方案已采纳或纯 UI | WBS 1–10 完成 | `plan-gate-check.sh` 失败 |
| 自动化测试 | 开发切片 4–10 完成 | 测试 plan 通过 + 切片 11 ✅ | 缺覆盖率门槛 |
| 部署 | 测试通过 | 切片 13–14 ✅ | 发布检查未勾 |
| 归档 | 线上冒烟通过 | 切片 15 ✅ | — |

---

## 三、WBS 看板（1–15）

| # | 切片 | 输入 | 输出 | 验收 | 预估 | 阻塞 |
|---|------|------|------|------|------|------|
| 1 | 需求分析闭环 | PRD | 需求 plan | P0=0 | 【】 | 【】 |
| 2 | 技术方案采纳 | 需求 plan | 方案 plan | status=已采纳 | 【】 | 【】 |
| 3 | Figma 读节点 | 设计稿 | 度量表 | node-id 齐全 | 【】 | 【】 |
| 4 | Domain / UseCase | 方案 | 领域模型 | 单测可过 | 【】 | 【】 |
| 5 | Data / API | 方案 | Repository | RPC 联调 | 【】 | 【】 |
| 6 | UI 骨架 | Figma | 1:1 布局 | 走查通过 | 【】 | 【】 |
| 7 | 静态 + 绑定 | VM + 数据 | Cell 展示 | 假数据 OK | 【】 | 【】 |
| 8 | 交互 + Variant | 设计稿 | 完整交互 | Variant 齐 | 【】 | 【】 |
| 9 | 异常 / 边界 | 需求边界表 | 空态/错误态 | 边界清单 ✅ | 【】 | 【】 |
| 10 | 联调 + 走查 | Gateway | 真机可用 | 设计走查 | 【】 | 【】 |
| 11 | 单元/集成测试 | 功能 plan | 测试 plan | CI 绿 | 【】 | 【】 |
| 12 | Code Review | PR | Review 记录 | 无 P0 | 【】 | 【】 |
| 13 | 发布检查 | 发布模板 | 检查清单 | 全勾 | 【】 | 【】 |
| 14 | 线上冒烟 | 部署 plan | 监控正常 | 无 P0 告警 | 【】 | 【】 |
| 15 | Epic 归档 | 全阶段 | Contexts 沉淀 | plan 关闭 | 【】 | 【】 |

```
[ ] 1.  需求分析闭环（链需求 plan，P0=0）
[ ] 2.  技术方案/架构采纳
[ ] 3.  Figma 读节点 + 组件映射（纯 UI 从 3 开始）
[ ] 4.  Domain / UseCase
[ ] 5.  Data 层 / API 对接
[ ] 6.  UI 骨架（1:1）
[ ] 7.  静态 + 数据绑定
[ ] 8.  交互 + Variant
[ ] 9.  异常态 / 边界
[ ] 10. 联调 + 设计走查
[ ] 11. 单元/集成测试（见自动化测试模板）
[ ] 12. Code Review（Code-Review 模板）
[ ] 13. 发布检查（发布检查清单）
[ ] 14. 线上冒烟 + 监控观察
[ ] 15. Epic 归档（Contexts 沉淀 + 关 plan）
```

---

## 四、变更日志

| 日期 | 变更类型 | 影响阶段 | 重开切片 | 确认人 | 说明 |
|------|----------|----------|----------|--------|------|
| {{date}} | 创建 Epic | — | — | 【】 | 从 Epic 母版实例化 |

---

## 续做

```
/resume plan=Plans/Epic/{{date}}-{{title}}.md 进度=【当前阶段 / WBS 片号】
```

**编排**：`/full-cycle` · `全流程闭环` · `@Skills/full_cycle_assistant.md`（自动打开看板）· `/workflow full-cycle`
