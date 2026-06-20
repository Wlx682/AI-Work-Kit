# 全流程闭环助手（full-cycle-assistant）

当用户说 **全流程开发 / 全流程闭环 / 启动全流程 / full-cycle / /full-cycle**，或 **从【阶段】开始**（如从自动化测试开始）时执行。

> Cursor：`@Skills/full_cycle_assistant.md` 或 `.cursor/skills/full-cycle-assistant/SKILL.md`  
> Claude Code：`@Skills/full_cycle_assistant.md` 或 `/workflow full-cycle`（仍须 boot 看板）

## 与 project-manager 的关系

| | project-manager | full-cycle-assistant |
|--|-----------------|----------------------|
| 定位 | 编排草案 / 说明 | **可执行入口** |
| 看板 | 无 | **开场必启** `full-cycle-boot.sh` |
| 中间阶段 | 未细化 | **支持阶段= test / deploy 等** |

新对话默认用 **full-cycle-assistant**；`project-manager` 保留作状态机参考。

## 开场命令（Agent 必须执行）

```bash
cd ~/Documents/AI-Work-Kit
bash scripts/full-cycle-boot.sh [--epic Plans/Epic/xxx.md]
```

浏览器：**http://127.0.0.1:7777/**

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
