---
tags: [Epic, 学习工作流, 模板]
type: plan
category: Epic
status: 草稿
date: {{date}}
epic_id: learning-{{title-kebab}}
workflow: learning-loop
lifecycle_state: topic-intake
p0_open: 0
plans:
  topic-intake: null
  material-prepare: null
  study: null
  design: null
  code: null
  verify: null
  retro: null
  record: null
relations:
  depends_on:
    - Templates/模板约定.md
    - Templates/学习循环模板.md
  dependents: []
  supersedes: []
  superseded_by: []
  conflicts: []
---

# 学习 Epic：{{title}}（工作流：learning-loop）

**创建日期**：{{date}}  
**存放路径**：`Plans/Epic/{{date}}-{{title}}.md`  
**状态**：草稿 | 进行中 | 评审中 | 已采纳 | 搁置  
**workflow**：`learning-loop`

> 本 Epic 是学习旅程的聚合根：记录学习目标、当前循环、历史循环索引、知识图谱来源与整体实践地图。
> 阶段推进由 `.workflows/blueprints/learning-loop.json` + `scripts/workflow-gate.sh` 判定；`plans.*` 只指向当前活动循环，历史学习记录以「循环索引」和「知识图谱来源索引」为准。

---

## 一、学习目标

| 项 | 内容 |
|----|------|
| 学习主题 | {{title}} |
| 为什么学 | 【】 |
| 最终能做什么 | 【】 |
| 明确不学 | 【】 |
| 结束条件 | 用户明确确认整个学习旅程结束 |

---

## 二、子 Plan 索引

| 阶段 | stage key | 路径 | status |
|------|-----------|------|--------|
| 学习主题确认 | topic-intake | — | ⬜ |
| AI 准备核心概念 | material-prepare | — | ⬜ |
| 用户理解概念 + 答疑 | study | — | ⬜ |
| 设计决策 | design | — | ⬜ |
| 编码实现 | code | — | ⬜ |
| 验证：概念 + 代码 + 设计 | verify | — | ⬜ |
| 学习复盘 | retro | — | ⬜ |
| 学习记录与知识图谱增量 | record | — | ⬜ |

> 说明：`plans.*` 和上表只表示当前活动循环入口，会随着下一轮学习切换；历史学习记录必须保留在「循环索引」和「知识图谱来源索引」，不能只依赖 `plans.*`。

---

## 三、循环索引（历史不可覆盖）

| 轮次 | 学习地图节点 | 状态 | 本轮主题 | 子 Plan 链路 | 学习记录 | 图谱增量 |
|------|--------------|------|----------|--------------|----------|----------|
| 01 | L0 【】 | ⬜ | 【】 | topic-intake: —<br>material-prepare: —<br>study: —<br>design: —<br>code: —<br>verify: —<br>retro: —<br>record: — | — | 【】 |

---

## 四、WBS 看板（学习循环 1–8）

| # | 切片 | 归属 stage | Skill | 验收 |
|---|------|------------|-------|------|
| 1 | 确认学习主题与完成门槛 | topic-intake | workflow-router | 明确主题、范围和本轮完成门槛 |
| 2 | AI 准备核心概念与最小概念树 | material-prepare | material-prep-assistant | 资料可直接学习，概念树可解释 |
| 3 | 用户理解概念与答疑 | study | material-prep-assistant | 用户完成学习并提出/解决关键问题 |
| 4a | 设计决策 | design | feature-dev-assistant | 用户做出架构/方案选择并说明理由 |
| 4b | 编码实现 | code | feature-dev-assistant | 产生可运行的代码产物，用户理解每行代码 |
| 5 | 验证：概念 + 代码 + 设计 | verify | test-generator | 验证清单有结论，问题可追踪 |
| 6 | 学习复盘 | retro | report-assistant | 形成已掌握/未掌握/下一步 |
| 7 | 学习记录与知识图谱增量 | record | material-prep-assistant | 学习记录和知识图谱摘要已更新，用户确认是否进入下一轮 |

```
[ ] 1. 确认学习主题与完成门槛
[ ] 2. AI 准备核心概念与最小概念树
[ ] 3. 用户理解概念与答疑
[ ] 4a. 设计决策
[ ] 4b. 编码实现
[ ] 5. 验证：概念 + 代码 + 设计
[ ] 6. 学习复盘
[ ] 7. 学习记录与知识图谱增量
```

---

## 五、学习地图

| 层级 | 主题 | 状态 | 关联循环 plan |
|------|------|------|---------------|
| L0 | 【】 | ⬜ | — |

---

## 六、知识图谱来源索引

| 来源记录 | 覆盖节点 | 状态 | 知识地图用途 |
|----------|----------|------|--------------|
| — | L0 【】 | ⬜ | 【】 |

---

## 七、知识图谱（滚动摘要）

```mermaid
graph TD
  A[{{title}}] --> B[待补充]
```

| 概念 | 我自己的解释 | 关联实践 | 掌握度 |
|------|--------------|----------|--------|
| 【】 | 【】 | 【】 | 生疏 |

---

## 八、整体实践地图

| 实践项目 | 覆盖能力 | 文件/仓库 | 当前状态 |
|----------|----------|-----------|----------|
| 【】 | 【】 | 【】 | ⬜ |

---

## 九、阶段性总结

| 日期 | 我已经学会 | 仍然卡住 | 下一步 |
|------|------------|----------|--------|
| {{date}} | 【】 | 【】 | 【】 |

---

## 十、用户确认

- [ ] 继续下一轮学习
- [ ] 生成阶段总结
- [ ] 生成知识图谱
- [ ] 用户确认整个学习旅程结束

---

## 续做

```text
/resume plan=Plans/Epic/{{date}}-{{title}}.md 进度=【当前循环 / 当前阶段】
```
