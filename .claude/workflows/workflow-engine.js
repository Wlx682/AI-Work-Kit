export const meta = {
  name: 'workflow-engine',
  description: '通用工作流编排引擎：读蓝图 manifest → 机械门禁（只看子 Plan 事实）→ 执行当前 Skill。蓝图决定阶段链，Epic 仅作数据上下文，不驱动流程。',
  whenToUse: '用户说「开始做这个项目」「全流程开发」「电脑管理」「帮我清理电脑」，或任意蓝图触发词时',
  phases: [
    { title: '选蓝图与启动', detail: '参数/Epic字段/自然语言 选蓝图 + boot 看板' },
    { title: '机械门禁定位', detail: 'workflow-gate.sh 逐 stage 查子 Plan 事实' },
    { title: '执行当前 Skill', detail: '调用蓝图 stage 对应 Skill 产出 plan' },
    { title: '汇报与下一步', detail: '上下文汇报 + 推荐下一阶段（游标不写回 Epic）' },
  ],
}

// args 可能是结构化对象 { workflow, projectName, requirementPlan, epic, platform } 或一段原始用户文本。
// 三层架构（见 Contexts/决策/AI-Work-Kit工作流总览）：
//   积木=子 Skill / 状态机=本引擎+蓝图 / 数据上下文=Epic（只存不驱动）。
// 门禁只看子 Plan 文件系统事实，绝不读 Epic lifecycle_state。
const rawArgs = typeof args === 'string' ? args : ''
const objArgs = (args && typeof args === 'object') ? args : {}

const explicitWorkflow = objArgs.workflow || null
const projectName = objArgs.projectName || null
const requirementPlan = objArgs.requirementPlan || null
const epicPath = objArgs.epic || null
const userContext = rawArgs || objArgs.context || ''

phase('选蓝图与启动')

// ---------- 步骤 0：解析可用蓝图清单 + 选定蓝图 ----------
const RESOLVE_SCHEMA = {
  type: 'object',
  required: ['workflow', 'uses_epic', 'boot_ok', 'gate_text'],
  properties: {
    workflow: { type: 'string', description: '最终选定的蓝图 name（如 client-dev / computer-mgmt）' },
    uses_epic: { type: 'boolean' },
    workflow_reason: { type: 'string', description: '选定该蓝图的依据：参数 / Epic字段 / 自然语言 / 默认' },
    boot_ok: { type: 'boolean' },
    kanban_url: { type: 'string' },
    gate_text: { type: 'string', description: 'workflow-gate.sh 人类可读 stdout 原文' },
    gate_json: { type: 'string', description: 'workflow-gate.sh --json stdout 原文（未解析）' },
  },
}

const gateArg = epicPath
  ? `--epic ${epicPath}`
  : projectName
    ? `--project ${projectName}`
    : ''

const resolveSetup = await agent(
  `你是通用工作流引擎的「选蓝图与启动」步骤。工作目录为仓库根。\n` +
  `\n## 1. 列出可用蓝图\n` +
  `用 Bash 运行 \`ls .workflows/blueprints/*.json\`，读每个蓝图的 name / label / usesEpic / triggerHints（可 \`cat\` 各 json 的这几个字段）。\n` +
  `\n## 2. 选定蓝图（优先级，重要）\n` +
  `a) 若用户给了 workflow 参数「${explicitWorkflow || '（无）'}」→ 直接用。\n` +
  `b) 否则若指定了 Epic「${epicPath || '（无）'}」→ 读该 Epic frontmatter 的 workflow 字段；有则用。\n` +
  `c) 否则按**自然语言意图**匹配 triggerHints（用户原文很重要）：\n` +
  (userContext ? `   用户原文：「${userContext}」\n` : `   用户原文：（无，从对话上下文推断）\n`) +
  `   把原文与各蓝图 triggerHints 比对，命中最贴切的一个。\n` +
  `d) 都无法确定 → 默认 client-dev，并在 workflow_reason 注明「默认，建议向用户确认」。\n` +
  `\n## 3. 启动看板 + 机械门禁\n` +
  `选定蓝图后（记其 name 为 WF，usesEpic 为 UE）依次运行：\n` +
  `1. \`./scripts/workflow-board-boot.sh ${epicPath ? `--epic ${epicPath} ` : ''}2>&1 || true\`（UE=false 的蓝图看板可选；取 stdout 中 KANBAN_URL= 后地址放 kanban_url）\n` +
  `2. \`./scripts/workflow-gate.sh --workflow <WF> ${gateArg}\`（人类可读，放 gate_text）\n` +
  `3. \`./scripts/workflow-gate.sh --workflow <WF> ${gateArg} --json\`（放 gate_json，原样不解析）\n` +
  `\n返回：workflow=选定蓝图 name，uses_epic=其 usesEpic，workflow_reason=依据，boot_ok=第1步是否成功，其余同名字段。不要改写脚本输出。`,
  { label: 'resolve-workflow+setup', phase: '选蓝图与启动', schema: RESOLVE_SCHEMA }
)

