---
tags: [工作流, computer-mgmt]
type: plan
category: 电脑管理
status: 已完成
date: 2026-07-31
workflow: computer-mgmt
workflow_stage: review
skill: code-review
---

# 复核（结果核对 + 归档）：Codex Lark MCP 单例化最终复核

**工作流**：`computer-mgmt`
**阶段**：`review` / 复核（结果核对 + 归档）
**推荐 Skill**：`code-review`
**存放路径**：`Plans/电脑管理/2026-07-31-复核-Codex-Lark-MCP-单例化最终复核.md`

---

## 一、输入

- 来源：用户反馈 Lark 出现 4 套实例，并在单例化迁移后先后遇到 OAuth 错误码 20028、20029。
- 范围：复核根因、单例进程模型、OAuth 配置、密钥边界、文件权限、资源改善和回滚资料。
- 非目标：不代替组织管理员轮换飞书 App Secret；不在本任务中重启当前 Codex 桌面会话。

## 二、Findings（按严重级）

**当前未发现阻塞问题。**

### 高（已修复）

1. **初次凭据迁移取到了环境变量名文本，导致 OAuth 报错 20028。**
   - 位置：`~/.local/bin/codex-lark-mcp-server:9-20`
   - 处理：从当前 Codex 环境取出实际 App ID/Secret 后写入 macOS 登录钥匙串；启动脚本只按钥匙串服务名读取。
   - 验证：App ID 格式与长度检查通过，飞书/Lark tenant token 官方端点均返回 HTTP 200、业务码 0；`codex mcp login lark_mcp` 成功。

### 中（已修复）

1. **服务最初改用端口 17345，与飞书应用已登记的 OAuth 回调不一致，导致错误码 20029。**
   - 位置：`~/.local/bin/codex-lark-mcp-server:23-30`、`~/.codex/config.toml:92-93`
   - 处理：统一为 `http://localhost:3000/mcp`，回调使用 `http://localhost:3000/callback`。
   - 验证：OAuth 登录完成；Codex 显示传输类型为 `streamable_http`。
2. **Codex shell snapshot 曾保存两项 Lark 凭据导出，且部分文件权限偏宽。**
   - 位置：`~/.codex/shell_snapshots/`
   - 处理：精确移除 10 个快照中的 20 行 Lark 凭据导出并收紧为 `600`，未删除快照其他内容。
   - 验证：`^export LARK_MCP_APP_(ID|SECRET)=` 复扫为 0。
3. **服务日志初始权限偏宽。**
   - 位置：`~/Library/LaunchAgents/com.wanglongxiang.codex-lark-mcp.plist:28-32`
   - 处理：日志目录改为 `700`，stdout/stderr 改为 `600`。

### 建议 / 残余风险

1. 旧 STDIO 进程参数曾携带 App Secret。当前本机残留已清理，但仍建议由飞书应用管理员轮换一次 App Secret。
2. `@larksuiteoapi/lark-mcp@0.5.1` 已固定安装，但 npm 报告其传递依赖 `prebuild-install@7.1.3` 已废弃；后续升级前需先做 OAuth 与工具调用回归。
3. 当前 Codex 会话无法在不中断本任务的情况下完成“彻底退出并重开 Codex、再并行打开多个任务”的最终场景测试；这是唯一的人工复测缺口，不影响现有单例服务运行。

## 三、复核摘要

- [x] 不属于重复安装：全局无重复包，旧 npx 缓存仅一份。
- [x] 旧 4 套逻辑服务已退出；当前仅 1 个 `node` 进程监听 `[::1]:3000`。
- [x] 当前 Codex Lark 配置只含一个 HTTP URL，没有 STDIO `command/args`。
- [x] LaunchAgent 状态为 `running`，PID 与唯一监听进程一致。
- [x] 启动脚本通过 `zsh -n`，plist 通过 `plutil -lint`。
- [x] 未授权 MCP 初始化请求返回 `401`；OAuth 元数据端点返回 `200`。
- [x] App Secret 不在当前配置、脚本、plist、进程参数或 shell snapshot 中。
- [x] 性能复核：CPU 约 `85% idle`，系统内存空闲压力指标 `57%`，负载降至 `1.71 / 2.28 / 3.33`。
- [x] 迁移前/迁移后备份及回滚说明齐全。

结论：单例化方案达到放行条件。此前 4 个实例的根因是 STDIO 会话各自拉起本地服务，不是重复安装；切换为 launchd 托管的单个 Streamable HTTP 服务后，进程数量与资源占用均恢复正常。

## 四、完成门禁

- `childPlanExists`: True
- `skillRun`: True

> 完成阶段工作后，在本 plan 末尾追加 `skill_run`，再运行 `bash scripts/workflow-gate.sh --workflow computer-mgmt --json`。

## 五、续做

```text
/resume plan=Plans/电脑管理/2026-07-31-复核-Codex-Lark-MCP-单例化最终复核.md 进度=【当前完成情况】
```

## 反馈（skill_run）

```yaml
skill_run:
  skill: code-review
  plan: Plans/电脑管理/2026-07-31-复核-Codex-Lark-MCP-单例化最终复核.md
  date: 2026-07-31
  contexts_used:
    - path: Contexts/MCP/Codex-Lark-MCP单例化配置.md
      utility: high
      reason: "用于逐项复核根因、单例架构、OAuth 回调、安全边界和回滚标准"
  contexts_missing: []
  contexts_stale: []
  outcome_status: pass
  revisit_needed: false
```
