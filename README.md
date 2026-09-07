# AI-Work-Kit

一个人主导的 LLM 工作台：人给目标、方向和授权边界，LLM 高效完成明确工作，结果由模型外的证据验证。

它不包含固定工作流、阶段状态机、Epic、Gate 或进度看板。

## 使用

用 Cursor、Claude Code 或 Codex 打开本仓库，然后直接描述目标。AI 会读取现实上下文，在授权范围内执行可撤销、可验证的动作；需要价值判断、权限扩大、外部承诺或不可逆操作时再请人决定。

核心原则：[Knowledge/决策/Kit核心原则.md](Knowledge/决策/Kit核心原则.md)
入口索引：[索引.md](索引.md)

## 目录

- `Knowledge/`：跨任务仍成立的知识。
- `Skills/`：按需调用的能力；不规定任务顺序。
- `Sessions/`：仅为跨会话或交接保留的可选快照。
- `scripts/`：Skill 同步与 Kit 不变量验证。

## 校验与同步

```bash
python3 scripts/verify-kit.py
python3 scripts/sync-skills.py --sync
python3 scripts/sync-skills.py --check
```
