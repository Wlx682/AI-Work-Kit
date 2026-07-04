---
tags: [功能开发, web, 子任务]
type: plan
category: 功能开发
status: 草稿
date: 2026-07-04
lifecycle_state: development
parent: Plans/功能开发/2026-07-04-纳米P视频web首页.md
epic: Plans/Epic/2026-07-04-纳米P视频web首页.md
含业务逻辑: 是
---

# 子任务 T05：埋点接入 + 全 Variant（空/错误态）

**parent**：`Plans/功能开发/2026-07-04-纳米P视频web首页.md`

## 输入
- tracking 封装壳（T01）、各区块组件（T02/T03/T04 就位）。
- PRD §9 埋点清单（key=namivideo_home，show/click/hover）。

## 输出
- 各区块接入埋点：首页曝光、主导航/资产库/登录/胶囊/头像/菜单项点击、Banner 曝光/点击/翻屏、工具项/查看更多、Tab 切换、子分组曝光/横滑、卡片曝光/点击/一键同款/悬停。
- 去重防抖：show 会话去重、hover ≥2s 会话去重仅内容卡片、click 300ms 首次 / Tab 切换取最后。
- 全 Variant 补齐：各区块空态 / 错误态 / 加载态视觉走查对齐。

## 验收
- 埋点字段（key/action/attr/ext/ext2/type/position/work_id/tab_name）按清单正确；必填缺失不上报 + dev warning。
- 上报失败静默不重试不阻断；积分面板曝光/CTA 归全局组件不重复上报。
- 各区块空/错误/加载 Variant 与设计一致。

## 依赖
- T02、T03、T04。

## 覆盖
| GWT | 说明 |
|-----|------|
| 埋点用例 | UT-1801/1802/1803 去重防抖/必填校验 |
| 各区块 Variant | B1-B23 边界视觉态 |

## WBS 切片状态
| # | 切片 | 状态 |
|---|------|------|
| 10 | 埋点接入 + 全 Variant（内层 TDD 补充见 T06） | ⬜ |

## 续做
`/resume plan=Plans/功能开发/2026-07-04-纳米P视频web首页-子任务05-埋点与Variant.md`
