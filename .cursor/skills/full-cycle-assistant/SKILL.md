---
name: full-cycle-assistant
description: >-
  启动 Epic 全流程闭环开发（需求→方案→开发→测试→部署），支持从中间阶段切入；
  开场必跑 full-cycle-boot.sh 自动打开看板 http://127.0.0.1:7777/。
  触发词：全流程开发、全流程闭环、启动全流程、启动项目、一条龙、full-cycle、/full-cycle、从测试开始、阶段=自动化测试。
  互斥锁：单阶段词路由子Skill，不劫持全流程；≥3 Skill命中→resume-assistant降级兜底。
---

# 全流程闭环助手（full-cycle-assistant）

Vault：`~/git/AI-Work-Kit`  
原则：[[Contexts/决策/Kit核心原则]] · 状态机：`.claude/workflows/full-cycle.json`

> 与 `project-manager` 区别：**本 Skill 可执行**——开场拉起看板、解析入口阶段、路由到子 Skill。

## 触发条件

当用户说 **全流程开发 / 全流程闭环 / 启动全流程 / 启动项目 / 一条龙 / full-cycle / /full-cycle**，或 **从【阶段】开始**（如从自动化测试开始）时执行。

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

---

## 0. 开场（硬规则 · 每次必做）

**在分析需求或写 plan 之前**，于 Vault 根目录执行：

```bash
cd ~/git/AI-Work-Kit
bash scripts/full-cycle-boot.sh [--epic Plans/Epic/YYYY-MM-DD-模块.md]
```

- 自动后台启动 `kanban-server`（未运行时）
- 自动用系统浏览器打开 **http://127.0.0.1:7777/**（可加 `?epic=` 预选 Epic）
- 向用户确认：**「看板已打开，WBS 变更会写回 markdown」**

> **新需求例外**：本次是「创建新需求」、看板/Epic 还没建好时，用
> `bash scripts/full-cycle-boot.sh --new-requirement`——只起服务、**不**自动打开浏览器，
> 也不回退选旧 Epic。等 Epic 建好后再 `--epic Plans/Epic/...md` boot，看板才会自动打开。

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

## 反馈回路（skill_run）

完成任务的最后一步**必须**输出 `skill_run` 反馈（协议：`Contexts/决策/Skill反馈协议.md`）：
追加到本次 本步子 Skill 产出的阶段 plan（由该子 Skill 追加；full-cycle 仅编排不重复写） **末尾**的 `## 反馈（skill_run）` 节（fenced ```yaml`，非裸 frontmatter）。
`contexts_used[].utility` 二选一：`high`（附一句话 `reason`）或 `not-needed`；必填 `skill: full-cycle-assistant` / `plan` / `date` / `contexts_used` / `contexts_missing` / `contexts_stale`。缺则 `plan-gate-check.sh` 报失败。
