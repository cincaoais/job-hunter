---
description: Show the job-hunting feature menu, then ask which to run
---

Use the `job-hunting` skill and follow its **Feature Guide** flow (`references/feature-guide.md`).

First read the candidate profile (skill Step 0/1 — the one source of truth) so any follow-up is grounded in what's already known.

Then present the feature menu table from feature-guide.md and **ask which feature the user wants** — don't just dump the table and stop. Remind the user that every feature is also reachable by describing the task in plain English, not only through a slash command.

Route into the chosen feature's real flow rather than re-explaining it. Honor the honesty guardrail (never invent metrics, titles, or achievements), and regenerate the updated candidate profile at the end if anything changed.
