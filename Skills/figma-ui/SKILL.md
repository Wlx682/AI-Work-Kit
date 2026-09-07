---
name: figma-ui
description: Implement or compare a user interface against Figma when the user asks for design-to-code work, visual alignment or node-level inspection.
---

# Figma UI

Read the target Figma nodes and the current code. Node properties and variants are design evidence; screenshots are comparison evidence, not a substitute for measurements.

Reuse existing components and assets where they match. AI may choose reversible code structure, but must not invent missing interaction, data or product semantics. Ask the human or designer only for a decision that cannot be recovered from the design and code.

Use the current project's conventions in `Knowledge/Figma/` when relevant. Completion requires running code and visual evidence appropriate to the request; report concrete differences rather than a self-assigned fidelity score. Do not create a mandatory UI plan or checklist.
