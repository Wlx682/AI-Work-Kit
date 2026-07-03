#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import re
import sys
from dataclasses import dataclass
from pathlib import Path


ROOT = Path(__file__).resolve().parent.parent
WORKFLOW_DIR = ROOT / ".workflows" / "blueprints"
DEFAULT_WORKFLOW = "client-dev"


@dataclass(frozen=True)
class Match:
    workflow: str | None
    matched: bool
    score: int
    hits: list[str]
    reason: str


def normalize(text: str) -> str:
    return re.sub(r"\s+", "", text).lower()


def load_blueprints() -> list[dict]:
    blueprints: list[dict] = []
    for path in sorted(WORKFLOW_DIR.glob("*.json")):
        data = json.loads(path.read_text(encoding="utf-8"))
        if data.get("kind") == "engine-index":
            continue
        if not data.get("name") or not data.get("triggerHints"):
            continue
        data["_path"] = str(path.relative_to(ROOT))
        blueprints.append(data)
    return blueprints


def load_engine_triggers() -> list[str]:
    index = WORKFLOW_DIR / "full-cycle.json"
    if not index.exists():
        return []
    data = json.loads(index.read_text(encoding="utf-8"))
    return [str(item) for item in data.get("triggerPhrases", []) if str(item).strip()]


def explicit_workflow(utterance: str, blueprints: list[dict]) -> tuple[bool, str | None]:
    names = {bp["name"] for bp in blueprints}
    patterns = [
        r"(?:workflow|工作流)\s*[:=：]\s*([A-Za-z0-9_-]+)",
        r"/workflow\s+([A-Za-z0-9_-]+)",
    ]
    for pattern in patterns:
        m = re.search(pattern, utterance, flags=re.IGNORECASE)
        if not m:
            continue
        name = m.group(1)
        if name in names:
            return True, name
        return True, None
    return False, None


def engine_trigger_hits(utterance: str) -> list[str]:
    norm = normalize(utterance)
    hits = []
    for phrase in load_engine_triggers():
        phrase_norm = normalize(phrase)
        if phrase_norm and phrase_norm in norm:
            hits.append(phrase)
    return hits


def route(utterance: str) -> Match:
    blueprints = load_blueprints()
    has_explicit, explicit = explicit_workflow(utterance, blueprints)
    if explicit:
        return Match(explicit, True, 10_000, [f"workflow={explicit}"], "explicit-workflow")
    if has_explicit:
        return Match(None, False, 0, [], "unknown-explicit-workflow")

    norm = normalize(utterance)
    candidates: list[tuple[int, str, list[str]]] = []
    for bp in blueprints:
        hits = []
        score = 0
        for hint in bp.get("triggerHints", []):
            hint_norm = normalize(str(hint))
            if not hint_norm:
                continue
            if hint_norm in norm:
                hits.append(str(hint))
                score += len(hint_norm)
        candidates.append((score, bp["name"], hits))

    candidates.sort(key=lambda item: (item[0], item[1]), reverse=True)
    if not candidates or candidates[0][0] <= 0:
        engine_hits = engine_trigger_hits(utterance)
        if engine_hits:
            return Match(DEFAULT_WORKFLOW, True, 100, engine_hits, "engine-default")
        return Match(None, False, 0, [], "no-trigger-hint")

    top_score, top_name, top_hits = candidates[0]
    if len(candidates) > 1 and candidates[1][0] == top_score:
        tied = [name for score, name, _ in candidates if score == top_score]
        return Match(None, False, top_score, top_hits, f"ambiguous:{','.join(tied)}")

    return Match(top_name, True, top_score, top_hits, "trigger-hints")


def main() -> int:
    ap = argparse.ArgumentParser(
        description="检查自然语言是否命中 workflow 蓝图 triggerHints。",
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    ap.add_argument("utterances", nargs="*", help="要检查的自然语言输入；不传则从 stdin 按行读取")
    ap.add_argument("--json", action="store_true", help="输出 JSON")
    args = ap.parse_args()

    utterances = args.utterances
    if not utterances:
        utterances = [line.strip() for line in sys.stdin if line.strip()]

    rows = []
    for utterance in utterances:
        match = route(utterance)
        rows.append(
            {
                "utterance": utterance,
                "matched": match.matched,
                "workflow": match.workflow,
                "score": match.score,
                "hits": match.hits,
                "reason": match.reason,
            }
        )

    if args.json:
        print(json.dumps(rows if len(rows) != 1 else rows[0], ensure_ascii=False, indent=2))
        return 0

    for row in rows:
        workflow = row["workflow"] or "-"
        hits = ",".join(row["hits"]) if row["hits"] else "-"
        print(f"{row['utterance']}\tmatched={row['matched']}\tworkflow={workflow}\thits={hits}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
