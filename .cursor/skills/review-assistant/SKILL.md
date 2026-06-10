---
name: review-assistant
description: 日报、周报、月度复盘。日报→Contexts/日报/；周报→Contexts/周报/。触发：日报、周报、今日/本周总结、复盘。
---

# 复盘助理

Vault：AI-Work-Kit 根目录

| 模式 | 写入 |
|------|------|
| 日报 | 写入 `Contexts/日报/`；git 仅本人；**正文不写规则/元信息** |
| 周报 | 写入 `Contexts/周报/`；汇总日报 + 本人 git；**正文不写规则** |
| 月度 | `Contexts/复盘/YYYY-MM.md`；可引用日报/周报 |

模板：`Templates/日报模板.md` · `Templates/周报模板.md` · `Templates/月度复盘模板.md`

同步：`Skills/review_assistant.md`
