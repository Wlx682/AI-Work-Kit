---
tags: [工作流, computer-mgmt]
type: plan
category: 电脑管理
status: 进行中
date: 2026-08-24
workflow: computer-mgmt
workflow_stage: inventory
task_id: computer-mgmt-2026-08-24-清理微信Cursor360Chrome缓存和Xcode-DerivedData
task_title: 清理微信Cursor360Chrome缓存和Xcode-DerivedData
skill: material-prep-assistant
---

# 盘点（磁盘/应用/启动项/大文件）：清理微信Cursor360Chrome缓存和Xcode-DerivedData

**工作流**：`computer-mgmt`
**阶段**：`inventory` / 盘点（磁盘/应用/启动项/大文件）
**推荐 Skill**：`material-prep-assistant`
**存放路径**：`Plans/电脑管理/2026-08-24-盘点-清理微信Cursor360Chrome缓存和Xcode-DerivedData.md`

---

## 一、输入

- 来源：用户明确要求删除微信、Cursor、360家、Xcode DerivedData，并删除 Chrome 超过 3 个月的缓存。
- 范围：仅处理下列固定目标：
  - `~/Library/Containers/com.tencent.xinWeChat`（清理前约 5.62 GiB）
  - `~/Library/Application Support/Cursor`（清理前约 5.36 GiB）
  - `~/Library/Application Support/360家`（清理前约 0.45 GiB）
  - `~/Library/Developer/Xcode/DerivedData`（清理前约 31.69 GiB）
  - Chrome 缓存目录内修改时间早于 `2026-05-24 00:00:00` 的普通文件（3,835 个，约 2.08 GiB）
- 非目标：Chrome 书签、密码、浏览历史、Cookies、扩展配置；Xcode 源码、模拟器和 DeviceSupport；其他微信、Cursor、360 相关目录。

## 二、阶段产出

- [x] 已完成清理前只读盘点、固定目标清单和 Chrome 过期缓存 dry-run。
- [x] 用户已在对话中逐项明确授权删除。
- [x] 清理前 Data 卷可用空间：74,223,476 KiB。
- [x] 已删除 Cursor、360家和 Xcode DerivedData 目标目录。
- [x] 微信容器主体数据已删除，仅保留 macOS 保护的容器元数据（36 KiB）。
- [x] Chrome 截止日期前缓存复核为 0 个文件、0 bytes。
- [x] 清理后 Data 卷可用空间：118,222,636 KiB；净释放 43,999,160 KiB（约 41.96 GiB / 45.05 GB）。

### 删除后差异

| 目标 | 清理前 | 清理后 |
|---|---:|---:|
| 微信容器 | 约 5.62 GiB | 36 KiB 系统元数据 |
| Cursor | 约 5.36 GiB | 目录不存在 |
| 360家 | 约 0.45 GiB | 目录不存在 |
| Xcode DerivedData | 约 31.69 GiB | 目录不存在 |
| Chrome 2026-05-24 前缓存 | 3,835 文件 / 约 2.08 GiB | 0 文件 / 0 bytes |


## 三、完成门禁

- `childPlanExists`: True
- `skillRun`: True

> 完成阶段工作后，在本 plan 末尾追加 `skill_run`，再运行 `bash scripts/workflow-gate.sh --workflow computer-mgmt --json`。

## 四、续做

```text
/resume plan=Plans/电脑管理/2026-08-24-盘点-清理微信Cursor360Chrome缓存和Xcode-DerivedData.md 进度=【当前完成情况】
```

## 反馈（skill_run）

```yaml
skill_run:
  skill: material-prep-assistant
  plan: Plans/电脑管理/2026-08-24-盘点-清理微信Cursor360Chrome缓存和Xcode-DerivedData.md
  date: 2026-08-24
  contexts_used:
    - path: Contexts/决策/Skill反馈协议.md
      utility: high
      reason: "用于按工作流要求记录盘点证据和阶段反馈"
  contexts_missing: []
  contexts_stale: []
  outcome_status: pass
  friction: "computer-mgmt 的推荐 Skill 偏向 PM 资料沉淀，且标题包含清理时 gate 将盘点 plan 同时识别为 cleanup plan"
  revisit_needed: false
```
