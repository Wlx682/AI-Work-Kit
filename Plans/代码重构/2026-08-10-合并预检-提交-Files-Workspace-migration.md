---
tags: [工作流, merge-code]
type: plan
category: 代码重构
status: 进行中
date: 2026-08-10
workflow: merge-code
workflow_stage: preflight
task_id: merge-code-2026-08-10-提交-Files-Workspace-migration
task_title: 提交 Files Workspace migration
skill: merge-code-assistant
---

# 合并前预检：提交 Files Workspace migration

**工作流**：`merge-code`
**阶段**：`preflight` / 合并前预检
**推荐 Skill**：`merge-code-assistant`
**存放路径**：`Plans/代码重构/2026-08-10-合并预检-提交-Files-Workspace-migration.md`

---

## 一、输入

- 来源：用户要求提交当前 Files / User Upload / AI Files / Workspace 迁移实现，若与最新 `origin/dev` 冲突则解决。
- 仓库：`/Users/wanglongxiang/git/namiwork-flutter`
- 目标分支：`dev` @ `c5190de9160eb7ad7f538a02f9ca902c1a8af7c3`
- 来源分支：`origin/dev` @ `27da2c192ff9bfd51d6c5578f26dfb842a230a2e`
- merge-base：`c5190de9160eb7ad7f538a02f9ca902c1a8af7c3`
- 领先/落后：本地 `0` / 远端 `41`
- 范围：先将本地 110 个改动/新增路径形成可回滚提交，再普通 merge 最新 `origin/dev`，保留双方业务意图并验证组合结果。
- 非目标：不 rebase、不 squash、不 force push、不删分支、不自动 push。

## 二、阶段产出

- [x] 已确认工作树无 `U` 状态文件，当前不存在未解决文本冲突。
- [x] 已执行 `git fetch origin`，固定源/目标 SHA 与 merge-base。
- [x] 已识别 17 个双边共同触达路径：主要是 app composition、personal-cloud owner/repository、l10n 生成物、app shell、`pubspec.yaml` 及对应测试。
- [x] 本地候选已通过 Files/Workspace 定向回归 `218/218`、格式、定向 analyze、命名门禁与 `git diff --check`。
- [x] 回滚方式：合并前本地功能提交可独立 revert；合并后若组合验证失败，不 push，保留现场继续修复。


## 三、完成门禁

- `childPlanExists`: True
- `skillRun`: True

> 完成阶段工作后，在本 plan 末尾追加 `skill_run`，再运行 `bash scripts/workflow-gate.sh --workflow merge-code --json`。

## 四、续做

```text
/resume plan=Plans/代码重构/2026-08-10-合并预检-提交-Files-Workspace-migration.md 进度=【当前完成情况】
```

## 反馈（skill_run）

```yaml
skill_run:
  skill: merge-code-assistant
  plan: Plans/代码重构/2026-08-10-合并预检-提交-Files-Workspace-migration.md
  date: 2026-08-10
  contexts_used:
    - path: Contexts/决策/Skill原子契约.md
      utility: high
      reason: 按可验证产物和阶段门禁约束记录 merge-code 预检证据
  contexts_missing: []
  contexts_stale: []
  outcome_status: pass
  revisit_needed: false
```
