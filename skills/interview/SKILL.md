---
name: interview
description: Stage-aware interview prep pack, a live mock interview with anchored scoring, or a debrief after a round. Runs the job-hunting skill's Coach role.
argument-hint: [company, role, round — or "mock <mode>" or "debrief"]
disable-model-invocation: true
---

Use the `job-hunting` skill, role **Coach**. Context: $ARGUMENTS

1. Resolve storage mode (workspace: `python3 ${CLAUDE_SKILL_DIR}/../job-hunting/scripts/workspace.py where`); read the profile and the pipeline row for this company first — echo company, role, round and date instead of re-asking.
2. Default: `references/interview-prep.md` — pin the round, build and save the prep pack.
3. If the input says "mock": `references/interview-coach.md` — one question at a time, stay in character, probe, self-score first, then the anchored rubric and a scorecard.
4. If the input says "debrief": `references/interview-debrief.md` — questions asked, what landed, outcome, promises and follow-ups.
5. Create and update interview files only through `${CLAUDE_SKILL_DIR}/../job-hunting/scripts/interview.py` (`new`, `outcome`, `bank`); never hand-write the frontmatter.
6. Coach delivery of real experience only (`references/facts-policy.md`). Update the pipeline row's Next action and Due; end with the `saved: …` line.
