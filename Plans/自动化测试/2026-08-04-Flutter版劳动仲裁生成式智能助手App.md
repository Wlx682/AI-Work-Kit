---
tags: [测试, 自动化测试, Flutter, client-dev]
type: plan
category: 自动化测试
status: 已采纳
date: 2026-08-04
lifecycle_state: test
epic: Plans/Epic/2026-08-04-Flutter版劳动仲裁生成式智能助手App.md
requirement: Plans/需求分析/2026-08-04-Flutter版劳动仲裁生成式智能助手App.md
architecture: Plans/技术方案/2026-08-04-Flutter版劳动仲裁生成式智能助手App.md
repo: labor_assistant
wbs:
  "4": done
---

# 自动化测试：Flutter版劳动仲裁生成式智能助手App

**创建日期**：2026-08-04  
**存放路径**：`Plans/自动化测试/2026-08-04-Flutter版劳动仲裁生成式智能助手App.md`  
**状态**：已采纳  
**lifecycle_state**：test（兼容展示，实际阶段由 `workflow-gate.sh` 派生）  
**关联需求（真理源）**：`Plans/需求分析/2026-08-04-Flutter版劳动仲裁生成式智能助手App.md`  
**关联技术方案**：`Plans/技术方案/2026-08-04-Flutter版劳动仲裁生成式智能助手App.md`  
**关联功能开发**：`Plans/功能开发/2026-08-04-Flutter版劳动仲裁生成式智能助手App.md`（含新增 7d/7e 模型与 Agent 子任务）  
**业务仓库**：`/Users/wanglongxiang/git/labor_assistant`

---

## 一、测试范围

本 Plan 是外层 TDD 验收契约。现有 6 条测试作为可运行基线保留；尚未实现的验收项标记为 **Red**，必须先补测试并观察其因缺少业务能力而失败，再由开发切片逐项转绿。真实 GGUF、系统分享和移动端文件权限不阻塞确定性 P0，但必须进入真机清单。

### 1.2 本轮范围调整（用户确认）

- 本轮继续收口 Domain、Data、RAG、文书、持久化和 iOS/Widget/Chrome 行为自动化。
- Android SDK/AVD 与 Android 真机回归暂缓，不作为当前行为闭环的阻塞项。
- 正式 Figma 节点、像素级 UI 对稿和截图评分暂缓；截图仅作视觉证据，不替代 `flutter_test` / `integration_test`。

| 层级 | 覆盖模块 | 工具/框架 |
|------|----------|-----------|
| 单元测试 | `CompensationCalculator`、`AgentEngine`、`LawRetriever`、输入校验 | `flutter_test` |
| 集成测试 | `EvaluateLaborCaseWorkflow`、`TemplateFiller`、知识库兜底、模型降级、本地持久化 | `flutter_test` + 临时目录/内存仓储 |
| Widget 测试 | 案情输入、报告合规文案、设置页隐私与清理确认 | `flutter_test` + `ProviderScope` |
| E2E / 真机 | 文书保存、系统分享取消、iOS/Android 权限、模型加载失败降级 | Flutter `integration_test` + 集中式 `AppTestIds` / `find.byKey` + iOS/Android 真机；截图仅作视觉证据 |

### 1.1 当前基线

- `flutter analyze`：通过，无静态检查问题。
- `flutter test --coverage`：6 条测试通过；行覆盖率 82.8%（471/569），覆盖率不等于 AC 完成率。
- `flutter test --platform chrome`：6 条测试通过；Web 仅作开发验证，不替代移动端验收。
- 已有测试覆盖：N/2N、双倍工资 11 个月上限、加班倍率、案情描述工资/未签合同提取、两类 docx 基础生成、主导航 smoke。
- 关键缺口：非法日期/工资、缺字段阻断、协商解除适用项、法条 Top-K/兜底、docx 内容与 fallback、模型降级提示、支持率免责声明、数据清理与持久化。
- 生成式增强新增测试缺口：Runtime 生命周期、真实本地 JSON 提取、Prompt/Schema 版本、缺字段追问、工具调用边界、非法输出和 Agent trace 回放。

