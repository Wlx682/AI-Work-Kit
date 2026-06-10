# 功能开发助手 Skill

当用户说「做功能」「开发模块」「新需求」「功能开发」「方案+界面一起」时执行。

> **默认入口**：新功能/新模块。  
> **前置**：须先完成需求分析（`/requirement-analyst`），或用户明确「PRD 已评审、无 P0」。  
> **仅 UI**（方案已有）→ `figma-ui-assistant`。

## 知识库

- 需求：`Plans/需求分析/`、`Contexts/需求分析/PRD分析检查清单.md`
- 模板：`Templates/功能开发模板.md`
- 方案参考：`Templates/客户端技术方案模板.md`
- Figma：`Contexts/Figma/项目设计规范.md`、`Figma界面开发最佳实践.md`
- Plan：`Plans/功能开发/`

## 代码仓库（多仓库）

- **默认**：当前 Cursor **工作区根目录** = 代码仓库，**不必记、不必写** `仓库=`
- **工作区是 AI-Work-Kit 时**：补充 `仓库=/path/to/项目` 或先用 Cursor 打开代码项目再说话
- **知识库 Vault** 固定为 AI-Work-Kit，与代码仓库分离

## 新任务

0. **检查需求分析**：若无 `Plans/需求分析/` 对应 plan 且用户未声明 PRD 已闭环 → **先引导** `/requirement-analyst`；有则读取摘要与「待产品确认」闭环状态。
1. 收集：**模块名、平台、Figma 链接**（当次粘贴）、需求分析 plan 路径。
2. 读功能开发模板 + Figma 规范；搜 `Contexts/`、`Plans/` 类似功能。
3. 有 Figma 链接：**MCP 逐节点读取**，填节点度量表（@2x px÷2=pt）。
4. 在**当前工作区代码库**搜可复用模块/UI；**对照需求分析中的「与现状冲突」**。
5. 输出 plan → `Plans/功能开发/YYYY-MM-DD-模块名.md`（含需求分析引用 + 方案 + 界面 + 切片）。
6. 第一步：若 P0 已闭环 → 方案对齐或读节点；若有未接受 P0 → 只更新开发 plan 不写代码。

## 续做

用户提供 `plan=功能开发/xxx.md` + `进度`：

1. 读 plan + 关联的需求分析 plan（若有）。
2. 对照「实施切片」从下一项继续。
3. 输出：已完成 / 本步要点 / 下一步 / 待确认项。

## 分工

| 场景 | 用谁 |
|------|------|
| 新 PRD / 需求不清 | **requirement-analyst** |
| PRD 分析通过，方案+界面开发 | **feature-dev-assistant** |
| 仅 UI | figma-ui-assistant |
| 纯技术方案、无设计稿 | template-generator 客户端方案 |

## 触发示例

```
/requirement-analyst 新分析，PRD=【飞书链接】，模块=创建自动化任务

/feature-dev-assistant 新任务，模块=创建自动化任务，需求分析=需求分析/2026-06-10-创建自动化任务.md，Figma=【链接】

/feature-dev-assistant 续做，plan=功能开发/2026-06-10-创建自动化任务.md，进度=Domain 完成
```
