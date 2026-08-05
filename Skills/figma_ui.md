# Figma 界面开发 Skill

## 触发条件

当用户说「做界面」「Figma 开发」「还原设计稿」「对稿」「Figma MCP」「纯界面开发」时执行；也响应 `/figma-ui` / `/ui` 命令。

> **定位：仅 UI 子任务。** 新功能/新模块 → `feature-dev-assistant`。

## 🔒 路由优先级（硬规则）

以下语义命中时**强制本 Skill**，`feature-dev-assistant` **不得**替代：

- 「界面」「对稿」「还原」「Figma」「1:1」「自检表」
- Story 子 Plan、UI 子任务或子 plan **Skill 列**标明 `figma-ui`

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

- 契约：`Contexts/决策/Skill原子契约.md`
- 规范：`Contexts/Figma/项目设计规范.md`
- 实践：`Contexts/Figma/Figma界面开发最佳实践.md`
- 模板：`Templates/客户端功能开发模板.md`（含业务逻辑=否）
- **验证：对抗验证子 Agent + `.workflows/schemas/figma-verdict.schema.json` ⭐ 报完成前硬门槛（见下方三段结构）**
- 辅助：`Templates/Figma还原自检表.md`（实现期自查用，非报完成门禁）
- Plan：`Plans/功能开发/`

## 原子契约

| 字段 | 要求 |
|------|------|
| 输入 | Figma 链接或截图、目标页面、平台、允许偏差 |
| 输出 | UI 实现说明、真机截图（落盘文件）、对抗验证裁决 `verdict.json`、差异表 |
| 门禁 | 对抗验证子 Agent 裁决 `pass==true` 且经主控复核 `reviewed==true`；有 P0 不得说完成（不再用自评分） |
| 越界 | 出现接口联调、埋点、状态机、跨模块业务逻辑时升级到功能开发流程 |
| smoke | `python3 scripts/skill-smoke-test.py figma-ui tests/fixtures/skills/figma-ui/basic-card.input.md` |

## 新任务

1. 确认 Figma MCP 已连接（绿点 / `whoami`）
2. 索要带 node-id 的 Figma 链接
3. `get_metadata` + `get_design_context`（指定 Swift/UIKit、@2x÷2=pt）
4. 输出度量表（**含形状判定**）+ `**` 切图清单 + 差异表 → 写 Plan → 确认后编码

## ✋ 报"完成"前硬门槛（对抗式验证三段结构）

> **不再用"自评≥9"** —— 同一张脸既当运动员又当裁判，认知盲区完全重叠，藏在 metadata `hidden` 属性里的语义差异（如列表某行是"未选中勾选圈"而非"移除"图标）自评几乎必漏。改用**独立 context 的对抗验证子 Agent**。

不满足下述**全部**三段 → **禁止**对用户说"完成 / 还原好了"：

### ① 产物落盘（硬前置）

1. **编译通过**。
2. 真机 / 模拟器截图**必须存成文件**（如 `Plans/.../<任务>.impl.png`）。聊天里贴的图喂不进子 Agent，必须落盘成路径。

### ② 对抗验证（起独立子 Agent）

用 `Agent()` 起一个**全新 context** 的验证子 Agent，只喂它：
- 设计稿 node-id（让它**自己**调 Figma MCP `get_screenshot` + `get_metadata` 拉真相，不由你转述）。
- 实现截图的**文件路径**（让它自己 `Read`）。
- **不传**你的任何推理 / 度量表 / "我觉得对了"——保证评判不相关性。

子 Agent 输出严格 JSON 裁决（schema：`.workflows/schemas/figma-verdict.schema.json`）：
`{pass, score, summary, deviations[], verified_ok[]}`。prompt 模板见下节。

### ③ 主控复核（滤误报后采信）

对抗验证会**误报**（实测把图层名"知识广场"当成标题真相，实为残留命名）。你必须复核每条 deviation：
- 滤掉 metadata 命名 / 图层名导致的误判。
- 修正后写回子 Plan：frontmatter 加 `verdict: <裁决文件路径>`，裁决 JSON 里标 `reviewed: true`。
- 仍有 P0 → 交付**差异表**，列未达标项 + 建议，让用户决定；**不得**说"完成"。

> 门禁 `workflow-gate.sh` 的 `verdictPass` 只读这份**复核后**的 verdict.json 文件事实（`pass==true && reviewed==true`），不实时跑子 Agent。

### 对抗验证子 Agent · prompt 模板

```
你是对抗式 UI 视觉还原验证 Agent。唯一职责：找出实现相对设计稿的一切偏差。
不写代码、不体谅实现难度、不给情面，默认怀疑一切。你不知道是谁做的、用什么做的。

第一步：自己调 Figma MCP 拉设计稿真相
  · mcp__figma__get_screenshot  nodeId="<NODE_ID>"
  · mcp__figma__get_metadata    nodeId="<NODE_ID>"（@2x 稿，px÷2=pt）
第二步：Read 实现截图 <IMPL_PNG_PATH>
第三步：逐区域对抗比对，重点：
  · 顶部标题逐字核对（勿把图层名当文案真相）
  · tab 选中态：metadata 里 hidden=true 是未选中、visible 是选中，据此判高亮位置
  · 列表右侧图标语义逐行核对（移除 vs 未选中勾选圈，别统一成一种）
  · 底部按钮：文案 / 数量 / 实心还是虚线
  · 头像形状（正圆）、凭空增减的元素
输出严格 JSON（无多余文字）：
  {pass, score:0-10, summary, deviations:[{area,design,impl,severity:P0|P1|P2,fix}], verified_ok:[]}
判据：任意 P0 → pass=false；P0 每个扣≥3，P1 扣1-2，P2 扣0.5。
```

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
