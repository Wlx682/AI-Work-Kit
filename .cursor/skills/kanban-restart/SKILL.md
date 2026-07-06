---
name: kanban-restart
description: 重启 Epic Web 看板服务（kanban-server）。用户说「重启看板」「看板重启」「重启 kanban」「kanban 重启」「刷新看板服务」「restart kanban」时触发；停掉现有 kanban-server.py 进程再用 scripts/kanban-server.sh 拉起，让改动过的看板代码生效，并做 HTTP 健康检查。不响应：改看板页面/后端内容→workflow-evolution-assistant；部署/同步 Skill→skill-sync。
---

# 重启看板

定位：**运维 Skill**，只负责重启 Epic Web 看板服务进程，不改任何看板代码或数据。

## 触发

- 重启看板、看板重启、重启 kanban、kanban 重启、刷新看板服务、拉起看板
- `restart kanban`、`/kanban-restart`

## 不触发

- 改看板页面/后端逻辑（kanban-server.py、kanban/*.html）→ `workflow-evolution-assistant`
- 部署/同步 Skill → `skill-sync`
- 看 Epic 进度/审计状态 → `dev-lifecycle-audit-assistant`（那是读数据，不是重启服务）

## 背景

- 服务脚本：`scripts/kanban-server.sh`（默认后台启动 `scripts/kanban-server.py`，端口 `KANBAN_PORT`，默认 7777，日志 `/tmp/kanban.log`）。
- 脚本自带「端口已在监听则直接退出」保护——所以**必须先停旧进程，否则重启是空操作、旧代码继续跑**。改过 kanban-server.py 后尤其要重启才生效。

## 执行

1. 查现有进程：
   ```bash
   ps aux | grep kanban-server.py | grep -v grep
   ```
2. 停旧进程（先温和 kill 已知 PID，端口仍占再强杀），确认端口释放：
   ```bash
   pkill -f kanban-server.py; sleep 1
   lsof -nP -iTCP:"${KANBAN_PORT:-7777}" -sTCP:LISTEN >/dev/null 2>&1 && { pkill -9 -f kanban-server.py; sleep 1; }
   ```
3. 重启：
   ```bash
   bash scripts/kanban-server.sh
   ```
4. 健康检查（首页 + 关键接口应 200）：
   ```bash
   curl -s -o /dev/null -w "首页 HTTP %{http_code}\n" "http://127.0.0.1:${KANBAN_PORT:-7777}/"
   curl -s -o /dev/null -w "/api/tests HTTP %{http_code}\n" "http://127.0.0.1:${KANBAN_PORT:-7777}/api/tests"
   ```
5. 汇报：停了哪个 PID、新地址、健康检查结果。启动失败则贴 `/tmp/kanban.log` 末尾。

## 注意

- `pkill -f kanban-server.py` 只杀看板进程，进程名精确、误伤面小；仍应先 `ps` 确认目标。
- 重启是可逆常规运维；无破坏性数据操作。
- 若端口被非看板进程占用，先排查占用者（`lsof -nP -iTCP:7777`），不要盲目强杀。

## 反馈回路

任务结束按 `Contexts/决策/Skill反馈协议.md` 输出 `skill_run` YAML 块（无 plan → 追加到 `Contexts/决策/孤立反馈记录.md` 顶部）。
