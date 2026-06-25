# 任务拆分助手 Skill

当用户说「任务拆分」「拆任务」「原子任务」「/task-splitter」时执行。

> 读取 `Plans/客户端技术方案/` 或 `Plans/服务端技术方案/`，拆解为 **5–10 个可独立续做的原子任务**。

## 知识库

- 输入：`Plans/【客户端|服务端】技术方案/xxx.md`（须 `status: 已采纳` 或用户声明可拆）
- 模板：`Templates/客户端功能开发模板.md`（子任务简化版）
- 输出：`Plans/功能开发/`

## 执行步骤

1. 读取技术方案 plan + 链回的 `Plans/需求分析/` 真理源。
2. 按模块/API/数据/UI 维度拆 **5–10 个原子任务**，例如：
   - 数据库建表 / 迁移
   - API 接口实现
   - Domain / UseCase
   - Repository / 数据层
   - 前端组件 / 页面骨架
   - 联调与走查
3. 产出 **两份**：
   - **主清单**：`Plans/功能开发/YYYY-MM-DD-模块名.md`（含子任务 Checklist + 双向链接）
   - **子任务 plan**：`Plans/功能开发/YYYY-MM-DD-模块名-子任务NN-简述.md`（每任务一个，便于细粒度 `/resume`）
4. 每个子任务 frontmatter：`lifecycle_state: development`，`parent: Plans/功能开发/主plan.md`
5. 主 plan Checklist 示例：

```markdown
- [ ] T1 · [[Plans/功能开发/xxx-子任务01-建表.md]]
- [ ] T2 · [[Plans/功能开发/xxx-子任务02-API.md]]
```

## 拆分原则

- 单任务可在一个会话内完成或明确验收
- 依赖顺序写清（T2 依赖 T1）
- 不写实现代码，只写任务边界、输入输出、验收

## ✋ 禁止擅自下结论（硬规则）

- 拆解与 WBS 修订时，**禁止**输出「我推荐方案 A/B/C」式单方面定论。
- 信息不足或拆分边界不清 → **暂停**，列出待确认项找用户；或建议先走 `requirement-analyst` 闭环 P0。
- Epic WBS 表结构变更（增删切片、改 Skill 列）须经本 Skill 产出/更新 `Plans/功能开发/` plan **或**用户书面确认后再写回 Epic（见 `Contexts/决策/母子plan投影规则.md`）。

## 与 feature-dev-assistant 衔接

拆分完成后，对每个子任务用 `/resume plan=Plans/功能开发/xxx-子任务01.md` 进入实现。

## 上下文汇报

```
📌 当前阶段：[任务拆分] | 产出：主 plan + N 个子任务 | 下一阶段：[功能开发 /resume] | 中断：/resume plan=...
```

## 触发示例

```
/task-splitter 方案=Plans/服务端技术方案/2026-06-20-支付.md
```
