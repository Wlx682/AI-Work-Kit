#!/usr/bin/env python3
"""Dedicated regression for pattern-insight reader writing and publishing gates."""

from __future__ import annotations

import subprocess
import sys
import tempfile
from pathlib import Path


ROOT = Path(__file__).resolve().parent.parent
SKILL_DIR = ROOT / ".cursor/skills/pattern-insight-workflow"


def require(condition: bool, message: str) -> None:
    if not condition:
        raise AssertionError(message)


def require_fragments(path: Path, fragments: list[str]) -> None:
    text = path.read_text(encoding="utf-8")
    try:
        display_path = path.relative_to(ROOT)
    except ValueError:
        display_path = path
    for fragment in fragments:
        require(fragment in text, f"{display_path} missing: {fragment}")


def main() -> int:
    require_fragments(
        SKILL_DIR / "SKILL.md",
        [
            "知乎发布协议",
            "08-zhihu-answer.md",
            "草稿验收",
            "行动时确认",
            "公开 URL",
            "visual-markdown-toolbox",
            "最多 1–2 张",
            "渲染图不计入生成式图片额度",
            "02-research-pack.md",
            "不能只给链接",
            "默认阅读对象是中文研究包",
            "门禁 C 自动失效",
            "视觉资产清单",
            "图片加载、响应式裁切",
            "读者入口卡",
            "共同现状 → 直接压力 → 解释缺口 → 核心判断",
            "不得让读者先解释陌生案例",
            "旧信息连接 → 新信息推进",
            "标题与开头释义测试",
            "zhihu-independent-article.md",
            "当前界面没有独立摘要字段时不得虚构摘要配置",
            "1440 × 810",
            "3:2 居中裁切",
            "创作声明和内容来源",
            "投稿至问题最多 1 个",
        ],
    )
    require_fragments(
        SKILL_DIR / "references/method.md",
        [
            "内容、账号与位置审批 D",
            "草稿写入与结构验收",
            "行动时确认",
            "点击发布并回写链接",
            "结构可视化",
            "生成图克制",
            "翻译式总结",
            "不能把“去读五篇原文”作为默认交付",
            "内容基线",
            "实质内容变更",
            "375 与 1440 宽度的首屏裁切",
            "文章类型与读者入口卡",
            "Nature 的信息依赖顺序",
            "案例前置检查",
            "读者问题链",
            "反向提纲与释义测试",
            "知乎独立文章平台适配",
            "标题、首屏、封面和话题形成相关性闭环",
            "按钮名称",
            "没有强匹配就保持未选择",
        ],
    )
    require_fragments(
        ROOT / "Skills/pattern_insight_workflow.md",
        [
            "知乎发布硬门禁",
            "中文研究包硬门禁",
            "流程图或架构图",
            "最多 1–2 张",
            "最终点击授权",
            "门禁 C 自动失效",
            "视觉资产清单",
            "375/1440 首屏裁切",
            "Nature 的同心入口",
            "案例只有在读者能立即识别场景",
            "读者问题链",
            "释义测试",
            "2–3 个平台真实话题",
            "3:2 居中裁切",
            "创作声明和内容来源",
            "投稿至问题最多 1 个",
        ],
    )
    require_fragments(
        SKILL_DIR / "references/artifact-templates.md",
        [
            "门禁后变更",
            "门禁 C 内容基线",
            "已失效待重验",
            "视觉资产清单",
            "最终提示词",
            "16:9 原图 / 3:2 居中裁切",
            "文章类型：研究结果型 / 技术观点型 / 案例复盘型",
            "同心入口：共同现状 / 直接压力 / 解释缺口 / 核心判断",
            "信息分层",
            "发布形式：知乎问答 / 知乎独立文章",
            "当前编辑器无独立摘要字段，由首屏承担",
            "16:9 结论 / 3:2 居中裁切结论",
            "投稿至问题：候选问题 / URL / 匹配判断 / 最终选择或未选择理由",
        ],
    )
    require_fragments(
        SKILL_DIR / "references/reader-centered-writing.md",
        [
            "读者带入不是靠“上来讲故事”",
            "How to construct a Nature summary paragraph",
            "技术观点型",
            "同心入口",
            "案例前置的四个条件",
            "旧信息 → 新信息",
            "正文与证据分层",
            "标题与首段释义测试",
        ],
    )
    require_fragments(
        SKILL_DIR / "references/quality-rubric.md",
        [
            "32/40",
            "读者定位",
            "开场定向",
            "释义一致性",
            "案例若前置",
            "研究结果型、技术观点型和案例复盘型",
            "平台相关性",
            "四个入口回答同一个读者问题",
        ],
    )
    require_fragments(
        SKILL_DIR / "references/zhihu-independent-article.md",
        [
            "标题框提示最多 100 字",
            "1440 × 810",
            "150 × 100",
            "3:2 居中裁切",
            "当前编辑器未见独立摘要字段",
            "核心对象—工程语境—关键机制",
            "不自造标签",
            "新发布 / 更新旧文章",
            "按钮是“发布”还是“更新”",
            "最多选择 1 个",
            "没有强匹配就保持未选择",
        ],
    )
    require_fragments(
        ROOT / ".cursor/skills/visual-markdown-toolbox/SKILL.md",
        [
            "生成式图片边界",
            "确定性渲染不计入此额度",
            "生成式图片绝不超过 2 张",
            "不要用氛围插画代替关系表达",
        ],
    )

    with tempfile.TemporaryDirectory(prefix="pattern-insight-regression-") as temp:
        workspace = Path(temp)
        result = subprocess.run(
            [
                sys.executable,
                str(SKILL_DIR / "scripts/init_cycle.py"),
                "--workspace",
                str(workspace),
                "--domain",
                "AI Agent 工作流",
                "--question",
                "如何把知乎发布固化到流程？",
                "--date",
                "2026-08-13",
            ],
            check=True,
            capture_output=True,
            text=True,
        )
        cycle = Path(result.stdout.strip())
        require((cycle / "08-zhihu-answer.md").exists(), "initializer missing Zhihu answer artifact")
        require_fragments(
            cycle / "02-research-pack.md",
            [
                "翻译式总结",
                "原文链接与定位只作为核验入口",
                "关键证据",
                "局限与反方",
                "需要你判断",
            ],
        )
        require_fragments(
            cycle / "07-publish-package.md",
            [
                "默认平台：知乎问答",
                "草稿验收：待执行",
                "行动时确认：未取得",
                "发布状态：未发布",
                "生成式图片：0 张（最多 2 张）",
                "文本图表：待规划",
                "门禁后变更",
                "门禁 C 内容基线：待记录",
                "视觉资产清单",
                "封面：非默认必需",
                "1440×810 / 16:9 原图 / 3:2 居中裁切",
                "发布形式：知乎问答 / 知乎独立文章（待确认）",
                "1440×810 / 16:9 原图 / 3:2 居中裁切",
                "不虚构摘要配置",
                "创作声明：待确认可见选项与最终选择",
                "投稿至问题：待搜索强匹配问题；无匹配则保持未选择",
            ],
        )

    print("OK:pattern-insight-workflow:reader writing and publishing regression passed")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
