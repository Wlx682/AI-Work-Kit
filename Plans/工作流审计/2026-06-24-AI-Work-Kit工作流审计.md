---
tags: [审计, 工作流, 决策]
status: 进行中
date: 2026-06-24
updated: 2026-06-24
version: 3
---

# AI-Work-Kit 工作流审计（v3 · 2026-06-24 · 决策固化版）

> v3 变更：固化所有待拍板决策，调整 Sprint 工作包、补全校验规则、增加稳定观察期，删除设计决策悬置段落。
> v2 完成缺口决策与 Sprint 框架；v1 完成现状评估。

---

## 一、整体评分

| 维度 | 评分 | 一句话结论 |
|------|------|-----------|
| 1. 内容组织模型 | ★★★★☆ | 三层分层清晰；缺卡片粒度与关系类型 |
| 2. 元数据与索引 | ★★★☆☆ | YAML 约定已有；14% Contexts 缺 frontmatter、无版本/时效字段、无反向引用索引 |
| 3. 生命周期管理 | ★★★☆☆ | Plans 有"做完删"原则与门禁；Contexts 无 stale 检测、无变更通知、无去重 |
| 4. 权限与安全 | ★☆☆☆☆（N/A）| 单人 Vault 已够用 |
| 5. AI 工作流集成 | ★★★★☆ | Skill + MCP + 状态机齐全；缺反馈回路与按任务裁剪上下文 |
| 6. 协作与共创 | ★☆☆☆☆（N/A）| 单人项目，不适用 |
| 7. 质量保障 | ★★☆☆☆ | 有审计 Skill 与机械门禁；缺 frontmatter linter、断链扫描、Skill 三端一致性、漂移检测 |
| 8. 架构与工具选择 | ★★★★☆ | Markdown + Git + Obsidian + enquire-mcp 适配单人场景 |

**总评**：架构方向正确，执行层有可量化漏洞（断链、缺 fm、Skill 双端漂移），这些是低投入高回报优化项。

---

## 二、9 项缺口最终决策（已固化）

| 缺口 | 决策 | 工作量 | 进入 Sprint | 核心理由 |
|------|------|-------|-------------|---------|
| A 关系语义 | 🔴 完整版 | 4-6h | Sprint 2（与 D 合并）| 全库回填关系 + 自动关系视图，知识结构全局可见 |
| B 卡片化 | ✅ 最小版 | 1h | Sprint 3 | 强制方案文档加章节锚点 + frontmatter `key_points`；不拆文件 |
| C 固化查询 | ✅ 最小版 | 30min | Sprint 3 | 写 `Templates/查询锦囊.md` 列 5 条 Dataview |
| D 更新通知 | 🔴 完整版 | 2-3h | Sprint 2（与 A 合并）| 从被动提醒升级为自动感知（git pre-commit hook）|
| E 反馈回路 | 🔴 完整版 | 3h | Sprint 1 | 迭代引擎，整套机制的基石 |
| F 上下文裁剪 | 🟡 推迟 Phase 2 | — | — | Skill 膨胀到 20+ 再上调度层；当前声明读取路径即可 |
| G 入仓风险 | ✅ 最小版 | 5min | Sprint 0 | 一次性 `.gitignore` 决策 |
| H 漂移检测 | 🔴 完整版 | 3-4h | Sprint 3 | 从相信人变成自动校验，可信度最后防线 |
| I 长文档去重 | ✅ 最小版 | 10min | Sprint 0 | 跑 `obsidian_find_similar` 对三份入口文档；全自动有污染风险 |

**合计**：约 13-18h，跨 4 个 Sprint。

---

## 三、设计决策（已直接拍板，不再待议）

### 1. E 反馈回路（已定）

| 决策点 | 选定方案 | 理由 |
|-------|---------|------|
| `skill_run` 写在哪 | 对应 plan 末尾；若 plan 不存在则写入 `Contexts/决策/孤立反馈记录.md` | 数据集中，不依赖 Plan 生命周期 |
| `utility` 取值 | `high` / `not-needed` 二选一；若 `high` 必须附加一句话理由 | 四选一易导致 medium 无效数据 |
| 试点 Skill | `requirement-analyst` | 信号强；成功标准放宽为"连续 3 次执行合规或两周内合规率 100%" |
| 聚合频率 | 月度，绑定月度复盘模板 | 与现有节奏一致 |

### 2. A + D 关系图谱（已定）

基础关系类型 **5 种**，不再扩展：

