---
tags: [功能开发, 用户故事, TDD, files]
type: plan
category: 功能开发
status: 进行中
date: 2026-08-10
lifecycle_state: story-development
parent: Plans/功能开发/2026-08-10-workspace-browser.md
requirement_plan: Plans/需求分析/2026-08-10-workspace-browser.md
architecture_plan: Plans/技术方案/2026-08-10-workspace-browser.md
story_id: US-002
story_points: 8
sprint_scope: true
tdd_evidence: Plans/功能开发/2026-08-10-workspace-browser-US-002.tdd.json
implementation_design: Plans/功能开发/2026-08-10-workspace-browser-US-002.impl.json
---
# US-002：文件目录独立页面、统一面包屑与完整动作菜单

AC1 用户上传与工作空间的可导航目录点击后 push 独立页面，返回时首页状态不被覆盖；AC2 AI 文件更多菜单按 iOS 条件展示分享、下载、导出、附件发送、引用、查看任务文件和查看原对话；AC3 用户上传文件展示分享、下载、移动、删除、重命名，文件夹仅展示移动、删除、重命名；AC4 工作空间文件展示 iOS 默认动作并按渠道与会话能力追加动作；AC5 三类目录页统一使用 Figma `30371:42190` / iOS `BreadcrumbView` 的 12px、4px 间距、12px 分隔符、当前层强调和横向滚动样式。

底层下载、系统分享导出、附件发送及引用能力若尚未由独立正式任务交付，菜单必须显式反馈不可用，不得冒充成功；已有 `filesystem.download/share/upload-yunpan` typed RPC 可在当前 owner fence 下复用。

## 实现与验收结果

- 用户上传与工作空间目录使用独立 `MaterialPageRoute` 和独立 Controller；逐层进入会继续 push，返回后父页查询、分页和列表状态不变。
- 用户上传与工作空间目录页统一压入应用根 Navigator；Compact 二级页覆盖底部 Tab，返回时恢复 Shell 与父列表状态。
- 亮暗主题统一设置 AppBar 标题居中；文件首页、用户上传目录和工作空间目录同时显式锁定屏幕中心线。目录页使用对称的左右操作区，长标题在 320/360/390pt、3 倍字体与 LTR/RTL 下仍保持画板居中。
- 三类目录页统一使用共享 `FileBreadcrumb`，对齐 Figma `30371:42190` 与固定 iOS `BreadcrumbView`。
- 三类更多菜单统一使用 `FileActionMenuButton`，动作集合按固定 iOS 条件生成；用户上传文件 5 项、文件夹 3 项，AI 与工作空间菜单不再被禁用或缺失。
- 三类 push 目录页会观察 runtime owner；切号或 Gateway 换代时立即清空并关闭旧页面，面包屑按真实 Navigator 栈返回祖先层级。用户上传目录页补齐搜索与当前路径新增入口。
- 本地目标隐藏导出；附件发送通过 iOS 同款 `channel.link batch_get` 六渠道凭证规则、云控版本及 owner fence 生成，原对话要求 sessionKey/sessionId 双字段。尚未安装系统分享/落盘等下游消费链的动作显式提示不可用，不发送 RPC、不冒充成功。
- 搜索直达深层目录时，面包屑对已入栈祖先执行 pop，对未入栈祖先执行 replace，始终保留 Files 根页。
- 面包屑短层级按内容宽度从左侧连续排列，单层文字最大宽度 200pt；超长路径保持省略与横向滚动，不再把每段拉伸成离散的 200pt 块。
- 用户上传二级目录的搜索与加号恢复为 Figma/iOS 同款 36pt 透明资源画布，不再二次缩小到 24pt；仍保留 48pt 可点击热区。
- 工作空间进入子层级并显示面包屑时，移除面包屑与文件列表之间的 1pt `Divider`，保持与 Figma/iOS 一致的连续白色背景。
- 自动化回归 `218/218` 通过；有线 iPhone 已确认真实用户上传数据、独立目录页面覆盖底部 Tab、居中标题、统一面包屑及文件 5 项菜单，Flutter attach 持续保持。

当前保持 `PARTIAL`：真实 Gateway 渠道能力探测、系统分享/保存、导出到用户上传、引用、查看任务文件及原对话的最终业务跳转仍需对应正式任务落地。

## Figma 还原自检（面包屑）

