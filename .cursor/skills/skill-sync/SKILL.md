---
name: skill-sync
description: 技能多端部署/同步。用户说「部署所有技能」「部署技能」「同步技能」「刷新技能」「技能同步」「skill sync」「更新技能到全局」时触发；以 .cursor/skills 为真理源，跑 scripts/sync-claude-skills.sh --sync 把技能传播到 .claude / .codex 及全局 ~/.claude/skills、~/.codex/skills，并校验多端一致。不响应：写具体某个 Skill 内容→对应阶段 Skill；工作流进化/反馈聚合→workflow-evolution-assistant。
---

# 技能同步 / 部署

定位：**运维 Skill**，把 Skill 定义从真理源部署到各 Agent 生效目录，不改任何 Skill 的业务内容。

## 触发

- 部署所有技能、部署技能、部署 Skill、发布技能
- 同步技能、刷新技能、技能同步、更新技能、更新技能到全局
- `skill sync`、`/skill-sync`、`sync skills`

## 不触发

- 写/改某个具体 Skill 的内容 → 交给对应阶段 Skill 或直接编辑 `.cursor/skills/<name>/SKILL.md`
- 工作流进化、反馈聚合、流程改进沉淀 → `workflow-evolution-assistant`
- 新建一个全新 Skill 的正文设计 → 由用户/对应 Skill 先写好 stub，再来这里部署

## 真理源与目标端

- 真理源：`.cursor/skills/<name>/SKILL.md`（agent stub）
- 生成端：`.claude/skills/<name>/SKILL.md`、`.codex/skills/<name>/SKILL.md`（gitignore，由脚本生成）
- 全局副本：`~/.claude/skills/<name>/`、`~/.codex/skills/<name>/`（仅覆盖项目内同名，保留用户自装）
- 人类真理源：`Skills/<name>.md`（下划线命名，dash→underscore），只检查存在性

## 执行

1. 先干跑校验，让用户看清将变更什么：
   ```bash
   ./scripts/sync-claude-skills.sh --check
   ```
   - 退出码 0 且「多端一致」→ 已同步，无需再动，据实告知用户。
   - 有差异（缺失 / 内容不一致 / 缺真理源）→ 列出差异摘要给用户。
2. 执行部署（以 `.cursor/skills` 为基准强制覆盖生成端与全局同名副本，并清理项目生成端旧 Skill）：
   ```bash
   ./scripts/sync-claude-skills.sh --sync
   ```
3. 复校验确认落地：
   ```bash
   ./scripts/sync-claude-skills.sh --check   # 期望：✓ 多端一致：N 个 Skill
   ```
4. 汇报：同步了几个 Skill、补齐/更新了哪些、全局保留了哪些用户自装 Skill。

## 注意

- `--sync` 会 `rm -rf` 目标端同名目录再复制，属预期覆盖；项目生成端会删除 `.cursor/skills` 已不存在的旧 Skill，确保复校验可直接通过；全局仅动项目内同名 Skill，不碰用户自装的。
- 若 `--check` 报「Skills/ 缺真理源」→ 先补 `Skills/<name>.md` 人类文档，再 `--sync`。
- 部署是幂等的，可安全重复执行。

## 反馈回路

任务结束按 `Contexts/决策/Skill反馈协议.md` 输出 `skill_run` YAML 块（无 plan → 追加到 `Contexts/决策/孤立反馈记录.md` 顶部）。
