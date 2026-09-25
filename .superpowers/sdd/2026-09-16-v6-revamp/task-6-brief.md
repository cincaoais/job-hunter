### Task 6: Board sources with recorded fixtures

**Files:**
- Create: `skills/job-hunting/scripts/sources/__init__.py` (empty), `sources/jobstreet.py`, `sources/mcf.py`, `sources/linkedin.py`, `sources/hiredly.py`, `sources/indeed.py`
- Create: `tests/fixtures/recorded/jobstreet_my_search.json`, `jobstreet_detail.json`, `mcf_search.json`, `mcf_detail.json`, `linkedin_search.html`, `linkedin_detail.html`, `hiredly_kl.html` — record each with one live call (see step 1)
- Test: `tests/test_sources.py`

**Interfaces (Produces):**
```python
# Every source module exposes:
NAME: str                                                   # "jobstreet" | "mcf" | "linkedin" | "hiredly" | "indeed"
def search(keywords: str, location: str, *, country: str, days: int | None = None,
           salary_min: int | None = None, pages: int = 1, fetch=None) -> list[dict]
def parse_search(raw: bytes | str, *, country: str) -> list[dict]       # pure, fixture-testable
def detail(job_id: str, *, country: str, fetch=None) -> dict | None      # {"description_md": str, "title":..., "company":..., "url":..., "screening_questions": [...]}
def parse_detail(raw: bytes | str, *, country: str) -> dict
# Normalized job dict (all keys always present, "" or None when unknown):
# {"id": "jobstreet:94655291", "source": "jobstreet", "title", "company", "location", "mode" ("Hybrid"/"Remote"/"Onsite"/""),
#  "salary_min": int|None, "salary_max": int|None, "currency": "MYR"|"SGD"|"", "salary_label": str,
#  "posted": "YYYY-MM-DD"|"", "url": str, "teaser": str, "applicants": int|None, "country": "MY"|"SG"}
```
`fetch` is an injectable `(url, headers, method, payload) -> (status, bytes)` for tests; default uses `_common.http_get/http_post_json`.

**Exact requests (verified live 2026-09-16):**
- JobStreet search: `GET https://{my|sg}.jobstreet.com/api/jobsearch/v5/search?siteKey={MY|SG}-Main&sourcesystem=houston&locale=en-{MY|SG}&keywords=<q>&where=<loc>&page=<n>&pageSize=100&sortmode=ListedDate` plus optional `daterange=<days>`, `salaryrange=<min>-&salarytype=monthly`. JSON `data[]` fields: `id, title, companyName, salaryLabel, listingDate, locations[0].label, workTypes[], workArrangements.displayText, teaser, bulletPoints[]`. URL = `https://{host}/job/{id}`. Parse `salaryLabel` like `RM 15,000 – RM 20,000 per month` / `$4,000 – $6,500 per month` with regex `(\d[\d,]*)` → ints; currency from country.
- JobStreet detail: `POST https://{host}/graphql` JSON `{"operationName":"jobDetails","variables":{"jobId":ID,"locale":"en-MY","zone":"asia-4","timezone":"Asia/Kuala_Lumpur"},"query":Q}` where SG uses `en-SG`, `asia-5`, `Asia/Singapore` and Q is exactly:
  ```
  query jobDetails($jobId: ID!, $zone: Zone!, $locale: Locale!, $timezone: Timezone!) { jobDetails(id: $jobId) { job { id title isExpired shareLink(platform: WEB, zone: $zone, locale: $locale) advertiser { id name(locale: $locale) } content(platform: WEB) abstract location { label(locale: $locale, type: LONG) } salary { label currencyLabel(zone: $zone) } listedAt { label(context: JOB_POSTED, length: SHORT, timezone: $timezone, locale: $locale) dateTimeUtc } workTypes { label(locale: $locale) } products { bullets } } } }
  ```
  `content` is HTML → convert to markdown-ish text with `html_to_text()` in `_common` (strip tags, `<li>` → `- `, `<br>`/`</p>` → newline, unescape entities).
