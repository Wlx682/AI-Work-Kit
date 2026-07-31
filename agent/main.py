#!/usr/bin/env python3
"""CLI 入口。只负责参数解析和 REPL 交互，不含业务逻辑。

用法：
  python3 -m agent.main                                   # 单智能体 REPL
  python3 -m agent.main "帮我看看当前目录有哪些文件"        # 单智能体
  python3 -m agent.main --team "统计有多少个 .py 文件"      # 多智能体团队
"""

import sys
import os
import json

from .orchestrator import Orchestrator
from .memory import Memory


def report_result(result):
    if result.is_paused:
        kinds = {item["value"].get("kind") for item in result.interrupts}
        waiting_for = "用户输入" if "input" in kinds else "人工处理" if "unknown" in kinds else "审批"
        print(f"⏸️  执行暂停，等待{waiting_for}（run={result.run_id}, thread={result.thread_id}）")
        for item in result.interrupts:
            kind = item["value"].get("kind")
            label = "信息请求" if kind == "input" else "未知执行结果" if kind == "unknown" else "审批请求"
            print(f"   {label}:")
            print(json.dumps(item["value"], ensure_ascii=False, indent=2))
        return
    if not result.succeeded:
        print(f"❌ 执行失败（run={result.run_id}, thread={result.thread_id}）：{result.error}")
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

    pending_result = None
    while True:
        try:
            if pending_result is not None:
                interruption = pending_result.interrupts[0]["value"]
                if interruption.get("kind") == "input":
                    value = input(f"\n📝 {interruption['question']}: ").strip()
                    if not value:
                        continue
                    result = agent.resume(
                        pending_result.thread_id,
                        {"value": value},
                        parent_run_id=pending_result.run_id,
                    )
                else:
                    raw = input("\n📝 请输入 resolution JSON: ").strip()
                    if not raw:
                        continue
                    result = agent.resume(
                        pending_result.thread_id,
                        json.loads(raw),
                        parent_run_id=pending_result.run_id,
                    )
            else:
                task = input("\n📝 请输入任务: ").strip()
                if not task:
                    continue
                if task.lower() in ("quit", "exit", "q"):
                    print("👋 再见！")
                    break
                result = agent.run(task) if use_team else agent.run_with_trace(task)
        except (EOFError, KeyboardInterrupt):
            print("\n👋 再见！")
            break
        except Exception as error:
            print(f"\n❌ 错误: {error}")
            continue

        try:
            report_result(result)
            pending_result = result if result.is_paused else None
        except KeyboardInterrupt:
            print("\n\n⚠️  用户中断执行。")
        except Exception as error:
            print(f"\n❌ 错误: {error}")


if __name__ == "__main__":
    main()
