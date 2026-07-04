---
name: best-practice-digest
description: >-
  每周提效最佳实践案例。从真实工作出发，量化提效数据（可测量可验证）→ 套案例报告模板 → 附 skill_run 反馈接入工作流进化链。
  触发词：提效案例、最佳实践、技术提交分享、产品提效、每周案例、/best-practice、/best-practice-digest。
  不响应：找外部文章→weekly-intel-digest；项目日报→report-assistant。
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

**不响应**：找外部文章 → `weekly-intel-digest`；项目日报/复盘 → `report-assistant`；纯需求分析 → `requirement-analyst`。

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

## 执行协议（每期八步 · 三卷产物）

```
1. 读口径与模板 → 提效度量口径 + 案例报告模板 + 进化闭环
2. 逐项追问    → 按模板「开工前 6 项输入」补齐，任一项缺失影响可验证性 → 追问，禁止瞎编
3. 量化提效    → 取基线+本次值(耗时精确到分钟)+证据链+可复用性等级，缺基线/断链则打回
4. 组装人类卷  → 写 .md 成品：按「人类卷写作规范」写技术博客(主题→自己的想法→结论→数据→复用)，说明性小标题、专业中性、禁装饰图标、禁娱乐化比喻段子。踩坑写成根因分析
   ├ 必配 ≥1 张 Mermaid 流程图/架构图，标签用大白话，非技术受众看图能懂
   └ 正常写完即干净成品（无需刻意去痕迹）；过自查清单
5. 生成 AI 卷  → 同名 .meta.yaml(纯 YAML)：skill_run(contexts_used/missing/stale)，喂 feedback-aggregate
6. 生成提示词卷 → 同名 .prompt.md：给纳米Work 智能体的生成指令，让它拿人类卷产出可访问的云端 web 链接，并明确要求：**①页面简洁漂亮炫酷（深色科技感+留白+卡片/渐变/微光+适度动效，不喧宾夺主）②零 WIP/零元说明/元指令/零机器块**（把关在此卷）
7. 提交确认语  → 一段发群的确认语（拿到 web 链接后补 URL，不带占位）
8. 收尾        → 三卷存 Plans/最佳实践/YYYY-MM-DD-案例名.{md,meta.yaml,prompt.md}；台账追加一行
```

**三卷分离**：①人类卷 .md 给读者/纳米Work（干净成品 + Mermaid 图，无机器噪音无 WIP）；②AI 卷 .meta.yaml 给脚本（`feedback-aggregate` 优先扫）；③提示词卷 .prompt.md 给纳米Work 智能体生成 web 链接。同源萃取，各司其职。

## 硬规则

1. **可测量可验证**：无基线/断证据链的「提升 X%」一律打回，遵 [[Contexts/最佳实践/提效度量口径]] 反作弊红线。
2. **AI 工作流创新必须体现**：每案例点明「哪个 Kit 能力把任务从点状变成可复用/可度量」，否则不算最佳实践。
3. **闭环不可省**：案例定稿必产出人类卷「进化建议」+ 独立 `.meta.yaml` 的 `skill_run`（喂 feedback-aggregate → vault-evolve）。不做则退化成一次性作业。
4. **网页质量把关在 `.prompt.md`**：人类卷正常写完即成品；`.prompt.md` 明确要求纳米Work 生成的页面 **①简洁漂亮炫酷（深色科技感+留白+卡片/渐变/适度动效）②零 WIP/零元说明/元指令/零机器块**。web 分享链接由纳米Work 依 `.prompt.md` 生成。
5. **必配 Mermaid 图，非技术人看图能懂**：受众混杂，涉及流程/结构/数据流必须有 ≥1 张 Mermaid 图，标签大白话，禁纯文本描述流程。
6. **人类卷是技术博客不是表也不是段子**：填表腔（字段堆砌/装饰图标）要返工；娱乐化（段子标题/打比方/卖关子）同样返工。基准=优秀工程博客。踩坑写成根因分析。
7. **标题短响亮 + 排版碎块化**：主标题 ≤15 字有冲击力、配一行副标题补准确；正文单段≤3行、每小节开头加粗归纳句、多列表、文字/列表/图表交替。大段密集文字即返工。

## 产物位置

- **人类卷（临时）**：`Plans/最佳实践/YYYY-MM-DD-案例名.md`，干净成品，给读者/纳米Work。
- **AI 卷（临时）**：`Plans/最佳实践/YYYY-MM-DD-案例名.meta.yaml`，顶层 `skill_run:`，给 `feedback-aggregate`。
- **提示词卷（临时）**：`Plans/最佳实践/YYYY-MM-DD-案例名.prompt.md`，给纳米Work 生成 web 链接。
- **长期沉淀**：台账追加、`contexts_missing` 沉淀为新 Skill/Contexts 候选 → `Contexts/最佳实践/`。

## 反馈回路

skill_run 写入**独立 `.meta.yaml`**（人类卷 .md 不含 YAML）——一次输出双处使用：对内喂 `feedback-aggregate → vault-evolve` 进化链，满足 CLAUDE.md 规则5。若为无 plan 的一次性输出，仍追加 `Contexts/决策/孤立反馈记录.md`。
