# Task 15 report — `ats_check.py` + `assets/slop-phrases.txt`

**Status:** DONE_WITH_CONCERNS
**Commit:** 22575a4 `ats_check.py: text-layer extraction, keyword coverage, 6-second lint, anti-slop scan`
(trailer `Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>`)

## Files
- `skills/job-hunting/scripts/ats_check.py` (new, stdlib only)
- `skills/job-hunting/assets/slop-phrases.txt` (new): all 41 brief phrases plus 7 inflections (hard-working, synergies, delves, delving, utilized, utilizing, utilise). 48 total, grouped with `#` comments.
- `tests/test_ats_check.py` (new, 42 tests)

## What it does (against the binding decisions)
- `extract_text(path) -> (text, method)`
  - `.docx` → `_common.docx_text` ("docx-xml").
  - `.pdf` → `pypdf` if importable ("pypdf"). Otherwise `pdftotext -raw -enc UTF-8 <file> -` through `subprocess.run` with a 60 s timeout ("pdftotext-raw"; form feeds become newlines). Otherwise `("", "unavailable")`.
  - `.md` → "markdown", with `#`, `**` and link syntax stripped and `*`/`+` bullets normalised to `- `. `.txt` → "text".
  - An unknown suffix is sniffed for PDF or zip magic; failing that it raises ValueError.
  - If pypdf fails on a damaged PDF, pdftotext is tried before giving up.
- `keyword_coverage(text, keywords)`
  - Returns `{present, missing, ratio}`.
  - Matching is case-insensitive and NFKC/curly-quote folded, with word boundaries. Keyword whitespace matches any whitespace, including line breaks in PDFs.
  - `C++`, `C#`, `.NET` and `Node.js` match literally. `C` does not match inside `C++`/`C#`, `Java` not inside `JavaScript`, `SQL` not inside `PostgreSQL`.
  - Keywords are deduped case-insensitively.
- `extract_keywords(posting_md)`
  - Reads the body after `## Description`, or strips the frontmatter.
  - Requirement-ish headings: Requirements, Qualifications, Skills, Must have, What you'll need, Nice to have, plus a few close variants. They are detected as `#` headings, `**bold**` lines, short plain lines and `Skills: a, b` inline forms.
  - Within those sections: tech tokens become keywords on their own. Other words form stopword-separated runs, trimmed of generic words (experience/strong/team/…) and capped at 3 words.
  - A posting with no requirement headings yields tech tokens only. Deduped, max 25.
  - Sample JD gives: backend, Go, gRPC, microservices, Kubernetes, EKS, PostgreSQL, schema design, query tuning, on-call, English, Payments, fintech, AWS, mentoring.
- `lint_six_second(text, target_title=None)`: one line per check, `ok <check>` or `FAIL <check>: <why>`.
  - **contact**: an email, and a phone of 7–15 digits. Year ranges such as `2019 - 2021` are not counted as phones.
  - **date**: a `(19|20)\d\d` year in the first 15 non-empty lines, ignoring emails, URLs and phones.
  - **first-bullet**: the first `- `/`• ` line after a short line matching experience (or employment/work history) must contain a digit or `%`.
  - **length**: ≤ 900 words passes; the line gives the word count.
  - **title**: with `--target-title`, every word of 3+ letters except and/of/the must appear in the first 5 non-empty lines. `--target-title` implies `--lint`.
- `slop_scan(text, phrases=None)`: case-insensitive; letter boundaries only where the phrase starts or ends with a letter; curly apostrophes fold to straight; a hyphen in a phrase also matches a space. Sorted by count, descending. `get_slop_phrases(path=None)` skips blank lines and `#` comments.
- **CLI**
  - Arguments: `<file> [--posting F | --keywords "a,b"] [--lint] [--target-title T] [--slop] [--text] [--json]`. `--posting` and `--keywords` are mutually exclusive (argparse, exit 2).
  - Report lines: `**Method:** <method> (<file>)`, then `**Keywords:** n/m present — missing: …`, then `present: …`, then `**Lint:**` with its lines, then `**Slop:**` lines or `**Slop:** none found`.
  - `--json` prints the same content as one dict.
  - Exit 0 whenever extraction worked. Exit 2 on bad arguments, a missing or unreadable file or posting, an unsupported type, or an empty `--keywords`; the message goes to stderr as `ats_check.py: …` with no traceback.
  - When extraction is unavailable, the exact fallback line goes to stdout and the exit is 2. A test checks it matches `resume-builder.md` line 127.