| 项目 | 结论 |
|---|---|
| 节点 | `30371:42190` |
| 布局 | 左边距 16pt，内容抱紧并从左侧连续排列 |
| 层级间距 | 4pt + 12pt 箭头 + 4pt |
| 宽度约束 | 单段最大 200pt，超长文本省略；整条路径可横向滚动 |
| 字体与颜色 | 12pt；祖先 50% 黑，当前层 90% 黑并加粗 |
| 交互与可访问性 | 祖先可点，当前层不可点；动态字体点击高度不低于 44pt |
| 导航栏标题 | 文件首页与两类目录页标题均落在画板中心线；左右操作区不对称时仍保持居中 |
| 导航按钮 | Figma `30371:41540/41547` 与 iOS `NMCloudDriveNavBar` 均为 36pt 资源画布；Flutter 二级页搜索/加号已由 24pt 修正为 36pt，实际图形约 18–19pt |
| 面包屑与列表 | 中间无分割线，白色背景连续；无面包屑的独立工具栏仍可保留自身分隔语义 |

自检评分：`10/10`。已用 Figma 截图与有线 iPhone 热重载截图核对，未发现本次范围内的残余视觉偏差。

## 反馈（skill_run）

```yaml
skill_run:
  skill: figma-ui
  plan: Plans/功能开发/2026-08-10-workspace-browser-US-002.md
  date: 2026-08-10
  contexts_used:
    - path: Contexts/Figma/Figma-MCP配置.md
      utility: high
      reason: 明确使用节点级 get_design_context 与截图取证流程
    - path: Contexts/Figma/项目设计规范.md
      utility: high
      reason: 约束 Flutter 复用共享组件并保持跨尺寸适配
    - path: Contexts/Figma/Figma界面开发最佳实践.md
      utility: high
      reason: 指导先锁定几何回归再进行真机热重载比对
  contexts_missing: []
  contexts_stale: []
  outcome_status: pass
  revisit_needed: false
```

```yaml
skill_run:
  skill: figma-ui
  plan: Plans/功能开发/2026-08-10-workspace-browser-US-002.md
  date: 2026-08-10
  contexts_used:
    - path: Contexts/Figma/Figma-MCP配置.md
      utility: high
      reason: 复用已读取的工作空间详情节点确认面包屑下无分割线
    - path: Contexts/Figma/项目设计规范.md
      utility: high
      reason: 以节点可见元素为依据移除代码额外添加的 Divider
    - path: Contexts/Figma/Figma界面开发最佳实践.md
      utility: high
      reason: 通过层级回归和生产 push 页回归锁定连续白色背景
  contexts_missing: []
  contexts_stale: []
  outcome_status: pass
  revisit_needed: false
```

```yaml
skill_run:
  skill: figma-ui
  plan: Plans/功能开发/2026-08-10-workspace-browser-US-002.md
  date: 2026-08-10
  contexts_used:
    - path: Contexts/Figma/Figma-MCP配置.md
      utility: high
      reason: 通过 get_design_context 直读导航按钮 72px@2x 的节点尺寸
    - path: Contexts/Figma/项目设计规范.md
      utility: high
      reason: 按 @2x 除二规则将设计按钮映射为 36pt 资源画布
    - path: Contexts/Figma/Figma界面开发最佳实践.md
      utility: high
      reason: 用节点度量、回归测试与真机热重载截图闭环缩放偏差
  contexts_missing: []
  contexts_stale: []
  outcome_status: pass
  revisit_needed: false
```

```yaml
skill_run:
  skill: feature-dev-assistant
  workflow_stage: story-development
  plan: Plans/功能开发/2026-08-10-workspace-browser-US-002.md
  date: 2026-08-10
  contexts_used:
    - path: Plans/功能开发/2026-08-10-workspace-browser-US-002.impl.json
      utility: high
      reason: 约束用户上传与工作空间详情使用独立路由且不破坏父列表状态
    - path: Plans/功能开发/2026-08-10-workspace-browser-US-002.tdd.json
      utility: high
      reason: 记录底部 Tab 覆盖与长标题几何居中问题的 Red、Green 与 218 项回归证据
  contexts_missing: []
  contexts_stale: []
  outcome_status: pass
  revisit_needed: false
```

```yaml
skill_run:
  skill: figma-ui
  plan: Plans/功能开发/2026-08-10-workspace-browser-US-002.md
  date: 2026-08-10
  contexts_used:
    - path: Contexts/Figma/Figma-MCP配置.md
      utility: high
      reason: 使用节点级设计上下文和设计截图确认标题画板中心线
    - path: Contexts/Figma/项目设计规范.md
      utility: high
      reason: 将节点约束映射为 Flutter 全局主题和局部 AppBar 显式规则
    - path: Contexts/Figma/Figma界面开发最佳实践.md
      utility: high
      reason: 通过几何回归与真机热重载截图完成视觉闭环
  contexts_missing: []
  contexts_stale: []
  outcome_status: pass
  revisit_needed: false
```