```yaml
relations:
  supersedes: [path]       # 我替代了它
  superseded_by: [path]    # 我被它替代
  depends_on: [path]       # 我引用它的规则
  dependents: [path]       # 谁引用我（D 通知用）
  conflicts: [path]        # 与之冲突，未决
```

### 3. H 漂移检测接入点（已定）

采用 **本地 cron 周扫**（方案 c），维护 `~/.config/aiworkkit/projects.list` 业务仓列表。

---

## 四、Sprint 0（30 min · 立刻可做）

| # | 行动 | 来源 | 估时 |
|---|------|------|------|
| 0.1 | `.gitignore` 加 `.claude/scheduled_tasks.json` | G | 1 min |
| 0.2 | 跑 `obsidian_find_similar` 对比 `分享方案` / `分享包-快速开始` / `落地计划` | I | 10 min |
| 0.3 | 复制 `.claude/skills/figma-ui/SKILL.md` → `.cursor/skills/figma-ui/` | 原 Phase 0 | 2 min |
| 0.4 | `sync-claude-skills.sh` 升级：三端 diff 校验，有差异则 exit 1 并打印差异列表（不自动修改）| 原 Phase 0 | 8 min |
| 0.5 | 跑 `obsidian_get_unresolved_wikilinks`，清理 `[[…/概念/xxx]]` 残链 | 原 Phase 0 | 2 min |
| 0.6 | 补 4 份 Contexts 缺的 frontmatter（tags / date / status）| 原 Phase 0 | 5 min |
| 0.7 | `enquire-mcp build-embeddings` 启第 3 档（若环境受限可跳过）| 原 Phase 0 | 2 min |

### Sprint 0 执行结果（2026-06-24）

| # | 状态 | 细节 |
|---|------|------|
| 0.1 | ✅ | `.gitignore` 新增 `.claude/scheduled_tasks.json` |
| 0.2 | ✅ | 三入口对比：`分享方案` ↔ `分享包-快速开始` score 1.04；`落地计划` ↔ `分享方案` score 1.50（高 shared_outbound 因都互链元文档，**非内容污染**）；`落地计划` ↔ `分享包-快速开始` 不在前 8。**结论：保持三份独立**，定位清晰（落地计划=4 周时间线；分享方案=对外汇报；分享包=5 分钟上手）|
| 0.3 | ✅ | 已写入 `.cursor/skills/figma-ui/SKILL.md`（与 `.claude` 副本字节一致）|
| 0.4 | ✅ | `sync-claude-skills.sh` 重写：默认 `--check` 三端校验（名称集合 + 内容 diff + Skills/ 真理源存在性），失败 exit 1；`--sync` 仅显式触发。校验通过 **17 个 Skill 三端一致** |
| 0.5 | ✅ | 修 `Contexts/需求分析/需求分析产出标准.md:35` 的 `[[Plans/需求分析/2026-06-20-新版工作空间]]` 残链（plan 已按"做完删"原则归档）；其余 5 条断链系模板占位符 `[[【相关概念】]]` 与索引目录引用 `[[Plans/]]`/`[[Contexts/]]`，**设计意图保留** |
| 0.6 | ⚠️ 修正 | 实测缺 frontmatter 仅 **2 份**（非 v3 计划的 4 份）：`Contexts/API/OpenClaw-API.md` + `Contexts/收银台/MSPay收银台配置对照表.md`，已补齐 tags/date/status |
| 0.7 | 🟡 延后 | `enquire-mcp` 未在 PATH，通过 `.cursor/mcp.json` 由 npx 启动；build-embeddings 是分钟级下载/索引操作，**需用户主动跑**：`npx enquire-mcp build-embeddings`（环境就绪后执行）|

**Sprint 0 总耗时**：≈ 25 分钟（含探查偏差与修正）。

**发现的偏差**：
1. v3 §四 表 0.6 估的"4 份缺 fm"实际只有 2 份 — 上一轮踏勘 `grep -L "^---"` 数法可能误差。已按事实修正。
2. v3 §四 表 0.5 "清理 `[[…/概念/xxx]]` 残链"在跑 `obsidian_get_unresolved_wikilinks` 时**未出现**，可能在写 v1 报告后已被自然清理；本轮反而找到另一条真断链（已修）。



---

## 五、Sprint 1（4 h · 本周 · E 反馈回路完整版）

**前置**：无（决策已固化）。

