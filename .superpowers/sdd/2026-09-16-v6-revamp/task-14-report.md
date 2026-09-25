# Task 14 report: build_resume.py and the five HTML templates

Status: DONE
Commit: 4ee02cc `build_resume.py: markdown → ATS docx (stdlib), five HTML templates → PDF, JSON Resume export` (base c91126b; trailer `Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>`)
10 files, +1962 lines.

## What was built

### `skills/job-hunting/scripts/build_resume.py` (stdlib core)
- **CLI:** `build_resume.py <md> --docx [--pdf --template <name>] [--html] [--json] [--photo PATH] [--out DIR]`. You can combine output flags in one run. Outputs go next to the input with the same stem, or into `--out DIR` (created if missing). Each written path is printed on stdout.
  - Exit 0 on success, including "PDF skipped".
  - Exit 2, with a plain one-line message and no traceback, for: no output flag (argparse `error`), an unknown template (argparse `choices`), a missing or unreadable input, no `# Name` line, a missing photo or unsupported photo type, or a write failure.
- **`parse_resume(md) -> dict`:** returns `{name, headline, contact[], sections[{title, entries[{heading, meta, org_loc, dates, bullets[], lines[], groups[], labeled}]}]}`.
  - The `###` line is split on ` — ` into heading and meta. The last ` · ` part is taken as dates when it contains a date. Fallbacks cover heading lines without an em dash and profile-style `— KL — 03/2023–present`.
  - Contact items are classified as email (`@`), url (http/https/www, or linkedin.com/github.com without a scheme), phone (≥7 digits from `+ digits space ( ) - .`), or text. The first text item is the headline and the rest stay in `contact`.
  - Template B: `## Core skills & proof` bullets `- **Label:** text` become entries with `labeled=True`.
  - In a Skills section, `**Label:** a, b · **Label2:** c` lines and bullets become `groups` (commas inside parentheses do not split). A plain `- Go, C#, AWS` bullet becomes an unlabelled group. Prose stays as bullets or labelled entries (the `_is_list` rule: every item has ≤5 words).
  - Summary-type sections join wrapped lines into paragraphs. An indented line continues the previous bullet.
  - Unknown `##` sections pass through as generic sections.
  - With no `# Name`, it raises `ValueError`.
- **`split_dates(text)`:** returns `(start, end)` as `YYYY-MM` or `YYYY`. It accepts en dash, em dash, ` - `, `to`, bare `2019-2021`, `M/YYYY` and `Jan 2020`. `end` is None for Present/Current/Now or a single date.
- **`docx_bytes(resume) -> bytes`:** built with `zipfile` and XML strings.
  - Parts: `[Content_Types].xml` (an Override for every part), `_rels/.rels`, `word/_rels/document.xml.rels` (styles, numbering, settings), `word/document.xml`, `styles.xml`, `numbering.xml`, `settings.xml` (compat mode 15), `docProps/core.xml` (`dc:title` = name) and `docProps/app.xml`.
  - Styles: Title 20pt bold, Subtitle 12pt, Heading1 13pt bold with a bottom-border `pBdr`, Heading2 11pt bold with a right tab at 9638 twips, Normal 10.5pt Calibri.
  - Page: A4 with 20 mm (1134-twip) margins. Dates sit after a `<w:tab/>` against the right tab stop, on job lines and on `Degree — School — 2021` lines.
  - Bullets use a `numbering.xml` abstractNum with `numFmt bullet` and Symbol U+F0B7, so no literal `•`.
  - There are no tables, drawings, headers or footers.
  - All text is escaped for `& < > " '`, and characters XML cannot hold are removed. The child-element order in pPr, rPr and style follows the OOXML schema sequence.
- **`html_str(resume, template_name, photo=None) -> str`:** fills `{{name}} {{headline}} {{contact_html}} {{sections_html}} {{sidebar_html}} {{photo_html}}` in a single `re.sub` over the template, so resume text is never rescanned for placeholders.
  - For the two sidebar templates, sections whose title matches skill/certif/languag (but not proof/educat/experien) go to `sidebar_html`. Every other section goes to `sections_html`.
  - All text is HTML-escaped, and links are limited to http/https/mailto/tel.
  - With `--photo`, the photo is embedded as a base64 data-URI `<img>`. Without it, nothing is emitted.
