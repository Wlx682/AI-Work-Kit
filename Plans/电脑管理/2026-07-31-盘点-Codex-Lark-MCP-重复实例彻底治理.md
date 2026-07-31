---
tags: [工作流, computer-mgmt]
type: plan
category: 电脑管理
status: 已完成
date: 2026-07-31
workflow: computer-mgmt
workflow_stage: inventory
skill: material-prep-assistant
---

# 盘点（磁盘/应用/启动项/大文件）：Codex Lark MCP 重复实例彻底治理

**工作流**：`computer-mgmt`
**阶段**：`inventory` / 盘点（磁盘/应用/启动项/大文件）
**推荐 Skill**：`material-prep-assistant`
**存放路径**：`Plans/电脑管理/2026-07-31-盘点-Codex-Lark-MCP-重复实例彻底治理.md`

---

## 一、输入

- 来源：用户反馈电脑卡顿；进程采样发现 Codex 下存在多套 Lark MCP。
- 范围：盘点安装来源、配置定义、进程父子关系、传输模式、内存占用与可替代架构。
- 非目标：不删除 Lark 账号、不改变飞书应用权限、不改业务数据。

## 二、阶段产出

- [x] Codex 配置只有一个 `mcp_servers.lark_mcp`。
- [x] npm 全局没有安装 Lark MCP。
- [x] npx 缓存只有一份 `@larksuiteoapi/lark-mcp@0.5.1`。
- [x] 实测 4 套逻辑服务均由同一个 Codex host 拉起，每套为 `npm + node`。
- [x] 单个 `node` 服务约 647–681 MiB，4 套合计接近 2.9 GiB。
- [x] 确认包支持 Streamable HTTP，端点为 `/mcp`，支持 OAuth 发现。
- [x] 确认 Codex 官方配置支持以 `url` 连接 Streamable HTTP MCP。
- [x] 形成长期资料：`Contexts/MCP/Codex-Lark-MCP单例化配置.md`。

## 三、盘点结论

不是重复安装。根因是旧配置使用本地 STDIO：Codex 的多个内部会话分别启动 Lark MCP，且旧进程未及时回收。重新安装同一 npm 包不能解决；应改为一套本机 Streamable HTTP 服务供各会话复用。

## 四、完成门禁

- `childPlanExists`: True
- `skillRun`: True

> 完成阶段工作后，在本 plan 末尾追加 `skill_run`，再运行 `bash scripts/workflow-gate.sh --workflow computer-mgmt --json`。

## 五、续做

```text
/resume plan=Plans/电脑管理/2026-07-31-盘点-Codex-Lark-MCP-重复实例彻底治理.md 进度=【当前完成情况】
```

## 反馈（skill_run）

```yaml
skill_run:
  skill: material-prep-assistant
  plan: Plans/电脑管理/2026-07-31-盘点-Codex-Lark-MCP-重复实例彻底治理.md
  date: 2026-07-31
  contexts_used:
    - path: Contexts/MCP进阶指南.md
      utility: high
      reason: "用于核对本库既有 MCP 配置原则、单服务约束和验证方式"
  contexts_missing:
    - "Codex 本地 STDIO MCP 多会话进程生命周期说明"
  outcome_status: pass
  friction: "material-prep-assistant 偏 PM 对接物料，电脑管理盘点缺少系统诊断专用字段"
  revisit_needed: false
```