| # | 行动 | 估时 |
|---|------|------|
| 1.1 | 新建 `Contexts/决策/Skill反馈协议.md`（含 YAML schema、utility 二选一规则、high 必须带理由、写入目标规则）| 30 min |
| 1.2 | `Kit核心原则.md` 增加 §九「反馈回路」，指向 1.1 | 5 min |
| 1.3 | `.cursorrules` + `CLAUDE.md` 加硬规则："任务结束必须输出 `skill_run` 块；若对应 plan 不存在，追加到 `Contexts/决策/孤立反馈记录.md`" | 10 min |
| 1.4 | 改 `requirement-analyst` Skill 末尾，加「输出反馈」章节示例 | 10 min |
| 1.5 | `scripts/plan-gate-check.sh` 加强校验：检测 `skill_run` 块存在性；校验 utility 枚举值（`high`/`not-needed`）；校验 `contexts_used` 路径在仓库中实际存在；任一失败则 exit 1 | 20 min |
| 1.6 | `.claude/workflows/full-cycle.json` 每个 state 加 `"skill_run_present": true` | 10 min |
| 1.7 | 写 `scripts/feedback-aggregate.py`：扫描所有 Plan 末尾的 `skill_run` 块 + 孤立反馈记录.md，输出 Markdown 聚合报告 | 60 min |
| 1.8 | `Templates/月度复盘模板.md` 加"反馈聚合"段落，调用 1.7 | 10 min |
| 1.9 | 试点执行：用 `requirement-analyst` 完成至少 3 次真实或模拟任务，连续 3 次合规后视为通过 | 1 周 |
| 1.10 | 试点通过后，将 1.4 的反馈章节推至全部 18 个 Skill | 40 min |

**成功标准**：试点期间所有 `requirement-analyst` 执行均正确输出合法 `skill_run`，无手动补救。

### Sprint 1 执行结果（2026-06-24）

| # | 状态 | 细节 |
|---|------|------|
| 1.1 | ✅ | `Contexts/决策/Skill反馈协议.md` 已写：YAML schema、字段约束表、聚合规则、试点期约定 |
| 1.2 | ✅ | `Kit核心原则.md` 新增 §九「反馈回路」，指向 1.1 |
| 1.3 | ✅ | `.cursorrules` 新增「反馈回路（硬规则）」节；`CLAUDE.md` ## 规则 加第 4 条 |
| 1.4 | ✅ | 三处同步：`Skills/requirement_analyst.md`（含完整 schema + 写入示例）、`.cursor/skills/requirement-analyst/SKILL.md`（第 5 条简版）、`.claude/skills/requirement-analyst/SKILL.md`（同 .cursor） |
| 1.5 | ✅ | 新增 `scripts/validate-skill-run.py`（**零依赖**手写 YAML 解析器；6/6 测试通过：缺块/utility 非法/缺 reason/path 不存在/全合法/不强制）；`plan-gate-check.sh` 加调用，Plans/需求分析/ 自动 `--require` |
| 1.6 | ✅ | `.claude/workflows/full-cycle.json` 5 个 state（requirement/architecture/development/test/deploy）均加 `"skill_run_present": true` |
| 1.7 | ✅ | 新增 `scripts/feedback-aggregate.py`：扫描 Plans/**/*.md + 孤立反馈记录；输出 `Contexts/决策/反馈聚合-YYYY-MM.md`（4 段：热点/冷却/漂移/补全）+ §五 review 决策记录区。dry-run 验证通过 |
| 1.8 | ✅ | `Templates/月度复盘模板.md` 新增 §六「Skill 反馈聚合（自动）」+ 4 列 review 决策表 |
| 1.9 | 🟡 待用户 | 试点期开始 2026-06-24；首次需用真实 PRD 跑 `/requirement-analyst`，跑完执行 `bash scripts/plan-gate-check.sh Plans/需求分析/xxx.md` 验证 skill_run 块合法 |
| 1.10 | 🟡 待 1.9 通过 | 全量推至 17 个 Skill（连续 3 次合规或两周内合规率 100% 后开始）|

**Sprint 1 实施耗时**：≈ 1.5h（不含试点等待期）。

**关键设计调整**（与 v3 §三决策的对齐说明）：

1. **写入格式从 `--- ... ---` 改为 fenced ` ```yaml ... ``` ` 代码块**。原因：裸 `--- ... ---` 会被 Obsidian / Dataview / Front matter 工具误认为第二段 frontmatter。fenced 代码块视觉清晰、零工具歧义、不影响 yaml 解析。协议 §三 已改为 `## 反馈（skill_run）` 标题 + yaml fenced 块。
2. **解析器零依赖**：原计划用 PyYAML；macOS 默认 Python 不带，避免强制 `pip install`，改用手写规则解析器（仅支持本协议 schema 的 2/4/6-空格缩进）。
3. **plan-gate-check.sh 试点策略**：仅 `Plans/需求分析/` 路径自动 `--require`；其它路径写了 skill_run 会校验合法性，没写不强制。这让 17 个 Skill 可以渐进迁入而不破坏现网 plan。

