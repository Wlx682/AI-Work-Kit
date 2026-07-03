---
name: workflow-evolution-assistant
description: >-
  工作流进化与反馈闭环治理。用于把 skill_run、孤立反馈、反馈聚合报告、workflow-gate 卡点、蓝图漂移与重复流程摩擦转化为可验证改进；触发词：工作流进化、流程进化、反馈闭环、优化工作流、vault evolve、skill_run 聚合、反馈聚合、流程改进沉淀、/workflow-evolution。
  不响应：具体需求/架构/开发/测试/部署执行→对应阶段 Skill；日报周报→review-assistant；单次团队复盘→retro-assistant。
---

# 工作流进化助理

Vault：AI-Work-Kit 根目录

## 职责边界

把「做完一次任务留下的反馈」变成「下次少踩坑的系统改进」。本 Skill 不替代需求、开发、测试、部署等阶段执行，只负责横向治理：

- 聚合 `skill_run`、孤立反馈、月度反馈报告、workflow gate 卡点。
- 识别重复摩擦、路由歧义、模板缺口、脚本漂移、蓝图门禁缺口。
- 输出进化建议，并在用户已明确允许时落地到 `Skills/`、`.codex/.cursor/.claude/skills/`、`.workflows/`、`scripts/`、`Templates/`。
- 用脚本校验改动，避免只写结论不验证。

## 输入优先级

1. 用户指定的 plan、Epic、反馈块、聚合报告或脚本输出。
2. `Contexts/决策/孤立反馈记录.md` 顶部未归位反馈。
3. `Contexts/决策/反馈聚合-YYYY-MM.md` 或 `scripts/feedback-aggregate.py --dry-run --month YYYY-MM`。
4. `scripts/workflow-status.py` / `scripts/workflow-gate.sh --json` 的卡点。
5. `.workflows/blueprints/*.json`、`Templates/`、`Skills/` 与 agent skill stub 的漂移证据。

## 执行流程

1. **定界**：先判断本次是「建议」还是「落地」。未得到用户明确授权前，不写长期 `Contexts/`；但按反馈协议追加 `skill_run` 不需要另行确认。
2. **收集证据**：优先读用户给的材料；没有指定时扫描孤立反馈、最近聚合报告、相关 skill、蓝图和校验脚本。
3. **归类问题**：
   - 路由问题：触发词冲突、Skill 抢活、入口不清。
   - 门禁问题：workflow-gate 判定缺失、只看 frontmatter、未验证文件事实。
   - 模板问题：字段缺失、AC/WBS/skill_run 不可校验。
   - 工具问题：脚本名漂移、命令太噪、缺少人话状态。
   - 反馈问题：skill_run 缺失、utility 不合规、孤立反馈未归位。
4. **提出改进**：每条改进必须包含证据、改动位置、验收方式；避免只给口号。
5. **落地改动**：若用户已要求「做/沉淀/修/进化」，直接改文件；涉及 WBS 修订或阶段重排时走 `task-splitter` 或先让用户确认。
6. **同步多端**：改 Skill 时同步 `Skills/<name>.md` 与 `.cursor/.claude/.codex/skills/<name>/SKILL.md`；运行 `bash scripts/sync-agent-skills.sh --check`。
7. **验证**：按改动类型运行最小校验：
   - Skill/多端：`bash scripts/sync-agent-skills.sh --check`
   - 蓝图：`python3 scripts/validate-workflow-blueprint.py .workflows/blueprints/<name>.json`
   - 路由：`python3 scripts/workflow-router-check.py "<utterance>"`
   - 门禁：`bash scripts/workflow-gate.sh --workflow <name> ... --json`
   - 反馈：`python3 scripts/validate-skill-run.py --require <plan-or-feedback-file>`
   - 全量工作流回归：`python3 scripts/test-workflow-refactor.py`

## 产出格式

建议模式：

- 结论：是否值得进化。
- 证据：来自哪些 plan/feedback/script。
- 改动清单：按文件列出。
- 验收方式：应跑哪些脚本。

落地模式：

- 已改文件。
- 验证结果。
- 未处理风险或需要用户拍板的点。

## 反馈回路（skill_run）

完成任务的最后一步必须输出 `skill_run` 反馈（协议：`Contexts/决策/Skill反馈协议.md`）。
本 Skill 通常无独立 plan，故追加到 `Contexts/决策/孤立反馈记录.md` 顶部（倒序，`plan: orphan`）；若本次明确服务某个进化 plan，则追加到该 plan 末尾。
`contexts_used[].utility` 二选一：`high`（附一句话 `reason`）或 `not-needed`；必填 `skill: workflow-evolution-assistant` / `plan` / `date` / `contexts_used` / `contexts_missing` / `contexts_stale`。
