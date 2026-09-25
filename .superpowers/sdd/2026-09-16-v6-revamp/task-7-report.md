# Task 7 report — `search_jobs.py`, criteria-driven multi-board search

Branch `v6-revamp`. Commit:

- `0379416` search_jobs.py: criteria-driven multi-board search with dedupe, knockouts, freshness ranking

## What I implemented

`skills/job-hunting/scripts/search_jobs.py` (stdlib only, LF, Windows-safe), the brief's
public surface plus the aggregator core:

- **`read_criteria(profile_md) -> dict`** — `{keywords, location, country, salary_min,
  must_have, dealbreakers, boards}`. Reads every `- **Label:** value` line into a
  label→value map (first occurrence wins); a value that is only a template hint
  (`(e.g. …)`) or `TBD`/`N/A`/`—` counts as unset, so an unfilled template yields
  defaults rather than garbage. Lists split on `,`/`;` with quotes stripped. Salary floor
  = first number ≥ 1000 (`RM 9,000–12,000` → 9000). Boards map by substring
  (jobstreet/linkedin/mycareersfuture|mcf/hiredly/indeed), unknown names ignored, empty →
  `jobstreet,mcf,linkedin,hiredly`. `location` drops a trailing country
  ("Kuala Lumpur, Malaysia" → "Kuala Lumpur") because the boards want a city/state.
- **Country**: `"singapore"`/`"malaysia"` by **earliest mention**, else the first two
  letters upper. The brief's literal rule ("SG if it contains singapore, else MY") would
  make the sample profile SG — its market line is
  "Malaysia (KL/Selangor); open to remote roles for Singapore companies" — which
  contradicts the brief's own step-1 assertion of `"MY"`. Earliest-mention satisfies both
  and degrades to the brief's rule when only one country is named.
