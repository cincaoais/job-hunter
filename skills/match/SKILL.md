---
name: match
description: Should you apply? Knockout pre-check, legitimacy check, fit scorecard and honest apply/stretch/skip verdict for a posting, with truthful resume edits. Runs the job-hunting skill's Qualifier role.
argument-hint: [posting URL or pasted posting]
disable-model-invocation: true
---

Use the `job-hunting` skill, role **Qualifier** (`${CLAUDE_SKILL_DIR}/../job-hunting/references/jd-match.md`). Posting: $ARGUMENTS
If that is empty, ask for the posting URL or text before proceeding.

1. Run `sh ${CLAUDE_SKILL_DIR}/../job-hunting/scripts/jh workspace.py where`; read profile.md first and never re-ask what it answers.
2. With a URL: run `sh ${CLAUDE_SKILL_DIR}/../job-hunting/scripts/jh fetch_posting.py <url> --save` and read the saved file under `postings/`. If fetch_posting prints a message starting `unavailable:`, the board did not answer — ask the user to paste the posting text instead of treating the job as gone.
3. Run jd-match end to end, in its order: fetch → extract → knockout pre-check → score → legitimacy block (the cap on the honest verdict) → optimize (truthful before/after edits) → record (`sh ${CLAUDE_SKILL_DIR}/../job-hunting/scripts/jh tracker.py add --company "<X>" --role "<Y>" --stage saved`).
4. For a full rebuild rather than posting-specific edits, hand off to `/job-hunter:resume`.
5. End with the `saved:` line naming `postings/<file>` and the pipeline row.
