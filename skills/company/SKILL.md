---
name: company
description: One-page, live-searched, cited company dossier before an interview or application. Runs the job-hunting skill's Coach role.
argument-hint: [company name]
disable-model-invocation: true
---

Use the `job-hunting` skill, role **Coach** (`references/company-dossier.md`). Company: $ARGUMENTS

1. Resolve storage mode (workspace: `python3 ${CLAUDE_SKILL_DIR}/../job-hunting/scripts/workspace.py where`); read the profile and any pipeline row or saved posting for this company so "likely themes" map to real evidence.
2. Research live in decision-value order (product, health and news, stack and team, comp intel from `references/markets/<cc>.md` sources, interview process, culture); cite everything; label anecdote as anecdote.
3. Produce the one-page table plus why they're hiring, 3–5 likely themes mapped to profile evidence, and 3–5 researched questions to ask.
4. Save to `dossiers/<company>.md` (workspace) or inline (chat); write the one-line takeaway and red flags into the pipeline row's Notes.