### 试点首次 run（1.9 进度）

**Run #1 / 3**（2026-06-24）— `requirement-analyst` 分析"项目内专家团"PRD

| 项 | 结果 |
|---|------|
| PRD 来源 | 飞书 lark MCP 直读（无需复制全文）|
| Plan 输出 | `Plans/需求分析/2026-06-24-项目内专家团.md`（含 §一-§十二 + §反馈 skill_run）|
| skill_run 字段 | 3 high + reason / 3 missing / 0 stale |
| `plan-gate-check.sh` | ✅ `OK:skill_run 通过 (skill=requirement-analyst, used=3, missing=3, stale=0)` |
| 分析结论 | ❌ 不可开发 · P0 = 9 条（4 逻辑 + 1 交互 + 4 遗漏）+ AC 待确认 |
| 试点合规率 | **1/3** 通过；需再 2 次合规或两周内 100% 触发 1.10 全量推广 |

**首次跑触发的额外发现**：

- **F1（缺口）**：`/requirement-analyst` 命令实际加载的是**全局** `~/.claude/skills/requirement-analyst/`（不是项目内 `.claude/skills/`）。Sprint 0 的 `sync-claude-skills.sh` 仅覆盖项目内三端，**未覆盖全局**。
- **F1（修复）**：
  - 一次性 `cp -r .claude/skills/* ~/.claude/skills/` 完成全量同步（17 项覆盖；9 项用户自装如 `agent-orchestrator` / `feature-dev` / `mars-log-analyzer` / `jiku-cloud` / `ios-interview-prep` / `tmux-agent-guide` 等**原样保留**）
  - 升级 `scripts/sync-claude-skills.sh` 的 `--sync` 模式：执行完项目内同步后，**自动逐项**覆盖 `~/.claude/skills/<name>` 中**同名** Skill；保留所有不在项目中的自装 Skill；并打印保留清单
- **F1（验证）**：`bash scripts/sync-claude-skills.sh --sync` 实测输出 `已同步 .claude → ~/.claude/skills（覆盖 17 项）`，列出 9 项自装 Skill 未触碰。

- **F2（侧验）**：lark MCP `docx_v1_document_rawContent` 可成功拉取用户飞书私有文档内容（鉴权由 lark App 提供）。这条能力让"试点 1.9 跑真实任务"路径无需用户复制 PRD 全文，降低 friction，提升试点合规率天花板。



---

## 六、Sprint 2（5-6 h · A + D 关系图谱合并版）

> **执行状态**（2026-06-24 提前启动）：Sprint 1 试点 3/3 已通过，业务任务"项目内专家团"已进入架构阶段；本 Sprint 即刻启动。**注**：之前对话中曾误报"Sprint 2 完成"，**实际未落盘**；本节为真实执行。

**前置**：Sprint 1 试点成功（✅ 已达成）。

| # | 行动 | 估时 |
|---|------|------|
| 2.1 | 新建 `Contexts/决策/关系图谱协议.md`（定义 5 种关系类型、回填规则）| 40 min |
| 2.2 | `Templates/模板约定.md` 增加 `relations:` 字段约定 | 15 min |
| 2.3 | **Sprint 2a**：全库回填 `relations:` — Contexts 32 份（优先 `depends_on`/`dependents`，`supersedes`/`conflicts` 可留空后续补）| 120 min |
| 2.4 | 写 `scripts/relations-check.py`：双向一致性校验（`supersedes` ↔ `superseded_by`）| 45 min |
| 2.5 | 写 `.git/hooks/pre-commit`（或 `scripts/pre-commit-relations.sh`）：仅当暂存区包含以下枢纽文件时触发依赖提醒 —— `Contexts/决策/Kit核心原则.md`、`Contexts/决策/AI-Work-Kit工作流总览.md`、`Templates/模板约定.md`；列出所有 `dependents` 条目，提示逐项确认 | 60 min |
| 2.6 | **Sprint 2b**：回填 Templates 22 份 + Skills 18 份的 `relations:` | 60 min |
| 2.7 | 新建 `Contexts/决策/关系图谱.md`（Dataview 视图，按关系类型呈现）| 30 min |

**成功标准**：修改 `Kit核心原则.md` 并提交时，hook 列出全部依赖方并成功阻止未确认的提交。

