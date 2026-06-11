# 学习进度审计 Skill

当用户说「审计学习进度」「学习审计」「learning-audit」「检查学习计划完成度」「声称进度 vs 真实进度」时执行。

> **Claude Code 等价物**：`.claude/workflows/learning-audit.js`（`/learning-audit`）  
> **Cursor 等价物**：本 Skill + `scripts/learning-audit-collect.sh`

## 解决的问题

plan 的 frontmatter 写「已完成」，但步骤复选框未勾选、笔记未写。单会话自查易遗漏；本流程用**分阶段取证 + 交叉比对**降低自我欺骗。

## 三阶段（对齐 learning-audit workflow）

| 阶段 | 动作 | Cursor 做法 |
|------|------|-------------|
| 1. 发现课程 | 列出 `Plans/学习/*.md` | 跑 `scripts/learning-audit-collect.sh` 或 glob |
| 2. 逐课取证 | 四类证据并行采集 | 每课独立读文件（不要一次会话混读下结论） |
| 3. 交叉比对 | 写审计报告 | 汇总后写入 `Contexts/LLM学习/笔记/` |

## 四类证据

| 维度 | 数据来源 | 判定要点 |
|------|----------|----------|
| A. 声称状态 | plan frontmatter `status:` | 原文记录，不解释 |
| B. 步骤勾选 | 同文件 `- [ ]` / `- [x]` | 用脚本计数为准 |
| C. 概念卡 | plan 资料区 `[[双链]]` → `Contexts/LLM学习/概念/` | 存在 `.md` 即可；**不能证明学完** |
| D. 学习笔记 | `Contexts/LLM学习/笔记/` | 须以本课为主题；其他笔记里的交叉链接**不算** |

### verdict 规则

| 情况 | verdict |
|------|---------|
| status=已完成，但勾选 0 或无本课笔记 | **严重矛盾** |
| status=进行中/未开始，证据相符 | **一致** |
| 介于两者之间（如标已完成但只勾一半） | **轻微偏差** |

## 执行步骤

1. **机械取证**（vault 根目录）：
   ```bash
   ./scripts/learning-audit-collect.sh Plans/学习
   ```
2. **逐课语义取证**：对每节课 plan 单独读取，提取双链概念卡、练习表是否填写、笔记目录是否有本课笔记。
3. **写报告**：`Contexts/LLM学习/笔记/YYYY-MM-DD-学习进度审计报告.md`（同名可覆盖）。

### 报告结构

```markdown
---
tags: [学习, 审计报告, workflow]
date: YYYY-MM-DD
---

# 学习进度审计报告（LLM 学习路线）

【一段综合结论：声称 vs 证据是否存在系统性偏差】

## 总览

| 课程 | 声称状态 | 实际完成度 | 步骤(勾选/总) | 概念卡 | 有笔记 | 一致性 |

## ⚠️ 发现的不一致

## 下一步建议

---
由 learning-audit（Cursor: learning-audit-assistant）生成 · YYYY-MM-DD
```

4. **回复用户**：报告路径 + 一句话 summary + 矛盾最严重的 1–2 课。

## 可选参数

```
/learning-audit-assistant
/learning-audit-assistant 日期=2026-06-12
/learning-audit-assistant plans=Plans/学习
```

## 与 learn-assistant 分工

| | learn-assistant | learning-audit-assistant |
|--|-----------------|--------------------------|
| 目的 | 学下一课、考我、整理笔记 | **审计**声称进度是否可信 |
| 产出 | plan 进度、学习笔记 | 审计报告 |
| 何时用 | 日常学习 | 周末/交作业前/感觉「好像学完了」时 |
| 自动收集 | **learn-assistant 统一负责**（开场读 + 收尾快照） | 全量交叉比对 → `学习进度审计报告.md` |

被 learn-assistant 转交审计时：审计前已读进度；审计后由 learn-assistant 收尾快照。

### 定时全量审计（可选）

在 Cursor Automations 或 Claude `/loop` 中每周跑一次 `/learning-audit-assistant`，与每次学习后的快照互补。

## 触发示例

```
/learning-audit-assistant
审计我的学习进度
跑 learning-audit
检查 Plans/学习 真实完成度
```

同步：`.cursor/skills/learning-audit-assistant/SKILL.md` · Claude：`.claude/workflows/learning-audit.js`
