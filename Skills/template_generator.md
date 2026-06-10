# 模板生成器 Skill

当用户需要启动高频任务时，按任务类型选用 `Templates/` 下模板。全库约定见 `Templates/模板约定.md`。

## 支持的任务类型

| 类型 | 模板文件 | 存放路径 |
|------|----------|----------|
| 排查 | `Templates/排查问题模板.md` | `Plans/Bug排查/` |
| **技术方案**（客户端/服务端） | `Templates/技术方案模板.md` | `Plans/客户端技术方案/` 或 `Plans/服务端技术方案/` |
| 重构 | `Templates/技术方案模板.md` | `Plans/代码重构/` |
| review | `Templates/Code-Review模板.md` | 按需 |
| **需求分析** | `Templates/需求分析模板.md` | `Plans/需求分析/` |
| **功能开发**（需求+方案+界面） | `Templates/客户端功能开发模板.md` | `Plans/功能开发/` |
| 界面 / Figma（仅 UI） | `Templates/客户端功能开发模板.md`（含业务逻辑=否） | `Plans/功能开发/` |
| 会议 | `Templates/会议记录模板.md` | `Contexts/会议/` |
| API 设计 | `Templates/API设计模板.md` | `Contexts/API/` |
| 发布检查 | `Templates/发布检查清单模板.md` | `Contexts/发布/` |

## 执行步骤

1. 确认任务类型（客户端 / 服务端 / 排查 / …）。
2. 读取对应模板，填充 `【】`；日期用 `{{date}}`。
3. 搜索 `Contexts/`、`Plans/` 引用历史决策。
4. 输出 plan 草稿 + 建议路径 + 续做命令：

```
/resume plan=Plans/【分类】/{{date}}-{{title}}.md 进度=【】
```

## 触发示例

```
/template-generator 任务类型=技术方案，平台=服务端，背景=订单接口 P99 超时

/template-generator 任务类型=功能开发，背景=【模块名】，Figma=【链接】

/template-generator 任务类型=排查，背景=...
```

> 功能开发也可用 `/feature-dev-assistant`（推荐，含 Figma 读节点流程）。
