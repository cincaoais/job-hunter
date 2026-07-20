---
description: Step-by-step guided walkthrough of the whole job hunt, one stage at a time
argument-hint: where you are — searching, interviewing, offer, etc. (optional)
---

Use the `job-hunting` skill to run a guided, one-step-at-a-time walkthrough of the user's job hunt, following SKILL.md Steps 0–2.

Where the user is (optional): $ARGUMENTS

1. FIRST, do Step 0 / Step 1: read the Candidate Profile (the one source of truth); if none exists, build one from the template by ingesting any existing resume/LinkedIn before asking, then filling only genuine gaps in grouped questions.
2. Determine which stage they're in — setup, finding openings, applying (resume/cover letter), interviewing, or offer — using $ARGUMENTS if given, otherwise inferring from the profile and search status, confirming in one line.
3. Guide only the CURRENT stage, routing to the matching Step 2 feature (positioning/fit, finding live openings, resume-builder/revamp, jd-match, interview-prep/coach, company-dossier, offer-coach, funnel diagnosis). Never dump the whole journey at once — finish one step, then offer the next.

Honor the honesty guardrail: never invent metrics, titles, or achievements. If anything changed, regenerate the full updated profile at the end and tell the user to save it back.
