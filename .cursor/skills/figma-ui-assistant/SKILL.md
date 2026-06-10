---
name: figma-ui-assistant
description: 仅 UI 子任务（方案已有或纯改界面）。新模块用 feature-dev-assistant。触发词：做界面、Figma开发、对稿。
---

# Figma 界面开发助手

知识库（只读这三类）：
1. `Contexts/Figma/项目设计规范.md` — 公共规范，无链接、无功能清单
2. `Contexts/Figma/Figma界面开发最佳实践.md`
3. `Templates/Figma界面开发模板.md`、`Templates/Figma设计走查模板.md`

代码：当前 Cursor 工作区（多仓库不写死）

## 新任务

1. 用户**当次提供** Figma 链接 + Frame 名；未提供则索要。
2. 读规范与模板；在代码库搜可复用组件（不查 Obsidian 功能索引）。
3. 输出 plan 草稿 → 存 `Plans/界面开发/`（进行中任务，非永久沉淀）。
4. 切片实施：骨架 → 静态 → 数据 → 交互 → 异常态 → 走查。

## 原则

- **1:1 还原**：Figma MCP 逐节点读取；@2x px÷2=pt；禁止截图估像素
- 设计节点 > Variant > 规范兜底（圆角/阴影/border/按压态无标注才用兜底）
- 先复用组件；plan 填节点度量表
- 已上线功能不写回 Contexts

同步：`Skills/figma_ui_assistant.md`
