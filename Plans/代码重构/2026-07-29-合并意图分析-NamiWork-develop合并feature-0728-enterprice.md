---
tags: [工作流, merge-code]
type: plan
category: 代码重构
status: 已采纳
p0_open: 0
date: 2026-07-29
workflow: merge-code
workflow_stage: intent-analysis
skill: merge-code-assistant
---

# 双边代码意图与业务冲突分析：NamiWork-develop合并feature-0728-enterprice

**工作流**：`merge-code`
**阶段**：`intent-analysis` / 双边代码意图与业务冲突分析
**推荐 Skill**：`merge-code-assistant`
**存放路径**：`Plans/代码重构/2026-07-29-合并意图分析-NamiWork-develop合并feature-0728-enterprice.md`

---

## 一、输入

- 来源：用户要求从本地 `develop` 新建临时分支，再合入仓库实际分支 `feature/0728/enterprice`，且不创建远端分支。
- 范围：分析 merge-base `822d346c7c550dd21e9b18a40e3301a43b4d67da` 到目标 `develop@bff763d4` 与源 `feature/0728/enterprice@cac96053` 的提交、diff、调用方和测试；形成兼容并集合并策略。
- 非目标：不改变产品规则，不用整边覆盖解决冲突，不 push、不创建远端分支、不运行未获授权的 `xcodebuild`。

## 二、阶段产出

- [x] 双边代码意图
- [x] 业务冲突矩阵
- [x] 开发者决策清单
- [x] 合并策略与验证映射


## 双边代码意图

| 意图ID | 分支侧 | 文件/模块 | 代码变化 | 业务目标 | 行为/规则变化 | 证据 | 置信度 |
|---|---|---|---|---|---|---|---|
| TGT-01 | 目标侧 develop | ClawChat 输入选择、发送管线、Workflow | 新增输入选择状态、页面生命周期、发送参数快照和统一发送管线，并修改模型/模式/思考深度与消息队列调用 | 保证一次发送使用用户点击时的稳定输入快照，避免并发切换和旧状态串入 | 模型可用性校验、手选优先级、发送快照和队列重放成为统一约束 | `git log 822d346c..develop` 中 `56a3b12d`、`389fc952`、`0e623d4b`、`6e43200e`；相关 `NMWorkflowSendParametersTests`、`NMChatHistoryContractTests` | 高 |
| TGT-02 | 目标侧 develop | ClawChat 历史、运行时、项目 iPad Renderer handoff | 强化历史恢复、会话边界、运行时复用、跨设备隔离和 iPad 项目输入草稿交接 | 会话重进不丢消息、不串会话；项目列表与内容区切换时不误清草稿或错误接管 Renderer | 运行时按身份复用且重新校验；显式项目选择会丢弃旧 handoff，权威列表负责确认项目状态 | `git log 822d346c..develop` 中 `2953536d`、`ce4d8e98`、`94f3d03f`；`NMChatHistoryContractTests`、`NMIPadPlaceholderModuleProviderTests` | 高 |
| TGT-03 | 目标侧 develop | AppRating、CloudConfig、AppShell 与其他独立修复 | 合入引导评价、云控拆分、iPad AppShell 和编译修复等 develop 现行代码 | 保留 develop 当前已集成的横向功能与构建基线 | 企业功能不能回退或覆盖这些与企业分支无直接关系的现行实现 | `git log feature/0728/enterprice..develop` 的 20 个目标侧提交与 `git diff feature/0728/enterprice...develop` | 高 |
| SRC-01 | 源侧 feature/0728/enterprice | Login、NMEnterpriseAPI、Team、企业身份与资源 | 新增企业登录/拦截、企业 HTTP API、组织部门成员、权限、多语言和资源 | 支持企业账号登录、组织浏览、成员/专家权限等企业版完整入口 | 个人版与企业版按账号和企业身份隔离，企业接口使用独立契约 | `git log 822d346c..feature/0728/enterprice` 中 `62918d4f`、`e4df5c9d`、`8cd3db88`、`8ec78f41`、`a2768168`；新增 `NMTeam*Tests` | 高 |
| SRC-02 | 源侧 feature/0728/enterprice | GatewayAccess、连接池、ClawChat Runtime | 引入 `NMChatGatewayAccess`、个人/池化 Access、连接池和按 Gateway 隔离的 Runtime/EventDispatcher | 企业项目聊天绑定正确的企业 Gateway，同时个人聊天继续使用个人 Gateway | RPC、事件、历史、发送、中止、分享均应走页面绑定的 Gateway；相同 session 在不同 Gateway 不共享 Runtime | 新增 `NMChatGatewayAccess*`、`NMGatewayConnectionPool`；`NMChatHistoryContractTests.testRuntimeRegistryIsolatesSameSessionAcrossGateways`；提交 `f7bd3107`、`85adeaa5` | 高 |
| SRC-03 | 源侧 feature/0728/enterprice | Projects、iPad Projects、项目服务契约 | 拆分项目管理/会话/知识/专家服务，新增企业项目目录、Gateway 解析、成员页、会话绑定与权限模型 | 个人项目保持原体验，企业共享项目通过企业 Gateway 和企业权限访问 | 企业项目不可使用不完整的个人缓存；进入项目先解析 AccessContext；共享项目禁删并显示成员/权限 | `NMProjectPermission.swift`、`NMProjectChatEntryCoordinator.swift`、`NMEnterpriseProjectConversationLoader.swift`、`NMProjectsService.swift`；提交 `85adeaa5`、`1092ccd4`、`01ecbe12`、`386c2875` | 高 |
| SRC-04 | 源侧 feature/0728/enterprice | 分享、公开会话、专家编辑权限 | 新增企业会话公开入口、逐轮分享与做同款、专家权限编辑及对应 API/资源 | 企业用户可公开指定轮次，并管理企业专家和项目可见性 | 公开动作仅企业账号显示；附件和分享请求使用当前聊天绑定 Gateway；权限变更即时回显并可回滚 | 提交 `531a6550`、`9db5a126`、`5e0d5114`、`07fbe0a4`；`NMChatViewModel+ShareExport.swift`、`NMAgentEditPermissionCell.swift` | 高 |

