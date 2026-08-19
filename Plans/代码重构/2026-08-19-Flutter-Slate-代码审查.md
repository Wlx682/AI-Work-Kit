---
tags: [代码审查, Flutter, InputBar, Slate]
date: 2026-08-19
status: 通过
commit: c26d3adc
---

# Code Review：Flutter Slate 单 TextView 实现

## Findings

### 已关闭（原高）：异步 mention picker 返回后可能写入错误文档或直接抛 RangeError

- 位置：`lib/features/chat/presentation/input_bar/slate/nami_slate_text_view.dart:147-157`
- `_openMentionPicker` 只保存旧 `request.range`，回调返回时直接操作 `widget.controller`。等待期间若外部状态清空/替换文档，或 Widget 换成另一个 controller，旧 range 会作用到新文档：越界时抛 `RangeError`，未越界时会静默替换错误文本。
- 建议：请求携带 controller/document revision；回调后同时校验 controller identity、document revision 和 reference identity，不匹配则丢弃迟到结果。
- 关闭证据：`c26d3adc` 为 request 增加 document revision，异步返回后同时校验 controller identity/revision；外部 `applyDocument`、controller replacement 和 picker 打开期间的最新请求排队均有 Widget 回归。

### 已关闭（原高）：原子 inline reference 的选区与命中体验不完整

- 位置：`lib/features/chat/presentation/input_bar/slate/nami_slate_editing_controller.dart:258-296`、`nami_slate_text_view.dart:161-166`
- mention/file 仅渲染为蓝色粗体 `@name`。光标仍可进入文本内部；复制粘贴会退化为普通文本；点击 mention 末尾后的插入点也会因为 `offset - 1` 被误判为点击 mention，弹出重选器。
- 现有原子删除只保护了文本 delta，尚未覆盖边界点击、剪贴板和结构化粘贴。
- 建议：单 TextField 方向不变，但需要显式的 inline range selection policy、命中测试和结构化 clipboard policy；至少先修复 mention 末尾误触。
- 关闭证据：collapsed selection 落入 reference 时按最近首尾吸附，非 collapsed selection 会扩展到完整 reference；点击使用吸附前真实 offset，reference 末尾不再通过 `offset - 1` 误触。
- 剪贴板裁决：固定 iOS `NMCustomYYTextView.paste` 读取 `UIPasteboard.general.string` 并调用系统粘贴，没有 Slate 私有结构协议；Flutter 同样按纯文本跨剪贴板互操作，不额外引入不可跨端的私有格式。

### 已关闭（原中）：多 paragraph 的 display/prompt 与固定 iOS 实现不一致

- 位置：`lib/features/chat/presentation/input_bar/domain/nami_slate_document.dart:312-316,366-383,598-618`
- Flutter 在 paragraph 之间自动插入 `\n`，并把 plain text 的换行拆成多个 paragraph；固定 iOS 的 `NMDocumentManager.getDisplayText`、`NMSlatePromptTools` 和 renderer 都是直接拼接 paragraph children，不自动插入换行。
- 当前测试只覆盖“单 paragraph 内含 `\n`”，没有覆盖两个顶层 paragraph，因此未发现跨端 prompt 差异。
- 建议：先确认 Web/后端期望；若要求完全对齐 iOS，应去掉隐式 paragraph 换行并补双端 fixture；若 Flutter 行为是刻意修正，需要记录 ADR 和兼容迁移。
- 关闭证据：display/prompt/reference offset/renderer 均移除顶层 paragraph 隐式换行；plain text 中的真实 `\n` 仍保留在同一 paragraph，双 paragraph fixture 已补齐。

### 已关闭（原中）：字符上限与组合字符边界未完全对齐 iOS

- 位置：`lib/features/chat/presentation/input_bar/slate/nami_slate_text_view.dart:125-145`、`nami_slate_editing_controller.dart:83-95`
- Flutter 使用 `runes.length`，iOS Swift `String.count` 按扩展字素簇计数；ZWJ emoji、组合音标会得到不同的 50000 字判断。
- iOS 文档操作会将 range 规范化到 composed character sequence；Flutter 的公开 `replaceTextInRange` 只扩展 reference range，外部传入半个组合字符边界时可能拆坏文本。
- 建议：统一 grapheme 计数工具，并在公开 range API 入口做字素边界归一化。
- 关闭证据：字符上限改按 extended grapheme cluster 计数；公开 range、IME delta 均避免拆分 ZWJ emoji 等组合字符。

## 摘要

- 架构方向正确：单一 Flutter `TextField` 足够，不需要迁 YY/Native/Porton renderer、PlatformView 或异步 synchronizer 队列。
- `c26d3adc` 已关闭迟到回调、controller replacement、最新 picker 排队、reference 选区/边界命中、双 paragraph 显示及编辑后 block 保留、grapheme 场景；InputBar 目录 42 条测试和 scoped analyze 通过。
- 结论：**通过**。Flutter 仍只使用一个 `TextField`，不需要 PlatformView、多 renderer/adapter 或全局 runtime provider。

## 测试缺口

- widget dispose 期间 picker 返回由 `mounted` 防护，但尚未单列 dispose 回归。
- undo/redo 仍委托 Flutter `EditableText`；跨 App 剪贴板按固定 iOS 的纯文本策略，不保留 reference 结构。
- Android/iOS 真机 IME 与选择菜单矩阵仍为 `NOT_RUN`，在 InputBar 功能链路里程碑统一执行。

## 反馈（skill_run）

```yaml
skill_run:
  skill: code-review
  plan: Plans/代码重构/2026-08-19-Flutter-Slate-代码审查.md
  date: 2026-08-19
  contexts_used:
    - path: Templates/Code-Review模板.md
      utility: high
      reason: "按 Findings-first、严重级、位置和结论组织审查产物"
    - path: Plans/功能开发/2026-08-18-Flutter组件化InputBar-US-IB-001.md
      utility: high
      reason: "对照完整迁移声明、AC 和 TDD 证据识别未覆盖边界"
    - path: Contexts/决策/2026-08-19-开发流程审计报告.md
      utility: high
      reason: "防止再次把最小投影能力直接等同于完整 Slate 编辑器"
  contexts_missing:
    - "iOS 与 Flutter Slate 多 paragraph、clipboard、grapheme 的共享兼容 fixture"
  contexts_stale:
    - path: Plans/功能开发/2026-08-18-Flutter组件化InputBar-US-IB-001.md
      reason: "已完成声明未包含异步 picker owner 校验、inline 边界与多 paragraph 兼容缺口"
  outcome_status: pass
  revisit_needed: false
  outcome: "c26d3adc 已关闭全部代码级 finding；剩余真机矩阵按 Epic 里程碑统一执行"
```
