### Task 7: `search_jobs.py` — criteria, dedupe, knockouts, ranking

**Files:**
- Create: `skills/job-hunting/scripts/search_jobs.py`
- Test: `tests/test_search_jobs.py`

**Interfaces:**
- Consumes: `sources.*.search`, `_common.workspace_dir/read_table`.
- Produces CLI: `search_jobs.py [--keywords "..."] [--location "..."] [--country MY|SG] [--days N] [--salary-min N] [--sources jobstreet,mcf,linkedin,hiredly,indeed] [--pages N] [--markdown|--json] [--all] [--no-seen]`. Defaults read from `profile.md` §2/§3 via `read_criteria(profile_md) -> dict` (keys: `keywords: list[str]`, `location`, `country`, `salary_min`, `must_have: list[str]`, `dealbreakers: list[str]`, `boards: list[str]`). Functions: `knockout(job, criteria) -> str | None` (reason or None), `rank(jobs) -> list[dict]` (freshness desc, then salary_max desc, then source priority jobstreet > mcf > linkedin > hiredly > indeed), `dedupe(jobs, seen: dict) -> tuple[list[dict], dict]` (key = `id`; secondary key = `slugify(company+title)`; updates `seen[id] = first_seen_date`), `render_markdown(jobs, knocked: list[tuple[dict,str]]) -> str`.

**`read_criteria` parsing rules:** profile lines are `- **Label:** value`. Map: "Search keywords / title variants" → split on `,` or `;` → `keywords`; "Location" (§1) → `location`; "Job market / country I'm hunting in" → `country` = "SG" if contains "singapore" else "MY" if contains "malaysia" else first two letters upper; "Salary expectation" → first integer ≥ 1000 → `salary_min`; "Must-haves in a posting" → list; "Dealbreakers (must avoid)" → list; "Job boards to search" → lowercased tokens intersected with known source names (default all except indeed).

**Knockout rules:** any dealbreaker token (case-insensitive) in title/company/teaser → `"dealbreaker: <token>"`; `salary_max` present and `< salary_min` → `"salary below floor"`; if a must-have list is non-empty and none of its tokens appear in title+teaser → `"missing must-have"` (soft: put in a separate "needs a look" list, not dropped); posted older than `--days` → dropped silently.

- [ ] **Step 1: Write failing tests** covering `read_criteria` on `tests/fixtures/sample-profile.md` (copy today's fixture; assert keywords list, country "MY", salary_min 9000), `knockout` for a gambling-company dealbreaker, `dedupe` marks second run's repeats, `rank` order, and an end-to-end `run(criteria, sources={"fake": fake_module}, seen={})` using a stub module whose `search()` returns three normalized jobs.
- [ ] **Step 2: Fail → implement → pass.** Output markdown table columns: `# | Posted | Source | Company | Role | Location / mode | Salary | Link` followed by a "Knocked out" list with reasons and a "Sources used / skipped" line (e.g. `indeed skipped: pip install python-jobspy`). `--json` prints the list. Save updated `seen-jobs.json` unless `--no-seen`. Print `"0 new since last run"` when appropriate.
- [ ] **Step 3: Live smoke** (manual, not CI): `JOB_HUNT_DIR=/tmp/jh python3 skills/job-hunting/scripts/workspace.py init && python3 skills/job-hunting/scripts/search_jobs.py --keywords "software engineer" --location "Kuala Lumpur" --country MY --days 3 --markdown` → non-empty table.
- [ ] **Step 4: Commit** — `search_jobs.py: criteria-driven multi-board search with dedupe, knockouts, freshness ranking`.

