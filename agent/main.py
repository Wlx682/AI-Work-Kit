#!/usr/bin/env python3
"""CLI 入口。只负责参数解析和 REPL 交互，不含业务逻辑。

用法：
  python3 -m agent.main                                   # 单智能体 REPL
  python3 -m agent.main "帮我看看当前目录有哪些文件"        # 单智能体
  python3 -m agent.main --team "统计有多少个 .py 文件"      # 多智能体团队
"""

import sys
import os

from .orchestrator import Orchestrator
from .memory import Memory


def report_result(result):
    if result.is_paused:
        print(f"⏸️  执行暂停，等待审批（run={result.run_id}）")
        for item in result.interrupts:
            print(f"   审批请求: {item['value']}")
        return
    if not result.succeeded:
        print(f"❌ 执行失败（run={result.run_id}）：{result.error}")
    for warning in result.warnings:
        print(f"⚠️ {warning}")


def main():
    api_key = os.environ.get("DEEPSEEK_API_KEY")
    if not api_key:
        print("❌ 请先设置 DEEPSEEK_API_KEY 环境变量：")
        print("   export DEEPSEEK_API_KEY='sk-...'")
        print()
        print("   获取 API key: https://platform.deepseek.com/api_keys")
        sys.exit(1)

    # --team 开关：选多智能体团队编排，否则走单智能体
    args = sys.argv[1:]
    use_team = "--team" in args
    args = [a for a in args if a != "--team"]

    if use_team:
        from .team_graph_runtime import TeamGraphRuntime
        agent = TeamGraphRuntime(Memory())
    else:
        agent = Orchestrator(Memory())

    if args:
        task = " ".join(args)
        result = agent.run(task) if use_team else agent.run_with_trace(task)
        report_result(result)
        return

    mode = "多智能体 Team Graph（Planner→Predictor→Executor→Reviewer）" if use_team else "单智能体（一个脑子顺序调能力）"
    print(f"🤖 通用小助手 Agent — {mode}（输入 quit 退出）")
    print("═" * 60)
    print("   能力层：act 执行 · planning 规划 · reviewing 评审（单/多智能体共用）")
    print("   编排层：Orchestrator 单智能体图 / Team 四角色图")
    print("   📚 记忆 = 工作/情景/语义/程序/纠正")

    while True:
        try:
            task = input("\n📝 请输入任务: ").strip()
        except (EOFError, KeyboardInterrupt):
            print("\n👋 再见！")
            break

        if not task:
            continue
        if task.lower() in ("quit", "exit", "q"):
            print("👋 再见！")
            break

        try:
            result = agent.run(task) if use_team else agent.run_with_trace(task)
            report_result(result)
        except KeyboardInterrupt:
            print("\n\n⚠️  用户中断执行。")
        except Exception as e:
            print(f"\n❌ 错误: {e}")


if __name__ == "__main__":
    main()
