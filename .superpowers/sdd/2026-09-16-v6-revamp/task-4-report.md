# Task 4 report: `_common.py` + `workspace.py` + workspace templates

## Summary

Implemented the shared stdlib-only helper module `_common.py`, the
`workspace.py` CLI (init/where), and the four workspace templates
(`profile-template.md`, `pipeline-template.md`, `contacts-template.md`,
`answers-template.md`), replacing `candidate-profile-template.md`.

## TDD evidence

**RED** — wrote `tests/test_common.py` and `tests/test_workspace.py` from the
brief (env dict changed per the controller's instruction to
`{**os.environ, "JOB_HUNT_DIR": str(tmp_path)}` instead of a bare
`{"JOB_HUNT_DIR": ..., "PATH": ""}`, to avoid breaking Python startup on
Windows CI — everything else verbatim), then ran:

```
$ python3 -m pytest tests/test_common.py tests/test_workspace.py -q
ImportError while importing test module '.../tests/test_common.py'
ModuleNotFoundError: No module named '_common'
```
(module didn't exist yet, confirming failure before implementation.)

**GREEN** — after implementing `_common.py`:

```
$ python3 -m pytest tests/test_common.py -q
.....
5 passed in 0.04s
```

After implementing `workspace.py` + the four templates:

```
$ python3 -m pytest tests/test_workspace.py -q
..
2 passed in 0.16s
```

Full suite + build check:

```
$ python3 -m pytest -q
...............
15 passed in 0.18s

$ python3 build.py --check
OK: 1 skills pass checks
```

## Files changed

- `skills/job-hunting/scripts/_common.py` (new) — `UA`, `workspace_dir`,
  `slugify`, `optional_import`, `http_get`, `http_post_json`, `read_table`,
  `write_table`, `today`. Rate limiting via a module-level `_last_call: dict[str,
  float]` keyed by host, `time.sleep` to cap each host at ≤1 req/s.
  `http_get`/`http_post_json` catch `HTTPError` → `(e.code, e.read())` and
  `URLError` → `(0, str(e).encode())`; default headers include
  `User-Agent: UA` (POST also sets `Content-Type: application/json`).
  `read_table`/`write_table` locate a table by scanning for a `|`-prefixed
  line followed by a separator line (optionally anchored after a heading
  line matched by exact stripped equality); `write_table` re-renders and
  splices in place, or appends (with a `## {heading}` if given) when no
  table is found.
- `skills/job-hunting/scripts/workspace.py` (new) — `init`/`where` CLI, exactly
  as specified in the brief.
- `skills/job-hunting/assets/pipeline-template.md` (new) — verbatim from brief.
- `skills/job-hunting/assets/contacts-template.md` (new) — verbatim from brief.
- `skills/job-hunting/assets/answers-template.md` (new) — sections for
  expected salary (per-market table: single number + range), notice period /
  earliest start, work authorization (per-country table), why this company
  (reusable pattern note), why leaving, relocation, years-in-tool table,
  three STAR stories (title + one-liner), references table (name,
  relationship, permission asked Y/N).
- `skills/job-hunting/assets/profile-template.md` (new, replaces
  `candidate-profile-template.md`) — §1–§8 and old §11 kept verbatim
  (renumbered §1–§8, §10), with the exact field labels the brief called out
  (`**Search keywords / title variants:**`, `**Job market / country I'm
  hunting in:**`, `**Salary expectation:**`, `**Must-haves in a posting:**`,
  `**Dealbreakers (must avoid):**`, `**Job boards to search:**`,
  `**Location:**`) preserved verbatim for the later parser. New §9
  "Tracking" says "Workspace mode: see `pipeline.md`, `contacts.md`,
  `answers.md`. Chat mode (claude.ai): keep the three tables below in this
  file." followed by ### Pipeline, ### Offers, ### Contacts, and ###
  Soft skills development tables, with column headers copied verbatim from
  `pipeline-template.md`/`contacts-template.md` (and the old §10 soft-skills
  table). Final file is §1–§10.
- `skills/job-hunting/assets/candidate-profile-template.md` — removed via
  `git rm` (shows as a rename in `git show --stat`).
- `skills/job-hunting/SKILL.md` — updated the one live reference to
  `assets/candidate-profile-template.md` → `assets/profile-template.md` (Step
  0 memory-file pointer). This file wasn't in the brief's file list but was
  the only in-tree consumer of the deleted asset path, so leaving it
  unpatched would have shipped a dangling reference; the plan/spec docs under
  `docs/superpowers/` that also mention the old filename are historical
  planning artifacts and were left untouched.
- `tests/test_common.py`, `tests/test_workspace.py` (new) — from the brief,
  with the env-dict tweak noted above.

## Self-review

- File list matches the brief exactly, plus the one-line `SKILL.md` pointer
  fix explained above.
- Names/signatures match the "Interfaces (Produces)" section verbatim,
  including `UA`.
- No extra helpers added (left `html_to_text`/`docx_text` for later tasks, as
  instructed).
- Tests are the brief's own tests (verbatim except the env-dict change),
  which exercise real read/write-table round-tripping, slugify, workspace
  resolution precedence (env > local `./job-hunt` > `~/job-hunt`), and the
  `workspace.py init`/idempotency behavior through an actual subprocess.
- `python3 -m pytest -q` (15 tests, all passing) and `python3 build.py
  --check` both clean; `git status` clean after commit.

## Concerns

- None blocking. Two judgment calls worth flagging for review:
  1. The `SKILL.md` one-line reference fix (outside the brief's file list,
     but necessary to avoid a broken pointer left by deleting the asset it
     named).
  2. `read_table`/`write_table`'s table-detection regex/logic is my own
     implementation of the brief's prose spec (not literally provided as
     code) — validated against the brief's exact test assertions, including
     the round-trip re-parse check, but later tasks that read/write
     `pipeline.md`/`contacts.md`/`answers.md` should double check their
     table shapes parse as expected once written by real scripts.

