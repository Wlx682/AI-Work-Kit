# 续做助手 Skill

当用户说「续做」或使用 `**/resume**` 命令时执行。

## 标准命令（全库统一）

```
/resume plan=Plans/【分类】/【文件名】.md 进度=【当前完成情况】
```

也兼容：`续做，plan=Bug排查/xxx.md，进度=...`（plan 可为相对 `Plans/` 的路径）。

## 执行步骤

1. 读取 `Plans/[plan路径]`；若含 `[[Contexts/]]` 链接一并读取。
2. **Epic 感知**：若 frontmatter 含 `epic:`，读取 Epic 母 plan 的 `workflow`、WBS 复选框、子 Plan 索引表，并运行 `scripts/workflow-gate.sh --workflow <name> --epic <epic>` 派生当前阶段。
3. **事件流回放（会话层，优先于凭空猜测）**：跑 `python3 scripts/workflow-status.py --workflow <name> --epic <epic>`——它除派生当前阶段外，还会从 `.workflows/events/<run-id>.events.jsonl` 回放门禁历史，输出「最近门禁：<日期> 通过/未过 — <原因>」与「连续判不过」告警。**答「上次为何卡住 / 门禁为何判不过」时先读这里的历史，不要只凭当前快照重新推断**；有 run_id 时可加 `--run <run-id>` 精确定位。
4. **门禁（开发阶段）**：对 `Plans/功能开发/` 下 plan，先跑 `bash scripts/plan-gate-check.sh <plan> --stage development`；若 `BLOCKED:` → **只输出补文档任务，不建议写代码**。
5. 根据进度判断下一步（对照 plan / Epic WBS 勾选切片）。
6. **推荐 Skill**：优先采用 `workflow-gate.sh` 输出的 `recommended_skill`；development 仍须读 WBS/子 plan **Skill 列**。


| workflow-gate current_state | 推荐 Skill | 典型切片 |
|-----------------------------|------------|----------|
| requirement | `event-storming-assistant` / `spec-by-example-assistant` / `requirement-analyst` | WBS 1–2 |
| architecture | `architecture-design-assistant` | WBS 3 |
| test-first | `test-generator` | WBS 4 |
| split | `task-splitter` | WBS 5 |
| development | Skill=`figma-ui` → `figma-ui`；否则 `feature-dev-assistant` | WBS 6–11 |

**WBS 修订**：用户要改切片/拆任务 → 路由 `task-splitter` 或列待确认项找用户；禁止擅自推荐 A/B/C 方案。


1. 输出结构化结果（见下方格式）。
2. 进度不足时要求用户补充。

## 输出格式

```markdown
## 续做：[任务标题]

**Plan**：`Plans/...`
**Epic**：`Plans/Epic/...`（如有）
**阶段**：由 workflow-gate 派生（如 requirement / architecture / test-first / development / verify / review / deploy / retro）
**进度**：...

### 已完成
- ...

### 下一步
1. ...

### 可能原因（排查类）
- ...（如 workflow-status 回放出「最近门禁未过」，直接引用其原因，而非重新猜）

### 验证方法
- ...

### 待补充（如有）
- ...
```

## 触发示例

```
/resume plan=Plans/功能开发/2026-06-11-会员-首次启动与过期处理.md 进度=§2.2 首页弹窗方案已定

@Skills/resume_assistant.md 续做，plan=Plans/学习/【课程 plan 文件】，进度=概念已讲，待勾选步骤
```
