---
tags: [工作流, merge-code]
type: plan
category: 代码重构
status: 进行中
date: 2026-09-01
workflow: merge-code
workflow_stage: preflight
task_id: merge-code-2026-09-01-迁移-ARM-Simulator-修复
task_title: 迁移 ARM Simulator 修复
skill: merge-code-assistant
repository: /Users/wanglongxiang/git/NNamiWork
source_branch: main
target_branch: codex/test-fence-full-repo
source_sha: e42ea1f76d5fe16de66b5e8044bf4e37660e80d7
target_sha: ffcd9ae00
---

# 合并前预检：迁移 ARM Simulator 修复

**工作流**：`merge-code`
**阶段**：`preflight` / 合并前预检
**推荐 Skill**：`merge-code-assistant`
**存放路径**：`Plans/代码重构/2026-09-01-合并预检-迁移-ARM-Simulator-修复.md`

---

## 一、输入

- 来源：用户确认把 `main` 中提交 `e42ea1f76` 已解决的 ARM Simulator 兼容方案迁移到当前测试围栏分支。
- 范围：按用户最新确认迁移 `e42ea1f76` 整个提交，包括 SDK、登录、分享、推送、Simulator 适配与单元测试；同时保留当前 arm64-only 门禁改动。
- 非目标：不合入该提交之外的 `main` 后续提交，不 push、不改写历史。

## 二、阶段产出

- [x] 仓库：`/Users/wanglongxiang/git/NNamiWork`；源 `main@e42ea1f76`；目标 `codex/test-fence-full-repo@ffcd9ae00`。
- [x] merge-base：`3012a5cf5`；当前分支相对源提交领先 89、落后 4；用户已明确接受源提交包含的 SDK/业务变化，范围以整个提交为准。
- [x] 当前脏文件均为本任务已确认的 arm64-only 配置、runner、能力表和规范改动；迁移仅与 `Podfile`、工程文件发生已知交叉。
- [x] 源意图：Simulator 不链接 device-only `mars.framework`，改由 Simulator stub 提供最小日志符号，并在产物阶段移除真机-only framework。
- [x] 目标意图：全量测试只允许 arm64，禁止回退 x86；两者行为互补。
- [x] 策略：在隔离工作树完整 cherry-pick `e42ea1f76`，只对 `.gitignore`、登录控制器和 Workflow 测试的三处文本冲突做意图合并；随后叠加 arm64-only 门禁提交，验证后 fast-forward 当前分支。
- [x] 验证：脚本单测、`pod install --deployment`、arm64 增量 `xcodebuild test`、xcresult 逐测试耗时；任何下一处 SDK 兼容问题单独归因。
- [x] 回滚：迁移与 arm64-only 门禁保留为两个独立本地提交；不执行 reset/stash/强推。


## 三、完成门禁

- `childPlanExists`: True
- `skillRun`: True

> 完成阶段工作后，在本 plan 末尾追加 `skill_run`，再运行 `bash scripts/workflow-gate.sh --workflow merge-code --json`。

## 四、续做

```text
/resume plan=Plans/代码重构/2026-09-01-合并预检-迁移-ARM-Simulator-修复.md 进度=【当前完成情况】
```

## 反馈（skill_run）

```yaml
skill_run:
  skill: merge-code-assistant
  workflow_stage: preflight
  plan: Plans/代码重构/2026-09-01-合并预检-迁移-ARM-Simulator-修复.md
  date: 2026-09-01
  contexts_used:
    - path: /Users/wanglongxiang/git/NNamiWork
      utility: high
      reason: "确认当前分支、arm64-only 未提交改动和实际 mars 链接失败"
    - path: /Users/wanglongxiang/git/NNamiWork/NAMIWork.xcodeproj/project.pbxproj
      utility: high
      reason: "通过 git show e42ea1f76 还原既有 ARM Simulator 修复的工程配置、代码与测试"
  contexts_missing: []
  contexts_stale: []
  outcome: "按用户最新确认完整迁移 e42ea1f76，并在隔离工作树解决三处冲突后叠加 arm64-only 门禁"
  utility: high
  reason: "完整保留既有 ARM Simulator 修复所依赖的 SDK 与业务适配，同时不带入该提交之外的 main 历史"
```
