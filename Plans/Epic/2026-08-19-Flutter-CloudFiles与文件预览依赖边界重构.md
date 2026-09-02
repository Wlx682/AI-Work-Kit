---
tags: [Epic, client-dev, Flutter, Files, CloudFiles, 文件预览, 架构重构]
type: plan
category: Epic
status: 已归档
date: 2026-08-19
epic_id: flutter-cloud-files-preview-boundary-refactor
workflow: client-dev
lifecycle_state: integration-test
platform: 客户端
repo: namiwork-flutter
branch: dev
p0_open: 0
plans:
  requirement: Plans/需求分析/2026-08-19-Flutter-CloudFiles与文件预览依赖边界重构.md
  prioritization: Plans/需求排序/2026-08-19-Flutter-CloudFiles与文件预览依赖边界重构.md
  architecture: Plans/技术方案/2026-08-19-Flutter-CloudFiles与文件预览依赖边界重构.md
  development: Plans/功能开发/2026-08-19-Flutter-CloudFiles与文件预览依赖边界重构.md
  integration_plan: Plans/自动化测试/2026-08-19-Flutter-CloudFiles与文件预览依赖边界重构-集成测试计划.md
  integration: Plans/自动化测试/2026-08-19-Flutter-CloudFiles与文件预览依赖边界重构-集成测试.md
relations:
  depends_on:
    - Templates/模板约定.md
    - Templates/需求排序模板.md
    - Templates/技术方案模板.md
    - Templates/客户端功能开发模板.md
    - Templates/集成测试计划模板.md
    - Templates/集成测试模板.md
  dependents: []
  supersedes: []
  superseded_by: []
  conflicts: []
---

# Epic：Flutter CloudFiles 与文件预览依赖边界重构（client-dev）

**创建日期**：2026-08-19
**关联仓库**：`namiwork-flutter` · **分支**：`dev`

> 本 Epic 收敛 Cloud Files、Files 宿主和统一文件预览的 App composition 边界：消除 Feature → App 反向依赖与 composition 循环，保留 environment/account/workspace/session/generation owner 围栏和现有产品行为。

## 一、Epic 范围

### 目标

- 将“Provider 定义、Feature 契约、App 生产实现”拆成单向依赖。
- `lib/features/**` 不再 import `lib/app/**`，Files 通过宿主注入消费窄契约。
- `lib/app/composition/**` 不再反向 import `composition_root.dart`。
- 保留 Cloud Files 认证、签名、上传/下载、预览、owner 换代和资源释放语义。
- 将任务治理口径从“进入 `composition_root.dart`”修正为“由对应 App composition module 完成生产装配”。

### 不做

- 不改变云盘 HTTP/Gateway 协议、签名参数、缓存 namespace 或持久化格式。
- 不新增云盘、下载、上传或预览功能。
- 不改变 Files 三 Tab 交互、页面视觉或 Android/iOS 平台预览选择。
- 不在本 Epic 中处理 InputBar 或其他并行功能改动。

## 二、阶段索引

| 阶段 | stage key | Plan | 状态 |
|------|-----------|------|------|
| 需求分析 | requirement | `Plans/需求分析/2026-08-19-Flutter-CloudFiles与文件预览依赖边界重构.md` | ✅ 已采纳 |
| 需求排序 | prioritization | `Plans/需求排序/2026-08-19-Flutter-CloudFiles与文件预览依赖边界重构.md` | ✅ 已采纳 |
| 正式架构设计 | architecture | `Plans/技术方案/2026-08-19-Flutter-CloudFiles与文件预览依赖边界重构.md` | ✅ 已采纳 |
| 功能故事拆分与故事点 | story-split | `Plans/功能开发/2026-08-19-Flutter-CloudFiles与文件预览依赖边界重构.md` | ✅ 已拆分（7 故事 / 39 点，story-scope 通过） |
| 实现落点设计 | implementation-design | 同上及动态故事子 Plan | ✅ 7/7 完成 |
| 逐故事 TDD | story-development | 同上及动态故事子 Plan | ✅ 7/7 完成 |
| 集成测试计划与审核 | integration-test-plan | `Plans/自动化测试/2026-08-19-Flutter-CloudFiles与文件预览依赖边界重构-集成测试计划.md` | ✅ 8 用例已审核 |
| 全量集成测试 | integration-test | `Plans/自动化测试/2026-08-19-Flutter-CloudFiles与文件预览依赖边界重构-集成测试.md` | 🟡 PARTIAL：自动化全绿，设备矩阵阻塞 |

## 三、阶段门禁

| 阶段 | 退出条件 |
|------|----------|
| requirement | 需求已采纳、P0=0、边界/异常/AC 齐全 |
| prioritization | Backlog 价值/紧迫度/依赖/优先级/依据齐全且团队确认 |
| architecture | 模块、模型、内部 Port、NFR、ADR、需求影响矩阵齐全并已采纳 |
| story-split | 每个 Scope 故事可独立验收、有故事点、AC 和架构引用 |
| implementation-design | 每个 Scope 故事有实现落点 JSON，明确代码证据、目标文件、分层边界和 Red 测试位置 |
| story-development | 每个 Scope 故事 Red/Green/Refactor/冒烟/AC 证据齐全 |
| integration-test-plan | Scope 内每个 Story/AC 都有结构化测试用例；测试审核通过且审核证据与用例版本一致 |
| integration-test | 当前目标 commit 的全量集成报告通过；随后直接 Done |

