# skill-sync · 技能多端部署 / 同步

## 用途

把 Skill 定义从**真理源** `.cursor/skills/` 部署（传播）到各 Agent 的生效目录，并校验多端一致。这是一个**运维类 Skill**，不修改任何 Skill 的业务内容。

## 触发词

「部署所有技能」「部署技能」「同步技能」「刷新技能」「技能同步」「更新技能到全局」「skill sync」「/skill-sync」。

## 多端约定

| 位置 | 角色 | 是否入 git |
|------|------|-----------|
| `.cursor/skills/<name>/SKILL.md` | **真理源**（agent stub） | 是 |
| `.claude/skills/<name>/SKILL.md` | Claude Code 生成端 | 否（gitignore，脚本生成） |
| `.codex/skills/<name>/SKILL.md` | Codex 生成端 | 否（gitignore，脚本生成） |
| `~/.claude/skills/<name>/` · `~/.codex/skills/<name>/` | 全局副本（仅覆盖项目内同名，保留用户自装） | — |
| `Skills/<name>.md` | 人类阅读真理源（下划线命名） | 是 |

## 执行步骤

```bash
# 1. 干跑校验，看清差异（默认模式，只读不写）
./scripts/sync-claude-skills.sh --check

# 2. 部署：以 .cursor/skills 为基准覆盖生成端 + 全局同名副本，并清理项目生成端旧 Skill
./scripts/sync-claude-skills.sh --sync

# 3. 复校验，期望「✓ 多端一致：N 个 Skill」
./scripts/sync-claude-skills.sh --check
```

## 为什么需要它

真理源 `.cursor/skills/` 改动后，其它三端不会自动跟随，`--check` 默认也只报警不写。此前没有任何自动触发点，导致 Skill 漂移（例如新增 Skill 全局不生效、内容改了旧版仍在跑）。本 Skill 让「部署所有技能」这类自然语言即可一键传播。

## 注意

- `--sync` 会 `rm -rf` 目标端同名目录再复制，是预期覆盖行为。
- 项目生成端会自动删除 `.cursor/skills` 已不存在的旧 Skill，避免同步后还需手动清理才能通过 `--check`。
- 全局只动项目内同名 Skill，不碰用户自装的。
- 若报「Skills/ 缺真理源」，先补 `Skills/<name>.md` 再 `--sync`。
- 创建或修改 Skill 后的完整校验链见 `Skills/README.md`「创建 / 修改 Skill 的最小校验链」。
- 幂等，可安全重复执行。

## 关联

- 脚本：`scripts/sync-claude-skills.sh`（`sync-agent-skills.sh` 是其 wrapper）
- 反馈协议：`Contexts/决策/Skill反馈协议.md`
