---
tags: [决策, 工作流, Epic]
date: 2026-06-20
---

# AI-Work-Kit 工作流总览

> **原则**（放哪、删不删）→ [[Contexts/决策/Kit核心原则]]（勿在本文件重复）  
> **格式**（YAML、续做）→ [[Templates/模板约定]]  
> **上手 Case** → [[分享包-快速开始]]

---

## 一、怎么用（给同事）

1. 打开 Vault + Cursor（或业务仓 + 全局 Skill）。
2. **新需求** → `/full-cycle 模块=XX`。
3. **续做** → `/resume plan=Plans/... 进度=...`。
4. **看 WBS** → `./scripts/full-cycle-boot.sh` → http://127.0.0.1:7777/

---

## 二、Epic 五阶段

| 阶段 | Skill | 产出 |
|------|-------|------|
| 需求 | `requirement-analyst` | `Plans/需求分析/` |
| 方案 | `architecture-design-assistant` | `Plans/客户端\|服务端技术方案/` |
| 开发 | `task-splitter` · `feature-dev-assistant` · `figma-ui-assistant` | `Plans/功能开发/` |
| 测试 | `test-generator` | `Plans/自动化测试/` |
| 部署 | `deployment-assistant` | `Plans/部署/` |

新建 Epic：复制 [[Templates/Epic母版]] → `Plans/Epic/`。

```mermaid
stateDiagram-v2
    direction LR
    [*] --> requirement
    requirement --> architecture: P0=0
    architecture --> development: 方案已采纳
    development --> test
    test --> deploy
    deploy --> done
    done --> [*]
```

---

## 三、独立任务（不建 Epic 或半独立）

| 任务 | 说法 | plan |
|------|------|------|
| Bug | `template-generator 任务类型=排查` | `Plans/Bug排查/` |
| 学习 | `/learn-assistant` | `Plans/学习/` |
| 纯 UI 小改 | `/figma-ui-assistant` | `Plans/功能开发/` |
| PM 对照表 | `/material-prep` | **Contexts/**（通用） |

---

## 四、看板与门禁

```bash
./scripts/full-cycle-boot.sh --epic Plans/Epic/xxx.md
bash scripts/full-cycle-gate.sh --epic Plans/Epic/xxx.md
bash scripts/kanban-sync.sh --boot --epic Plans/Epic/xxx.md
bash scripts/plan-gate-check.sh Plans/功能开发/xxx.md
```

| 脚本 | 用途 |
|------|------|
| `full-cycle-boot.sh` | 看板 + 浏览器 |
| `full-cycle-gate.sh` | Epic 阶段门禁 |
| `plan-gate-check.sh` | 写代码前 |
| `kanban-sync.sh` | Agent 改进度 |
| `generate-pipeline-status.sh --write` | 刷新 [[索引]] 进度表 |
| `learning-progress-read.sh` / `snapshot.sh` | 学习开/收尾 |

---

## 五、Skill 速查

开发主线：`full-cycle` · `requirement-analyst` · `architecture-design-assistant` · `task-splitter` · `feature-dev-assistant` · `figma-ui-assistant` · `test-generator` · `deployment-assistant` · `change-impact-analysis`

通用：`resume-assistant` · `template-generator` · `review-assistant` · `material-prep-assistant`

学习：`learn-assistant` · `learning-audit-assistant`

Claude workflow：`.claude/workflows/full-cycle.js` · `learning-audit` · `dev-lifecycle-audit`

详情：[[Skills/README]] · [[索引#高频任务速查]]

---

## 六、Figma（规范在 Contexts，任务在 Plans）

- 读节点：Figma MCP；度量表、走查 → **Plans**（见 [[Templates/Figma设计走查模板]]）。
- Contexts 只保留：[[Contexts/Figma/项目设计规范]]、[[Contexts/Figma/Figma界面开发最佳实践]]、[[Contexts/Figma/Figma-MCP配置]]。

---

## 相关

- [[Contexts/分享/2026-06-11-AI工作流的构建]]
- [[Contexts/Claude-Code集成AI-Work-Kit]]