## 四、动态用户故事看板

故事真理源：`Plans/功能开发/2026-08-19-Flutter-CloudFiles与文件预览依赖边界重构.stories.json`；点数字段为 `story_points`。

| Story | 用户能力 | 优先级 | 点数 | Scope | 依赖 | 状态 |
|-------|----------|--------|------|-------|------|------|
| US-CFR-001 | 边界与行为不变量回归网（先红后绿基线） | P0 | 5 | ✅ | — | ✅ 已完成 |
| US-CFR-002 | 单向 App composition 装配链（Files 模块不反向 import root） | P0 | 5 | ✅ | US-CFR-001 | ✅ 已完成 |
| US-CFR-003 | 分离 CloudFilesAppRuntime 与 CloudFilesFeatureRuntime | P0 | 8 | ✅ | US-CFR-001,002 | ✅ 已完成 |
| US-CFR-004 | Files 页面消费 Host 注入的窄依赖并去 app import | P0 | 8 | ✅ | US-CFR-003 | ✅ 已完成 |
| US-CFR-005 | 文件预览 Feature 归位与 typed host actions | P0 | 8 | ✅ | US-CFR-003,004 | ✅ 已完成 |
| US-CFR-006 | 迁移 Main/Projects/Download 消费者并闭合生命周期 | P0 | 5 | ✅ | US-CFR-003,004,005 | ✅ 已完成 |
| US-CFR-007 | 固化 Provider 装配规则与边界回归门禁 | P1 | 3 | ✅ | US-CFR-001..006 | ✅ 已完成 |

> 故事卡片由看板从 `.stories.json` 与子 Plan 派生；禁止把 UI、Domain、Data/API 分别作为交付故事。故事点不换算工时或个人绩效。

## 五、当前进度快照（2026-08-21）

### 已完成基线（本 Epic 创建前）

- CloudFiles 与文件预览主体不是从零开始：`e96f3f9b`、`142a924c`、`22fca349` 已接通个人云预览生产链及 iOS/Android 宿主预览。
- `4c1ee55d` 已拆出 Preview Planner、Coordinator、Launcher、Source、App composition provider 与多格式预览页面。
- `9c156421` 已统一 Files 三类文件预览与 CloudFiles 模块；`1c2be2f8` 已接通上传/分享；`6073ae16` 已补齐 PPTX、HTML、图片缓存与媒体兼容。
- `f1224fb6`、`beeff8dd` 完成 InputBar 附件上传/预览生产链，可为 typed host action 提供复用基础，但属于本 Epic 明确排除范围，不计入 Story 完成。

### 本 Epic 专属进度

| 项目 | 当前事实 |
|------|----------|
| 已完成阶段 | requirement、prioritization、architecture、story-split |
| 当前阶段 | `integration-test` |
| 当前滚动 Story | 无（7/7 已完成） |
| 实现落点 | 7/7 完成 |
| 逐故事 TDD | 7/7 完成；US-CFR-001..007 `validate-client-dev story-development` 通过 |
| 集成测试计划/执行 | 8 条用例已审核；7 自动化 suite PASS；iPhone EPUB/应用内预览 PASS；PDF 前置阻塞 |
| 仍存核心债务 | 无实现边界债务；需在已同意隐私+已登录+根目录有 PDF 的宿主重跑真实 PDF，并补 Android Phone/Pad/Fold 与 iPad 矩阵 |

> 进度口径：已有 CloudFiles/Preview 功能与第一轮架构成果作为重构基线保留；本 Epic 只在依赖边界目标及对应 Red/Green/TDD 证据闭合后计 Story 完成。

## 六、初始风险

| 风险 | 应对方向 |
|------|----------|
| Files 与 Projects 同时消费 Cloud Files Runtime | 先建立 Feature 可见投影与 App 内部 Runtime 边界，不直接搬移或删除依赖 |
| owner 换代期的迟到结果和预览资源泄漏 | 保留现有 generation/identity/lease 围栏，先锁回归再重构 |
| 拆 Provider 导致网络 Client 重复创建 | 应用内部 Runtime 继续统一持有 transport，Feature 仅消费 Repository/Port |
| 现有并行 InputBar 改动 | 独立 Epic 和文件范围，冲突时停止并转交用户 |

## 七、变更记录

