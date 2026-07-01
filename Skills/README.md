# Skills 文件夹说明

> 存放规则 → [[Contexts/决策/Kit核心原则]] · 工作流 → [[Contexts/决策/AI-Work-Kit工作流总览]]

## Obsidian vs Cursor

| | `Skills/` | `.cursor/skills/` |
|--|-----------|-------------------|
| 用途 | 人类阅读、版本管理 | Agent 自动匹配 |
| 触发 | `@Skills/xxx.md` | 说触发词或 `/skill` |

业务仓开发：复制 `.cursor/skills/` → `~/.cursor/skills/`。

## Skill 一览

> **路由原则**（详见各 Skill 文件「触发条件」段）：
> 1. **命令优先**：`/command` 永远是精准救急通道，命中即走。
> 2. **互斥锁**：`full-cycle-assistant` 仅响应「全流程 / 启动项目」类输入；单阶段词路由到子 Skill，不劫持。
> 3. **降级兜底**：≥3 个 Skill 同时命中 → 走 `resume-assistant` 询问用户「续做 vs 开新」。

### Epic 闭环（推荐自然语言触发词 + 命令）

| 推荐自然语言触发词 | Skill | 备用命令 | 产出 |
|---------------------|-------|----------|------|
| 全流程开发、启动项目、一条龙 | full-cycle-assistant | `/full-cycle` | `Plans/Epic/` + 子 plan |
| PRD 评审、需求分析、查 PRD 漏洞 | requirement-analyst | `/req` `/requirement-analyst` | `Plans/需求分析/` |
| 系统架构、模块边界、ER 图、数据模型 | architecture-design-assistant | `/arch` `/architecture-design-assistant` | 技术方案 plan |
| 拆任务、子任务拆分、WBS | task-splitter | `/split` `/task-splitter` | 主 plan + 子任务 |
| 开发 [模块] 功能、实现 [目标]、写代码 | feature-dev-assistant | `/dev` `/feature-dev-assistant` | `Plans/功能开发/` |
| Figma 还原、对稿、纯界面开发 | figma-ui | `/ui` `/figma-ui` | UI plan |
| 写测试、生成测试用例 | test-generator | `/test` `/test-generator` | `Plans/自动化测试/` |
| 上线检查、发布计划、灰度 | deployment-assistant | `/deploy` `/deployment-assistant` | `Plans/部署/` |
| 需求变了、改个东西、Scope 调整 | change-impact-analysis | `/change-impact-analysis` | 变更影响 |
| 检查 Epic 进度、审计版本状态、这个需求做完了吗 | dev-lifecycle-audit-assistant | `/dev-lifecycle-audit` | 审计报告 |

### 通用

| 推荐自然语言触发词 | Skill | 备用命令 |
|---------------------|-------|----------|
| 续做、接着做、断点续 | resume-assistant | `/resume plan=...` |
| 生成 XX 模板、套用模板、起个骨架 | template-generator | `/template-generator` |
| 日报、周报、项目复盘、迭代回顾 | review-assistant | `/review` `/review-assistant` |
| PM 物料、整理通用资料 | material-prep-assistant | `/material-prep` |
| 找 CC 文章、周报选题、海外资讯、整理分享帖 | weekly-intel-digest | `/intel` `/weekly-intel-digest` |
| 提效案例、最佳实践、技术提交分享、产品提效 | best-practice-digest | `/best-practice` `/best-practice-digest` |

### 学习

| 推荐自然语言触发词 | Skill | 备用命令 |
|---------------------|-------|----------|
| 学习路线、继续课程、LLM 学习、考我课程 | learn-assistant | `/learn` `/learn-assistant` |
| 审计学习进度、learning-audit | learning-audit-assistant | `/learning-audit-assistant` |

### 内部（不直接对用户暴露）

| Skill | 用途 |
|-------|------|
| project-manager | `trigger: internal_only`，仅由 full-cycle 内部引用作状态机参考；用户说「全流程」一律走 `full-cycle-assistant` |

全文见各 `Skills/*.md`。
