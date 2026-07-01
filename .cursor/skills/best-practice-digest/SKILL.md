---
name: best-practice-digest
description: >-
  每周提效最佳实践案例。从真实工作出发，量化提效数据（可测量可验证）→套案例报告模板→附 skill_run 反馈接入工作流进化链。
  触发词：提效案例、最佳实践、技术提交分享、产品提效、每周案例、/best-practice、/best-practice-digest。
  不响应：找外部文章→weekly-intel-digest；项目日报→review-assistant。
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

**不响应**：找外部文章→`weekly-intel-digest`；日报复盘→`review-assistant`；需求分析→`requirement-analyst`。

## 必读资产

- [[Contexts/最佳实践/提效度量口径]]、[[Contexts/最佳实践/案例报告模板]]、[[Contexts/最佳实践/进化闭环]]、[[Contexts/最佳实践/已提交案例台账]]

## 执行协议（七步）

```
1. 读口径与模板（度量口径+案例模板+进化闭环）
2. 逐项追问：6 项输入(任务/基线/AI方法/本次耗时/迭代/过程记录)缺则问，禁瞎编
3. 量化提效：基线+本次值(耗时到分钟)+证据链+可复用性等级，缺基线/断链打回
4. 组装人类卷 .md：按「人类卷写作规范」写成技术博客水准文章(问题→方案→踩坑根因→数据→复用)，说明性小标题、专业中性、禁装饰图标、禁娱乐化比喻段子、能画就画，不含 YAML；写完过信息完整性自查清单
5. 生成 AI 卷 .meta.yaml(纯YAML)：skill_run，喂 feedback-aggregate
6. 提交确认语：附一段可直接发群/领导的话
7. 收尾：人类卷 .md + 同名 .meta.yaml 存 Plans/最佳实践/，台账追加，⏸ 交接报告链接
```

**双卷分离**：人类卷(.md)给同事读、无 YAML；AI 卷(.meta.yaml)给脚本读。

## 硬规则

1. 可测量可验证：无基线/断证据链的「提升X%」打回。
2. AI 工作流创新必须体现：点明哪个 Kit 能力把任务从点状变可复用/可度量。
3. 闭环不可省：定稿必附 skill_run + 可否沉淀结论（喂 vault-evolve 进化链）。
4. 报告链接（纳米Work/飞书）Agent 生成不了 → ⏸ 交接人工。
5. 人类卷=技术博客水准：填表腔(字段堆/装饰图标)返工，娱乐化(段子标题/打比方/卖关子)同样返工。踩坑写成根因分析。

## 反馈回路

skill_run 写入**独立 .meta.yaml**（人类卷 .md 不含 YAML），喂 feedback-aggregate → vault-evolve。无 plan 时仍追加 `Contexts/决策/孤立反馈记录.md`。
