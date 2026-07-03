# 工作流路由器 Skill

`workflow-router` 是自然语言入口，不是业务执行 Skill。它只负责把用户的话转成工作流蓝图与门禁命令，然后把任务交给真正的阶段 Skill。

## 触发时机

- 「全流程开发」「启动项目」「启动全流程」「一条龙」「做个功能」「开发一个客户端功能」
- 「帮我看一下电脑空间」「电脑管理」「清理电脑」「整理电脑」「磁盘满了」「磁盘空间」「释放空间」「备份电脑」「系统加固」
- `/full-cycle`
- `workflow=client-dev` / `workflow=computer-mgmt`

## 不触发时机

- 单阶段任务：PRD 评审、日报/周报、学习审计、Figma 对稿、测试计划、部署清单、代码 review
- 普通代码任务：实现这个函数、写脚本、修 bug、开发环境报错
- 普通资料整理：备份这份文档、整理需求列表、清理文档
- 无效显式工作流：`workflow=unknown` 时先提示未知 workflow，不回退默认蓝图

## 职责边界

只做：

1. 选择 workflow 蓝图
2. 启动看板
3. 运行 `workflow-status.py` 输出人话状态
4. 必要时再查看 `workflow-gate.sh --json` 详情

不做：

- 不写需求、方案、代码、测试、部署内容
- 不替代阶段 Skill
- 不靠 `lifecycle_state` 推进流程
- 不把 Epic 当状态机

## 蓝图选择

优先级：

1. 用户显式 `workflow=xxx`
2. Epic frontmatter `workflow:`
3. 自然语言匹配 `.workflows/blueprints/<name>.json` 的 `triggerHints`
4. 默认 `client-dev`，并说明是默认选择

若用户显式写了不存在的 `workflow=xxx`，先阻塞确认，不要静默回退。

常见匹配：

| 用户说法 | 蓝图 |
|----------|------|
| 客户端功能、做个功能、全流程开发 | `client-dev` |
| 电脑空间、电脑管理、清理电脑、磁盘满了、释放空间、备份电脑、加固 | `computer-mgmt` |

## 回归检查

新增或调整触发词后，先跑自然语言样本检查：

```bash
python3 scripts/workflow-router-check.py '全流程开发一下支付收银台' '帮我清理电脑缓存' '实现这个函数'
python3 scripts/test-workflow-refactor.py
```

## 命令

新需求先启动看板服务：

```bash
bash scripts/full-cycle-boot.sh --new-requirement
```

已有 Epic：

```bash
bash scripts/full-cycle-boot.sh --epic Plans/Epic/xxx.md
python3 scripts/workflow-status.py --workflow client-dev --epic Plans/Epic/xxx.md
```

按项目名定位 Epic：

```bash
python3 scripts/workflow-status.py --workflow client-dev --project 模块名
```

无 Epic 轻量工作流：

```bash
python3 scripts/workflow-status.py --workflow computer-mgmt
```

需要排查底层字段时再跑：

```bash
bash scripts/workflow-gate.sh --workflow client-dev --epic Plans/Epic/xxx.md --json
```

## 输出

```text
当前：验收测试先行
卡点：P0 反例 AC1-反 还没有测试用例
下一步：补自动化测试 plan 的用例映射
继续：/resume plan=Plans/自动化测试/xxx.md
```

若 `blockers` 里提示缺 Epic，下一步是 `template-generator` 创建 Epic；不要手写 `lifecycle_state` 试图推进。
