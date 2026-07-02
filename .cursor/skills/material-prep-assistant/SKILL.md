---
name: material-prep-assistant
description: 从代码/对话提炼 PM 对接物料，沉淀到 AI-Work-Kit Contexts（对照表、配置清单）。触发词：准备资料、整理资料、沉淀资料库、PM 物料、对照表、收银台配置表。
---

# 资料准备助手

Vault：**AI-Work-Kit** · 代码对照：**当前 Cursor 工作区**（非 AI-Work-Kit 时向用户索要仓库）

**产出路径**：`Contexts/{分类}/` — **不要**默认写业务仓库 `docs/`。

同步：`Skills/material_prep_assistant.md` · 模板：`Templates/资料沉淀模板.md` · 示例：`Contexts/收银台/MSPay收银台配置对照表.md`

## 步骤

1. 确认资料类型、参考 App、待补充 App。
2. 参考 App 现值：grep 代码仓库（工作区是 Vault 则先要代码路径）。
3. 只保留 **外部部门申请** 且 **写代码或 ASC** 的字段；排除登录、业务 API、代码共识、不变 UI 文案。
4. 写入 `Contexts/{分类}/xxx.md`；新分类更新 `索引.md`。
5. 多 App 列对照；未知值「待补充」/「待收银台部门提供」，不猜。

## MSPay 收银台（字段边界）

**保留**：product、appKey、serviceURL、subscriptionURL、IAP 回调 URL（正式/测试）

**不写**：checkstandType、member_level、env、登录、业务 API、按钮文案；**不拼**协议 URL（收银台部门下发）

Claw 代码：`NMPaymentManager.registerPayment()`

## 表头

```markdown
| 配置项 | {参考App} | {新App} |
| product / appKey / serviceURL / subscriptionURL | 参考列填现值 | 待补充 |
| IAP 回调 URL（正式/测试） | 待收银台部门提供 | 待补充 |
```

## 触发

```
/material-prep 类型=收银台，参考=Claw，新App=namiWork
准备资料 / 沉淀到资料库 / PM 物料 / 对照表
```

## 反馈回路（skill_run）

完成任务的最后一步**必须**输出 `skill_run` 反馈（协议：`Contexts/决策/Skill反馈协议.md`）：
本 Skill 沉淀资料到 `Contexts/` 而非产 plan，故追加到 `Contexts/决策/孤立反馈记录.md` **顶部**（倒序，`plan: orphan`）。
`contexts_used[].utility` 二选一：`high`（附一句话 `reason`）或 `not-needed`；必填 `skill: material-prep-assistant` / `plan` / `date` / `contexts_used` / `contexts_missing` / `contexts_stale`。喂 `feedback-aggregate → vault-evolve` 进化链。
