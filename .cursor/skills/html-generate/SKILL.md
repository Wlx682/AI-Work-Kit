---
name: html-generate
description: >-
  把一篇技术正文生成炫酷、专业、有科技感的自渲染 `.html` 网页。核心是「内容→骨架」选择器：按正文形态自动挑布局骨架（侧栏文档/指标看板/新旧对比/流程时间线），也支持用户一句话指定。内嵌 mermaid.js 自渲染、渐进增强、流式栅格适配，产完必过本地浏览器自检。遵 [[Contexts/规范/炫酷建站规范]]，纳米Work 只上传 CDN 出短链。
  触发词：生成网页、做成网页、出 HTML、技术文档网页、把这篇做成页面、换个骨架、换个风格、/html、/html-generate。
  不响应：找外部文章→weekly-intel-digest；提效案例→best-practice-digest（二者产网页时内部引用本 Skill）。
---

# HTML 生成助手

知识库：`/Users/wanglongxiang/git/AI-Work-Kit`
原则：[[Contexts/决策/Kit核心原则]] · 建站硬标准：[[Contexts/规范/炫酷建站规范]] · 全文：`Skills/html_generate.md`

## 定位

把「一篇技术正文」变成「炫酷专业的自渲染网页」。技术文档偏多，**骨架要多、要不一样**（换布局结构，不是换配色）。维护骨架库 + 内容→骨架选择器：读正文形态自动挑骨架，也接受用户指定。炫酷标准/技术基线/自检清单全部沿用 [[Contexts/规范/炫酷建站规范]]。

## 骨架库（Contexts/规范/html模版/samples/）

| 骨架 | 文件 | 最适合 |
|------|------|--------|
| A 单栏叙事式 | `A-single-scroll.html` | 保底通用款：无明显结构特征的通用长文 |
| B 侧栏文档式 | `B-sidebar-docs.html` | 章节多、需导航的长篇技术文档/架构说明 |
| C 指标看板式 | `C-metrics-dashboard.html` | 有基线/提升幅度的提效数据、性能报告 |
| D 新旧对比式 | `D-before-after.html` | 方案演进、迁移、before/after |
| E 流程时间线式 | `E-timeline.html` | 实施步骤、上线手册、复盘时序 |

## 内容→骨架选择器（自动选 · 可覆盖）

默认读正文自动挑骨架并一句话说明「选了哪种·理由」，用户可当场改；用户显式指定 > 自动判据，无条件服从。判据：量化提升→C；旧/新对照→D；有序步骤/时序→E；概念长文≥4 章→B；其余保底 A。

## 触发条件

- 「生成网页」「做成网页」「出 HTML」「技术文档网页」「换个骨架/风格」
- `/html` / `/html-generate`
- **被调用**：`weekly-intel-digest` / `best-practice-digest` 产网页那一步内部走本 Skill。

## 执行协议（五步）

1. 选骨架：读正文跑选择器（或用用户指定），报「骨架X·理由」。
2. 套正文：复制该骨架 `.html` 起手，正文填进对应容器；Mermaid `<br/>` 转义 `&lt;br/&gt;`。
3. 落炫酷硬要求（细则以 [[Contexts/规范/炫酷建站规范]] 为准）。
4. 浏览器自检：`python3 -m http.server` + Playwright，图全 SVG / console 0 error / section 全可见 / 375·768·1440 无横溢出 / count-up 触发；清理残留。
5. 交接：一句托管话术「把这个 .html 传 CDN、返回短链，不改内容」。

## 硬规则

1. 骨架=布局不同不是换皮；新增骨架先在 samples/ 落过自检样例 + 补骨架表，再被选择器引用。
2. 自检不可省，未过不交付（含三宽度无溢出）。
3. 自动选要透明、允许当场改；用户指定无条件服从。
4. 设计令牌一致（深色科技感 + mermaid 深色主题）。
5. 只托管不生成：纳米Work 只上传 CDN + 出短链。
