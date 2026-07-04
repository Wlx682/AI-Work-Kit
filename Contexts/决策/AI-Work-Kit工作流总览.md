---
tags: [决策, 工作流, Epic]
date: 2026-06-20
relations:
  depends_on:
    - Contexts/决策/Kit核心原则.md
    - Templates/模板约定.md
  dependents:
    - Contexts/决策/2026-07-03-开发流程审计报告.md
    - Contexts/决策/AI-Work-Kit架构总览.md
    - Contexts/决策/新手引导与最佳实践.md
  supersedes: []
  superseded_by: []
  conflicts: []

---
# AI-Work-Kit 工作流总览

> **原则**（放哪、删不删）→ [[Contexts/决策/Kit核心原则]]（勿在本文件重复）  
> **格式**（YAML、续做）→ [[Templates/模板约定]]  
> **入门 + 决策树** → [[Contexts/决策/新手引导与最佳实践]]

---

## 一、怎么用（给同事）

1. 打开 Vault + AI 编辑器（Cursor / Claude Code / Codex 任选；或业务仓 + 全局 Skill）。
2. **新需求** → 自然语言或 `/full-cycle 模块=XX`，先命中 `workflow-router`，再自动选蓝图 client-dev。
3. **其它工作流** → 自然语言即可（如「帮我清理电脑」→ `workflow-router` → computer-mgmt），或 `/full-cycle workflow=computer-mgmt`。
4. **轻流程建 plan** → `python3 scripts/workflow-plan-init.py --workflow ui-change --title 卡片`；需要一次生成全部阶段则加 `--all`。
5. **续做** → `/resume plan=Plans/... 进度=...`。
6. **看当前卡点** → `python3 scripts/workflow-status.py --workflow client-dev --epic Plans/Epic/xxx.md`。
7. **看 WBS** → `./scripts/full-cycle-boot.sh` → http://127.0.0.1:7777/

---

## 二、三层架构（积木框架）

`workflow-router` 是**自然语言入口 Skill**；`full-cycle` 是**通用编排引擎**。不同 Skill/模板/脚本通过**蓝图 manifest** 组合成不同工作流。

| 层 | 组件 | 职责 |
|----|------|------|
| **入口**（路由层） | `workflow-router` | 把自然语言映射到 workflow 蓝图；只启动引擎，不做阶段工作 |
| **状态外壳**（UX 层） | `workflow-status.py` | 把 `workflow-gate --json` 翻译成「当前 / 卡点 / 下一步 / 继续」 |
| **积木**（执行层） | 各子 Skill（requirement-analyst 等） | 读写 Plan 文件，干具体活 |
| **状态机**（控制层） | `full-cycle` 引擎 + 工具中性蓝图 `.workflows/blueprints/<name>.json` | 读蓝图决定下一阶段调哪个 Skill；维护 workflow run 游标 |
| **数据上下文**（持久层） | Epic Plan（`Plans/Epic/`） | **只存不驱动**：子 Plan 路径映射、WBS 人工确认板、里程碑摘要 |

**Epic 的硬边界**：
- ✅ 存 `plans.*` 路径索引、WBS 勾选、交付摘要。
- ❌ **不驱动阶段跳转**、不承担门禁逻辑、不记录执行游标。
- `lifecycle_state` 不参与路由：阶段由 `scripts/workflow-gate.sh` 依子 Plan 事实判定；如需整体阶段跑 `scripts/derive-epic-status.sh` 从 WBS + 子 Plan status 派生。

### 已有蓝图

| 蓝图                | usesEpic | 说明                               | Epic 母版                           |
| ----------------- | -------- | -------------------------------- | --------------------------------- |
| `client-dev`      | 是        | 客户端功能开发（需求→架构→测试先行→拆分→开发）          | `Templates/Epic模板-client-dev.md`  |
| `computer-mgmt`   | 否        | 电脑管理（盘点→清理→备份→加固→复核），无 Epic 轻量清单 | `Templates/电脑管理清单模板.md`           |
| `ui-change`       | 否        | 纯 UI 小改（范围确认→实现自检→复核）            | `workflow-plan-init.py` 生成阶段 plan |
| `bugfix`          | 否        | Bug 修复（复现→定位→修复→回归）              | `workflow-plan-init.py` 生成阶段 plan |
| `task-split-only` | 否        | 只拆任务（拆分→复核），不进入代码实现              | `workflow-plan-init.py` 生成阶段 plan |

新增蓝图：在 `.workflows/blueprints/` 新建 `<name>.json`，声明 `stages` / `epicMapping` / `usesEpic` / `triggerHints`（自然语言路由信号），并跑 `python3 scripts/validate-workflow-blueprint.py`。

### client-dev 阶段链

