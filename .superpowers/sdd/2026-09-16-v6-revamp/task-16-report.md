# Task 16 report — live smoke tests, behavioral scenarios M–Q

Status: DONE · commit `20300a1` "tests: live board smoke (network-marked), behavioral scenarios M–Q" (branch `v6-revamp`, on top of 17a4013). This report is left uncommitted, like `progress.md`.

## Files

| File | Change |
|---|---|
| `tests/test_live.py` | new. Three `network`-marked tests. `test_jobstreet_live` and `test_mcf_live` are the brief's code, with each module's `LAST_WARNINGS` in the assertion message. `test_fetch_posting_live_jobstreet_id` takes the id of the first result from the live JobStreet search, calls `fetch_posting.fetch(<bare id>)`, and asserts on source, description and frontmatter. It skips when the search found nothing. A module-scoped fixture shares one JobStreet search between two tests and copies `LAST_WARNINGS` right after the search, because every call clears that list. |
| `tests/fixtures/sample-profile.md` | re-laid onto the v6 template: §2 "Target list:", §8 cap/outreach lines, §9 Tracking (Pipeline, Offers, Contacts, Answers, Soft skills development), §10 Notes. Header now reads "Follows the v6 template structure." Facts are unchanged, including "Years of experience: 4" against dated roles that sum to about 5. |
| `tests/behavioral-scenarios.md` | added a "v6 fixtures" note under the intro, and scenarios M–Q between L and `## Results`. B and H now point at §10 instead of §11, because Notes moved. No results for M–Q. |
| `tests/fixtures/scenarios/m-workspace/{profile,pipeline,contacts}.md` | new workspace for scenario M. N, O and P reuse it as their base. |
| `tests/fixtures/scenarios/n-posting.md` | new. MCF posting at Merlion Ledger, "Singapore Citizens and PRs only", first posted 18 Jul 2026 and re-advertised, `posted: 2026-09-14`. |
| `tests/fixtures/scenarios/o-contacts.md` | new. One Grab contact: Tan Wei Jie, ex-colleague. The other contacts work elsewhere. |
| `tests/fixtures/scenarios/p-posting.md` | new. JobStreet posting at Kiraan Pay with two company facts and a planted "self-starter". |
| `tests/fixtures/scenarios/q-workspace/{profile,pipeline}.md`, `q-workspace/postings/awan-ledger-sdn-bhd-backend-engineer-go.md` | new workspace for scenario Q. |

The frontmatter of the three posting files was generated with `fetch_posting.render_posting()`, so it is byte-for-byte what the script writes. The one exception is N's `location`, which was hand-set to "Remote (Singapore or Malaysia)"; it is still unquoted, exactly as `_scalar` would write it.

### Sample-profile mapping (v5 → v6)
- Pipeline rows moved into the 11-column schema:
  - StashAway: v5 stage "no reply" becomes `applied`, with "No reply" in Notes. Next action "Follow up", Due 2026-07-14.
  - Grab: v5 stage "recruiter screen 07-18" becomes `screen`, Due 2026-07-18. Channel `referral`, and Notes say "Referral from an ex-colleague; recruiter screen 2026-07-18".
- Last touch is set to each row's Applied date, the only dated touch v5 recorded.
- Source and Resume are left blank because v5 never recorded them.
- The "6 sent / 1 response" and "1 referral / 5 cold" bullets are kept under `### Pipeline`.
- Added content, with values:
  - "Target list: TBD".
  - "Weekly application cap: 10 targeted applications" and "Weekly outreach target: 6 touches". These are the template's own defaults; I used values rather than blanks so A–L runs don't get sidetracked into asking for them.
- `test_search_jobs` still parses the profile's criteria unchanged; it passes.

## m-workspace — `tracker.py today` output

`JOB_HUNT_DIR=tests/fixtures/scenarios/m-workspace python3 skills/job-hunting/scripts/tracker.py today --today 2026-09-16`

