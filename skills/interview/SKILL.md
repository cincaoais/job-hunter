---
name: interview
description: Stage-aware interview prep pack, a live mock with anchored scoring, a debrief after a round, or (with `company`) a one-page cited company dossier. Runs the job-hunting skill's Coach role.
argument-hint: [company, role, round | mock <mode> | debrief | company <name>]
disable-model-invocation: true
---

Use the `job-hunting` skill, role **Coach**. Context: $ARGUMENTS

1. Run `sh ${CLAUDE_SKILL_DIR}/../job-hunting/scripts/jh workspace.py where`; read profile.md and the pipeline row for this company first; echo company, role, round and date instead of re-asking.
2. Default: `${CLAUDE_SKILL_DIR}/../job-hunting/references/interview-prep.md` — pin the round, build and save the prep pack.
3. `mock`: `${CLAUDE_SKILL_DIR}/../job-hunting/references/interview-coach.md` — one question at a time, stay in character, probe, self-score first, then the anchored rubric and a scorecard.
4. `debrief`: `${CLAUDE_SKILL_DIR}/../job-hunting/references/interview-debrief.md` — questions asked, what landed, outcome, promises and follow-ups; if no pipeline row exists for this company and role, first create one with `sh ${CLAUDE_SKILL_DIR}/../job-hunting/scripts/jh tracker.py add --company "<X>" --role "<Y>" --stage interview` (interview.py refuses to create files without a row).
5. `company <name>`: `${CLAUDE_SKILL_DIR}/../job-hunting/references/company-dossier.md` — read profile.md and any saved posting so likely themes map to real evidence; research live in decision-value order (product, health and news, stack and team, comp intel from `${CLAUDE_SKILL_DIR}/../job-hunting/references/markets/<cc>.md` sources, interview process, culture); cite everything; label anecdote as anecdote. Produce the one-page table plus why they're hiring, 3–5 likely themes mapped to profile evidence, and 3–5 researched questions to ask; save to `dossiers/<company>.md`; write the one-line takeaway and red flags into the pipeline row's Notes via `sh ${CLAUDE_SKILL_DIR}/../job-hunting/scripts/jh tracker.py set --company "<X>" --role "<Y>" --note "<takeaway>"`.
6. Create and update interview files only through `interview.py` (`new`, `outcome`, `bank`) via the jh launcher; never hand-write the frontmatter.
7. Coach delivery of real experience only (`${CLAUDE_SKILL_DIR}/../job-hunting/references/facts-policy.md`). Update the pipeline row's Next action and Due; end with the `saved:` line.
