# Figma 界面开发 Skill

当用户说「做界面」「Figma 开发」「还原设计稿」「UI 实现」时执行。

> **定位：仅 UI 子任务。** 新功能/新模块（方案+界面一起）→ 用 `feature-dev-assistant`。  
> 纯 UI 使用 `Templates/客户端功能开发模板.md`，设 **含业务逻辑=否**。

## 知识库路径

- 公共规范：`Contexts/Figma/项目设计规范.md`
- 最佳实践：`Contexts/Figma/Figma界面开发最佳实践.md`
- 模板：`Templates/客户端功能开发模板.md`

**代码仓库**：默认 = 当前 Cursor 工作区；工作区是 AI-Work-Kit 时加 `仓库=/path` 或先打开代码项目。
- Plan 存放：`Plans/功能开发/`（推荐，与完整功能同一目录）

## 新任务（开工）

1. 读取项目设计规范 + 最佳实践（**不读、不猜 Figma URL**）。
2. 若用户未提供 Figma 链接，先索要；链接只用于当次任务和 plan，不写回 Contexts。
3. 读取客户端功能开发模板，设 **含业务逻辑=否**，填充：链接、Frame 名、平台、需求摘要。
4. 在**代码仓库**内搜索类似 UI 组件。
5. 有 Figma 链接时：**用 Figma MCP 逐节点读取** Frame 及子 layer。
6. 输出：节点度量表、组件映射、Variant 清单、Plan 草稿、第一步指令。
7. 用户确认后再写代码。

## 续做

```
/resume plan=Plans/功能开发/xxx.md 进度=【】
```

## 设计走查

用户说「走查」「对稿」时：读取 `Templates/Figma设计走查模板.md`，对照 plan 逐项检查。

## 触发示例

```
/figma-ui-assistant 新任务，Figma=【链接】，平台=iOS，页面=0608模型选择

/resume plan=Plans/功能开发/2026-06-10-设置页.md 进度=已完成静态UI

/figma-ui-assistant 走查，plan=Plans/功能开发/2026-06-10-设置页.md
```

## 代码原则

- **1:1 还原**：@2x px ÷ 2 = pt；规范默认值仅设计未标注时使用
- 逐节点读取，不靠截图目测
- 切片：读节点 → 骨架 → 静态 → 数据 → 交互 → 异常态 → 走查
