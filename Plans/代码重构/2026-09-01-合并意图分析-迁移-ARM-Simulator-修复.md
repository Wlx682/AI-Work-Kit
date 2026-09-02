---
tags: [工作流, merge-code]
type: plan
category: 代码重构
status: 已采纳
p0_open: 0
date: 2026-09-01
workflow: merge-code
workflow_stage: intent-analysis
task_id: merge-code-2026-09-01-迁移-ARM-Simulator-修复
task_title: 迁移 ARM Simulator 修复
skill: merge-code-assistant
repository: /Users/wanglongxiang/git/NNamiWork
source_branch: main
target_branch: codex/test-fence-full-repo
source_sha: e42ea1f76d5fe16de66b5e8044bf4e37660e80d7
target_sha: ffcd9ae00
---

# 双边代码意图与业务冲突分析：迁移 ARM Simulator 修复

**工作流**：`merge-code`
**阶段**：`intent-analysis` / 双边代码意图与业务冲突分析
**推荐 Skill**：`merge-code-assistant`
**存放路径**：`Plans/代码重构/2026-09-01-合并意图分析-迁移-ARM-Simulator-修复.md`

---

## 一、输入

- 来源：用户要求迁移 `e42ea1f76` 中已经解决过的 ARM Simulator 兼容方案。
- 范围：用户明确要求迁移 `e42ea1f76` 整个提交，覆盖 SDK 二进制、登录、分享、推送、Simulator 适配和对应测试，并保留目标分支 arm64-only 门禁。
- 非目标：不迁移该提交之外的 `main` 历史，不 push、不改写历史。

## 二、阶段产出

- [x] 双边代码意图
- [x] 业务冲突矩阵
- [x] 开发者决策清单
- [x] 合并策略与验证映射


## 双边代码意图

| 意图ID | 分支侧 | 文件/模块 | 代码变化 | 业务目标 | 行为/规则变化 | 证据 | 置信度 |
|---|---|---|---|---|---|---|---|
| SI-001 | 源提交 | `NMMarsSimulatorStub.mm`、Pod xcconfig patcher | Simulator 不链接 device-only mars，最小 stub 提供 BRLogModule 需要的符号；真机继续链接 mars | 恢复 Apple Silicon Simulator 构建 | Simulator 改走日志 stub，真机 mars 日志行为不变 | `e42ea1f76`；patcher 单测 | 高 |
| SI-002 | 源提交 | device-only framework 清理脚本、工程 build phase | Simulator 产品移除 IJK/Holmes/ogg，真机保留 | 避免错误平台 framework 污染 Simulator 产品 | 仅 Simulator 清理，iphoneos 产品保持原样 | `e42ea1f76`；清理脚本单测 | 高 |
| TI-001 | 目标分支 | Xcode/Podfile、XCTest runner、能力表 | Simulator/XCTest 固定 arm64，显式拒绝 x86 及历史制品 | 防止测试再次回退 x86 | x86 destination/DerivedData/xctestrun 在执行前失败 | 当前工作树 diff；13 项 runner 测试 | 高 |
| TI-002 | 目标分支 | 大量测试围栏资产 | 保留当前分支 89 个围栏提交和冻结契约 | 维持测试分母及证据可追溯性 | 不用业务 SDK 大迁移覆盖当前测试资产 | `HEAD@ffcd9ae00` | 高 |

## 业务冲突矩阵

| 冲突ID | 关联意图 | 冲突类型 | 业务影响 | AI结论 | 需开发者决策 | 决策ID |
|---|---|---|---|---|---|---|
| MC-001 | SI-001, TI-001 | 架构设置 | 源提交清空 Simulator 排除项，目标明确排除 x86 | 保留目标 `EXCLUDED_ARCHS=x86_64`；与源允许 arm64 的目标一致且更严格 | 否 | 无 |
| MC-002 | SI-001, TI-002 | 工程/Podfile 同文件不同历史 | 完整 cherry-pick 与后续围栏代码存在三处文本冲突 | 逐处按双边意图合并，保留目标后续围栏行为并完整纳入源提交其余内容 | 否 | 无 |
| MC-003 | SI-002, TI-002 | SDK 范围 | 源提交包含大规模 QUC/登录/分享 SDK 迁移 | 需开发者决策：选择性移植或完整迁移会产生不同业务范围；用户已通过 D-001 明确选择完整迁移 | 是 | D-001 |

## 开发者决策清单

| 决策ID | 待决策问题 | 可选方案及影响 | 开发者结论 | 决策人 | 确认记录 | 状态 |
|---|---|---|---|---|---|---|
| D-001 | 是否完整迁移源提交 | 选择性移植风险较小；完整迁移能保留该修复的 SDK 与业务依赖闭环 | 完整迁移 `e42ea1f76` 整个提交 | 用户 | 2026-09-01：用户明确“整个commit都应该迁移过来” | 已决策 |

## 合并策略与验证映射

| 冲突ID | 处理策略 | 影响范围 | 验证场景 | 状态 |
|---|---|---|---|---|
| MC-001 | 保留 arm64-only/x86 排除，Pod patcher 仅条件化 mars | `Podfile`、Pods xcconfig | `pod install --deployment`；检查 Simulator/iphoneos flags | 已规划 |
| MC-002 | 隔离工作树完整 cherry-pick；三处冲突分别采用并集、源登录行为+目标围栏、源显式类型+目标后续测试 | `.gitignore`、登录控制器、Workflow 测试 | `git diff --check`、脚本测试、完整 arm64 build/test | 已规划 |
| MC-003 | 落实 D-001，完整迁移源提交全部 467 个文件变化，不纳入源提交之外历史 | QUC、登录、分享、推送、Pods、测试资产 | `pod install --deployment`、SDK 脚本测试、arm64 XCTest | 已规划 |

## 三、完成门禁

- `childPlanExists`: True
- `status`: ['已采纳']
- `sectionsPresent`: True
- `mergeAnalysis`: True
- `skillRun`: True

> 完成阶段工作后，在本 plan 末尾追加 `skill_run`，再运行 `bash scripts/workflow-gate.sh --workflow merge-code --json`。

## 四、续做

```text
/resume plan=Plans/代码重构/2026-09-01-合并意图分析-迁移-ARM-Simulator-修复.md 进度=【当前完成情况】
```

## 反馈（skill_run）

```yaml
skill_run:
  skill: merge-code-assistant
  workflow_stage: intent-analysis
  plan: Plans/代码重构/2026-09-01-合并意图分析-迁移-ARM-Simulator-修复.md
  date: 2026-09-01
  contexts_used:
    - path: /Users/wanglongxiang/git/NNamiWork/Podfile
      utility: high
      reason: "确认目标 arm64-only 设置和 Pod post_install 交叉点"
    - path: /Users/wanglongxiang/git/NNamiWork/NAMIWork.xcodeproj/project.pbxproj
      utility: high
      reason: "对比源提交与目标工程结构，限定最小移植项"
  contexts_missing: []
  contexts_stale: []
  outcome: "按 D-001 完整迁移源提交；三处文本冲突与 arm64-only 设置均有可追溯处理策略"
  utility: high
  reason: "完整保留源修复依赖闭环，并把用户要求、冲突处理和验证证据一一映射"
```
