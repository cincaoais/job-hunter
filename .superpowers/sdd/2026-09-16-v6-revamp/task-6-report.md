# Task 6 report — board sources with recorded fixtures

Branch `v6-revamp`. Commits:

- `b078828` sources: JobStreet MY/SG, MyCareersFuture, LinkedIn guest, Hiredly, optional Indeed — fixture-tested parsers
- `a975e67` linkedin: ignore cents in guest salary labels (self-review follow-up, see below)

## What I implemented

`skills/job-hunting/scripts/sources/` — `__init__.py` (empty) plus five modules, each
exposing exactly `NAME`, `LAST_WARNINGS`, `search()`, `parse_search()`, `detail()`,
`parse_detail()` with the brief's signatures. Parsers are pure (bytes or str in, dicts
out, no network); `search`/`detail` take an injectable
`fetch(url, headers, method, payload) -> (status, bytes)` defaulting to
`_common.default_fetch`, which routes to the rate-limited `http_get`/`http_post_json`.

- **jobstreet.py** — jobsearch v5 GET per country (`siteKey`, `sourcesystem=houston`,
  `locale`, `keywords`, `where`, `page`, `pageSize=100`, `sortmode=ListedDate`, optional
  `daterange`, `salaryrange=<min>-&salarytype=monthly`); detail via the `jobDetails`
  GraphQL POST. `JOB_DETAILS_QUERY` is byte-identical to the brief's query (verified by
  diffing against the brief text). `posted = listingDate[:10]`, url `https://{host}/job/{id}`,
  mode from `workArrangements.displayText` (On-site → "Onsite"), teaser falls back to
  `bulletPoints` joined with "; ", currency always MYR/SGD from country.
- **mcf.py** — POST `/v2/search?limit=20&page=<n>` with `{"search", "sortBy":
  ["new_posting_date"]}` (+ `"salary"`), GET `/v2/jobs/{uuid}` for detail. id is
  `mcf:<uuid>` (the uuid is what `detail()` needs), `posted = metadata.newPostingDate`,
  `applicants = metadata.totalNumberJobApplication`, location `address.districts[0].location`
  with "Singapore" fallback, teaser = position level · employment type, mode from
  `flexibleWorkArrangements` when it names remote/hybrid, salary label built from
  `salary.minimum/maximum`. `screeningQuestions[]` are parsed into
  `screening_questions` (strings or `{question: ...}` dicts both handled; the fixture's
  list is empty). `location`/`days` are not MCF query parameters, so they are ignored
  (documented in the docstring).
- **linkedin.py** — guest `seeMoreJobPostings/search` with browser UA, `start=0/25/50`,
  optional `f_TPR=r{days*86400}`, `MAX_PAGES = 3`, `PAGE_DELAY = 2.5` s slept only on the
  live path (an injected `fetch` never sleeps, so tests are instant). Cards parsed per
  `<li>` with anchored class regexes; job id = trailing digits of the link path; query
  string stripped from the url; `posted` from `<time datetime>`; currency claimed only
  when a salary is present. Detail extracts the `show-more-less-html__markup` div
  depth-aware, plus `top-card-layout__title` / `topcard__org-name-link` / the canonical
  `/jobs/view/` url.
- **hiredly.py** — one SSR page fetch per state, `__NEXT_DATA__` → `props.pageProps.jobs[]`,
  id/url from `slug`, `posted = activeAt[:10]`, teaser = unescaped `gptSummary`
  (falling back to career level + min years), MY only (`country != "MY"` → `[]` plus a
  warning). Keyword filter is a case-insensitive substring on the title, applied in
  `search()`; `pages`/`days` are ignored (no trustworthy pagination), documented.
  `detail()` fetches the job page and reads `pageProps.job` — best effort, no fixture
  exists for it (the brief did not record one).
- **indeed.py** — `optional_import("jobspy")`; when absent `search()` returns `[]`, sets
  `UNAVAILABLE_REASON = "pip install python-jobspy"` and appends a warning. Otherwise it
  calls `scrape_jobs(site_name=["indeed"], search_term, location, results_wanted,
  country_indeed)` and maps rows. `parse_search` accepts a DataFrame (`to_dict("records")`),
  a list of row dicts, or JSON, and guards `nan`/`NaT`/`None`; `posted = str(date_posted)[:10]`,
  teaser = `html_to_text(description)[:300]`, currency only when a salary was parsed.
  `detail()` returns `None` (jobspy has no per-id endpoint; descriptions ride along with
  the search rows, which `parse_detail` can turn into a detail record).

