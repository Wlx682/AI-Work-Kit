---
name: best-practice-digest
description: >-
  每周提效最佳实践案例。从真实工作出发，量化提效数据（可测量可验证）→ 套案例报告模板 → 附 skill_run 反馈接入工作流进化链。
  触发词：提效案例、最佳实践、技术提交分享、产品提效、每周案例、/best-practice、/best-practice-digest。
  不响应：找外部文章→weekly-intel-digest；项目日报→review-assistant。
---

# 提效最佳实践助手 Skill

知识库：`/Users/wanglongxiang/git/AI-Work-Kit`
原则：[[Contexts/决策/Kit核心原则]] · 反馈协议：[[Contexts/决策/Skill反馈协议]]

## 定位（与 weekly-intel-digest 的区别）

| | weekly-intel-digest | **本 Skill** |
|--|---------------------|--------------|
| 来源 | 搬运海外一手英文文章 | **自己真实工作**的提效案例 |
| 频道 | 1.Claude Code 使用分享 | **2.技术提交分享 / 3.产品提效最佳实践** |
| 灵魂 | 学最新资讯 | **可测量提效 + 反哺工作流进化** |

## 触发条件

- 「提效案例」「最佳实践」「技术提交分享」「产品提效」「每周案例」
- `/best-practice` / `/best-practice-digest`

**不响应**：找外部文章 → `weekly-intel-digest`；项目日报/复盘 → `review-assistant`；纯需求分析 → `requirement-analyst`。

## 必读资产（Contexts/最佳实践/）

- [[Contexts/最佳实践/提效度量口径]] —— 什么算可验证数据（**先读**，防拍脑袋）
- [[Contexts/最佳实践/案例报告模板]] —— 技术版 / 产品版两套版式
- [[Contexts/最佳实践/进化闭环]] —— **灵魂**：案例如何反哺 Kit 进化
- [[Contexts/最佳实践/已提交案例台账]] —— 去重与进化倒推

## 两类作业分流

| 人群 | 案例来源 | 频道 | 模板 |
|------|----------|------|------|
| 技术 / QA | Loop Engineering、subagents、test-generator 等在真实开发中的案例 | 2.技术提交分享 | 模板 A |
| 产品 / 设计 / 运营 | 需求调研、原型设计、官网设计等真实工作 | 3.产品提效最佳实践 | 模板 B |

## 执行协议（每期七步）

```
1. 读口径与模板 → 提效度量口径 + 案例报告模板 + 进化闭环
2. 逐项追问    → 按模板「开工前 6 项输入」补齐，任一项缺失影响可验证性 → 追问，禁止瞎编
3. 量化提效    → 取基线+本次值(耗时精确到分钟)+证据链+可复用性等级，缺基线/断链则打回
4. 组装人类卷  → 写 .md：按「人类卷写作规范」写成技术博客水准的文章(问题→方案→踩坑根因分析→数据→复用)，说明性小标题、专业中性语气、禁装饰图标、禁娱乐化比喻/段子、能画就画。不含 YAML
   └ 写完过「信息完整性自查清单」，确保数据/证据/进化建议都自然融进叙事（不是列字段）
5. 生成 AI 卷  → 同目录写同名 .meta.yaml(纯 YAML)：skill_run(contexts_used/missing/stale)，喂 feedback-aggregate
6. 提交确认语  → 附一段可直接发群/领导的确认语（简报风格）
7. 收尾        → 人类卷存 Plans/最佳实践/YYYY-MM-DD-案例名.md；AI卷同名 .meta.yaml；台账追加一行；⏸ 交接报告链接
```

**双卷分离**：人类卷(.md)给同事读——讲故事、给结论、无 YAML 噪音；AI 卷(.meta.yaml)给脚本读——`feedback-aggregate` 优先扫 .meta.yaml。两卷同源，一次萃取。

## 硬规则

1. **可测量可验证**：无基线/断证据链的「提升 X%」一律打回，遵 [[Contexts/最佳实践/提效度量口径]] 反作弊红线。
2. **AI 工作流创新必须体现**：每案例点明「哪个 Kit 能力把任务从点状变成可复用/可度量」，否则不算最佳实践。
3. **闭环不可省**：案例定稿必产出人类卷「进化建议」+ 独立 `.meta.yaml` 的 `skill_run`（喂 feedback-aggregate → vault-evolve）。不做则退化成一次性作业。
4. **报告链接人工节点**：创作过程转分享链接（纳米Work/飞书）Agent 生成不了 → 输出 ⏸ 交接。
5. **人类卷是技术博客不是表也不是段子**：填表腔（字段堆砌/装饰图标）要返工；娱乐化（段子标题/打比方/卖关子）同样返工。基准=优秀工程博客：客观、准确、有信息密度。踩坑写成根因分析。

## 产物位置

- **案例报告（临时）**：`Plans/最佳实践/YYYY-MM-DD-案例名.md`，发布后删 plan。
- **长期沉淀**：台账追加、`contexts_missing` 沉淀为新 Skill/Contexts 候选 → `Contexts/最佳实践/`。

## 反馈回路

skill_run 写入**独立 `.meta.yaml`**（人类卷 .md 不含 YAML）——一次输出双处使用：对内喂 `feedback-aggregate → vault-evolve` 进化链，满足 CLAUDE.md 规则5。若为无 plan 的一次性输出，仍追加 `Contexts/决策/孤立反馈记录.md`。