- MCF search: `POST https://api.mycareersfuture.gov.sg/v2/search?limit=20&page=<n>` body `{"search": q, "sortBy": ["new_posting_date"]}` (+ `"salary": min` when given). `results[]`: `title, postedCompany.name, salary.minimum/maximum, metadata.jobPostId/newPostingDate/totalNumberJobApplication/jobDetailsUrl, positionLevels[].position, employmentTypes[].employmentType, address.districts[0].location (fallback "Singapore"), uuid`. Detail: `GET https://api.mycareersfuture.gov.sg/v2/jobs/{uuid}` → `description` (HTML), `minimumYearsExperience`, `screeningQuestions[]`.
- LinkedIn search: `GET https://www.linkedin.com/jobs-guest/jobs/api/seeMoreJobPostings/search?keywords=<q>&location=<loc>&start=<0|25|50>` (+ `&f_TPR=r{days*86400}`), browser-like UA. Parse each `<li>`: title `class="base-search-card__title"`, company `base-search-card__subtitle`, location `job-search-card__location`, `<time ... datetime="YYYY-MM-DD">`, link `a.base-card__full-link[href]` (strip `?` query), optional `job-search-card__salary-info`. Job id = trailing digits of the link path. Cap pages at 3; sleep 2.5 s between; on 429 stop and return what was collected with a `warnings` note.
- LinkedIn detail: `GET https://www.linkedin.com/jobs-guest/jobs/api/jobPosting/{id}` → description inside `<div class="show-more-less-html__markup ...">`.
- Hiredly: `GET https://my.hiredly.com/jobs?state=<State>` → `<script id="__NEXT_DATA__">` JSON → `props.pageProps.jobs[]`: `title, company.name, salary ("3500 - 4999"), stateRegion, jobType, activeAt, slug, careerLevel, minYearsExperience`; URL `https://my.hiredly.com/jobs/{slug}`. Keyword filter client-side (case-insensitive substring on title). MY only.
- Indeed: only if `optional_import("jobspy")`; `jobspy.scrape_jobs(site_name=["indeed"], search_term=q, location=loc, results_wanted=25, country_indeed={"MY":"malaysia","SG":"singapore"}[country])`; map columns `title, company, location, date_posted, min_amount, max_amount, currency, job_url, description[:300]`. When jobspy is missing return `[]` and set module-level `UNAVAILABLE_REASON = "pip install python-jobspy"`.

- [ ] **Step 1: Record fixtures** (one call each, save raw bytes to `tests/fixtures/recorded/`): JobStreet MY search `keywords=software engineer&where=Kuala Lumpur&pageSize=10`; JobStreet detail for the first id; MCF search `software engineer` limit 5; MCF detail for first uuid; LinkedIn search KL start=0; LinkedIn detail for first id; Hiredly KL page. Trim nothing; commit them.
- [ ] **Step 2: Write `tests/test_sources.py`** — for each source: `parse_search(fixture)` returns ≥ 1 job whose keys equal the normalized key set, `posted` matches `^\d{4}-\d{2}-\d{2}$` or "", `url` startswith `https://`, ids prefixed `source:`; `parse_detail(fixture)["description_md"]` length > 200 and contains no `<`. Plus salary parsing unit tests: `jobstreet.parse_salary("RM 15,000 – RM 20,000 per month") == (15000, 20000)`, `("", ) -> (None, None)`, `hiredly.parse_salary("3500 - 4999") == (3500, 4999)`.
- [ ] **Step 3: Run → fail (ImportError).**
- [ ] **Step 4: Implement the five modules + `html_to_text` in `_common.py`.**
- [ ] **Step 5: Run tests → pass. Commit.**

```bash
git add skills/job-hunting/scripts tests
git commit -m "sources: JobStreet MY/SG, MyCareersFuture, LinkedIn guest, Hiredly, optional Indeed — fixture-tested parsers

Co-Authored-By: Claude Fable 5.1 <noreply@anthropic.com>"
```

