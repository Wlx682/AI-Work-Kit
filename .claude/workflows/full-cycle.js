export const meta = {
  name: 'full-cycle',
  description: '全流程开发编排：Epic 优先 → 机械门禁 → 执行当前 Skill。上一阶段 plan 或 WBS 未满足退出条件则不进入下一阶段。',
  whenToUse: '用户说「开始做这个项目」「全流程开发」「full-cycle」「project-manager 帮我开发」时',
  phases: [
    { title: '启动看板', detail: 'full-cycle-boot.sh 拉起 kanban' },
    { title: '机械门禁', detail: 'full-cycle-gate.sh 读取 Epic + plan-gate-check' },
    { title: '定位项目', detail: '结合门禁结果确认当前阶段' },
    { title: '执行当前 Skill', detail: '调用对应 assistant 产出 plan' },
    { title: '汇报与下一步', detail: '上下文汇报 + 推荐下一阶段' },
  ],
}

// args: { projectName, requirementPlan, epic, platform: '客户端'|'服务端' }
const projectName = (args && args.projectName) || null
const requirementPlan = (args && args.requirementPlan) || null
const epicPath = (args && args.epic) || null
const platform = (args && args.platform) || '客户端'

const STATES = [
  { key: 'requirement', folder: 'Plans/需求分析', skill: 'requirement-analyst', label: '需求分析' },
  { key: 'architecture', folder: platform === '服务端' ? 'Plans/服务端技术方案' : 'Plans/客户端技术方案', skill: 'architecture-design-assistant', label: '架构设计' },
  { key: 'development', folder: 'Plans/功能开发', skill: 'task-splitter / feature-dev-assistant', label: '功能开发' },
  { key: 'test', folder: 'Plans/自动化测试', skill: 'test-generator', label: '自动化测试' },
  { key: 'deploy', folder: 'Plans/部署', skill: 'deployment-assistant', label: '部署' },
]

phase('启动看板')

const bootArgs = epicPath ? `--epic ${epicPath}` : ''
await bash(`./scripts/full-cycle-boot.sh ${bootArgs} 2>/dev/null || true`)

phase('机械门禁')

const gateArgs = epicPath
  ? `--epic ${epicPath}`
  : projectName
    ? `--project ${projectName}`
    : ''
const gateResult = await bash(`./scripts/full-cycle-gate.sh ${gateArgs}`)
if (!gateResult) {
  return { error: 'full-cycle-gate.sh 执行失败' }
}
log(gateResult)

const gateJson = await bash(`./scripts/full-cycle-gate.sh ${gateArgs} --json`)
let gate = null
try {
  gate = gateJson ? JSON.parse(gateJson) : null
} catch {
  gate = null
}

phase('定位项目')

const DISCOVER_SCHEMA = {
  type: 'object',
  required: ['current_state', 'plans_found', 'blockers', 'recommended_skill', 'report'],
  properties: {
    current_state: { type: 'string', enum: ['requirement', 'architecture', 'development', 'test', 'deploy', 'done'] },
    plans_found: {
      type: 'object',
      properties: {
        requirement: { type: 'string' },
        architecture: { type: 'string' },
        development: { type: 'string' },
        test: { type: 'string' },
        deploy: { type: 'string' },
      },
    },
    blockers: { type: 'array', items: { type: 'string' } },
    recommended_skill: { type: 'string' },
    next_state: { type: 'string' },
    report: { type: 'string', description: '📌 上下文汇报，中文' },
  },
}

