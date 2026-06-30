# 架构设计助手 Skill

## 触发条件（侧重「内容」）

当用户说以下任一时执行 —— 关键词偏 **系统设计内容**，与「生成模板骨架」区分开：

- 「**系统架构设计**」「**模块边界划分**」「**ER 图设计**」「**数据模型**」「**接口契约 / API Schema**」「**技术方案（系统级）**」
- `/architecture-design-assistant` / `/arch` 命令

**不响应（让位给其他 Skill）**：

- 「**生成技术方案模板**」「**套用方案模板**」（只要骨架）→ `template-generator`
- 「**全流程开发**」→ `full-cycle-assistant`（再由其编排到本 Skill）
- 「**开发 / 写代码**」（方案已定）→ `feature-dev-assistant`

> **承上启下**：输入必须是已闭环（或可开发）的 `Plans/需求分析/` plan；产出写入 `Plans/客户端技术方案/` 或 `Plans/服务端技术方案/`。

## 知识库

- 真理源：`Plans/需求分析/xxx.md`（**必读**，架构变动须先回看）
- 模板：`Templates/技术方案模板.md`
- 清单：`Contexts/需求分析/需求分析规范.md` §五（逐类挑问题）
- Plan 输出：`Plans/客户端技术方案/` 或 `Plans/服务端技术方案/`

## 前置门禁

1. 读取关联 `Plans/需求分析/xxx.md`
2. 若 P0 未闭环且用户未「接受风险并记录」→ **停止**，引导 `/requirement-analyst`
3. 若需求 plan 缺「边界情况清单」「异常流程矩阵」「验收标准」→ 补全或提醒换用 `Templates/需求分析-带验收标准模板.md`

## 执行步骤

1. 收集：**模块名、平台（客户端/服务端）、需求 plan 路径**。
2. 读需求 plan 全文 + 在**当前工作区代码库**搜索相关模块与可复用代码。
3. 按 `技术方案模板` 输出，**必须包含**：
   - **模块边界划分**（表 + mermaid 依赖图）
   - **数据模型**（ER 图 + 字段定义表）
   - **接口契约 / API Schema**（含 Request/Response 示例、错误码）
4. frontmatter 设置 `lifecycle_state: architecture`，正文链回需求 plan。
5. Plan → `Plans/【客户端|服务端】技术方案/YYYY-MM-DD-模块名.md`
6. `status` 需经评审后为 `已采纳`，方可进入 `/task-splitter`。

## 与 task-splitter 衔接

| 结论 | 下一步 |
|------|--------|
| 方案草稿 / 待确认项多 | 继续本 Skill 或 `/resume` |
| `status: 已采纳` | `/task-splitter`，引用本方案 plan |

## 上下文汇报（每步结束必输出）

```
📌 当前阶段：[架构设计] | 产出：Plans/.../xxx.md | 下一阶段：[任务拆分 /task-splitter] | 中断：/resume plan=...
```

## 触发示例

```
/architecture-design-assistant 模块=支付模块，平台=服务端，需求=Plans/需求分析/2026-06-20-支付.md

架构设计，续做 plan=客户端技术方案/xxx.md，进度=ER 图已定，待 API Schema
```

代码仓库 = 当前 Cursor 工作区；Vault 工作区时用 `仓库=/path/to/项目`。
