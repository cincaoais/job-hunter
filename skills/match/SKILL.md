---
name: match
description: Should you apply? Knockout pre-check, legitimacy check, fit scorecard and honest apply/stretch/skip verdict for a posting, with truthful resume edits. Runs the job-hunting skill's Qualifier role.
argument-hint: [posting URL or pasted posting]
disable-model-invocation: true
---

Use the `job-hunting` skill, role **Qualifier** (`references/jd-match.md`). Posting: $ARGUMENTS
If that is empty, ask for the posting URL or text before proceeding.

1. Resolve storage mode (workspace: `python3 ${CLAUDE_SKILL_DIR}/../job-hunting/scripts/workspace.py where`); read the profile first and never re-ask what it answers.
2. Workspace mode with a URL: run `python3 ${CLAUDE_SKILL_DIR}/../job-hunting/scripts/fetch_posting.py <url> --save` and read the saved file under `postings/`.
3. Run jd-match end to end, in its order: fetch → extract → knockout pre-check → score → legitimacy block (the cap on the honest verdict) → optimize (truthful before/after edits) → record (`python3 ${CLAUDE_SKILL_DIR}/../job-hunting/scripts/tracker.py add --stage saved`).
4. For a full rebuild rather than posting-specific edits, hand off to `/job-hunter:resume`.
