---
tags: [工作流, bugfix]
type: plan
category: Bug排查
status: 已完成
date: 2026-08-18
workflow: bugfix
workflow_stage: implementation-design
task_id: bugfix-2026-08-18-Android-PPT-应用内预览
task_title: Android PPT 应用内预览
skill: feature-dev-assistant
implementation_design: Plans/Bug排查/2026-08-18-Android-PPT-应用内预览-implementation-design.json
---

# 复现与影响范围：Android PPT 应用内预览

**工作流**：`bugfix`
**阶段**：`reproduce` / 复现与影响范围
**推荐 Skill**：`feature-dev-assistant`
**存放路径**：`Plans/Bug排查/2026-08-18-复现-Android-PPT-应用内预览.md`

---

## 一、输入

- 来源：Android 点击 PPTX 后由 `systemDocument -> OpenFilex` 交给外部 App，与用户“应用内预览”的最新裁决冲突。
- 范围：Android PPTX 使用离线、无网络权限的应用内 renderer；iOS Quick Look 保持不变；外部 App 仅作显式用户动作。
- 非目标：不实现 legacy `.ppt`，不把 PPTX 上传第三方在线服务，不改动 Word/Excel/PDF 的 renderer 选型。

## 二、阶段产出

- [x] 根因已确认：Android 生产 Composition 把 Office 绑定到 `OpenFilexNamiDocumentPreviewPlatform`。
- [x] 用户已确认允许内置 `@aiden0z/pptx-renderer 1.2.4` 生产运行时。
- [x] 修复落点见 `implementation_design`。

## 修复落点设计

- Core Planner 新增独立 PPTX 应用内 destination，不再借用 `systemDocument` 表示两种完全不同的交互。
- `nami_document_preview` 只暴露 typed PPTX renderer，内部负责离线 WebView、ZIP 资源限额、禁网和错误转换。
- App Coordinator 只持有 artifact lease 并调用 presenter，不直接依赖 JS/WebView 实现。

```yaml
skill_run:
  skill: implementation-design-assistant
  workflow_stage: implementation-design
  result: pass
  date: 2026-08-18
```


## 三、完成门禁

- `childPlanExists`: True
- `skillRun`: True

> 完成阶段工作后，在本 plan 末尾追加 `skill_run`，再运行 `bash scripts/workflow-gate.sh --workflow bugfix --json`。

## 四、续做

```text
/resume plan=Plans/Bug排查/2026-08-18-复现-Android-PPT-应用内预览.md 进度=【当前完成情况】
```

## 五、修复与验证

- Android 生产 Composition 只对 `.pptx` 注册应用内 presenter；iOS 继续 Quick Look，旧 `.ppt` 继续系统兜底。
- 预览页先进入，再异步等待本地 artifact；Coordinator 在页面关闭前持有 lease。
- `nami_document_preview` 内置 `@aiden0z/pptx-renderer 1.2.4`，以断网 CSP 的本地 WebView 加载；Android `file:` origin 使用固定 IIFE 产物，不再动态导入 ES Module。
- 文件按 48 MiB 默认上限流式读取，renderer 同时限制 ZIP entry、单 entry、总解压量与媒体量；禁止网络请求和外部页面跳转。
- Red：真机首转报 `pptx_reader_runtime_unavailable`，证实 Android WebView 的本地 ES Module 导入不可用。
- Green：插件全量 76 项测试通过；Core/Coordinator/Page 目标 66 项测试通过；Android 12 真机 `JTK5T19C18009054` 使用真实 `sample.pptx` 应用内渲染通过。
- 全仓 `flutter analyze` 被既有 `test/app/payment_membership_provider_test.dart` 对已迁移 `personal_cloud` 文件的 6 个旧引用阻断；本次目标 analyze 为 0 issue。
- 生产 `flutter build apk --debug` 两次均长时间等待 Gradle 远程依赖下载，人工中断；插件真机集成 APK 已成功构建、安装和运行。

```yaml
skill_run:
  skill: feature-dev-assistant
  workflow_stage: fix
  result: pass
  date: 2026-08-18
  tdd: red-green-refactor
  device: Android-12-JTK5T19C18009054
  revisit_needed: false
```
