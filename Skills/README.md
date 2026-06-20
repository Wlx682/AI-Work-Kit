# Skills 文件夹说明

> 存放规则 → [[Contexts/决策/Kit核心原则]] · 工作流 → [[Contexts/决策/AI-Work-Kit工作流总览]]

## Obsidian vs Cursor

| | `Skills/` | `.cursor/skills/` |
|--|-----------|-------------------|
| 用途 | 人类阅读、版本管理 | Agent 自动匹配 |
| 触发 | `@Skills/xxx.md` | 说触发词或 `/skill` |

业务仓开发：复制 `.cursor/skills/` → `~/.cursor/skills/`。

## Skill 一览

### Epic 闭环

| 触发 | Skill | 产出 |
|------|-------|------|
| `/full-cycle` | full-cycle-assistant | `Plans/Epic/` + 子 plan |
| `/requirement-analyst` | requirement-analyst | `Plans/需求分析/` |
| `/architecture-design-assistant` | architecture-design-assistant | 技术方案 plan |
| `/task-splitter` | task-splitter | 主 plan + 子任务 |
| `/feature-dev-assistant` | feature-dev-assistant | `Plans/功能开发/` |
| `/figma-ui-assistant` | figma-ui-assistant | UI plan |
| `/test-generator` | test-generator | `Plans/自动化测试/` |
| `/deployment-assistant` | deployment-assistant | `Plans/部署/` |
| `/change-impact-analysis` | change-impact-analysis | 变更影响 |

### 通用

| 触发 | Skill |
|------|-------|
| `/resume plan=...` | resume-assistant |
| `/template-generator` | template-generator |
| `/review-assistant` | review-assistant → Contexts 日报/周报 |
| `/material-prep` | material-prep-assistant → **通用** Contexts |

### 学习

| 触发 | Skill |
|------|-------|
| `/learn-assistant` | learn-assistant → `Plans/学习/` |
| `/learning-audit-assistant` | learning-audit-assistant |

全文见各 `Skills/*.md`。