---

## 二、用例映射（链需求验收标准）

| 验收项 # | 测试用例 ID | 类型 | 描述 | 首轮状态 |
|----------|-------------|------|------|----------|
| AC1 | WT-001 | Widget/性能 | 完整 6 字段点击评估后 30 秒内展示金额、法条、可行性和报价 | Green：计时、保存与四区报告断言通过 |
| AC2 | UT-001 | 单元 | 月薪 8000、工作 6 年、违法辞退得到 N=48000、2N=96000，双倍工资按规则计算 | Green |
| AC3 | UT-002 | 单元 | 协商解除只把 N/N+1 标为适用，不把 2N 标为适用 | Green |
| AC4 | WT-002 | Widget | 工资缺失或非法时提示字段错误，且不生成精确金额 | Green |
| AC5 | UT-003 / IT-001 | 单元/集成 | 违法辞退引用第 87 条，未签合同引用第 82 条，引用含法名、条号、原文 | Green |
| AC6 | IT-002 | 集成 | 仲裁申请书 docx 大于 1KB，解包后包含申请人、被申请人、事实理由、金额、法条 | Green |
| AC7 | IT-003 | 集成 | 证据清单按合同状态动态包含或排除“未签合同证明” | Green |
| AC8 | IT-004 | 集成 | 模板读取/`docx_template` 失败时仍生成合法最小 docx | Green |
| AC9 | IT-005 / WT-003 | 集成/Widget | 本地模型未加载或加载失败时仍生成确定性报告，并显示降级提示 | Green |
| AC10 | WT-004 | Widget | 判例支持率旁明确显示“参考/非胜诉承诺” | Green |
| AC11 | E2E-001 | E2E | 清理本地数据必须二次确认；确认后历史、报告和缓存不可见 | Green：仓储集成 + Widget 确认链；真机清理待 WBS 11 |
| AC12 | UT-004～UT-009 | 单元 | 非法日期、0/负工资、不满 6 个月、6～12 个月、未签不足 1 月、双倍工资 11 月上限 | Green |

> 状态定义：Green = 当前已有可验证断言；Partial = 只覆盖验收项的一部分；Red = 下一开发阶段必须先落测试并确认失败原因仅为能力未实现。

---

## 三、单元测试清单

| ID | 被测单元 | 输入 | 期望 | 文件路径（代码库） |
|----|----------|------|------|-------------------|
| UT-001 | `CompensationCalculator.calculate` | 8000 元、72 个月、违法辞退、未签合同 | N=48000、2N=96000、双倍工资差额=88000 | `test/compensation_calculator_test.dart` |
| UT-002 | `CompensationBreakdown.claims` | 协商解除 | N/N+1 `isApplicable=true`，2N `isApplicable=false` | `test/compensation_calculator_test.dart` |
| UT-003 | `LawRetriever.retrieveForCase` | 违法辞退、未签合同、加班 | 含 47/82/87/44/仲裁时效，最多 5 条且字段完整 | `test/law_retriever_test.dart` |
| UT-004 | 输入校验 | `endDate <= startDate` | 返回日期字段错误，不产出报告 | `test/labor_case_validation_test.dart` |
| UT-005 | 输入校验 | 工资为 0、负数、非数字 | 返回工资字段错误，不产出报告 | `test/labor_case_validation_test.dart` |
| UT-006 | `calculateCompensationMonths` | 工作不足 6 个月 | 补偿月数为 0.5 | `test/compensation_calculator_test.dart` |
| UT-007 | `calculateCompensationMonths` | 工作满 6 个月不足 1 年 | 补偿月数为 1 | `test/compensation_calculator_test.dart` |
| UT-008 | `calculateDoubleSalaryDifference` | 未签合同且工作不足/等于 1 个月 | 双倍工资差额为 0 | `test/compensation_calculator_test.dart` |
| UT-009 | `calculateDoubleSalaryDifference` | 未签合同且工作超过 12 个月 | 计薪月数封顶 11 个月 | `test/compensation_calculator_test.dart` |
| UT-010 | `AgentEngine.runFromDescription` | 缺工资、含违法辞退文本 | 返回缺字段结果，不使用 demo 工资生成金额 | `test/agent_engine_test.dart` |
| UT-011 | Agent 确定性工具 | 完整案件、序列化案件、缺少 caseInput | 赔偿/法条/评估/文书工具复用确定性工作流；缺参显式失败 | `test/agent_tools_test.dart` |

