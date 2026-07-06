---
tags: [决策, 协议, 漂移检测, 工作流]
date: 2026-06-24
status: 已采纳
relations:
  depends_on:
    - Contexts/决策/Kit核心原则.md
  dependents: []
  supersedes: []
  superseded_by: []
  conflicts: []
---

# Contexts 漂移检测协议

> 解决什么问题：**Contexts 文档与业务代码脱钩** —— 文档里"现网逻辑"过了三个月就和代码不一致，AI 调用 Contexts 时被误导。
> 自动机制：`scripts/drift-scan.py` 每周扫一次，对比 Contexts 内 `verified_against` 字段与业务仓 HEAD commit。

---

## 一、何时该写 `verified_against`

| 写 ✅ | 不写 ❌ |
|------|--------|
| Contexts 描述了**某业务仓**的现网行为（API、字段、流程）| 决策 / 原则 / 协议（与代码无关）|
| 设计规范引用了**代码层**约定 | 通用 Figma 规范、模板约定 |

判断：**Contexts 内容是否会因代码改动而过期？** 是 → 写 verified_against；否 → 跳过。

---

## 二、schema（frontmatter 字段）

### 形态 A：单仓引用

```yaml
---
tags: [...]
verified_against:
  repo: NamiWork
  commit: cf726179
  date: 2026-06-24
  note: "v1.1.0 上线版本"     # 可选
---
```

### 形态 B：多仓引用（同一份 Contexts 跨多仓库）

```yaml
---
tags: [...]
verified_against:
  - repo: NamiWork
    commit: cf726179
    date: 2026-06-24
  - repo: ClawAI
    commit: 90dc1ad4
    date: 2026-06-22
    note: "对照 cloud_drive 分支"
---
```

### 字段规则

| 字段 | 必填 | 说明 |
|------|------|------|
| `repo` | ✅ | identifier，必须与 `~/.config/aiworkkit/projects.list` 中某行 = 左侧值完全一致 |
| `commit` | ✅ | 短 SHA（7+ 字符）或完整 SHA。前缀匹配 |
| `date` | ✅ | YYYY-MM-DD，**人读用**，不影响漂移判定 |
| `note` | ⛔ | 备注，可省略 |

---

## 三、扫描与漂移判定

`scripts/drift-scan.py` 每次跑：

1. 加载 `~/.config/aiworkkit/projects.list` → `{identifier: path}`
2. 对每个仓 `git rev-parse HEAD` → `{identifier: current_sha}`
3. 遍历 `Contexts/**/*.md`，提取 `verified_against` 字段
4. 对每条记录：`recorded[:N] != current[:N]`（N = min 长度）→ **漂移**
5. 输出报告：`Contexts/决策/漂移报告-YYYY-WW.md`

### 漂移分级

| 类型 | 含义 | 行动 |
|------|------|------|
| **真漂移**（代码改了，文档没动）| 现网行为已变 | 更新 Contexts 内容 + 更新 verified_against |
| **假漂移**（文档已对齐，但 verified_against 未更新）| 内容已是最新，只是没刷 commit | 仅更新 verified_against 字段 |
| **无关漂移**（commit 改了但本 Contexts 描述的部分没变）| 误报 | 更新 verified_against 到当前 HEAD，加 note 备忘 |

报告中每条都需人工 review，不自动修。

---

## 四、运行节奏

| 模式 | 命令 |
|------|------|
| 手动（按需）| `python3 scripts/drift-scan.py` |
| 手动（预览）| `python3 scripts/drift-scan.py --dry-run` |
| 自动（周扫）| `cp scripts/com.aiworkkit.drift-scan.plist ~/Library/LaunchAgents/ && launchctl load ~/Library/LaunchAgents/com.aiworkkit.drift-scan.plist`（周日 10:07）|

报告产物纳入**月度复盘**审视一次（取本月所有周报告，归并决策）。

---

## 五、与其它协议关系

| 协议 | 关系 |
|------|------|
| [[Contexts/决策/Skill反馈协议]] | 反馈回路的 `contexts_stale` 字段是**人工标记**漂移；本协议是**自动检测**。两者互补 |
| [[Contexts/决策/Kit核心原则]] | 本协议是“反馈闭环原则”的延伸（被动 → 主动）|

---

## 六、首批应用建议（手动回填）

回填顺序按 ROI（频繁引用且与代码强耦合的优先）：

1. `Contexts/收银台/MSPay收银台配置对照表.md` —— 多仓（NamiWork、ClawAI）+ 接口字段高度依赖代码
2. `Contexts/Figma/项目设计规范.md` —— 引用代码层约定（颜色 token、组件命名等）
