---
tags: [功能开发, 用户故事, TDD]
type: plan
category: 功能开发
status: 待开发
date: {{date}}
lifecycle_state: story-development
parent: Plans/功能开发/{{date}}-{{title}}.md
story_id: US-001
story_points: 5
sprint_scope: true
tdd_evidence: Plans/功能开发/{{date}}-{{title}}-US-001.tdd.json
implementation_design: Plans/功能开发/{{date}}-{{title}}-US-001.impl.json
relations:
  depends_on:
    - Templates/模板约定.md
    - Templates/客户端功能开发模板.md
  dependents:
    - Templates/客户端功能开发模板.md
  supersedes: []
  superseded_by: []
  conflicts: []

---
# US-001：{{story-title}}

## 用户故事与 AC

作为【角色】，我想要【能力】，以便【价值】。

覆盖：AC1。架构引用：ADR-001。

## 故事内部实现边界

- UI / 交互：【】
- Domain / 状态：【】
- Data / API：【】
- 测试与异常：【】

## 实现落点设计

落点证据：`implementation_design`。必须先通过 `python3 scripts/validate-client-dev.py implementation-design --plan Plans/功能开发/父Plan.md`。

- 代码证据：【读过的既有文件/目录】
- 目标文件：【修改/新建路径、原因、命名依据】
- 模块边界：【所属层级与依赖方向】
- Red 测试位置：【测试文件与命令】

## TDD

1. **Red**：先运行从 AC 转换的测试，保存非零退出码和“仅因尚未实现”的原因。
2. **Green**：最小实现使同一测试通过。
3. **Refactor**：重构后再次运行并保持通过。
4. **Integration smoke**：合并前运行小型跨组件冒烟。

执行证据写入 `tdd_evidence`，由 `scripts/validate-client-dev.py story-development` 校验。

## 故事验收

- [ ] `implementation_design` 已通过校验
- [ ] AC 全部通过
- [ ] Red / Green / Refactor / integration smoke 证据齐全
- [ ] `status: 已完成`

## 续做

```text
/resume plan=Plans/功能开发/{{date}}-{{title}}-US-001.md 进度=从Red测试开始
```