---

## 四、集成测试清单

| ID | 场景 | 依赖 | Mock 策略 | 期望 |
|----|------|------|-----------|------|
| IT-001 | 评估工作流检索法律依据 | `EvaluateLaborCaseWorkflow` + `LawRetriever` | 使用内置法条数据，不访问网络 | 引用来源、条号、原文齐全，违法辞退/未签合同命中正确条文 |
| IT-002 | 生成仲裁申请书 | `TemplateFiller` + 模板 asset | 解包返回 bytes 检查 `word/document.xml` | 文件大于 1KB，核心字段全部出现 |
| IT-003 | 生成证据清单 | `TemplateFiller` + 两种合同状态 | 解包返回 bytes 检查文本 | 未签时包含对应证据项，已签时排除该项 |
| IT-004 | 文书模板失败兜底 | `TemplateFiller` | 注入缺失/损坏模板加载器或强制 fallback | 返回合法 docx，不静默失败 |
| IT-005 | 模型不可用降级 | `AgentEngine` + `LlmClient` | 注入 `notInstalled` / `loadFailed` fake | 确定性计算、法条和报告继续可用，暴露降级状态 |
| IT-006 | 知识库未初始化 | RAG repository + 内置法条兜底 | 注入空索引/初始化失败 fake | 仍返回内置法条并提示索引待初始化 |
| IT-007 | 本地保存与清理 | Case/Report/Document repositories | 使用临时 SQLite/Hive 目录 | 保存后可重启读取；清理后记录和缓存为空 |
| IT-008 | 本地模型 Runtime 生命周期 | `LocalLlmService` + `LlmClient` | 注入 fake GGUF backend，不下载真实权重 | missing/loading/ready/loadFailed/timeout/unload 状态可观察；失败释放资源并回落确定性链路 |
| IT-009 | Agent 结构化参数提取 | `AgentEngine` + Prompt/JSON Schema | 注入可控 fake LLM JSON/非法 JSON | 字段值、置信度、缺失字段和来源 trace 可复现；非法 JSON 进入 fallback |
| IT-010 | Agent 追问与工具编排 | Agent tool registry + `EvaluateLaborCaseWorkflow` | fake LLM 依次返回缺字段、工具调用和完成结果 | 有最大追问轮数/超时/取消；金额只来自计算器，法条只来自检索器，步骤 trace 完整 |
| IT-011 | Agent 确定性业务工具 | Agent tool registry + `EvaluateLaborCaseWorkflow` + `TemplateFiller` | 传入 fake/序列化案件参数，不访问网络 | 赔偿、法条、评估和文书字节工具只能消费校验后的案件；输出金额/法条/文书元数据，非法参数显式失败 |

---

## 五、Widget / E2E 与真机清单

| ID | 平台 | 场景 | 期望 |
|----|------|------|------|
| WT-001 | Widget | 完整填写并运行评估 | 30 秒内出现报告四个核心区块 |
| WT-002 | Widget | 工资为空、0、负数 | 显示字段错误，报告总额不更新 |
| WT-003 | Widget | 模型不可用 | 显示“确定性报告/模型不可用”提示，基础功能仍可操作 |
| WT-004 | Widget | 查看类似判例支持率 | 同屏显示“本地判例参考/非胜诉承诺” |
| WT-005 | Widget | 打开设置页 | 明确显示“默认本地保存、不上传云端” |
| E2E-001 | iOS/Android | 清理本地数据 | 二次确认后历史、报告、文书索引和缓存不可见 |
| E2E-002 | iOS/Android | 生成并保存两类文书 | 文件保存到 App 私有目录，可由系统打开 |
| E2E-003 | iOS/Android | 打开分享面板后取消 | 本地文书仍存在，不显示生成失败 |
| E2E-004 | 低内存 Android/iPhone | 模型加载失败 | 自动释放资源，确定性评估与文书仍可用 |

