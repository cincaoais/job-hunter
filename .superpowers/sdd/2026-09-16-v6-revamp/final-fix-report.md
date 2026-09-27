# Final-review fix report — v6-revamp

Base 60ebb4b → head 176a1e2 (6 commits). Not pushed, not tagged. `progress.md` (controller's) left unstaged.

| Commit | Subject | Items |
|---|---|---|
| a92482a | fetch_posting: never save a still-blocked browser page; JobStreet country domains | 1, 10 |
| 7fdc96b | build_resume: unindented hard wraps continue their bullet; name failing PDF backends | 4, 12 |
| 2412585 | search_jobs: salary floor only in its own currency; name an unsupported country | 5, 11, 6, 9 |
| 3fe729d | windows: python fallback for today/review; CI on every branch | 2, 3 |
| 8e8c057 | minors: JOB_HUNT_DIR expands ~, no (unset) funnel bucket for unsent rows, --check count | 13, 14, 15 |
| 176a1e2 | references: literal references brief, undated referral ask; v6.0.1 follow-ups | 7, 8, 16 |

Each commit was checked out in a temp worktree and passes on its own: 413 → 415 → 426 → 428 → 431 → 431 passed, `build.py --check` OK at every step.

## Important

**1. Still-blocked browser page saved as a posting.**
Change: `scripts/fetch_posting.py:59-61` adds `BROWSER_BLOCK_MARKERS` (BLOCK_MARKERS plus "humans only", "prove you are human", "verify you are human", "are you a robot") and `BROWSER_MARKER_SPAN = 2000`. `:272` adds `is_browser_blocked(got)`: blocked when the title or the first 2,000 chars match a marker, or the text is under `MIN_GENERIC_TEXT`. `:339`: after `browse()`, a blocked result returns `(None, "blocked")`, so the CLI prints `BLOCKED_MSG` and exits 3.
Design note: markers are read from the title and the text's first 2,000 chars, not the whole text. A challenge page states itself at the top, and the existing HTTP-path rule already keeps a real JD that says "access denied" further down.
Tests: `tests/test_fetch_posting.py::test_main_exits_3_and_saves_nothing_when_the_browser_is_walled` (Glassdoor "Humans only … Your IP address: 203.0.113.42" behind two 403s; `main([url, "--save"]) == 3`, blocked message on stderr, IP not echoed, nothing under `postings/`). `::test_is_browser_blocked[cloudflare|robot-check|thin-shell|posting|late-access-denied]`. The existing fake-browser texts were under 200 chars, so they were lengthened (`BROWSER_JD`) and those tests still assert the same behaviour. On the old code the 4 new blocked cases fail.

**2. Windows `python3`.**
Change: `skills/today/SKILL.md:8` and `skills/review/SKILL.md:8` now read `` !`"$(command -v python3 || command -v python)" ${CLAUDE_SKILL_DIR}/../job-hunting/scripts/tracker.py today` `` (and `funnel`), still the first body line. `skills/job-hunting/SKILL.md:21-22` (storage-mode section) adds "Commands below use `python3`; if it is not found (a python.org install on Windows), use `python` — or `py -3`." SKILL.md is 140 lines and its description is unchanged. `README.md:204-210` (§Windows) gives the remedy: the Microsoft Store Python adds `python3`; otherwise run with `python`/`py -3`; the today/review inline commands already fall back.
Test: `tests/test_build.py::test_inline_tracker_command_falls_back_to_python[today|review]`.
Manual check: I ran the inline line under bash and zsh. With `PATH` holding only a `python` symlink (`command -v python3` → none), it still ran `tracker.py funnel`.

**3. CI never ran on Windows for this branch.**
Change: `.github/workflows/ci.yml:3` is `push: { branches: ["**"], tags: ["v*"] }` and `pull_request` is kept. `:5-6` adds top-level `permissions: contents: read`. `:22-23` keeps `contents: write` on `build`. The release step is still `if: startsWith(github.ref, 'refs/tags/v')` (`:31`). The YAML parses.
Test: none (workflow). It takes effect on the next push.

**4. Hard-wrapped bullet corrupts the .docx.**
Change: `scripts/build_resume.py:167` adds an `after_bullet` flag. It is set after a bullet (`:224`), kept through continuations, and cleared by headings, entry lines and skill groups. `:207` defines `continues = last is not None and not blank and (after_bullet or kind == "summary")`. `:225` treats the line as a continuation when `continues` holds or the line is indented (the indentation rule is unchanged).
Test: `tests/test_build_resume.py::test_an_unindented_hard_wrap_continues_its_bullet`. The parsed entry has `bullets == ["Cut latency 40% by moving the hot path to Redis and batching writes", "Second bullet"]` and `lines == []`. `docx_text(docx_bytes(...))` contains the tail once, on the line right after the `Dev — Acme, KL\t2019 – 2021` heading. It fails on the old code.

**5. Salary-floor knockout ignores currency.**
Change: `scripts/search_jobs.py:60` adds `_CURRENCY_RE` and `:137` adds `_salary_currency`: RM/MYR/ringgit → MYR, S$/SG$/SGD → SGD, none → "". `:174` puts the result in `criteria["salary_currency"]`. `:239` `_floor_currency` returns the stated currency, else the search market's (`MARKET_CURRENCY` `:47`), else "". `:245` `_is_floor_comparable` compares with the job's currency, or with the job's market currency when the job has none. A floor with no currency and no market is compared as before, which keeps the existing tests green. `:277`: the knockout runs only when the currencies are comparable.
Also:
- `:377`: `_gather` passes the floor to the boards' server-side filter (JobStreet `salaryrange`, MCF `salary`) only when it is in the market's currency. Otherwise an RM floor on an SG search would still hide SGD postings at the source.
- `:618`: `--salary-min` clears `salary_currency`, so it is read in the market's currency, and its help text says so.
Tests (all in `tests/test_search_jobs.py`):
- `::test_salary_floor_applies_only_in_its_own_currency`: an RM 15,000 floor keeps an SGD 8,000 posting, knocks out an RM 9,000 one, knocks out a currency-less MY one and keeps a currency-less SG one.
- `::test_read_criteria_salary_currency` (5 cases).
- `::test_run_keeps_a_foreign_floor_away_from_the_board_filter`.
- The existing salary tests are unchanged and green.

**6. sourcing.md misstates politeness.**
Change: `references/sourcing.md:133-139` now says:
- Every host is rate-limited to about one request per second (`_common._rate_limit`). Indeed goes through python-jobspy's own client.
- LinkedIn also pauses 2.5 s between pages and stops at 3 pages.
- Board APIs and first fetch attempts identify as `job-hunter-skill`. LinkedIn's guest pages (search and detail both send `BROWSER_UA`) and the generic-page retry use a browser User-Agent, because those pages return nothing to a non-browser client.
Test: none (reference text). Verified against `_common.py:65,106-120`, `sources/linkedin.py:34-36,138,185` and `fetch_posting.py:37-45`.

## Fix-before-merge

**7.** `references/post-offer.md:102-105` adds a **References brief** block with the literal template, plus "Not the current manager until after resigning." The file is 167 lines (≤ 175). `ats_check.py --slop` on the block: none found.
**8.** `references/networking.md:100`: the referral ask now reads "I've spent [n] years on [Y] — for example, [one sourced result from profile §5, as stated], which lines up with …". "most recently" is removed. `--slop`: none found.

## Minors

**9.** `references/sourcing.md:54-57`: the knocked-out reasons are `dealbreaker: <phrase>` or `salary below floor` (currency-matched); rows missing a must-have go to "Needs a look".
**10.** `scripts/fetch_posting.py:95-97`: `jobstreet.com.sg`/`*.jobstreet.com.sg` → SG, `jobstreet.com.my`/`*.jobstreet.com.my` → MY. Test: `tests/test_fetch_posting.py::test_classify_jobstreet_country_domains` (4 URLs).
**11.** `scripts/search_jobs.py:395-399`: a `ValueError` whose message says "unsupported country" becomes `"<source>: unsupported country <CC>"`; any other `ValueError` still reads "search failed (ValueError)". Test: `tests/test_search_jobs.py::test_run_names_an_unsupported_country` (the real `sources.jobstreet` with country ID; it raises before any network call).
**12.** `scripts/build_resume.py:692` `render_pdf(..., failures=None)` appends `"playwright (ErrorClass)"` / `"cloakbrowser (ErrorClass)"` for a backend that imports but fails (`:712`, `:723`). The CLI prints `note: installed but failed: …` on stderr after the unchanged "PDF skipped" line (`:941`). Test: `tests/test_build_resume.py::test_cli_pdf_names_a_backend_that_is_installed_but_fails`.
**13.** `scripts/_common.py:38`: `Path(env).expanduser()` (docstring updated). Test: `tests/test_common.py::test_workspace_dir_env_expands_a_leading_tilde` (sets HOME and USERPROFILE, so it runs on Windows too).
**14.** `scripts/tracker.py:336-337`: `_group` skips rows with an empty Channel/Source cell whose stage is `saved`. `total` still counts them as rows. A sent row with no channel still shows "(unset)". Test: `tests/test_tracker.py::test_funnel_has_no_unset_bucket_for_rows_never_sent`.
**15.** `scripts/workspace.py:6`: `import shutil, sys` (json dropped). `build.py:114`: the OK line counts only directories that contain `SKILL.md`. Test: `tests/test_build.py::test_check_ok_line_counts_only_skill_directories` (2 skills plus a stray `.DS_Store` → "OK: 2 skills pass checks").
**16.** `docs/followups-v6.0.1.md` (new) is titled "v6.0.1 follow-ups" and has a one-line intro and a checklist with file:line anchors, grouped as Scripts / Resume builder / References / Round 4 leftovers. It ends with "re-run scenarios O and Q". OK-count and CI permissions are omitted as instructed. The T14 "PDF backend failures" item is now mostly done (item 12). Its remaining part, the `TypeError` retry around `cloak.launch(stealth_args=False)` that can mask an unrelated `TypeError`, stays listed.

## Command output (head 176a1e2)

```
$ python3 -m pytest -q -m "not network"
431 passed, 3 deselected in 0.93s

$ python3 build.py --check
OK: 12 skills pass checks

$ python3 -m pytest -q -m network        # fetch_posting.py and search_jobs.py were touched
3 passed, 431 deselected in 1.37s
```

## Concerns

- Item 1 now also classes a browser result under 200 chars as blocked, even when the HTTP answer was a thin 200 rather than a 403. A genuinely tiny posting behind a JavaScript shell now exits 3 ("paste the text") instead of being saved. That is the requested rule. The reply is harmless, since it asks the user to paste.
- Item 5 is read as "a floor with no stated currency uses the search market's currency". Without that, a bare `--salary-min` or a currency-less profile line would never knock anything out, and the existing salary tests would break.
- Item 3: pushes now run CI on every branch, and a same-repo PR runs it twice (push + pull_request). This was accepted in the controller's ruling.
