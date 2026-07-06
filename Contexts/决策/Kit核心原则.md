---
tags: [决策, 原则, 工作流]
date: 2026-06-20
updated: 2026-07-06
key_points:
  - 少而精原则：工作流文档只保留能指导执行和判断的内容
  - 真理源原则：Plans 承载执行事实，Contexts 承载长期决策，Templates 承载复用骨架
  - 生命周期原则：Plans 做完即归档或删除，不保留任务残留
  - 测试先行原则：先定义验收/失败样例，再实现或接入
  - Gate 原则：跨阶段和跨 Epic 的推进必须由文件事实和门禁显式确认
  - 投影原则：母 Plan 定边界与索引，子 Plan 记录执行事实，投影不能制造事实
  - 反馈闭环原则：skill_run 必须有输出、反馈和归位判断
  - 写回边界原则：Contexts 只写跨任务结论，默认需要用户确认
relations:
  depends_on: []
  dependents:
    - Contexts/决策/AI-Work-Kit工作流总览.md
    - Contexts/决策/AI-Work-Kit架构总览.md
    - Contexts/决策/AI-Work-Kit运行时拓扑.md
    - Contexts/决策/Contexts漂移检测协议.md
    - Contexts/决策/Skill原子契约.md
    - Contexts/决策/Skill反馈协议.md
    - Contexts/决策/关系图谱协议.md
    - Contexts/决策/对话用词习惯.md
    - Contexts/决策/新手引导与最佳实践.md
    - Contexts/决策/母子plan投影规则.md
    - Contexts/决策/测试先行原则.md
    - Templates/模板约定.md
  supersedes:
    - Contexts/决策/资料与代码仓库边界.md
  superseded_by: []
  conflicts: []

---
# Kit 核心原则

## 少而精原则

工作流文档只保留能指导执行和判断的内容，少写索引、口号和过程流水。原则文件讲边界，细则文件讲执行，模板讲填写，三者都不互相替代。

## 真理源原则

`Plans` 是执行事实，`Contexts` 是长期决策上下文，`Templates` 是可复用骨架；三者不可混用。业务代码属于独立仓库，Kit 只保存工作流资产。

## 生命周期原则

`Plans` 只服务当前任务，做完即归档或删除。不得保留“已执行但未清理”的任务残留，也不得把任务流水搬进 `Contexts` 备查。

## 测试先行原则

任何新增或修改，先定义验收样例、失败样例或测试清单，再实现。测试或验收未通过，不允许宣称完成或接入真实工作流。

## Gate 原则

跨阶段、跨 Epic 或影响流程推进的动作，必须经过文件事实和 `workflow-gate` 显式确认。不允许靠口头判断、frontmatter 状态或智能体猜测静默跨越。

## 投影原则

母 Plan 定边界、索引与看板投影，子 Plan 记录执行事实；投影只能反映事实，不能制造事实。子 Plan 不得篡改母本字段，母 Plan 也不得用备注偷藏子 Plan 未完成状态。

## 反馈闭环原则

每次 Skill 执行必须留下可追踪结果：有输出、有反馈、有归位判断。没有反馈闭环的执行视为空跑，不能沉淀为流程经验。

## 写回边界原则

`Plans` 可按任务流程直接写，`Contexts` 只写跨任务仍成立的结论，并默认需要用户确认。智能体可以辅助判断和整理，但不能替人越过确认、门禁或归位边界。
