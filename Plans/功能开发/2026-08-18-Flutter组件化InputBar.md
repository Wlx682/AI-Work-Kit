---
tags: [功能开发, Flutter, InputBar, Slate, 附件]
type: plan
category: 功能开发
status: 已完成
date: 2026-08-18
lifecycle_state: story-development
epic: Plans/Epic/2026-08-18-Flutter组件化InputBar.md
requirement_plan: Plans/需求分析/2026-08-18-Flutter组件化InputBar.md
backlog_plan: Plans/需求排序/2026-08-18-Flutter组件化InputBar.md
architecture_plan: Plans/技术方案/2026-08-18-Flutter组件化InputBar.md
story_index: Plans/功能开发/2026-08-18-Flutter组件化InputBar.stories.json
---

# Flutter 组件化 InputBar：生产 Scope

## Scope

用户最终确认本 Epic 全部实现以下能力：Slate Text/@、FileInput、MediaPreview/上传、Model、Skill；明确排除 `NMNewTextAndVoiceComponent`、独立 Voice 与 AIGC。`474e5cd2` 只作为可编译框架底座，不再作为完整交付证据。

| Story ID | 可独立演示的用户能力 | Backlog/AC | 优先级 | 点数 | Epic Scope | 当前滚动 Scope |
|---|---|---|---|---:|---|---|
| US-IB-001 | 在 Flutter Slate 输入框输入文本、@专家并按协议发送 | REQ-IB-001/002；AC-IB-002..004 | P0 | 8 | true | false |
| US-IB-002 | 选择照片/文件/云盘项，查看上传进度并重试、删除、预览 | REQ-IB-003/004；AC-IB-005..009 | P0 | 8 | true | false |
| US-IB-003 | 把成功附件与 Slate prompt 冻结进 durable delivery，并安全恢复/清理草稿 | REQ-IB-006；AC-IB-010、012、013 | P0 | 8 | true | false |
| US-IB-004 | 外部数据契约稳定后选择 Model/Skill，并组装完整 5 组件 InputBar | REQ-IB-001/005；AC-IB-001、011 | P1 | 8 | true | true（已完成，供阶段门禁核验） |

四个故事均为 UI → State → Repository/Port → 生产调用 → 失败恢复的纵向切片；无 13 点故事和估算豁免。US-IB-001..004 已全部完成；US-IB-004 仅作为最后一个已完成滚动 Scope 供阶段门禁核验，不代表仍有待开发代码。下一阶段进入集成测试计划与审核。

## 历史实现处理

- 原 US-IB-001 的中心 State、Component、双 Delegate、四位置与 ChatPage 接线保留并复用。
- 原 `TextEditingValue` 文档真值、纯文本组件和旧 TDD 证据由新 US-IB-001 取代。
- 集成测试计划保持 `pending-change`，待四个 Scope Story 全部完成后重建并审核。
- AgentSummary、Skill 等跨业务模型和生产 adapter 不由当前 Slate/附件 Story 修改；US-IB-004 后置等待对应模块契约。

## 实现落点设计

- US-IB-001 已完成：`Plans/功能开发/2026-08-18-Flutter组件化InputBar-US-IB-001.impl.json`。
- US-IB-002 已完成：`Plans/功能开发/2026-08-18-Flutter组件化InputBar-US-IB-002.tdd.json`。
- US-IB-003 已完成：`Plans/功能开发/2026-08-18-Flutter组件化InputBar-US-IB-003.impl.json`。
- US-IB-004 已完成：`Plans/功能开发/2026-08-18-Flutter组件化InputBar-US-IB-004.tdd.json`。
- 四个 Story 的实现落点、TDD 与生产接线已闭合；真机与跨 Story 组合缺口转入集成测试计划。

## 反馈（skill_run）

