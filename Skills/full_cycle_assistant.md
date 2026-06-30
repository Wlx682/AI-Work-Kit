# 全流程闭环助手（full-cycle-assistant）

## 触发条件

当用户说 **全流程开发 / 全流程闭环 / 启动全流程 / 启动项目 / full-cycle / /full-cycle**，或 **从【阶段】开始**（如从自动化测试开始）时执行。

> Cursor：`@Skills/full_cycle_assistant.md` 或 `.cursor/skills/full-cycle-assistant/SKILL.md`  
> Claude Code：`@Skills/full_cycle_assistant.md` 或 `/workflow full-cycle`（仍须 boot 看板）

## 🔒 互斥锁（必守）

**用户若只说单个阶段词，优先路由到对应子 Skill，不要劫持为「全流程」**：

| 用户输入命中 | 路由到 | 不要走 full-cycle |
|--------------|--------|-------------------|
| 「需求分析 / PRD」 | `requirement-analyst` | ✗ |
| 「系统架构 / 模块边界 / ER 图」 | `architecture-design-assistant` | ✗ |
| 「拆任务 / WBS」 | `task-splitter` | ✗ |
| 「开发功能 / 写代码 / 实现 XX」 | `feature-dev-assistant` | ✗ |
| 「做界面 / 还原 Figma / 对稿」 | `figma-ui` | ✗ |
| 「写测试 / 生成测试用例」 | `test-generator` | ✗ |
| 「上线 / 发布 / 灰度」 | `deployment-assistant` | ✗ |
| 「需求变了 / 改 scope」 | `change-impact-analysis` | ✗ |
| 「检查 Epic 进度 / 审计」 | `dev-lifecycle-audit-assistant` | ✗ |

**只有用户显式说「全流程 / 启动项目 / 一条龙 / 从需求一直做到上线」时，才走本 Skill**。

## ✋ WBS 修订门禁

修订 Epic WBS（增删切片、改 Skill/验收、重排顺序）时：

1. **优先** `task-splitter` 产出/更新 `Plans/功能开发/` 主 plan + 子任务
2. 边界不清 → **问用户**，禁止 Agent 单方面推荐拆分方案
3. 写回 Epic 前须有子 plan 真理源（见 `Contexts/决策/母子plan投影规则.md`）

## 🛟 降级兜底（≥3 Skill 同时命中时）

如果对当前用户输入有 **3 个或以上** Skill 都能匹配，**禁止 Agent 自行选定**，统一路由到 `resume-assistant`，由它询问：

> 「您是想 **续做旧任务**（请给 plan 路径），还是 **开启新流程**（请明确是：需求 / 架构 / 开发 / 测试 / 上线 中的哪一步）？」

由用户裁决，避免 Agent 替用户做决定。

## 与 project-manager 的关系

| | project-manager | full-cycle-assistant |
|--|-----------------|----------------------|
| 定位 | 编排草案 / 说明 | **可执行入口** |
| 看板 | 无 | **开场必启** `full-cycle-boot.sh` |
| 中间阶段 | 未细化 | **支持阶段= test / deploy 等** |

新对话默认用 **full-cycle-assistant**；`project-manager` 保留作状态机参考。

## 开场命令（Agent 必须执行）

```bash
cd ~/git/AI-Work-Kit
bash scripts/full-cycle-boot.sh [--epic Plans/Epic/xxx.md]
```

浏览器：**http://127.0.0.1:7777/**

> **新需求阶段例外**：当本次是「创建新需求」、看板/Epic 还没建好时，用
> `bash scripts/full-cycle-boot.sh --new-requirement`——只起服务、**不**自动打开浏览器。
> 等 Epic 建好后再 `--epic Plans/Epic/xxx.md` boot，看板才会自动打开。

## 阶段入口

| 说法 | lifecycle_state | Skill |
|------|-----------------|-------|
| 需求 / PRD | requirement | requirement-analyst |
| 方案 / 架构 | architecture | architecture-design-assistant |
| 开发 / 功能 | development | task-splitter → feature-dev-assistant |
| **测试 / 自动化测试** | test | test-generator |
| **部署 / 上线** | deploy | deployment-assistant |

## 输出尾

每步更新 Epic/WBS/子 plan 进度后执行：

```bash
bash scripts/kanban-sync.sh --boot --epic Plans/Epic/xxx.md
# WBS 勾选推荐：
bash scripts/kanban-sync.sh --epic Plans/Epic/xxx.md --slices-done 1,2,3
```

```
📌 当前阶段：… | 看板：http://127.0.0.1:7777/ | 下一个阶段：… | /resume plan=…
```

细则见 `.cursor/skills/full-cycle-assistant/SKILL.md`。
