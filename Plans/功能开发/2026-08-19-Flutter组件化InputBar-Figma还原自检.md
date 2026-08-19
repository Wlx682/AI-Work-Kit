---
status: PARTIAL
date: 2026-08-19
feature_plan: Plans/功能开发/2026-08-18-Flutter组件化InputBar.md
figma_file: xpLHgvbfToG4QbQk43biAT
figma_node: 1:30792
---

# Flutter 组件化 InputBar — Figma 还原自检

## 基准

- Figma 状态：`1:31431` 默认、`1:31452` 聚焦空态、`1:31480` 多行、`1:31508` 长文本、`1:31546` 收起单行、`1:30958` 模型胶囊。
- iOS 行为：frozen `4d405cf0` 的 `NMInputBar.swift`、`NMNewTextInputComponent.swift`。
- Flutter 渲染预览：`/tmp/nami-inputbar-preview.png`（本机临时证据，未作为仓库资产提交）。

## 逐项自检

| 项 | 设计值 / 行为 | Flutter 结果 | 状态 |
|---|---|---|---|
| 主容器宽度 | 360 画板左右各 12，宽 336 | `horizontalInset: 12`，widget test 精确断言 336 | PASS |
| 默认高度 | Figma 59，iOS 60 | 60 | PASS |
| 聚焦空态高度 | 94 | 94（误差断言 ±1） | PASS |
| 圆角 | 20 | 20 | PASS |
| 阴影 | 两层 10% 黑，y=2/5、blur=10 | 两层 `BoxShadow`，真实渲染未裁切 | PASS |
| 正文 | 16，正文行高 25，占位 30% 黑 | 16/25，占位 30% 黑 | PASS |
| 内边距 | collapsed 左右 14；expanded top 16/bottom 13.5；row gap 10 | 一致 | PASS |
| 附件入口 | 32 frame，22 圆环；编辑态在下行左侧 | Figma SVG；位置一致；展开旋转为关闭态 | PASS |
| 发送入口 | 44×32，黑底；空态 30% | Figma SVG；启用/禁用一致 | PASS |
| 模型胶囊 | 高 36、圆角 12、1px 10% 黑边、14 medium | 一致 | PASS |
| 同一编辑器 | 状态变化不替换 SlateView | ChatPage 常驻同一个 TextInputComponent/TextField，AnimatedPositioned 只改约束 | PASS |
| @ / Slate | 聚焦和高度变化不能丢文档/引用 | Slate 与 @ 专项测试通过 | PASS |
| 附件联动 | 聚焦收起面板；点加号退出编辑再展开 | 中心状态合并；相等短路；专项测试通过 | PASS |
| 高度动效 | 从当前状态继续，避免硬跳 | 100ms easeInOutCubic；中间帧测试证明 60 < mid < 94 | PASS |
| 长文本 | 最高 200，出现展开入口 | 5 行/最高 200；复用 Slate 的全屏编辑页 | PASS |
| Android 真机 | Phone 实机对稿 | APK PASS，华为拼图阻塞安装 | NOT_RUN |
| iPhone 真机 | iPhone 实机对稿 | build PASS，既有未签名 framework 阻塞安装 | NOT_RUN |
| Pad/Fold/iPad | 三档自适应对稿 | 未执行里程碑矩阵 | NOT_RUN |

## 评分

| 维度 | 分数 |
|---|---:|
| 静态布局与尺寸 | 2.0 / 2.0 |
| 颜色、圆角、阴影、图标 | 1.9 / 2.0 |
| 状态与交互逻辑 | 2.0 / 2.0 |
| 高度动画与连续输入 | 1.9 / 2.0 |
| 真机与多形态证据 | 0.7 / 2.0 |
| **总分** | **8.5 / 10** |

当前结论为 `PARTIAL`：实现与自动化门禁通过，不能在缺少真机截图时声称 Figma 还原完成。解除条件是完成至少 Android Phone + iPhone 默认/聚焦/三行/附件展开四态对稿；Pad/Fold/iPad 留到功能链路里程碑矩阵。

## 回归证据补充

- InputBar、Slate、Chat 生产入口、导航、handoff 与 runtime adapter 合并回归：`127 tests passed`。
- Outbox history/stop authority 补充回归：`16 tests passed`。
- `flutter analyze`（InputBar、ChatPage 及对应测试）、`git diff --check`、task-ID naming gate：PASS。
- 文本变更先更新组件本地状态并触发一次 UI 刷新，再交由聚合状态分发；外部状态相等时短路，避免高度变化与父级重建互相回写形成死循环。
