---
tags: [Epic, 工作流, client-dev]
type: plan
category: Epic
status: 草稿
date: 2026-08-04
epic_id: flutter-labor-arbitration-generative-assistant-app
workflow: client-dev
lifecycle_state: requirement
platform: 客户端
repo: labor_assistant
branch: main
含业务逻辑: 是
p0_open: 0
plans:
  requirement: Plans/需求分析/2026-08-04-Flutter版劳动仲裁生成式智能助手App.md
  architecture: Plans/技术方案/2026-08-04-Flutter版劳动仲裁生成式智能助手App.md
  test: Plans/自动化测试/2026-08-04-Flutter版劳动仲裁生成式智能助手App.md
  development: Plans/功能开发/2026-08-04-Flutter版劳动仲裁生成式智能助手App.md
relations:
  depends_on:
    - Templates/模板约定.md
  dependents: []
  supersedes: []
  superseded_by: []
  conflicts: []
---
# Epic：Flutter版劳动仲裁生成式智能助手App（工作流：client-dev · 15 步）

**创建日期**：2026-08-04  
**存放路径**：`Plans/Epic/2026-08-04-Flutter版劳动仲裁生成式智能助手App.md`  
**状态**：草稿  
**关联仓库**：`/Users/wanglongxiang/git/labor_assistant` · 分支：`main`

> **三层架构定位**：本 Epic 是**数据上下文（聚合根）**——只存子 Plan 路径映射、WBS 人工确认板、里程碑摘要。  
> **不驱动流程**：阶段推进由通用执行器读工具中性蓝图 `.workflows/blueprints/client-dev.json` + `scripts/workflow-gate.sh`（只看子 Plan 事实）决定。  
> `lifecycle_state` 不参与路由，仅供人工阅读；整体阶段跑 `bash scripts/derive-epic-status.sh Plans/Epic/2026-08-04-Flutter版劳动仲裁生成式智能助手App.md` 派生。

---

## 一、项目目标

面向执业 1-5 年的小律师/独立律师，构建 Flutter 版“劳动仲裁生成式智能助手 App”：在手机本地完成案情理解、赔偿金精准计算、法条/判例检索、评估报告生成、全套 Word 文书生成与分享，并逐步演进为可上架、可试用、可商业转化的生产化移动应用。

核心价值主张：让律师 3 分钟内判断“这个案子能不能接、能收多少钱、胜算有多大”，并把评估结果进一步生成可编辑、可分享、可归档的法律文书。

### 生成式产品定位

| 层级 | 产品能力 | 说明 |
|------|----------|------|
| 第一阶段可交付基线 | 确定性评估 + 结构化报告 + Word 文书生成 | 先保证计算正确、法条可追溯、文书可导出。 |
| 生成式增强版本 | 本地 LLM 参数提取、追问补全、报告润色、文书动态改写 | 让 App 从“表单工具”升级为“劳动仲裁 Agent”。 |
| 生产化上架版本 | 模型管理、知识库更新、历史案件管理、试用/订阅、真机性能优化 | 面向真实律师试用、付费转化和应用市场发布。 |

---

## 二、产品范围

### P0（必须有）

| 功能 | 描述 | 技术实现 |
|------|------|----------|
| 案件评估器 | 输入 6 个字段或案情描述，输出完整评估报告 | Agent 调度 + Dart 计算 + 本地法条检索 |
| 赔偿金计算器 | N、2N、双倍工资、加班费、未休年假折算 | 纯 Dart 代码 |
| 文书生成 | 生成《劳动仲裁申请书》《证据清单》Word 文档 | docx_template + 模板兜底 |
| 本地存储 | 用户案情、报告、文书记录本地保存 | SQLite + Hive |

### P1（差异化）

| 功能 | 描述 |
|------|------|
| 本地判例检索 | 检索类似判例，给出支持率和平均赔偿金额参考 |
| 律师费报价建议 | 按赔偿金额生成固定收费与风险代理区间 |
| 一键分享 | 微信/邮件发送文书 |

### P2（长期）

| 功能 | 描述 |
|------|------|
| 对方抗辩模拟 | Agent 模拟被申请人可能抗辩理由 |
| 多领域扩展 | 交通事故、婚姻家事等领域复用 Agent/文书/RAG 架构 |