## TDD
The tests were written first and failed at collection (`ModuleNotFoundError`); after implementation all 42 passed.

What the tests cover:
- docx built from `resume-sample.md` with `build_resume.docx_bytes`: coverage finds Go and PostgreSQL and misses gRPC; the lint passes.
- Crafted texts: missing email; missing phone, where the year range is not counted as a phone; no number in the first bullet, no date and over-length; round bullets; heading with no bullet.
- `--target-title`: pass case and fail case.
- `slop_scan`: finds the phrase; count ordering and word boundaries (`robustness` is not a hit); apostrophe folding.
- The phrase file: LF line endings, ≥ 40 entries, no duplicates.
- `extract_keywords(sample-jd.md)` includes Go, PostgreSQL, gRPC, Kubernetes and AWS, and no generic words or noise from the "What we offer" section. Also covered: Description-body preference, heading forms, the no-heading fallback, and the cap of 25.
- PDF paths:
  - pypdf through a monkeypatched `optional_import`.
  - pdftotext through a monkeypatched `shutil.which` and `subprocess.run`: asserts `-raw`, not `-layout`, and a timeout.
  - pdftotext failing becomes a ValueError.
  - A real pdftotext run on a hand-built one-page PDF, skipped when pdftotext is absent.
- Unavailable extraction prints the exact line and exits 2.
- CLI: markdown, JSON, posting, empty text layer, bad inputs, and one subprocess run.

**Full suite:** `python3 -m pytest -q -m "not network"` → **360 passed** (318 + 42). `python3 build.py --check` → `OK: 12 skills pass checks`.

## Real end-to-end
`build_resume.py tests/fixtures/resume-sample.md --docx --pdf --template corporate-sidebar --out <scratch>` (the PDF was rendered by cloakbrowser), then `ats_check.py <file> --keywords "Go,PostgreSQL,gRPC" --lint --slop`:

```
**Method:** docx-xml (…/e2e/resume-sample.docx)
**Keywords:** 2/3 present — missing: gRPC
present: Go, PostgreSQL
**Lint:**
ok contact
ok date
ok first-bullet
ok length: 163 words (limit 900, about 2 pages)
**Slop:** none found
```
exit 0

```
**Method:** pdftotext-raw (…/e2e/resume-sample.pdf)
**Keywords:** 2/3 present — missing: gRPC
present: Go, PostgreSQL
**Lint:**
ok contact
FAIL date: no year (19xx/20xx) in the first 15 lines
FAIL first-bullet: no "- " or "• " bullet under the Experience heading (a PDF text layer often drops list markers; lint the .md draft or .docx master)
ok length: 166 words (limit 900, about 2 pages)
**Slop:** none found
```
exit 0

**Sidebar reading order:** sane with `-raw`. The order is name, title, then the sidebar block (CONTACT: location, phone, email, links; SKILLS), then Summary, then Experience (each role followed by its bullets), then Education & Certifications. No lines are interleaved.

For comparison, `pdftotext` in its default mode does interleave: Summary sits between CONTACT and its entries, and the phone number lands under "Experience". That confirms the `-raw` decision.

Also checked: `--posting tests/fixtures/sample-jd.md` on the .md draft gives 7/15 present, and `--target-title "Senior Backend Engineer"` passes. Hiding pdftotext from PATH prints the exact fallback line with exit 2.

