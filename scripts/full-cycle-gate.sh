#!/usr/bin/env bash
# [DEPRECATED 薄封装] 全流程机械门禁 —— 已迁移到通用引擎 scripts/workflow-gate.sh。
# 本脚本保留仅为兼容旧引用（SKILL.md / 工作流总览 / 模板约定 等）。
# 行为：等价于 workflow-gate.sh --workflow client-dev，转发所有 --epic/--project/--json 参数。
# 新代码请直接调用：scripts/workflow-gate.sh --workflow <name> ...
set -euo pipefail

ROOT="$(cd "$(dirname "$0")/.." && pwd)"
exec bash "$ROOT/scripts/workflow-gate.sh" --workflow client-dev "$@"
