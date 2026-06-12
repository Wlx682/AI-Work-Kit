# Figma 界面开发 Skill

当用户说「做界面」「Figma 开发」「还原设计稿」「对稿」「Figma MCP」时执行。

> **定位：仅 UI 子任务。** 新功能/新模块 → `feature-dev-assistant`。

## MCP 配置（必读）

`Contexts/Figma/Figma-MCP配置.md`

- 推荐：`/add-plugin figma`（官方插件 + OAuth）
- 项目已写 `.cursor/mcp.json`：`figma`（remote）+ `figma-desktop`（备选）
- 对稿必须用 MCP 读节点，禁止截图估像素

## 知识库

- 规范：`Contexts/Figma/项目设计规范.md`
- 实践：`Contexts/Figma/Figma界面开发最佳实践.md`
- 模板：`Templates/客户端功能开发模板.md`（含业务逻辑=否）
- Plan：`Plans/功能开发/`
- Cursor Skill：`~/.cursor/skills/figma-ui-assistant/SKILL.md`

## 新任务

1. 确认 Figma MCP 已连接（绿点 / `whoami`）
2. 索要带 node-id 的 Figma 链接
3. `get_metadata` + `get_design_context`（指定 Swift/UIKit、@2x÷2=pt）
4. 输出度量表 + `**` 切图清单 + 差异表 → 写 Plan → 确认后编码

## 续做 / 走查

```
/resume plan=Plans/功能开发/xxx.md 进度=【】
```

走查：`Templates/Figma设计走查模板.md` + MCP `get_screenshot`
