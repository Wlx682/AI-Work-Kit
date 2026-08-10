---
name: workflow-router
description: 自然语言工作流入口。用户说全流程开发、启动项目、做个客户端功能、Story 拆分、用户故事拆分、合代码、合并分支、解决合并冲突、帮我清理电脑、做界面、修 bug、我要学习、准备学习资料、学习复盘、workflow=xxx 时触发；只负责选择具体 workflow 蓝图、确保 Epic/看板启动、运行 workflow-status，必要时查看 workflow-gate，不做具体阶段工作。
---

# 工作流路由器

定位：**入口 Skill / 路由器**，不是业务执行 Skill。  
职责：自然语言 → 选择具体 workflow 蓝图 → 复用电脑/Kit 级安装检查缓存并只做必要运行时预检 → 启动执行器 → 用 `workflow-status.py` 汇报任务状态 → 仅在缺失时创建阶段 Plan → 把下一步交给阶段 Skill。

## 触发

- 全流程开发、启动项目、启动全流程、一条龙、做个功能、开发一个客户端功能
- 帮我看一下电脑空间、电脑管理、清理电脑、整理电脑、磁盘满了、磁盘空间、释放空间、备份/加固/复核电脑
- 做界面、Figma 对稿、页面视觉不对齐、样式调整
- 修 bug、线上报错、崩溃、按钮点不动、问题排查
- Story 拆分、用户故事拆分、方案拆成用户故事、只拆 Story
- 合代码、合并代码、合分支、merge 分支、把这个分支合进去、解决合并冲突
- 我要学习、我想学习、帮我准备资料、学完实践、实践完验证、学习复盘、学习记录、总结知识图谱
- `workflow=client-dev`、`workflow=merge-code`、`workflow=computer-mgmt`、`workflow=ui-change`、`workflow=bugfix`、`workflow=story-split-only`、`workflow=learning-loop`

## 不触发

- 单阶段任务：PRD 评审、日报/周报、测试计划、部署清单、代码 review
- 普通代码任务：实现这个函数、写脚本、开发环境报错
- 普通资料整理：备份这份文档、整理需求列表、清理文档
- 无效显式工作流：`workflow=unknown` 时先提示未知 workflow，不回退默认蓝图

## 不做

- 不写需求分析正文
- 不写技术方案
- 不写代码
- 不改 `lifecycle_state` 推进阶段
- 不替代 `event-storming`、`requirement-analyst`、`feature-dev`、`figma-ui` 等阶段 Skill
- 不允许只加载本 Skill 后直接读写业务代码；命中 workflow 后必须先完成下方“执行”链路

## 执行

硬门禁：一旦选中 workflow，必须先完成“选蓝图 → 缓存感知 preflight → status → 必要时 plan-init → status”，再调用阶段 Skill 或进入业务代码。安装静态项是电脑/Kit 级状态，不得要求用户为每个项目重复安装；`status` 和条件式 `plan-init` 是任务级动作，由 Agent 内部执行，不要求用户复制粘贴例行命令。若 `workflow-status.py` 显示缺当前阶段子 plan，Epic 工作流运行 `workflow-plan-init.py --workflow <name> --epic <path>`，轻流程运行 `workflow-plan-init.py --workflow <name> --title <标题>`；禁止跳过这一步直接执行阶段工作。

1. 选择蓝图：
   - 显式 `workflow=xxx` 优先
   - 有 Epic 时读 Epic frontmatter `workflow:`
   - 否则由宿主模型按用户语义、蓝图 `label/description` 与 `triggerHints` 做高置信判断；学习型请求优先考虑 `learning-loop`
   - `scripts/workflow-router-check.py` 只作为触发词回归检查与低成本兜底，不是唯一判断来源
   - 无法命中具体 workflow 时，阻塞确认
   - 若用户显式写了不存在的 `workflow=xxx`，先阻塞确认，不要静默回退
   - 不把抽象执行器当成业务 workflow，也不用它给 `client-dev` 兜底
   - 语义判断只选择现有业务蓝图；一句话同时像多个蓝图时先问清楚
2. 启用前置检查：
   - 选定蓝图后运行 `python3 scripts/workflow-install.py check --workflow <name>`；静态电脑/Kit 检查命中缓存时只保留看板端口等运行时检查，不得全量重检
   - 首次使用、缓存因 Kit/Skill/Hook/全局指令变化而失效，或显式排查环境时才重新执行静态检查；强制重检使用 `--refresh`
   - 若出现 `BLOCK`，先处理 Skill 多端入口、全局工作流优先级、pre-commit hook、看板端口互斥或缺失脚本
   - `apply` 是首次安装或修复动作，不是每项目动作；可自动修复的本地 hook 用 `python3 scripts/workflow-install.py apply --workflow <name>`，Skill 全局同步需用户明确授权再加 `--sync-skills`
3. 启动看板:
   - `client-dev` 的 `.workflows/blueprints/client-dev.json` 固化 `startup.createBoard=true`
   - `usesEpic=true` 的蓝图必须先有 Epic；`client-dev` 用 `Templates/Epic模板-client-dev.md`，`learning-loop` 用 `Templates/Epic模板-learning-loop.md`
   - 已有/刚创建 Epic：`bash scripts/workflow-board-boot.sh --epic Plans/Epic/xxx.md`
   - `--new-requirement` 只允许临时启动空看板服务，不算完成 client-dev 启动
4. 看状态：
   - 下列 `status` / `plan-init` 命令由 Agent 内部执行；只有执行环境不可用或需要用户授权时才交给用户
   - 有 Epic：`python3 scripts/workflow-status.py --workflow <name> --epic Plans/Epic/xxx.md`
   - 有 Epic 且缺当前阶段 Plan：`python3 scripts/workflow-plan-init.py --workflow <name> --epic Plans/Epic/xxx.md`，再重新 status
   - 有项目名：`python3 scripts/workflow-status.py --workflow <name> --project <模块名>`
   - 无 Epic 的轻量工作流：`python3 scripts/workflow-status.py --workflow <name>`；若缺当前阶段 plan，先 `python3 scripts/workflow-plan-init.py --workflow <name> --title <任务标题>`，再重新 status；代码/分支合并使用 `merge-code`
   - 学习循环：`python3 scripts/workflow-status.py --workflow learning-loop --epic Plans/Epic/xxx.md`
   - 需要底层字段时再跑 `bash scripts/workflow-gate.sh --workflow <name> --epic Plans/Epic/xxx.md --json`
5. 根据 `recommended_skill` 调用真正阶段 Skill；若 `usesEpic=true` 的蓝图阻塞为缺 Epic，必须先调用 `template-generator` 创建对应 Epic，然后重新 `boot --epic` 打开具体看板。
   - 当前阶段缺子 Plan 时只创建当前阶段，不使用 `--all`；`usesEpic=true` 传 `--epic`，`usesEpic=false` 传 `--title`。

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
python3 scripts/workflow-router-check.py '全流程开发一下支付收银台' '帮我合代码' '这个方案拆成用户故事'
python3 scripts/test-workflow-refactor.py
```

同步：`Skills/workflow_router.md`
