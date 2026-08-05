# 重启看板 Skill

> 存放规则 → [[Contexts/决策/Kit核心原则]] · 工作流 → [[Contexts/决策/AI-Work-Kit工作流总览]]

定位：**运维 Skill**，只负责重启 Epic Web 看板服务进程，不改任何看板代码或数据。与 [[Skills/skill_sync]] 同属运维类。

## 触发条件

- 「重启看板」「看板重启」「重启 kanban」「kanban 重启」「刷新看板服务」「拉起看板」
- `restart kanban`、`/kanban-restart`

**不触发（让位）**：

- 改看板页面/后端逻辑（`scripts/kanban-server.py`、`scripts/kanban/*.html`）→ `workflow-evolution-assistant`
- 部署/同步 Skill → `skill-sync`
- 看 Epic 进度/审计状态（读数据而非重启服务）→ `dev-lifecycle-audit-assistant`

## 背景：为什么要「先停再启」

- 服务脚本：`scripts/kanban-server.sh`，默认后台启动 `scripts/kanban-server.py`，端口 `KANBAN_PORT`（默认 7777），日志 `/tmp/kanban.log`。
- 该脚本有一段保护：**端口已在监听就直接退出**。所以如果不先停旧进程，直接跑脚本是空操作——旧进程（旧代码）继续跑，重启没生效。
- 典型场景：改过 `kanban-server.py` 后，必须重启才让新代码生效；否则页面看到的还是旧逻辑。

## 执行步骤

1. **查现有进程**：
   ```bash
   ps aux | grep kanban-server.py | grep -v grep
   ```
2. **停旧进程**（先温和停，端口仍占再强杀），确认端口释放：
   ```bash
   pkill -f kanban-server.py; sleep 1
   lsof -nP -iTCP:"${KANBAN_PORT:-7777}" -sTCP:LISTEN >/dev/null 2>&1 && { pkill -9 -f kanban-server.py; sleep 1; }
   ```
3. **重启**：
   ```bash
   bash scripts/kanban-server.sh
   ```
4. **健康检查**（首页 + 关键接口应返回 200）：
   ```bash
   curl -s -o /dev/null -w "首页 HTTP %{http_code}\n" "http://127.0.0.1:${KANBAN_PORT:-7777}/"
   curl -s -o /dev/null -w "/api/tests HTTP %{http_code}\n" "http://127.0.0.1:${KANBAN_PORT:-7777}/api/tests"
   ```
5. **汇报**：停了哪个 PID、新访问地址、健康检查结果。启动失败则贴 `/tmp/kanban.log` 末尾排查。

## 注意

- `pkill -f kanban-server.py` 进程名精确、误伤面小；仍建议先 `ps` 确认目标进程。
- 重启是可逆的常规运维，无破坏性数据操作。
- 端口被**非看板**进程占用时，先 `lsof -nP -iTCP:7777` 排查占用者，不要盲目强杀。

## 反馈回路

任务结束按 [[Contexts/决策/Skill反馈协议]] 输出 `skill_run` YAML 块；无 plan → 追加到 `进化/孤立反馈记录.md`。运维类无实际内容产出时 `utility` 可填 `not-needed`。