需求(事件风暴+实例化 1-2) → 架构+ADR(3) → 验收测试先行(4) → 拆分任务(5) → 开发(Domain/Data/UI/交互/单测/联调 6-11)。详见 `Templates/Epic模板-client-dev.md` §三。

```mermaid
stateDiagram-v2
    direction LR
    [*] --> requirement
    requirement --> architecture: 已采纳/P0=0
    architecture --> test_first: 方案已采纳
    test_first --> split: WBS 4 ✅
    split --> development: 子任务已拆
    development --> [*]
```

新建 client-dev Epic：复制 `Templates/Epic模板-client-dev.md` → `Plans/Epic/`。

---

## 三、独立任务（不建 Epic 或半独立）

| 任务 | 说法 | plan |
|------|------|------|
| Bug | `workflow=bugfix` 或 `python3 scripts/workflow-plan-init.py --workflow bugfix --title xxx` | `Plans/Bug排查/` |
| 学习 | `/learn-assistant` | `Plans/学习/` |
| 纯 UI 小改 | `workflow=ui-change` 或 `python3 scripts/workflow-plan-init.py --workflow ui-change --title xxx` | `Plans/界面开发/` |
| 只拆任务 | `workflow=task-split-only` 或 `python3 scripts/workflow-plan-init.py --workflow task-split-only --title xxx` | `Plans/功能开发/` |
| PM 对照表 | `/material-prep` | **Contexts/**（通用） |

---

## 四、看板与门禁

```bash
./scripts/full-cycle-boot.sh --epic Plans/Epic/xxx.md
python3 scripts/workflow-status.py --workflow client-dev --epic Plans/Epic/xxx.md
bash scripts/workflow-gate.sh --workflow client-dev --epic Plans/Epic/xxx.md --json
bash scripts/derive-epic-status.sh Plans/Epic/xxx.md      # 派生真实阶段（只读）
bash scripts/kanban-sync.sh --boot --epic Plans/Epic/xxx.md
bash scripts/plan-gate-check.sh Plans/功能开发/xxx.md
python3 scripts/workflow-plan-init.py --workflow ui-change --title 卡片
python3 scripts/workflow-smoke-test.py ui-change bugfix task-split-only
```

| 脚本 | 用途 |
|------|------|
| `full-cycle-boot.sh` | 看板 + 浏览器 |
| `workflow-status.py` | **日常推荐**：人话状态摘要（当前 / 卡点 / 下一步 / 继续） |
| `workflow-gate.sh` | **通用**工作流阶段门禁（读蓝图，只看子 Plan 事实） |
| `workflow-plan-init.py` | 为无 Epic 轻流程创建当前阶段/全部阶段 plan 骨架 |
| `workflow-smoke-test.py` | 隔离验证轻流程：路由、空态阻塞、补齐阶段 plan 后 done |
| `derive-epic-status.sh` | 从 WBS+子 Plan status 派生 `derived_status`（只读，不写回） |
| `full-cycle-gate.sh` | 兼容封装：等价转发到 `workflow-gate.sh --workflow client-dev`；新引用直接使用 `workflow-gate.sh` |
| `plan-gate-check.sh` | 写代码前（与蓝图正交，不动） |
| `kanban-sync.sh` | Agent 改进度 |
| `generate-pipeline-status.sh --write` | 刷新 [[索引]] 进度表 |
| `learning-progress-read.sh` / `snapshot.sh` | 学习开/收尾 |

---

## 五、Skill 速查

开发主线：`workflow-router` · `full-cycle` · `requirement-analyst` · `architecture-design-assistant` · `test-generator` · `task-splitter` · `feature-dev-assistant` · `figma-ui` · `code-review` · `change-impact-analysis`

通用：`resume-assistant` · `template-generator` · `report-assistant` · `material-prep-assistant`

学习：`learn-assistant` · `learning-audit-assistant`

Claude workflow：`.claude/workflows/full-cycle.js` · `learning-audit` · `dev-lifecycle-audit`

工作流蓝图真理源：`.workflows/blueprints/*.json`；`.claude/workflows/full-cycle.js` 只是 Claude Code 的引擎入口。日常状态看 `workflow-status.py`，底层排查才看 `workflow-gate.sh --json`。

详情：[[Skills/README]] · [[索引#高频任务速查]]

---

## 六、Figma（规范在 Contexts，任务在 Plans）

- 读节点：Figma MCP；度量表、走查 → **Plans**（见 [[Templates/Figma设计走查模板]]）。
- Contexts 只保留：[[Contexts/Figma/项目设计规范]]、[[Contexts/Figma/Figma界面开发最佳实践]]、[[Contexts/Figma/Figma-MCP配置]]。

---

## 相关

- [[Contexts/决策/新手引导与最佳实践]] — 入门 + 决策树 + 脚本速查
- [[Contexts/Claude-Code集成AI-Work-Kit]]
