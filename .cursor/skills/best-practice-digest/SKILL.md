---
name: best-practice-digest
description: >-
  每周提效最佳实践案例。从真实工作出发，量化提效数据（可测量可验证）→套案例报告模板→附 skill_run 反馈接入工作流进化链。
  触发词：提效案例、最佳实践、技术提交分享、产品提效、每周案例、/best-practice、/best-practice-digest。
  不响应：找外部文章→weekly-intel-digest；项目日报→report-assistant。
---

# 提效最佳实践助手

知识库：`/Users/wanglongxiang/git/AI-Work-Kit`
原则：[[Contexts/决策/Kit核心原则]] · 全文：`Skills/best_practice_digest.md`

## 定位

自己**真实工作**的提效案例（区别于 weekly-intel-digest 搬运外部文章）。
频道：技术/QA→「2.技术提交分享」；产品/设计/运营→「3.产品提效最佳实践」。

## 触发条件

- 「提效案例」「最佳实践」「技术提交分享」「产品提效」「每周案例」
- `/best-practice` / `/best-practice-digest`

**不响应**：找外部文章→`weekly-intel-digest`；日报复盘→`report-assistant`；需求分析→`requirement-analyst`。

## 必读资产

- [[Contexts/最佳实践/提效度量口径]]、[[Contexts/最佳实践/案例报告模板]]、[[Contexts/最佳实践/进化闭环]]、[[Contexts/最佳实践/已提交案例台账]]

## 执行协议（八步 · 三卷产物）

```
1. 读口径与模板（度量口径+案例模板+进化闭环）
2. 逐项追问：6 项输入(任务/基线/AI方法/本次耗时/迭代/过程记录)缺则问，禁瞎编
3. 量化提效：基线+本次值(耗时到分钟)+证据链+可复用性等级，缺基线/断链打回
4. 组装人类卷 .md 成品：技术博客(主题→想法→结论→数据→复用)，说明性小标题、专业中性、禁装饰图标、禁段子；必配 ≥1 张 Mermaid 图(大白话标签,非技术看图能懂)；正常写完即干净成品；过自查清单
5. 生成 AI 卷 .meta.yaml(纯YAML)：skill_run，喂 feedback-aggregate
6. 生成炫酷网页 .html：**Agent 直接产同名 `.html` 自渲染成品**(遵 Contexts/规范/炫酷建站规范：深色科技感+内嵌mermaid.js自渲染+适度动效+**关键数字主角化(特大字/独占卡/count-up)**+**流式栅格auto-fit动态适配**,零WIP/零机器块),用本地浏览器过自检(图全SVG/console0报错/正文全可见/**375·768·1440三宽度无横溢出**)
7. 提交确认语：拿到纳米Work 托管短链后补 URL，不带占位
8. 收尾：三卷存 Plans/最佳实践/YYYY-MM-DD-案例名.{md,html,meta.yaml}，台账追加
```

**三卷分离**：①人类卷 .md 给读者(干净成品+Mermaid图)；②AI 卷 .meta.yaml 给脚本；③**网页卷 .html 由 Agent 直接产**(过浏览器自检)，交纳米Work 只上传CDN出短链。

## 硬规则

1. 可测量可验证：无基线/断证据链的「提升X%」打回。
2. AI 工作流创新必须体现：点明哪个 Kit 能力把任务从点状变可复用/可度量。
3. 闭环不可省：定稿必附 .meta.yaml 的 skill_run（喂 vault-evolve 进化链）。
4. 网页由 Agent 产 `.html`·纳米Work 只托管：人类卷写完即成品；Agent 依 Contexts/规范/炫酷建站规范 产自渲染 `.html`(①炫酷深色科技感+适度动效 ②内嵌mermaid.js自渲染 ③零WIP/零机器块)并过浏览器自检；纳米Work 传CDN出短链不改内容。
5. 必配 Mermaid 图，非技术人看图能懂：受众混杂，流程/结构/数据流必须有 ≥1 张图，标签大白话，禁纯文本描述流程。
6. 人类卷=技术博客：填表腔(字段堆/装饰图标)返工，娱乐化(段子/打比方/卖关子)同样返工。踩坑写成根因分析。
7. 标题短响亮+排版碎块化：主标题≤15字有冲击力+副标题补准确；正文单段≤3行、每小节开头加粗归纳句、多列表、文字/列表/图表交替；大段密集文字返工。

## 反馈回路

skill_run 写入**独立 .meta.yaml**（人类卷 .md 不含 YAML），喂 feedback-aggregate → vault-evolve。无 plan 时仍追加 `Contexts/决策/孤立反馈记录.md`。
