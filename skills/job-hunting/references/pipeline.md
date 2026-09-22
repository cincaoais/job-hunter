# Pipeline — the Operations role

The tracker is the coach: every application, touch and reply is logged, the
today view says what to do, and the weekly funnel says what to change. Run
the search like a sales pipeline, not a pile of sent emails.

## 1. Schema

`pipeline.md` (workspace) or profile §9 (chat mode) — one row per
company + role:

| Company | Role | Source | Channel | Applied | Stage | Next action | Due | Last touch | Resume | Notes |

- **Stage** vocabulary, exact: `saved` · `applied` · `screen` · `interview`
  · `final` · `offer` · `accepted` · `rejected` · `withdrawn` · `cold`.
- **Source** = where the application went (JobStreet, MCF, LinkedIn, career
  page, agency, referral). **Channel** = `cold` / `referral` /
  `recruiter-inbound` / `agency`.
- **Resume** names the variant file actually sent (`resumes/<company>-<role>-v2.md`).
- Dates are `YYYY-MM-DD`; never a `|` in a cell.
- `contacts.md` holds the networking CRM (`networking.md` owns its rules).
  Offers live in the `## Offers` table (`offer-coach.md` fills it).

## 2. Logging rules

- Log every application the day it goes out, with Source, Channel and
  Resume version: `tracker.py add --company X --role Y --source S --channel
  C --stage applied --resume <file>`.
- Next action and Due are always set; a row without them is invisible to
  the today view. Stage changes: `tracker.py set --company X [--role Y]
  --stage screen --next "Prep the screen" --due 2026-09-23`.
- Follow-up: one polite nudge at Due + 7 days, never a second.
- Interviews: set Due to the interview date; the round type goes in Next
  action.
- Auto-cold: an `applied` row silent for 21 days (`AUTO_COLD_DAYS = 21`) is
  proposed for `cold`; apply it only after the user confirms.
- Rejections count as responses only when a human replied: put "rejected by
  email", "replied" or "response" in Notes; "no reply" / "never replied" /
  "without response" are not responses.
- Every write sets Last touch to today (`--last-touch` overrides).
- Contacts: `tracker.py contacts` lists touches due (Next touch ≤ today);
  `tracker.py contact --name … --next-touch …` upserts a row.
- A Gmail MCP connector, when present, may be used to spot recruiter replies
  and log them — opportunistic, never required.
- A Calendar MCP connector, when present, may be used to pick up interview
  dates into Due — opportunistic, never required.

## 3. The today view — `tracker.py today`

The `today` skill runs it inline. Sections appear in this order and only
when non-empty:

| Section | Rule | What to do |
|---|---|---|
| Overdue | Due before today, non-terminal stage | Draft the follow-up now; move Due or close the row |
| Due today | Due = today | Do the next action; log the touch |
| Interviews within 7 days | Due in the next 7 days, stage screen/interview/final | Start the prep pack (`interview-prep.md`), book a mock |
| Stale | No touch in over 7 days (`STALE_DAYS = 7`), stage applied…final | Set a concrete next action, or send the one nudge if Due + 7 has passed |
| Auto-cold candidates | `applied` and silent 21+ days | Confirm, then run the printed `tracker.py set … --stage cold` line |
| Contacts due | `Next touch` ≤ today (same list as `tracker.py contacts`) | Send the touch from `networking.md`; log with `tracker.py contact --name … --next-touch …` |
| Fresh postings | always last | `search_jobs.py --days 2` for postings under 48 hours old |

When every section is empty it prints
`Nothing due — run search_jobs.py --days 2 for fresh postings.`
— that is the cue to source and to do outreach, not to rest.

Chat mode: compute the same sections from the profile's tables by hand,
in the same order.

## 4. The weekly review ritual — Monday

1. `tracker.py digest` (the `review` skill runs `tracker.py funnel` inline
   first) — writes `reviews/<date>.md` with the funnel and today view and
   updates `_Last weekly review: <date>_` in `pipeline.md`. Chat mode: record
   the date in the profile.
2. Read the two tables (by Channel, by Source) and the `Leak:` line.
3. Apply **one** change this week — the fix the leak names, or the user's
   own refinement of it. One change, so next week's numbers mean something.
4. Set next week's cap and outreach target in profile §8 on the lines
   "Weekly application cap:" and "Weekly outreach target:": 10–20 targeted
   applications; 60/40 outreach to applications by time spent.
5. Check wellbeing (§6) before closing.

Run the review when the user asks how the search is going, when about ten
applications have accumulated, or when the tracker has not been touched for
two weeks.

## 5. Funnel and leak diagnosis

Counting: **Sent** = every row not `saved`; **Responses** = stage in
screen/interview/final/offer/accepted plus `rejected` rows whose Notes show a
human reply; **Interviews** = interview/final/offer/accepted; **Offers** =
offer/accepted. Benchmarks printed under the table:
`cold ~3% interview, referral ~40%, recruiter-inbound ~25% — Ashby 2025/26`.

The script picks the first failing stage and prints one recommended change:

| Branch | Rule | Recommended change (verbatim from the script) |
|---|---|---|
| too small | sent < 10 | Pipeline too small to diagnose (n<10) — keep logging |
| targeting | sent ≥ 10 and response % < 10 | Tighten targeting: re-run the knockout pre-check on the last 10 applications and move to referral-first outreach (networking.md) |
| screen | responses ≥ 3 and interviews == 0 | Screens aren't converting: run a mock recruiter screen (interview-coach.md) and rework the six prepared answers |
| close | interviews ≥ 3 and offers == 0 | Onsites aren't closing: debrief each final round, run the offer-stage questions, and rehearse negotiation (offer-coach.md) |
| healthy | none of the above | No clear leak — hold the cadence: keep 10–20 targeted applications and 60/40 outreach per week |

Read the channel split before accepting the diagnosis: a cold-only pipeline
at 3% is performing at benchmark, and the change is channel mix
(`networking.md`), not the resume. Three rejections at the same stage point
at that stage's coach file; a targeting leak goes to `strategy.md`.

## 6. Cadence and wellbeing

- **Weekly cap** 10–20 targeted applications, 60/40 outreach to
  applications by time spent: 11–20 applications → ~9% interview rate,
  100+ → ~2.6% (Huntr Q1 2026, 140k applications). Quality of fit, not
  volume, moves the funnel.
- **Batch and rest**: source and apply in two or three blocks a week; keep
  one weekday application-free. Interview weeks pause new applications.
- **Runway-aware urgency**: under 3 months of runway → widen targets one
  notch, add agencies and contract roles (`markets/<cc>.md`), raise the cap
  to 20; over 6 months → hold the bar and the referral-first rule.
- **Expect 82–108 days** for a median search (Huntr Q1/Q2 2026); say so
  at the start so week six does not read as failure.
- **Rejection reframing** — one line, then move on: a rejection is one
  reader's decision on one day; a form rejection carries no information
  about the user; a rejection after a final round means the profile is
  interviewing at the right level.
- **Rest week trigger**: three rejections in one week, or two weeks of zero
  responses, → propose a rest week (no new applications; outreach and prep
  only) and run the funnel review before restarting.
- Ghosting is structural (about half of applicants are ghosted): the
  auto-cold rule exists so silence stops costing attention.

## 7. Record

Workspace mode: every change is a `tracker.py` call or an in-place edit;
end with the `saved:` line. Chat mode: regenerate the profile block
(SKILL.md closing step).
