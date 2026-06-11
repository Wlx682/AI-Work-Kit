export const meta = {
  name: 'learning-audit',
  description: '审计 Plans/学习/ 各课声称状态与实际证据（步骤复选框、概念卡、学习笔记）的一致性，交叉比对后写入审计报告',
  whenToUse: '用户要求「审计学习进度」「检查学习计划真实完成度」「声称进度 vs 真实进度」时',
  phases: [
    { title: '发现课程', detail: '扫描学习计划目录下的课程 plan' },
    { title: '逐课取证', detail: '每课一个 agent，独立采集四类证据' },
    { title: '交叉比对', detail: '汇总比对一致性，写入审计报告' },
  ],
}

// 可通过 args 覆盖默认路径：{ plansFolder, conceptsFolder, notesFolder, reportFolder, today }
const plansFolder = (args && args.plansFolder) || 'Plans/学习'
const conceptsFolder = (args && args.conceptsFolder) || 'Contexts/LLM学习/概念'
const notesFolder = (args && args.notesFolder) || 'Contexts/LLM学习/笔记'
const reportFolder = (args && args.reportFolder) || 'Contexts/LLM学习/笔记'
// 脚本内不可用 Date.now()；today 可由 args 传入，否则由写报告的 agent 自行运行 `date +%F` 获取
const today = (args && args.today) || null

phase('发现课程')

const LESSONS_SCHEMA = {
  type: 'object',
  required: ['lessons'],
  properties: {
    lessons: {
      type: 'array',
      items: {
        type: 'object',
        required: ['path', 'title'],
        properties: {
          path: { type: 'string', description: 'vault 相对路径' },
          title: { type: 'string', description: '课程名，如「第1课-LLM与提示词入门」' },
        },
      },
    },
  },
}

const discovered = await agent(
  `列出 ${plansFolder}/ 目录下所有课程 plan 的 .md 文件（vault 根目录为当前工作目录）。` +
  `每个文件返回 path（相对路径）和 title（从文件名提取课程名）。不要读取文件内容，只列目录。`,
  { label: 'scan-lessons', phase: '发现课程', schema: LESSONS_SCHEMA }
)

if (!discovered || !discovered.lessons.length) {
  return { error: `${plansFolder}/ 下未发现课程 plan，审计中止` }
}
log(`发现 ${discovered.lessons.length} 节课，开始逐课取证`)

const EVIDENCE_SCHEMA = {
  type: 'object',
  required: ['lesson', 'claimed_status', 'checkbox_checked', 'checkbox_total', 'concept_cards_expected', 'concept_cards_found', 'has_note', 'verdict', 'details'],
  properties: {
    lesson: { type: 'string' },
    claimed_status: { type: 'string', description: 'frontmatter 中的 status 原文，如「已完成」「进行中」' },
    checkbox_checked: { type: 'number', description: '已勾选 - [x] 数量' },
    checkbox_total: { type: 'number', description: '复选框总数' },
    concept_cards_expected: { type: 'array', items: { type: 'string' }, description: 'plan 资料区双链指向的概念卡名' },
    concept_cards_found: { type: 'array', items: { type: 'string' }, description: '概念卡目录中实际存在的' },
    has_note: { type: 'boolean', description: '笔记目录下是否存在本课对应的学习笔记（交叉引用链接不算）' },
    note_paths: { type: 'array', items: { type: 'string' } },
    verdict: { type: 'string', enum: ['一致', '轻微偏差', '严重矛盾'], description: '声称状态与四类证据的一致性结论' },
    details: { type: 'string', description: '取证细节与矛盾点说明，中文' },
  },
}

phase('逐课取证')

const evidences = await parallel(discovered.lessons.map(l => () =>
  agent(
    `你是学习进度审计员，只看文件证据，不轻信任何声称。审计课程「${l.title}」（文件：${l.path}）。\n` +
    `独立采集四类证据：\n` +
    `1. 读 ${l.path} 的 frontmatter，记录 status 原文（claimed_status）；\n` +
    `2. 统计同一文件内 - [ ] / - [x] 复选框的总数与已勾选数；\n` +
    `3. 提取 plan 资料区 [[双链]] 指向的概念卡名，逐一核对 ${conceptsFolder}/ 下是否存在对应 .md；\n` +
    `4. 在 ${notesFolder}/ 下查找本课对应的学习笔记——必须是以本课主题为内容的笔记，其他笔记里出现交叉引用链接不算；练习表格是否填写也作为佐证。\n` +
    `判定 verdict：status=已完成 但复选框 0 勾选或无笔记 → 严重矛盾；status=进行中/未开始 且证据相符 → 一致；介于两者之间 → 轻微偏差。\n` +
    `在 details 中说明取证细节和矛盾点。`,
    { label: `audit:${l.title}`, phase: '逐课取证', schema: EVIDENCE_SCHEMA }
  )
))

const valid = evidences.filter(Boolean)
if (!valid.length) {
  return { error: '所有取证 agent 失败，审计中止' }
}
if (valid.length < discovered.lessons.length) {
  log(`警告：${discovered.lessons.length - valid.length} 节课取证失败，报告仅覆盖 ${valid.length} 节`)
}

phase('交叉比对')

const REPORT_SCHEMA = {
  type: 'object',
  required: ['report_path', 'summary'],
  properties: {
    report_path: { type: 'string' },
    summary: { type: 'string', description: '一句话综合结论' },
  },
}

const dateInstruction = today
  ? `报告日期为 ${today}。`
  : `先用 Bash 运行 \`date +%F\` 获取今天日期。`

const report = await agent(
  `你是审计汇总员。以下是对各节课独立取证的 JSON 证据：\n\n` +
  JSON.stringify(valid, null, 2) +
  `\n\n${dateInstruction}\n` +
  `交叉比对后，将审计报告写入 ${reportFolder}/<日期>-学习进度审计报告.md（若同名文件已存在则覆盖）。报告结构：\n` +
  `1. frontmatter：tags: [学习, 审计报告, workflow]、date；\n` +
  `2. 开头一段综合结论（声称进度与真实进度是否存在系统性偏差）；\n` +
  `3. 「## 总览」表格：课程 | 声称状态 | 实际完成度 | 步骤(勾选/总) | 概念卡 | 有笔记 | 一致性；\n` +
  `4. 「## ⚠️ 发现的不一致」逐课说明矛盾点；\n` +
  `5. 「## 下一步建议」逐课给出可执行的补救步骤；\n` +
  `6. 末尾注明由 learning-audit workflow 生成及日期。\n` +
  `返回 report_path 和一句话 summary。`,
  { label: 'synthesize-report', phase: '交叉比对', schema: REPORT_SCHEMA }
)

return {
  lessons_audited: valid.length,
  verdicts: valid.map(e => ({ lesson: e.lesson, claimed: e.claimed_status, verdict: e.verdict })),
  report_path: report ? report.report_path : null,
  summary: report ? report.summary : '报告写入失败',
}
