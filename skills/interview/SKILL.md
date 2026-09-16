---
name: interview
description: Stage-aware interview prep pack for a round, or a live mock interview with honest scoring. Runs the job-hunting skill's Coach role.
argument-hint: [company, role, round — or "mock"]
disable-model-invocation: true
---

Use the `job-hunting` skill, role **Coach**. Context: $ARGUMENTS

1. Resolve storage mode (workspace: `python3 ${CLAUDE_SKILL_DIR}/../job-hunting/scripts/workspace.py where`); read the profile and the pipeline row for this company first — echo company, role, round and date instead of re-asking.
2. Default: `references/interview-prep.md` — pin the round, build the prep pack (six answers, question banks, questions to ask by stage, the market rights sheet from `references/markets/<cc>.md`, the follow-up loop).
3. If the input says "mock": `references/interview-coach.md` — one question at a time, stay in character, probe, score honestly, debrief and file STAR stories.
4. Feed in the company dossier's themes if one exists under `dossiers/`. Coach delivery of real experience only (`references/facts-policy.md`). Update the pipeline row's Next action and Due.
