---
name: today
description: What to do today — overdue follow-ups, debriefs due, interviews this week, stale and auto-cold applications, contacts due — or, with `week`, the weekly funnel review and the one change to make. Runs the job-hunting skill's Operations role.
argument-hint: [week] [optional date YYYY-MM-DD]
disable-model-invocation: true
---

Use the `job-hunting` skill, role **Operations** (`${CLAUDE_SKILL_DIR}/../job-hunting/references/pipeline.md`). Arguments: $ARGUMENTS

1. Read the arguments: `week` selects the weekly review; a YYYY-MM-DD date means pass `--today <date>` to every tracker.py command below.
2. Daily (default): run `sh ${CLAUDE_SKILL_DIR}/../job-hunting/scripts/jh tracker.py today [--today <date>]`. If it says no workspace exists, offer `sh ${CLAUDE_SKILL_DIR}/../job-hunting/scripts/jh workspace.py init` and stop. Then turn each section into concrete actions: draft the overdue follow-ups, Debriefs due → run the debrief (`/job-hunter:interview debrief`), name the next action for stale rows, confirm before applying any auto-cold change (`sh ${CLAUDE_SKILL_DIR}/../job-hunting/scripts/jh tracker.py set --company "<X>" --role "<Y>" --stage cold`), list contacts due with their touch.
3. Daily, close with the day's plan: fresh postings sweep (`/job-hunter:search --days 2`), applications capped per the profile's cadence, outreach target.
4. Weekly (`week`): run `sh ${CLAUDE_SKILL_DIR}/../job-hunting/scripts/jh tracker.py funnel [--today <date>]`. Read the leak diagnosis and benchmarks; confirm or refine the one recommended change; check cadence and wellbeing (cap, rest week, runway). Write the review with `sh ${CLAUDE_SKILL_DIR}/../job-hunting/scripts/jh tracker.py digest [--today <date>]` (saves `reviews/<date>.md` and updates the last-review line). Set next week's application cap and outreach target in the profile's §8.
5. Write back every change; end with the `saved:` line.