```yaml
skill_run:
  skill: task-splitter
  workflow_stage: story-split
  plan: Plans/功能开发/2026-08-18-Flutter组件化InputBar.md
  date: 2026-08-19
  contexts_used:
    - path: Plans/需求排序/2026-08-18-Flutter组件化InputBar.md
      utility: high
      reason: "按用户最终范围固定 Slate/@、附件链、Model/Skill 与完整发送的依赖顺序"
    - path: Plans/技术方案/2026-08-18-Flutter组件化InputBar.md
      utility: high
      reason: "把每个故事约束为 UI 到 durable/失败恢复的纵向切片"
  contexts_missing: []
  contexts_stale:
    - path: Plans/功能开发/2026-08-18-Flutter组件化InputBar-US-IB-001.tdd.json
      reason: "旧证据仅覆盖 TextEditingValue/纯文本底座，已由 Slate 完整迁移的 tdd-v2 证据取代"
  outcome_status: pass
  outcome: "拆为四个 8 点纵向 Story；Epic Scope 全量确认，当前滚动 Scope 为 Slate/@"
  revisit_needed: false
```

```yaml
skill_run:
  skill: task-splitter
  workflow_stage: story-split
  plan: Plans/功能开发/2026-08-18-Flutter组件化InputBar.md
  date: 2026-08-19
  contexts_used:
    - path: Plans/需求排序/2026-08-18-Flutter组件化InputBar.md
      utility: high
      reason: "复核六项有序 Backlog 均已被四个纵向 Story 覆盖，附件链仍是当前 P0"
    - path: Plans/技术方案/2026-08-18-Flutter组件化InputBar.md
      utility: high
      reason: "确认每个 Story 都包含 UI、状态、端口、生产调用和失败恢复，不退化为横向分层任务"
    - path: Plans/功能开发/2026-08-18-Flutter组件化InputBar.stories.json
      utility: high
      reason: "保持用户已确认的四个 8 点 Story，并继续以 US-IB-002 作为唯一滚动 Scope"
  contexts_missing: []
  contexts_stale:
    - path: Plans/功能开发/2026-08-18-Flutter组件化InputBar-US-IB-001.tdd.json
      reason: "旧 Slate MVP 证据不再作为 US-IB-001 完成真值"
  outcome_status: pass
  outcome: "未改动用户已确认的 Story/点数/Scope，仅修复反馈协议并确认 US-IB-002 继续开发"
  revisit_needed: false
```

```yaml
skill_run:
  skill: implementation-design-assistant
  workflow_stage: implementation-design
  plan: Plans/功能开发/2026-08-18-Flutter组件化InputBar.md
  date: 2026-08-19
  contexts_used:
    - path: Plans/功能开发/2026-08-18-Flutter组件化InputBar-US-IB-002.impl.json
      utility: high
      reason: "确认当前 Scope 的代码落点、实例级依赖方向和 Red 测试位置均完整"
    - path: Plans/技术方案/2026-08-18-Flutter组件化InputBar.md
      utility: high
      reason: "对齐 typed Picker/Upload/Preview API Schema 与 `/api/s3/upload` 生产契约"
    - path: Plans/功能开发/2026-08-18-Flutter组件化InputBar-US-IB-002.md
      utility: high
      reason: "把实现设计结果回写当前纵向 Story，并补齐需求/架构追溯链接"
  contexts_missing: []
  contexts_stale: []
  outcome_status: pass
  outcome: "US-IB-002 实现落点校验通过，可进入 story-development"
  revisit_needed: false
```


## 2026-08-19 Figma 视觉与高度动画校正

### 设计输入

- Figma：`纳米Work-移动端 / 0714-对话框简化`
- 根节点：`1:30792`
- 状态节点：
  - `1:31431` 默认单行
  - `1:31452` 聚焦空态
  - `1:31480` 多行输入
  - `1:31508` 长文本与展开入口
  - `1:31546` 键盘收起后回落单行
  - `1:30958` 顶部模型/模式胶囊
