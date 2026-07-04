---
tags: [决策, Skill, 工作流, 测试]
date: 2026-07-03
status: 草稿
relations:
  depends_on:
    - Contexts/决策/Kit核心原则.md
    - Contexts/决策/AI-Work-Kit工作流总览.md
    - Contexts/决策/Skill反馈协议.md
    - Templates/模板约定.md
  dependents: []
  supersedes: []
  superseded_by: []
  conflicts: []

---
# Skill 原子契约

> 目标：让 Skill 像积木一样被 workflow 蓝图组合，同时能被单独 smoke test。
> 本文只定义接口形状；存放原则、反馈协议、工作流引擎仍以相关决策文件为准。

---

## 一、原子 Skill 的定义

一个原子 Skill 只交付一个清晰产物，并明确自己不处理的边界。

| 维度 | 要求 |
|------|------|
| 单一职责 | 一个 Skill 对应一个主要产物，如需求分析、Figma 还原、任务拆分、Review |
| 输入显式 | 必需输入必须列出，缺失时要阻塞或降级说明 |
| 输出可验 | 产物路径、章节、表格、状态、门禁都要可检查 |
| 边界清楚 | 发现越界场景时转给正确 Skill 或 workflow |
| 可测试 | 至少有一个最小 fixture 能跑结构检查 |

---

## 二、契约字段

每个可编排 Skill 至少声明以下字段：

| 字段 | 必填 | 说明 |
|------|------|------|
| `name` | 是 | dash-form 名称，与路由表一致 |
| `scope` | 是 | 只做什么，不做什么 |
| `inputs` | 是 | 必需输入，如 PRD、Figma 链接、错误日志、技术方案 |
| `outputs` | 是 | 产物类型和路径，如 plan、审查结论、测试计划 |
| `gates` | 是 | 完成门槛，如 checklist、状态、脚本校验 |
| `contexts` | 是 | 默认要读或按需读取的 Contexts |
| `feedback` | 是 | 是否写 `skill_run`，写到 plan 还是孤立反馈 |
| `smoke_tests` | 是 | fixture 路径、断言项、预期失败样例 |

---

## 三、契约模板

```yaml
skill_contract:
  name: example-skill
  scope:
    does:
      - "交付什么"
    does_not:
      - "不处理什么；越界时转给谁"
  inputs:
    required:
      - name: "输入名"
        source: "用户粘贴 / plan / Contexts / 代码仓库"
    optional: []
  outputs:
    artifacts:
      - path_pattern: "Plans/分类/YYYY-MM-DD-标题.md"
        required_sections: []
    response:
      format: "最终回复必须包含的关键信息"
  gates:
    required:
      - "完成门槛"
    scripts: []
  contexts:
    default: []
    optional: []
  feedback:
    skill_run: required | optional | not-needed
    location: "plan-end | orphan | meta-yaml"
  smoke_tests:
    fixtures:
      - "tests/fixtures/skills/example/basic.input.md"
    assertions:
      - "结构断言"
```

---

## 四、一期 Skill 示例

### `figma-ui`

| 字段 | 内容 |
|------|------|
| 输入 | Figma 链接或截图、目标页面、平台、允许偏差 |
| 输出 | UI 实现说明、截图、`Figma还原自检表` 或同 plan 自检节 |
| 门禁 | 自评分 >= 9；差异表完整；未达标时不得说完成 |
| 越界 | 出现接口联调、埋点、状态机、跨模块业务逻辑时升级到功能开发流程 |
| fixture | `tests/fixtures/skills/figma-ui/basic-card.input.md` |

### `task-splitter`

| 字段 | 内容 |
|------|------|
| 输入 | 已采纳技术方案、Epic 或明确目标范围 |
| 输出 | 5-10 个原子任务，必要时写主 plan 与子任务 plan |
| 门禁 | 每个任务有输入、输出、验收、依赖；不混职责 |
| 越界 | WBS 方案不明确时请求用户确认，不擅自推荐 A/B/C |
| fixture | `tests/fixtures/skills/task-splitter/checkout-tech-plan.input.md` |

### `code-review`

| 字段 | 内容 |
|------|------|
| 输入 | diff、PR、分支、审查范围 |
| 输出 | Findings-first review 结论 |
| 门禁 | 问题按严重级排序；引用文件行号；无问题时说明测试缺口 |
| 越界 | 需要实现修复时转功能开发或 bugfix 流程 |
| fixture | `tests/fixtures/skills/code-review/risky-diff.input.md` |

---

## 五、Smoke Test 分层

| 层级 | 目的 | 一期做法 |
|------|------|----------|
| Fixture 完整性 | 输入和期望断言没有缺项 | `scripts/skill-smoke-test.py <skill> <input>` |
| 产物结构检查 | 检查真实输出是否包含关键结构 | `scripts/skill-smoke-test.py <skill> <input> --output <file>` |
| 端到端质量评估 | 判断内容是否真的好用 | 后续人工抽样或评审，不在一期强做 |

一期只做前两层，避免为了测试框架本身引入过高成本。

---

## 六、和 Workflow 的关系

Workflow 不复述 Skill 规则，只引用 Skill 名称、产物目录和退出条件。

| 层 | 职责 |
|----|------|
| Skill Contract | 说明单块积木的输入、输出、门禁 |
| Workflow Blueprint | 说明积木排列顺序和阶段推进 |
| Gate Script | 机械检查子 plan、状态、反馈、追踪关系 |
| Plan | 承载一次真实任务的上下文和结果 |

新增轻流程时，优先复用已有 Skill；只有当现有 Skill 边界长期不合适时再新增 Skill。

---

## 七、反馈策略

建议分两档：

| 场景 | 反馈要求 |
|------|----------|
| workflow 阶段或写入 plan 的任务 | 必须写 `skill_run` |
| 纯讨论、脑暴、临时答疑 | 不自动写孤立反馈；形成可复用规则、脚本或 plan 时再写 |

自 2026-07-03 起，`plan-gate-check.sh` 对所有 plan 全量强制 `skill_run`。纯讨论不自动写孤立反馈；一旦形成可复用规则、脚本或 plan，就按反馈协议记录。

---

## 八、相关

- [[Contexts/决策/Kit核心原则]]
- [[Contexts/决策/AI-Work-Kit工作流总览]]
- [[Contexts/决策/Skill反馈协议]]
- [[Templates/模板约定]]