## 业务冲突矩阵

| 冲突ID | 关联意图 | 冲突类型 | 业务影响 | AI结论 | 需开发者决策 | 决策ID |
|---|---|---|---|---|---|---|
| MC-001 | TGT-01 SRC-02 | 聊天模型与发送契约 | 目标侧要求按点击时快照校验和发送，源侧把 RPC 改为页面绑定 Gateway 并补充会话模型同步；若退回全局 Gateway 或绕过快照会串连接或发送错误模型 | 保留目标侧快照校验/发送管线，以源侧绑定 Gateway 替换全局 RPC；仅保留不绕过快照规则的会话模型同步，属于可验证兼容并集 | 否 | 无 |
| MC-002 | TGT-01 TGT-02 SRC-02 SRC-03 | 新会话身份与生命周期 | 双方同时重写新会话创建、sessionKey/sessionId 提升、Dispatcher 注册和重试；错误组合会重复建会话、丢 pending send 或跨 Gateway 串台 | 以目标侧统一 new-conversation pipeline、delivery identity 和重试围栏为主，注入源侧 Gateway 与项目会话创建能力，保持一次身份提升和一次 pending 重放 | 否 | 无 |
| MC-003 | TGT-02 SRC-03 | 项目导航与 iPad 状态机 | 源侧改为 `NMProjectListItem`、企业 AccessContext 和异步选项解析；目标侧维护 Renderer handoff、草稿和显式选择状态；任一整边覆盖都会丢企业入口或丢草稿 | 在源侧企业项目结构上保留目标侧 handoff/draft 状态机与输入选择快照，项目切换同时取消旧企业解析任务和旧 Renderer 等待，行为可形成向后兼容并集 | 否 | 无 |
| MC-004 | TGT-01 SRC-03 | 项目输入模型与创建任务 | 目标侧手选模型优先且发送时捕获快照，源侧从项目 Gateway 拉智能体模型并将 prompt/model/mentions 传入企业项目会话 | Gateway 模型只作为未手选时默认值；点击发送仍使用目标侧 `NMInputState` 快照，并通过源侧项目 session service 与绑定 Gateway 创建，避免默认值覆盖手选 | 否 | 无 |
| MC-005 | TGT-01 TGT-02 SRC-02 SRC-03 SRC-04 | 文本冲突与测试并集 | `git merge-tree` 显示 22 个共同修改文件，12 个文本冲突，涉及聊天、项目、Claw 编辑和测试；机械选边会删掉一侧行为 | 逐冲突保留两侧新增测试与调用链，工程文件/集合分支做结构性并集；以调用方、编译期类型和冲突标记扫描复核，不整边覆盖 | 否 | 无 |
| MC-006 | TGT-03 SRC-01 SRC-04 | 非交叉功能与资源并集 | AppRating/CloudConfig 与企业登录/组织/资源大多无同行冲突，但工程文件和本地化聚合可能遗漏引用 | Git 自动合并非交叉功能；人工复核工程文件、资源目录、本地化 JSON 和新增测试是否全部进入最终树 | 否 | 无 |

