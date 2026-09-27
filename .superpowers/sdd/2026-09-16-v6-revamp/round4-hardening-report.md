# Round 4 hardening — report

Branch `v6-revamp`, base 9247fbd. Paths below are under `skills/job-hunting/references/` unless stated otherwise.

| # | Edit | Where (after the change) |
|---|---|---|
| 1 | Cover-letter flow gates the letter before the user sees it: save as `letters/…-vN.md`, then the claims audit and the slop scan, then show it, then approval | `resume-builder.md:219-226` |
| 1 | Step 3 note: "(a cover letter is saved and gated before it is shown — see Cover letters)" | `resume-builder.md:21-22` |
| 1 | Stale "gated after approval" wording fixed: step 4 now reads "(a cover letter: before it is shown)", and so does the Claims audit section's "After approval" | `resume-builder.md:24`, `:50` |
| 2 | §1 bullet "No posting chosen yet, or not fresh" (apply-direct date) | `networking.md:18-20` |
| 3 | "Always — even when a warm contact is already on file — give the user two LinkedIn people-search links" | `networking.md:36` |
| 4 | §5 slop-scan line under the heading | `networking.md:91-92` |
| 4 | "One ask only…" note after the Referral ask | `networking.md:97-99` |
| 4 | Application nudge template (≤ 60 words; `--slop` gives no hits) | `networking.md:101-102` |
| 5 | Today view: Overdue row (one nudge, then a Next action that isn't a second nudge, then log once sent) | `pipeline.md:55` |
| 5 | Today view: Stale row (swap a passive "Wait…" for a dated action and propose the `tracker.py set` line) | `pipeline.md:58` |
| 6 | Repost age: "first-posted date (a re-ad keeps the original date) and its age in days as of today" | `jd-match.md:91` |
| 7 | §1: start date checked against notice, with the last working day and the earliest start stated | `post-offer.md:20-22` |
| 7 | §2 "Fill both dates…" | `post-offer.md:32-35` (end of the §2 lead paragraph, directly above the template; see concerns) |
| 7 | §5 new first bullet "Brief references now…" | `post-offer.md:83-86` |
| 7 | §9: withdrawals drafted now, sent once the background check clears and the start date is agreed in writing, then `withdrawn` is set; also the slop-scan line. The "same week" wording is gone | `post-offer.md:140-144` |
| 8 | Cover-letter length follows profile §10 ('concise' → ~250); tone and length are echoed in one line, not asked | `application-guide.md:33-35` |
| 9 | M: turn 3 is now "Sent it. And yes, mark Borneo cold." | `tests/behavioral-scenarios.md:183` |
| 9 | M: bullet 4 "…once the user says it was sent — a new Next action and Due that is not a second nudge" | `tests/behavioral-scenarios.md:196-198` |
| 9 | Q: bullet 3 (withdrawals drafted, send timing, no slop phrases) | `tests/behavioral-scenarios.md:333-337` |
| 9 | Q: bullet 6 (`withdrawn` when the messages are sent; the command is run or given pending that) | `tests/behavioral-scenarios.md:346-348` |

The Results section is untouched.

## Checks

- `python3 build.py --check` → `OK: 12 skills pass checks`
- `python3 -m pytest -q -m "not network"` → `403 passed, 3 deselected`
- Line budgets (HEAD → now): resume-builder 229→235 (+6), networking 135→147 (+12), pipeline 138→138, jd-match 176→176, post-offer 143→155 (+12), application-guide 86→88 (+2). Only `resume-builder.md` is over 180 lines, and it already was (229).
- `grep -rn "same week" skills/job-hunting/references/post-offer.md` → no matches
- `git diff --check` → clean

## Concerns

- **post-offer §2 placement.** "Fill both dates…" is appended to the §2 lead paragraph (the grader's ~line 30, directly above the template), not in a new paragraph after the template. A separate paragraph after the template would have made the file +13 lines, one over the +12 budget. The wording is unchanged.
- **networking.md reflows.** To stay at +12, three existing paragraphs in `networking.md` were reflowed without changing any words: the Fresh-posting bullet, the "No recent post" bullet, and the tail of the §2 search-links paragraph. A few of those lines now run to 77–78 characters.
- **post-offer §9 wording.** Reads "then set `withdrawn`" rather than "in the tracker when they are sent". The sequence ("send each once…, then set") carries the same timing, and the code block above holds the command.

## Review fixes (commit 657c89d)

| # | Finding | Fix (after the change) |
|---|---|---|
| 1 (Medium) | The §9 workspace code block ran `withdrawn` with no condition | Lead-in now reads "Workspace mode — the `withdrawn` line only after that withdrawal is sent:" (`post-offer.md:133`). The gate paragraph now applies to both modes rather than chat mode only: draft now; send once the background check clears and the start date is agreed in writing; then set `withdrawn` (chat mode, by hand) (`post-offer.md:140-144`). Line count stays at 155. |
| 2 (Medium) | `/cover` saved the letter after delivery | Steps 3–4 now run: draft → save `letters/<company>-<role>-vN.md` → claims audit + `ats_check.py <file> --slop` (replace every hit; chat mode by reading) before the user sees it → show inline with the audit and scan results (iterating overwrites and re-gates) → approve → deliver and log the touch (`skills/cover/SKILL.md:12-13`, 13 lines). |
| 3 (Low) | Step 4's parenthetical only covered half of the sentence | "on the approved draft (a cover letter: on the saved draft, before it is shown) — a fresh critical read before any file exists." (`resume-builder.md:23-25`) |

Checks: `build.py --check` → `OK: 12 skills pass checks`; pytest `-m "not network"` → `403 passed, 3 deselected`; `git diff --check` clean. Line counts: post-offer 155 (the budget of +12 from 143 still holds), resume-builder 236 (+7 from 229), cover SKILL.md 13 (limit 20).

## Second pass (commit 870b51b), after the re-run failed O and Q

Paths are under `skills/job-hunting/references/`.

| # | Edit | Where (after the change) |
|---|---|---|
| 1 | "No posting chosen yet" bullet: one reply carries the §2 map (warm contact + recruiter / role-keyword / alumni links), the §5 ask, the §3 dates for the contact and for anyone new from the searches, and the apply-direct date | `networking.md:18-24` |
| 2 | Scan line: before a referral ask is shown, it must have exactly one §5 result and one question (a second result or an 'or …?' counts as a hit) | `networking.md:94-97` |
| 3 | New paragraph above §1: "'I accepted' gets one reply that drafts everything and sends nothing…"; open §1 items gate sending, never drafting. The §9 wording from 657c89d is unchanged | `post-offer.md:9-14` |
| 4 | Cover letters: the claims audit covers every sentence about the user's past (domain words applied to past work, or scenes the profile doesn't state, are dropped) | `resume-builder.md:233-236` |
| 5 | Application nudge: "Quote the result as a plain past fact — no 'since then' or 'most recently' the profile doesn't date." | `networking.md:109-110` |

Line counts (limit is +8 over the length before this pass): networking 147→155 (+8; the scan paragraph was reflowed at 78 columns without changing any words), post-offer 155→162 (+7), resume-builder 236→240 (+4).

Checks: `build.py --check` → `OK: 12 skills pass checks`; pytest `-m "not network"` → `403 passed, 3 deselected`; `git diff --check` clean.
