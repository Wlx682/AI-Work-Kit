---
name: creative-capture-assistant
description: >-
  运行长期“创意捕捉周循环”：跨领域采集信号、用深层问题过滤、随机连接洞察卡、合成副业或产品创意，并通过最小现实实验筛选。触发词：创意捕捉、创意工作流、信息输入少、新鲜感匮乏、跨领域灵感、副业创意、创意洞察、每周创意合成、随机链接、/creative-capture。
---

# 创意捕捉助手

Vault：AI-Work-Kit。蓝图：`.workflows/blueprints/creative-capture.json`。模板：`Templates/创意捕捉周循环模板.md`。

## 核心约束

- 目标是制造可验证的意外链接，不是扩大收藏量。
- 每周只维护一份共享 plan；五个阶段都写回该文件。
- 把文章主张、个人观察和 AI 推断分开标记；来源必须带链接与日期。
- 当前信息可能变化时，使用可用 Web 搜索/浏览能力核验，优先一手来源。无法核实时写“待核验”，不伪造。
- 发布内容、联系外部人员、收费、购买工具或创建外部服务前，必须获得用户明确授权。
- 写入 `Contexts/` 前必须让用户确认；`archive_decision: 待确认` 时不得结束本轮。

## 启动或恢复

新一周：

```bash
python3 scripts/workflow-install.py check --workflow creative-capture
python3 scripts/workflow-plan-init.py --workflow creative-capture --title "<YYYY-Www 或本周主题>"
python3 scripts/workflow-status.py --workflow creative-capture --project "<同一标题>"
```

已有 plan：

1. 读取 plan frontmatter 和现有表格。
2. 运行 `bash scripts/workflow-gate.sh --workflow creative-capture --project "<task_title>" --json`。
3. 只执行 `current_state` 对应阶段，不提前替用户发布或归档。
4. 完成阶段后追加带 `workflow_stage` 的 `skill_run`，再跑门禁。

## 阶段协议

### radar：跨域信号雷达

- 从科技战略、人文哲思、心智模型、一人企业、产品前沿、跨职业“活人”观察和随机行业漫步中采集。
- 原始候选最多 30 条；保留至少 12 条完整 `S-*` 信号。
- 合格配额：至少 4 个领域、2 条同温层外信号、1 条随机漫步。
- 每条写核心主张、意外关联、来源、观察日期。只写“新”但没有机制或问题价值的内容要淘汰。

### insight：问题化过滤

- 对保留信号提炼“核心主张 → 底层思维模型 → 反常跨域关联 → 反证条件”。
- 生成至少 5 张 `I-*` 洞察卡和 3 张 `Q-*` 深层问题卡。
- 问题卡描述持续的人性或系统问题，不使用“AI、教育、创业”这类主题标签代替问题。
- 明确区分来源证据和推断；证据弱时降低结论强度。

### synthesis：随机链接合成

- 从合格洞察卡随机抽 3 张，不因“不搭”而重抽；再加入一个亲眼观察或当事人表达的现实痛点。
- 使用模板中的 20 个问题，生成恰好 3 个可盈利创意 `C-*`。
- 每个创意包含付费客群、产品/服务形态、付费理由和七日测试。
- 按痛点强度、付费者清晰度、个人能力匹配、七日可测性、可复用杠杆各 1–5 分。
- 将最高价值候选写入 `selected_idea`，并产出约 200 字概念白皮书。

### reality-test：最小现实测试

- 为选中创意定义一个可证伪假设、对象、渠道、动作、时限和停止条件。
- 优先无代码测试：定向访谈、概念白皮书、预约表单、手工服务或极简落地页。
- 外部动作先交用户确认；没有真实触达就不能伪造 `EV-*` 证据。
- 至少记录 1 个 `E-*` 实验和 1 条 `EV-*` 行为证据。
- 点赞是弱证据；主动对话、预约、留资、付费或转介绍是较强证据。
- 将 `experiment_result` 写为“继续验证 / 转向 / 停止”。

### retro：周复盘与播种

- 复盘最意外链接、最强证据、被证伪假设、应停止的输入和下周唯一主问题。
- 生成至少 3 个 `N-*` 下轮种子，设置 `cycle_decision`。
- 列出建议归档项并请求用户决定。确认写入 Contexts 后才执行归档，并设置 `archive_decision: 已归档`；用户明确不要沉淀时设置 `不沉淀（用户确认）`。
- 门禁通过后按 Kit 核心原则删除已完成的临时 plan；若有下轮，使用新周期标题重新初始化。

## 阶段门禁

```bash
python3 scripts/validate-creative-capture.py --stage <radar|insight|synthesis|reality-test|retro> <plan>
bash scripts/workflow-gate.sh --workflow creative-capture --project "<task_title>" --json
```

禁止用手填计数器冒充产物；校验器读取实际 `S/I/Q/C/E/EV/N` 表格行。

## 反馈回路

每个阶段完成后追加一块：

```yaml
skill_run:
  skill: creative-capture-assistant
  workflow_stage: <当前阶段>
  plan: Plans/创意捕捉/<文件>.md
  date: <YYYY-MM-DD>
  contexts_used:
    - path: Contexts/决策/Skill反馈协议.md
      utility: high
      reason: "按阶段留下可校验反馈，使长期周循环能复盘和进化。"
  contexts_missing: []
  contexts_stale: []
```

阶段结束输出：

```text
📌 当前阶段：[阶段] | 下一个阶段：[Skill] | 如需中断：/resume plan=Plans/创意捕捉/xxx.md
```
