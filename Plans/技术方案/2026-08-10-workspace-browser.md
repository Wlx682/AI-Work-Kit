---
tags: [技术方案, workspace]
type: plan
category: 技术方案
status: 已采纳
date: 2026-08-10
lifecycle_state: architecture
epic: Plans/Epic/2026-08-10-workspace-browser.md
---
# 技术方案：工作区文件分层浏览与搜索

- ADR-001：Feature 采用 Presentation→Application→Domain Repository→Data Adapter→现有 FilesystemGateway；不复用泄漏多域职责的旧 CloudDriveSdk。
- ADR-002：分页游标按层级建模：agent/file 用 offset，session 用 before timestamp；每次请求捕获 route/query/cursor/generation。
- ADR-003：稳定 identity 优先使用 agent sessionKey、sessionId、file outputId/fileId/path；分页 merge 去重但不跨层复用。
- ADR-004：非空搜索统一走 canonical `filesystem.ws.search`：root=global mixed union、agent=session+file、session/process=session+scope file；旧网关仅在 `METHOD_NOT_FOUND` 时显式 capability 降级。
- ADR-005：Compact 单栏；Medium/Expanded 双栏列表+当前层，二者共享同一 Controller，不因窗口变化重发请求。
- ADR-006：Files Tab 共享宿主与 l10n 由当前串行集成 Owner 接线。

## 反馈（skill_run）

```yaml
skill_run:
  skill: architecture-design-assistant
  workflow_stage: architecture
  plan: Plans/技术方案/2026-08-10-workspace-browser.md
  date: 2026-08-10
  contexts_used:
    - path: Contexts/需求分析/需求分析产出标准.md
      utility: high
      reason: "由已采纳需求的分页、搜索、身份隔离和响应式边界反推模块与接口契约。"
  contexts_missing: []
  contexts_stale: []
  outcome_status: pass
  revisit_needed: false
```
