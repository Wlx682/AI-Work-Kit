# 部署助手 Skill

当用户说「部署」「上线检查」「发布计划」「/deployment-assistant」时执行。

> 读取技术方案 + 功能开发 + 测试 plan，生成部署检查清单。

## 知识库

- 模板：`Templates/部署模板.md`、参考 `Templates/发布检查清单模板.md`
- 输入：`Plans/【客户端|服务端】技术方案/`、`Plans/功能开发/`、`Plans/自动化测试/`
- 输出：`Plans/部署/`

## 执行步骤

1. 读 **Epic** frontmatter `workflow:` 与 `plans.*`（architecture / development / test），运行 `workflow-gate.sh --workflow client-dev --epic <epic>` 确认已进入 `deploy` 或明确用户要准备发布材料。
2. 读技术方案中的迁移、环境依赖、回滚策略。
3. 读自动化测试 plan，确认通过门槛。
4. 按 `部署模板` 输出：
   - 环境变量清单
   - 迁移脚本路径与 review 状态
   - 灰度 / 全量步骤
   - 回滚预案
   - 部署后冒烟（链需求 AC）
5. Plan → `Plans/部署/YYYY-MM-DD-模块名.md`；frontmatter：`lifecycle_state: deploy`、`epic: Plans/Epic/xxx.md`（`lifecycle_state` 仅兼容展示，阶段以 `workflow-gate.sh` 派生为准）
6. **回写 Epic**：`plans.deploy:` + §一 索引表 + WBS 13–14 指引

## 门禁

- `Plans/自动化测试/` 未标记通过 → 警告，用户确认后可继续
- 缺技术方案 → 停止，引导 `/architecture-design-assistant`
- `workflow-gate.sh --workflow client-dev` 在 deploy 阶段检查部署 plan 与 WBS 13–14；不通过修改 `lifecycle_state` 推进阶段

## 上下文汇报

```
📌 当前阶段：[deploy] | 产出：Plans/部署/xxx.md | 下一阶段：[retro / retro-assistant] | 中断：/resume plan=...
```

## 触发示例

```
/deployment-assistant 模块=支付，方案=Plans/技术方案/2026-06-20-支付.md
```
