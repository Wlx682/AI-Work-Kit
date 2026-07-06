---
name: workflow-router
description: 自然语言工作流入口。用户说全流程开发、启动项目、做个客户端功能、帮我清理电脑、学习工作流、workflow=xxx 时触发；只负责选择具体 workflow 蓝图、确保 Epic/看板启动、运行 workflow-status，必要时查看 workflow-gate，不做需求/架构/开发/测试等阶段工作。
---

# 工作流路由器

定位：**入口 Skill / 路由器**，不是业务执行 Skill。  
职责：自然语言 → 选择具体 workflow 蓝图 → 启动执行器 → 用 `workflow-status.py` 汇报人话状态 → 把下一步交给阶段 Skill。

## 触发

- 全流程开发、启动项目、启动全流程、一条龙、做个功能、开发一个客户端功能
- 帮我看一下电脑空间、电脑管理、清理电脑、整理电脑、磁盘满了、磁盘空间、释放空间、备份/加固/复核电脑
- 学习工作流、智能体开发学习
- `workflow=client-dev`、`workflow=computer-mgmt`、`workflow=learning-agent-dev`

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
   - 无法命中具体 workflow 时，阻塞确认
   - 若用户显式写了不存在的 `workflow=xxx`，先阻塞确认，不要静默回退
   - 不把抽象执行器当成业务 workflow，也不用它给 `client-dev` 兜底
2. 启动看板：
   - `client-dev` 的 `.workflows/blueprints/client-dev.json` 固化 `startup.createBoard=true`
   - `client-dev` 客户端开发必须先有 Epic；若无 Epic，先调用 `template-generator` 用 `Templates/Epic模板-client-dev.md` 创建 `Plans/Epic/xxx.md`
   - 已有/刚创建 Epic：`bash scripts/workflow-board-boot.sh --epic Plans/Epic/xxx.md`
   - `--new-requirement` 只允许临时启动空看板服务，不算完成 client-dev 启动
3. 看状态：
   - 有 Epic：`python3 scripts/workflow-status.py --workflow <name> --epic Plans/Epic/xxx.md`
   - 有项目名：`python3 scripts/workflow-status.py --workflow <name> --project <模块名>`
   - 无 Epic 的轻量工作流：`python3 scripts/workflow-status.py --workflow <name>`
   - 需要底层字段时再跑 `bash scripts/workflow-gate.sh --workflow <name> --epic Plans/Epic/xxx.md --json`
4. 根据 `recommended_skill` 调用真正阶段 Skill；若 `client-dev` 阻塞为缺 Epic，必须先调用 `template-generator` 创建 Epic，然后重新 `boot --epic` 打开具体看板。

## 输出

```text
当前：[阶段人话名]
卡点：[一句话 blocker]
下一步：[下一步动作]
继续：/resume plan=Plans/.../xxx.md
```

## 回归检查

新增或调整触发词后，先跑自然语言样本检查：

```bash
python3 scripts/workflow-router-check.py '全流程开发一下支付收银台' '帮我清理电脑缓存' '实现这个函数'
python3 scripts/test-workflow-refactor.py
```

同步：`Skills/workflow_router.md`
