# Task 8 report — `fetch_posting.py`, URL/id → `postings/<slug>.md`

Branch `v6-revamp`. Commit:

- `6f2b68c` fetch_posting.py: URL → postings/<slug>.md with board-specific detail APIs and
  stealth-browser fallback

Files: `skills/job-hunting/scripts/fetch_posting.py` (478 lines), `tests/test_fetch_posting.py`
(51 tests). Stdlib only, LF, Windows-safe. Nothing else in the repo was touched.

## Public surface

- **`classify(target) -> (source, id, country)`** — `jobstreet|linkedin|mcf|hiredly|generic`.
  A bare number is a JobStreet **MY** id, a bare 32-hex string an MCF **SG** uuid; anything
  unmatched is `("generic", target, "")`. Country comes from the host (`my.`/`sg.` prefix or
  `.my.`/`.sg.` label, mycareersfuture→SG, hiredly→MY), `""` when the host does not say, and
  `BOARD_DEFAULT_COUNTRY` (jobstreet/linkedin MY, mcf SG, hiredly MY) fills that in at call
  time so `www.linkedin.com/jobs/view/<id>` still works.
- **`generic_extract(html) -> {"title", "text"}`** — `<title>` for the title; head, script,
  style, noscript, template, svg, iframe, nav, header, footer, aside, form, button and select
  blocks dropped; then the **largest** `<main>`/`<article>` block (nesting-aware scanner, not
  a non-greedy regex), falling back to `<body>`, then to whatever is left; `html_to_text` for
  the flattening.
- **`fetch_html(url, *, get=None) -> (status, text)`** — identified UA first, then exactly one
  Chrome-UA retry (with Accept/Accept-Language), keeping whichever answer is more diagnostic.
- **`looks_blocked(status, body)`** — 403/429/503, or a body containing `cf-chl`,
  `cf-challenge`, `just a moment`, `prove your humanity`, `challenge-platform`,
  `access denied` (first 200 KB, case-insensitive).
- **`browse(url, *, cloak=None)`** — `optional_import("cloakbrowser")` → `launch(headless=True)`,
  `new_page()` if present (CloakBrowser hands back a Playwright Browser), `goto(url,
  wait_until="domcontentloaded", timeout=45000)`, `document.body.innerText` +
  `document.title`, close. Everything is wrapped: a missing binary, a timeout or an API change
  all return `None`, which the caller reads as blocked.
- **`fetch_board(source, id, country, *, detail_fetch=None)`** — the existing
  `sources/<board>.detail(...)` with its injectable `fetch`; exceptions and a `None` detail
  become `None`.
- **`fetch(target, *, get=None, detail_fetch=None) -> (job|None, reason)`** — `reason` is
  `""`, `"blocked"`, or `"not found: …"`. The only impure parts are the two injected callables.
- **`render_posting(job)`** — frontmatter in the brief's order (`source, url, company, title,
  location, salary, posted, fetched, screening_questions`), `screening_questions: []` or a
  two-space YAML list, `fetched` defaulting to `today()`, then `## Description` and the text.
  Accepts `salary_label` and `text` as aliases for `salary`/`description_md`.
- **`save(job, *, ws=None)`** → `<workspace>/postings/<slugify(company + " " + title)>.md`,
  written with `newline="\n"`. Same `url:` → overwrite; different `url:` → `-2`, `-3`, …
  Blank company and title fall back to `<source>-posting`.
- **CLI** `fetch_posting.py <url-or-id> [--save] [--print] [--stdin] [--company X] [--title X]
  [--url X]`. Prints the markdown when `--save` is absent; `--save` also prints the path.
  Exit codes 0 / 2 (bad args, empty stdin) / 3 (blocked) / 4 (no such job, HTTP failure, or a
  page with no text). No traceback on any network path.

## Decisions and deviations

- **`--stdin`** (source `pasted`) is implemented as the brief's decision asked, plus
  `--company/--title/--url` overrides — they name the saved file and let a user correct a bad
  generic extraction (`--title "AI Engineer"` instead of Greenhouse's
  "Job Application for AI Engineer at GitLab").
