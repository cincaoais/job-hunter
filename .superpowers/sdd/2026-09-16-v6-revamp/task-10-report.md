# Task 10 report — sourcing.md, pipeline.md, today/review wiring

## What I wrote

- `skills/job-hunting/references/sourcing.md` — 123 lines. Sections: the
  four-rung fallback ladder with the "state the rung" rule and the exact
  `search_jobs.py` invocations/flags; how to read the script's output
  (`## N new postings …` title, main table columns, `### Needs a look`,
  `### Knocked out`, the `Sources:` line and its stopped/skipped meanings);
  freshness and cadence (`--days 2` daily, `--days 7` weekly, `/loop 1d
  /job-hunter:search`, weekly cap 10–20, one shot per company); direct-channel
  routing (Easy Apply 1–4% vs direct 2–3×, log Source truthfully); agencies →
  `markets/my.md`/`sg.md`; ghost/scam heuristics moved from the old SKILL.md
  with the MCF applicant-count nuance; the presentation table (script columns
  + Fit /10, Why it matches, Red flags) and the verbatim LinkedIn people-search
  referral links framed as searches; feed-forward to jd-match, networking,
  strategy, plus the politeness note (≤ 3 LinkedIn pages).
- `skills/job-hunting/references/pipeline.md` — 132 lines. Sections: schema
  and exact stage vocabulary; logging rules (Source/Channel/Resume the day it
  goes out, Next action + Due always, one nudge at Due + 7, auto-cold 21 days
  after confirmation, the reply-note rule with negations, Gmail/Calendar
  opportunistic line); the today view as a table of section → rule → action in
  the script's order plus the `Nothing due` line; the Monday review ritual
  (`tracker.py digest`, one change, cap and 60/40 target, wellbeing check);
  funnel counting rules, the benchmarks line, and the five-branch leak table
  quoting the script's FIX strings verbatim; cadence and wellbeing (cap,
  batch-and-rest, runway rules, 80–110 day expectation, rejection reframes,
  rest-week trigger, ghosting note); record step.

## Wiring check (no edits needed)

- `skills/today/SKILL.md` and `skills/review/SKILL.md` already carry the
  inline `` !`python3 ${CLAUDE_SKILL_DIR}/../job-hunting/scripts/tracker.py today` ``
  / `funnel` line as the first body line, and their bodies tell the model how
  to act per section (today) and how to apply the one change and set next
  week's cap (review). Left unchanged.
- `skills/job-hunting/SKILL.md` contains no leftover ghost/scam or funnel
  prose — only the one-paragraph "Sourcing in one breath" pointer and the
  Operations row. Left unchanged.

## Script facts quoted and verified

Verified programmatically against `tracker.py` constants (string containment
in `pipeline.md`): `FIX_TARGETING`, `FIX_SCREEN`, `FIX_CLOSE`, `FIX_TOO_SMALL`,
`FIX_HEALTHY`, `BENCHMARKS`, `NOTHING_DUE` — all present verbatim.
Thresholds quoted: `STALE_DAYS = 7`, `AUTO_COLD_DAYS = 21`,
`INTERVIEW_WINDOW_DAYS = 7`. Diagnose ladder and Responses rule copied from
`tracker.py funnel --help`. `search_jobs.py --help` flags and the output
shape (`NEEDS_LOOK_ROWS`, `MISSING_MUST_HAVE`, `Sources:` line, knocked-out
not written to seen) from the script. `fetch_posting.py --help`: `--save`,
`--stdin`, exit 3 blocked.

## Checks

```
$ python3 build.py --check
OK: 12 skills pass checks
$ python3 -m pytest -q -m "not network"
275 passed in 0.54s
```

Line endings LF; no forbidden links (`feature-guide`, `tech-role-map`,
`sea-market-notes`); angle-bracket matches are placeholders only
(`<Company>`, `<url>`, `<cc>`, `<date>`, `<file>`, `<role>`, `<city>`).

## Commit

`8fe5cc0` — sourcing.md + pipeline.md: fallback ladder, freshness, cadence,
funnel diagnosis; today/review skills run tracker first (trailer: Claude
Fable 5.1).

## Self-review

- Both files stay inside 80–180 lines and are imperative.
- Every command shown exists with those flags (`add`, `set`, `contact`,
  `digest`, `today`, `funnel`; `search_jobs.py --markdown --days --all`).
- The referral-link URLs are byte-identical to the brief's pattern.
- Brief item "shortlist presentation table (today's columns plus Posted and
  Source)" satisfied by the merged 11-column table in sourcing.md §6.

## Concerns

- `sourcing.md` links `markets/my.md`, `markets/sg.md`, `strategy.md`,
  `networking.md`, and `pipeline.md` links `networking.md`, `strategy.md`,
  `markets/<cc>.md` — all planned for Tasks 11–12 and not yet on disk.
- The "80–110 days median search" and "about half of applicants are ghosted"
  figures are from the research reports (Huntr Q1/Q2 2026, Fortune/Criteria
  2026) and are stated without citations inside the reference, matching the
  house style of the other reference files.

## Fix round 1

Findings → changes (all in `sourcing.md` / `pipeline.md` only):

1. Knocked-out reasons — `sourcing.md` §2 now lists exactly `dealbreaker:
   <phrase>`, `salary below floor`, `missing must-have`, and states that
   postings older than `--days` are dropped silently before knockout and
   never listed.
2. `Sources:` example — rewritten to the `_sources_line` shape verified in
   `search_jobs.py:474-488` (count first, warnings in parentheses with the
   `linkedin:` prefix stripped; LinkedIn's warning text from
   `sources/linkedin.py:140`): `linkedin 12 (HTTP 429 at page 2, stopped)`.
3. Politeness — replaced "one request per second per board" with the exact
   LinkedIn-only throttle (`PAGE_DELAY = 2.5`, `MAX_PAGES = 3`, verified at
   `sources/linkedin.py:34-36`) and the `job-hunter-skill` User-Agent from
   `_common.py:24`.
4. `tracker.py contacts` (touches due ≤ today) now named alongside `contact`
   in `pipeline.md` §2 commands and in the today-view Contacts row.
5. Statistics — "halves past 20" replaced in both files with "11–20
   applications → ~9% interview rate, 100+ → ~2.6% (Huntr Q1 2026, 140k
   applications)"; re-applying kept and cited (Huntr Q1 2026); median search
   "82–108 days (Huntr Q1/Q2 2026)"; Easy Apply vs direct "1–4% vs 2–3×
   (Huntr/LinkedIn data)"; Ashby benchmarks untouched (`BENCHMARKS`).

Minors folded in: `fetch_posting.py` invocations prefixed with
`python3 ${CLAUDE_SKILL_DIR}/scripts/`; Needs-a-look 10-row cap + `--json`
noted; `NOTHING_DUE` on one line; `read_criteria` reads §1–§3; 60/40 and
10–20 restated in "Cadence and wellbeing"; Gmail and Calendar split into one
line each; §8 lines "Weekly application cap:" / "Weekly outreach target:"
named in the review ritual.

Line counts: sourcing.md 134, pipeline.md 138 (within 80–180).

```
$ python3 build.py --check
OK: 12 skills pass checks
$ python3 -m pytest -q -m "not network"
275 passed in 0.55s
```

Commit: `8668a2f` — sourcing/pipeline: quote the scripts exactly, cite Huntr,
name tracker.py contacts (trailer: Claude Fable 5.1).
