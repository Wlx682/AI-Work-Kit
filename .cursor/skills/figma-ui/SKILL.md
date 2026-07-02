---
name: figma-ui
description: >-
  Figma 界面开发（仅 UI 子任务）。触发词：做界面、Figma开发、还原设计稿、对稿、Figma MCP、纯界面开发、/ui、/figma-ui。
  含业务逻辑门禁：接口联调/埋点/状态机等→转feature-dev-assistant。
  资料库 Contexts/Figma/；报完成前必填 Figma还原自检表。
---

# Figma 界面开发 Skill

## 触发条件

当用户说「做界面」「Figma 开发」「还原设计稿」「对稿」「Figma MCP」「纯界面开发」时执行；也响应 `/figma-ui` / `/ui` 命令。

> **定位：仅 UI 子任务。** 新功能/新模块 → `feature-dev-assistant`。

## 🔒 路由优先级（硬规则）

以下语义命中时**强制本 Skill**，`feature-dev-assistant` **不得**替代：

- 「界面」「对稿」「还原」「Figma」「1:1」「自检表」
- Epic WBS 或子 plan **Skill 列**标明 `figma-ui` 的切片

## ✋ 业务逻辑门禁（接手前必判）

若用户描述中包含以下任一关键词 → **暂停本 Skill**，主动建议转交 `feature-dev-assistant`，由用户确认：

- 「**接口联调**」「**调接口**」「**对接 API**」
- 「**业务逻辑**」「**状态机**」「**埋点**」
- 「**数据处理**」「**本地存储**」「**缓存策略**」
- 「**登录态 / 鉴权 / 支付逻辑**」

只有用户明确「**只做 UI，业务逻辑后续单独开会话**」时，才继续走本 Skill。

## MCP 配置（必读）

`Contexts/Figma/Figma-MCP配置.md`

- 对稿必须用 MCP 读节点，禁止截图估像素

## 知识库

- 规范：`Contexts/Figma/项目设计规范.md`
- 实践：`Contexts/Figma/Figma界面开发最佳实践.md`
- **自检：`Templates/Figma还原自检表.md` ⭐ 报完成前必填**
- Plan：`Plans/功能开发/`

## 报"完成"前硬门槛

1. **编译通过**
2. **MCP `get_screenshot`** 对比设计稿与真机截图
3. 走 `Templates/Figma还原自检表.md`，**自评 ≥ 9/10**

同步：`Skills/figma_ui.md`

## 反馈回路（skill_run）

完成任务的最后一步**必须**输出 `skill_run` 反馈（协议：`Contexts/决策/Skill反馈协议.md`）：
追加到本次 UI 子任务所属功能开发 plan（`Plans/功能开发/`） **末尾**的 `## 反馈（skill_run）` 节（fenced ```yaml`，非裸 frontmatter）。
`contexts_used[].utility` 二选一：`high`（附一句话 `reason`）或 `not-needed`；必填 `skill: figma-ui` / `plan` / `date` / `contexts_used` / `contexts_missing` / `contexts_stale`。缺则 `plan-gate-check.sh` 报失败。