- 平台：Flutter，Android Phone/Pad/Fold、iPhone/iPad 共用呈现层。
- 视觉取值按 Figma 720 画板折算到 360 logical px：主容器宽 336、高 60、水平外边距 12、圆角 20；聚焦空态高 94；正文 16/25；左右内边距 14；按钮 32，发送胶囊 44×32。
- 逻辑事实源：iOS frozen `4d405cf0` 的 `NMInputBar.swift` 与 `NMNewTextInputComponent.swift`。同一个 SlateView 通过约束切换单行/上下两层；聚焦收起附件面板，附件按钮退出编辑态再切面板；状态相等不回灌；高度动画从当前布局继续。

### 组件映射

| Figma / iOS | Flutter 落点 | 裁决 |
|---|---|---|
| 白色双阴影圆角主容器 | `NamiInputBar` composer surface | 主容器统一承载 Skill、MediaPreview、Slate；不再由 TextField 自己画矩形边框 |
| 单行 ↔ 上下两层 | `NamiTextInputComponent._ComposerLayout` | 同一个 `NamiSlateTextView` 常驻，只更新位置/高度，避免焦点丢失和状态回路 |
| 上传加号 | `NamiTextInputComponent` | 对齐 iOS：入口属于 Text 组件，File 组件只负责 bottom panel |
| 发送胶囊 | `NamiTextInputComponent` | Figma SVG；编辑空态保留 30% 禁用背景 |
| 长文本展开 | `_ExpandedSlateEditor` | 仍使用唯一 Flutter Slate TextView 与 Slate document，不增加 native/adaptor |
| 模型胶囊 | `NamiModelComponent` | 36 高、12 圆角、1px 10% 黑边、14 medium、右箭头 |
| 高度动画 | 内外两层 `AnimatedSize` + `AnimatedPositionedDirectional` | 100ms `easeInOutCubic`，支持连续重定向；不再使用 60ms 线性突变 |

### 验证状态

- `flutter analyze lib/features/chat/presentation/input_bar lib/features/chat/presentation/chat_page.dart test/features/chat/presentation/input_bar/nami_input_bar_test.dart`：PASS。
- `flutter test test/features/chat/presentation/input_bar`：PASS，55 tests。
- `flutter test test/app/product_chat_destination_test.dart`：PASS，13 tests。
- Figma `get_screenshot`：已复核默认态 `1:31431` 与聚焦态 `1:31452`。
- Flutter 真实渲染预览：已复核 360 规则在 800 Web viewport 等比呈现，默认 60 / 聚焦 94、阴影、圆角、按钮和内边距一致。
- Android Phone：APK 构建 PASS；安装被华为 AppGallery 交互式拼图拦截，真机截图 `NOT_RUN`。
- iPhone：Xcode build PASS；安装被仓库既有未签名 `nami_text_view.framework` 拒绝，真机截图 `NOT_RUN`。本次未恢复 native bridge，也未扩大为原生签名修复。

详细自检：`Plans/功能开发/2026-08-19-Flutter组件化InputBar-Figma还原自检.md`。

```yaml
skill_run:
  skill: figma-ui
  workflow_stage: ui-development
  plan: Plans/功能开发/2026-08-18-Flutter组件化InputBar.md
  date: 2026-08-19
  contexts_used:
    - path: Contexts/Figma/项目设计规范.md
      utility: high
      reason: "按 @2x 画板折算 logical px，并以节点数据而非截图猜测还原布局"
    - path: Contexts/Figma/Figma界面开发最佳实践.md
      utility: high
      reason: "先读取节点状态、复用现有组件和 token，再做真实渲染对稿与自检"
    - path: Templates/Figma还原自检表.md
      utility: high
      reason: "记录静态、状态、动效、适配与真机阻塞项"
  contexts_missing: []
  contexts_stale: []
  outcome_status: partial
  outcome: "完成 InputBar 默认/聚焦/多行/长文本/收起态视觉迁移与 100ms 连续高度动画；代码测试和 Flutter 渲染通过，双端真机截图被外部安装门禁阻塞"
  revisit_needed: true
  revisit_trigger: "华为拼图由用户完成，或 iOS 既有 nami_text_view.framework 签名问题修复后补真机对稿"
```


