---
skill: html-generate
case: technical-doc-page
---

# HTML Generate Smoke Input

## 输入

- 请求：把一篇 Agent 评测体系技术文档做成自渲染 HTML 页面。
- 正文形态：章节多，包含指标表、流程图和落地步骤。
- 指定偏好：可自动选择骨架，但要说明选择理由。
- 交付：本地 `.html` 文件，纳米Work 只负责上传 CDN 并返回短链。

## 要求

- 按内容形态选择骨架，骨架差异必须是布局结构差异。
- 内嵌 Mermaid 自渲染，处理 `<br/>` 转义。
- 通过本地浏览器自检：console 0 error、375/768/1440 无横向溢出。
- 交接时给出 CDN 托管话术，不改正文内容。
