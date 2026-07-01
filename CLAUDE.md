# AI-Work-Kit · Claude Code 项目说明

> 与 Cursor 共用 Vault。集成：[[Contexts/Claude-Code集成AI-Work-Kit]]。

## 核心原则

**只认** [[Contexts/决策/Kit核心原则]]：`Plans/` 任务临时 · `Contexts/` 通用固定 · 做完删 plan。  
YAML/Epic：[[Templates/模板约定]] · 工作流：[[Contexts/决策/AI-Work-Kit工作流总览]]。

## 多仓库

- Vault：本仓库。代码：Claude 当前工作目录。仅 Vault 时向用户要代码路径。

## 目录

| 路径 | 用途 |
|------|------|
| `Plans/` | 进行中（Epic、需求、开发、学习…） |
| `Contexts/` | 通用规范与长期资料 |
| `Templates/` · `Skills/` · `scripts/` | 模板、Skill、脚本 |
| `.claude/workflows/` | full-cycle、learning-audit 等 |

## 规则

1. 查资料 → `Plans/` + `Contexts/`（可选 enquire MCP）。
2. 写 **Contexts 前须用户确认**（「存档到 Contexts」除外）。
3. Epic 入口与 Cursor `.cursorrules` 一致；无 Epic 不建功能主 plan。
4. **Skill 路由硬规则**（与 `.cursorrules` 一致）：含「界面/对稿/还原/Figma」或 WBS 指定 `figma-ui` → 强制 `figma-ui`，`feature-dev-assistant` 不得替代；WBS 修订/拆任务 → `task-splitter` 或用户确认，禁止擅自推荐 A/B/C 方案。
5. **反馈回路硬规则**：任务结束必须输出 `skill_run` YAML 块。有 plan 追加到 plan 末尾；无 plan 追加到 `Contexts/决策/孤立反馈记录.md` 顶部。`utility` 二选一：`high`（必给一句话理由）/ `not-needed`。协议：[[Contexts/决策/Skill反馈协议]]；校验：`scripts/plan-gate-check.sh`。

## Skill 表

与 `.cursorrules` Skill 触发一致；显式引用 `@Skills/xxx.md`。

| 说法 | Skill |
|------|-------|
| 续做 | `resume-assistant` |
| 全流程 / full-cycle | `full-cycle-assistant` + `full-cycle-boot.sh` |
| 需求/架构/开发/测试/部署/变更 | 见 `.cursorrules` |
| 学习 | `learn-assistant`（snapshot stdout） |
| PM 物料 | `material-prep-assistant` → Contexts |
| 找 CC 文章 / 周报选题 / 海外资讯 / 分享帖 | `weekly-intel-digest` → `Contexts/情报源/` |
| 提效案例 / 最佳实践 / 技术提交分享 / 产品提效 | `best-practice-digest` → `Contexts/最佳实践/`（附 skill_run 反哺进化链） |

全流程步骤结束输出：

```text
📌 当前阶段：[阶段] | 下一个阶段：[Skill] | 如需中断：/resume plan=Plans/.../xxx.md
```

## 入口

[[索引]] · [[Contexts/决策/新手引导与最佳实践]] · [[Contexts/决策/Kit核心原则]]
