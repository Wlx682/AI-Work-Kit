# 工作流路由器 Skill

`workflow-router` 是自然语言入口，不是业务执行 Skill。它只负责把用户的话转成工作流蓝图与门禁命令，然后把任务交给真正的阶段 Skill。

## 触发时机

- 「全流程开发」「启动项目」「启动全流程」「一条龙」「做个功能」「开发一个客户端功能」
- 「帮我看一下电脑空间」「电脑管理」「清理电脑」「整理电脑」「磁盘满了」「磁盘空间」「释放空间」「备份电脑」「系统加固」
- 「做界面」「Figma 对稿」「页面视觉不对齐」「样式调整」
- 「修 bug」「线上报错」「崩溃」「按钮点不动」「问题排查」
- 「Story 拆分」「用户故事拆分」「方案拆成用户故事」「只拆 Story」
- 「合代码」「合并代码」「合分支」「merge 分支」「把这个分支合进去」「解决合并冲突」
- 「我要学习」「我想学习」「帮我准备资料」「学完实践」「实践完验证」「学习复盘」「学习记录」「总结知识图谱」
- 「创意捕捉」「信息输入少」「新鲜感匮乏」「跨领域灵感」「副业创意」「每周创意合成」

## 不触发时机

- 普通代码任务：实现这个函数、写脚本、开发环境报错
- 普通资料整理：备份这份文档、整理需求列表、清理文档
- 无效显式工作流：`workflow=unknown` 时先提示未知 workflow，不回退默认蓝图

## 职责边界

只做：

1. 选择 workflow 蓝图
2. 运行蓝图 `enablement.preflight`，确认工具入口、hook、全局优先级与互斥环境可用
3. 确保客户端开发 Epic 存在并启动看板
4. 运行 `workflow-status.py` 输出人话状态
5. 必要时再查看 `workflow-gate.sh --json` 详情
6. 任一工作流缺当前阶段 plan 时，用 `workflow-plan-init.py` 创建当前阶段 plan；Epic 工作流传 `--epic` 并严格写入 `plans.<epicField>` 指定路径

不做：

- 不写需求、方案、代码、测试、部署内容
- 不替代阶段 Skill
- 不靠 `lifecycle_state` 推进流程
- 不把 Epic 当状态机
- 不允许只加载本 Skill 后直接读写业务代码；命中 workflow 后必须先完成“选蓝图 → preflight → status → 必要时 plan-init → status”

## 蓝图选择

硬门禁：一旦选中 workflow，必须先完成“选蓝图 → preflight → status → 必要时 plan-init → status”，再调用阶段 Skill或进入业务代码。若 `workflow-status.py` 显示缺当前阶段子 plan，Epic 工作流运行 `workflow-plan-init.py --workflow <name> --epic <path>`，轻流程运行 `workflow-plan-init.py --workflow <name> --title <标题>`；禁止跳过这一步直接执行阶段工作。

优先级：

1. 用户显式 `workflow=xxx`
2. Epic frontmatter `workflow:`
3. 宿主模型按用户语义、蓝图 `label/description` 与 `triggerHints` 做高置信判断
4. `scripts/workflow-router-check.py` 作为触发词回归检查与低成本兜底
5. 无法命中具体 workflow 时，阻塞确认，不使用默认引擎兜底

若用户显式写了不存在的 `workflow=xxx`，先阻塞确认，不要静默回退。
不要把抽象执行器当成业务 workflow，也不要用它给 `client-dev` 兜底。

语义判断只用于选择现有业务蓝图，不新增临时 workflow。若一句话同时像多个蓝图，先问清楚；若只是单阶段 Skill（例如 PRD 评审、日报、技术方案模板、写测试计划、部署清单、代码 review），让位给对应 Skill。

常见匹配：

| 用户说法 | 蓝图 |
|----------|------|
| 客户端功能、做个功能、全流程开发 | `client-dev` |
| 电脑空间、电脑管理、清理电脑、磁盘满了、释放空间、备份电脑、加固 | `computer-mgmt` |
| 做界面、Figma 对稿、还原设计稿、样式调整 | `ui-change` |
| 修 bug、线上报错、崩溃、问题排查 | `bugfix` |
| Story 拆分、用户故事拆分、方案拆成用户故事、只拆 Story | `story-split-only` |
| 合代码、合并代码、合分支、解决合并冲突 | `merge-code` |
| 我要学习、准备学习资料、实践验证、学习复盘、学习记录、知识图谱 | `learning-loop` |
| 创意捕捉、信息输入少、跨领域灵感、副业创意、每周创意合成 | `creative-capture` |

