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
- **自检：`Templates/Figma还原自检表.md` ⭐ 报完成前必填**
- Plan：`Plans/功能开发/`

## 新任务

1. 确认 Figma MCP 已连接（绿点 / `whoami`）
2. 索要带 node-id 的 Figma 链接
3. `get_metadata` + `get_design_context`（指定 Swift/UIKit、@2x÷2=pt）
4. 输出度量表（**含形状判定**）+ `**` 切图清单 + 差异表 → 写 Plan → 确认后编码

## ✋ 报"完成"前硬门槛

不满足下述任一条 → **禁止**对用户说"完成 / 还原好了"：

1. **编译通过**
2. **MCP `get_screenshot`** 取设计稿截图 + 真机/模拟器截图，**逐元素对比**
3. 走 `Templates/Figma还原自检表.md`，**自评 ≥ 9/10** 才能报"完成"
4. 不满足 → 必须交付**差异表**，列出未达标项 + 建议方案，让用户决定

## Mock 边界（极重要）

> "mock 数据" ≠ "自由发挥视觉资源"。**只 mock 文本内容**。

| 类型 | 可以 mock | 必须从节点还原 |
|---|---|---|
| **文本内容** | 项目名、描述、长文 ✅ | — |
| **颜色** | — | 色板色值 / 数量 / 顺序 ❌ |
| **图标** | — | 集合 / 顺序 / 首选项；SF Symbol 不能自由替代 ❌ |
| **形状** | — | 圆 / 方 / 圆角方块(squircle) ❌ |
| **Variant** | — | 默认 / 选中 / 禁用 / 按压 状态稿 ❌ |

无法还原时 → **明确告知用户**"需要切图 / 设计色板规范"，不要自己脑补。

## 续做 / 走查

```
/resume plan=Plans/功能开发/xxx.md 进度=【】
```

走查：`Templates/Figma设计走查模板.md` + MCP `get_screenshot`
