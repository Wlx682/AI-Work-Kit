# implementation-design-assistant · 代码落点设计

在需求、Story Scope 或 bug 根因已确认后，写代码前读取现有代码库，产出实现落点契约：目录、文件名、模块边界、依赖方向、Red 测试位置与待确认项。

## 适用位置

- `client-dev`：`story-split` 之后，`story-development` 之前。
- `bugfix`：`diagnose` 根因定位之后，`fix` 修复实现之前。
- 普通单阶段写代码：当用户要求先规划文件目录、文件名、架构落点时使用。

## 边界

- 不写业务实现代码。
- 不替代 `architecture-design-assistant`；系统级模块、数据模型、API Schema 和 ADR 仍由架构阶段决定。
- 不把 UI、Domain、Data/API 拆成横向交付任务；它们只是 Story 内部落点。
- 不能凭空发明目录或命名规则。找不到证据时写入 `blocked_questions`，阻塞进入开发。

## 输入

- 已采纳需求 Plan、Backlog、架构 Plan。
- `client-dev` 的功能开发主 Plan、`.stories.json` 和 Scope Story 子 Plan。
- `bugfix` 的复现/定位 Plan、根因摘要、影响范围。
- 当前代码仓库；若没有代码，必须显式记录 `codebase_available: false` 与原因。

## 输出

### client-dev

1. 在每个 Scope Story 子 Plan frontmatter 写入：

```yaml
implementation_design: Plans/功能开发/{{title}}-US-001.impl.json
```

2. 在功能开发主 Plan 追加 `## 实现落点设计`，列出 Story → implementation design JSON。
3. 每个 JSON 必须满足 `scripts/validate-client-dev.py implementation-design --plan Plans/功能开发/父Plan.md`。
4. 最后一个反馈增加 `workflow_stage: implementation-design`。

### bugfix

1. 在落点设计 Plan frontmatter 写入：

```yaml
implementation_design: Plans/Bug排查/{{title}}.impl.json
```

2. 在正文写 `## 修复落点设计`，说明修复范围、文件落点与回归测试位置。
3. JSON 必须满足 `python3 scripts/validate-implementation-design.py --plan Plans/Bug排查/xxx.md`。
4. 最后一个反馈增加 `workflow_stage: implementation-design`。

## implementation_design JSON 契约

```json
{
  "story_id": "US-001",
  "codebase_available": true,
  "codebase_read": [
    {"path": "src/features/demo/view.ts", "reason": "同模块命名和分层参考"}
  ],
  "target_files": {
    "modify": [
      {"path": "src/features/demo/view.ts", "purpose": "接入新增入口", "layer": "Presentation"}
    ],
    "create": [
      {"path": "src/features/demo/use-case.ts", "reason": "现有模块没有该用例", "naming_basis": "沿用 use-case.ts 命名", "layer": "Domain"}
    ]
  },
  "module_boundary": {
    "layer": "Presentation / Domain / Data / Infrastructure",
    "dependency_rule": "Presentation 只能依赖 Domain，不直连 Data"
  },
  "tests": {
    "red": [{"path": "tests/demo.test.ts", "command": "npm test -- demo"}],
    "smoke": [{"command": "npm run test:smoke"}]
  },
  "risks": [],
  "blocked_questions": [],
  "confirmed": true
}
```

规则：

- `codebase_available=true` 时，`codebase_read[].path` 必须引用真实存在的文件或目录。
- `target_files.modify[].path` 必须存在；`target_files.create[].path` 可不存在，但必须有 `reason` 和 `naming_basis`。
- `target_files.modify/create` 至少有一个目标文件。
- 每个目标文件必须有 `layer`，且不得违反架构依赖方向。
- `tests.red` 至少一条，必须有测试路径和命令；没有 Red 位置不得进入 TDD。
- `blocked_questions` 非空时，`confirmed` 不能为 true，开发阶段必须阻塞。

## 反馈回路

按 `Contexts/决策/Skill反馈协议.md` 写入目标 Plan 末尾；`contexts_used[].utility` 二选一：`high` / `not-needed`。完成后必须运行对应 validator。