## 开发者决策清单

| 决策ID | 待决策问题 | 可选方案及影响 | 开发者结论 | 决策人 | 确认记录 | 状态 |
|---|---|---|---|---|---|---|
| 无 | 无需在两套互斥产品规则中选边 | 全部冲突均可依据分支提交、调用方和测试形成兼容并集；若合并现场出现新的互斥规则则退回本阶段 | 无需决策 | 不适用 | 用户明确要求将企业分支合入从 develop 创建的临时分支；本分析不改变两侧产品规则 | 无需决策 |

## 合并策略与验证映射

| 冲突ID | 处理策略 | 影响范围 | 验证场景 | 状态 |
|---|---|---|---|---|
| MC-001 | 保留 `NMChatTurnOptionsSnapshot` 可用模型门禁和 send pipeline；所有 RPC/断网检查改走 `handler.gateway`；模型订阅不得覆盖本次发送快照 | NMChatViewController、NMChatMessageSender、Workflow | 搜索不得在绑定 Gateway 的发送路径回退 `GatewayService.shared.activeRPC`；保留模型门禁与相关测试 | 已规划 |
| MC-002 | 合并目标侧 delivery identity、session promotion、重试/pending send 逻辑与源侧 gateway/project session 创建；更新 Dispatcher 只发生于最终身份 | NMChatNetworkHandler、NMChatMessageSender、Runtime、History | 检查新建个人/项目会话均设置 key/id；pending 消息只发送一次；相同 session 不同 Gateway 的 Runtime 测试保留 | 已规划 |
| MC-003 | 使用企业 `NMProjectListItem` 和 AccessContext 为数据骨架，移植 develop 的 Renderer handoff、草稿丢弃/接管和显式选择逻辑 | iPhone/iPad Projects Controller、Coordinator | 项目切换取消旧任务；企业/个人项目均可进入；显式切换不复用旧草稿；企业成员 Tab 仍存在 | 已规划 |
| MC-004 | 默认模型先遵守用户手选状态，未手选时再从绑定 Gateway/云控加载；创建任务传递冻结的 prompt/model/mentions | Project Detail、iPad Content、ViewModel、InputBar | 搜索手选优先标志仍被使用；创建会话参数来自同一 `NMInputState`；输入栏仅在成功交接后重置 | 已规划 |
| MC-005 | 逐文件解析冲突，保留双方测试方法；集合 section 使用源侧枚举结构并保留目标侧有效空 section 语义；所有文件清除标记 | 12 个预测文本冲突文件与 22 个共同修改文件 | `git diff --check`；`git status --short` 无 unmerged；`rg` 扫描冲突标记；检查测试方法和新增文件均存在 | 已规划 |
| MC-006 | 接受 Git 的非冲突并集，并复核工程文件、本地化和资源引用；不主动构建 | project.pbxproj、Localizations.json、Assets、独立模块 | `git diff --check`、祖先关系、merge commit 双亲；工程文件无冲突标记，新增资源和测试在最终树可见 | 已规划 |

## 三、完成门禁

- `childPlanExists`: True
- `status`: ['已采纳']
- `sectionsPresent`: True
- `mergeAnalysis`: True
- `skillRun`: True

> 完成阶段工作后，在本 plan 末尾追加 `skill_run`，再运行 `bash scripts/workflow-gate.sh --workflow merge-code --json`。

## 四、续做

```text
/resume plan=Plans/代码重构/2026-07-29-合并意图分析-NamiWork-develop合并feature-0728-enterprice.md 进度=【当前完成情况】
```

## 反馈（skill_run）

```yaml
skill_run:
  skill: merge-code-assistant
  plan: Plans/代码重构/2026-07-29-合并意图分析-NamiWork-develop合并feature-0728-enterprice.md
  date: 2026-07-29
  contexts_used:
    - path: Skills/merge_code_assistant.md
      utility: high
      reason: "用于拆分双边意图、业务冲突、决策权和验证映射。"
    - path: /Users/wanglongxiang/git/NamiWork/CLAUDE.md
      utility: high
      reason: "用于确认项目技术与验证边界。"
  contexts_missing:
    - path: 源分支关联 PR 或正式 PRD
      impact: "未提供外部需求链接；以提交历史、代码调用方和测试作为意图证据。"
  contexts_stale: []
```
