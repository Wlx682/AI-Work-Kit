---
name: code-change
description: Implement, fix or refactor code when the user asks for a concrete repository change, including locating the right files and adding proportionate tests.
---

# Code change

Inspect the repository, identify the observable outcome, make the smallest coherent change and verify it. Do not require a separate requirement, architecture, story or implementation-design artifact before editing.

LLM may make reversible implementation choices that stay within the requested behavior and can be tested. Stop and ask the human when the change would alter user-visible semantics, public contracts, security posture, data compatibility, external systems or the authorized scope.

Prefer existing conventions and tests over invented structure. Add or adjust tests when they provide meaningful evidence; do not create ceremonial tests. Completion requires the relevant diff plus executed verification, with any unverified area stated plainly.
