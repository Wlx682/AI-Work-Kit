# 功能开发助手

Vault：AI-Work-Kit · 代码：**当前 Cursor 工作区**

## 触发条件

当用户说以下任一时执行（**方案已定、需要落地写代码**的场景）：

- 「**开发 [模块] 功能**」「**实现 [目标]**」「**写 [模块] 代码**」「**开始写代码**」「**做这个功能**」「**落地这个方案**」
- `/feature-dev-assistant` / `/dev` 命令

**不响应**：

- 「全流程开发 / 启动项目」→ `full-cycle` 引擎（蓝图 manifest）
- 「需求分析 / PRD」→ `requirement-analyst`
- 「架构 / 技术方案」→ `architecture-design-assistant`
- 「只做界面 / 还原 Figma」→ `figma-ui`（无业务逻辑时）

## ✋ UI 子任务门禁（硬规则）

以下任一命中 → **立即转交** `figma-ui`，禁止用本 Skill 手写布局冒充还原：

- 用户描述含「界面 / 对稿 / 还原 / Figma / 1:1」
- Epic WBS 或子 plan **Skill 列**为 `figma-ui`
- 验收标准为 Figma 自检表 ≥9/10

## Epic 治理

见 [[Contexts/决策/Kit核心原则]] §七 · [[Templates/模板约定]] §Epic 入口。

**前置**：`requirement-analyst` P0 闭环或用户声明 PRD 已评审。

- 模板：`Templates/客户端功能开发模板.md`
- Plan：`Plans/功能开发/`
- 续做：`/resume plan=Plans/功能开发/xxx.md 进度=...`

仅 UI → `figma-ui` 或模板设含业务逻辑=否。

同步：`.cursor/skills/feature-dev-assistant/SKILL.md`
