---
name: today
description: What to do today — overdue follow-ups, stale applications, interviews this week, auto-cold candidates, contacts due. Runs the job-hunting skill's Operations role.
argument-hint: [optional date YYYY-MM-DD]
disable-model-invocation: true
---

!`python3 ${CLAUDE_SKILL_DIR}/../job-hunting/scripts/tracker.py today`

Use the `job-hunting` skill, role **Operations** (`references/pipeline.md`). Date override: $ARGUMENTS

1. The block above is today's report from the workspace pipeline (if it says no workspace exists, offer `python3 ${CLAUDE_SKILL_DIR}/../job-hunting/scripts/workspace.py init`; in chat mode compute the same sections from the profile's §9 tables).
2. Turn each section into concrete actions: draft the overdue follow-ups, name the next action for stale rows, confirm before applying any auto-cold change (`python3 ${CLAUDE_SKILL_DIR}/../job-hunting/scripts/tracker.py set --company <X> --stage cold`), list contacts due with their touch.
3. Close with the day's plan: fresh postings sweep (`/job-hunter:search` with `--days 2`), applications capped per the profile's cadence, outreach target.
4. Write back every change; end with the `saved:` line.
