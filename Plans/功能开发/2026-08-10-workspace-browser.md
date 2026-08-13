---
tags: [功能开发, 用户故事, workspace]
type: plan
category: 功能开发
status: 已采纳
date: 2026-08-10
lifecycle_state: story-development
epic: Plans/Epic/2026-08-10-workspace-browser.md
requirement_plan: Plans/需求分析/2026-08-10-workspace-browser.md
architecture_plan: Plans/技术方案/2026-08-10-workspace-browser.md
story_index: Plans/功能开发/2026-08-10-workspace-browser.stories.json
---
# 功能故事开发：工作区文件分层浏览与搜索

| Story ID | 用户能力 | AC | 架构引用 | 优先级 | 故事点 | Scope | 子 Plan |
|---|---|---|---|---|---:|---|---|
| US-001 | 分层浏览、分页和搜索工作区文件 | AC1..AC9 | ADR-001..006 | P0 | 8 | true | `Plans/功能开发/2026-08-10-workspace-browser-US-001.md` |
| US-002 | 文件目录独立页面、统一面包屑与完整动作菜单 | AC1..AC5 | iOS frozen source + Figma 30371:42190 | P0 | 8 | true | `Plans/功能开发/2026-08-10-workspace-browser-US-002.md` |

## 实现落点设计

| Story | 设计文件 | 摘要 | Red | 状态 |
|---|---|---|---|---|
| US-001 | `Plans/功能开发/2026-08-10-workspace-browser-US-001.impl.json` | workspace/browser 四层、FilesystemGateway adapter、Files Tab/l10n 串行接线 | repository/controller/view | 已确认 |
| US-002 | `Plans/功能开发/2026-08-10-workspace-browser-US-002.impl.json` | 独立目录页、共享面包屑/菜单、AI/用户上传/工作空间动作接线 | navigation/action/view | 已确认 |

依赖固定为 View→Controller→Repository→FilesystemGateway；Feature 不暴露 GatewayPayload，不依赖个人云盘 Feature。

## US-002 Figma/iOS 增量自检

- Figma 节点 `30371:42190`：面包屑左边距 16、字号 12、间距 4、分隔符 12；祖先层 50% 黑、当前层 90% 黑并加重，超宽横向滚动到当前层。
- 固定 iOS `4d405cf`：用户上传文件为分享/下载/移动/删除/重命名，目录为移动/删除/重命名；AI 与工作空间默认包含分享/下载/导出到用户上传/引用，并按会话和渠道能力追加查看任务文件、原对话、发送附件。
- Flutter：目录逐层 push 独立页面；三分区共享 `FileBreadcrumb` 与 `FileActionMenuButton`，不再使用各自原地切层或被禁用的更多按钮。
- 真机：Flutter attach 下通过 VM Inspector 确认“自动备份”详情页与五项文件菜单；自动化回归 `196/196`。
- 差异：尚未安装的系统分享/保存、导出、引用及业务路由明确提示不可用，故功能状态保持 `PARTIAL`，不冒充完成。

### Figma 还原自检

| 检查项 | 结论 |
|---|---|
| 布局与排版 | 12px 字体、4px 间距、12px 分隔符、16px 左边距及当前层强调与节点一致 |
| 层级与滚动 | 祖先/当前颜色和字重区分；长路径横向滚动并定位当前层 |
| 导航行为 | 用户上传与工作空间逐层 push，返回保持父页状态，符合 iOS 控制器栈 |
| 动作菜单 | 动作顺序和条件来自固定 iOS，视觉复用已收敛的 Figma 白色圆角菜单 |
| 真机证据 | 有线 iPhone 已确认独立页面、面包屑及用户上传文件五项菜单，连接保持 |
| **自评** | **9.5/10**；剩余差异为未交付业务能力，不是视觉差异 |

```yaml
skill_run:
  skill: figma-design-to-code
  workflow_stage: story-development
  plan: Plans/功能开发/2026-08-10-workspace-browser.md
  date: 2026-08-10
  contexts_used:
    - path: Figma/Z3hhNwFzvLZOdnCtXkIRHn/30371:42190
      utility: high
      reason: "读取面包屑的尺寸、层级色值、字体和横向滚动结构"
  contexts_missing: []
  contexts_stale: []
  outcome_status: pass
  revisit_needed: false
```

