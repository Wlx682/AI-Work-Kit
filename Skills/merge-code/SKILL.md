---
name: merge-code
description: Analyze and perform a local code or branch merge when the user asks to merge branches or resolve conflicts while preserving both sides' intended behavior.
---

# Merge code

Resolve the repository, source and target from local evidence; ask only when they cannot be determined safely. Compare both sides' behavior before editing conflicts.

Textual conflicts may be resolved directly when intent is evident and verifiable. A semantic conflict involving product behavior, data meaning or incompatible commitments must be returned to the human with evidence and consequences.

By default perform only the requested local merge and relevant verification. Do not push, force, delete branches or merge a remote pull request without explicit authorization. Completion requires Git state plus tests or other evidence appropriate to the affected code.