- **`knockout(job, criteria) -> str | None`** — dealbreakers matched word-boundary
  against title + company + teaser (whitespace/hyphen interchangeable, so "6-day work
  week" also catches "6 day work week"); a trailing category noun is optional, so
  "gambling industry" catches "online gambling platform" but "hybrid" still does not
  match "fully onsite". Then `salary_max < salary_min` → `"salary below floor"`. Then
  must-haves: significant words of the entries (stopwords dropped) matched against
  title + teaser; none present → `"missing must-have"` (soft).
- **`rank(jobs)`** — three stable passes: board priority, then salary_max desc (unknown
  last), then freshness desc (undated last).
- **`dedupe(jobs, seen, *, today=None, keep_seen=False)`** — primary key `id`, secondary
  `slugify(company + " " + title)`; the highest-priority board wins a cross-board
  duplicate; returns a **copy** of `seen` with `seen[id] = first_seen` for every new id
  (existing dates are never overwritten). `keep_seen=True` backs `--all`.
- **`run(criteria, *, sources, seen, today=None, all_=False)`** — the pure core. Queries
  every source for every keyword, applies the `--days` filter itself on `posted`
  (undated = fresh, per the decision), knocks out, dedupes, ranks, and returns
  `{new, needs_look, knocked_out, sources, seen, seen_before}`. A source that warns is
  not re-queried for the remaining keywords (no hammering a 429'd LinkedIn three times);
  a source that raises is reported as a warning, never a traceback; `mcf` is skipped
  unless country SG and `hiredly` unless MY (`SOURCE_COUNTRIES`), and a module that sets
  `UNAVAILABLE_REASON` (indeed without jobspy) is reported as skipped.
- **`render_markdown(jobs, knocked, *, needs_look, sources, seen_before)`** — headline
  `## N new postings (M knocked out, K needs a look, S seen before)` (or
  `## 0 new since last run (…)`), the brief's 8-column table (rendered through
  `_common.write_table`, so pipes and newlines are escaped by the shared code),
  `### Needs a look`, `### Knocked out` bullets `- Company — Role: reason`, and a
  `Sources: jobstreet 42 · mcf skipped: SG only · linkedin 7 (HTTP 429 at page 2,
  stopped) · indeed skipped: pip install python-jobspy` line built from the counts and
  each module's `LAST_WARNINGS`.
- **`main()`** — argparse per the brief (`--keywords --location --country --days
  --salary-min --sources --pages --markdown|--json --all --no-seen`), flags overriding
  the profile; reads `profile.md`/`seen-jobs.json` from `workspace_dir()`, writes
  `seen-jobs.json` unless `--no-seen`. Exit 0 including on zero results, 2 for an unknown
  `--sources` name (argparse) and 2 with a message naming the profile field when there
  are no keywords at all. `--json` prints exactly `{new, needs_look, knocked_out,
  sources}`. `get_sources()` imports the real modules by name (renamed from
  `load_sources` for the repo's naming rule: `load_` is retired in favour of `get_`).

## Tests + TDD evidence

`tests/test_search_jobs.py` — 45 tests, network-free (stub modules with the real
`search()` signature; jobs built with `_common.job_record`).

- Red first: tests written before the module, run →
  `ModuleNotFoundError: No module named 'search_jobs'` … `1 error in 0.08s`.
- Green after implementing: `45 passed`.
- Coverage: `read_criteria` on `tests/fixtures/sample-profile.md` (keywords list, country
  MY, salary_min 9000, location, boards, dealbreakers, must-haves), on the unfilled
  template (defaults), an SG/board-alias/unknown-board case and the two-letter fallback;
  `knockout` parametrized over 8 cases (gambling company, gambling teaser, multiword
  phrase, absent dealbreaker, salary floor, no salary, missing must-have, clean) plus
  empty criteria; `dedupe` first run / second run keeps the original date / no caller
  mutation / `keep_seen` / cross-board collapse by priority / same company different
  role; `rank` full order and the unknown-salary tie-break; `run` splitting
  new/needs-look/knocked, per-keyword queries, seen-before exclusion, `--all`, freshness
  drop with undated kept, warning capture, stop-after-warning, a raising source, a
  country-skipped source, an unavailable optional source, ranked output;
  `render_markdown` sections/sources line/needs-look cap/zero-results/pipe escaping;
  `main` markdown+seen write, `--json` shape, `--no-seen`, flag overrides, zero results
  exit 0, unknown source exit 2, no-keywords exit 2; `default_sources` per country and
  `get_sources` importing the real modules.
- Full suite: **150 passed** (`python3 -m pytest -q`). `python3 build.py --check` →
  `OK: 12 skills pass checks`. Both files LF, stdlib only.
- The post-edit test hook flagged "45 tests against 0 production lines" while the red
  phase had no implementation yet, and one duplicated-literal pair which I folded into
  the parametrized `test_knockout`.

## Live smoke (step 3)

`JOB_HUNT_DIR=<scratch>/jh3 workspace.py init && search_jobs.py --keywords "software
engineer" --location "Kuala Lumpur" --country MY --days 3 --markdown` (scratchpad instead
of `/tmp`; same effect), exit 0, ~3 s:

```
## 93 new postings (0 knocked out, 0 needs a look, 0 seen before)

| # | Posted | Source | Company | Role | Location / mode | Salary | Link |
|---|---|---|---|---|---|---|---|
| 1 | 2026-09-22 | jobstreet | Reliable Business Technologies | Microsoft Dynamics 365 CRM Developer | Kuala Lumpur | RM 7,000 – RM 10,000 per month | [open](https://my.jobstreet.com/job/94790238) |
| 2 | 2026-09-22 | jobstreet | HTC Global Services | Senior IAM Engineer | Kuala Lumpur | RM 7,000 – RM 10,000 per month | [open](https://my.jobstreet.com/job/94788201) |
| 3 | 2026-09-22 | hiredly | Snappymob Sdn. Bhd. (Reg. No. …) | Senior Software Engineer (Node.js) | Kuala Lumpur | 8000 - 10000 | [open](https://my.hiredly.com/jobs/…) |
| 4 | 2026-09-22 | jobstreet | HashWhale Pte.Ltd | AI-Native Full Stack Engineer (Java) – Remote | Bandar Malaysia, Kuala Lumpur · Remote | RM 6,000 – RM 9,000 per month | [open](https://my.jobstreet.com/job/94790829) |
…
Sources: jobstreet 85 · linkedin 10 · hiredly 1
```

Three more live checks on the same code:

- Second identical run → `## 0 new since last run (0 knocked out, 0 needs a look, 90 seen
  before)` — dedupe against `seen-jobs.json` works across runs.
- `--country SG --sources jobstreet,mcf,indeed,hiredly` →
  `Sources: jobstreet 100 · mcf 20 · hiredly skipped: MY only · indeed skipped: pip
  install python-jobspy`.
- The sample profile as the workspace profile, `--days 7` (no flags) →
  `## 21 new postings (32 knocked out, 80 needs a look, 0 seen before)`, knockouts like
  `- Ambition Recruitment — Data Engineer: salary below floor`. That 80-row soft bucket is
  what made me cap the rendered "Needs a look" table at 10 rows with
  `… and N more (--json for the rest).`.

## Files changed

- `skills/job-hunting/scripts/search_jobs.py` (new, 598 lines)
- `tests/test_search_jobs.py` (new, 45 tests)

Nothing else touched: no `_common.py` change was needed (`write_table` renders the table,
`loads_or_empty` reads the seen file, `slugify`/`today`/`workspace_dir` as-is).

## Self-review (fixed before committing)

1. **`dedupe` collapsed every id-less row into one** and would have written an empty `""`
   key into `seen-jobs.json` — both keys are now guarded on a non-empty id.
2. **`rank()` was called twice** to split new from needs-look; now ranked once and
   partitioned. The soft rows are tracked by object identity (`id(job)`) rather than by
   `job["id"]`, so rows with a duplicate or missing id cannot cross buckets, and nothing
   is written into the records themselves (kept out of the `--json` payload).
3. **A source module that fails to import was silently dropped** from the run; it now
   prints a `warning: source X failed to import (…)` line on stderr.
4. **Windows**: the table uses `·` and `—`, and a redirected Windows console is cp1252, so
   `main()` reconfigures stdout to UTF-8 with `errors="replace"` when the stream supports
   it.
5. The 80-row soft bucket from the live run → the `NEEDS_LOOK_ROWS = 10` cap plus test.

## Concerns / deferred

- **Must-have matching is word-level and therefore noisy.** "backend role primarily in Go
  or Python; hybrid or remote" reduces to {backend, go, python, hybrid, remote}, and
  board teasers are short, so ~60% of a broad live query landed in "Needs a look". It is
  soft by design (nothing is dropped) and the table is capped, but if the bucket should be
  the exception rather than the rule, the check needs the full posting text
  (`fetch_posting.py`, Task 8) rather than the teaser.
- **`seen-jobs.json` grows without bound** (90 ids after one query). Nothing prunes it;
  if that matters, a later task should drop entries older than N days.
- **Keywords multiply requests**: 3 keywords × 3 boards = 9 requests, and Hiredly re-fetches
  the same state page per keyword (it has no keyword API — the filter is local). It is
  rate-limited to 1 req/s per host and stops a board after its first warning, but a
  per-source result cache would be the obvious optimisation.
- **Cross-board dedupe is title+company exact after slugify** — "Sr. Backend Engineer" at
  the same company on two boards still shows twice.
- **Dealbreaker category-tail stripping is a heuristic.** `_CATEGORY_TAILS` turns
  "gambling industry" into a match on bare "gambling"; a dealbreaker like "night work"
  would strip to "night". Tails were chosen to be nouns that cannot stand as the
  dealbreaker's whole meaning, but the list is a judgement call.
- `--markdown` is accepted and is the default; it exists only so the brief's command line
  works.

---

# Fix round 1 — review findings addressed

Commit `69d6f10` search_jobs: safer dealbreaker variants, salary floor k/annual, template
wording. Task tests `56 passed`, full suite `161 passed`, `build.py --check` →
`OK: 12 skills pass checks`. Tests written first: the 5 new expectations failed
(`5 failed, 51 passed`) before the implementation changed.

1. **Important — dealbreaker variants no longer decay into a bare word.**
   `_CATEGORY_TAILS` lost `only`, `work`, `role`, `roles`, `job`, `jobs` (they carry
   meaning) and now holds only pure category nouns
   (`industry/industries/sector/sectors/company/companies/firm/firms/business/businesses/space/field`).
   `_dealbreaker_res` strips **at most one** tail instead of looping, so a phrase can
   lose a category noun but never unravel. Verified live and by test:
   "commission-only roles" no longer knocks out "Base salary plus commission on closed
   deals", "contract work" leaves "Contract negotiation with vendors" alone, and
   "gambling industry" still catches "online gambling platform". New parametrized
   `test_knockout_dealbreaker_variants` covers those three plus the full-phrase hit.
   - Writing the full-phrase case surfaced a second real gap: the dealbreaker is written
     plural ("commission-only roles") while the posting says "role", so the literal
     phrase never matched. `_phrase_re` now makes the **final word plural-tolerant**
     (`roles` ↔ `role`; words ending in "ss" such as "business" are left alone), which is
     what keeps the whole-phrase path useful for entries written either way.
   - Sanity sweep (9 hand cases) all correct, and the live profile-driven run over ~230
     postings produced the same 32 knockouts as before, every one
     `salary below floor` — no dealbreaker false positives.
2. **Minor — salary floor.** `_salary_floor` now multiplies a `k`/`K` suffix by 1000 and
   divides by 12 when the line says per year / annum / annual(ly) / yearly / `/yr` /
   `p.a.` **and** does not also say per month. `RM9k/month` → 9000,
   `RM 120,000 per year` → 10000, `SGD 96k p.a.` → 8000; the previously covered
   `RM 9,000–12,000 / month` → 9000 and the noise case
   `up to 8 months bonus, SGD 7,500 / month` → 7500 still hold. Six cases in the new
   parametrized `test_read_criteria_salary_floor`.
3. **Minor — template wording.** `assets/profile-template.md:34` now reads
   "(postings matching none of these go to a 'needs a look' list instead of the main
   shortlist)", matching the soft implementation.
4. **Minor — knocked-out rows are deliberately not marked seen.** Comment added at the
   `dedupe(kept, …)` call in `run()` saying why (so a posting is re-evaluated when the
   profile's dealbreakers or salary floor change), pinned by
   `test_run_does_not_mark_knocked_out_postings_as_seen`.

Also removed a stray double blank line before `if __name__` left by an earlier edit.

Concerns from the first report stand, minus the dealbreaker-heuristic one, which this
round narrows: the tail list is now only nouns that cannot be the dealbreaker's whole
meaning, and a single strip means the worst case is one category noun ignored rather than
a phrase collapsing to its first word.
