---
name: search
description: Find fresh job openings matching the saved criteria, ranked with fit and red flags. Runs the job-hunting skill's Scout role.
argument-hint: [role or location tweaks]
disable-model-invocation: true
---

Use the `job-hunting` skill, role **Scout** (`references/sourcing.md`). Tweaks: $ARGUMENTS

1. Resolve storage mode (workspace: `python3 ${CLAUDE_SKILL_DIR}/../job-hunting/scripts/workspace.py where`).
2. Read the profile's search criteria; echo them in one line; apply the tweaks above as adjustments, not replacements.
3. Workspace mode: run `python3 ${CLAUDE_SKILL_DIR}/../job-hunting/scripts/search_jobs.py --markdown` (add `--days 2` for a daily digest) and present the shortlist it prints, adding fit reasoning and the referral path per row per `references/networking.md`. Chat mode: follow the fallback ladder in `references/sourcing.md` and say which rung was used.
4. Offer to save chosen rows to the pipeline (`python3 ${CLAUDE_SKILL_DIR}/../job-hunting/scripts/tracker.py add`) and to fetch full postings (`python3 ${CLAUDE_SKILL_DIR}/../job-hunting/scripts/fetch_posting.py <url> --save`).
