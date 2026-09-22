---
name: network
description: Build the referral map for a target company, draft outreach and follow-ups, and manage the contacts CRM. Runs the job-hunting skill's Networker role.
argument-hint: [company, person, or "due"]
disable-model-invocation: true
---

Use the `job-hunting` skill, role **Networker** (`references/networking.md`). Input: $ARGUMENTS

1. Resolve storage mode (workspace: `python3 ${CLAUDE_SKILL_DIR}/../job-hunting/scripts/workspace.py where`); read the profile and the contacts table first. Workspace mode: run `python3 ${CLAUDE_SKILL_DIR}/../job-hunting/scripts/tracker.py contacts` to list touches due. Chat mode: read the contacts table in the profile and note which Next touch dates are due.
2. For a company: build the referral map (alumni, ex-colleagues, teammates, TA — LinkedIn people-search links framed as searches, never as found people) and the rule is referral **before** application.
3. For a person or message: draft the touch (≤ 150 words, one specific ask) following the 3-touch sequence with dates; never invent shared history.
4. Log every contact and set Next touch. Workspace mode: `python3 ${CLAUDE_SKILL_DIR}/../job-hunting/scripts/tracker.py contact --name X [--company C --role R --relationship REL --target T --last-touch D --next-touch D --status S --note N]` (upserts by Name+Company). Chat mode: edit the contacts table in the profile. `tracker.py add`/`set` are pipeline-only — never use them for contacts.
