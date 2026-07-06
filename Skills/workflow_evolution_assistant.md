# 工作流进化助理

> Agent 入口：`.cursor/skills/workflow-evolution-assistant/SKILL.md` · `.claude/skills/workflow-evolution-assistant/SKILL.md` · `.codex/skills/workflow-evolution-assistant/SKILL.md`

## 触发条件

当用户说以下任一时执行：

- 「工作流进化」「流程进化」「优化工作流」「流程优化」
- 「反馈闭环」「skill_run 聚合」「反馈聚合」「vault evolve」
- 「把这次踩坑沉淀到流程」「把孤立反馈归位」「流程改进沉淀」
- `/workflow-evolution` / `/workflow-evolution-assistant`

**不响应（让位给其他 Skill）**：

- 具体需求、架构、开发、测试执行 → 对应阶段 Skill
- 日报、周报、项目复盘 → `report-assistant`
- WBS 修订 / 拆任务 → `task-splitter` 或用户确认

## 职责

本 Skill 是 AI-Work-Kit 的「元工作流」：它不做某个阶段的业务产出，而是把各阶段留下的反馈、卡点和漂移，转化为下一轮工作更顺的系统改进。

它主要处理五类问题：

| 类型 | 典型信号 | 常见落点 |
|------|----------|----------|
| 路由问题 | 用户说法命中多个 Skill、入口抢活、阶段推荐不准 | `Skills/`、`.cursor/.claude/.codex/skills/`、`workflow-router-check.py` |
| 门禁问题 | workflow-gate 放行/阻塞不符合事实 | `.workflows/blueprints/`、`scripts/workflow-gate.sh`、`scripts/gate_parse.py` |
| 模板问题 | plan 字段缺失、AC/WBS/skill_run 无法校验 | `Templates/`、阶段 Skill |
| 工具问题 | 脚本名漂移、命令输出太噪、缺状态摘要 | `scripts/`、`Contexts/决策/` |
| 反馈问题 | skill_run 缺失、不合规、孤立反馈长期未归位 | `Contexts/决策/孤立反馈记录.md`、`feedback-aggregate.py`、`vault-evolve.py` |

## 输入材料

优先读用户指定材料；若用户只说「进化一下工作流」，按以下顺序找证据：

1. `Contexts/决策/孤立反馈记录.md` 的 `## 待整理` 未归位候选。
2. 最近的 `Contexts/决策/反馈聚合-YYYY-MM.md`。
3. `python3 scripts/feedback-aggregate.py --dry-run --month YYYY-MM`。
4. `scripts/workflow-status.py` 或 `scripts/workflow-gate.sh --json` 输出。
5. 涉及的 `.workflows/blueprints/*.json`、`Templates/*.md`、`Skills/*.md` 与 agent stub。

## 执行步骤

1. **判定模式**
   - 建议模式：用户只是讨论「是不是该进化」或要求分析。
   - 落地模式：用户说「做掉」「沉淀」「修」「更新 Skill/蓝图/模板」。

2. **收集证据**
   - 只采纳可追溯证据：plan、反馈块、脚本输出、模板/skill/蓝图原文。
   - 不把一次偶发偏好直接升级为长期规则；同类反馈 ≥3 次或用户明确拍板，才进入长期 `Contexts/`。

3. **形成改进项**
   每条改进必须写清：
   - 问题：具体哪里卡。
   - 证据：来自哪个文件或命令。
   - 改动：要改哪几个文件。
   - 验收：跑什么脚本确认。

4. **落地修改**
   - 改 Skill 时同步 `Skills/<name>.md` 与 `.cursor/.claude/.codex/skills/<name>/SKILL.md`。
   - 改蓝图时校验 schema，并尽量补路由/门禁回归样本。
   - 改长期 `Contexts/` 前必须用户确认；用户明确说「存档到 Contexts」除外。

5. **验证**
   根据改动类型运行最小校验集：
   ```bash
   bash scripts/sync-agent-skills.sh --check
   python3 scripts/validate-workflow-blueprint.py .workflows/blueprints/<name>.json
   python3 scripts/workflow-router-check.py "<utterance>"
   bash scripts/workflow-gate.sh --workflow <name> --json
   python3 scripts/test-workflow-refactor.py
   ```

6. **收口**
   - 告知已改文件与验证结果。
   - 若本次服务某个进化 plan，把 `skill_run` 追加到该 plan 末尾。
   - 若无 plan，不写完整过程小票：未落地的进化项写入 `Contexts/决策/孤立反馈记录.md` 的 `## 待整理`；已落地的只在 `## 已归位` 补一行摘要。
   - 孤立反馈只保存“以后怎么用/还要做什么”，不保存“这次我是怎么操作的”。

## 输出模板

### 建议模式

```markdown
结论：值得/暂不值得进化。

证据：
- ...

建议改动：
- 文件：...
  原因：...
  验收：...

需要你拍板：
- ...
```

### 落地模式

```markdown
已落地：
- ...

验证：
- ...

风险/待拍板：
- ...
```

## 反馈回路

按 `Contexts/决策/Skill反馈协议.md` 收口：

- 有进化 plan：在 plan 末尾追加 `## 反馈（skill_run）`。
- 无 plan 且产生未落地候选：写入 `Contexts/决策/孤立反馈记录.md` 的 `## 待整理`，标题用 `### 进化候选：...` 或 `### 待整理：...`。
- 无 plan 且本次已落地：只在 `## 已归位` 补一行摘要，指向落点与验证方式。

禁止把无 plan 执行过程以完整 `skill_run` YAML 小票写入孤立反馈；过程细节会累计太快，且会污染候选区。
