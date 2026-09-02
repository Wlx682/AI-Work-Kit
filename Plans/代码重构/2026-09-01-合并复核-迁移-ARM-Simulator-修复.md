---
tags: [工作流, merge-code, code-review]
type: plan
category: 代码重构
status: 需修改
p0_open: 1
date: 2026-09-01
workflow: merge-code
workflow_stage: review
task_id: merge-code-2026-09-01-迁移-ARM-Simulator-修复
task_title: 迁移 ARM Simulator 修复
skill: code-review
---

# 合并结果复核：迁移 ARM Simulator 修复

**工作流**：`merge-code`
**阶段**：`review` / 合并结果复核
**推荐 Skill**：`code-review`
**存放路径**：`Plans/代码重构/2026-09-01-合并复核-迁移-ARM-Simulator-修复.md`

---

## 一、输入

- 来源：复核当前分支 `codex/test-fence-full-repo` 的 `df942130c`（完整迁移）、`e2c6bb759`（arm64-only 固定配置）与 `27d720224`（XCTest target 补强）。
- 范围：源/目标意图、MC-001～MC-003、D-001、三处冲突解析、SDK/Pods 组合、arm64 XCTest 与耗时证据。
- 非目标：不在 review 阶段直接修复迁移提交未触及的 App Shell 或 Web Preview 测试。

## 二、阶段产出

- [x] Findings-first 复核结论
- [x] 双边意图与冲突追踪核对
- [x] 测试缺口和残余风险记录

## 三、Findings-first

### 阻塞

1. **全量回归仍有 2 条可复现失败，当前不能给出“全量测试通过”的合并结论。**
   - `NAMIWorkTests/AppShell/NMPhoneAppShellRegressionTests.swift:77-78`：`accessibilityActivate()` 返回 false，选中项保持 `.home` 而非 `.profile`。
   - `NAMIWorkTests/NMWebPreviewShareNavigationTitleDirectContractTests.swift:28-29`：关闭按钮激活失败，`onDismiss` 未触发。
   - 首次 iPhone arm64 全量执行为 1109 条、1090 通过、18 失败、1 跳过；其中 16 条 iPad Shell 失败在 iPad arm64 定向重跑全部通过，剩余上述 2 条在 iPad 上仍失败。
   - 两个测试文件及对应 App Shell/Web Preview 生产模块均不在 `df942130c` 的变更路径内，因此没有证据把它们归因为本次 SDK/ARM 迁移；但在缺少可运行的迁移前 arm64 基线时，也不能机械宣告它们是既有失败。建议进入独立 bugfix/测试诊断流程。

### 高 / 中

- 未发现迁移特有的高、中优先级代码问题。

### 建议

- 源提交携带的 QUC XCFramework vendor headers 含既有尾随空白，`git diff --check ffcd9ae00..e2c6bb759` 会报告这些第三方文件；不建议为格式单独修改签入 SDK 内容。

## 四、双边意图与冲突追踪

| 检查项 | 结论 | 证据 |
|---|---|---|
| D-001 完整迁移整个提交 | 已落实 | 源与迁移提交均涉及 602 个路径，路径集合一致；迁移提交为 `df942130c` |
| MC-001 arm64-only 与源 Simulator 兼容 | 已落实 | `e2c6bb759` 固定 runner/Pods/App，`27d720224` 补齐 XCTest Debug/Release 的 x86 排除；runner 13 项测试通过；两个 xcresult 均显示 `architecture=arm64` |
| MC-002 三处文本冲突 | 已落实 | `.gitignore` 取并集；登录保留源 SMS/退役一键登录与目标 debug 围栏；Workflow 测试保留目标内容并使用源显式 payload 类型；完整编译通过 |
| MC-003 SDK/业务范围 | 已落实 | QUC、WeChat、ReactiveObjC、登录/分享/推送与脚本均完整迁入；`pod install --deployment` 和 7 组构建脚本测试通过 |
| 源意图 SI-001/SI-002 | 已保留 | mars Simulator stub 生效；device-only framework 清理测试通过；真机分支脚本断言保持 |
| 目标意图 TI-001/TI-002 | 已保留 | 当前围栏资产未丢失；执行命令固定 arm64 并拒绝 x86 destination/制品 |

## 五、验证与残余风险

- arm64 iPhone 冷构建成功，mars device-only 链接错误已消失；测试执行 13.959 秒，测试阶段 44.267 秒，冷构建至结束 307.771 秒。
- arm64 iPad 定向重跑：18 条中 16 条 iPad Shell 通过，2 条跨设备仍失败。
- 未做真实账号下的登录、微信分享、推送端到端验证，也未做 iphoneos 真机安装；当前真机行为证据来自脚本分支测试和编译配置。
- 工作树干净，未 push；迁移与 arm64-only 设置为两个独立提交，便于回滚。

## 六、结论

- [ ] 通过
- [x] 修改后通过
- [ ] 需讨论

结论：**迁移范围、冲突解析与 arm64-only 固定配置复核通过；全量回归结论因 2 条未归因失败保持阻塞。**

## 七、关联材料

- 合并意图分析：`Plans/代码重构/2026-09-01-合并意图分析-迁移-ARM-Simulator-修复.md`
- 代码合并：`Plans/代码重构/2026-09-01-代码合并-迁移-ARM-Simulator-修复.md`

## 反馈（skill_run）

```yaml
skill_run:
  skill: code-review
  plan: Plans/代码重构/2026-09-01-合并复核-迁移-ARM-Simulator-修复.md
  date: 2026-09-01
  contexts_used:
    - path: Contexts/决策/Skill原子契约.md
      utility: high
      reason: "按 findings-first、行号证据和 merge-code 双边意图追踪要求完成复核"
  contexts_missing: []
  contexts_stale: []
  outcome_status: partial
  revisit_needed: false
  friction: "迁移前分支因 mars 架构链接失败无法形成可比较的 arm64 全量测试基线"
```
