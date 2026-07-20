---
description: Should you apply? Fit score + verdict for a posting, with truthful edits
argument-hint: paste the job posting or its URL
---

Use the `job-hunting` skill and follow its `references/jd-match.md` flow (Job-Description Match & Resume Optimizer).

Posting: $ARGUMENTS
If that's empty, ask the user to paste the job posting or its URL before proceeding.

1. Read the Candidate Profile FIRST (skill Step 0/1 — the one source of truth); don't re-ask what it already answers.
2. Run jd-match.md end to end: Extract → Score (match report + honest overall fit /10 and verdict) → Optimize with truthful before → after resume edits. Never invent metrics, titles, or achievements — a real gap is never closed by wording.
3. If anything changed (e.g. logging the posting/outcome in the pipeline tracker), regenerate the updated profile at the end per the skill's closing step.

For a full resume rebuild rather than posting-specific tweaks, use `/job-resume`.
