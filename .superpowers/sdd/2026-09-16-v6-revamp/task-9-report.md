# Task 9 report — `tracker.py`

**Status:** DONE. Commit `9b698a8` on `v6-revamp` (HEAD was `e418dd5`).

## Files

- `skills/job-hunting/scripts/tracker.py` (new, ~690 lines, stdlib only)
- `tests/test_tracker.py` (new, 37 tests)
- `tests/fixtures/pipeline-sample.md` (8 rows + an Offers row, dated against `--today 2026-09-16`)
- `tests/fixtures/contacts-sample.md` (3 contacts: one due, one future, one with a blank Next touch)

## Contract

Pure core (no I/O, no clock): `today_data(rows, contacts_rows, date)`,
`today_report(rows, contacts_rows, date)`, `funnel(rows) -> {"channels", "sources", "total"}`,
`diagnose(f) -> (leak, fix)` (accepts a whole funnel dict or a bare counts dict),
`funnel_report(rows, date)`, `contacts_report(contacts_rows, date)`. Dates may be a
`datetime.date` or an ISO string. I/O: `load(ws)`, `save(ws, cols, rows)`,
`get_contacts(ws)`, `save_contacts(ws, cols, rows)`, `set_review_line(ws, iso)`.
Exported constants: `STAGES`, `TERMINAL_STAGES`, `BENCHMARKS`, `FIX_TARGETING`,
`FIX_SCREEN`, `FIX_CLOSE`, `FIX_TOO_SMALL`, `NOTHING_DUE`.

Commands: `add`, `set`, `today [--json]`, `funnel [--json]`, `digest`, `contacts`,
`contact`. Every subcommand takes `--today YYYY-MM-DD`. Exit 0 always for reads and
for a missing workspace (prints `No workspace found — run: python3 <abs path>/workspace.py init`,
so the inline `!` blocks in the today/review skills never abort); exit 2 for bad
input (unknown stage, bad date, ambiguous/unknown company, nothing to set).

Decisions implemented as specified: add matches (Company, Role) case-insensitively and
prints `updated existing row` instead of duplicating; `set` needs `--role` when the
company matches several rows (candidates printed, exit 2) and resolves company/role
exact-first then by substring; `--note` appends with `; `; `Last touch` = today unless
`--last-touch`; `contact` upserts by (Name, Company) case-insensitively; today sections
in the briefed order, each omitted when empty, `NOTHING_DUE` when all are; auto-cold rows
carry the literal `tracker.py set --company "X" --role "Y" --stage cold`; funnel prints the
Channel table, the Source table (each with an `**All**` row), the Ashby benchmarks line and
`Leak: <stage> — <fix>`; `digest` writes `reviews/<date>.md` (funnel + today) and rewrites
`_Last weekly review: …_`. Writes use `open(..., newline="\n")`.

Extras beyond the brief, all small: `--applied` and `--last-touch` on `add`; `--source`,
`--channel`, `--url` on `set`; an `**All**` total row in both funnel tables; `Applied` is
auto-filled with the touch date the first time a row leaves `saved`; `--url` is appended to
Notes because the table has no URL column.

## Verification

- `python3 -m pytest -q -m "not network"` → **262 passed** (37 new).
- `python3 build.py --check` → `OK: 12 skills pass checks`.
- Red first: the suite failed to collect (no `tracker` module) before implementing.
- Mutation spot-check (each reverted): `STALE_DAYS 7→30` (2 failures), `AUTO_COLD_DAYS 21→40`
  (2), targeting threshold `10→99` (2), rejected-response `and`→`or` (1) — the date rules,
  the diagnosis branches and the response rule are all actually pinned.
- Manual run on a copy of the fixtures: today/funnel/contacts/digest output eyeballed,
  `add`/`set`/`contact` round-tripped, the `## Offers` table and the prose above the pipeline
  table survived every write, review line moved from `2026-09-07` to `2026-09-16`.

Hand-computed funnel the tests assert (fixture, `--today 2026-09-16`): channels
cold 3/0/0/0, referral 2/2/1/0, recruiter-inbound 2/2/1/1, total 7/4/2/1; sources
JobStreet 2/0/0/0, LinkedIn 2/2/0/0, MCF 2/1/1/1, career page 1/1/1/0. Leak on the
fixture is `too small` (sent 7 < 10, interviews 2 < 3).

## Self-review findings (fixed before committing)

1. **`add` clobbered the stage of an existing row.** `--stage` defaulted to `saved`, so
   re-adding a row that had reached `screen` reset it. Fixed: the default now applies only
   when the row is created; covering test `test_add_on_an_existing_row_keeps_the_stage_it_had`.
