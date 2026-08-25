---
tags: [自动化测试, 集成测试计划, client-dev]
type: plan
category: 自动化测试
status: 已采纳
date: 2026-08-19
lifecycle_state: integration-test-plan
epic: Plans/Epic/2026-08-19-Flutter-CloudFiles与文件预览依赖边界重构.md
story_index: Plans/功能开发/2026-08-19-Flutter-CloudFiles与文件预览依赖边界重构.stories.json
target_commit: working-tree@a77bf828a587c882c3376aa73d3ccba8138f3c87+snapshot:bf0d4e69586d5259dbf71fbed32f950398edf7fbc6700cf5faefe6049a07f4a6
test_case_index: Plans/自动化测试/2026-08-19-Flutter-CloudFiles与文件预览依赖边界重构-集成测试计划.cases.json
test_review: Plans/自动化测试/2026-08-19-Flutter-CloudFiles与文件预览依赖边界重构-集成测试计划.review.json
relations:
  depends_on:
    - Templates/模板约定.md
    - Templates/用户故事TDD模板.md
  dependents:
    - Templates/Epic模板-client-dev.md
  supersedes: []
  superseded_by: []
  conflicts: []

---
# 集成测试计划：Flutter-CloudFiles与文件预览依赖边界重构

## 一、测试策略

- 目标 commit：`working-tree@a77bf828a587c882c3376aa73d3ccba8138f3c87+snapshot:bf0d4e69586d5259dbf71fbed32f950398edf7fbc6700cf5faefe6049a07f4a6`
- 范围：US-CFR-001..007，AC-01..10；Feature/App 依赖、Runtime/owner、Provider 生命周期、Files Host 注入、四来源预览、上传/下载/分享、错误恢复、质量围栏和五类设备矩阵。
- 非目标：新增产品功能；改动 HTTP/Gateway 协议、签名、namespace、持久化、UI 或平台预览策略；Chat/Claw 全仓架构治理。
- 环境与测试数据：Flutter 聚焦测试环境；连接 iPhone 及 Android Phone/Pad/Fold、iPhone/iPad 实体形态；有效登录、CloudFiles/Gateway/签名环境；四来源多格式文件与权限/离线/迟到结果数据。
- 风险分级：P0 / P1 / P2

## 二、测试用例

> 用例的机械真理源为 `test_case_index` JSON。本表用于人工审核，必须与 JSON 一致。

| 用例 ID | 标题 | 关联 Story / AC | 优先级 | 类型 | 前置条件 | 测试数据 | 步骤 | 预期结果 | 自动化 |
|---------|------|-----------------|----------|------|----------|----------|------|----------|--------|
| IT-CFR-001 | Feature/App 边界、归属与命名门禁 | US-002/004/005/006/007 | P0 | architecture-boundary | 快照一致 | 生产目录/旧符号 | 边界测试+源码扫描+文档核对 | 禁止依赖为 0，实现归 Feature | automated |
| IT-CFR-002 | Runtime 投影与 owner 围栏 | US-001/003 | P0 | runtime-owner-isolation | 可编排 owner | A/B generation | 投影、换代、迟到返回 | 能力不泄漏，旧结果不覆盖 | automated |
| IT-CFR-003 | Provider 单例与单次释放 | US-001/006 | P0 | provider-lifecycle | ProviderObserver | 同 owner/换代 | 重复读取、dispose | identical，add/dispose 各一次 | automated |
| IT-CFR-004 | Files Host 注入与三类浏览 | US-004 | P0 | production-composition | 生产 Scope | AI/Workspace/云盘 | 入口、浏览、retry、owner 切换 | 只消费窄 slots，行为不变 | automated |
| IT-CFR-005 | 四来源多格式 FilePreview | US-005 | P0 | cross-source-preview | binding 已装配 | 文档/图片/媒体 | Planner→Coordinator→Launcher | 统一 Feature，UI/缓存/策略不变 | automated |
| IT-CFR-006 | 上传/下载/分享与恢复 | US-005/006 | P0 | transfer-recovery | 可注入外部 I/O | cancel/offline/denied | 传输、中断、owner 换代 | 协议不变且不伪成功 | automated |
| IT-CFR-007 | 静态质量与 impact 围栏 | US-006/007 | P1 | quality-gate | 快照一致 | 变更目录/registry | analyze+naming+diff+selector | 静态门禁绿，unresolved 有着落 | automated |
| IT-CFR-008 | 五类设备预览/传输矩阵 | US-001/003/004/005/006 | P0 | device-matrix | 五类设备+真实环境 | 四来源多格式 | 预览、传输、旋转/分屏/折叠、恢复 | 产品行为不变，owner/形态安全 | manual |

## 三、需求与用例覆盖

| Story | AC | 覆盖用例 | 优先级 | 结论 |
|-------|----|----------|----------|------|
| US-CFR-001 | AC-06, AC-08 | IT-CFR-002,003,008 | P0 | 已覆盖 |
| US-CFR-002 | AC-02 | IT-CFR-001 | P0 | 已覆盖 |
| US-CFR-003 | AC-03, AC-06 | IT-CFR-002,008 | P0 | 已覆盖 |
| US-CFR-004 | AC-01, AC-04 | IT-CFR-001,004,008 | P0 | 已覆盖 |
| US-CFR-005 | AC-05, AC-07 | IT-CFR-001,005,006,008 | P0 | 已覆盖 |
| US-CFR-006 | AC-07, AC-08, AC-09 | IT-CFR-001,003,006,007 | P0 | 已覆盖 |
| US-CFR-007 | AC-10 | IT-CFR-001,007 | P1 | 已覆盖 |

## 四、测试审核

- [x] Scope 内所有 Story / AC 均有用例覆盖
- [x] P0 / P1 核心路径、异常、边界和恢复场景已审核
- [x] 测试数据、环境、执行方式可复现
- [x] `test_review` 已记录审核人、时间、目标 commit 和用例索引 SHA-256
- [x] 未解决审核意见为 0

```text
python3 scripts/validate-client-dev.py test-plan --plan Plans/自动化测试/2026-08-19-Flutter-CloudFiles与文件预览依赖边界重构-集成测试计划.md
```

审核通过后将 `status` 改为「已采纳」，进入 `integration-test`。执行中若需新增或重大修改用例，必须回到本阶段重新审核。

```yaml
skill_run:
  skill: test-generator
  workflow_stage: integration-test-plan
  plan: Plans/自动化测试/2026-08-19-Flutter-CloudFiles与文件预览依赖边界重构-集成测试计划.md
  date: 2026-08-21
  contexts_used:
    - path: Plans/功能开发/2026-08-19-Flutter-CloudFiles与文件预览依赖边界重构.stories.json
      utility: high
      reason: "以 7 个 Scope Story 和 14 组 Story/AC 关系作为覆盖真理源"
    - path: Plans/功能开发/2026-08-19-Flutter-CloudFiles与文件预览依赖边界重构-US-CFR-007.tdd.json
      utility: high
      reason: "以最终边界、命名、iPhone smoke 和 NOT_RUN 设备围栏决定集成策略"
    - path: Plans/自动化测试/2026-08-19-Flutter-CloudFiles与文件预览依赖边界重构-集成测试计划.cases.json
      utility: high
      reason: "8 条结构化用例覆盖主路径、反例、恢复、质量门禁和设备矩阵"
  contexts_missing: []
  contexts_stale: []
  outcome_status: pass
  friction: "当前是未提交工作树，使用 base SHA + 受控工作树 snapshot hash 冻结候选；设备矩阵保持 manual"
  revisit_needed: false
```
