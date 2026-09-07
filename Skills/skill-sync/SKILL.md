---
name: skill-sync
description: Synchronize the project's canonical Skills into Cursor, Claude and Codex directories when the user explicitly asks to deploy, refresh or check skills.
---

# Skill sync

`Skills/*/SKILL.md` is the only project source. Check project copies with:

```bash
python3 scripts/sync-skills.py --check
```

When the user asks to deploy or refresh, run `--sync`. Add `--global` only when the user explicitly asks to change user-level skills. The script may remove generated project copies that are not present in the canonical source; it never treats generated copies as edits to preserve.
