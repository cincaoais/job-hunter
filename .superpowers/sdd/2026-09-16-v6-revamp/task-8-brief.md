### Task 8: `fetch_posting.py`

**Files:**
- Create: `skills/job-hunting/scripts/fetch_posting.py`
- Test: `tests/test_fetch_posting.py`

**Interfaces:**
- CLI: `fetch_posting.py <url-or-id> [--save] [--print]`. `classify(url) -> tuple[source, id, country]` (regexes: `jobstreet.com/job/(\d+)` host `my.`/`sg.` → country; `linkedin.com/jobs/view/...-(\d+)`; `mycareersfuture.gov.sg/job/.*/([0-9a-f]{32})`; `hiredly.com/jobs/([\w-]+)`; else `("generic", url, "")`). `generic_extract(html) -> dict(title, text)` — take `<title>`, drop `script/style/nav/footer/header`, prefer the largest `<main>`/`<article>` block else body, `html_to_text`. `render_posting(job: dict) -> str` → markdown with frontmatter `source, url, company, title, location, salary, posted, fetched, screening_questions` then `## Description`. `save(job) -> Path` writes `postings/<slugify(company-title)>.md` (suffix `-2` on collision with different url).
- CloakBrowser fallback: when generic fetch status is 403/503 or body contains `cf-challenge`/`Just a moment`/`Prove your humanity`, and `optional_import("cloakbrowser")` exists → `launch(headless=True)`, `goto`, `body.innerText`; otherwise print `"blocked; paste the posting text instead (or pip install cloakbrowser)"` and exit 3.

- [ ] **Step 1: Tests** — `classify` on six sample URLs; `generic_extract` on a small inline HTML; `render_posting` contains frontmatter keys; `save` path slug and collision suffix (tmp workspace).
- [ ] **Step 2: Implement, run, commit** — `fetch_posting.py: URL → postings/<slug>.md with board-specific detail APIs and stealth-browser fallback`.