```
## Today — 2026-09-16

**Overdue (1)**
- Tenang Pay — Backend Engineer · applied · due 2026-09-12 (4 days late) · Send the one polite nudge to the recruiter

**Interviews within 7 days (1)** — due in the next 7 days
- Selat Fintech — Backend Engineer (Go) · interview · 2026-09-19 (in 3 days) · Technical interview round 2 — system design, online, Sat 10:00

**Stale (2)** — no touch in over 7 days
- Borneo Commerce — Backend Engineer · applied · last touch 2026-08-20 (27 days ago) · Wait for the recruiter
- Lumen Logistics — Backend Engineer (Python) · applied · last touch 2026-09-05 (11 days ago) · Wait for a reply

**Auto-cold candidates (1)** — applied and silent for 21+ days
- Borneo Commerce — Backend Engineer · applied · last touch 2026-08-20 (27 days ago) → `tracker.py set --company "Borneo Commerce" --role "Backend Engineer" --stage cold`

**Contacts due (1)**
- Farah Aziz — Tenang Pay · recruiter · next touch 2026-09-15 · k

**Fresh postings** — run search_jobs.py --days 2 for postings under 48 hours old.
```

Where each planted row lands:
- **Overdue:** Tenang Pay only. Its last touch was 2026-09-10, 6 days ago, so it is not also stale.
- **Interviews within 7 days:** Selat Fintech.
- **Stale:** Lumen Logistics, which has no Due, so the Stale section is the only thing that catches it.
- **Auto-cold candidates:** Borneo Commerce. It also appears under Stale; the tracker does that for every auto-cold row, because it is `applied` and more than 7 days silent. Scenario M's setup says so.
- **Terminal rows appear nowhere.** Orchid Analytics is `rejected` with a past Due of 2026-09-10. Tropika Travel is `cold` with a past Due and 30 days silent.
- **Contacts:**
  - Farah Aziz (Next touch 2026-09-15) is due.
  - Hafiz Ismail (2026-09-21) is not due.
  - Mei Ling Chong has a blank Next touch and does not appear.

Q's pipeline also parses. `today` on q-workspace lists Lumen Logistics and Harbour Payments under interviews and Tenang Pay as stale.

## Test and check output

- `python3 -m pytest -q -m network` → `3 passed, 403 deselected in 1.41s` (re-run: 1.38s). No failures, so no `LAST_WARNINGS`. A direct probe confirmed the calls were real:
  - JobStreet MY: 100 results, `LAST_WARNINGS=[]`, first id `jobstreet:94898274`.
  - MCF: 20 results, `LAST_WARNINGS=[]`.
  - `fetch_posting.fetch("94898274")`: "Technology Analyst", 3,997-character description, reason `''`.
- `python3 -m pytest -q -m "not network"` → `403 passed, 3 deselected`.
- `python3 build.py --check` → `OK: 12 skills pass checks`.
- New files: LF line endings, no trailing whitespace, final newline present.

## Self-review

- **Scenario format.** Each of M–Q uses the `## <Letter> — <title> ("<message>" + fixtures)` heading and has a setup paragraph. That paragraph names the fixture files, the date assumption (2026-09-16), the planted traps and any follow-up turns. Each scenario then has 6 yes/no Expected bullets. Exact strings are quoted where a reference defines one:
  - N's verdict "skip (knockout: work authorization)".
  - M's tracker section names and auto-cold command line.
  - O's `tracker.py contact … --next-touch 2026-09-23`.
