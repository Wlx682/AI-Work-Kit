---
tags: [figma, mcp, 决策, 界面开发]
---

# Figma MCP 配置（Cursor）

> 目标：Agent 通过 MCP 读 Figma 节点属性（非截图估像素），用于对稿与切片 2 度量表。

## 已配置：Personal Access Token + `figma-api` MCP（本机）

Token 存 **gitignore** 的 `.cursor/figma.env`（勿提交）。MCP 走 `figma-developer-mcp`：

| 仓库 | 启动脚本 |
|------|----------|
| NamiWork | `.cursor/run-figma-mcp.sh` |
| AI-Work-Kit | `.cursor/run-figma-mcp.sh` |

`mcp.json` 中服务名：**`figma-api`**。改 token 只改 `figma.env`，然后 Cursor → MCP 重启该服务。

也可用 REST 直读（Agent 内 curl）：

```bash
curl -H "X-Figma-Token: $FIGMA_API_KEY" \
  "https://api.figma.com/v1/files/{fileKey}/nodes?ids={nodeId}"
```

`node-id=29450-3465` → `ids=29450%3A3465`。

---

## 推荐：官方 Figma 插件（一次装好 MCP + Skills）

在 Cursor Agent 对话输入：

```text
/add-plugin figma
```

按提示安装并完成 Figma OAuth。插件自带 MCP 配置与官方 Skills。

## 手动：项目 mcp.json

已在以下仓库写入模板（二选一启用即可，不必两个都连）：

| 仓库 | 路径 |
|------|------|
| NamiWork | `.cursor/mcp.json` |
| AI-Work-Kit | `.cursor/mcp.json` |

```json
{
  "mcpServers": {
    "figma": {
      "url": "https://mcp.figma.com/mcp"
    },
    "figma-desktop": {
      "url": "http://127.0.0.1:3845/mcp"
    }
  }
}
```

### 连接步骤（Remote，推荐）

1. Cursor → **Settings → MCP**
2. 找到 `figma` → 点 **Connect** → 浏览器 **Allow access**
3. 状态变绿后，对话里应能看到 `get_design_context` 等工具

官方文档：[Remote server installation](https://developers.figma.com/docs/figma-mcp-server/remote-server-installation/)

### 备选：Desktop 本地 MCP

Remote OAuth 失败时（Cursor 社区有已知问题），用 Figma 桌面版：

1. 打开 Figma **桌面 App** → 打开设计文件 → **Dev Mode**（`Shift+D`）
2. Inspect 面板 → **Enable desktop MCP server**（`http://127.0.0.1:3845/mcp`）
3. Cursor MCP 里启用 `figma-desktop`（保持 Figma 文件在前台）

官方文档：[Desktop server installation](https://developers.figma.com/docs/figma-mcp-server/local-server-installation/)

| 能力 | Remote `figma` | Desktop `figma-desktop` |
|------|----------------|-------------------------|
| 链接读节点 | ✅ 必须带 node-id | ✅ |
| 当前选中帧 | ❌ | ✅ 在 Figma 里选中后 prompt |
| `use_figma` 写回稿面 | ✅ | ❌ |
| 完整工具集 | ✅ | 子集 |

## 对稿时怎么用

### 1. 链接格式

任务对话粘贴带 **node-id** 的链接，例如：

```text
https://www.figma.com/design/Z3hhNwFzvLZOdnCtXkIRHn/...?node-id=29450-3465&m=dev
```

URL 中 `29450-3465` → MCP 参数 `29450:3465`。

### 2. 建议 Prompt（iOS / UIKit）

```text
用 Figma MCP 读 node 29450:3465，fileKey Z3hhNwFzvLZOdnCtXkIRHn。
先 get_metadata 看结构，再 get_design_context，输出 Swift/UIKit 度量表（@2x px÷2=pt）。
列出所有 ** 切图图层。
```

大帧可先 `get_metadata` 再对子 layer 调 `get_design_context`。

### 3. 常用工具

| 工具 | 用途 |
|------|------|
| `get_design_context` | 尺寸、圆角、颜色、字体、间距（主工具） |
| `get_metadata` | 轻量 XML 结构（大稿先扫层级） |
| `get_variable_defs` | 颜色 / 间距 token |
| `get_screenshot` | 走查对照截图 |
| `whoami` | 验证 OAuth 是否成功 |

完整列表：[Tools and prompts](https://developers.figma.com/docs/figma-mcp-server/tools-and-prompts/)

### 4. 与团队规范衔接

- 图层 `**名称**` = 切图 → 见 [[项目设计规范]]、[[Figma界面开发最佳实践]]
- 数值优先级：**Figma 节点 > Variant > 规范兜底**
- Skill：`figma-ui-assistant`（`~/.cursor/skills/figma-ui-assistant/`）

## 故障排查

| 现象 | 处理 |
|------|------|
| MCP 红点 / 无工具 | Remote：重连 OAuth；或改开 Desktop MCP |
| Desktop 连不上 | 确认桌面 App 已开 Dev Mode MCP；重启 Figma + Cursor |
| 匿名浏览器打不开 Inspect | 正常；必须用 MCP 或登录 Figma |
| 返回 Tailwind 代码 | Prompt 里指定「Swift/UIKit」「@2x÷2=pt」 |

## 相关

- [[Figma界面开发最佳实践]]
- [[项目设计规范]]
- Plan 示例：`Plans/功能开发/2026-06-11-会员细节.md` §2.5
