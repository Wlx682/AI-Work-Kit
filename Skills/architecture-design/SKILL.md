---
name: architecture-design
description: Analyze system boundaries, dependencies, data models, APIs, reliability or architectural tradeoffs when the user asks for technical design or a cross-cutting change.
---

# Architecture design

Ground the design in the current repository and real constraints. Describe the smallest architecture decision needed for the user's goal; do not expand a local change into a mandatory design exercise.

Make dependency direction, data ownership, failure behavior and migration impact explicit when they matter. Present alternatives only where a real tradeoff exists. AI can recommend, but decisions that change product semantics, long-term coupling, security, cost or operational responsibility belong to the human.

Use diagrams, schemas or ADR-style notes only when they materially improve the decision. Validate claims against code, interfaces, experiments or authoritative sources. A design document is produced only when requested or when it is itself the deliverable.