| 日期 | 变更 | 影响阶段 | 证据 | 确认人 |
|------|------|----------|------|--------|
| 2026-08-19 | 创建 CloudFiles 与文件预览依赖边界重构 Epic | requirement | 用户明确要求重构并创建计划 Epic | 用户 |
| 2026-08-19 | 需求与排序门禁通过，完成架构方案并停在 ADR 评审 | architecture | requirement/backlog/architecture plan-gate 通过 | 待用户确认 |
| 2026-08-19 | 用户确认 Preview 装配与三项架构裁决合理，架构正式采纳 | architecture | architecture_open=0，新增架构采纳 skill_run | 用户 |
| 2026-08-20 | 授权并完成 Story 拆分：7 故事 / 39 点，story-scope 与 skill_run 门禁通过，进入 implementation-design | story-split | validate-client-dev story-scope=OK；workflow-gate 推进至 implementation-design | 用户 |
| 2026-08-20 | 根据代码提交与生产依赖复核更新真实进度：补记已完成基线，当前滚动至 US-CFR-001 落点设计 | implementation-design | `Contexts/决策/2026-08-20-开发流程审计报告.md`；workflow-status / workflow-gate | 用户 |
| 2026-08-21 | 完成 US-CFR-001 实现落点：显式 clean Red + 默认债务快照、Provider lifecycle 与既有 owner 绿基线 | implementation-design | `…-US-CFR-001.impl.json`；implementation-design validator | Codex |
| 2026-08-21 | 完成 US-CFR-001 test-only TDD：边界 Red、债务快照、owner/lifecycle 与聚焦 smoke；滚动至 US-CFR-002 | story-development | `…-US-CFR-001.tdd.json`；story-development validator | Codex |
| 2026-08-21 | 完成 US-CFR-002：四个 Files composition 消除 root import，primitive 叶子与 root 兼容 export 保持 Provider/owner/lifecycle 语义；滚动至 US-CFR-003 | story-development | `…-US-CFR-002.tdd.json`；story-development validator | Codex |
| 2026-08-21 | 完成 US-CFR-003 实现落点：Files Feature Runtime 契约、App Runtime 投影、兼容面与 owner/lifecycle Red 位置已锁定 | implementation-design | `…-US-CFR-003.impl.json`；implementation-design validator | Codex |
| 2026-08-21 | 完成 US-CFR-003 TDD：App/Feature Runtime 字段分离、生产投影、owner generation 与单次生命周期通过；滚动至 US-CFR-004 | story-development | `…-US-CFR-003.tdd.json`；story-development validator | Codex |
| 2026-08-21 | 完成 US-CFR-004：Files UI 通过 Host 注入消费窄依赖，Feature 对 App import 清零，overlay route 继承 owner/generation 围栏；滚动至 US-CFR-005 | story-development | `…-US-CFR-004.tdd.json`；story-development validator | Codex |
| 2026-08-21 | 完成 US-CFR-005：预览 UI/协调/缓存/plugin adapter 归位 FilePreview Feature，传输实现归位 Files，App 只保留装配/路由与无凭据 binding；滚动至 US-CFR-006 | story-development | `…-US-CFR-005.tdd.json`；233 项 focused regression；连接 iPhone 启动 smoke | Codex |
| 2026-08-21 | 完成 US-CFR-006：旧 Runtime typedef/消费者与下载 App 所有权命名收窄，runtime/manager 单例与单次 dispose 通过 | story-development | `…-US-CFR-006.tdd.json`；84/84 + 14/14 + 2/2 focused regression | Codex |
| 2026-08-21 | 完成 US-CFR-007：固化 Feature/App 归属文档、FilePreview 类型词典和自动边界；7/7 Story 闭合后进入集成测试计划 | story-development | `…-US-CFR-007.tdd.json`；60/60 focused regression；iPhone home first frame 1776ms | Codex |
| 2026-08-21 | 集成计划 8 用例通过审核；7 自动化 suite、iPhone EPUB 和应用内多格式预览通过；PDF 设备回归的旧 Home key 已修复，但真实链路被隐私/登录 fixture 阻塞 | integration-test | `…-集成测试.integration.json`；integration validator 保持 BLOCKED | Codex |

## 反馈（skill_run）

```yaml
skill_run:
  skill: template-generator
  workflow_stage: requirement
  plan: Plans/Epic/2026-08-19-Flutter-CloudFiles与文件预览依赖边界重构.md
  date: 2026-08-19
  contexts_used:
    - path: Templates/Epic模板-client-dev.md
      utility: high
      reason: "按 client-dev 蓝图建立 Epic frontmatter、阶段索引与动态 Story 看板入口"
    - path: Templates/模板约定.md
      utility: high
      reason: "确保文件命名、status、workflow、lifecycle_state 和子 Plan 路径符合 Vault 约定"
  contexts_missing: []
  contexts_stale: []
  outcome: "创建 Flutter CloudFiles 与文件预览依赖边界重构 Epic，锁定无产品行为变更的架构重构范围"
  utility: high
  reason: "为跨模块重构建立唯一 client-dev 工作流入口"
```

## 续做

```text
/resume plan=Plans/Epic/2026-08-19-Flutter-CloudFiles与文件预览依赖边界重构.md 进度=integration-test-plan
```

## 四、变更日志

| 日期 | 变更类型 | 影响阶段 | 重开切片 | 确认人 | 说明 |
|------|----------|----------|----------|--------|------|
| 2026-08-25 | 归档 | — | — | web | status → 已归档 |