## Concerns
1. **The Chromium PDFs have no bullet glyphs in their text layer.** The templates' list markers are drawn as shapes, so `--lint` on a presentation PDF always FAILs first-bullet. The FAIL message says why and points at the .md draft or .docx master. The binding rule is kept as written. The builder already lints the draft (step 4.6) and resume-revamp lints the master, so this only shows up in off-contract use on a PDF.
2. **The sidebar PDF fails `date`.** Contact and skills fill the first 15 extracted lines, so this is an accurate finding for the sidebar layout.
3. **Template text-layer issue (not in this task's scope).** In the sidebar PDF, the narrow sidebar wraps `linkedin.com/in/arif-rahman-` / `example` onto two lines, so an ATS sees broken profile URLs. Worth a follow-up in the Task 14 templates.
4. **Case-insensitive coverage, as bound.** A short keyword like "Go" will count as present on English "go" (for example "go live"). This is a known false-positive risk.
5. **`extract_keywords` is heuristic.**
   - Postings heavy with prose and soft skills still produce some noise, e.g. "lead meetings" and "set agendas" from an EA design posting in `tests/fixtures/recorded`. The Grab posting fills the 25-keyword cap with a few noisy tail items.
   - Tech-heavy postings come out clean.
   - The report prints the `present:` list so the agent sees exactly which keywords were checked.
6. **Additions beyond the brief:**
   - `--text`, which prints the extracted text layer. It is also the default when no check flag is given, because the step-6 reading-order check needs the text.
   - A `present:` line after `**Keywords:**`.
   - An empty-text-layer notice.
   - `markdown_to_text()` as a public helper.
7. **Naming:** the phrase loader is `get_slop_phrases`, not `load_…`. A user-level naming hook retires the `load_` prefix.

---

## Fix round 1

**Commit:** 562d25e `ats_check: PDF-aware lint, case-aware keywords, robust extraction, step-6 evidence` (trailer `Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>`)

**Tests:** `tests/test_ats_check.py` has 66 passing. The regression tests were written first, and 27 of the 29 new cases failed before the fix. The full suite `-m "not network"` gives 384 passed. `python3 build.py --check` is OK.

### Findings and fixes

**1. PDF lint.**
- `lint_six_second(text, target_title=None, method=None)`.
- When `method` is `pypdf` or `pdftotext-raw`, it prints the exact ruling lines `skip date: …` and `skip first-bullet: …`. Contact, length and title still run.
- JSON `lint` carries those `skip …` strings.
- The old PDF hint in the non-PDF no-bullet FAIL was removed.
- Tests: `test_lint_skips_date_and_first_bullet_on_pdf_text[pypdf|pdftotext-raw]`, plus `--lint --json` through mocked pdftotext in `test_cli_pdf_via_pdftotext`.

**2. Keyword false passes.**
- `_keyword_regex` matches case-sensitively when `k.isupper()` or when the keyword has ≤ 2 letters.
- `.`-led keywords need `(?<![\w.])` before them.
- The right boundary for alphanumeric endings is `(?![\w+#]|[-&][^\W\d_])`. This also catches "R&D", which a hyphen-only rule would miss.
- Test: `test_keyword_coverage_lookalikes_and_true_positives`, 11 parametrised cases. It covers go live, Go-to-market, tm.net.my, R&D, C-suite and "the rest" as misses, and Go, `.NET 8`, API↔APIs, Payments↔payment, payment↔Payments as hits.
- The symbol test was updated because ASP.NET no longer counts as `.NET` under the ruling.

**3. Unmarked requirement lines.**
- A plain unmarked line is a heading only if it ends with ":" or matches the requirement or nice regex, or the section vocabulary. The vocabulary is the ruling's list plus information, culture, life at, why join, opportunit*, stand for, how to apply, compensation, welfare, package, duties, what you'll do, day-to-day, the team, our team, who we are. Without these extras, "Additional Information", "Life at Grab" and "Unique Opportunity" in the recorded postings would run on into requirement sections.
- `**bold**`-only lines and `#` headings are still headings.
- When the sections give fewer than 5 keywords, tech tokens from the whole body are merged in.
- Tests: `test_extract_keywords_survives_unmarked_requirement_lines` (sample JD with `- ` stripped), `test_extract_keywords_merges_tech_tokens_when_sections_are_thin`.

**4. Step-6 evidence.**
- `--text` already combined with checks; the text layer prints after the report.
- `resume-builder.md` step 6 and the ATS text-layer section now read exactly `python3 ${CLAUDE_SKILL_DIR}/scripts/ats_check.py <file> --posting postings/<slug>.md --lint --text`. The second place previously said `<file.docx|file.pdf>`.
- `skills/resume/SKILL.md:12` now reads `… --lint --slop --text`.
- Tests: `test_cli_posting_lint_text_prints_all_three_parts`, `test_step6_invocations_ask_for_lint_and_text`.

**5. Phones.**
- `_phones` blanks date ranges and parenthesised groups containing a year before scanning.
- It skips runs preceded by a currency code or symbol (RM, Rp, IDR, SGD, USD, MYR, PHP, THB, VND, EUR, GBP, INR, AUD, HKD, CNY, JPY, $ € £ ¥ ₹).
- Tests: two new `test_lint_flags_missing_contact` params ("Universiti Malaya (2017 - 2021)", "IDR 10.000.000"), and `test_lint_parenthesised_year_range_counts_as_a_date` ("Acme (2019 - 2021)" gives `ok date`).

**6. Experience heading.** Anchored with the ruling's `fullmatch` regex. Tests: "User Experience Designer" is not a heading; "Professional Experience:" is.

**7. Must-have and nice-to-have.**
- New `extract_keyword_groups(posting_md) -> {"must", "nice"}`. Nice means a heading matching nice-to-have, good-to-have, bonus, preferred, desirable or pluses. The two groups are deduped against each other and total at most 25. `extract_keywords` returns must + nice.
- The report prints `**Keywords (must-have):** …` and `**Keywords (nice-to-have):** …` when the posting has nice keywords. JSON adds `keywords.must_have` and `keywords.nice_to_have`. Otherwise the report keeps the plain `**Keywords:**` line.
- Plural tolerance applies to a purely alphabetic last word: a trailing "s" is optional both ways. Words ending in "ss" and ALL-CAPS words ending in S (AWS, EKS) are left alone.
- Tests: `test_extract_keyword_groups_split_must_and_nice`, `test_cli_posting_splits_must_and_nice_to_have`.

**8. Slop.**
- `slop_scan` counts the longest non-overlapping match only, with ties in list order.
- Added utilizes, utilised, utilising, spearhead, spearheading, delved and "I'm confident that". The list now has 55 phrases.
- Tests: `test_slop_scan_longest_match_wins`, extended `test_slop_phrase_file`.

**9. Title.** "-" and space match each other. Test: `test_lint_title_treats_hyphen_and_space_alike`, both directions.

**10. Errors.**
- A pdftotext failure shows only the last non-empty stderr line.
- A phrase file that is not UTF-8 gives `cannot read the phrase list …: it is not UTF-8 text` with exit 2.
- Tests: extended `test_extract_text_pdftotext_failure_raises_valueerror` and `test_cli_unreadable_files_exit_2`.

### End-to-end re-run
Same build (corporate-sidebar), `--keywords "Go,PostgreSQL,gRPC" --lint --slop`:
- **.docx:** unchanged. 2/3 keywords, missing gRPC; all four lint checks ok; no slop.
- **.pdf:** 2/3 keywords, missing gRPC; `ok contact`, `skip date: …`, `skip first-bullet: …`, `ok length: 166 words`; no slop.
- **.pdf with `--posting sample-jd.md --lint --text`:** must-have 5/11, missing gRPC, Kubernetes, EKS, schema design, query tuning, English. Nice-to-have 3/4, missing mentoring. Then the lint lines, then the text layer in sane reading order.
- Keyword extraction on the three recorded postings (EA, Grab, MCF) is unchanged.

### Remaining concerns
- ASP.NET no longer counts as `.NET`, by the ruling.
- "Go" and "GO" differ now, so an ALL-CAPS resume line won't match "Go".
- The section-vocabulary heuristic can still end a requirements section early on a short unmarked line containing "about", "role" or "company". The fewer-than-5 tech-token merge limits the damage.

---

## Fix round 2

**Commit:** bee8338 `ats_check: section headings need a colon or ≤4 words` (trailer `Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>`)

**Tests:** `tests/test_ats_check.py` has 76 passing. The 6 new failing cases failed before the fix. The full suite `-m "not network"` gives 394 passed. `python3 build.py --check` is OK.

**Finding:** requirement sentences that contain a section-vocabulary word were read as headings. Examples: "Information security fundamentals matter here", "Package management experience required here", "Compensation benchmarking…", "Duties may vary…", "Culture fit…". Each one silently ended the requirements section.

**Fix (the ruling), in `_heading`:**
- A plain unmarked line counts as a heading only if it ends with ":" and has ≤ 8 words, or has ≤ 4 words and matches the requirement, nice-to-have or section vocabulary.
- It must still start uppercase and have no mid-line `, ; . ! ? :`.
- `#` headings, bold-only lines and inline `Skills: …` headings are unchanged.
- The rationale is in the `_heading` docstring rather than a comment block, per a user comments hook.

**Stopwords:** added here, essential, need, needs, needed. "What Essential Skills You Will Need" (6 words) is no longer a heading, so as content it would otherwise yield the noise keywords "Essential" and "Need". It sits inside the Grab posting's Qualifications section, so it doesn't change which section applies.

**Tests.** Every case starts with a Requirements lead carrying 5 keywords, so the fewer-than-5 tech-token merge cannot mask a truncated section. "English", which the merge never adds, is the deciding keyword.
- `test_extract_keywords_unmarked_heading_rule`: 9 parametrised cases.
  - Each of the 5 trigger sentences keeps the section open: English, Docker and Terraform are extracted.
  - "Additional Information", "Life at Grab", "What we offer" and a 7-word colon line all still end it.
- `test_extract_keywords_reviewer_repro_block`: Requirements, then the 5 trigger lines in a row with "Information security fundamentals matter here" in the middle, then "Written English, Docker and Terraform". All three keywords are extracted.

**Real postings:** keyword groups for the sample JD and the recorded EA, Grab and MCF postings are identical to round 1.

---

## Fix round 3

**Commit:** 530ecc7 `ats_check: title-case heading signal for unmarked requirement headings` (trailer `Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>`)

**Tests:** `tests/test_ats_check.py` has 82 passing. The 4 new heading cases failed before the fix. The full suite `-m "not network"` gives 400 passed. `python3 build.py --check` is OK.

**Finding (Critical regression from round 2):** an unmarked requirement heading of 5–8 words with no colon did not open the section when it followed a non-requirement section. Examples: "What Essential Skills You Will Need", "Skills and Experience We Are Looking For". Its keywords, English among them, were dropped.

**Fix (the ruling), in `_heading`:** an unmarked line is a heading when it
- (a) ends with ":" and has ≤ 8 words, or
- (b) has ≤ 4 words and matches the requirement, nice-to-have or section vocabulary, or
- (c) has ≤ 8 words, matches that vocabulary, and passes the new `_is_title_cased()`: at least 2 words of 4+ letters, with ≥ 75% of them starting uppercase.

Mid-line or terminal `, ; . ! ? :` still rules a line out, as before. Sentence-case lines stay content. The round-2 stopwords are kept. The helper is named `_is_title_cased` per the user naming hook for bool returns.

**Tests:**
- `test_extract_keywords_title_case_requirement_heading_opens_section`: 4 cases, the two headings × {alone, after a Requirements block that already has ≥ 5 keywords}. Each posting is: About the role, 2 content lines, the heading, then 5 unmarked requirement lines including "Strong written and spoken English required" and Docker/Terraform. English, Docker and Terraform land in `must`.
- `test_extract_keyword_groups_heading_shape_inside_requirements`: 2 cases, both passing before the fix as guards.
  - Inside an open Requirements list, "Strong Python skills preferred for this role" stays content, and Kubernetes, Docker and Terraform stay in `must`.
  - "Nice To Have Skills" switches Kubernetes, Docker and Terraform to `nice`, while the earlier items stay in `must`.

**Real postings:** keyword groups for the sample JD and the recorded EA, Grab and MCF postings are identical to rounds 1 and 2. In the Grab posting, "Get to Know the Team/Role" and "About Grab and Our Workplace" now read as (non-requirement) headings; none of them is inside a requirement section.

---

## Fix round 4

**Commit:** 2d8c074 `ats_check: long title-cased lines may open a requirements section, never end one` (trailer `Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>`)

**Tests:** `tests/test_ats_check.py` has 85 passing (82 + 3). The repro test and the vocabulary-matching trade-off case failed before the fix; the no-vocabulary trade-off case already passed. The full suite `-m "not network"` gives 403 passed. `python3 build.py --check` is OK.

**Finding:** rule (c) in `_heading()` (5–8 title-cased words, no colon) accepted both the requirement/nice-to-have vocabulary (`_section_kind`) and the generic section-ending vocabulary (`_SECTION_WORDS_RE`). A title-cased content line inside a Requirements list, e.g. "Own The Full Platform Responsibility Here" (matches `responsibilit\w*`), read as a heading, ended the section, and dropped every later requirement line. Confirmed at baseline: the repro block gave `must = [Go, Kafka, Redis, gRPC, PostgreSQL]`; Docker, Terraform and English were lost.

**Fix (the ruling), `skills/job-hunting/scripts/ats_check.py:357-360` in `_heading()`:** the combined condition is split in two.
- `n <= 4 and (_section_kind(words) or _SECTION_WORDS_RE.search(words))` — rule (b), unchanged in effect.
- `n <= 8 and _section_kind(words) and _is_title_cased(words)` — rule (c), now requirement/nice-to-have vocabulary only.
Rule (a) (colon, ≤ 8 words), the uppercase-start and mid-line-punctuation guards, `#`/bold/inline headings, `_is_title_cased`, stopwords and the extractor are untouched. The docstring (`ats_check.py:327-336`) states the rule and the trade-off.

After the fix the repro block gives `must = [Go, Kafka, Redis, gRPC, PostgreSQL, Full Platform Responsibility, Docker, Terraform, infra, English fluency]`. "English fluency required" yields the two-word run "English fluency" (fluency is not a stopword), so the test asserts English by prefix rather than changing the extractor.

**Tests added (`tests/test_ats_check.py:318-335`):**
- `test_extract_keywords_title_case_content_line_keeps_section_open`: the repro block verbatim; Go, Kafka, Redis, gRPC, PostgreSQL, Docker, Terraform in `must`, plus a keyword starting with "English".
- `test_extract_keywords_long_title_case_line_never_ends_section`, 2 cases after `SECTION_LEAD` (5 keywords, so the tech-token merge cannot mask a truncated section): "Why You Will Love Working Here" (the requested negative; it matches no section word, so it was already content) and "About Our Company And Culture Here" (matches `about`, `company`, `culture`; a heading before the fix). Both keep English, Docker and Terraform. The docstring records the trade-off: a long title-cased section heading without a colon now runs on into the requirements list.

**Still passing (guards from rounds 2–3):** "What Essential Skills You Will Need" and "Skills and Experience We Are Looking For" open the section alone and after a ≥ 5-keyword Requirements block; "Strong Python skills preferred for this role" stays content; "Nice To Have Skills" switches to `nice`; "Additional Information", "Life at Grab", "What we offer" and the 7-word colon line still end a section; the five round-2 sentence-case lines stay content. Spot-checked by hand: "REQUIREMENTS" and "About The Company" still read as headings.

**Real postings:** keyword groups for the sample JD and the recorded EA (JobStreet), Grab (LinkedIn) and MCF postings are identical to rounds 1–3 (rendered with `sources.*.parse_detail` → `fetch_posting.render_posting`, diffed before/after). Expected consequence in the Grab posting: "About Grab and Our Workplace", "Get to Know the Team", "Get to Know the Role" and "What We Stand For At Grab" no longer read as headings (5–6 title-cased words with only generic vocabulary). None sits inside a requirement section, so nothing changes; "Qualifications" and "What Essential Skills You Will Need" still open it and "Additional Information"/"Life at Grab" still close it.

**Commands and output:**
```
python3 -m pytest -q tests/test_ats_check.py      # before fix: 2 failed, 83 passed
python3 -m pytest -q tests/test_ats_check.py      # after fix:  85 passed in 0.23s
python3 -m pytest -q -m "not network"             # 403 passed in 0.98s
python3 build.py --check                          # OK: 12 skills pass checks
```

**Trade-off (documented):** a 5–8-word title-cased section heading with no colon and only generic vocabulary (e.g. a posting whose "Why You Will Love Working Here" or "About Our Company And Culture" follows the requirements list) no longer ends the section, so that section's prose can add noise keywords. A colon, a `#`/bold marker, or a ≤ 4-word heading still ends it.