if (!resolveSetup || !resolveSetup.gate_text) {
  return { error: 'workflow-gate.sh 执行失败或未选出蓝图', resolveSetup }
}

const workflow = resolveSetup.workflow
const usesEpic = resolveSetup.uses_epic
const gateResult = resolveSetup.gate_text
const kanbanUrl = resolveSetup.kanban_url || 'http://127.0.0.1:7777/'
log(`蓝图：${workflow}（${resolveSetup.workflow_reason || ''}）`)
if (usesEpic) log(`看板：${kanbanUrl}（若未自动弹出请手动打开）`)
log(gateResult)

let gate = null
try {
  gate = resolveSetup.gate_json ? JSON.parse(resolveSetup.gate_json) : null
} catch {
  gate = null
}

phase('机械门禁定位')

// 门禁已给出 current_state / next_state / recommended_skill / blockers / plans_found（全部基于文件系统事实）。
// 引擎直接采用门禁结论，不做二次状态推断，也不读 Epic lifecycle_state。
if (!gate || !gate.current_state) {
  return { error: '机械门禁未返回 current_state', gate: gateResult }
}

const report = gateResult.match(/report: (.+)/)?.[1] || ''
log(report)

if (gate.current_state === 'done') {
  return { status: 'done', workflow, gate: gateResult, report }
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

const plansFound = (gate.plans_found || [])
  .map(s => s.split(':'))
  .filter(p => p.length >= 2)
  .reduce((acc, p) => { acc[p[0]] = p.slice(1).join(':'); return acc }, {})

const executed = await agent(
  `执行工作流「${workflow}」当前阶段「${gate.current_state}」。\n` +
  `调用 Skill：${gate.recommended_skill}（读 Skills/ 或 .cursor/skills/ 对应说明；蓝图 .workflows/blueprints/${workflow}.json 该 stage 的 skills 数组为候选）。\n` +
  (usesEpic ? `Epic（仅数据上下文，不写 lifecycle_state）：${gate.epic || epicPath || '（见门禁结果）'}。\n` : `本工作流无 Epic，plan 直接放蓝图 stage 的 planFolder。\n`) +
  (userContext ? `用户原始需求/上下文：${userContext}\n` : '') +
  (requirementPlan ? `指定需求 plan：${requirementPlan}。\n` : '') +
  `已发现子 plan：${JSON.stringify(plansFound)}。\n` +
  `阻塞：${(gate.blockers || []).join('；') || '无'}。\n` +
  `\n硬规则：\n` +
  `- 阶段退出条件由 workflow-gate.sh 依「子 Plan 文件系统事实」判定（childPlanExists/status/plan-gate-check/WBS 勾选）；**不要**改 Epic frontmatter 的 lifecycle_state 来「推进」阶段。\n` +
  `- 开发阶段写代码前须 plan-gate-check.sh 通过。\n` +
  `- 若阻塞仅因「未创建子 plan」→ 按该 stage 的 template 创建 plan 到 planFolder；${usesEpic ? '并回写 Epic plans.<字段> 路径索引（仅路径映射，属数据上下文允许项）。' : '无 Epic 无需回写。'}\n` +
  `- 若阻塞为 P0/未采纳/WBS 未勾 → 只输出待办，不进入下一阶段。\n` +
  `- 界面/对稿/还原/Figma 类切片强制 figma-ui，不得用 feature-dev-assistant 手写布局替代。\n` +
  `- 完成后子 Skill 须在其 plan 末尾追加 skill_run 反馈块（协议见 Contexts/决策/Skill反馈协议）。\n` +
  `\n完成后 output report：📌 当前阶段 | 产出路径 | ${usesEpic ? '看板 | ' : ''}下一阶段 | /resume 命令。`,
  { label: `exec:${workflow}:${gate.current_state}`, phase: '执行当前 Skill', schema: EXEC_SCHEMA }
)

phase('汇报与下一步')

if (usesEpic) {
  await agent(
    `用 Bash 运行 \`./scripts/kanban-sync.sh --boot ${epicPath ? `--epic ${epicPath} ` : ''}2>/dev/null || true\` 同步看板。只需运行并简短确认，不要分析。`,
    { label: 'kanban-sync', phase: '汇报与下一步' }
  )
}

return {
  workflow,
  uses_epic: usesEpic,
  current_state: gate.current_state,
  next_state: gate.next_state,
  skill: gate.recommended_skill,
  gate: gateResult,
  execution: executed,
  report: executed?.report || report,
  blueprint: `.workflows/blueprints/${workflow}.json`,
}
