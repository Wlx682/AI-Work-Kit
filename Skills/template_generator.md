# 模板生成器 Skill

当用户需要启动高频任务时，按任务类型选用 `Templates/` 下模板。

## 支持的任务类型

| 类型 | 模板文件 | 存放路径 |
|------|----------|----------|
| 排查 | `Templates/排查问题模板.md` | `Plans/Bug排查/` |
| **客户端方案** | `Templates/客户端技术方案模板.md` | `Plans/客户端技术方案/` |
| **服务端方案** | `Templates/服务端技术方案模板.md` | `Plans/服务端技术方案/` |
| 重构 | `Templates/客户端技术方案模板.md` | `Plans/代码重构/`（客户端重构时） |
| review | `Templates/Code-Review模板.md` | 按需 |
| **需求分析** | `Templates/需求分析模板.md` | `Plans/需求分析/` |
| **功能开发**（需求+方案+界面） | `Templates/功能开发模板.md` | `Plans/功能开发/` |
| 界面 / Figma（仅 UI） | `Templates/Figma界面开发模板.md` | `Plans/界面开发/` |

> 用户说「方案」未说明端时，询问是**客户端**还是**服务端**。

## 执行步骤

1. 确认任务类型（客户端 / 服务端 / 排查 / …）。
2. 读取对应模板，填充 `【】`。
3. 搜索 `Contexts/`、`Plans/` 引用历史决策。
4. 输出 plan 草稿 + 建议路径 + 第一条 Cursor 指令。

## 触发示例

```
@Skills/template_generator.md 任务类型=客户端方案，背景=iOS 设置页重构，需 Clean Arch

@Skills/template_generator.md 任务类型=服务端方案，背景=订单接口 P99 超时，需加缓存

/template-generator 任务类型=排查，背景=...

/template-generator 任务类型=功能开发，背景=【模块名+需求】，Figma=【链接】
```

> 功能开发也可用 `/feature-dev-assistant`（推荐，含 Figma 读节点流程）。
