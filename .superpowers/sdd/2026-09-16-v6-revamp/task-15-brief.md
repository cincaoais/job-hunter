### Task 15: `ats_check.py` + slop phrase list

**Files:**
- Create: `skills/job-hunting/scripts/ats_check.py`, `skills/job-hunting/assets/slop-phrases.txt`
- Test: `tests/test_ats_check.py`

**Interfaces (CLI):** `ats_check.py <file.docx|file.pdf|file.md> [--posting postings/x.md | --keywords "a,b,c"] [--lint] [--slop] [--json]`. Functions: `extract_text(path) -> tuple[str, str]` (text, method: "docx-xml" | "pypdf" | "pdftotext" | "markdown" | "unavailable"), `keyword_coverage(text, keywords) -> dict{present:[], missing:[], ratio}`, `extract_keywords(posting_md) -> list[str]` (capitalized tech tokens and comma-separated items after "Requirements"/"Skills" headings, deduped, max 25), `lint_six_second(text, target_title=None) -> list[str]` (checks: contact email + phone present as literal text; a `20\d\d` date in first 15 lines; a digit or `%` in the first bullet after the first Experience heading; word count ≤ 900 (≈ 2 pages); if `target_title` given, its words appear in the first 5 lines), `slop_scan(text) -> list[tuple[phrase, count]]` using `assets/slop-phrases.txt` (one phrase per line; ship ~40: "passionate about", "proven track record", "results-driven", "dynamic team player", "I am writing to express my interest", "in today's fast-paced", "leverage my skills", "hit the ground running", "detail-oriented", "think outside the box", "synergy", "delve", "tapestry", "testament to", "I am confident that", "excited about the opportunity", "aligns perfectly", "unique blend", "go-getter", "self-starter", "hardworking", "team player", "excellent communication skills", "responsible for", "assisted with", "duties included", "helped with", "various tasks", "fast learner", "as a highly motivated", "I believe I would be a great fit", "thank you for considering", "seamlessly", "cutting-edge", "state-of-the-art", "robust", "spearheaded", "utilize", "in conclusion", "furthermore", "moreover").
- PDF extraction: `pypdf` if importable; else `pdftotext` on PATH via `subprocess`; else `("", "unavailable")` and the CLI prints the declared fallback line from `resume-builder.md` and exits 2.
- Report (markdown): method line; coverage `n/m` with missing list; lint findings; slop findings; exit 0 always unless extraction unavailable.

- [ ] **Step 1: Tests** — docx built from the Task 14 fixture: coverage finds "Go" and misses "gRPC"; lint passes on the fixture and flags a crafted text missing email; `slop_scan("I am passionate about ...")` returns the phrase; `extract_keywords` on `tests/fixtures/sample-jd.md` includes "Go" and "PostgreSQL".
- [ ] **Step 2: Implement; run; commit** — `ats_check.py: text-layer extraction, keyword coverage, 6-second lint, anti-slop scan`.

---

## Phase 5 — Verification, docs, release