- **`render_pdf(html, out)`:** tries `playwright.sync_api` Chromium, then `cloakbrowser.launch(headless=True, stealth_args=False)`, which falls back to the literal `launch(headless=True)` on a TypeError. It calls `page.pdf(format="A4", print_background=True, prefer_css_page_size=True)` and always closes the browser in a `finally`. If both backends fail, the CLI writes the `.html` and prints the brief's exact "PDF skipped: …" line, then exits 0.
- **`json_resume(resume) -> dict`:** JSON Resume v1.
  - `basics{name, label, email, phone, url, summary, location{city}, profiles[{network, username, url}]}`.
  - `work[]{name, position, location, startDate, endDate, summary, highlights}`. `endDate` is omitted for Present.
  - `education[]{institution, area, endDate}`.
  - `skills[]{name, keywords}`.
  - `certificates[]`, `languages[]` and `projects[]` are added when those sections exist.

### `skills/job-hunting/scripts/_common.py`
- `docx_text(data: bytes) -> str` reads `word/document.xml` and returns one line per paragraph. `w:t` becomes text, `w:tab` a tab and `w:br` a newline, and only runs are read, so tab-stop definitions are not picked up as text. Paragraphs with `w:numPr` are prefixed `- `. Input that is not a .docx raises `ValueError`. Task 15 can reuse it as is.

### `skills/job-hunting/assets/templates/*.html`
Each template is a full document with embedded CSS only: no external fonts, CDNs or scripts. Each has `@page { size: A4; margin: 14mm }`, one `--accent` variable, body 10pt with line-height 1.45, secondary text at 9pt (the 9pt floor rather than 0.875×), semibold 600, and one spacing rhythm (gap and 2× gap).

| Template | Structure / signature |
|---|---|
| chicago | Single column. Centred serif masthead (Charter → Georgia). Navy uppercase headings (12.5pt) with 1pt rules. Inline comma skills. Muted navy used only for structure. |
| executive | Single column with an extra ~9 mm of side whitespace. Baskerville name at 23pt (1.84× the 12.5pt heading), left-aligned, with contact stacked on the right. 0.5pt hairline under the masthead and trailing each heading. En-dash bullets. Company in italic on its own line. Near-monochrome #3b3b3b. |
| corporate-sidebar | Full-width masthead with a 2pt accent rule, then `grid-template-columns: 30% 70%`. The light-tint sidebar (`color-mix` of the accent) holds Contact, Skills, Certifications and Languages. The tint is a fixed strip, so it runs the full height of every page. |
| accent-band | Single column under a solid teal band with name, title and contact reversed out. Section headings have a 3pt left bar. Skills are subtle pills. |
| creative-sidebar | Saturated violet 33% sidebar (fixed strip, full height on every page) holding the optional round headshot, the reversed name, contact, skill tags and languages. Main-column headings are violet with a short underline bar. |

`{{photo_html}}` is present in all five templates, in the top corner or sidebar top. The photo matrix says the user's preference wins, so a photo is not limited to creative-sidebar.

## Tests (TDD)
- Fixtures:
  - `tests/fixtures/resume-sample.md`: Template A, the fictional Arif Rahman from `sample-profile.md`, 2 roles, Summary, 2 skill groups, an Education line and a cert line. It contains "Go" and no "gRPC", so it suits Task 15's coverage test.
  - `tests/fixtures/resume-sample-b.md`: Template B, the fictional Mei Ling Tan, with Core skills & proof.
- RED: `python3 -m pytest -q tests/test_build_resume.py` gave `ERROR tests/test_build_resume.py … Interrupted: 1 error during collection` (`ModuleNotFoundError: No module named 'build_resume'`).
- GREEN: `tests/test_build_resume.py` has 27 test functions and 43 cases, all passing (0.25s).
- They cover:
  - parse: header, entries and dates, skill groups, Template B, missing name, edge cases (hyphen dates, wrapped bullet, `C#` in a heading, unlabelled skill bullet, unknown section)
  - `split_dates`: 7 parametrized cases
  - docx: package structure, XML well-formedness, overrides, rels, core title, no `w:tbl` or `•`, numPr
  - docx: styles, right tab at 9638, A4 margins
  - `docx_text`: every bullet and the reading order
  - XML escaping of `& < " '` in a bullet and in the name
  - `docx_text` rejects non-docx input
  - HTML: all 5 templates (doctype, name, first bullet, no leftover `{{`, no `<img>`, escaping, `@page`/`--accent`, no external CSS/JS/fonts)
  - HTML: sidebar split for all 5, HTML escaping, photo only when given, unknown template
  - HTML: Template B labelled entries
  - JSON Resume for A and B (dates `YYYY-MM`, no endDate for Present, profiles, education/certificates split)
  - CLI: writes next to the input, `--out`, the PDF-skipped path, bad args exit 2, missing name or missing file exit 2 with no traceback (subprocess), missing photo exit 2
  - The PDF backend order and browser close, using fake playwright/cloakbrowser modules, so no real browser runs in the unit suite (rules/tests.md §5).