---

## 三、技术路线

| 模块 | 技术方案 | 备注 |
|------|----------|------|
| 跨平台 | Flutter | iOS + Android，Web 仅用于开发验证 |
| 状态管理 | Riverpod | 轻量响应式 |
| 本地模型 | flutter_llama / llama.cpp FFI | GGUF 模型接入预留 |
| RAG | sqlite_vector / mobile_rag_engine | 当前先有本地检索抽象和关键词兜底 |
| 文书生成 | docx_template + archive fallback | 模板占位符生成 Word 文件 |
| 本地存储 | SQLite + Hive | 历史、报告、配置 |
| 分享 | share_plus | 文书分享 |
| 隐私 | flutter_secure_storage | 敏感配置本地加密 |

---

## 四、当前代码状态

已在 `/Users/wanglongxiang/git/labor_assistant` 创建独立 Flutter 项目，并完成第一阶段可验证基线骨架：

- `lib/core/agent_engine.dart`：Agent 调度骨架
- `lib/tools/compensation_calculator.dart`：赔偿金计算器
- `lib/tools/law_retriever.dart`：本地法条检索器
- `lib/tools/template_filler.dart`：Word 文书生成
- `lib/domains/labor/workflows/evaluate_case.dart`：劳动案件评估工作流
- `lib/ui/`：案情、报告、文书、设置四页
- `assets/domains/labor/knowledge/`：劳动法条与典型案例种子数据
- `assets/templates/`：仲裁申请书与证据清单模板
- `test/`：计算器、Agent、模板生成、UI 测试

当前验证已通过：

```bash
flutter analyze
flutter test
flutter test --platform chrome
flutter build web
```

---

## 五、子 Plan 索引

| 阶段 | 路径 | status |
|------|------|--------|
| 需求分析（事件风暴+实例化） | `Plans/需求分析/2026-08-04-Flutter版劳动仲裁生成式智能助手App.md` | ⬜ |
| 技术方案 + ADR | `Plans/技术方案/2026-08-04-Flutter版劳动仲裁生成式智能助手App.md` | ⬜ |
| 验收测试先行 | `Plans/自动化测试/2026-08-04-Flutter版劳动仲裁生成式智能助手App.md` | ✅ |
| 拆分任务 | — | ⬜ |
| 功能开发 | `Plans/功能开发/2026-08-04-Flutter版劳动仲裁生成式智能助手App.md` | ⬜ |
| Bug 排查 | — | — |

---

## 六、阶段门禁（退出条件 = 子 Plan 文件系统事实）

| 阶段 | stage key | WBS | 退出条件（workflow-gate.sh 判定） |
|------|-----------|-----|-----------------------------------|
| 需求分析 | requirement | 1–2 | 需求 plan `status: 已采纳` 且 `p0_open: 0` + 验收标准章节 |
| 技术方案 | architecture | 3 | 方案 `status: 已采纳`（含业务逻辑时必经） |
| 验收测试先行 | test-first | 4 | 测试 plan 存在 + WBS 4 ✅ |
| 拆分任务 | split | 5 | 主 plan + 子任务已拆 + WBS 5 ✅ |
| 功能开发 | development | 6–11 | `plan-gate-check.sh` OK + WBS 6–11 ✅ |

---

## 七、WBS 看板（1–11 · 精简版）

