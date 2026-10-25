---
name: cover
description: Draft or refine a cover letter, outreach note, or screening-question answers for a specific posting. Runs the job-hunting skill's Writer role.
argument-hint: [company and role, or paste the posting]
disable-model-invocation: true
---

Use the `job-hunting` skill, role **Writer** (`references/resume-builder.md` "Cover letters" + `references/answer-bank.md`). Target: $ARGUMENTS

1. Resolve storage mode (workspace: `python3 ${CLAUDE_SKILL_DIR}/../job-hunting/scripts/workspace.py where`); read the profile and `answers.md` first. If no company or posting is named, ask which job this is for.
2. Anti-slop gate before drafting: get one user-supplied story (offer options from the profile's evidence) and one company-specific fact (dossier or posting). No story or no fact → no letter.
3. Draft in the Application Guide's four beats and save it as `letters/<company>-<role>-vN.md` (workspace mode). Then a reviewer pass: dispatch a fresh-context read-only subagent with the posting and the letter inline to flag generic language and weak framing, and revise on its findings (chat mode: do the same critique yourself, one round). Then run the claims audit and `python3 ${CLAUDE_SKILL_DIR}/../job-hunting/scripts/ats_check.py <file> --slop`, replacing every hit (chat mode: both by reading, and say so) — all before the user sees it. For screening-form answers, tailor from `answers.md` and keep them truthful.
4. Show it inline with the one-line audit result and the scan result; iterating overwrites the same file and re-runs both gates. Once approved, deliver as file or paste-ready text as the portal needs and log the touch in the pipeline.
