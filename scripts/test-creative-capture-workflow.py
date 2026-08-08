#!/usr/bin/env python3
from __future__ import annotations

import json
import subprocess
import tempfile
import textwrap
import unittest
import uuid
from pathlib import Path


ROOT = Path(__file__).resolve().parent.parent
WORKFLOW = "creative-capture"


def run(args: list[str], *, check: bool = True) -> subprocess.CompletedProcess[str]:
    proc = subprocess.run(
        args,
        cwd=ROOT,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
    )
    if check and proc.returncode != 0:
        raise AssertionError(
            f"command failed ({proc.returncode}): {' '.join(args)}\n"
            f"stdout:\n{proc.stdout}\nstderr:\n{proc.stderr}"
        )
    return proc


def complete_plan() -> str:
    signal_rows = []
    domains = ["哲学", "生物学", "建筑", "餐饮"]
    for index in range(1, 13):
        source_type = "随机漫步" if index == 1 else "订阅源"
        outside = "是" if index <= 3 else "否"
        signal_rows.append(
            f"| S-{index:02d} | {domains[(index - 1) % len(domains)]} | {source_type} | "
            f"https://example.com/{index} | 主张{index} | 关联{index} | {outside} | 2026-08-09 |"
        )

    insight_rows = [
        f"| I-{index:02d} | S-{index:02d}, S-{index + 1:02d} | 人性问题{index} | "
        f"洞察{index} | 模型{index} | 反常关联{index} | 证据{index} |"
        for index in range(1, 6)
    ]
    problem_rows = [
        f"| Q-{index:02d} | 深层问题{index} | I-{index:02d} | 长期成立原因{index} |"
        for index in range(1, 4)
    ]
    idea_rows = [
        f"| C-{index:02d} | I-{index:02d}, I-{index + 1:02d}, I-{index + 2:02d} | "
        f"痛点{index} | 客群{index} | 服务{index} | 付费理由{index} | 测试{index} | 20 |"
        for index in range(1, 4)
    ]
    next_rows = [
        f"| N-{index:02d} | 问题卡 | 下轮种子{index} | 因为值得继续追踪{index} |"
        for index in range(1, 4)
    ]

    rendered = textwrap.dedent(
        f"""
        ---
        workflow: {WORKFLOW}
        selected_idea: C-01
        experiment_result: 继续验证
        cycle_decision: 继续
        archive_decision: 不沉淀（用户确认）
        ---

        # 创意捕捉周循环

        ## 一、本周意外性配额

        本周至少覆盖四个陌生领域，并完成一次随机漫步。

        ## 二、信号捕捉

        | 信号ID | 领域 | 来源类型 | 来源/链接 | 核心主张 | 意外关联 | 同温层外 | 观察日期 |
        |--------|------|----------|-----------|----------|----------|----------|----------|
        {chr(10).join(signal_rows)}

        ## 三、问题卡聚类

        | 问题ID | 深层问题 | 关联洞察卡 | 为什么长期成立 |
        |--------|----------|------------|----------------|
        {chr(10).join(problem_rows)}

        ## 四、洞察卡

        | 洞察ID | 关联信号 | 人性问题 | 核心洞察 | 思维模型 | 反常关联 | 证据 |
        |--------|----------|----------|----------|----------|----------|------|
        {chr(10).join(insight_rows)}

        ## 五、随机链接实验

        抽取 I-01、I-02、I-03，并与最近观察到的痛点组合。

        ## 六、创意候选

        | 创意ID | 三张洞察卡 | 痛点 | 付费客群 | 产品/服务形态 | 付费理由 | 七日测试 | 总分 |
        |--------|------------|------|----------|---------------|----------|----------|------|
        {chr(10).join(idea_rows)}

        ## 七、最小现实测试

        | 实验ID | 创意ID | 待证伪假设 | 渠道 | 对象 | 动作 | 时限 |
        |--------|--------|------------|------|------|------|------|
        | E-01 | C-01 | 客户愿意预约访谈 | 朋友圈 | 目标客户5人 | 发布微文档 | 48小时 |

        ## 八、证据与判定

        | 证据ID | 实验ID | 行为/原话 | 日期 | 强度 |
        |--------|--------|-----------|------|------|
        | EV-01 | E-01 | 两人主动预约 | 2026-08-09 | 强 |

        ## 九、本周复盘

        继续验证 C-01；停止扩充无关订阅源。

        ## 十、下轮种子

        | 种子ID | 类型 | 内容 | 为什么进入下轮 |
        |--------|------|------|----------------|
        {chr(10).join(next_rows)}
        """
    )
    # 插入的表格行从列 0 开始，会让 dedent 保留模板缩进；只剥模板的固定 8 空格。
    return "\n".join(line[8:] if line.startswith("        ") else line for line in rendered.splitlines()).strip() + "\n"


