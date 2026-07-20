---
description: Find live job openings with fit scores, red-flag checks, and referral links
argument-hint: role or location tweaks (optional)
---

Use the `job-hunting` skill and follow SKILL.md's **Finding live openings** flow.

1. Read the candidate profile first (skill Step 0/1) — one source of truth. Treat anything in `$ARGUMENTS` below as tweaks to the saved role/location/criteria, not a replacement.
2. Confirm or refine the profile's search criteria before searching (Step 1.5), then run the flow as written: build queries, search the boards the profile names live (connector or browser if available, otherwise scoped web search — never from memory), filter hard, and return the ranked shortlist with Fit /10, red flags, and the per-role LinkedIn referral links the flow specifies.

Honesty guardrail: never invent metrics, titles, achievements, listings, or salary numbers — flag likely ghost jobs and scams rather than presenting them clean. Regenerate the updated profile at the end if anything changed.

Tweaks: $ARGUMENTS