- **Two deliberate additions beyond the brief**, both found by live smoke, both tested:
  1. **Thin-page fallback.** A JS-rendered career page answers **200 with an empty shell**, so
     `looks_blocked` is false and the brief's flow would have saved an empty posting. When the
     extracted text is under `MIN_GENERIC_TEXT` (200 chars) the stealth browser is tried; if it
     is unavailable and there is no text at all, the run exits 4 with
     "no posting text … the page may need JavaScript; paste the text instead".
  2. **Settle step in `browse`.** `domcontentloaded` fires *before* an SPA hydrates —
     `jobs.ashbyhq.com/ramp` gave `innerText` of length **0** at that moment and **22915** three
     seconds later. `browse` keeps the brief's `wait_until="domcontentloaded"` but, on a thin
     first read, calls `wait_for_load_state("networkidle", timeout=15000)`, else
     `wait_for_timeout(3000)`, else `time.sleep(3)`, and re-reads. Without this the
     CloakBrowser fallback is dead on exactly the pages it exists for.
- **Library chatter off stdout.** CloakBrowser prints a banner on launch; `browse` runs under
  `contextlib.redirect_stdout(sys.stderr)` so `--print` output stays parseable markdown.
- **LinkedIn id regex requires ≥ 6 digits** (`view/[^/?#]*?(\d{6,})(?:[/?#]|$)`). A shorter
  minimum makes the slug form ambiguous — `senior-engineer-2-at-grab-4455634411` would match
  the "2". LinkedIn job ids have been 9–10 digits for years.
- **Frontmatter quoting** is slightly broader than "contains `:`": a value is quoted when it
  contains any of `:#&*!|>%@`"'{}[],` or starts with `-`. Every such value is still valid YAML
  and the brief's rule is satisfied; `source: jobstreet` and `title: Lead Product Designer`
  stay bare.
- **Attribution trailer.** This session's harness attribution reminder names
  `Co-Authored-By: Claude Opus 5 (1M context)`, which is the model that wrote this task, so the
  commit carries that instead of the brief's `Claude Fable 5.1` line. Say the word and I will
  amend it (the commit is unpushed).
- `location`, `salary` and `posted` come out **empty for board postings**: the sources'
  `parse_detail` only returns the five `DETAIL_KEYS`, and Task 8 does not change `sources/`.
  The data exists in the JobStreet GraphQL payload (`location`, `salary`, `listedAt`) and in
  MCF's; wiring it through is a `sources/` change for a later task.

## Tests — `tests/test_fetch_posting.py`, 51 tests, no network

`classify` on the six URL shapes plus the three bare-input cases; `generic_extract` on inline
HTML (title/entities, main preferred, largest-of-two-articles, body fallback, junk);
`render_posting` (key order parsed back out of the frontmatter, quoting, defaults, aliases,
body); `save` (slug, same-url overwrite, `-2`/`-3` suffixes, empty-company fallback, no CR in
the bytes) in a `JOB_HUNT_DIR` tmp workspace; **a JobStreet URL routing to
`sources.jobstreet.detail`** with an injected fake `fetch` serving
`tests/fixtures/recorded/jobstreet_detail.json` (asserting the GraphQL url, `jobId` and zone
`asia-4`); the same for an MCF uuid with `mcf_detail.json`; **a 403 with `optional_import`
monkeypatched to `None` exiting 3** with the exact message; `looks_blocked` over seven
challenge shapes plus a clean page; the browser fallback (launch kwargs, goto args, close, the
banner staying off stdout, a launch failure counting as blocked, the SPA settle path through
both wait APIs and the sleep fallback); and the CLI (default print, `--save`, `--stdin`,
usage error, empty stdin, network failure reported not raised).

Full suite: **212 passed** (`python3 -m pytest -q`). `python3 build.py --check` → OK, 12 skills.

## Live smoke (`JOB_HUNT_DIR=/tmp/jh-smoke`)

`python3 skills/job-hunting/scripts/fetch_posting.py https://my.jobstreet.com/job/94655291 --save`
→ `Saved /tmp/jh-smoke/postings/electronic-arts-lead-product-designer.md`, 85 lines:

```
---
source: jobstreet
url: "https://my.jobstreet.com/job/94655291"
company: Electronic Arts
title: Lead Product Designer
location:
salary:
posted:
fetched: 2026-09-22
screening_questions: []
---

## Description

Locations: Kuala Lumpur, Wilayah Persekutuan Kuala Lumpur, Malaysia
```

Also live, all exit 0 unless noted:

