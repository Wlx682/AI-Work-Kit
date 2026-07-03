---
name: deployment-assistant
description: 读 Epic+技术方案与测试 plan，生成部署检查清单到 Plans/部署/，并回写 Epic plans.deploy + WBS 13–14。触发词：部署、上线、deployment-assistant。
---

# 部署助手

模板：`Templates/部署模板.md` · 参考 `Templates/发布检查清单模板.md`  
输入：Epic `plans.*`（architecture / development / test）  
产出：`Plans/部署/`；frontmatter 保留 `lifecycle_state: deploy` 仅作兼容展示，阶段以 `workflow-gate.sh` 派生为准。

## 执行步骤

1. 读 Epic frontmatter `workflow:` 与子 Plan 索引；运行 `workflow-gate.sh --workflow client-dev --epic <epic>`，确认已进入 `deploy` 或明确用户要准备发布材料。
2. 读技术方案（迁移、环境、回滚）与自动化测试 plan 通过门槛。
3. 按模板输出：环境变量、迁移、灰度、回滚、冒烟（链需求 AC）。
4. Plan → `Plans/部署/YYYY-MM-DD-模块名.md`；frontmatter 含 `epic:`、`lifecycle_state: deploy`。
5. **回写 Epic**（硬规则）：
   - frontmatter `plans.deploy: Plans/部署/xxx.md`
   - §一 子 Plan 索引表 deploy 行
   - 指引 WBS 13（发布检查）、14（线上冒烟）执行项
6. 测试未通过 → 警告，用户确认后可继续

## 门禁

- 缺技术方案 → 停止，引导 `architecture-design-assistant`
- `workflow-gate.sh --workflow client-dev` 在 deploy 阶段检查部署 plan 与 WBS 13–14；不通过修改 `lifecycle_state` 推进阶段

## 上下文汇报

```
📌 当前阶段：[deploy] | 产出：Plans/部署/xxx.md | Epic plans.deploy 已更新 | 下一阶段：[retro / retro-assistant] | 中断：/resume plan=...
```

同步：`Skills/deployment_assistant.md`

## 反馈回路（skill_run）

完成任务的最后一步**必须**输出 `skill_run` 反馈（协议：`Contexts/决策/Skill反馈协议.md`）：
追加到本次 部署 plan（`Plans/部署/`） **末尾**的 `## 反馈（skill_run）` 节（fenced ```yaml`，非裸 frontmatter）。
`contexts_used[].utility` 二选一：`high`（附一句话 `reason`）或 `not-needed`；必填 `skill: deployment-assistant` / `plan` / `date` / `contexts_used` / `contexts_missing` / `contexts_stale`。缺则 `plan-gate-check.sh` 报失败。