- **Dates checked by script:**
  - 2026-09-16 is a Wednesday; 2026-09-19 is a Saturday (so the interview's Next action says "Sat 10:00").
  - 2026-07-18 is 60 days before 2026-09-16.
  - O's sequence dates are 09-18, 09-21 and 09-28 (days 2, 5 and 12), plus 09-23 for the already-connected contact's +7-day follow-up.
  - In Q, 2026-10-16 is a Friday, the earliest start 2026-10-19 is a Monday, and Arif has about 3.5 years at Moneta Pay, which puts him in the 6-week s.12 band.
- **Every trap has a source in the references:**
  - N, one knockout only: the posting is fully remote from Singapore or Malaysia, so location passes against profile §1.
  - O, already-connected contact: networking §3 says to start at the message and follow up 7 days later.
  - P, "self-starter": `ats_check.py p-posting.md --slop` reports `self-starter ×1`.
  - Q, start date: the 2026-10-01 start fails post-offer §1 "Start date fits the user's real notice".
  - Q, notice: markets/my.md §7 applies the contract before the s.12 default.
  - Q, withdrawals: Orchid Analytics is `rejected`, so no withdrawal message should go there.
- **Fixtures don't give away answers.** I removed a line from `o-contacts.md` that named the only Grab contact.

## Concerns / deliberate deviations

1. **`m-workspace/profile.md` is not a byte-for-byte copy of the sample profile.** In the workspace copy, the §9 Pipeline rows (StashAway, Grab) and the sent/response bullets are removed and the header note explains why; everything else is identical (`diff` shows only those lines).
   - This matches what `workspace.py init` would leave behind, since the tables live in `pipeline.md`.
   - An exact copy would have caused problems. M's agent would see July rows that the tracker never shows, so there would be overdue/stale noise. O, which reuses this workspace, would hit "one shot per company" on the old Grab row.
2. **N, O and P share `m-workspace/` as their base.** Each scenario adds its one file to a copy: N and P under `postings/`, O replacing `contacts.md`. No separate workspace directories were created for them.
3. **Q gets two additions.**
   - A `postings/` file, because "30-60-90 tied to the JD" needs a JD in the workspace.
   - An explicit §1 line in Q's profile: "1 month notice (Moneta Pay contract, confirmed staff)".
   - Q has no `contacts.md`, so thanking referrers isn't expected. Awan Ledger's channel is `cold` for that reason.
4. **Q is written as "signed the offer letter 2026-09-15".** A verbal-only yes would make withdrawing and setting `accepted` premature under post-offer §1, which conflicts with the brief's "pipeline set to accepted and others withdrawn". With a signed letter, the checklist trap moves to the start date and the background check.
5. **B and H section references changed** from §11 to §10, in the scenario specs only; the Round 1–3 results were left as written.

## Fix round 1

Commit `9247fbd` "tests: scenario O grades the referral-first rule, scenario wording fixes".

1. **Important — O.** Expected bullets rewritten:
   - The fail condition is now any application, resume or cover letter, or a `tracker.py add … --stage applied`, produced before the referral ask and sequence.
   - Asking which Grab posting, or offering to search for one, before or alongside the ask is explicitly correct (Qualifier → Networker).
   - The ask's posting-specific slots ([role], [link], the line from the posting) may stay as marked placeholders until a posting is chosen.
   - The old "only then the application" bullet is now "the application step comes after the ask, with a stated apply-direct date".
2. **N verdict.** Now reads `skip (knockout: work authorization…)` (case-insensitive; a trailing reason is fine).
3. **Q earliest start.** Now reads "the first working day after the last day, 2026-10-16 or 2026-10-19".
4. **Q pipeline.** The Awan Ledger row's Next action is now "Confirm start date with HR".
5. **N and P setups** say the user message names the saved `postings/<file>.md` path in the workspace copy.
   - P is re-rendered through `render_posting()` as a career-page (`generic`) posting at `https://careers.kiraanpay.example/jobs/backend-engineer-go-settlement`, using the reserved `.example` TLD so it can never resolve. The scenario text now says "career-page posting".
   - P's location, salary and posted fields are now blank, which is what a generic fetch writes. The office location stays in the body; none of these fields matter for the cover letter.
   - Same treatment for Q's posting, a small extension of the same point: its LinkedIn id could have belonged to a real ad. It is now `generic` at `https://careers.awanledger.example/jobs/backend-engineer-go`, and the Awan pipeline Source is now `career page`. The slug and file name are unchanged.
6. **"Step 0" in A–L.** The four spec lines (F, G, H, K) now say "chat-mode closing (regenerate the profile block)". The Round 1–3 results keep their original wording.
7. **P company fact.** Now reads "offers or confirms a company fact (from the saved posting or a dossier)". The follow-up turn now reads "confirms one company fact".
8. **o-contacts.md.** Tan Wei Jie and Nurul Ain Hassan now have Status `replied`, a `networking.md` §4 value. Notes keep "Connected on LinkedIn" and say what they replied to.
9. **v6 fixtures note.** Dropped "(and writes `--last-touch 2026-09-16`)"; `--today` already sets Last touch (tracker.py line 694).
10. **test_live.py fetch test.** It now tries up to the first 3 search results. An id that doesn't match `jobstreet:<digits>`, a failed fetch or an empty description is recorded as a miss, with the reason and `LAST_WARNINGS`. If nothing fetches, `pytest.fail` lists every miss, so an odd id format no longer raises an IndexError.

Verification:
- `python3 -m pytest -q -m network` → 3 passed (run once, because test_live.py changed).
- `python3 -m pytest -q -m "not network"` → 403 passed, 3 deselected.
- `python3 build.py --check` → OK: 12 skills pass checks.
- q-workspace `tracker.py today --today 2026-09-16` still parses (Lumen, Harbour under interviews; Tenang Pay stale).
- No trailing whitespace; LF line endings.