- **Generic / Greenhouse** — `https://job-boards.greenhouse.io/gitlab/jobs/8556658002`
  (`--company GitLab --title "AI Engineer"`) → `gitlab-ai-engineer.md`, 123 lines of real JD
  text; the only noise is Greenhouse's trailing "Apply for this job / * indicates a required
  field".
- **MCF** — a live uuid URL from `mcf.search` →
  `eos-innovation-singapore-pte-ltd-software-engineer-and-senior-software-engineer.md`.
- **Bare id** — `fetch_posting.py 94655291 --save` overwrote the same file (still 3 files in
  `postings/`), proving the same-url rule.
- **Blocked → stealth browser** — `https://www.glassdoor.com/Job/index.htm` is a hard 403 for
  both UAs; CloakBrowser (installed here, free v146 binary) returned the page, 742 chars.
- **JS-only page** — `https://jobs.ashbyhq.com/ramp` is 200 with 0 extractable chars; the
  thin-page + settle path returned 22915 chars.
- **Error paths** — `…/job/11111111` → `not found: jobstreet has no job 11111111`, exit 4; no
  argument → usage, exit 2; `--stdin` with blank input → exit 2.

## Concerns for review

1. `location`/`salary`/`posted` are always empty for board postings (see above) — the
   frontmatter keys exist but `jd-match.md` cannot rely on them yet.
2. A page `<title>` is a poor job title on some ATSes ("Job Application for … at GitLab"); the
   generic path has no company at all. `--company/--title` are the escape hatch, and the slug
   is only as good as what the user passes.
3. Greenhouse's apply-form labels leak into the description (their inputs are inside `<main>`
   and not all are wrapped in `<form>`). Cosmetic, a few trailing lines.
4. `MIN_GENERIC_TEXT = 200` and `SETTLE_MS = 3000` are my numbers, not the brief's.
5. `_blocks` treats `<main data-x=/foo/>` (an unquoted attribute ending in `/`) as
   self-closing. Contrived, no real page seen doing it.
6. Board URLs whose host does not name a market silently default to MY (jobstreet/linkedin) —
   a `www.jobstreet.com.my/en/job/<id>` link is right by luck, not by parsing.
7. `browse` can cost ~20 s per call (browser launch + settle). Only reached when a page is
   blocked or thin, never in tests.

---

# Fix report — round 1 of 5

Commit `e418dd5` (amended into the single task commit; the old sha `6f2b68c` is gone). Trailer
is now exactly `Co-Authored-By: Claude Fable 5.1 <noreply@anthropic.com>`, verified with
`git log -1 --format=%B`. Subject line unchanged; the body gained a "Review fix round 1"
paragraph. Files touched this round: `_common.py`, `sources/{jobstreet,mcf,linkedin,hiredly}.py`,
`fetch_posting.py`, `tests/test_fetch_posting.py`, `tests/test_sources.py`.

## 1. `<form>` no longer dropped — ADDRESSED

`_DROP_TAGS` lost `form` and gained `textarea`, `label`, `option`, `fieldset` (alongside the
existing `button`, `select`), with a comment naming Workday/Lever/SmartRecruiters so nobody
re-adds it. `input` was not added: it has no end tag, so the `<tag>…</tag>` drop regex can
never match it, and `html_to_text` strips it anyway — listing it would have been dead code.

New test `test_generic_extract_keeps_a_form_wrapped_description` builds
`<body><form><main><p>…×15</p><label>…<button>…<select>…</main></form></body>`, asserts the
description survives, is over `MIN_GENERIC_TEXT`, and that `Resume/CV` / `Apply` / `Yes` do
**not** appear — and then runs it through `fetch()` with `optional_import` monkeypatched to
raise, so a regression that empties the page (and thus reaches for the browser) fails loudly
instead of silently passing.

**Cost, measured:** the live GitLab/Greenhouse posting went from 123 to **178 lines** — the
extra 55 are Greenhouse's EEO self-identification prose and a stray "Select…", which live in
plain `<p>`s inside the same `<main>` as the JD. No cheap rule separates them (both the JD and
the form are inside one `<main>`, so block selection cannot help). Keeping the JD on
form-wrapped ATSes is clearly the better trade; flagging it in case you want a
Greenhouse-specific trim later.

## 2. `location` / `salary` / `posted` now live — ADDRESSED

- `_common.DETAIL_KEYS` += `location`, `salary_label`, `posted` (default `""` via
  `detail_record`).