## 回归检查

新增或调整触发词后，先跑自然语言样本检查：

```bash
python3 scripts/workflow-router-check.py '全流程开发一下支付收银台' '帮我合代码' '帮我清理电脑缓存'
python3 scripts/test-workflow-refactor.py
```

## 启用前置检查

选定蓝图后，启动看板或创建阶段 plan 前先执行蓝图声明的 preflight：

```bash
python3 scripts/workflow-install.py check --workflow <name>
```

若输出 `BLOCK`，先处理安装项：Skill 多端入口、全局工作流优先级、pre-commit hook、看板端口互斥或缺失脚本。可自动修复的本地 hook 用：

```bash
python3 scripts/workflow-install.py apply --workflow <name>
```

## client-dev Epic 硬门禁

`client-dev` 客户端开发必须创建 Epic；Epic 是看板的数据源。若用户说「客户端全流程开发 PRD=...」「客户端功能」「做个客户端项目」但还没有 `Plans/Epic/xxx.md`，下一步不是停在空看板，也不是直接做需求分析，而是先调用 `template-generator` 按 `Templates/Epic模板-client-dev.md` 创建 Epic，再用该 Epic 启动看板。

这条规则固化在 `.workflows/blueprints/client-dev.json` 的 `startup.createBoard=true` 与 `startup.requireEpicBeforeBoot=true`；入口只执行蓝图契约，不临场判断。

临时命令 `bash scripts/workflow-board-boot.sh --new-requirement` 只允许用于启动空看板服务，不算完成 `client-dev` 看板启动。

## 命令

客户端新需求先创建 Epic，再启动具体看板：

```bash
/template-generator 任务类型=Epic，workflow=client-dev，标题=模块名，PRD=...
bash scripts/workflow-board-boot.sh --epic Plans/Epic/xxx.md
python3 scripts/workflow-status.py --workflow client-dev --epic Plans/Epic/xxx.md
```

仅临时启动空看板服务：

```bash
bash scripts/workflow-board-boot.sh --new-requirement
```

已有 Epic：

```bash
bash scripts/workflow-board-boot.sh --epic Plans/Epic/xxx.md
python3 scripts/workflow-status.py --workflow client-dev --epic Plans/Epic/xxx.md
```

按项目名定位 Epic：

```bash
python3 scripts/workflow-status.py --workflow client-dev --project 模块名
```

无 Epic 轻量工作流：

```bash
python3 scripts/workflow-status.py --workflow bugfix
python3 scripts/workflow-plan-init.py --workflow bugfix --title 案例视频产物预览标题错误
python3 scripts/workflow-status.py --workflow bugfix
python3 scripts/workflow-plan-init.py --workflow merge-code --title feature-search合入main
python3 scripts/workflow-plan-init.py --workflow creative-capture --title 2026-W33
python3 scripts/workflow-status.py --workflow computer-mgmt
python3 scripts/workflow-status.py --workflow merge-code
python3 scripts/workflow-status.py --workflow creative-capture --project 2026-W33
```

学习循环：

```bash
# 先用 Templates/Epic模板-learning-loop.md 创建 Plans/Epic/xxx.md
bash scripts/workflow-board-boot.sh --epic Plans/Epic/xxx.md
python3 scripts/workflow-status.py --workflow learning-loop --epic Plans/Epic/xxx.md
```

需要排查底层字段时再跑：

```bash
bash scripts/workflow-gate.sh --workflow client-dev --epic Plans/Epic/xxx.md --json
```

## 输出

```text
当前：需求排序
卡点：Backlog 尚未由团队确认
下一步：按价值、紧迫度和依赖排序
继续：/resume plan=Plans/需求排序/xxx.md
```

若 `blockers` 里提示缺 Epic，下一步是 `template-generator` 创建 Epic；创建后必须重新 `boot --epic`。不要手写 `lifecycle_state` 试图推进。