`skills/job-hunting/scripts/_common.py` gained:

- `html_to_text(html)` — drops `<script>`/`<style>`, `<li>` → "- " (swallowing the
  whitespace that follows the tag), `<br>` / block ends / `<p>` / headings → newline,
  all other tags stripped, entities unescaped, NBSP → space, per-line whitespace
  collapsed, 3+ newlines → 2.
- `job_record(source, country, **fields)` and `detail_record(**fields)` — the normalized
  dicts with every key always present ("" / None / []); unknown field names raise
  `KeyError` so a typo cannot silently drop a column. Shared by all five modules rather
  than duplicating a 15-key literal five times. `JOB_KEYS` / `DETAIL_KEYS` published
  alongside.
- `default_fetch(url, headers, method, payload)` — the injectable-fetch default.

## Fixture provenance

Copied verbatim (byte-for-byte `cp`) from `.superpowers/sdd/2026-09-16-v6-revamp/recorded/`
into `tests/fixtures/recorded/`: `jobstreet_my_search.json`, `jobstreet_sg_search.json`,
`mcf_search.json`, `mcf_detail.json`, `linkedin_search.html`, `linkedin_detail.html`,
`hiredly_kl.html`.

`jobstreet_detail.json` — **recorded live and successfully** on 2026-09-22 with a single
POST to `https://my.jobstreet.com/graphql`, using the brief's query verbatim and job id
`94655291` (still live; `isExpired: false`). First attempt through
`_common.http_post_json` failed with `SSL: CERTIFICATE_VERIFY_FAILED` — this Python
install has no CA bundle configured, not a site problem — so the recording was made with
`curl` using the same payload, headers (`Content-Type: application/json`,
`User-Agent: UA`) and raw response bytes (HTTP 200, 6804 bytes). Nothing was trimmed or
re-encoded; `test_fixtures_are_verbatim_recordings` guards against accidental rewrites.

Worth noting for later tasks: the local `python3` cannot make HTTPS calls until a CA
bundle is installed (`pip install certifi` / `Install Certificates.command`). Skill
scripts hitting the network on this machine will fail the same way.

## Tests + TDD evidence

`tests/test_sources.py` (40 tests) and 6 new `_common` tests in `tests/test_common.py`.

1. Tests written first, then run:

```
$ python3 -m pytest -q tests/test_sources.py
ImportError while importing test module '.../tests/test_sources.py'
E   ModuleNotFoundError: No module named 'sources'
1 error in 0.09s
```

2. After implementing the modules, two real failures surfaced and were fixed:

```
FAILED tests/test_sources.py::test_jobstreet_parse_search_fields    # bulletPoints fallback
FAILED tests/test_sources.py::test_jobstreet_parse_detail           # "- \nLocation:" from <li>\n
2 failed, 35 passed in 0.07s
```

   - the `<li>`-to-"- " substitution left the newline that followed the tag, so list items
     rendered as a bare "-" on its own line — fixed in `html_to_text` (`<\s*li[^>]*>\s*`).
   - no fixture row has an empty `teaser` *and* bullet points, so the fallback is covered
     by a small synthetic payload test instead of an index into the recording.

3. Green, whole suite, plus the skill check:

```
$ python3 -m pytest -q -m "not network"
....................................................................... [100%]
71 passed in 0.26s

$ python3 build.py --check
OK: 12 skills pass checks
```

