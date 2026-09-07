---
tags: [MCP, Codex, Lark, 性能, 电脑管理]
date: 2026-07-31
status: 已验证
---

# Codex Lark MCP 单例化配置

> 用于解决 Codex 以本地 STDIO 方式反复启动 Lark MCP、造成多进程和高内存占用的问题。

## 根因结论

- 本机不存在重复安装：无全局 npm 安装，npx 缓存只有一份 `@larksuiteoapi/lark-mcp@0.5.1`。
- Codex 全局配置只有一个 `mcp_servers.lark_mcp` 定义。
- 旧配置使用 STDIO。每套服务由一个 `npm` 启动器和一个 `node` 服务组成；多个 Codex 内部会话会各自启动一套本地进程。
- 实测曾同时存在 4 套逻辑服务（8 个进程），每个 `node` 服务约占 647–681 MiB。
- 因此，重装 npm 包不会解决重复实例；根因是 STDIO 传输的进程模型与旧实例回收不及时。

## 已采用架构

| 项目 | 配置 |
|---|---|
| Lark MCP 版本 | `0.5.1`，固定安装 |
| 安装目录 | `~/.local/share/codex-lark-mcp` |
| 启动脚本 | `~/.local/bin/codex-lark-mcp-server` |
| LaunchAgent | `~/Library/LaunchAgents/com.wanglongxiang.codex-lark-mcp.plist` |
| 监听地址 | `http://localhost:3000/mcp`（仅回环） |
| Codex 配置 | `[mcp_servers.lark_mcp]` 使用 `url`，不再使用 `command/args` |
| 凭据 | macOS 登录钥匙串，不出现在配置文件和进程参数中 |
| 日志 | `~/Library/Logs/CodexLarkMCP/`（目录 `700`，文件 `600`） |

服务仅监听回环地址，不对局域网或公网开放。Lark MCP 使用 Streamable HTTP，并提供标准 OAuth 发现端点。

## 常用检查

```bash
lsof -nP -iTCP:3000 -sTCP:LISTEN
launchctl print "gui/$(id -u)/com.wanglongxiang.codex-lark-mcp"
tail -n 50 ~/Library/Logs/CodexLarkMCP/stderr.log
launchctl kickstart -k "gui/$(id -u)/com.wanglongxiang.codex-lark-mcp"
```

## 验证标准

- 端口 `3000` 只有一个回环监听进程。
- Codex 配置中 Lark 只有 `url`，没有 `command` 或 `args`。
- 进程列表中没有多套 `npm exec @larksuiteoapi/lark-mcp`。
- 重启 Codex、开启多个任务后，仍只有一个 Lark MCP 常驻进程。
- `/mcp` 首次连接可完成 OAuth，之后 Lark 工具可正常调用。

选择 `localhost:3000` 是为了复用 Lark MCP 官方默认 OAuth 回调
`http://localhost:3000/callback`；若改端口，必须先在飞书开放平台同步新增精确回调 URL。

Codex shell snapshot 中历史遗留的 `LARK_MCP_APP_ID` / `LARK_MCP_APP_SECRET`
导出行已定向清除，快照其他内容保留，复扫结果为 0。

## 回滚

原始 Codex 配置备份：

`~/.codex/backups/config.toml.20260731-1038-before-lark-http`

回滚时先卸载 LaunchAgent，再恢复备份配置并完全重启 Codex。恢复旧配置会重新启用 STDIO 多实例模型，只用于故障回退。

## 安全提醒

旧 STDIO 命令曾把 Lark App Secret 放在进程参数中。新方案已移入钥匙串，但历史密钥仍建议在飞书开放平台轮换一次。