## Commit

`b037ef9` — "workspace: ~/job-hunt layout, templates, markdown-table
helpers" (Co-Authored-By: Claude Fable 5.1 <noreply@anthropic.com>)

## Fix report — round 1 of 5 (review findings on `_common.py`)

Three findings from task review, all fixed:

1. **Critical — heading scope unbounded.** `_find_table` only used `heading`
   to set a *start* offset and then scanned to the end of the document, so
   `read_table(md, "## Pipeline")` could return a table that actually lived
   under a later `## Offers` heading, and `write_table(..., heading="##
   Pipeline")` could silently overwrite that later table.

   Fix: added `_section_bounds(lines, heading)`, which returns `(start,
   end)` — from the line after the heading up to (not including) the next
   line starting with `#` at any level, or `None` if the heading itself
   isn't in the document. `_find_table` now searches only within those
   bounds. `read_table` naturally returns `([], [])` when no table exists in
   that bounded section. `write_table`, when no table is found there, now
   inserts the new table at the end of that section (before the next
   heading), separated by blank lines, without touching anything outside the
   section — verified manually and via test before writing it up:
   ```
   >>> read_table(MD2, "## Pipeline")
   ([], [])
   >>> write_table(MD2, [...], heading="## Pipeline")
   ## Pipeline
   no table here yet

   | Company | Role |
   |---|---|
   | Grab | SWE |

   ## Offers
   ...  # Offers row untouched
   ```

2. **Important — escaped pipes didn't round-trip.** `_render_table` escaped
   `|` to `\|` in cell values, but `_split_row` split on every `|`,
   including escaped ones, corrupting cells like `"A|B"`.

   Fix: `_split_row` now splits on unescaped pipes only via
   `re.compile(r"(?<!\\)\|")`, then unescapes `\|` → `|` in each resulting
   cell. Verified: writing a row with `Notes: "A|B"` and reading it back
   returns `"A|B"` intact.

3. **Important — no tests for `http_get`/`http_post_json`/rate limiter.**
   Added tests in `tests/test_common.py`, all monkeypatching
   `urllib.request.urlopen` (no network):
   - `test_http_get_returns_status_and_body` — fake response with
     `.status`/`.read()` → `(200, b"body")`.
   - `test_http_get_returns_http_error_code_and_body` — raises
     `urllib.error.HTTPError(url, 404, "nf", {}, io.BytesIO(b"missing"))` →
     `(404, b"missing")`.
   - `test_http_get_returns_zero_status_on_url_error` — raises
     `urllib.error.URLError("boom")` → status `0` and `b"boom" in body`.
   - `test_http_post_json_sends_content_type_and_json_body` — captures the
     `Request` object passed to the fake `urlopen` and asserts
     `req.get_header("Content-type") == "application/json"` and
     `json.loads(req.data.decode()) == {"a": 1}`.
   - `test_rate_limit_same_host_sleeps_once` /
     `test_rate_limit_different_hosts_do_not_sleep` — monkeypatch
     `c.time.sleep` (recording calls) and `c.time.monotonic` (a
     deterministic fake clock via `iter([...])`) and call `c._rate_limit`
     directly twice: same host → exactly one recorded sleep call (≥ 0);
     different hosts → no sleep calls. Each test clears the module-level
     `c._last_call` dict first so rate-limiter state doesn't leak between
     tests.

No third-party dependencies were introduced; `_common.py` remains stdlib
only.

### Tests / commands run

```
$ python3 -m pytest tests/test_common.py -q
..............
14 passed in 0.05s

$ python3 -m pytest -q
........................
24 passed in 0.17s

$ python3 build.py --check
OK: 1 skills pass checks
```

### Files changed (this round)

- `skills/job-hunting/scripts/_common.py` — `_section_bounds` added;
  `_find_table` bounded to the heading's section; `write_table` inserts
  within-section when a heading is given and no table exists yet;
  `_split_row` now pipe-escape aware.
- `tests/test_common.py` — added heading-scope tests (`MD2` fixture),
  pipe round-trip test, and http/rate-limiter tests (10 new tests total,
  5 → 14).

### Commit

`50ddffe` — "_common: bound heading search to its section, pipe-safe cells,
http tests" (Co-Authored-By: Claude Fable 5.1 <noreply@anthropic.com>)