Coverage: a parametrized contract test over all five search fixtures (row counts, exact
normalized key set, `source:` id prefix, `posted` `^\d{4}-\d{2}-\d{2}$` or "", url
`https://`, mode/currency enums, int-or-None numerics, str fields); per-source field
mapping assertions on real recorded values; `parse_detail` on all three detail fixtures
(`len > 200`, no `<`, title/company/url, bullet conversion) and on junk input; salary unit
tests for jobstreet (`RM 15,000 – RM 20,000 per month`, NBSP variant, `$4,000 – $6,500`,
single number, no digits, empty), hiredly (`3500 - 4999`, `500`, `Undisclosed`, empty) and
linkedin (cents); request-shape tests through an injected fetch (JobStreet v5 query
params, the GraphQL payload's operationName/variables/query, MCF's POST body and url,
LinkedIn's `start=`/`f_TPR=` walk); warning behaviour (HTTP 429 → partial rows +
`LAST_WARNINGS`, Hiredly's MY-only skip, Indeed without jobspy); Hiredly's client-side
keyword filter; Indeed's row mapping from an in-test list of dicts. No test touches the
network, so no `network` marker was needed in this file.

## Files changed

- `skills/job-hunting/scripts/_common.py` (+72)
- `skills/job-hunting/scripts/sources/__init__.py` (empty), `jobstreet.py`, `mcf.py`,
  `linkedin.py`, `hiredly.py`, `indeed.py`
- `tests/test_sources.py` (new), `tests/test_common.py` (+48)
- `tests/fixtures/recorded/` — 8 fixtures (7 copied, `jobstreet_detail.json` recorded live)

All files LF-only, pathlib everywhere, no shell-isms; stdlib only (`json`, `re`, `html`,
`sys`, `time`, `pathlib`, `urllib.parse`) with `jobspy` reached only through
`optional_import`.

## Self-review findings

- Found and fixed while reviewing: `linkedin.parse_salary("MYR8,000.00 - MYR12,000.00")`
  returned `(8000, 0)` because `\d[\d,]*` matched the trailing `00` of the cents as the
  second number. LinkedIn now strips `\.\d+` before matching; covered by
  `test_linkedin_parse_salary_ignores_decimals` (commit `a975e67`). JobStreet's regex is
  left exactly as the brief specifies (its labels carry no decimals).
- Each module inserts `scripts/` on `sys.path` only if absent, so importing all five does
  not pollute the path with duplicates.
- `detail()` returns `None` on non-200 *and* when the payload holds no job, so callers
  never see a hollow record.
- Interface completeness checked mechanically by
  `test_every_source_exposes_the_same_interface`.

## Concerns / notes for the next task

- Fixtures are a 2026-09-16 snapshot of live HTML/JSON; LinkedIn and Hiredly markup
  changes will break their parsers silently in production while the tests stay green. A
  `network`-marked smoke test per source (one call each, asserting ≥ 1 parsed row) would
  catch drift — out of scope here, and deliberately not added so the suite stays offline.
- Hiredly `detail()` / `parse_detail()` are unverified against a real job page (no fixture
  was recorded for it); the field names (`pageProps.job.description`) are a guess and may
  need one live call to confirm.
- MCF `search()` ignores `location` and `days`, and Hiredly ignores `pages`/`days`; the
  aggregator in the next task should not assume those filters were applied. `LAST_WARNINGS`
  is module-level state, so an aggregator must read it right after each `search()` call
  (and before calling that module again).
- `html_to_text` leaves a blank line between consecutive list items (the brief's
  "collapse 3+ newlines to 2" rule). That renders as a loose markdown list — correct, just
  airier than a tight one.

---

# Fix report — review round 1

One commit: `77d93a4` sources: never-raise guards, shared salary/json helpers, TLS context, mode tests

## 1. `search()` can still raise — fixed

(a) Payload-shape guards. Added to `_common.py`:

- `loads_or_empty(raw)` — JSON from bytes/str, `{}` for anything unparseable.
- `rows_of(container, key)` — `container[key]` only when the container is a dict *and* the
  value is a list, else `[]`.
- `dict_at(container, *keys)` — walks nested dict keys, returning `{}` the moment anything
  is not a dict.

Every list iteration in jobstreet/mcf/hiredly/indeed now goes through `rows_of` (plus a
`isinstance(row, dict)` skip per row), and every nested dig through `dict_at`, so
`{"data": "oops"}`, a top-level list, `null`, `"just a string"`, `{"results": [None, 7]}`
and `{"jobs": "oops"}` all yield `[]` instead of `AttributeError`. Field reads are
`str(...)`-wrapped so a non-string title or an int `listingDate` cannot raise either.
MCF's `screeningQuestions` and `flexibleWorkArrangements` are list-guarded too.

(b) Transport failures. `http_get`/`http_post_json` now share one `_send(req, timeout)`
whose handler chain is `HTTPError` → `URLError` → `http.client.HTTPException` →
`OSError`, each non-HTTP failure returning `(0, b"ClassName: message")`. That covers a
bare `TimeoutError` (OSError subclass), `RemoteDisconnected`/`IncompleteRead`
(`HTTPException`) and `ConnectionReset` during `getresponse()`/`read()`.

Tests: `test_json_parse_search_survives_malformed_payloads` (parametrized over jobstreet
and mcf, 7 malformed bodies each), `test_hiredly_parse_search_survives_malformed_payloads`,
`test_indeed_parse_search_survives_malformed_payloads`,
`test_search_survives_malformed_bodies_without_raising` (all four network sources, HTTP
200 + garbage body), `test_http_get_turns_a_timeout_into_status_zero`,
`test_http_post_json_turns_a_dropped_connection_into_status_zero`,
`test_loads_or_empty_and_shape_guards`.

## 2. Duplicated logic — extracted

- `_common.first_two_ints(label)` holds the "first two integers, one number means both
  bounds, no digits means (None, None)" rule. `jobstreet.parse_salary` and
  `hiredly.parse_salary` are now one-line wrappers; `linkedin.parse_salary` keeps its
  cents pre-substitution then delegates. Each module keeps its own public `parse_salary`
  so the per-board docstring and the brief's interface stay intact.
- `_common.loads_or_empty` replaced the identical `jobstreet._loads` / `mcf._loads` (and
  indeed's inline try/except, and hiredly's `__NEXT_DATA__` parse).
- `_common.finish_detail(got)` holds the repeated epilogue (`got` if it has a description
  or title, else `None`) — used by all four network `detail()`s.
- `_common.dict_at` replaced the repeated `(x.get("a") or {}).get("b")` chains.

`json` is no longer imported by jobstreet/mcf/hiredly/indeed. Tests:
`test_first_two_ints`, `test_finish_detail_drops_empty_records`,
`test_loads_or_empty_and_shape_guards`.

## 3. LinkedIn delay no longer tied to `fetch is None`

`linkedin.search(..., fetch=None, sleep=time.sleep)` and the pause is now unconditional
between pages. `test_linkedin_search_pages_and_stops_on_429` passes `sleep=naps.append`
and asserts `naps == [linkedin.PAGE_DELAY]` — one pause, before page 2 and not before
page 1. The suite is back to sub-second (it had crept to 2.56 s once the sleep became
unconditional, which is exactly the coupling the finding was about).

## 4. `mode` mappings tested

`test_jobstreet_mode_mapping` — synthetic `workArrangements.displayText` of "On-site" →
"Onsite", "Hybrid", "Remote", an unknown string → "" and `None` → "".
`test_mcf_mode_mapping` — `flexibleWorkArrangements` of `["Telecommuting"]` and
`["Work from home"]` → "Remote", `["Hybrid working"]` → "Hybrid", `["Flexi-time"]` and
`[]` → "".

## 5. `detail()` now clears `LAST_WARNINGS`

All five modules reset it on entry (Indeed clears then records its no-detail-endpoint
note). `test_detail_clears_stale_warnings` seeds a "stale" warning in each module and
asserts it is gone after a failing `detail()`.

## 6. TLS

`_common._ssl_context()` returns `ssl.create_default_context(cafile=certifi.where())`
when `optional_import("certifi")` succeeds, else `ssl.create_default_context()` — never
an unverified context — and `_send` passes it to `urlopen`. certifi is reached only
through `optional_import`, so the stdlib-only rule still holds.

Live verification (one call):

```
$ python3 -c "import sys; sys.path.insert(0,'skills/job-hunting/scripts'); import _common; print(_common.http_get('https://api.mycareersfuture.gov.sg/v2/jobs/x')[0])"
404
```

404, not 0 — TLS verification now succeeds on this machine (it was
`CERTIFICATE_VERIFY_FAILED` before, which is why `jobstreet_detail.json` had to be
recorded with curl). Tests: `test_ssl_context_verifies` (is an `ssl.SSLContext`,
`CERT_REQUIRED`, `check_hostname`) and `test_ssl_context_without_certifi_still_verifies`.
The existing fake `urlopen`s in `tests/test_common.py` gained a `context=None` parameter.

## Commands and output

```
$ python3 -m pytest -q tests/test_sources.py tests/test_common.py
........................................................................ [ 85%]
............                                                             [100%]
84 passed in 0.12s

$ python3 -m pytest -q -m "not network"
........................................................................ [ 76%]
......................                                                   [100%]
94 passed in 0.32s

$ python3 build.py --check
OK: 12 skills pass checks
```

(57 tests in test_sources.py, 27 in test_common.py, 94 in the whole offline suite.)

## Files changed in this round

`skills/job-hunting/scripts/_common.py`, `sources/jobstreet.py`, `sources/mcf.py`,
`sources/linkedin.py`, `sources/hiredly.py`, `sources/indeed.py`, `tests/test_sources.py`,
`tests/test_common.py`.

## Notes

- `search()`/`parse_search()` still raise `ValueError` for an unsupported `country`
  (jobstreet outside MY/SG, mcf outside SG). That is a caller programming error, not a
  network or payload condition, and is deliberately left loud; Hiredly's MY-only case is
  a `LAST_WARNINGS` skip because MY/SG both reach it in normal multi-country use.
- The earlier concern stands: Hiredly `detail()`/`parse_detail()` remain unverified
  against a real job page.

---

# Fix report — review round 2

One commit: `c8eb35d` mcf: guard nested list fields in _teaser

## The residual hole and why round 1 missed it

Confirmed the reproduction first:

```
$ python3 -c "... mcf.parse_search('{\"results\":[{\"uuid\":\"u1\",\"title\":\"Dev\",\"positionLevels\":\"oops\"}]}', country='SG')"
REPRO: AttributeError 'str' object has no attribute 'get'
```

Root cause of the miss: round 1's `_teaser` rewrite was applied with a scripted
string replacement whose search text used the escape `·` while the file holds the
literal `·` character. The replacement silently matched nothing and I did not assert
that it had applied — the other `mcf.py` edits in the same script did apply, so the
tests stayed green and the hole survived. Lesson applied below.

## Fix

`mcf._teaser` now reads both nested lists through the shared guards:

```python
bits = [dict_at(p).get("position", "") for p in rows_of(row, "positionLevels")]
bits += [dict_at(e).get("employmentType", "") for e in rows_of(row, "employmentTypes")]
return " · ".join(str(b).strip() for b in bits if b and str(b).strip())
```

Also tightened `mcf._screening_questions`: a non-str, non-dict entry (`null`, a number)
is now skipped rather than stringified into `"None"` / `"3"` — it never raised, but it
was manufacturing junk questions. Strings and `{"question": ...}` dicts still parse:
`['Why us?', {'question': 'Notice period?'}, None, 7]` → `['Why us?', 'Notice period?']`.

## Sweep for the same pattern

`grep -n "for .* in (.*get(" skills/job-hunting/scripts/sources/*.py` and
`grep -n "or \[\])"` now return only `indeed.py:69`, which iterates a literal tuple of
two already-`_str()`-ed values — not a payload-derived list. No other module iterates a
nested list without `rows_of`.

Because a grep is only as good as the pattern, I also fuzzed every parser instead of
trusting it: for each source, every key of the real recorded row (plus an unexpected key)
was replaced in turn by each of `"oops"`, `[None]`, `[7]`, `[{"x": 1}]`, `{"x": 1}`, `7`,
`None`, `[]`, `{}`, `True`, and `parse_search`/`parse_detail` were called on the result —
roughly 1,500 permutations across jobstreet, mcf, hiredly, indeed, plus degenerate HTML
for linkedin. Result: **0 failures**. (Throwaway script, not committed.)

## Tests added

- `test_mcf_parse_search_guards_nested_list_and_dict_fields` — parametrized over the
  coordinator's exact reproduction (`positionLevels: "oops"`) plus `employmentTypes:
  "oops"`, `positionLevels: [None, 7, "x"]`, `employmentTypes: [{"nope": 1}]`, and
  string-instead-of-list/dict for `flexibleWorkArrangements`, `screeningQuestions`,
  `address`, `salary`, `postedCompany`, `metadata`. Each must yield one row with the full
  normalized key set rather than raising.
- `test_mcf_parse_detail_guards_nested_fields` — same idea on the detail parser,
  asserting `screening_questions == []` for junk inputs.

## Commands and output

```
$ python3 -m pytest -q tests/test_sources.py
.................................................................... [100%]
68 passed in 0.06s

$ python3 -m pytest -q -m "not network"
........................................................................ [ 68%]
.................................                                        [100%]
105 passed in 0.33s

$ python3 build.py --check
OK: 12 skills pass checks
```

## Files changed in this round

`skills/job-hunting/scripts/sources/mcf.py`, `tests/test_sources.py`.
