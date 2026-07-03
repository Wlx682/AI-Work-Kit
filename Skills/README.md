# Skills 文件夹说明

> 存放规则 → [[Contexts/决策/Kit核心原则]] · 工作流 → [[Contexts/决策/AI-Work-Kit工作流总览]]

## Obsidian vs Agent Skills

| | `Skills/` | `.cursor/skills/` | `.claude/skills/` | `.codex/skills/` |
|--|-----------|-------------------|-------------------|------------------|
| 用途 | 人类阅读、版本管理 | Cursor 自动匹配 | Claude Code 自动匹配 | Codex 自动匹配 |
| 触发 | `@Skills/xxx.md` | 说触发词或 `/skill` | 说触发词或 `/skill` | 说触发词或 `/skill` |

业务仓开发：运行 `./scripts/sync-agent-skills.sh --sync` 部署 Claude / Codex 全局 Skill；Cursor 继续复制 `.cursor/skills/` → `~/.cursor/skills/`。

## Skill 一览

> **路由原则**（详见各 Skill 文件「触发条件」段）：
> 1. **命令优先**：`/command` 永远是精准救急通道，命中即走。
> 2. **互斥锁**：`workflow-router` 是入口 Skill，只启动引擎；`full-cycle` 是工作流引擎；单阶段词路由到子 Skill，不劫持。
> 3. **降级兜底**：≥3 个 Skill 同时命中 → 走 `resume-assistant` 询问用户「续做 vs 开新」。

### Epic 闭环（推荐自然语言触发词 + 命令）

| 推荐自然语言触发词 | Skill | 备用命令 | 产出 |
|---------------------|-------|----------|------|
| 全流程开发、启动项目、一条龙 | workflow-router | `/full-cycle` | 选择蓝图并启动 full-cycle 引擎 |
| 事件风暴、领域事件、事件墙 | event-storming-assistant | `/event-storming-assistant` | `Plans/需求分析/` |
| 实例化需求、GWT、验收标准 | spec-by-example-assistant | `/spec-by-example-assistant` | `Plans/需求分析/` |
| PRD 评审、需求分析、查 PRD 漏洞 | requirement-analyst | `/req` `/requirement-analyst` | `Plans/需求分析/` |
| 系统架构、模块边界、ER 图、数据模型 | architecture-design-assistant | `/arch` `/architecture-design-assistant` | 技术方案 plan |
| 拆任务、子任务拆分、WBS | task-splitter | `/split` `/task-splitter` | 主 plan + 子任务 |
| 开发 [模块] 功能、实现 [目标]、写代码 | feature-dev-assistant | `/dev` `/feature-dev-assistant` | `Plans/功能开发/` |
| Figma 还原、对稿、纯界面开发 | figma-ui | `/ui` `/figma-ui` | UI plan |
| 写测试、生成测试用例 | test-generator | `/test` `/test-generator` | `Plans/自动化测试/` |
| 非功能验证、性能/安全/可访问性检查 | nfr-assistant | `/nfr-assistant` | `Plans/非功能验证/` |
| 上线检查、发布计划、灰度 | deployment-assistant | `/deploy` `/deployment-assistant` | `Plans/部署/` |
| 团队回顾、复盘、流程改进 | retro-assistant | `/retro-assistant` | `Plans/最佳实践/` |
| 需求变了、改个东西、Scope 调整 | change-impact-analysis | `/change-impact-analysis` | 变更影响 |
| 检查 Epic 进度、审计版本状态、这个需求做完了吗 | dev-lifecycle-audit-assistant | `/dev-lifecycle-audit` | 审计报告 |

### 入口路由

| 推荐自然语言触发词 | Skill | 作用 |
|---------------------|-------|------|
| 全流程开发、启动项目、做个功能、帮我清理电脑 | workflow-router | 自然语言选蓝图，启动 `full-cycle` 引擎，不做阶段执行 |

### 通用

| 推荐自然语言触发词 | Skill | 备用命令 |
|---------------------|-------|----------|
| 续做、接着做、断点续 | resume-assistant | `/resume plan=...` |
| 生成 XX 模板、套用模板、起个骨架 | template-generator | `/template-generator` |
| 日报、周报、项目复盘、迭代回顾 | review-assistant | `/review` `/review-assistant` |
| PM 物料、整理通用资料 | material-prep-assistant | `/material-prep` |
| 找 CC 文章、周报选题、海外资讯、整理分享帖 | weekly-intel-digest | `/intel` `/weekly-intel-digest` |
| 提效案例、最佳实践、技术提交分享、产品提效 | best-practice-digest | `/best-practice` `/best-practice-digest` |
| 工作流进化、反馈闭环、skill_run 聚合、流程改进沉淀 | workflow-evolution-assistant | `/workflow-evolution` `/workflow-evolution-assistant` |

### 学习

| 推荐自然语言触发词 | Skill | 备用命令 |
|---------------------|-------|----------|
| 学习路线、继续课程、LLM 学习、考我课程 | learn-assistant | `/learn` `/learn-assistant` |
| 审计学习进度、learning-audit | learning-audit-assistant | `/learning-audit-assistant` |

### 工作流引擎（不属于 Skill 积木）

| 入口 | 用途 |
|------|------|
| `.claude/workflows/full-cycle.js` / `AGENTS.md` | 读取工作流蓝图，组合各子 Skill 执行多工作流 |
| `scripts/workflow-status.py` | 日常看状态：当前 / 卡点 / 下一步 / 继续 |
| `scripts/workflow-gate.sh` | 底层门禁详情：按蓝图与子 Plan 文件事实派生阶段 |
| `scripts/workflow-plan-init.py` | 为 `ui-change` / `bugfix` / `task-split-only` 等无 Epic 轻流程创建阶段 plan |
| `scripts/workflow-smoke-test.py` | 一条命令测试轻流程能路由、阻塞、补齐后 done |

### 内部（不直接对用户暴露）

| Skill | 用途 |
|-------|------|
| project-manager | `trigger: internal_only`，历史编排草案；新流程以 full-cycle 引擎 + 蓝图为准 |

全文见各 `Skills/*.md`。
