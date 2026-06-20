---
name: full-cycle-assistant
description: >-
  启动 Epic 全流程闭环开发（需求→方案→开发→测试→部署），支持从中间阶段切入；
  开场必跑 full-cycle-boot.sh 自动打开看板 http://127.0.0.1:7777/。
  触发词：全流程开发、全流程闭环、启动全流程、full-cycle、/full-cycle、从测试开始、阶段=自动化测试。
---

# 全流程闭环助手（full-cycle-assistant）

Vault：`~/Documents/AI-Work-Kit`  
原则：[[Contexts/决策/Kit核心原则]] · 状态机：`.claude/workflows/full-cycle.json`

> 与 `project-manager` 区别：**本 Skill 可执行**——开场拉起看板、解析入口阶段、路由到子 Skill。  
> Claude Code 亦可用 `/workflow full-cycle`，但**仍须先跑 boot 脚本**打开看板。

---

## 0. 开场（硬规则 · 每次必做）

**在分析需求或写 plan 之前**，于 Vault 根目录执行：

```bash
cd ~/Documents/AI-Work-Kit
bash scripts/full-cycle-boot.sh [--epic Plans/Epic/YYYY-MM-DD-模块.md]
```

- 自动后台启动 `kanban-server`（未运行时）
- 自动用系统浏览器打开 **http://127.0.0.1:7777/**（可加 `?epic=` 预选 Epic）
- 向用户确认：**「看板已打开，WBS 变更会写回 markdown」**

若 boot 失败：贴 `scripts/.kanban-server.log` 末尾，仍继续文字流程。

**每步有进度**（WBS / lifecycle / 子 plan status）后**必跑**：

```bash
bash scripts/kanban-sync.sh --boot --epic Plans/Epic/YYYY-MM-DD-模块.md
# WBS 勾选（推荐，带变更日志）：
bash scripts/kanban-sync.sh --epic Plans/Epic/…md --slice 4 --done
```

浏览器打开看板后会 **每 2.5s 自动同步** markdown 变更，无需手点「刷新」。

---

## 1. 触发词（对话 / @Skill 均可）

| 类型 | 示例 |
|------|------|
| 从头 | 全流程开发、全流程闭环、启动全流程、`/full-cycle` |
| 中间切入 | **从测试开始**、阶段=开发、入口=deploy |
| 带模块 | `/full-cycle 模块=支付` · `epic=Plans/Epic/xxx.md` |

**治理**：无 Epic 的新需求 → 用本 Skill 建 Epic（见 [[Contexts/决策/Kit核心原则]]）。

**解析优先级**：用户显式 `阶段=` / `从X开始` > Epic 现有 `lifecycle_state` > 默认 `requirement`。

---

## 2. 阶段 → Skill 路由

| lifecycle_state | 用户说法 | WBS | 执行 Skill | 产出目录 |
|-----------------|----------|-----|------------|----------|
| `requirement` | 需求、PRD、需求分析 | 1 | `requirement-analyst` | `Plans/需求分析/` |
| `architecture` | 方案、架构、技术方案 | 2 | `architecture-design-assistant` | `Plans/客户端\|服务端技术方案/` |
| `development` | 开发、功能、拆任务 | 3–10 | `task-splitter` → `feature-dev-assistant` | `Plans/功能开发/` |
| `test` | 测试、自动化测试 | 11 | `test-generator` | `Plans/自动化测试/` |
| `deploy` | 部署、上线、发布 | 13–14 | `deployment-assistant` | `Plans/部署/` |

中间切入时：

1. 读取或创建 Epic（`Templates/Epic母版.md` / `template-generator 任务类型=Epic`）
2. 将 Epic frontmatter `lifecycle_state` 设为入口阶段（用户指定时）
3. **门禁提醒**（机械检查 `scripts/full-cycle-gate.sh --epic ...`）：
   - 开发前：需求 P0=0、方案已采纳 → `plan-gate-check.sh`
   - 测试前：WBS 1–10 完成、Epic `plans.test` 可填
   - 部署前：WBS 11 完成、`plans.deploy` 可填
4. 执行该阶段 Skill **仅一步**；完成后汇报并指向看板上下一切片

---

## 3. Epic  bootstrap（无 Epic 时）

1. 问清：模块名、平台（客户端/服务端）、是否含业务逻辑、代码仓/分支（可选）
2. `template-generator` 或按 `Templates/Epic母版.md` 创建 `Plans/Epic/YYYY-MM-DD-模块.md`
3. 子 plan 索引表留空位，随阶段 Skill 填充
4. **再次** `full-cycle-boot.sh --epic Plans/Epic/...md`

---

## 4. 与看板协作

| 用户操作 | Agent 行为 |
|----------|------------|
| 看板点 WBS 完成 | 以 markdown 为准；续做时读 Epic 复选框 |
| **Agent 更新 Epic 进度** | **硬规则**：改 WBS / lifecycle / 子 plan status 后**必跑** `bash scripts/kanban-sync.sh --boot --epic Plans/Epic/xxx.md`；WBS 勾选**优先** `--slice` / `--slices-done` |
| 需要续做命令 | 看板「复制续做命令」或 `/resume plan=...` |
| 阶段跳转 | `--lifecycle` 或改 Epic frontmatter + `kanban-sync` |

浏览器已 **每 2.5s 轮询** `/api/revision`；markdown 变更后看板自动刷新（无需手点「刷新」）。

---

## 5. 阻塞

无法自动决策 → `Plans/阻塞问题/YYYY-MM-DD-简述.md` + 询问用户；看板 WBS 相关片标为阻塞（`p0_open>0` 时 WBS 1–2 在看板显示 blocked 列）。

---

## 6. 每步结束（必输出）

```text
📌 当前阶段：[lifecycle_state 中文] | 正在执行：[Skill名] | 看板：http://127.0.0.1:7777/ | 下一个阶段：[...] | 如需中断：/resume plan=Plans/...
```

---

## 7. 示例

```
/full-cycle 模块=会员盒子切换 平台=客户端 从测试开始
```

Agent 顺序：boot 看板 → 查/建 Epic → `lifecycle_state: test` → `test-generator` → 更新 Epic 索引 test plan 路径。

```
全流程闭环  epic=Plans/Epic/2026-06-20-新版工作空间.md
```

Agent 顺序：boot `--epic` → 读 Epic `lifecycle_state` → 路由当前阶段 Skill。

---

同步：`Skills/full_cycle_assistant.md`
