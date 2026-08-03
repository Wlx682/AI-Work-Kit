"""能力·评审（reviewing）：中途反思 / 终局评审。

两个不同用途的能力：
  - reflect：执行途中，判断继续/调整/完成，并标记是否有教训（供 L7 蒸馏）。
  - review：全部执行完后，以第三方视角判断结果是否达标，accept/revise。

以前单智能体反思和 Reviewer 评审分散实现；现在统一到评审能力层。
"""

from ..infrastructure import llm

REFLECT_PROMPT = """\
你会看到已完成步骤的执行结果和剩余步骤。

请判断：
- 如果剩余步骤仍然合理，输出：{"action": "continue", "has_lesson": false}
- 如果需要调整剩余步骤，输出：{"action": "replan", "new_steps": ["新步骤1", ...], "has_lesson": true}
- 如果任务已经完成，输出：{"action": "done", "summary": "一句话总结", "has_lesson": false}

has_lesson 表示本次执行过程中是否出现了走弯路、犯错、被纠正、或发现了值得记住的规律。
只在确实有教训时设为 true，常规顺利执行设为 false。
只输出 JSON。
"""

REVIEW_PROMPT = """\
你以第三方视角审查结果是否真正完成了任务——你没有参与规划和执行。

请输出 JSON：
{
  "verdict": "accept" 或 "revise",
  "reason": "你的判断理由",
  "suggestion": "如果 revise，给出具体的修改建议；accept 则留空"
}

规则：
- "accept"：结果确实完成了任务，质量可接受。
- "revise"：有明显缺陷、遗漏或答非所问，需要打回。
- suggestion 要具体到可据此改进计划，不要泛泛而谈。
- 只输出 JSON。
"""


def reflect(
    task: str,
    steps: list[str],
    done_index: int,
    results: list[str],
    acceptance: tuple[str, ...] = (),
) -> dict:
    """执行途中反思，决定下一步。"""
    completed = "\n".join(f"步骤 {i+1} [{steps[i]}]: {r}" for i, r in enumerate(results))
    remaining = "\n".join(
        f"步骤 {i+1}: {s}"
        for i, s in enumerate(steps[done_index:], done_index)
    )

    acceptance_text = "\n".join(f"- {item}" for item in acceptance) or "(未额外声明)"
    return llm.chat_json([
        {"role": "system", "content": REFLECT_PROMPT},
        {"role": "user", "content": (
            f"原始任务：{task}\n\n验收标准：\n{acceptance_text}\n\n"
            f"已完成：\n{completed}\n\n剩余步骤：\n{remaining or '(无)'}"
        )},
    ])


def review(
    task: str,
    steps: list[str],
    results: list[str],
    acceptance: tuple[str, ...] = (),
) -> dict:
    """终局评审：审查最终执行结果，返回 {"verdict", "reason", "suggestion"}。"""
    execution = "\n".join(
        f"步骤{i+1}：{s}\n结果：{r}" for i, (s, r) in enumerate(zip(steps, results))
    )
    acceptance_text = "\n".join(f"- {item}" for item in acceptance) or "(未额外声明)"
    return llm.chat_json([
        {"role": "system", "content": REVIEW_PROMPT},
        {"role": "user", "content": (
            f"任务：{task}\n\n验收标准：\n{acceptance_text}\n\n执行记录：\n{execution}"
        )},
    ])
