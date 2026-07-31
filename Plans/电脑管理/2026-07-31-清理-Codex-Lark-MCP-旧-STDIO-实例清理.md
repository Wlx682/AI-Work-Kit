---
tags: [工作流, computer-mgmt]
type: plan
category: 电脑管理
status: 已完成
date: 2026-07-31
workflow: computer-mgmt
workflow_stage: cleanup
skill: material-prep-assistant
---

# 清理（缓存/临时/无用应用）：Codex Lark MCP 旧 STDIO 实例清理

**工作流**：`computer-mgmt`
**阶段**：`cleanup` / 清理（缓存/临时/无用应用）
**推荐 Skill**：`material-prep-assistant`
**存放路径**：`Plans/电脑管理/2026-07-31-清理-Codex-Lark-MCP-旧-STDIO-实例清理.md`

---

## 一、输入

- 来源：盘点确认旧 STDIO 模式产生多套 Lark MCP，并保留 npx 临时缓存。
- 范围：停止旧 STDIO 实例、移除明文启动参数、清理不再使用的 npx 缓存。
- 非目标：不清空整个 npm 缓存、不删除 Lark OAuth 数据、不删除其他 MCP。

## 二、阶段产出

- [x] Codex 中旧 `command/args` 配置已移除。
- [x] App Secret 不再出现在 Codex 配置或进程参数中。
- [x] 旧 STDIO 进程已退出；未强制终止其他 Node/Codex 进程。
- [x] 旧 npx 缓存 `74dfe5d932228314` 已验证为 Lark MCP 0.5.1 专用环境。
- [x] 101 MiB 旧缓存已移至废纸篓，可恢复。
- [x] 清理后端口 `3000` 仍只有一个回环监听进程。

## 三、清理结果

旧 STDIO 运行路径已完全脱离当前配置。保留固定安装目录、LaunchAgent、钥匙串凭据与 OAuth 数据；没有进行全局 npm 清理或不可恢复删除。


## 四、完成门禁

- `childPlanExists`: True
- `skillRun`: True

> 完成阶段工作后，在本 plan 末尾追加 `skill_run`，再运行 `bash scripts/workflow-gate.sh --workflow computer-mgmt --json`。

## 五、续做

```text
/resume plan=Plans/电脑管理/2026-07-31-清理-Codex-Lark-MCP-旧-STDIO-实例清理.md 进度=【当前完成情况】
```

## 反馈（skill_run）

```yaml
skill_run:
  skill: material-prep-assistant
  plan: Plans/电脑管理/2026-07-31-清理-Codex-Lark-MCP-旧-STDIO-实例清理.md
  date: 2026-07-31
  contexts_used:
    - path: Contexts/MCP/Codex-Lark-MCP单例化配置.md
      utility: high
      reason: "用于约束只清理旧 STDIO 路径、保留单例服务和回滚资料"
  contexts_missing: []
  outcome_status: pass
  revisit_needed: false
```
