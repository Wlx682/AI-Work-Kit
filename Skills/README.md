# Skills 文件夹说明

> 存放规则 → [[Contexts/决策/Kit核心原则]] · 工作流 → [[Contexts/决策/AI-Work-Kit工作流总览]]

## Obsidian vs Agent Skills

| | `Skills/` | `.cursor/skills/` | `.claude/skills/` | `.codex/skills/` |
|--|-----------|-------------------|-------------------|------------------|
| 用途 | 人类阅读、版本管理 | Cursor 自动匹配 | Claude Code 自动匹配 | Codex 自动匹配 |
| 触发 | `@Skills/xxx.md` | 说触发词或 `/skill` | 说触发词或 `/skill` | 说触发词或 `/skill` |

业务仓开发：运行 `./scripts/sync-agent-skills.sh --sync` 部署 Claude / Codex 全局 Skill；Cursor 继续复制 `.cursor/skills/` → `~/.cursor/skills/`。

## 创建 / 修改 Skill 的最小校验链

适用：新增 Skill、改触发词、改路由边界、改 Agent stub、改人类说明。

1. 更新人类真理源：`Skills/<name>.md`（下划线命名）。
2. 更新 Agent 真理源：`.cursor/skills/<name>/SKILL.md`（dash 命名）。
3. 若是新增 Skill，确认两端都存在；若是仅改人类说明，也要确认是否需要同步 stub。
4. 部署到生成端与全局同名副本：
   ```bash
   ./scripts/sync-agent-skills.sh --sync
   ```
5. 复校验多端一致：
   ```bash
   ./scripts/sync-agent-skills.sh --check
   ```
6. 若该 Skill 有固定产物 fixture，跑对应 smoke；否则确认它在 `scripts/skill-smoke-all.py` 的运维/路由豁免集中有合理说明：
   ```bash
   python3 scripts/skill-smoke-test.py <skill> tests/fixtures/skills/<skill>/<case>.input.md
   python3 scripts/skill-smoke-all.py
   ```

判定：`sync-agent-skills.sh --check` 必须通过；产物类 Skill 的 fixture 缺口至少要在本次变更说明里交代。

## Skill 一览

> **路由原则**（详见各 Skill 文件「触发条件」段）：
> 1. **命令优先**：`/command` 永远是精准救急通道，命中即走。
> 2. **互斥锁**：`workflow-router` 是入口 Skill，只选择具体 workflow；通用执行器只读蓝图启动看板/门禁；单阶段词路由到子 Skill，不劫持。
> 3. **降级兜底**：≥3 个 Skill 同时命中 → 走 `resume-assistant` 询问用户「续做 vs 开新」。

### Epic 闭环（推荐自然语言触发词 + 命令）

| 推荐自然语言触发词 | Skill | 备用命令 | 产出 |
|---------------------|-------|----------|------|
| 全流程开发、启动项目、一条龙 | workflow-router | 自然语言或 `workflow=client-dev` | 选择具体蓝图并启动看板/门禁 |
| 事件风暴、领域事件、事件墙 | event-storming-assistant | `/event-storming-assistant` | `Plans/需求分析/` |
| 实例化需求、GWT、验收标准 | spec-by-example-assistant | `/spec-by-example-assistant` | `Plans/需求分析/` |
| PRD 评审、需求分析、查 PRD 漏洞 | requirement-analyst | `/req` `/requirement-analyst` | `Plans/需求分析/` |
| 需求排序、Backlog 优先级、确认本轮先做什么 | backlog-prioritization-assistant | `/backlog-prioritization-assistant` | `Plans/需求排序/` + `.backlog.json` |
| 系统架构、模块边界、ER 图、数据模型 | architecture-design-assistant | `/arch` `/architecture-design-assistant` | 技术方案 plan |
| 拆纵向 Story、故事点、Scope | task-splitter | `/split` `/task-splitter` | `.stories.json` + Story 子 Plan |
| 实现落点设计、代码落点、文件目录规划、文件名规划 | implementation-design-assistant | `/implementation-design` | Story / bugfix implementation design JSON |
| 开发 [模块] 功能、实现 [目标]、写代码 | feature-dev-assistant | `/dev` `/feature-dev-assistant` | `Plans/功能开发/` |
| 合代码、合并分支、处理合并冲突 | merge-code-assistant | `workflow=merge-code`；先分析双边业务意图，语义冲突由开发者决策 | `Plans/代码重构/` |
| Figma 还原、对稿、纯界面开发 | figma-ui | `/ui` `/figma-ui` | UI plan |
| 集成测试用例计划、测试审核、全量回归 | test-generator | `/test` `/test-generator` | `test_case_index` + `test_review` + `integration_report` |
| Code Review、review diff、审查 PR、UI 复核 | code-review | `/code-review` `/review` | Findings-first（`Plans/代码重构/`） |
| 需求变了、改个东西、Scope 调整 | change-impact-analysis | `/change-impact-analysis` | 变更影响 |
| 检查 Epic 进度、审计版本状态、这个需求做完了吗 | dev-lifecycle-audit-assistant | `/dev-lifecycle-audit` | 审计报告 |

### 入口路由

| 推荐自然语言触发词 | Skill | 作用 |
|---------------------|-------|------|
| 全流程开发、启动项目、做个功能、合代码、帮我清理电脑 | workflow-router | 自然语言选具体蓝图，启动看板/门禁，不做阶段执行 |

### 通用

| 推荐自然语言触发词 | Skill | 备用命令 |
|---------------------|-------|----------|
| 续做、接着做、断点续 | resume-assistant | `/resume plan=...` |
| 生成 XX 模板、套用模板、起个骨架 | template-generator | `/template-generator` |
| 日报、周报、项目复盘、迭代回顾 | report-assistant | `/report` `/report-assistant` |
| PM 物料、整理通用资料 | material-prep-assistant | `/material-prep` |
| 找 CC 文章、周报选题、海外资讯、整理分享帖 | weekly-intel-digest | `/intel` `/weekly-intel-digest` |
| 提效案例、最佳实践、技术提交分享、产品提效 | best-practice-digest | `/best-practice` `/best-practice-digest` |
| 生成网页、做成网页、出 HTML、技术文档网页、换个骨架/风格 | html-generate | `/html` `/html-generate` |
| 工作流进化、反馈闭环、skill_run 聚合、流程改进沉淀 | workflow-evolution-assistant | `/workflow-evolution` `/workflow-evolution-assistant` |
| 模式洞见、领域研究、从资料到文章、洞见文章与网页、发布知乎 | pattern-insight-workflow | `$pattern-insight-workflow` |

| 推荐自然语言触发词 | Skill | 备用命令 |
|---------------------|-------|----------|

### 工作流引擎（不属于 Skill 积木）

| 入口 | 用途 |
|------|------|
| `.claude/workflows/workflow-engine.js` / `AGENTS.md` | 读取工作流蓝图，组合各子 Skill 执行多工作流 |
| `scripts/workflow-status.py` | 日常看状态：当前 / 卡点 / 下一步 / 继续 |
| `scripts/workflow-gate.sh` | 底层门禁详情：按蓝图与子 Plan 文件事实派生阶段 |
| `scripts/workflow-plan-init.py` | 按蓝图创建当前阶段 Plan；Epic 工作流读取/补充 `plans.<epicField>`，轻流程按目录和前缀生成 |
| `scripts/workflow-smoke-test.py` | 一条命令测试轻流程能路由、阻塞、补齐后 done |

全文见各 `Skills/*.md`。
