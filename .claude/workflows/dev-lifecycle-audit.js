export const meta = {
  name: 'dev-lifecycle-audit',
  description: '审计 Plans/Epic/ 各 Epic 声称阶段与子 plan、Story/Scope、门禁、测试证据的一致性',
  whenToUse: '用户要求「开发流程审计」「Epic 审计」「检查全流程进度真实性」「dev-lifecycle-audit」时',
  phases: [
    { title: '机械取证', detail: '运行 dev-lifecycle-audit-collect.sh' },
    { title: '并行维度审计', detail: '五 agent 独立取证 A–E' },
    { title: '汇总报告', detail: '写入 Contexts/决策/ 审计报告' },
  ],
}

const epicFolder = (args && args.epicFolder) || 'Plans/Epic'
const reportFolder = (args && args.reportFolder) || 'Contexts/决策'
const today = (args && args.today) || null

phase('机械取证')

const collect = await bash(`./scripts/dev-lifecycle-audit-collect.sh ${epicFolder}`)
if (!collect || collect.includes('（无 Epic plan）')) {
  return { error: `${epicFolder}/ 下未发现 Epic，审计中止` }
}
log(collect)

phase('并行维度审计')

const DIM_SCHEMA = {
  type: 'object',
  required: ['dimension', 'epic_findings', 'verdict', 'details'],
  properties: {
    dimension: { type: 'string', enum: ['A-Epic元信息', 'B-需求P0', 'C-技术方案', 'D-Story进度', 'E-测试部署'] },
    epic_findings: {
      type: 'array',
      items: {
        type: 'object',
        required: ['epic', 'issue'],
        properties: {
          epic: { type: 'string' },
          issue: { type: 'string' },
          severity: { type: 'string', enum: ['ok', 'warn', 'block'] },
        },
      },
    },
    verdict: { type: 'string', enum: ['一致', '轻微偏差', '严重矛盾'] },
    details: { type: 'string' },
  },
}

const mechanical = collect

const [dimA, dimB, dimC, dimD, dimE] = await parallel([
  () => agent(
    `维度 A：Epic 元信息。根据以下机械取证，检查每个 Epic 是否存在 epic_id、lifecycle_state、子 plan 索引是否与 plans: 块一致。\n\n${mechanical}`,
    { label: 'audit:A-epic', phase: '并行维度审计', schema: DIM_SCHEMA }
  ),
  () => agent(
    `维度 B：需求 P0。检查 requirement plan 是否存在、p0_open 是否为 0、需求 plan status 是否已采纳（声称可开发时）。\n\n${mechanical}`,
    { label: 'audit:B-requirement', phase: '并行维度审计', schema: DIM_SCHEMA }
  ),
  () => agent(
    `维度 C：技术方案。含业务逻辑=是 时，architecture plan 须存在且 status=已采纳；lifecycle 在 development 但无方案 → 严重矛盾。\n\n${mechanical}`,
    { label: 'audit:C-architecture', phase: '并行维度审计', schema: DIM_SCHEMA }
  ),
  () => agent(
    `维度 D：Story 进度。对比 lifecycle_state 与 workflow-gate 派生阶段、.stories.json Scope、Story 子 Plan 与 tdd_evidence；story-development 阶段但 Scope Story 缺 TDD 证据 → block；gate_development 非 OK → block。\n\n${mechanical}`,
    { label: 'audit:D-story', phase: '并行维度审计', schema: DIM_SCHEMA }
  ),
  () => agent(
    `维度 E：测试/部署。lifecycle 为 integration-test/done 或 workflow-gate 已通过 story-development 时，integration-test plan 与 integration_report 应存在；缺子 plan 标 warn/block。\n\n${mechanical}`,
    { label: 'audit:E-test-deploy', phase: '并行维度审计', schema: DIM_SCHEMA }
  ),
])

const dims = [dimA, dimB, dimC, dimD, dimE].filter(Boolean)
if (!dims.length) {
  return { error: '所有维度 agent 失败，审计中止' }
}

phase('汇总报告')

const REPORT_SCHEMA = {
  type: 'object',
  required: ['report_path', 'summary'],
  properties: {
    report_path: { type: 'string' },
    summary: { type: 'string' },
  },
}

const dateInstruction = today
  ? `报告日期为 ${today}。`
  : `先用 Bash 运行 \`date +%F\` 获取今天日期。`

const report = await agent(
  `你是开发流程审计汇总员。以下是五维度独立取证 JSON：\n\n` +
  JSON.stringify(dims, null, 2) +
  `\n\n原始机械取证：\n${mechanical}\n\n${dateInstruction}\n` +
  `写入 ${reportFolder}/<日期>-开发流程审计报告.md。结构：\n` +
  `1. frontmatter tags: [决策, 审计报告, Epic, workflow]\n` +
  `2. 综合结论一段\n` +
  `3. ## 总览 表格：Epic | lifecycle | Story/Scope | 门禁 | 缺子plan | 一致性\n` +
  `4. ## 维度 A–E 摘要\n` +
  `5. ## ⚠️ 不一致项\n` +
  `6. ## 下一步建议（可链 /resume 与 kanban）\n` +
  `返回 report_path 与 summary。`,
  { label: 'synthesize-dev-audit', phase: '汇总报告', schema: REPORT_SCHEMA }
)

return {
  dimensions: dims.length,
  report_path: report ? report.report_path : null,
  summary: report ? report.summary : '报告写入失败',
}
