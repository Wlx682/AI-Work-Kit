"""结构化终身记忆。对应架构图「结构化终身记忆」。

四种记忆类型：
- 工作记忆（working）：当前任务的临时上下文，任务结束即清空
- 情景记忆（episodic）：历史任务的执行经历，可回顾
- 语义记忆（semantic）：提炼出的通用知识和规则
- 程序记忆（procedural）：学会的操作步骤模式
"""

import json
import os

MEMORY_DIR = os.path.join(os.path.dirname(__file__), ".memory")


class Memory:
    def __init__(self):
        self._working: list[dict] = []
        self._episodic: list[dict] = []
        self._semantic: list[dict] = []
        self._procedural: list[dict] = []
        self._load()

    def _store_path(self, kind: str) -> str:
        os.makedirs(MEMORY_DIR, exist_ok=True)
        return os.path.join(MEMORY_DIR, f"{kind}.json")

    def _load(self):
        for kind in ("episodic", "semantic", "procedural"):
            path = self._store_path(kind)
            if os.path.isfile(path):
                with open(path, "r", encoding="utf-8") as f:
                    setattr(self, f"_{kind}", json.load(f))

    def _save(self, kind: str):
        path = self._store_path(kind)
        with open(path, "w", encoding="utf-8") as f:
            json.dump(getattr(self, f"_{kind}"), f, ensure_ascii=False, indent=2)

    # --- 工作记忆：当前任务临时上下文 ---

    def working_add(self, entry: dict):
        self._working.append(entry)

    def working_get(self) -> list[dict]:
        return list(self._working)

    def working_clear(self):
        self._working.clear()

    # --- 情景记忆：历史任务记录 ---

    def episodic_add(self, task: str, steps: list[str], results: list[str], outcome: str):
        self._episodic.append({
            "task": task,
            "steps": steps,
            "results": results,
            "outcome": outcome,
        })
        if len(self._episodic) > 50:
            self._episodic = self._episodic[-50:]
        self._save("episodic")

    def episodic_search(self, keyword: str) -> list[dict]:
        return [e for e in self._episodic if keyword in e.get("task", "")]

    # --- 语义记忆：通用知识 ---

    def semantic_add(self, fact: str, source: str = ""):
        self._semantic.append({"fact": fact, "source": source})
        self._save("semantic")

    def semantic_get(self) -> list[dict]:
        return list(self._semantic)

    # --- 程序记忆：操作步骤模式 ---

    def procedural_add(self, pattern: str, steps: list[str]):
        self._procedural.append({"pattern": pattern, "steps": steps})
        self._save("procedural")

    def procedural_search(self, keyword: str) -> list[dict]:
        return [p for p in self._procedural if keyword in p.get("pattern", "")]

    # --- 汇总：给 System 2 的上下文 ---

    def to_context(self) -> str:
        parts = []
        if self._working:
            items = [w.get("summary", str(w)) for w in self._working[-5:]]
            parts.append("【工作记忆】\n" + "\n".join(items))
        if self._semantic:
            facts = [s["fact"] for s in self._semantic[-10:]]
            parts.append("【已知知识】\n" + "\n".join(facts))
        if self._episodic:
            recent = self._episodic[-3:]
            items = [f"- {e['task']}: {e['outcome']}" for e in recent]
            parts.append("【近期经历】\n" + "\n".join(items))
        return "\n\n".join(parts) if parts else "(无记忆)"