## 移动弹层根遮罩增量自检

- 用户反馈：移动弹层打开后，底部 Tab 与 Home Indicator SafeArea 仍浮在遮罩和弹层上方，视觉层级不完整。
- 实现：`showModalBottomSheet` 使用根 Navigator；遮罩覆盖完整 viewport，弹层覆盖底部 Tab 与 SafeArea，底部操作内容继续由弹层内部 `SafeArea` 避让 Home Indicator。
- 保持项：弹层仍为全宽、窗口高度减 100pt、顶部圆角 32pt、白色背景；移动状态、请求和关闭语义均未改变。
- 自动化验证：构造 390×844、顶部 47pt/底部 34pt inset、根 Scaffold + 分支 Navigator + BottomNavigationBar；锁定 barrier 从 `(0,0)` 覆盖完整窗口，底部区域不可穿透。目标测试 `6/6 PASS`，定向 analyze 无问题。
- 真机验证：有线 iPhone 保持 `flutter run` 连接，通过 VM Inspector 截图确认底部 Tab 不再浮于弹层之上。
- 自评：`9/10`；唯一缺口为用户未提供该弹层对应的 Figma node-id，无法补 MCP 设计节点截图。本次只按用户明确的层级裁决修改，不改变既有视觉参数。

```yaml
skill_run:
  skill: figma-ui
  workflow_stage: story-development
  plan: Plans/功能开发/2026-08-10-workspace-browser.md
  date: 2026-08-10
  contexts_used:
    - path: Contexts/Figma/项目设计规范.md
      utility: high
      reason: "约束本次只调整容器层级，保持弹层尺寸、颜色、圆角和 SafeArea 内容避让"
    - path: Contexts/Figma/Figma界面开发最佳实践.md
      utility: high
      reason: "按根路由层级、边界状态和真机截图完成 UI 收口"
    - path: Templates/Figma还原自检表.md
      utility: high
      reason: "记录度量保持项、遮罩交互、验证证据与设计节点缺口"
  contexts_missing:
    - "移动弹层对应的 Figma node-id"
  contexts_stale: []
  outcome_status: pass
  friction: "用户只提供运行截图，没有 Figma node-id，无法执行 MCP 设计节点截图"
  verdict_score: 9
  revisit_needed: false
```

```yaml
skill_run:
  skill: feature-dev-assistant
  workflow_stage: story-development
  plan: Plans/功能开发/2026-08-10-workspace-browser.md
  date: 2026-08-10
  contexts_used:
    - path: Plans/功能开发/2026-08-10-workspace-browser-US-002.impl.json
      utility: high
      reason: "约束独立路由、共享组件、条件动作集合及 runtime owner fence"
  contexts_missing:
    - "真实 Gateway 渠道能力和未交付业务路由的端到端证据"
  contexts_stale: []
  outcome_status: partial
  revisit_needed: true
```

## 反馈（skill_run）

```yaml
skill_run:
  skill: implementation-design-assistant
  workflow_stage: implementation-design
  plan: Plans/功能开发/2026-08-10-workspace-browser.md
  date: 2026-08-10
  contexts_used:
    - path: Contexts/决策/测试先行原则.md
      utility: high
      reason: "先固定分层游标、owner fence 和三档 renderer 的 Red 落点"
  contexts_missing: []
  contexts_stale: []
  outcome_status: pass
  revisit_needed: false
```

## 文件操作菜单 Figma 增量自检