2. Naming-hook fixes: `load_contacts` → `get_contacts`, `_no_workspace` → `_has_workspace`,
   `_same` → `_is_same` (the brief's `load`/`save` names were kept as specified).

## Concerns / notes for the next task

- **Response rule is literal.** Per the decision, a `rejected` row counts as a response when
  its Notes contain `reply`, `replied` or `rejected by` (case-insensitive substring), so a note
  reading "no reply" would be counted as a response. Documented in `tracker.py funnel --help`
  and in the counting-rules block; tighten only if the spec changes.
- **`diagnose` "else" branch** returns `too small` (with the n<10 wording) even for a healthy
  funnel with n ≥ 10, exactly as the brief's ladder specifies.
- **Interviews-within-7-days excludes today and overdue rows** (`today < Due <= today+7`) so
  a row never appears in two due-based sections; documented in the section heading semantics.
- `set_review_line` appends the line at the end of the file when `pipeline.md` has none
  (fresh template always has one, so this is a fallback only).
- `references/pipeline.md` does not exist yet (task 10). The four fixed recommendation strings
  live in `tracker.py` as `FIX_*`; keep them identical when that reference is written.

---

# Fix report — round 1

**Status:** all three Important findings and all three minors fixed. Commit `6e1e7e1`
(`tracker: contact matches by name, healthy-funnel diagnosis, negation-aware reply rule`).

1. **`contact --name` without `--company` no longer duplicates.** `cmd_contact` matches by
   Name (case-insensitive) first; `--company` narrows it when given. With `--company` omitted:
   one hit → update it (its Company cell is left alone), several → candidates printed and exit 2
   (same shape as `set`), none → create. Tests:
   `test_contact_updates_by_name_when_company_is_omitted`,
   `test_contact_ambiguous_name_without_company_lists_candidates_and_exits_2` (asserts nothing
   was written). `--company`'s help now reads "required only when one name appears at two companies".
2. **`diagnose` ladder replaced per the controller ruling.** `sent < 10 → ("too small",
   FIX_TOO_SMALL)`; at 10+ the targeting (`response_pct < 10`), screen (`responses >= 3 and
   interviews == 0`) and close (`interviews >= 3 and offers == 0`) branches run unchanged;
   nothing failing → `("healthy", FIX_HEALTHY)` with the exact string given. `FIX_TARGETING`,
   `FIX_SCREEN`, `FIX_CLOSE`, `FIX_TOO_SMALL` are byte-identical (verified with `git diff`).
   Tests: `test_diagnose_healthy_branch` and
   `test_diagnose_too_small_wins_below_ten_sent_however_bad_the_ratios` (9 sent / 5 interviews /
   0 offers used to read as `close`). The `--help` counting block was rewritten to match.
3. **Response rule is negation-aware.**
   `REPLY_NOTE_RE = (?<!no )(?<!never )(?<!without )(reply|replied|response|rejected by)`, case-
   insensitive ("response" added as a matched term per the finding). The old single funnel test is
   now parametrized over eight notes: `rejected by email…`, `replied with a template`,
   `some response from the recruiter` count; `no reply after 3 weeks`, `never replied`,
   `closed it myself without response`, `ghosted`, `no word, closed it myself` do not.

Minors: (a) the Interviews section header now carries
`— due in the next 7 days` (asserted verbatim in the today-view test); (b) the `_has_workspace`
check moved above `_bad_dates`/`_bad_stage` in `main`, so a workspace-less session exits 0 even
with a bad flag — `test_no_workspace_beats_bad_input`; (c) `Applied` is back-filled only for
`SENT_OPEN_STAGES = {applied, screen, interview, final, offer}`, so `saved → cold/withdrawn`
leaves it empty — `test_applied_stays_empty_when_a_saved_row_is_closed`.

**Verification:** `pytest tests/test_tracker.py -q` → 50 passed (was 37);
`pytest -q -m "not network"` → **275 passed**; `python3 build.py --check` → `OK: 12 skills pass checks`.
Mutation spot-check of the new logic (each reverted): `sent < 10` → `sent < 3` broke 4 tests,
dropping the three lookbehinds broke 3, `SENT_OPEN_STAGES` → `!= "saved"` broke 1.

**Remaining note:** the funnel output on `fixtures/pipeline-sample.md` still reads
`Leak: too small` (7 sent), so `test_funnel_report_has_both_tables_benchmarks_and_leak` is
unchanged; the `healthy` string is exercised by the pure-function tests only.