class CreativeCaptureWorkflowTests(unittest.TestCase):
    def test_00_blueprint_contract(self) -> None:
        path = ROOT / ".workflows/blueprints/creative-capture.json"
        bp = json.loads(path.read_text(encoding="utf-8"))
        self.assertFalse(bp["usesEpic"])
        self.assertEqual(bp["planRoot"], "Plans/创意捕捉")
        self.assertTrue(bp["planInit"]["useStageTemplate"])
        self.assertEqual(
            [stage["key"] for stage in bp["stages"]],
            ["radar", "insight", "synthesis", "reality-test", "retro"],
        )
        self.assertEqual({stage["planPrefix"] for stage in bp["stages"]}, {"周循环"})
        for stage in bp["stages"]:
            self.assertEqual(stage["skills"], ["creative-capture-assistant"])
            self.assertEqual(stage["template"], "Templates/创意捕捉周循环模板.md")
            self.assertEqual(stage["validator"], "scripts/validate-creative-capture.py")
            self.assertTrue(stage["exitCriteria"]["sectionsPresent"])
            self.assertTrue(stage["exitCriteria"]["skillRunStage"])

    def test_10_validator_rejects_under_quota_radar(self) -> None:
        with tempfile.TemporaryDirectory(prefix="aiwk-creative-capture-") as tmp:
            plan = Path(tmp) / "week.md"
            content = complete_plan().replace(
                "| S-12 | 餐饮 | 订阅源 | https://example.com/12 | 主张12 | 关联12 | 否 | 2026-08-09 |\n",
                "",
            )
            plan.write_text(content, encoding="utf-8")
            proc = run(
                ["python3", "scripts/validate-creative-capture.py", "--stage", "radar", str(plan)],
                check=False,
            )
            self.assertNotEqual(proc.returncode, 0)
            self.assertIn("至少需要 12 条完整信号", proc.stderr)

    def test_20_validator_accepts_complete_stage_facts(self) -> None:
        with tempfile.TemporaryDirectory(prefix="aiwk-creative-capture-") as tmp:
            plan = Path(tmp) / "week.md"
            plan.write_text(complete_plan(), encoding="utf-8")
            for stage in ["radar", "insight", "synthesis", "reality-test", "retro"]:
                proc = run(
                    ["python3", "scripts/validate-creative-capture.py", "--stage", stage, str(plan)]
                )
                self.assertIn(f"OK:creative-capture:{stage}", proc.stdout)

    def test_30_plan_init_renders_shared_weekly_template(self) -> None:
        token = f"fixture-{uuid.uuid4().hex[:10]}"
        day = "2099-01-01"
        rel = Path(f"Plans/创意捕捉/{day}-周循环-{token}.md")
        event = ROOT / f".workflows/events/{WORKFLOW}-{token}.events.jsonl"
        target = ROOT / rel
        try:
            proc = run(
                [
                    "python3",
                    "scripts/workflow-plan-init.py",
                    "--workflow",
                    WORKFLOW,
                    "--title",
                    token,
                    "--date",
                    day,
                ]
            )
            self.assertIn(f"created: {rel}", proc.stdout)
            content = target.read_text(encoding="utf-8")
            self.assertIn("## 二、信号捕捉", content)
            self.assertIn("## 十、下轮种子", content)
            self.assertIn(f"plan: {rel}", content)
        finally:
            target.unlink(missing_ok=True)
            event.unlink(missing_ok=True)


def main() -> int:
    parser = __import__("argparse").ArgumentParser()
    parser.add_argument("workflow", choices=[WORKFLOW])
    parser.parse_args()
    suite = unittest.defaultTestLoader.loadTestsFromTestCase(CreativeCaptureWorkflowTests)
    result = unittest.TextTestRunner(verbosity=2).run(suite)
    return 0 if result.wasSuccessful() else 1


if __name__ == "__main__":
    raise SystemExit(main())