| # | 切片 | 归属 stage | Skill | 验收 |
|---|------|-----------|-------|------|
| 1 | 事件风暴工作坊 | requirement | event-storming-assistant | 事件墙无歧义、热点认领 |
| 2 | 实例化需求（≥10 组 GWT + 线框） | requirement | spec-by-example-assistant | PO/开发/测试对齐 |
| 3 | 技术方案 + ADR + 领域模型 | architecture | architecture-design-assistant | status=已采纳 |
| 4 | 验收测试先行（外层 TDD，先红） | test-first | test-generator | 测试自动化运行，失败仅因未实现 |
| 5 | 原子任务拆分（主 plan + 子任务） | split | task-splitter | 子任务边界清晰、可独立验收 |
| 6 | Domain / UseCase 实现 | development | feature-dev-assistant | 单测过 |
| 7 | Data / API 实现与联调 | development | feature-dev-assistant | 真实接口替换假数据 |
| 7d | 本地模型 Runtime 与 GGUF 接入 | development | feature-dev-assistant | 模型生命周期、真实本地推理 adapter、失败恢复与 fake backend 测试 |
| 7e | Agent 增强编排与工具契约 | development | feature-dev-assistant | 结构化提取、evaluate_case 确定性工具、缺字段追问、fallback 与 trace；独立法条/文书工具待接 |
| 8 | UI 骨架 + 静态设计走查 | development | figma-ui | 静态布局走查通过 |
| 9 | 交互 + 全 Variant（空/错误态） | development | figma-ui | 交互走查 + 边界示例可覆盖 |
| 10 | 单元测试补充与回归（内层 TDD） | development | test-generator | CI 单测全绿 |
| 11 | 真机联调 + 集成设计走查 | development | figma-ui / feature-dev-assistant | 真机适配走查通过 |

```
[ ] 1.  事件风暴工作坊（领域事件墙 / 热点 / 角色-系统）
[ ] 2.  实例化需求（≥10 组 Given-When-Then + 线框草图）
[ ] 3.  技术方案 + ADR + 领域模型草图
[x] 4.  验收测试先行（外层 TDD，先红）
[x] 5.  原子任务拆分（主 plan + 子任务）
[x] 6.  Domain / UseCase 实现（单测过）
[x] 7.  Data / API 实现与联调
[ ] 8.  UI 骨架 + 静态设计走查
[ ] 9.  交互 + 全 Variant（空态 / 错误态）
[x] 10. 单元测试补充与回归（内层 TDD）
[ ] 11. 真机联调 + 集成设计走查
```

### 本轮执行顺序调整

WBS 编号保持兼容，但实施顺序调整为：UI Shell/入口先行 → 7d 本地模型 Runtime → 7e Agent 工具编排 → Domain/Data/文书工具接入 → 全状态与回归。UI 先行指可运行页面和状态容器，不等同于 Figma 像素级对稿；模型/Agent 先用 fake backend 固定契约，再接真实 GGUF。

---

## 八、10 周开发节奏映射

| 周期 | 工作流阶段 | 交付重点 |
|------|------------|----------|
| 第 1 周 | requirement | 律师访谈、6 字段原型、法条/案例初版、验收口径 |
| 第 2 周 | architecture / test-first | flutter_llama、docx_template、sqlite_vector 技术验证 |
| 第 3 周 | development | 赔偿金计算器：N/2N/双倍工资/加班费/年假 |
| 第 4 周 | development | RAG 引擎与知识库检索 |
| 第 5 周 | development | Agent 调度、意图识别、参数提取 |
| 第 6 周 | development | 评估报告生成与 UI 展示 |
| 第 7 周 | development | Word 文书生成、文件管理、分享 |
| 第 8 周 | test / review | 端到端测试、性能测试、真机验证 |
| 第 9-10 周 | release prep | 优化、商店素材、安装包、种子律师试用 |

---

## 九、变更日志

| 日期 | 变更类型 | 影响阶段 | 重开切片 | 确认人 | 说明 |
|------|----------|----------|----------|--------|------|
| 2026-08-04 | 创建 Epic | — | — | 用户 | 从 client-dev 母版实例化，补走开发工作流 |
| 2026-08-04 | 范围调整 | development | 8,9,11 | 用户 | 暂缓 Android、Figma/UI 视觉对稿；本轮以稳定 Key 驱动行为测试、业务回归和 iOS 集成为完成口径 |

---

## 续做

```text
/resume plan=Plans/Epic/2026-08-04-Flutter版劳动仲裁生成式智能助手App.md 进度=【派生阶段 / WBS 片号】
```

**编排**：自然语言「全流程开发」→ `workflow-router` → `client-dev`；或显式 `workflow=client-dev`  
**派生阶段**：`bash scripts/derive-epic-status.sh Plans/Epic/2026-08-04-Flutter版劳动仲裁生成式智能助手App.md`