```yaml
skill_run:
  skill: feature-dev-assistant
  workflow_stage: story-development
  plan: Plans/功能开发/2026-08-18-Flutter组件化InputBar.md
  date: 2026-08-19
  contexts_used:
    - path: Plans/功能开发/2026-08-18-Flutter组件化InputBar-US-IB-003.impl.json
      utility: high
      reason: "按 snapshot factory、sendInput、终态结算和 Red 测试落点完成纵向实现"
    - path: Plans/技术方案/2026-08-18-Flutter组件化InputBar.md
      utility: high
      reason: "遵守 remote URL 受控 prompt、既有 durable outbox 和精确 revision 清理 ADR"
    - path: Plans/功能开发/2026-08-18-Flutter组件化InputBar-US-IB-003.tdd.json
      utility: high
      reason: "记录 Red/Green/Refactor、48+86 回归、逐 AC 结果和真机 NOT_RUN"
  contexts_missing: []
  contexts_stale: []
  outcome_status: pass
  outcome: "US-IB-003 在 6973cc97 完成：immutable snapshot、durable sendInput、附件-only 发送与 completed-only 精确草稿结算"
  revisit_needed: false
```

```yaml
skill_run:
  skill: resume-assistant
  workflow_stage: story-development
  plan: Plans/功能开发/2026-08-18-Flutter组件化InputBar.md
  date: 2026-08-19
  contexts_used:
    - path: Plans/Epic/2026-08-18-Flutter组件化InputBar.md
      utility: high
      reason: "回放 Epic 当前门禁并确认 US-IB-002 是唯一滚动 Scope"
    - path: Plans/功能开发/2026-08-18-Flutter组件化InputBar-US-IB-002.md
      utility: high
      reason: "恢复附件 Story 的验收边界、实现落点和真机未执行口径"
  contexts_missing: []
  contexts_stale: []
  outcome_status: pass
  outcome: "恢复后继续完成 US-IB-002 Red→Green→Refactor、生产预览接线和证据回填"
  revisit_needed: false
```

```yaml
skill_run:
  skill: feature-dev-assistant
  workflow_stage: story-development
  plan: Plans/功能开发/2026-08-18-Flutter组件化InputBar.md
  date: 2026-08-19
  contexts_used:
    - path: Plans/功能开发/2026-08-18-Flutter组件化InputBar-US-IB-002.impl.json
      utility: high
      reason: "按既定 domain/application/data/components/usage-site 落点实现纵向附件链"
    - path: Plans/技术方案/2026-08-18-Flutter组件化InputBar.md
      utility: high
      reason: "落实 per-instance typed port、签名 /api/s3/upload 与 owner/operation 围栏"
    - path: Plans/功能开发/2026-08-18-Flutter组件化InputBar-US-IB-002.tdd.json
      utility: high
      reason: "记录 Red、Green、Refactor、集成 smoke、逐 AC 结果和 NOT_RUN 真机项"
  contexts_missing: []
  contexts_stale: []
  outcome_status: pass
  outcome: "US-IB-002 在 45e48c2c 完成：附件选择、上传、重试/删除、真实媒体预览、发送硬门禁和精确终态清理闭环"
  revisit_needed: false
```

```yaml
skill_run:
  skill: task-splitter
  workflow_stage: story-split
  plan: Plans/功能开发/2026-08-18-Flutter组件化InputBar.md
  date: 2026-08-19
  contexts_used:
    - path: Plans/功能开发/2026-08-18-Flutter组件化InputBar.stories.json
      utility: high
      reason: "US-IB-002 已完成，按已确认依赖顺序把唯一滚动 Scope 切换为 US-IB-003"
    - path: Plans/技术方案/2026-08-18-Flutter组件化InputBar.md
      utility: high
      reason: "保持四个 8 点纵向故事、AC、依赖和 Epic Scope 不变"
  contexts_missing: []
  contexts_stale: []
  outcome_status: pass
  outcome: "未重拆故事或改点数，仅把滚动 Scope 从已完成 US-IB-002 切到 US-IB-003"
  revisit_needed: false
```

