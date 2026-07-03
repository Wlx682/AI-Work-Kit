---
name: workflow-router
description: 自然语言工作流入口。用户说全流程开发、启动项目、做个客户端功能、帮我清理电脑、workflow=xxx、full-cycle 时触发；只负责选择蓝图、启动看板、运行 workflow-gate，不做需求/架构/开发/测试等阶段工作。
---

# 工作流路由器

定位：**入口 Skill / 路由器**，不是业务执行 Skill。  
职责：自然语言 → 选择 workflow 蓝图 → 启动 `full-cycle` 引擎 → 把下一步交给阶段 Skill。

## 触发

- 全流程开发、启动项目、启动全流程、一条龙、做个功能、开发一个客户端功能
- 帮我看一下电脑空间、电脑管理、清理电脑、整理电脑、磁盘满了、磁盘空间、释放空间、备份/加固/复核电脑
- `/full-cycle`、`workflow=client-dev`、`workflow=computer-mgmt`

## 不触发

- 单阶段任务：PRD 评审、日报/周报、学习审计、Figma 对稿、测试计划、部署清单、代码 review
- 普通代码任务：实现这个函数、写脚本、修 bug、开发环境报错
- 普通资料整理：备份这份文档、整理需求列表、清理文档
- 无效显式工作流：`workflow=unknown` 时先提示未知 workflow，不回退默认蓝图

## 不做

- 不写需求分析正文
- 不写技术方案
- 不写代码
- 不改 `lifecycle_state` 推进阶段
- 不替代 `event-storming`、`requirement-analyst`、`feature-dev`、`figma-ui` 等阶段 Skill

## 执行

1. 选择蓝图：
   - 显式 `workflow=xxx` 优先
   - 有 Epic 时读 Epic frontmatter `workflow:`
   - 否则用自然语言匹配 `.workflows/blueprints/<name>.json` 的 `triggerHints`
   - 不确定时默认 `client-dev`，并在输出中说明
   - 若用户显式写了不存在的 `workflow=xxx`，先阻塞确认，不要静默回退
2. 启动看板：
   - 新需求：`bash scripts/full-cycle-boot.sh --new-requirement`
   - 已有 Epic：`bash scripts/full-cycle-boot.sh --epic Plans/Epic/xxx.md`
3. 跑门禁：
   - 有 Epic：`bash scripts/workflow-gate.sh --workflow <name> --epic Plans/Epic/xxx.md`
   - 有项目名：`bash scripts/workflow-gate.sh --workflow <name> --project <模块名>`
   - 无 Epic 的轻量工作流：`bash scripts/workflow-gate.sh --workflow <name>`
4. 根据 `recommended_skill` 调用真正阶段 Skill；若阻塞为缺 Epic，调用 `template-generator` 创建 Epic。

## 输出

```text
📌 当前阶段：[current_state] | 下一个阶段：[recommended_skill] | 如需中断：/resume plan=Plans/.../xxx.md
```

## 回归检查

新增或调整触发词后，先跑自然语言样本检查：

```bash
python3 scripts/workflow-router-check.py '全流程开发一下支付收银台' '帮我清理电脑缓存' '实现这个函数'
python3 scripts/test-workflow-refactor.py
```

同步：`Skills/workflow_router.md`
