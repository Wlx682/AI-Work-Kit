---
tags: [工作流, computer-mgmt]
type: plan
category: 电脑管理
status: 已完成
date: 2026-07-31
workflow: computer-mgmt
workflow_stage: backup
skill: material-prep-assistant
---

# 备份（关键数据/配置）：Codex Lark MCP 单例方案备份与回滚

**工作流**：`computer-mgmt`
**阶段**：`backup` / 备份（关键数据/配置）
**推荐 Skill**：`material-prep-assistant`
**存放路径**：`Plans/电脑管理/2026-07-31-备份-Codex-Lark-MCP-单例方案备份与回滚.md`

---

## 一、输入

- 来源：单例化迁移已完成，需要同时保留迁移前和迁移后的可靠回滚点。
- 范围：备份 Codex 配置、启动脚本、LaunchAgent，校验权限与摘要。
- 非目标：不导出钥匙串中的 App Secret，不复制 Lark OAuth 令牌。

## 二、阶段产出

- [x] 迁移前配置已备份到 `~/.codex/backups/config.toml.20260731-1038-before-lark-http`。
- [x] 迁移后配置、启动脚本和 LaunchAgent 已备份到 `~/.codex/backups/lark-mcp-singleton-20260731/`。
- [x] 备份目录权限为 `700`，文件权限为 `600`。
- [x] 三个迁移后文件均已生成 SHA-256 摘要并核对可读。
- [x] App Secret 仅保存在 macOS 登录钥匙串，没有额外明文导出。

## 三、回滚边界

迁移前备份包含旧 STDIO 命令及凭据环境变量名，但经比对不包含当前 App Secret 实值；文件仍按敏感配置以 `600` 权限保管。恢复旧配置前必须先停止 LaunchAgent；恢复后会重新启用多实例模型，因此仅用于紧急回退。


## 四、完成门禁

- `childPlanExists`: True
- `skillRun`: True

> 完成阶段工作后，在本 plan 末尾追加 `skill_run`，再运行 `bash scripts/workflow-gate.sh --workflow computer-mgmt --json`。

## 五、续做

```text
/resume plan=Plans/电脑管理/2026-07-31-备份-Codex-Lark-MCP-单例方案备份与回滚.md 进度=【当前完成情况】
```

## 反馈（skill_run）

```yaml
skill_run:
  skill: material-prep-assistant
  plan: Plans/电脑管理/2026-07-31-备份-Codex-Lark-MCP-单例方案备份与回滚.md
  date: 2026-07-31
  contexts_used:
    - path: Contexts/MCP/Codex-Lark-MCP单例化配置.md
      utility: high
      reason: "用于确定备份对象、权限边界和回滚顺序"
  contexts_missing: []
  outcome_status: pass
  revisit_needed: false
```