```yaml
skill_run:
  skill: implementation-design-assistant
  workflow_stage: implementation-design
  plan: Plans/功能开发/2026-08-18-Flutter组件化InputBar.md
  date: 2026-08-19
  contexts_used:
    - path: Plans/功能开发/2026-08-18-Flutter组件化InputBar-US-IB-003.impl.json
      utility: high
      reason: "确认 snapshot factory、sendInput、durable 终态结算与 Red 测试落点"
    - path: Plans/技术方案/2026-08-18-Flutter组件化InputBar.md
      utility: high
      reason: "遵守远程 URL 受控 prompt、既有 outbox 和精确 revision 清理 ADR"
    - path: Plans/功能开发/2026-08-18-Flutter组件化InputBar-US-IB-003.md
      utility: high
      reason: "回写当前 Story 的实现边界与代码证据"
  contexts_missing: []
  contexts_stale: []
  outcome_status: pass
  outcome: "US-IB-003 实现落点完整，可进入 story-development"
  revisit_needed: false
```

```yaml
skill_run:
  skill: resume-assistant
  workflow_stage: integration-test
  plan: Plans/功能开发/2026-08-18-Flutter组件化InputBar.md
  date: 2026-08-19
  contexts_used:
    - path: Plans/Epic/2026-08-18-Flutter组件化InputBar.md
      utility: high
      reason: "回放当前阶段并确认唯一门禁是 device-matrix"
    - path: Plans/自动化测试/2026-08-18-Flutter组件化InputBar-集成测试.md
      utility: high
      reason: "按已审核计划刷新当前候选自动化和真机证据"
  contexts_missing:
    - "当前候选五类设备完整 IT-IB-501 交互矩阵"
  contexts_stale:
    - path: Plans/自动化测试/2026-08-18-Flutter组件化InputBar-集成测试计划.md
      reason: "续做时计划仍冻结旧 commit 且缺 Figma 动画用例；本次已重新审核到 79dfcc0b"
  outcome_status: partial
  outcome: "恢复 integration-test，补 IT-IB-104、刷新候选并完成 144 自动化与 iPhone 安装启动；设备矩阵仍未闭合"
  revisit_needed: true
  revisit_reason: "从 IT-IB-501 当前候选真机交互矩阵继续"
```

```yaml
skill_run:
  skill: resume-assistant
  workflow_stage: integration-test
  plan: Plans/功能开发/2026-08-18-Flutter组件化InputBar.md
  date: 2026-08-19
  contexts_used:
    - path: Plans/Epic/2026-08-18-Flutter组件化InputBar.md
      utility: high
      reason: "回放后确认唯一阶段仍为 integration-test，继续执行 IT-IB-501"
    - path: Plans/自动化测试/2026-08-18-Flutter组件化InputBar-集成测试计划.cases.json
      utility: high
      reason: "从已审核 manual 用例恢复，不新增或改写测试范围"
  contexts_missing:
    - "iPhone InputBar 触控自动化或人工交互窗口"
    - "Android Pad/Fold 与 iPad 实体设备"
  contexts_stale:
    - path: Plans/自动化测试/2026-08-18-Flutter组件化InputBar-真机证据.json
      reason: "恢复时 Android Phone 仍绑定旧 SHA；本次已补当前候选部分证据"
  outcome_status: partial
  outcome: "继续完成当前候选 Android Phone 长文本自动换行、附件核心链、离线失败重试、旋转恢复和生产组件核验；整体仍由剩余设备矩阵阻断"
  revisit_needed: true
  revisit_reason: "从 Android Phone 剩余场景与 iPhone/Pad/Fold/iPad 继续"
```
