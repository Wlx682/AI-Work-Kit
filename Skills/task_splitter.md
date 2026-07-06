# 任务拆分助手 Skill

当用户说「任务拆分」「拆任务」「原子任务」「/task-splitter」时执行。

> 读取 `Plans/技术方案/`，拆解为 **5–10 个可独立续做的原子任务**。

## 知识库

- 契约：`Contexts/决策/Skill原子契约.md`
- 输入：`Plans/技术方案/xxx.md`（须 `status: 已采纳` 或用户声明可拆）
- 模板：`Templates/客户端功能开发模板.md`（子任务简化版）
- 输出：`Plans/功能开发/`

## 原子契约

| 字段 | 要求 |
|------|------|
| 输入 | 已采纳技术方案、Epic 或明确目标范围 |
| 输出 | 5-10 个原子任务，必要时写主 plan 与子任务 plan |
| 门禁 | 每个任务有输入、输出、验收、依赖；不混职责 |
| 越界 | WBS 方案不明确时请求用户确认，不擅自推荐 A/B/C |
| smoke | `python3 scripts/skill-smoke-test.py task-splitter tests/fixtures/skills/task-splitter/checkout-tech-plan.input.md` |

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
   - **主清单**：`Plans/功能开发/YYYY-MM-DD-模块名.md`（含子任务 Checklist + 双向链接；§五实施切片表必须保留「覆盖 AC」列）
   - **子任务 plan**：`Plans/功能开发/YYYY-MM-DD-模块名-子任务NN-简述.md`（每任务一个，便于细粒度 `/resume`）
4. 每个子任务 frontmatter：`lifecycle_state: development`，`parent: Plans/功能开发/主plan.md`
5. 主 plan 的「覆盖 AC」列填写需求验收标准 ID，多个用英文逗号分隔，如 `AC1, AC2, AC1-反`；无覆盖填 `—`。P0 AC 必须至少被一个功能开发任务覆盖。
6. WBS 切片生产规则：
   - 默认产出父编号 `[ ] N. 描述`。
   - 一个父切片里确实有可独立验收的 Mock / 真联调、静态态 / 接口态、基础态 / Variant 态时，用子编号拆成 `[ ] Na.` / `[ ] Nb.`，例如 `7a`、`7b`；不要为了凑数拆子编号。
   - AI 可语义判断“本需求不需要”的子切片，并标成 `[-] Nb. 描述`，但必须在该行或实施切片表「阻塞」列写明理由，如“无后端接口/无空态/纯前端静态页”。
   - 只要主 plan 里出现 `[-] N...`，必须同步提醒把对应父编号 N 加入蓝图 stage 的 `optionalWbsSlices`，或由看板跳过按钮执行；否则 gate 会按必选切片阻塞。
   - 不确定是否应跳过时，保留 `[ ]` 并写阻塞项，不擅自替用户关闭切片。
7. 主 plan Checklist 示例：

```markdown
- [ ] T1 · [[Plans/功能开发/xxx-子任务01-建表.md]]
- [ ] T2 · [[Plans/功能开发/xxx-子任务02-API.md]]
```

## 拆分原则

- 单任务可在一个会话内完成或明确验收
- 依赖顺序写清（T2 依赖 T1）
- 不写实现代码，只写任务边界、输入输出、验收
- optional / `[-]` 只是“不阻塞当前交付”的显式事实，不等于删除需求；跳过理由必须可被 PM/QA 复核

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
/task-splitter 方案=Plans/技术方案/2026-06-20-支付.md
```
