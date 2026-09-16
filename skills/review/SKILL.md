---
name: review
description: Weekly funnel review — sent → response → interview → offer by channel and source, leak diagnosis, and one concrete change. Runs the job-hunting skill's Operations role.
argument-hint: [optional date YYYY-MM-DD]
disable-model-invocation: true
---

!`python3 ${CLAUDE_SKILL_DIR}/../job-hunting/scripts/tracker.py funnel`

Use the `job-hunting` skill, role **Operations** (`references/pipeline.md`, weekly review ritual). Date override: $ARGUMENTS

1. The block above is the funnel from the workspace pipeline (if it says no workspace exists, offer `python3 ${CLAUDE_SKILL_DIR}/../job-hunting/scripts/workspace.py init`; in chat mode compute it from the profile's §9 tables).
2. Read the leak diagnosis and benchmarks; confirm or refine the one recommended change; check cadence and wellbeing (cap, rest week, runway).
3. Workspace mode: write the review with `python3 ${CLAUDE_SKILL_DIR}/../job-hunting/scripts/tracker.py digest` (saves `reviews/<date>.md` and updates the last-review line). Chat mode: record "Last weekly review: <date>" in the profile.
4. Set next week's application cap and outreach target in the profile's §8; end with the `saved:` line.
