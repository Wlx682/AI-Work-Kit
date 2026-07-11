#!/usr/bin/env python3
"""CLI 入口。只负责参数解析和 REPL 交互，不含业务逻辑。

用法：
  python3 -m agent.main
  python3 -m agent.main "帮我看看当前目录有哪些文件"
"""

import sys
import os

from .orchestrator import Orchestrator
from .memory import Memory


def main():
    api_key = os.environ.get("DEEPSEEK_API_KEY")
    if not api_key:
        print("❌ 请先设置 DEEPSEEK_API_KEY 环境变量：")
        print("   export DEEPSEEK_API_KEY='sk-...'")
        print()
        print("   获取 API key: https://platform.deepseek.com/api_keys")
        sys.exit(1)

    agent = Orchestrator(Memory())

    if len(sys.argv) > 1:
        task = " ".join(sys.argv[1:])
        agent.run(task)
        return

    print("🤖 通用小助手 Agent — 双系统架构（输入 quit 退出）")
    print("═" * 60)
    print("   🧠 System 2 = 规划 + 反思 + 世界模型")
    print("   ⚡ System 1 = 工具执行（经安全层审核）")
    print("   📚 记忆 = 工作/情景/语义/程序")

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
            agent.run(task)
        except KeyboardInterrupt:
            print("\n\n⚠️  用户中断执行。")
        except Exception as e:
            print(f"\n❌ 错误: {e}")


if __name__ == "__main__":
    main()
