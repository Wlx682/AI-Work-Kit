---
tags: [Epic, client-dev, Flutter, Files, CloudFiles, 文件预览, 架构重构]
type: plan
category: Epic
status: 进行中
date: 2026-08-19
epic_id: flutter-cloud-files-preview-boundary-refactor
workflow: client-dev
lifecycle_state: story-split
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
| 功能故事拆分与故事点 | story-split | `Plans/功能开发/2026-08-19-Flutter-CloudFiles与文件预览依赖边界重构.md` | ⏸ 未开始，等待授权 |
| 实现落点设计 | implementation-design | 同上及动态故事子 Plan | ⬜ |
| 逐故事 TDD | story-development | 同上及动态故事子 Plan | ⬜ |
| 集成测试计划与审核 | integration-test-plan | `Plans/自动化测试/2026-08-19-Flutter-CloudFiles与文件预览依赖边界重构-集成测试计划.md` | ⬜ |
| 全量集成测试 | integration-test | `Plans/自动化测试/2026-08-19-Flutter-CloudFiles与文件预览依赖边界重构-集成测试.md` | ⬜ |

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
| — | 待 requirement / architecture 门禁通过后按纵向可验收价值拆分 | — | — | — | — | 待拆分 |

> 故事卡片由看板从 `.stories.json` 与子 Plan 派生；禁止把 UI、Domain、Data/API 分别作为交付故事。故事点不换算工时或个人绩效。

## 五、初始风险

| 风险 | 应对方向 |
|------|----------|
| Files 与 Projects 同时消费 Cloud Files Runtime | 先建立 Feature 可见投影与 App 内部 Runtime 边界，不直接搬移或删除依赖 |
| owner 换代期的迟到结果和预览资源泄漏 | 保留现有 generation/identity/lease 围栏，先锁回归再重构 |
| 拆 Provider 导致网络 Client 重复创建 | 应用内部 Runtime 继续统一持有 transport，Feature 仅消费 Repository/Port |
| 现有并行 InputBar 改动 | 独立 Epic 和文件范围，冲突时停止并转交用户 |

## 六、变更记录

| 日期 | 变更 | 影响阶段 | 证据 | 确认人 |
|------|------|----------|------|--------|
| 2026-08-19 | 创建 CloudFiles 与文件预览依赖边界重构 Epic | requirement | 用户明确要求重构并创建计划 Epic | 用户 |
| 2026-08-19 | 需求与排序门禁通过，完成架构方案并停在 ADR 评审 | architecture | requirement/backlog/architecture plan-gate 通过 | 待用户确认 |
| 2026-08-19 | 用户确认 Preview 装配与三项架构裁决合理，架构正式采纳 | architecture | architecture_open=0，新增架构采纳 skill_run | 用户 |

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
/resume plan=Plans/Epic/2026-08-19-Flutter-CloudFiles与文件预览依赖边界重构.md 进度=架构已采纳；等待明确授权 Story 拆分，禁止开始开发
```
