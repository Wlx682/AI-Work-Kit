---
tags: [工作流, computer-mgmt]
type: plan
category: 电脑管理
status: 已完成
date: 2026-07-31
workflow: computer-mgmt
workflow_stage: harden
skill: material-prep-assistant
---

# 加固（安全/权限/更新）：Codex Lark MCP 单例服务安全加固

**工作流**：`computer-mgmt`
**阶段**：`harden` / 加固（安全/权限/更新）
**推荐 Skill**：`material-prep-assistant`
**存放路径**：`Plans/电脑管理/2026-07-31-加固-Codex-Lark-MCP-单例服务安全加固.md`

---

## 一、输入

- 来源：Streamable HTTP 单例服务已运行，需要验证本机边界、凭据、文件权限和 OAuth 防护。
- 范围：监听地址、进程模型、密钥暴露、钥匙串、文件权限、未授权访问与 OAuth 发现。
- 非目标：不自动轮换飞书开放平台 App Secret，不扩大监听范围。

## 二、阶段产出

- [x] 服务只监听 `localhost:3000` 的回环地址，没有暴露到局域网或公网。
- [x] 端口只有一个监听进程，LaunchAgent 状态为 `running`。
- [x] 6 个旧 STDIO 进程已精确退出，释放约 1.16 GiB RSS。
- [x] App ID 与 App Secret 均存在 macOS 登录钥匙串。
- [x] App Secret 不存在于当前 Codex 配置、启动脚本、LaunchAgent 或进程参数。
- [x] `config.toml` 权限为 `600`，启动脚本为 `700`，plist 语法校验通过。
- [x] 清理 10 个 Codex shell snapshot 中 20 行历史 Lark 凭据导出，并将相关快照权限收紧为 `600`；复扫结果为 0。
- [x] 日志目录权限为 `700`，stdout/stderr 日志权限为 `600`。
- [x] 未授权 `/mcp` 请求返回 `401`。
- [x] OAuth 发现端点返回 `200`。

## 三、剩余安全动作

旧密钥曾出现在历史 STDIO 进程参数中。当前本机暴露已消除；密钥轮换需要在飞书开放平台执行，留给用户按组织权限决定。


## 四、完成门禁

- `childPlanExists`: True
- `skillRun`: True

> 完成阶段工作后，在本 plan 末尾追加 `skill_run`，再运行 `bash scripts/workflow-gate.sh --workflow computer-mgmt --json`。

## 五、续做

```text
/resume plan=Plans/电脑管理/2026-07-31-加固-Codex-Lark-MCP-单例服务安全加固.md 进度=【当前完成情况】
```

## 反馈（skill_run）

```yaml
skill_run:
  skill: material-prep-assistant
  plan: Plans/电脑管理/2026-07-31-加固-Codex-Lark-MCP-单例服务安全加固.md
  date: 2026-07-31
  contexts_used:
    - path: Contexts/MCP/Codex-Lark-MCP单例化配置.md
      utility: high
      reason: "用于逐项核对监听、凭据、文件权限和 OAuth 安全边界"
  contexts_missing: []
  outcome_status: pass
  revisit_needed: false
```
