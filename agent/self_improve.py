"""自我纠错与经验提炼。对应架构图「自我纠错反馈 → 存取经验 → 提炼知识」。

职责：
1. 任务完成后，审视本次执行的情景记忆
2. 提炼通用知识（→ 语义记忆）和操作步骤模式（→ 程序记忆）
3. 识别执行中的错误和纠正（→ 纠正记忆）
4. 定期合并去重语义记忆（consolidate）
"""

from . import llm

DISTILL_PROMPT = """\
你是经验提炼器。你会看到一次任务的完整执行记录（任务、步骤、结果）。

请从中提炼可复用的经验，输出 JSON：
{
  "facts": ["通用知识1", "通用知识2"],
  "patterns": [
    {"trigger": "遇到什么类型的任务", "steps": ["应该怎么做的步骤1", "步骤2"]}
  ],
  "corrections": [
    {"mistake": "犯了什么错", "lesson": "应该怎么做"}
  ]
}

规则：
- facts 是通用知识，未来遇到类似情况可以直接复用的结论，而不是本次任务的具体细节。
- patterns 是可复用的操作步骤模式，trigger 描述触发条件，steps 描述步骤。
- corrections 是本次执行中走了弯路、犯了错、或被 System 2 纠正的地方。mistake 描述做错了什么，lesson 描述正确做法。
- 如果没有值得提炼的经验，对应字段输出空数组。
- 只输出 JSON。
"""

CONSOLIDATE_PROMPT = """\
你是知识整理器。下面是一组已有的语义记忆（通用知识），其中可能存在重复、近似重复或矛盾。

请合并去重，输出一个 JSON 数组，每个元素是一条精简后的知识（字符串）。

规则：
- 含义相同的合并为一条，保留更准确的表述。
- 互相矛盾的保留更新的（排在后面的更新）。
- 不要丢失任何不重复的知识。
- 只输出 JSON 数组。
"""

CONSOLIDATE_THRESHOLD = 20


def distill(task: str, steps: list[str], results: list[str]) -> dict:
    """从一次任务执行中提炼经验。"""
    execution_log = f"任务：{task}\n\n"
    for i, (s, r) in enumerate(zip(steps, results), 1):
        execution_log += f"步骤 {i}：{s}\n结果：{r}\n\n"

    return llm.chat_json([
        {"role": "system", "content": DISTILL_PROMPT},
        {"role": "user", "content": execution_log},
    ])


def consolidate(memory) -> int:
    """合并去重语义记忆。返回精简掉的条数。"""
    facts = memory.semantic_get()
    if len(facts) < CONSOLIDATE_THRESHOLD:
        return 0

    fact_texts = [f["fact"] for f in facts]
    merged = llm.chat_json([
        {"role": "system", "content": CONSOLIDATE_PROMPT},
        {"role": "user", "content": "\n".join(f"- {t}" for t in fact_texts)},
    ])

    removed = len(facts) - len(merged)
    if removed <= 0:
        return 0

    memory._semantic = [{"fact": f, "source": "consolidated"} for f in merged]
    memory._save("semantic")
    return removed
