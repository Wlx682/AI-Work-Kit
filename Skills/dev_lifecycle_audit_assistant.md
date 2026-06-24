# 开发流程审计 Skill

当用户说「开发流程审计」「Epic 审计」「dev-lifecycle-audit」「检查 Epic 进度真实性」时执行。

> 对标 `learning-audit`：机械脚本 + 多维度交叉比对 → 决策文档。

## 执行

1. 运行 `./scripts/dev-lifecycle-audit-collect.sh Plans/Epic` 获取 Epic / 子 plan / 门禁 / WBS 机械证据。
2. 按五维度独立判定（可并行思考，不必真开 5 个 agent 除非跑 Claude workflow）：
   - **A** Epic 元信息：`epic_id`、`lifecycle_state`、`plans:` 与子 plan 文件一致
   - **B** 需求：`p0_open=0`、需求 plan 存在且非空、status 与阶段匹配
   - **C** 方案：`含业务逻辑=是` → 技术方案 plan 存在且 `status: 已采纳`
   - **D** WBS：`wbs_done_total` 与 `lifecycle_state` 一致；`plan-gate-check.sh` 须 OK（开发阶段）
   - **E** 测试/部署：lifecycle 进入 test/deploy 时对应 plan 应存在
3. **写入** `Contexts/决策/YYYY-MM-DD-开发流程审计报告.md`（用户未禁止写回时）。
4. 回复：报告路径 + 一句话 summary + 每个 Epic 最严重 1 条待办。

## verdict

| 情况                                           | 判定   |
| :------------------------------------------- | ---- |
| lifecycle=development 但 gate BLOCKED 或缺需求/方案 | 严重矛盾 |
| WBS 与阶段略有不符、缺 test plan 但未到 test 阶段          | 轻微偏差 |
| 机械证据与声称一致                                    | 一致   |

## Claude Code workflow

```
/workflow dev-lifecycle-audit
```

脚本：`.claude/workflows/dev-lifecycle-audit.js`

## 触发示例

```
/dev-lifecycle-audit 审计试点 Epic
审计一下 Plans/Epic/ 全流程进度
```
