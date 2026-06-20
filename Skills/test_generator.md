# 测试生成助手 Skill

当用户说「写测试」「测试计划」「自动化测试」「/test-generator」时执行。

> 读取功能开发 plan 与代码，生成单元测试 & 集成测试用例 plan。

## 知识库

- 模板：`Templates/自动化测试模板.md`
- 输入：`Plans/功能开发/xxx.md` + 链回的 `Plans/需求分析/`（验收标准 §九）
- 输出：`Plans/自动化测试/`
- 代码：**当前工作区**（读已有实现补用例）

## 执行步骤

1. 读 **Epic** frontmatter `plans.development` + 关联功能开发主 plan / 子任务 + 需求 plan **验收标准**。
2. 在代码库定位被测模块（类、API、组件路径）。
3. 按模板输出：
   - 单元测试清单（UT-xxx）
   - 集成测试清单（IT-xxx）
   - 与 AC 验收项的映射表
   - CI 命令（xcodebuild / pytest / go test 等，按项目实际）
4. Plan → `Plans/自动化测试/YYYY-MM-DD-模块名.md`；frontmatter：`lifecycle_state: test`、`epic: Plans/Epic/xxx.md`
5. **回写 Epic**（与看板对齐）：
   - `plans.test:` 指向新 plan
   - §一 子 Plan 索引表 test 行
   - WBS 切片 11 状态（完成或 `[~]` + CI 技术债说明）

## 原则

- 用例必须链回需求 AC，不凭空加测
- 优先补关键路径与边界/异常（来自需求 plan §四 §五）
- 可输出测试代码片段到 plan，**实际代码写入业务仓库**（非 Vault）

## 与 deployment-assistant 衔接

测试 plan 勾选通过 → `/deployment-assistant`

## 上下文汇报

```
📌 当前阶段：[自动化测试] | 产出：Plans/自动化测试/xxx.md | 下一阶段：[部署 /deployment-assistant] | 中断：/resume plan=...
```

## 触发示例

```
/test-generator 功能=Plans/功能开发/2026-06-20-支付-子任务02-API.md
```