### 5.1 生成式增强验收清单

| ID | 阶段 | 场景 | 期望 |
|----|------|------|------|
| GEN-001 | Runtime | 本地 GGUF 路径存在且加载成功 | `ModelRuntimeStatus.ready`，可完成 schema 约束的本地 JSON 提取 |
| GEN-002 | Runtime | 模型缺失、加载失败、推理超时或内存不足 | 状态可诊断、资源释放、确定性评估/法条/文书仍可用 |
| GEN-003 | Agent | 案情缺少工资/日期等关键字段 | 追问或返回结构化缺失字段，不生成精确金额 |
| GEN-004 | Agent | 模型请求计算、法条检索、文书生成工具 | 工具结果是唯一权威；模型不能覆盖金额、法条或核心事实 |
| GEN-005 | Agent | 非法 JSON、工具异常、达到追问上限、用户取消 | 返回可解释 fallback 和完整步骤 trace，不静默成功 |

---

## 六、Red → Green 实施顺序

1. 先补 UT-002～UT-010、IT-001～IT-006、WT-001～WT-005；测试应能编译运行，失败原因必须指向尚未实现的契约，不得因测试夹具或平台环境误红。
2. Domain / UseCase 切片将计算边界、输入校验、模型降级状态与法条契约转绿。
3. Data 切片补 IT-007 和 E2E-001 所需 SQLite/Hive 仓储，再实现清理闭环。
4. UI 切片补缺字段、降级提示、非承诺文案和二次确认。
5. 文书切片开放模板加载/fallback 注入点，使 IT-002～IT-004 可稳定验证。
6. 模型 Runtime 切片先用 fake backend 转绿 IT-008，再在可用设备上验证真实 GGUF 生命周期。
7. Agent 增强切片转绿 IT-009/IT-010 与 GEN-001～GEN-005；先固定工具权威边界，再接 UI 状态。
8. 最后在 iOS/Android 真机执行 E2E-001～E2E-004；Web 通过不得替代真机结论。

### 6.1 开发先行顺序

1. UI Shell 先用 fake Provider 和 `AppTestIds` 生成可运行页面，先确认入口、导航和状态容器。
2. 模型 Runtime 先用 fake backend 验证生命周期，再接真实 GGUF；Agent 先固定 Prompt/Schema/工具契约，再联调真实推理。
3. Domain/Data/文书工具接入 Agent，保持金额、法条和文书事实的确定性权威。
4. 全状态、性能和 iOS 集成回归；Android 与视觉像素对稿按本轮范围暂缓。

---

## 七、CI 命令与门槛

```bash
cd /Users/wanglongxiang/git/labor_assistant
flutter pub get
flutter analyze
flutter test --coverage
flutter test --platform chrome
flutter build web
```

| 门槛 | 值 |
|------|-----|
| P0 自动化测试通过率 | 100% |
| P1 可自动化测试通过率 | 100%；真机能力可在 E2E 清单单列 |
| 行覆盖率 | 不低于当前 82.8%，且新增核心 Domain/Data 代码有对应测试 |
| AC 追溯 | AC1-AC12 均至少映射 1 个测试 ID |
| 隐私边界 | 测试及应用运行不得访问云端案情/模型 API |

---

## 八、执行记录