- 用户反馈：用户上传文件右侧弹出菜单仍呈 Material 浅紫底、直角感和默认阴影，与设计不一致。
- 设计证据：通过 Figma MCP 读取页面节点 `30371:41534`，再定位并读取菜单节点 `33487:14622` 的设计上下文与截图。
- 精确度量：外框 `164×152`、白底、圆角 `12`、`0/0/8px/10% black` 阴影；内部 `4` 间距；每项 `156×48`、交互圆角 `10`；图标 `24`、图标与文字间距 `8`、左内边距 `10`；文字 `15 / w500 / 90% black`。
- 实现：复用现有 Figma 导出 `move.png`、`delete.png`、`rename.png`，以自定义 `PopupMenuEntry` 还原白色圆角菜单及 pressed/hover/focus 的 `4%` 黑色反馈；真机反馈证明 Material `elevation: 4` 的预设阴影扩散小于 Figma blur，改用 `elevation: 8` 对齐节点的 8px 视觉效果；保留移动、删除、重命名原有业务回调，并补充 menuItem 语义与动态字体纵向扩展。
- 验证：Files 页面集成测试 `17/17` 通过；目标 analyze、format、任务命名与 diff 检查通过；独立 Review 为 `P0=0 / P1=0`；有线 iPhone 已热重载并继续保持 Flutter attach。

### Figma 还原自检

| 检查项 | 结论 |
|---|---|
| 布局与度量 | 外框、行高、padding、图标及文字间距均按节点 `33487:14622` 的 @2x 标注换算 |
| 色板与效果 | 纯白背景、90% 黑文字、4% 黑交互态、10% 黑阴影均已锁定测试 |
| 资源 | 复用仓库内 Figma 原始 PNG，无系统占位图标 |
| 状态与可访问性 | 覆盖默认、pressed/hover/focus、menuItem 语义；大字体允许菜单项纵向扩展 |
| 截图对比 | 已获取菜单 Figma 截图；修复已热重载，最终真机观感由用户现场确认 |
| 差异 | 无已知生产代码差异；仅保留多语言 3× 字体与键盘选择的非阻塞自动化覆盖缺口 |
| **自评** | **9.2/10** |

```yaml
skill_run:
  skill: figma-ui
  workflow_stage: story-development
  plan: Plans/功能开发/2026-08-10-workspace-browser.md
  date: 2026-08-10
  contexts_used:
    - path: Contexts/Figma/Figma界面开发最佳实践.md
      utility: high
      reason: "通过父页面节点定位独立菜单组件，按 @2x 标注换算 Flutter 逻辑像素并复用原始资源"
    - path: Templates/Figma还原自检表.md
      utility: high
      reason: "按布局、色彩、资源、状态、可访问性和证据完成增量自检"
  contexts_missing:
    - "Flutter attach 期间从有线 iPhone 非侵入抓取当前弹出菜单截图的标准命令"
  contexts_stale: []
  outcome_status: partial
  friction: "修复已实时热重载，但当前链路不能在不影响 Flutter attach 的前提下归档有线 iPhone 菜单截图"
  revisit_needed: false
```

```yaml
skill_run:
  skill: feature-dev-assistant
  workflow_stage: story-development
  plan: Plans/功能开发/2026-08-10-workspace-browser.md
  date: 2026-08-10
  contexts_used:
    - path: Plans/功能开发/2026-08-10-workspace-browser-US-001.impl.json
      utility: high
      reason: "约束 Repository、Gateway adapter、Controller、三档 View 与生产宿主的依赖方向"
  contexts_missing:
    - "真实 Gateway 账号与五种设备形态验收证据"
  contexts_stale: []
  outcome_status: partial
  revisit_needed: true
```

```yaml
skill_run:
  skill: resume-assistant
  workflow_stage: story-development
  plan: Plans/功能开发/2026-08-10-workspace-browser.md
  date: 2026-08-10
  contexts_used:
    - path: Plans/Epic/2026-08-10-workspace-browser.md
      utility: high
      reason: "从 Files Tab 续做 BUS-057，保留真实账号与真机门禁"
  contexts_missing: []
  contexts_stale: []
  outcome_status: partial
  revisit_needed: true
```

## Files 页 Figma 还原记录

