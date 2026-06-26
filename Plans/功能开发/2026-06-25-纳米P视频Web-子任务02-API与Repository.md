---
tags: [功能开发, 子任务, 纳米P视频]
type: plan
category: 功能开发
status: 已完成
date: 2026-06-25
epic: Plans/Epic/2026-06-25-纳米P视频Web.md
parent: Plans/功能开发/2026-06-25-纳米P视频Web.md
lifecycle_state: development
skill: feature-dev-assistant
wbs: 5
relations:
  depends_on:
    - Plans/功能开发/2026-06-25-纳米P视频Web-子任务01-脚手架与路由.md
  dependents: []
  supersedes: []
  superseded_by: []
  conflicts: []
---

# 子任务 02：API 与 Repository

**WBS**：#5

## 目标

Axios 实例（`withCredentials`）；统一 `code` 解析；实现 Task/Config/Material/Effect Repository 与 DTO 类型；接口 path 从 `接口索引.md` 读取（待核对标记）。

## 验收

- [x] 401/102009 触发登录拦截 hook
- [x] 510001–510003 映射为 typed error
- [x] Repository 单元可 mock 测试（vitest 6 passed）

## 续做

```
/resume plan=Plans/功能开发/2026-06-25-纳米P视频Web-子任务03-首页UI.md
```

---

## 反馈（skill_run）

```yaml
skill_run:
  skill: feature-dev-assistant
  plan: Plans/功能开发/2026-06-25-纳米P视频Web-子任务02-API与Repository.md
  date: 2026-06-25
  contexts_used:
    - path: Plans/功能开发/2026-06-25-纳米P视频Web-接口索引.md
      utility: high
      reason: "endpoint 路径与业务码真理源"
  contexts_missing: []
  contexts_stale: []
```
