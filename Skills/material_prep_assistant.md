# 资料准备助手 Skill

当用户说「准备资料」「整理资料」「沉淀到资料库」「PM 物料」「对照表」「收银台配置表」时执行。

> **资料库 = AI-Work-Kit `Contexts/`**，不是业务代码仓库的 `docs/`。

## 与 Plans / 其他 Skill 的分工

| | 资料准备 | template-generator / feature-dev |
|--|----------|-----------------------------------|
| 产出 | 长期对照表、配置清单 | 进行中 plan |
| 路径 | `Contexts/{分类}/` | `Plans/{分类}/` |
| 读者 | PM、对接外部部门 | 开发自己执行 |

## 知识库

- 示例：`Contexts/收银台/MSPay收银台配置对照表.md`
- 模板：`Templates/资料沉淀模板.md`
- 索引：更新 `索引.md`（目录结构 + 高频任务，如有新分类）

## 代码对照

- **参考 App 现值**：从**当前 Cursor 工作区**（业务代码仓库）grep / 读代码提取。
- 工作区是 AI-Work-Kit 时，向用户索要代码仓库路径，或请其打开 Claw / namiWork 等项目。

## 执行步骤

1. **确认资料类型**（收银台 / 第三方 SDK / 环境配置…）；无现成模板则按 `资料沉淀模板` 建表。
2. **确认 App**：参考 App（如 Claw）、待补充 App（如 namiWork）。
3. **从代码提取参考列**（仅当用户需要「对照参考 App」时）。
4. **筛选字段**——只保留需向**外部部门申请**、且会**写进代码或 ASC** 的项。
5. **写入** `Contexts/{分类}/{文件名}.md`；多 App 用列对照。
6. **更新** `索引.md` 入口（新分类时）。
7. **不要**在业务仓库 `docs/` 建同名文件（除非用户明确要求）。

## 字段边界（收银台 / MSPay）

**保留：**

| 配置项 | 来源 |
|--------|------|
| product | 收银台部门 |
| appKey | 收银台部门 |
| serviceURL | 收银台部门下发（不可自行拼 URL） |
| subscriptionURL | 收银台部门下发 |
| IAP 回调 URL（正式 / 测试） | 收银台部门 → 填 App Store Connect |

**不要写进表：**

- 登录（QUC src/key 等）
- Claw 业务 API、会员接口
- 代码实现细节（env 自动切换、PaymentDelegate、埋点 position…）
- 产品/UI 不变项（支付按钮文案等）
- checkstandType、member_level（运行时逻辑，非 PM 向收银台一次性申请项）
- 可自行推导的 URL 规律说明（协议地址必须由收银台部门提供）

## MSPay 表头模板

```markdown
# MSPay 收银台配置对照表

收银台部门申请/下发。`product` / `appKey` / 协议 URL 写入 `PaymentManager.register`；IAP 回调 URL 填 App Store Connect。

| 配置项 | {参考App} | {新App} |
|--------|-----------|---------|
| product | `{现值}` | 待补充 |
| appKey | `{现值}` | 待补充 |
| serviceURL | `{现值}` | 待补充 |
| subscriptionURL | `{现值}` | 待补充 |
| IAP 回调 URL（正式） | 待收银台部门提供 | 待补充 |
| IAP 回调 URL（测试） | 待收银台部门提供 | 待补充 |
```

Claw 参考：`NMPaymentManager.registerPayment()`（product / appKey / 协议 URL）。

## 触发示例

```
/material-prep 类型=收银台，参考=Claw，新App=namiWork

准备资料：整理 namiWork 收银台配置，对照 Claw

沉淀到资料库：MSPay 配置表，参考 App=Claw
```

## 输出原则

- 表格简洁，无废话、无共识说明。
- 未知值写「待补充」或「待收银台部门提供」，不猜。
- 完成后告知路径：`Contexts/收银台/MSPay收银台配置对照表.md`。
- 若用户仅讨论规则、不写文件，只输出表格草稿，不落盘。

同步：`.cursor/skills/material-prep-assistant/SKILL.md`