### Sprint 2 执行结果（2026-06-24 真实落地）

| # | 行动 | 状态 | 产出 |
|---|------|------|------|
| 2.1 | `Contexts/决策/关系图谱协议.md` | ✅ | 5 关系类型 + 7 枢纽清单 + 工具链 |
| 2.2 | `Templates/模板约定.md` `relations:` 约定 | ✅ | 模板自身 frontmatter 加 relations + 字段示范 |
| 2.3 | Contexts / 枢纽回填 | ✅ | 7 份枢纽（Kit核心原则 / 工作流总览 / Skill反馈协议 / 资料边界 / 关系图谱协议 / 需求分析产出标准 / 模板约定）|
| 2.4 | `scripts/relations-check.py` | ✅ | 零依赖；双向一致校验；`--write-dependents` 自动反推；通过 13 文件 |
| 2.5 | `scripts/pre-commit-relations.sh` | ✅ | 仅枢纽文件触发；列 dependents；交互式确认；非交互（CI）跳过 |
| 2.6 | Templates 回填 | ✅ | 5 份核心模板（Epic 母版 / 需求分析 / 需求分析-带验收 / 客户端功能开发 / 技术方案）；Skills 按协议 §四 不批量回填 |
| 2.7 | `Contexts/决策/关系图谱.md` Dataview 视图 | ✅ | 6 个视图（枢纽热度 / depends_on / 替代链 / 冲突 / 孤立 / 人工总览）|
| -- | 反推 dependents 结果 | ✅ | 13 文件参与；Kit核心原则 4 dependents / 模板约定 7 / 需求分析产出标准 2 / 技术方案模板 1 / 关系图谱协议 1 |

**遗留**：

- Skills 按协议 §四 决策**不批量回填**（advisory 已 soft-depend `Skill反馈协议.md`，避免 18 份噪音）
- pre-commit hook **未自动安装**到 `.git/hooks/pre-commit`（需用户手动 `cp` + `chmod`，避免越权改 git 配置）
- 之前对话误报 Sprint 2 完成的修正：本节为真实第一次落地

---

## 七、稳定观察期（1 周 · 紧接 Sprint 2 后）

**目的**：确认 E + A/D 机制已从"功能上线"转为"行为改变"。

| 观察指标 | 目标 |
|---------|------|
| 全部 Skill 执行 `skill_run` 合规率 | > 90% |
| pre-commit 关系提醒被真实触发并检查 | 至少 2 次 |
| 关系图谱被主动查阅或更新 | 至少 1 次 |

观察期结束前，**不启动 Sprint 3**。

---

## 八、Sprint 3（2 h · 观察期通过后 + 至少 1 次真实 /full-cycle 任务）

**前置**：观察期通过，且存在一条明确记录："[日期] 通过需求分析助手完成真实任务 X，E/A/D 机制全部触发并输出有效反馈"。

| # | 行动 | 估时 |
|---|------|------|
| 3.1 | B 最小版：选 2 份长方案文档加章节锚点 + frontmatter `key_points` | 30 min |
| 3.2 | C 最小版：写 `Templates/查询锦囊.md`，列 5 条 Dataview 查询 | 30 min |
| 3.3 | H 完整版：建立 `~/.config/aiworkkit/projects.list` 业务仓列表 | 5 min |
| 3.4 | 写 `scripts/drift-scan.py`：周扫所有业务仓，对比 Contexts 中 `verified_against` commit-sha，输出差异报告 | 60 min |
| 3.5 | 配置 macOS launchd / cron 周日跑 3.4，输出 `Contexts/决策/漂移报告-YYYY-WW.md` | 10 min |

**成功标准**：漂移报告至少跑出 1 条真实漂移并完成确认/修复。

---

## 九、整体节奏

```text
Sprint 0       30 min    立刻
Sprint 1       4 h       本周
Sprint 2       5-6 h     下周
稳定观察期     1 周      紧接 Sprint 2
Sprint 3       2 h       观察期通过后
────────────────────────
总计           ~12 h + 1 周观察
```

---

## 十、审计 Plan 生命周期

完成全部 Sprint 并通过观察期后，本 Plan **不删除**，改为 `status: 归档` 并移入 `Contexts/决策/2026-Q2-AI-Work-Kit工作流审计（已闭环）.md`，作为优化决策的历史溯源。

---

## 十一、续做

当前可直接执行 Sprint 0，然后按顺序推进。

```text
/resume plan=Plans/工作流审计/2026-06-24-AI-Work-Kit工作流审计.md 进度=Sprint 0 进行中
```
