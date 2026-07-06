---
tags: [Epic, 学习, Agent, 工作流]
type: plan
category: Epic
status: 进行中
date: {{date}}
epic_id: learning-agent-dev-{{title-kebab}}
workflow: learning-agent-dev
lifecycle_state: topic  # 不参与路由；阶段由 workflow-gate.sh 依子 Plan 事实判定
topic: {{title}}
repo: /Users/wanglongxiang/git/agent-workflow-dev
branch: main
含业务逻辑: 否
p0_open: 0
plans:
  topic: Plans/学习/{{date}}-学习选题-{{title}}.md
  theory: null
  test: null
  project_setup: null
  tool_build: null
  integration_run: null
  retro: null
relations:
  depends_on:
    - Plans/学习/2026-07-06-智能体开发与工作流接入.md
    - .workflows/blueprints/learning-agent-dev.json
  dependents: []
  supersedes: []
  superseded_by: []
  conflicts: []

---
# 学习 Epic：{{title}}（工作流：learning-agent-dev）

> 每个知识点单独一个学习 Epic。完成本 Epic 只代表这个知识点闭环，不代表整条学习路线结束。

## 一、子 Plan 索引

| 阶段 | 路径 | status |
|------|------|--------|
| 选题 | `Plans/学习/{{date}}-学习选题-{{title}}.md` | ⬜ |
| 理论输入 | — | ⬜ |
| 测试先行 | — | ⬜ |
| 工程与技术选型 | — | ⬜ |
| 工具实现 | — | ⬜ |
| 接入试跑 | — | ⬜ |
| 效果复盘 | — | ⬜ |

## 二、阶段门禁

| 阶段 | stage key | WBS | 退出条件 |
|------|-----------|-----|----------|
| 选题 | topic | 1 | 选题 plan 存在 + `skill_run` |
| 理论输入 | theory | 2 | 理论 plan 存在 + `skill_run` |
| 测试先行 | test-first | 3 | 测试样例 plan 存在 + `skill_run` |
| 工程与技术选型 | project-setup | 4 | 独立工程、技术栈、测试命令明确 + `skill_run` |
| 工具实现 | tool-build | 5 | 最小工具动作完成 + `skill_run` |
| 接入试跑 | integration-run | 6 | 接入试跑记录完成 + `skill_run` |
| 效果复盘 | retro | 7 | 保留/修正/放弃结论 + 下一轮任务 + `skill_run` |

## 三、WBS 看板（每个知识点一轮）

| # | 切片 | 归属 stage | Skill | 验收 |
|---|------|-----------|-------|------|
| 1 | 选题与边界 | topic | learn-assistant | 本轮知识点能落到文件或命令 |
| 2 | 理论输入 | theory | learn-assistant | 能用 3 句话说明何时用/何时不用 |
| 3 | 测试先行 | test-first | learn-assistant | 正例、反例、边界例先于实现 |
| 4 | 工程与技术选型 | project-setup | learn-assistant | 独立工程路径与测试命令可运行 |
| 5 | 工具实现 | tool-build | learn-assistant | 最小工具动作可本地验证 |
| 6 | 接入试跑 | integration-run | learn-assistant | 真实或模拟工作流入口跑通 |
| 7 | 效果复盘 | retro | learn-assistant | 形成下一轮任务 |

```
[ ] 1. 选题与边界
[ ] 2. 理论输入
[ ] 3. 测试先行
[ ] 4. 工程与技术选型
[ ] 5. 工具实现
[ ] 6. 接入试跑
[ ] 7. 效果复盘
```

## 四、变更日志

| 日期 | 变更类型 | 影响阶段 | 重开切片 | 确认人 | 说明 |
|------|----------|----------|----------|--------|------|
| {{date}} | 创建 Epic | — | — | 【】 | 从 learning-agent-dev 母版实例化 |

## 续做

```text
/resume plan=Plans/Epic/{{date}}-学习-{{title}}.md 进度=【派生阶段 / WBS 片号】
```