const discover = await agent(
  `你是 AI-Work-Kit 全流程编排器。项目名：${projectName || '（未指定，请从用户消息推断）'}。` +
  (epicPath ? `指定 Epic：${epicPath}。` : '') +
  (requirementPlan ? `指定需求 plan：${requirementPlan}。` : '') +
  `\n\n**机械门禁结果（优先采用，勿与 full-cycle.json 冲突）：**\n${gateResult}\n` +
  (gate ? `\n解析 JSON：${JSON.stringify(gate)}` : '') +
  `\n\n状态机（Plans/Epic/ 为入口，子 plan 索引见 Epic frontmatter plans:）：\n` +
  STATES.map(s => `- ${s.label}：${s.folder}/`).join('\n') +
  `\n\n规则（与 scripts/full-cycle-gate.sh 一致）：\n` +
  `1. 无 Epic → requirement，recommended_skill=full-cycle-assistant\n` +
  `2. 需求未采纳或 P0>0 → requirement\n` +
  `3. 含业务逻辑=是 且方案未采纳 → architecture\n` +
  `4. plan-gate-check 失败或 WBS 1–10 未完成 → development\n` +
  `5. 无测试 plan 或 WBS 11 未完成 → test\n` +
  `6. 无部署 plan 或 WBS 13–14 未完成 → deploy\n` +
  `7. 全部通过 → done\n` +
  `\n若机械门禁已给出 current_state / blockers，以之为准，仅补充 plans_found 路径细节。\n` +
  `输出 report：📌 当前阶段：[X] | 下一个阶段：[Y] | 看板：http://127.0.0.1:7777/ | 如需中断：/resume plan=...\n` +
  `blockers 列出具体缺失项（中文）。`,
  { label: 'full-cycle-discover', phase: '定位项目', schema: DISCOVER_SCHEMA }
)

const resolved = gate && gate.current_state
  ? {
      current_state: gate.current_state,
      next_state: gate.next_state,
      recommended_skill: gate.recommended_skill,
      blockers: gate.blockers || [],
      plans_found: Object.fromEntries(
        (gate.plans_found || [])
          .map(s => s.split(':'))
          .filter(p => p.length >= 2)
          .map(p => [p[0], p.slice(1).join(':')])
      ),
      report: gateResult.match(/report: (.+)/)?.[1] || discover?.report,
    }
  : discover

if (!resolved) {
  return { error: '阶段发现失败' }
}

log(resolved.report || discover?.report)

if (resolved.current_state === 'done') {
  return { status: 'done', gate: gateResult, report: resolved.report }
}

phase('执行当前 Skill')

const EXEC_SCHEMA = {
  type: 'object',
  required: ['skill_invoked', 'output_path', 'report'],
  properties: {
    skill_invoked: { type: 'string' },
    output_path: { type: 'string' },
    report: { type: 'string' },
  },
}

const stateInfo = STATES.find(s => s.key === resolved.current_state)
const executed = await agent(
  `执行全流程当前阶段「${stateInfo?.label || resolved.current_state}」。\n` +
  `调用 Skill：${resolved.recommended_skill || discover?.recommended_skill}（读 Skills/ 或 .cursor/skills/ 对应说明）。\n` +
  `Epic：${gate?.epic || epicPath || '（见门禁结果）'}。\n` +
  `已发现 plan：${JSON.stringify(resolved.plans_found || discover?.plans_found)}。\n` +
  `阻塞：${(resolved.blockers || discover?.blockers || []).join('；') || '无'}。\n` +
  `门禁：${gate?.gate_development || '见 full-cycle-gate 输出'}。\n` +
  `\n硬规则：\n` +
  `- 开发阶段写代码前须 plan-gate-check.sh 通过\n` +
  `- test-generator / deployment-assistant 产出后须回写 Epic plans.test / plans.deploy\n` +
  `- 若阻塞仅因「未写 plan」→ 按模板创建 plan 到对应 Plans/ 目录\n` +
  `- 若阻塞为 P0/未采纳/WBS → 只输出待办，不进入下一阶段\n` +
  `\n完成后 output report：📌 当前阶段 | 产出路径 | 看板 | 下一阶段 | /resume 命令。`,
  { label: `full-cycle-exec:${resolved.current_state}`, phase: '执行当前 Skill', schema: EXEC_SCHEMA }
)

phase('汇报与下一步')

await bash(`./scripts/kanban-sync.sh --boot ${epicPath ? `--epic ${epicPath}` : ''} 2>/dev/null || true`)

return {
  current_state: resolved.current_state,
  next_state: resolved.next_state || discover?.next_state,
  skill: resolved.recommended_skill || discover?.recommended_skill,
  gate: gateResult,
  execution: executed,
  report: executed?.report || resolved.report,
  spec: '.claude/workflows/full-cycle.json',
}
