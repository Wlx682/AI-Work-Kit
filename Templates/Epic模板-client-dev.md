---
tags: [Epic, 工作流, 模板]
type: plan
category: Epic
status: 草稿
date: {{date}}
epic_id: {{title-kebab}}
workflow: client-dev
lifecycle_state: requirement  # 不参与路由（勿手改驱动流程）；整体阶段跑 scripts/derive-epic-status.sh 派生
platform: 客户端
repo: 【业务仓库名】
branch: 【feature/xxx】
含业务逻辑: 是
p0_open: 0
plans:
  requirement: Plans/需求分析/{{date}}-{{title}}.md
  architecture: Plans/技术方案/{{date}}-{{title}}.md
  test: null
  development: Plans/功能开发/{{date}}-{{title}}.md
relations:
  depends_on:
    - Templates/模板约定.md
  dependents: []
  supersedes: []
  superseded_by: []
  conflicts: []

---
# Epic：{{title}}（工作流：client-dev · 15 步）

**创建日期**：{{date}}  
**存放路径**：`Plans/Epic/{{date}}-{{title}}.md`  
**状态**：草稿 | 进行中 | 评审中 | 已采纳 | 搁置  
**关联仓库**：【】 · 分支：【】

> **三层架构定位**：本 Epic 是**数据上下文（聚合根）**——只存子 Plan 路径映射、WBS 人工确认板、里程碑摘要。
> **不驱动流程**：阶段推进由通用执行器读工具中性蓝图 `.workflows/blueprints/client-dev.json` + `scripts/workflow-gate.sh`（只看子 Plan 事实）决定。
> `lifecycle_state` 不参与路由，仅供人工阅读；整体阶段跑 `bash scripts/derive-epic-status.sh Plans/Epic/{{date}}-{{title}}.md` 派生。

---

## 一、子 Plan 索引

| 阶段 | 路径 | status |
|------|------|--------|
| 需求分析（事件风暴+实例化） | `Plans/需求分析/{{date}}-{{title}}.md` | ⬜ |
| 技术方案 + ADR | `Plans/技术方案/{{date}}-{{title}}.md` | ⬜ |
| 验收测试先行 | — | ⬜ |
| 拆分任务 | — | ⬜ |
| 功能开发 | `Plans/功能开发/{{date}}-{{title}}.md` | ⬜ |
| Bug 排查 | — | — |

---

## 二、阶段门禁（退出条件 = 子 Plan 文件系统事实）

| 阶段 | stage key | WBS | 退出条件（workflow-gate.sh 判定） |
|------|-----------|-----|-----------------------------------|
| 需求分析 | requirement | 1–2 | 需求 plan `status: 已采纳` 且 `p0_open: 0` + 验收标准章节 |
| 技术方案 | architecture | 3 | 方案 `status: 已采纳`（含业务逻辑时必经） |
| 验收测试先行 | test-first | 4 | 测试 plan 存在 + WBS 4 ✅ |
| 拆分任务 | split | 5 | 主 plan + 子任务已拆 + WBS 5 ✅ |
| 功能开发 | development | 6–11 | `plan-gate-check.sh` OK + WBS 6–11 ✅ |

---

## 三、WBS 看板（1–11 · 精简版）

| # | 切片 | 归属 stage | Skill | 验收 |
|---|------|-----------|-------|------|
| 1 | 事件风暴工作坊 | requirement | event-storming-assistant | 事件墙无歧义、热点认领 |
| 2 | 实例化需求（≥10 组 GWT + 线框） | requirement | spec-by-example-assistant | PO/开发/测试对齐 |
| 3 | 技术方案 + ADR + 领域模型 | architecture | architecture-design-assistant | status=已采纳 |
| 4 | 验收测试先行（外层 TDD，先红） | test-first | test-generator | 测试自动化运行，失败仅因未实现 |
| 5 | 原子任务拆分（主 plan + 子任务） | split | task-splitter | 子任务边界清晰、可独立验收 |
| 6 | Domain / UseCase 实现 | development | feature-dev-assistant | 单测过 |
| 7 | Data / API 实现与联调 | development | feature-dev-assistant | 真实接口替换假数据 |
| 8 | UI 骨架 + 静态设计走查 | development | figma-ui | 静态布局走查通过 |
| 9 | 交互 + 全 Variant（空/错误态） | development | figma-ui | 交互走查 + 边界示例可覆盖 |
| 10 | 单元测试补充与回归（内层 TDD） | development | test-generator | CI 单测全绿 |
| 11 | 真机联调 + 集成设计走查 | development | figma-ui / feature-dev-assistant | 真机适配走查通过 |

> ⚠️ **看板硬约束**：下方 fenced checklist 每行必须为 `[标记] 编号. 描述`；标记 `[ ]`/`[~]`/`[-]`/`[x]`；编号纯数字或 `6a` 后缀。`[-]` 表示已跳过/不适用，必须由蓝图 `optionalWbsSlices` 或看板跳过按钮支撑。不符合会被 `kanban-server.py` 静默丢弃，`plan-gate-check.sh` 提交时预检。

```
[ ] 1.  事件风暴工作坊（领域事件墙 / 热点 / 角色-系统）
[ ] 2.  实例化需求（≥10 组 Given-When-Then + 线框草图）
[ ] 3.  技术方案 + ADR + 领域模型草图
[ ] 4.  验收测试先行（外层 TDD，先红）
[ ] 5.  原子任务拆分（主 plan + 子任务）
[ ] 6.  Domain / UseCase 实现（单测过）
[ ] 7.  Data / API 实现与联调
[ ] 8.  UI 骨架 + 静态设计走查
[ ] 9.  交互 + 全 Variant（空态 / 错误态）
[ ] 10. 单元测试补充与回归（内层 TDD）
[ ] 11. 真机联调 + 集成设计走查
```

---

## 四、变更日志

| 日期 | 变更类型 | 影响阶段 | 重开切片 | 确认人 | 说明 |
|------|----------|----------|----------|--------|------|
| {{date}} | 创建 Epic | — | — | 【】 | 从 client-dev 母版实例化 |

---

## 续做

```
/resume plan=Plans/Epic/{{date}}-{{title}}.md 进度=【派生阶段 / WBS 片号】
```

**编排**：自然语言「全流程开发」→ `workflow-router` → `client-dev`；或显式 `workflow=client-dev`
**派生阶段**：`bash scripts/derive-epic-status.sh Plans/Epic/{{date}}-{{title}}.md`
