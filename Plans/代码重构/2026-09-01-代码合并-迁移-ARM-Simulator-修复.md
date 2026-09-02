---
tags: [工作流, merge-code]
type: plan
category: 代码重构
status: 已完成
date: 2026-09-01
workflow: merge-code
workflow_stage: merge
task_id: merge-code-2026-09-01-迁移-ARM-Simulator-修复
task_title: 迁移 ARM Simulator 修复
skill: merge-code-assistant
---

# 代码合并与冲突处理：迁移 ARM Simulator 修复

**工作流**：`merge-code`
**阶段**：`merge` / 代码合并与冲突处理
**推荐 Skill**：`merge-code-assistant`
**存放路径**：`Plans/代码重构/2026-09-01-代码合并-迁移-ARM-Simulator-修复.md`

---

## 一、输入

- 来源：用户确认完整迁移 `main` 的 `e42ea1f76`，并要求今后测试固定不使用 x86。
- 范围：完整迁移源提交、解决与当前分支的冲突、叠加 arm64-only 固定配置并验证。
- 非目标：不合入源提交之外的 `main` 历史，不 push、不改写历史；不在本次迁移中修复既有业务测试断言。

## 二、阶段产出

- [x] 决策落实记录
- [x] 验证记录
- [x] 合并结果


## 决策落实记录

| 追踪ID | 影响文件 | 落实方式 | 验证用例 | 状态 |
|---|---|---|---|---|
| D-001 | 源提交全部 467 个文件变化 | 隔离工作树完整 cherry-pick `e42ea1f76`，不纳入源提交之外历史 | 提交范围核对；完整 arm64 XCTest | 已落实 |
| MC-001 | `NAMIWork.xcodeproj/project.pbxproj`、`Podfile`、XCTest runner 与能力表 | 固定 `EXCLUDED_ARCHS=x86_64`；runner 强制 `ARCHS=arm64 ONLY_ACTIVE_ARCH=YES` 并拒绝 x86 destination/制品 | runner 13 项测试；xcresult device architecture | 已落实 |
| MC-002 | `.gitignore`、`NMLoginViewController.m`、`NMWorkflowSessionCoordinatorTests.swift` | `.gitignore` 取并集；登录采用源业务意图并保留目标 debug 围栏；测试采用源显式 payload 类型并保留目标后续内容 | `git diff --check`；完整编译与 XCTest | 已落实 |
| MC-003 | QUC、登录、分享、推送、Pods 与测试资产 | 按 D-001 完整迁移并以 `df942130c` 独立记录 | 7 组构建脚本测试；`pod install --deployment`；arm64 XCTest | 已落实 |

## 验证记录

- `pod install --deployment`：通过；50 个依赖、69 个 Pod；mars xcconfig 与 QUC archive patch 均执行成功。
- 构建脚本测试：mars、device-only framework、QUC XCFramework、WeChat XCFramework、QUC one-login、运营商 SDK 清理、QHPush Simulator 共 7 组全部通过。
- arm64 门禁 runner：13 项测试通过；Ruby 语法与 `git diff --check` 通过。
- 完整 XCTest：iPhone 17 / iOS 26.5 Simulator / `arm64`；1109 条，1090 通过、18 条测试失败、1 条跳过；测试执行 13.959 秒，测试阶段 44.267 秒，冷构建至结束 307.771 秒。
- 失败聚类：首次 iPhone 全量运行的 18 条失败中，16 条 `NMIPadAppShellTests` 在 arm64 iPad 定向重跑全部通过，确认属于设备族不匹配；剩余 Phone App Shell、Web Preview Share 各 1 条在 iPad 重跑仍失败。两条对应的测试和生产模块均不在迁移提交变更路径内；mars 与 SDK 架构链接阻塞已解除。

## 合并结果

- 当前分支 `codex/test-fence-full-repo` 已迁移到 `27d720224`。
- 完整源提交迁移：`df942130c`。
- arm64-only 固定配置：`e2c6bb759`。
- XCTest target 补强：`27d720224`，Debug/Release 均显式排除 x86_64。
- 工作树干净，未 push。

## 三、完成门禁

- `childPlanExists`: True
- `sectionsPresent`: True
- `mergeDecisionTraceability`: intent-analysis
- `skillRun`: True

> 完成阶段工作后，在本 plan 末尾追加 `skill_run`，再运行 `bash scripts/workflow-gate.sh --workflow merge-code --json`。

## 四、续做

```text
/resume plan=Plans/代码重构/2026-09-01-代码合并-迁移-ARM-Simulator-修复.md 进度=【当前完成情况】
```

## 反馈（skill_run）

```yaml
skill_run:
  skill: merge-code-assistant
  workflow_stage: merge
  plan: Plans/代码重构/2026-09-01-代码合并-迁移-ARM-Simulator-修复.md
  date: 2026-09-01
  contexts_used:
    - path: /Users/wanglongxiang/git/NNamiWork
      utility: high
      reason: "隔离迁移、冲突处理、arm64 构建和 XCTest 验证"
    - path: /tmp/nami-port-e42.wRnpKL/NAMIWorkTests.xcresult
      utility: high
      reason: "确认执行架构、逐测试耗时与失败聚类"
  contexts_missing: []
  contexts_stale: []
  outcome: "完整源提交、arm64-only 固定配置与 XCTest target 补强已作为可追溯提交合入当前分支"
  utility: high
  reason: "同时解决既有 ARM Simulator 架构阻塞，并防止未来测试回退 x86"
```
