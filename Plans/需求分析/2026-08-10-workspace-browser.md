---
tags: [需求分析, workspace]
type: plan
category: 需求分析
status: 已采纳
date: 2026-08-10
lifecycle_state: requirement
source_of_truth: true
epic: Plans/Epic/2026-08-10-workspace-browser.md
p0_open: 0
---
# 需求分析：工作区文件分层浏览与搜索

作为已连接 Gateway 的用户，我要按专家→会话→文件/过程文件分层浏览，并能搜索会话或最终文件，以找到工作产物。

- 根层按 offset 分页专家；专家层按 timestamp cursor 分页会话；会话层按 offset 分页 final/process 文件。
- 根层没有 keyword 能力；专家层搜索会话；全局搜索使用 finals。缺少的搜索能力必须显式降级。
- owner 固定为 environment/account/Gateway stableID/generation；迟到请求不可覆盖新 owner。
- 刷新失败保留旧数据；加载更多失败保留已合并页并可重试。
- Compact 为单栏逐层导航；Medium/Expanded 为双栏，窗口切换保持 selection、query 和分页状态。
- 本轮不包含文件编辑、下载、分享、发送 IM。

## 边界情况清单

| 场景 | 期望 |
|---|---|
| 空专家/会话/文件列表 | 保留刷新和返回能力，显示对应空态 |
| agent/file 多页重复节点 | 按稳定 identity 去重，保留服务端顺序 |
| session `has_more=true` 但游标缺失 | 显式 codec failure，不重复请求首页 |
| final 首页含过程文件虚拟目录 | 点击后以同 sessionId、`scope=process` 独立分页 |
| 快速切 agent/session/搜索 | 旧 generation 结果丢弃 |
| 窗口跨三档变化 | 不重建 Controller，不清 selection/query/page |

## 异常流程矩阵

| 异常 | 用户反馈 | 恢复 |
|---|---|---|
| Gateway 未连接/连接失败 | 首屏错误或旧数据上的局部错误 | 重试当前 route |
| 权限/业务拒绝 | 显式安全错误，不显示假空列表 | 修复权限后重试 |
| 首屏 codec 失败 | 错误态 | 重试并保留诊断 code |
| 分页失败 | 保留已加载项目并显示重试入口 | 仅重试同 cursor |
| owner 切换 | 不展示旧成功或旧错误 | 新 owner 从根加载 |

## 验收标准

- [ ] 根层专家 offset 分页、专家层会话 timestamp 分页、文件层 offset 分页均可重复验证。
- [ ] session query 和 global finals 搜索不混用；根层搜索能力缺失有明确降级。
- [ ] 过程文件虚拟目录可进入、返回和分页。
- [ ] 刷新/分页失败保留可用旧数据；重试不跳层、不重复合并。
- [ ] owner/generation 变化后旧回调无法写入当前 UI。
- [ ] Compact/Medium/Expanded 切换保持 route、selection、query 和已加载页。
- [ ] Files Tab 使用生产 Gateway 接线；真实 Gateway 与五形态设备证据不足时保持 PARTIAL。

## 反馈（skill_run）

```yaml
skill_run:
  skill: requirement-analyst
  workflow_stage: requirement
  plan: Plans/需求分析/2026-08-10-workspace-browser.md
  date: 2026-08-10
  contexts_used:
    - path: Contexts/需求分析/需求分析规范.md
      utility: high
      reason: "用边界、异常矩阵和可测验收标准收敛工作区分层浏览与搜索需求。"
  contexts_missing: []
  contexts_stale: []
  outcome_status: pass
  revisit_needed: false
```