- 设计稿：[PC/App 设计文件，节点 30371:41534](https://www.figma.com/design/Z3hhNwFzvLZOdnCtXkIRHn/?node-id=30371-41534&m=dev)
- 目标平台：Flutter 共享实现（iPhone/iPad/Android Phone/Pad/Fold），本轮以 360×800 iPhone 画板和固定 iOS 资源为视觉基线。
- 用户裁决：原「云盘」入口改名为「文件」；页内三段为「用户上传 / AI文件 / 工作空间」，默认展示用户上传。
- 核心测量：工具栏 52；分段控件 x=16、宽 328、高 40、圆角 12；选中块内缩 3、高 34、圆角 10；说明文字 12/17；列表首行 y=194；图标 40；图标与标题间距 16；标题 16/22.5；元信息 12/17；行间距 6；更多操作触控区 44。
- 状态与交互：三 Tab 懒加载并保活；搜索入口及提示跟随当前 Tab，顶部查询与三个 Controller 双向同步，进入目录、runtime 就绪与 owner 替换均保持一致；用户上传显示新增入口；更多菜单 164×152，顺序为移动、删除、重命名；Compact 大字体保持最小触控高度和选中语义。
- 资源：复用固定 iOS/Figma 的 folder、general、document、pdf、presentation、spreadsheet、image、video、audio、link、more 位图；AI 头像和预览图继续使用运行时数据。
- 证据：`test/features/cloud_drive/browser/presentation/goldens/files-user-upload-figma.png`；相关 148 个测试通过；定向 analyze、format、任务命名与 diff 检查通过；Flutter 与 iOS 独立复审均 P0/P1/P2=0；已在有线 iPhone（iOS 18.6.2）完成最新最终候选构建、覆盖安装、启动和 Files deep link。

### Figma 还原自检

| 维度 | 得分 | 结论 |
|---|---:|---|
| 布局与间距 | 1.9/2 | 关键坐标、尺寸、圆角、列表节奏按 Dev Mode 测量落地 |
| 色彩与层级 | 1.9/2 | 白底、浅灰轨道、选中块、主次文字层级一致 |
| 字体与排版 | 1.9/2 | 标题 18 semibold，列表字号、行高、权重和最大行数一致；AI 元信息按 iOS 的 14px 头像及中文日期时间格式收口，并补大字体适配 |
| 图标与资源 | 2.0/2 | 直接复用固定 iOS 与 Figma 同源资源，不用系统占位图标替代 |
| 交互与状态 | 1.9/2 | Tab 保活、分区搜索状态双向同步、新建与操作菜单已接线；真实账号内容仍需用户现场观感验收 |
| **总分** | **9.6/10** | 达到 Figma UI 交付门槛 |

```yaml
skill_run:
  skill: figma-design-to-code
  workflow_stage: story-development
  plan: Plans/功能开发/2026-08-10-workspace-browser.md
  date: 2026-08-10
  contexts_used:
    - path: Figma/Z3hhNwFzvLZOdnCtXkIRHn/30371:41534
      utility: high
      reason: "通过 Dev Mode 提取用户上传、AI 文件、工作空间画板的真实尺寸、资源和菜单状态"
  contexts_missing: []
  contexts_stale: []
  outcome_status: pass
  revisit_needed: false
```

```yaml
skill_run:
  skill: figma-ui
  workflow_stage: story-development
  plan: Plans/功能开发/2026-08-10-workspace-browser.md
  date: 2026-08-10
  contexts_used:
    - path: Templates/Figma还原自检表.md
      utility: high
      reason: "按布局、色彩、字体、资源、交互五维完成 9.6/10 自检并保留 Golden 与真机证据"
  contexts_missing:
    - "真实账号返回内容后的用户现场视觉确认"
  contexts_stale: []
  outcome_status: pass
  revisit_needed: false
```

## Files SafeArea 白底增量自检

- 用户反馈：顶部系统 SafeArea 仍露出 Material 3 带色 surface，期望 Files 从状态栏到页面主体通屏纯白。
- 设计证据：通过 Figma MCP 重新读取节点 `30371:41534` 截图，Files 各状态画板的系统状态栏、导航栏和内容区均为纯白背景。
- 根因：系统 SafeArea 由外层 `AdaptiveAppShell` 消耗，叶子 `CloudBrowserPage` 的白色 Scaffold 无法绘制该区域。
- 实现：`AdaptiveAppShell` 接受可选页面背景色；`AppShell` 仅在当前一级分支为 Files 时传入 `Colors.white`，手机 Bottom Bar 与 Pad/Fold Rail 共用，其他分支继续使用原主题背景。
- 验证：导航、Shell 与 Files 定向测试 `54/54` 通过；analyze、format、任务命名与 diff 检查通过；有线 iPhone 已热重载且 Flutter 连接保持。

### Figma 还原自检

| 检查项 | 结论 |
|---|---|
| 度量/形状/字号/图标 | 本次仅修改全屏背景填充，尺寸与资源无变化 |
| 色板 | Figma 外层画板 `#FFFFFF`，Files Shell SafeArea 使用 `Colors.white` |
| 状态覆盖 | Compact Bottom Bar、Medium/Expanded Rail 均接入；切出 Files 恢复主题背景 |
| 截图对比 | 已获取 Figma 节点截图；当前工具无法直接抓取仍被 Flutter attach 占用的有线 iPhone 截图，保留用户现场观感确认 |
| 差异 | 无已知代码差异；仅缺修复后真机截图归档 |
| **自评** | **9.0/10** |

```yaml
skill_run:
  skill: figma-ui
  workflow_stage: story-development
  plan: Plans/功能开发/2026-08-10-workspace-browser.md
  date: 2026-08-10
  contexts_used:
    - path: Contexts/Figma/Figma界面开发最佳实践.md
      utility: high
      reason: "按布局骨架与安全区优先顺序定位外层 Shell 背景，而非继续修改叶子页面"
    - path: Templates/Figma还原自检表.md
      utility: high
      reason: "对照 Figma 节点截图、状态覆盖、差异和真机证据完成增量自检"
  contexts_missing:
    - "Flutter attach 期间从有线 iPhone 非侵入抓取当前页面截图的标准命令"
  contexts_stale: []
  outcome_status: partial
  friction: "CoreDevice 当前不提供 screenshot 子命令，修复后真机截图需用户现场确认"
  revisit_needed: false
```

## 文件操作菜单阴影增量自检

- Figma：页面节点 `30371:41535` 中浮层节点 `33487:14623` 明确为 `drop-shadow 0px 0px 8px rgba(0,0,0,0.1)`。
- 差异根因：Flutter Material `elevation` 是有方向的物理阴影预设，不等价于 Figma blur radius；即使从 4 调至 8，iPhone 截图仍表现为底部偏重、顶部与左右扩散不足。
- 修复：关闭 PopupMenu 的 Material shadow，由自定义 Shape 使用 `BoxShadow(color: 10% black, blurRadius: 4, offset: zero)` 绘制 Figma `8px @2x ÷ 2` 的对称柔光，并以 outside-only path 避免阴影覆盖菜单内容。
- 验证：通过 Flutter VM Inspector 在 Impeller 开启的有线 iPhone 上抓取 `1284×2778` 当前渲染图，修复后菜单四周阴影与 Figma `33487:14622` 截图的扩散方向、范围和灰阶接近；Files `17/17`、Analyze、format、任务命名与 diff check 通过，Flutter attach 保持。
- 自评：`9.8/10`；无已知视觉差异。

```yaml
skill_run:
  skill: figma-ui
  workflow_stage: story-development
  plan: Plans/功能开发/2026-08-10-workspace-browser.md
  date: 2026-08-10
  contexts_used:
    - path: Contexts/Figma/项目设计规范.md
      utility: high
      reason: "按 Effects 节点真值核对 shadow offset、blur 和透明度，并以真机像素截图识别 Material 方向性阴影偏差"
    - path: Contexts/Figma/Figma界面开发最佳实践.md
      utility: high
      reason: "重新读取用户提供的状态 Frame 及浮层子节点，使用显式 BoxShadow 对齐而非继续调 Material elevation"
    - path: Templates/Figma还原自检表.md
      utility: high
      reason: "记录设计值、真机截图对比、差异根因和最终修复状态"
  contexts_missing: []
  contexts_stale: []
  outcome_status: pass
  friction: "原生截图能力不可用且 Impeller 不支持 SKP screenshot，最终通过 Widget Inspector screenshot service 抓取当前 Flutter 渲染"
  revisit_needed: false
```
