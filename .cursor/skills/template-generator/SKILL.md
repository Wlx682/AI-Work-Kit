---
name: template-generator
description: 按模板启动排查/技术方案/review/功能开发/会议/API/发布。触发词：用模板、生成排查、写方案、template-generator。
---

# 模板生成器

约定：`Templates/模板约定.md`

## 任务类型 → 模板

| 类型 | 模板 | 存放 |
|------|------|------|
| 排查 | `Templates/排查问题模板.md` | `Plans/Bug排查/` |
| 技术方案 | `Templates/技术方案模板.md` | `Plans/客户端技术方案/` 或 `Plans/服务端技术方案/` |
| 重构 | `Templates/技术方案模板.md` | `Plans/代码重构/` |
| review | `Templates/Code-Review模板.md` | 按需 |
| 功能开发 | `Templates/客户端功能开发模板.md` | `Plans/功能开发/` |
| 仅 UI | 同上（含业务逻辑=否） | `Plans/功能开发/` |
| 会议 / API / 发布 | 对应模板 | `Contexts/会议/` 等 |

续做格式：`/resume plan=Plans/【分类】/xxx.md 进度=...`

同步：`Skills/template_generator.md`
