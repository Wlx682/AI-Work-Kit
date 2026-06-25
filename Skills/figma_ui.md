# Figma 界面开发 Skill

## 触发条件

当用户说「做界面」「Figma 开发」「还原设计稿」「对稿」「Figma MCP」「纯界面开发」时执行；也响应 `/figma-ui` / `/ui` 命令。

> **定位：仅 UI 子任务。** 新功能/新模块 → `feature-dev-assistant`。

## 🔒 路由优先级（硬规则）

以下语义命中时**强制本 Skill**，`feature-dev-assistant` **不得**替代：

- 「界面」「对稿」「还原」「Figma」「1:1」「自检表」
- Epic WBS 或子 plan **Skill 列**标明 `figma-ui` 的切片

误路由时主动纠正：「这是 UI 还原任务，应走 figma-ui（MCP 度量 + 自检表），不能用 feature-dev 手写布局。」

## ✋ 业务逻辑门禁（接手前必判）

若用户描述中包含以下任一关键词 → **暂停本 Skill**，主动建议转交 `feature-dev-assistant`，由用户确认：

- 「**接口联调**」「**调接口**」「**对接 API**」
- 「**业务逻辑**」「**状态机**」「**埋点**」
- 「**数据处理**」「**本地存储**」「**缓存策略**」
- 「**登录态 / 鉴权 / 支付逻辑**」

判别话术示例：

> 这个任务包含【接口联调 / 业务逻辑】，超出 `figma-ui` 的「仅 UI」边界。建议改走 `feature-dev-assistant`（含业务逻辑=是）；如果你只想先把界面对稿，再开新会话做业务，那就留在我这边。你想走哪个？

只有用户明确「**只做 UI，业务逻辑后续单独开会话**」时，才继续走本 Skill。

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