| 日期 | 分支/Commit | 结果 | 备注 |
|------|-------------|------|------|
| 2026-08-04 | `main@54958b7` | baseline pass | `flutter analyze`、`flutter test --coverage`、Chrome 测试通过；6 tests，82.8% 行覆盖率 |
| 2026-08-04 | `main@54958b7` | acceptance red planned | AC1-AC12 已映射；Partial/Red 项进入下一阶段原子任务拆分，不把基线绿灯视为验收完成 |
| 2026-08-04 | working tree | pass | VM 31 tests、Chrome 27 tests、Web build 通过；覆盖率 90.1%（842/935） |
| 2026-08-04 | working tree / WBS 7d-7e | pass | VM 41 tests、Chrome 36 tests、Web build 通过；覆盖率 89.5%（986/1102）；Runtime 生命周期、Agent 结构化提取、追问、工具失败和 AgentEngine 增强入口通过 |
| 2026-08-04 | working tree / WBS 7e | pass | VM 44 tests、Chrome 40 tests、Web build 通过；覆盖率 89.6%（1069/1193）；新增 `evaluate_case` 确定性工具、序列化输入、参数失败和编排注入测试通过 |
| 2026-08-04 | working tree / WBS 7e tools | pass | VM 46 tests、Chrome 42 tests、Web build 通过；覆盖率 89.6%（1119/1249）；赔偿、法条、评估、文书字节四个 Agent 工具及边界测试通过 |
| 2026-08-04 | working tree / WBS 7e final | pass | VM 47 tests、Chrome 43 tests、Web build 通过；覆盖率 89.7%（1121/1250）；四个确定性工具、版本化 JSON Schema、fallback 和 trace 全部通过 |
| 2026-08-04 | working tree / iOS 18.5 | pass | iPhone 16 Pro 模拟器 ID 驱动 E2E 通过：按 Key 填写真实输入、评估、Hive 持久化、报告四区块、历史、二次确认清理；点击未命中设为 fatal |
| 2026-08-04 | Android | deferred | 按用户确认暂不纳入本轮；本机仍无 Android SDK/AVD，后续补做 |

---

## 九、WBS 状态

```text
[x] 4. 验收测试先行（外层 TDD）：AC1-AC12 已映射，Red/Green 基线和 CI 门槛已定义
```

---

## 续做

```text
/resume plan=Plans/Epic/2026-08-04-Flutter版劳动仲裁生成式智能助手App.md 进度=split
```

**下一阶段 Skill**：`task-splitter`（生成开发主 plan 与原子子任务）

---

## 反馈（skill_run）

```yaml
skill_run:
  skill: test-generator
  plan: Plans/自动化测试/2026-08-04-Flutter版劳动仲裁生成式智能助手App.md
  date: 2026-08-04
  contexts_used:
    - path: Plans/需求分析/2026-08-04-Flutter版劳动仲裁生成式智能助手App.md
      utility: high
      reason: 作为 AC1-AC12、GWT、边界情况与异常流程的测试真理源。
    - path: Plans/技术方案/2026-08-04-Flutter版劳动仲裁生成式智能助手App.md
      utility: high
      reason: 用于把每条 AC 落到具体架构组件、测试类型和移动端验收边界。
    - path: Templates/自动化测试模板.md
      utility: high
      reason: 用于组织测试范围、AC 映射、UT/IT 清单、CI 命令和执行记录。
    - path: Contexts/决策/Skill反馈协议.md
      utility: high
      reason: 用于生成合法的 fenced skill_run 反馈并满足工作流机械门禁。
  contexts_missing: []
  contexts_stale: []
  outcome_status: pass
  friction: "功能开发 plan 尚未创建；测试计划依据已采纳需求、技术方案和当前代码基线先行建立。"
  revisit_needed: false
```

```yaml
skill_run:
  skill: test-generator
  plan: Plans/自动化测试/2026-08-04-Flutter版劳动仲裁生成式智能助手App.md
  date: 2026-08-04
  contexts_used:
    - path: Plans/需求分析/2026-08-04-Flutter版劳动仲裁生成式智能助手App.md
      utility: high
      reason: 用于逐项复核 AC1-AC12 的自动化覆盖与移动端保留项。
    - path: Plans/功能开发/2026-08-04-Flutter版劳动仲裁生成式智能助手App.md
      utility: high
      reason: 用于核对 Domain、Data、文书、UI 交互的实际交付和依赖。
    - path: Contexts/决策/Skill反馈协议.md
      utility: high
      reason: 用于追加合法的回归 skill_run 记录。
  contexts_missing: []
  contexts_stale: []
  outcome_status: pass
  friction: "文件系统/Hive 测试需标注 VM-only；Chrome 保留 27 项跨平台测试。"
  revisit_needed: false
```
