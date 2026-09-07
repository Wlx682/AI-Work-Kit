---
name: code-review
description: Review a diff, branch or pull request for concrete defects, regressions and missing verification; use when the user asks for code review or implementation risk assessment.
---

# Code review

Review the actual change and enough surrounding code to validate each finding. Lead with actionable findings ordered by impact; include the affected file and tight line range when available.

Focus on behavior, data loss, security, concurrency, compatibility and test gaps. Do not report style preferences as defects unless they cause a concrete maintenance or correctness risk. Do not infer completion from descriptions or status metadata.

Review is read-only unless the user also asks for fixes. If no actionable defect is found, say so and name any material area that could not be verified.