- Full suite: `python3 -m pytest -q -m "not network"` gives **318 passed** (275 + 43). `python3 build.py --check` gives `OK: 12 skills pass checks`.

## Visual check (pdftoppm -r 60, each image viewed)
All five sample PDFs are **1 A4 page** with body text at 10pt. PNGs are in `/private/tmp/claude-501/-Users-snapdec-Documents-workspace-job-hunter/0d5f8b22-1b34-4996-b710-009b7d784d94/scratchpad/templates/`:
- `chicago.png`: centred serif masthead, navy uppercase headings with 1pt rules, single column, dates flush right.
- `executive.png`: large Baskerville name on the left and stacked contact on the right, hairline rules trailing tracked headings, en-dash bullets, italic company line, wide side whitespace.
- `corporate-sidebar.png`: full-width masthead with an accent rule, and a light-blue 30% sidebar (Contact, Skills) running to the page foot beside a 70% main column (Summary, Experience, Education).
- `accent-band.png`: solid teal header band with name, title and contact reversed, left-bar headings, and skills as pale pills.
- `creative-sidebar.png`: full-height saturated violet sidebar (name, contact, skill chips) and a white main column with violet headings and underline bars.
- `docx-master-quicklook.png`: the .docx rendered by macOS Quick Look (Apple's own docx importer). It opens, shows Title/heading styles, heading rules and real list bullets. Calibri is replaced by Times here, and this importer ignores custom tab stops.
- `variants/photo-chicago-1.png`, `photo-accent-band-1.png`, `photo-creative-sidebar-1.png`: `--photo` in the top-right corner, in the band, and at the top of the sidebar. Nothing overlaps.
- `variants/templateB-corporate-sidebar-1.png`, `templateB-accent-band-1.png`: Template B with bold-label proof bullets.
- `variants/long-{corporate-sidebar,creative-sidebar,executive}-{1,2}.png`: a 6-role resume flowing to page 2. The tint and strip continue on page 2, and entry heads are not split across pages. Nothing is auto-shrunk.

Fixes made after looking:
1. The chicago and accent-band contact lines broke inside URLs and the phone number, and the chicago contact line ran under the photo. The contact list is now `flex-wrap` and wraps only between items. Chicago reserves side padding only when a photo is present (`header:has(.photo)`).
2. In the sidebar templates the company wrapped beside the dates in the narrow main column. It now sits on its own line.
3. On page 2 an entry's company line was split from its title. Fixed with `.entry-head { break-inside: avoid; break-after: avoid }`.
4. accent-band used `system-ui` (SF variable font), which embedded as Type 3 fonts. It now uses a Helvetica Neue / Segoe UI / Roboto / Arial stack, which embeds as CID TrueType.
5. pdftotext split the letter-spaced and small-caps headings ("S ummary", "S U M M A RY", "C O N TA C T"). Chicago now uses real uppercase instead of synthetic small-caps, and heading tracking is at most 0.08em. All headings now extract whole.

## Text-extraction check
- **.docx via `docx_text`:** `Arif Rahman` / `Backend Engineer` / contact line (`… | +60 12-345 6789 | arif.rahman@example.com | https://linkedin…`) / `Summary` / … / `Software Engineer — Moneta Pay, Kuala Lumpur<TAB>03/2023 – Present` / `- Cut payment webhook…` / … / `Skills` / `Languages: Go, Python, SQL` / … / `Education & Certifications` / `BSc Computer Science — Universiti Malaya<TAB>2021`. The name comes first and sections are in order. `textutil -convert txt` (an independent reader) gives the same text, with bullets recognized as list items.
- **PDFs via `pdftotext` (default mode):**
  - chicago, executive and accent-band: name first, then headline, contact, and sections in order; date lines follow their titles. No garbled characters (`~`, `→` and `–` survive).
  - corporate-sidebar and creative-sidebar: the name comes first, but pdftotext's physical-layout mode **interleaves the two columns** (for example, Summary text between contact lines). A wider gutter did not change this (tested with 40pt).
  - `pdftotext -raw` (content-stream order, which is also what pypdf returns) is clean for both: name, headline, Contact, Skills, then Summary, Experience and Education in order.

## Files changed
- A `skills/job-hunting/scripts/build_resume.py`
- M `skills/job-hunting/scripts/_common.py` (`docx_text`; imports io, zipfile, ElementTree)
- A `skills/job-hunting/assets/templates/{chicago,executive,corporate-sidebar,accent-band,creative-sidebar}.html`
- A `tests/test_build_resume.py`, `tests/fixtures/resume-sample.md`, `tests/fixtures/resume-sample-b.md`

## Self-review
- The binding decisions are met:
  - Template A and B parse, with skill groups and labelled proof entries.
  - Date split, contact classification, escaping, numbering bullets, right tab at the text edge, bottom-border headings, core.xml title, overrides and rels.
  - Templates have no external resources, `@page` A4/14mm and one accent variable. The sidebar split, and photo only with `--photo`.
  - PDF backend order with the browser always closed, and the skip line with exit 0.
  - Exit codes 0 and 2. Output next to the input or in `--out`. Stdlib core. `newline="\n"` and pathlib.
- Hooks flagged a `new_` prefix, now renamed `_create_entry`, and a test-budget note that cleared once the production code landed.
- Self-review fixes:
  - The heading regex had stripped a trailing `#` (`C#`).
  - The photo and template error messages were conflated.
  - The sidebar split now goes by index, not dict equality.
  - "Career Summary" is no longer lost from the JSON summary.
- Every render after the fixes is 1 page for the sample. No temporary file is left in the output directory.

## Concerns
1. **Playwright's Chromium does not launch here.** The installed package expects `chromium_headless_shell-1234`, but the cache has 1223. So every real render in this check went through the **cloakbrowser fallback**, and the playwright branch is covered only by the fake-module test. `playwright install chromium` would fix it; I did not change the environment.
2. **cloakbrowser hangs on `page.set_content`** (it times out even with `commit`). Both backends therefore load the page with `goto(file://…)` from a hidden temporary `.stem-XXXX.html` in the output directory, which is deleted in a `finally`. This is a small departure from `set_content`, and it still writes only inside the output directory.
3. **cloakbrowser is called with `stealth_args=False`**, falling back to the literal `launch(headless=True)`. In one stealth session out of about 20, the chicago PDF embedded Georgia instead of Charter, which looks like fingerprint font masking. I could not reproduce it in 15 further runs, so the evidence is thin. Turning spoofing off is harmless for printing.
4. **No full-bleed.** Chromium clips painting to the `@page` content box (tested with negative margins and fixed elements), so the accent band and the sidebars sit inside the binding 14 mm margin rather than reaching the paper edge.
5. **Two-column PDFs in pdftotext's default mode interleave columns.** Task 15's `ats_check.py` should prefer pypdf or `pdftotext -raw` (content order), or treat sidebar PDFs as the known two-column ATS risk. The ATS master is the single-column .docx.
6. **Not opened in Word, Google Docs or LibreOffice**, since none is available here. The evidence is: well-formed parts, schema-ordered elements, and Apple's importer (textutil and Quick Look) opening the file with styles and list bullets. That importer ignores custom tab stops, so right-aligned dates were not seen rendered. Word honours `w:tab w:val="right"`.
7. **`docx_text` prefixes list paragraphs with `- `.** Task 15's first-bullet lint can rely on this.
8. **JSON Resume choices:**
   - Template B proof entries become `skills[]{name: label, keywords: [proof sentence]}`: no text is lost, but keywords holds a sentence.
   - In a combined Education & Certifications section, education and certificates are split by a degree-keyword regex.
   - `location.city` is the text before the first comma, so the country is dropped.
   - Unknown sections other than projects and languages are not exported to JSON; they still render in the docx and HTML.
9. **Visual nit:** in chicago and accent-band, a wrapped contact line starts with its separator (`·` or `|`).