- **jobstreet** — `location.label`, `salary.label`, `listedAt.dateTimeUtc[:10]`.
- **mcf** — factored `_location(row)` out of `parse_search` (it had this logic inline) and
  reused it in `parse_detail`; `_salary_label(_int(min), _int(max))` (the existing helper) and
  `metadata.newPostingDate`. `_location` falls back to `"Singapore"` only for a **non-empty**
  payload, so the junk-payload contract ("every field empty") still holds — otherwise
  `parse_detail(b"{}")` would have claimed a location.
- **linkedin** — new `_detail_location(html)` walks every `topcard__flavor--bullet` span and
  takes the first that is not `--metadata` (that one is "47 applicants"); `posted` reuses
  `_DATE_RE` (`<time datetime=…>`) and `salary_label` reuses `_SALARY_RE`. The recorded guest
  detail page has neither, so both come back `""` — best effort, as ruled.
- **hiredly** — `stateRegion`/`location`, `salary`, `activeAt[:10]` (same field names its
  `parse_search` uses); also picked up `aggregatedCompanyName` as a company fallback, matching
  `parse_search`.
- `fetch_posting` needed no change for the mapping: `_value_of` already reads `salary` then
  falls back to `salary_label`.

Tests: `test_sources.py` DETAIL_KEYS set updated; `test_jobstreet_parse_detail` now asserts
`location == "Kuala Lumpur City Centre, Kuala Lumpur"`, `posted == "2026-09-15"`,
`salary_label == ""` (that advertiser published none); `test_mcf_parse_detail` asserts the
district, `2026-09-16` and `"SGD 4,000 - 6,500 per month"`; `test_linkedin_parse_detail`
asserts the top-card location and empty date/salary; the junk test asserts all three are `""`
for every source. In `test_fetch_posting.py`, two new tests drive the fixtures through
`fetch()` → `render_posting()` and assert the frontmatter lines.

Live proof:

```
source: jobstreet                       source: mcf
location: "Kuala Lumpur City Centre, Kuala Lumpur"   location: "D22 Jurong, Jurong Island, Tuas"
salary:                                 salary: "SGD 7,000 - 12,000 per month"
posted: 2026-09-15                      posted: 2026-09-22
```

## 3. Trailer — ADDRESSED

Amended as instructed (see the header of this fix report). For the record: I had used the
harness's own attribution line and flagged the conflict in the first report; your ruling
settles it and the branch is now internally consistent.

## Minors folded in

- **(a)** A 200 body is now always parsed before the browser is considered; the browser only
  starts when the extracted text is under `MIN_GENERIC_TEXT` (and only for a 200 or a blocked
  status, so a 0/404/500 still fails fast without a 20 s browser launch).
  `test_a_200_page_that_says_access_denied_is_still_parsed` uses a real-ish security JD
  containing both "Access Denied" and "challenge-platform", asserts `looks_blocked` is `True`
  for it, and that `fetch` returns it without touching the browser. A genuine Cloudflare
  interstitial is short, so it still routes to the browser — that is what separates the two.
- **(b)** `looks_blocked` is evaluated once into `blocked`.
- **(c)** MCF uuids are lowercased in both `classify` branches (bare id and URL);
  `test_classify_lowercases_an_uppercase_mcf_uuid` covers both, and a live uppercase-uuid URL
  fetched fine.
- **(d)** `_scalar` quotes YAML 1.1 reserved words (`yes/no/true/false/null/on/off/y/n/~`,
  case-insensitive) and values starting with `?` as well as `-`. Parametrized test included.

## Verification

- `python3 -m pytest tests/test_fetch_posting.py tests/test_sources.py -q` → **132 passed**
  (64 + 68).
- `python3 -m pytest -q` → **225 passed**.
- `python3 build.py --check` → OK, 12 skills (run before amending).
- Live re-smoke after the source changes: JobStreet 94655291, MCF (uppercase uuid URL),
  Greenhouse GitLab — all exit 0, frontmatter as shown above.
- The only >99-char line in the touched files (`_common.py:324`) is pre-existing in
  `read_table`.

## Still open / for your call

1. Greenhouse apply-form prose now rides along (finding 1's measured cost, above).
2. LinkedIn `posted`/`salary_label` are `""` on the recorded fixture — the selectors are in
   place but unproven against a live guest page that has them.
3. Hiredly `parse_detail` remains unverified against a real payload (carried over from Task 6).
