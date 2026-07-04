# 测试生成助手 Skill

当用户说「写测试」「测试计划」「自动化测试」「验收测试先行」「/test-generator」时执行。

> 读取 Epic、需求验收标准、功能开发 plan 与代码，生成验收测试先行或回归测试 plan。

## 知识库

- 模板：`Templates/自动化测试模板.md`
- 输入：`Plans/功能开发/xxx.md` + 链回的 `Plans/需求分析/`（验收标准 §九）
- 输出：`Plans/自动化测试/`
- 代码：**当前工作区**（读已有实现补用例）

## 执行步骤

1. 读 **Epic** frontmatter `workflow:`、`plans.*` + 关联功能开发主 plan / 子任务 + 需求 plan **验收标准**；运行 `workflow-gate.sh --workflow client-dev --epic <epic>` 确认当前测试语境。
2. 在代码库定位被测模块（类、API、组件路径）。
3. 按模板输出：
   - 单元测试清单（UT-xxx）
   - 集成测试清单（IT-xxx）
   - 与 AC 验收项的映射表
   - CI 命令（xcodebuild / pytest / go test 等，按项目实际）
4. Plan → `Plans/自动化测试/YYYY-MM-DD-模块名.md`；frontmatter：`lifecycle_state: test`、`epic: Plans/Epic/xxx.md`（`lifecycle_state` 仅兼容展示，阶段以 `workflow-gate.sh` 派生为准）。
5. **回写 Epic**（与看板对齐）：
   - `plans.test:` 指向新 plan
   - §一 子 Plan 索引表 test 行
   - 验收测试先行阶段对应 WBS 4；开发回归测试对应 WBS 9（如实际用于后置测试，按 Epic WBS 注明）

## 原则

- 用例必须链回需求 AC，不凭空加测
- 优先补关键路径与边界/异常（来自需求 plan §四 §五）
- 可输出测试代码片段到 plan，**实际代码写入业务仓库**（非 Vault）

## 与下一阶段衔接

测试 plan（先行）勾选通过 → 重新运行 `workflow-gate.sh` 进入 `split`（`task-splitter`）→ 开发

## 上下文汇报

```
📌 当前阶段：[test-first / 自动化测试] | 产出：Plans/自动化测试/xxx.md | 下一阶段：[跑 workflow-gate 派生] | 中断：/resume plan=...
```

## 触发示例

```
/test-generator 功能=Plans/功能开发/2026-06-20-支付-子任务02-API.md
```
