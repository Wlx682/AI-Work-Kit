#!/usr/bin/env python3
"""Initialize one pattern-insight cycle without overwriting existing work."""

from __future__ import annotations

import argparse
import datetime as dt
import re
from pathlib import Path


def slugify(value: str) -> str:
    value = value.strip().lower()
    value = re.sub(r"[^\w\u4e00-\u9fff]+", "-", value, flags=re.UNICODE)
    return value.strip("-_") or "research"


def create_exclusive(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("x", encoding="utf-8") as handle:
        handle.write(content)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--workspace", required=True, type=Path)
    parser.add_argument("--domain", required=True)
    parser.add_argument("--question", required=True)
    parser.add_argument("--date", default=dt.date.today().isoformat())
    parser.add_argument("--domain-slug")
    parser.add_argument("--cycle-slug")
    args = parser.parse_args()

    domain_slug = args.domain_slug or slugify(args.domain)
    cycle_slug = args.cycle_slug or slugify(args.question)[:60]
    domain_dir = args.workspace.resolve() / "Pattern-Insights" / domain_slug
    cycle_dir = domain_dir / "cycles" / f"{args.date}-{cycle_slug}"
    if cycle_dir.exists():
        raise SystemExit(f"Cycle already exists; no files changed: {cycle_dir}")

    domain_dir.mkdir(parents=True, exist_ok=True)
    ledger = domain_dir / "insight-ledger.md"
    if not ledger.exists():
        create_exclusive(ledger, "# 洞见资产账本\n\n| 日期 | 模式/主张 | 证据状态 | 适用边界 | 公开文章 | 反馈后的变化 | 下一问题 |\n|---|---|---|---|---|---|---|\n")

    files = {
        "STATUS.md": f"""# 周期状态

- 领域：{args.domain}
- 研究问题：{args.question}
- 当前阶段：1（研究立项）
- 当前责任人：共同
- 最近更新：{args.date}
- 已通过门禁：无
- 明确放宽的门禁：无
- 下一动作：补齐暂定假设、推翻证据和停止条件
- 阻塞：无
""",
        "01-brief.md": f"# 研究立项\n\n## 主问题\n\n{args.question}\n\n## 为什么现在值得研究\n\n## 目标读者与困境\n\n## 暂定假设\n\n## 推翻证据\n\n## 本期不研究\n\n## 时间盒与停止条件\n",
        "02-reading-queue.md": "# 阅读队列\n\n| 优先级 | 材料 | 作者/机构 | 日期 | 类型 | 为什么读 | 支持/挑战 | 状态 |\n|---|---|---|---|---|---|---|---|\n",
        "02-research-pack.md": "# 中文研究包\n\n> AI 交付翻译式总结，不是全文逐字翻译；原文链接与定位只作为核验入口。\n\n## 材料 1：待生成\n\n- 来源角色：\n- 要解决的问题：\n- 核心主张：\n- 机制/方法：\n- 关键证据：\n- 局限与反方：\n- 与本期问题的关系：\n- 需要你判断：\n- 原文核验入口：\n",
        "03-human-notes.md": "# 我的阅读批注\n\n> 用户默认阅读中文研究包后形成判断；AI 只能整理、补出处和追问，不要求用户默认阅读原文。\n",
        "04-pattern-map.md": "# 模式图\n",
        "05-claim.md": "# 核心主张\n\n- 用户确认：待确认\n",
        "06-draft.md": "# 研究稿\n",
        "06-article.md": "# 读者版文章\n\n> 门禁 C 未通过前不得用于 HTML 或发布。\n",
        "07-publish-package.md": """# 发布包

## 目标平台与读者

- 默认平台：知乎问答
- 发布形式：知乎问答 / 知乎独立文章（待确认）
- 操作类型：新发布 / 更新旧文章（待确认）
- 目标问题：待确定
- 目标 URL：待确定
- 发布账号：待确定

## 门禁后变更

- 门禁 C 内容基线：待记录
- 变更摘要：无
- 变更类型：无
- 门禁 C 状态：未通过

## HTML

- 文件：07-article.html
- 自检：待执行

## 视觉资产清单

- 文本图表：待规划
- 确定性渲染图：0 张
- 生成式图片：0 张（最多 2 张）
- 封面：非默认必需；独立文章若生成，待记录提示词摘要 / 用途 / 路径 / 1440×810 / 16:9 原图 / 3:2 居中裁切 / 平台加载

## 知乎发布

- 平台稿：08-zhihu-answer.md
- 相关性配置：读者问题 / 标题 / 首屏 150–250 字 / 封面语义 / 2–3 个平台真实话题
- 投稿至问题：待搜索强匹配问题；无匹配则保持未选择
- 摘要策略：待按当前编辑器字段确认，不虚构摘要配置
- 创作声明：待确认可见选项与最终选择
- 内容来源：待判断新闻 / 非新闻
- 草稿验收：待执行
- 生成图贴切性：待检查
- 正文字数 / 标题数 / 文本图表渲染数 / 生成式图片数 / 外链数：待记录
- 图片加载 / 外链 / 自动保存 / 发布按钮：待验收
- 行动时确认：未取得
- 发布状态：未发布
- 实际链接：

## 发布决定

- 门禁 D：未通过
""",
        "08-zhihu-answer.md": "# 知乎回答工作标题\n\n> 目标问题：待确定\n\n> 门禁 D 未通过前不得写入平台草稿。\n",
        "08-feedback.md": "# 反馈复盘\n",
    }
    for name, content in files.items():
        create_exclusive(cycle_dir / name, content)

    print(cycle_dir)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
