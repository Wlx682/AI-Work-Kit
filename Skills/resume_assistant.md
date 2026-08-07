# 续做助手 Skill

当用户说「续做」或使用 `**/resume**` 命令时执行。

## 标准命令（全库统一）

```
/resume plan=Plans/【分类】/【文件名】.md 进度=【当前完成情况】
```

也兼容：`续做，plan=Bug排查/xxx.md，进度=...`（plan 可为相对 `Plans/` 的路径）。

## 执行步骤

1. 读取 `Plans/[plan路径]`；若含 `[[Contexts/]]` 链接一并读取。
2. **Epic 感知**：若 frontmatter 含 `epic:`，读取 Epic 母 plan 的 `workflow` 与 `plans:` 子 Plan 索引，并运行 `scripts/workflow-gate.sh --workflow <name> --epic <epic>` 派生当前阶段。
3. **事件流回放（会话层，优先于凭空猜测）**：跑 `python3 scripts/workflow-status.py --workflow <name> --epic <epic>`——它除派生当前阶段外，还会从 `.workflows/events/<run-id>.events.jsonl` 回放门禁历史，输出「最近门禁：<日期> 通过/未过 — <原因>」与「连续判不过」告警。**答「上次为何卡住 / 门禁为何判不过」时先读这里的历史，不要只凭当前快照重新推断**；有 run_id 时可加 `--run <run-id>` 精确定位。
4. **门禁（开发阶段）**：对 `Plans/功能开发/` 下 plan，先跑 `bash scripts/plan-gate-check.sh <plan> --stage development`；若 `BLOCKED:` → **只输出补文档任务，不建议写代码**。
5. 根据进度判断下一步：优先对照 `workflow-gate.sh` 的 `current_state`、`recommended_skill`、`.stories.json` Scope、Story 子 Plan、`implementation_design` 与 `tdd_evidence`。
6. **推荐 Skill**：优先采用 `workflow-gate.sh` 输出的 `recommended_skill`；若 `current_state=implementation-design`，读取 `.stories.json` 和 Scope Story 子 Plan 后用 `implementation-design-assistant`；若 `current_state=story-development`，读取 `.stories.json` 中尚未完成的 Scope Story、Story 子 Plan、`implementation_design` 与 `tdd_evidence`，纯 UI Story 子任务才转 `figma-ui`，否则用 `feature-dev-assistant`。

| workflow-gate current_state | 推荐 Skill | 典型依据 |
|-----------------------------|------------|----------|
| requirement | `event-storming-assistant` / `spec-by-example-assistant` / `requirement-analyst` | 需求 plan、AC、P0 |
| prioritization | `backlog-prioritization-assistant` | Backlog 排序与团队确认 |
| architecture | `architecture-design-assistant` | 技术方案、ADR、架构引用 |
| story-split | `task-splitter` | Story 拆分、故事点、Scope、`.stories.json` |
| implementation-design | `implementation-design-assistant` | Scope Story 子 Plan、`implementation_design` |
| story-development | `feature-dev-assistant` / `figma-ui` | Scope Story 子 Plan、`implementation_design`、`tdd_evidence` |
| integration-test | `test-generator` | 全部 Scope Story TDD 完成后的集成报告 |

**Story/Scope 修订**：用户要改故事拆分、故事点或 Scope → 路由 `task-splitter` 或列待确认项找用户；禁止擅自推荐 A/B/C 方案。

1. 输出结构化结果（见下方格式）。
2. 进度不足时要求用户补充。

## 输出格式

```markdown
## 续做：[任务标题]

**Plan**：`Plans/...`
**Epic**：`Plans/Epic/...`（如有）
**阶段**：由 workflow-gate 派生（如 requirement / architecture / story-split / story-development / integration-test / done）
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
/resume plan=Plans/功能开发/2026-06-11-会员-首次启动与过期处理.md 进度=US-002 Green 已通过，等待 Refactor

```