```yaml
skill_run:
  skill: template-generator
  plan: Plans/Epic/2026-08-04-Flutter版劳动仲裁生成式智能助手App.md
  date: 2026-08-04
  utility: high
  reason: 用户要求补走开发工作流，Epic 是 client-dev 工作流看板和阶段门禁的入口。
  contexts_used:
    - path: Templates/Epic模板-client-dev.md
      utility: high
      reason: 用于实例化 client-dev Epic 的 frontmatter、WBS 与续做格式。
  contexts_missing: []
  contexts_stale: []
```

```yaml
skill_run:
  skill: resume-assistant
  plan: Plans/Epic/2026-08-04-Flutter版劳动仲裁生成式智能助手App.md
  date: 2026-08-04
  contexts_used:
    - path: Plans/自动化测试/2026-08-04-Flutter版劳动仲裁生成式智能助手App.md
      utility: high
      reason: 本次续做完成了 test-first 验收测试计划，并以该文件事实推进工作流到 split。
    - path: Plans/需求分析/2026-08-04-Flutter版劳动仲裁生成式智能助手App.md
      utility: high
      reason: 用于恢复 AC1-AC12、边界和异常流程，确认测试追溯范围。
    - path: Plans/技术方案/2026-08-04-Flutter版劳动仲裁生成式智能助手App.md
      utility: high
      reason: 用于恢复上次停点和测试类型、组件映射及移动端验收边界。
    - path: Contexts/决策/Skill反馈协议.md
      utility: high
      reason: 用于按协议追加本次续做的合法 skill_run 记录。
  contexts_missing: []
  contexts_stale: []
  outcome_status: pass
  revisit_needed: false
```

```yaml
skill_run:
  skill: resume-assistant
  plan: Plans/Epic/2026-08-04-Flutter版劳动仲裁生成式智能助手App.md
  date: 2026-08-04
  contexts_used:
    - path: Plans/功能开发/2026-08-04-Flutter版劳动仲裁生成式智能助手App.md
      utility: high
      reason: 用于恢复开发切片状态并继续 UI 自动化与真机验收收口。
    - path: Plans/功能开发/2026-08-04-Flutter版劳动仲裁生成式智能助手App-子任务05-移动端界面与全状态.md
      utility: high
      reason: 用于将关键 UI 行为定位从文案选择器升级为集中式稳定 Key。
    - path: Plans/功能开发/2026-08-04-Flutter版劳动仲裁生成式智能助手App-子任务07-真机集成验收.md
      utility: high
      reason: 用于复跑 iOS 模拟器的输入、评估、持久化、报告、历史和清理闭环。
    - path: Plans/自动化测试/2026-08-04-Flutter版劳动仲裁生成式智能助手App.md
      utility: high
      reason: 用于记录 ID 驱动 E2E 与截图视觉证据之间的职责边界。
    - path: Contexts/决策/Skill反馈协议.md
      utility: high
      reason: 用于按协议追加本次续做的合法 skill_run 记录。
  contexts_missing:
    - 正式 Figma 设计稿与 node-id。
    - Android SDK、AVD 或可用 Android 设备。
  contexts_stale: []
  outcome_status: partial
  friction: "iOS ID 驱动 E2E 已通过；Figma 视觉对稿与 Android 真机验收仍受外部环境阻塞。"
  revisit_needed: false
```

```yaml
skill_run:
  skill: resume-assistant
  plan: Plans/Epic/2026-08-04-Flutter版劳动仲裁生成式智能助手App.md
  date: 2026-08-04
  contexts_used:
    - path: Plans/功能开发/2026-08-04-Flutter版劳动仲裁生成式智能助手App.md
      utility: high
      reason: 用于按用户确认的范围继续业务自动化收口，并区分暂缓项与实际失败。
    - path: Plans/自动化测试/2026-08-04-Flutter版劳动仲裁生成式智能助手App.md
      utility: high
      reason: 用于确认 VM、Chrome、Web build 和 iOS integration_test 的最新回归事实。
    - path: Contexts/决策/Skill反馈协议.md
      utility: high
      reason: 用于按协议追加本次续做反馈。
  contexts_missing:
    - 正式 Figma 设计稿与 node-id（本轮暂缓）。
    - Android SDK、AVD 或可用 Android 设备（本轮暂缓）。
  contexts_stale: []
  outcome_status: pass
  friction: "本轮范围内无业务测试阻塞；平台与视觉项按用户确认延期。"
  revisit_needed: true
```
