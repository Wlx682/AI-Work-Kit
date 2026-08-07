# 开发流程审计 Skill

## 触发条件

当用户说以下任一时执行 —— 包含口语化变体，PM 日常说法即可：

- **正式词**：「开发流程审计」「Epic 审计」「dev-lifecycle-audit」「检查 Epic 进度真实性」
- **口语变体**：「**检查 Epic 进度**」「**审计版本状态**」「**这个 Epic 做完了吗**」「**这个需求做完了吗**」「**这个版本做的咋样了**」「**真不真实**」
- `/dev-lifecycle-audit` 命令

**不响应（让位给其他 Skill）**：

- 「日报 / 周报 / 项目复盘」→ `report-assistant`
- 「需求变更影响」→ `change-impact-analysis`


## 执行

1. 运行 `./scripts/dev-lifecycle-audit-collect.sh Plans/Epic` 获取 Epic / 子 plan / 门禁 / Story Scope 机械证据。
2. 按五维度独立判定（可并行思考，不必真开 5 个 agent 除非跑 Claude workflow）：
   - **A** Epic 元信息：`epic_id`、`lifecycle_state`、`plans:` 与子 plan 文件一致
   - **B** 需求：`p0_open=0`、需求 plan 存在且非空、status 与阶段匹配
   - **C** 方案：`含业务逻辑=是` → 技术方案 plan 存在且 `status: 已采纳`
   - **D** Story：`.stories.json` Scope、Story 子 Plan 与 `tdd_evidence` 和 `lifecycle_state` / gate 派生阶段一致；开发阶段 `plan-gate-check.sh` 须 OK
   - **E** 测试/部署：gate 已通过 story-development 后，`integration-test-plan` 应存在；进入 `integration-test` 前还须有测试审核人、审核时间、目标 commit、用例索引 SHA-256 与零未解决意见；执行阶段须引用该已审核计划
3. **写入** `Contexts/决策/YYYY-MM-DD-开发流程审计报告.md`（用户未禁止写回时）。
4. 回复：报告路径 + 一句话 summary + 每个 Epic 最严重 1 条待办。

## verdict

| 情况                                           | 判定   |
| :------------------------------------------- | ---- |
| lifecycle=development 但 gate BLOCKED 或缺需求/方案 | 严重矛盾 |
| Story/Scope 与阶段略有不符、尚未到测试阶段时缺测试计划 | 轻微偏差 |
| 已进入 integration-test 但测试计划未审核，或执行引用的用例版本已漂移 | 严重矛盾 |
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
