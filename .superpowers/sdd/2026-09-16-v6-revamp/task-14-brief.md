### Task 14: `build_resume.py` (markdown → docx / html / pdf / JSON Resume)

**Files:**
- Create: `skills/job-hunting/scripts/build_resume.py`, `skills/job-hunting/assets/templates/{chicago,executive,corporate-sidebar,accent-band,creative-sidebar}.html`
- Test: `tests/test_build_resume.py`, fixture `tests/fixtures/resume-sample.md`

**Resume markdown contract (parse this exactly; it is today's Template A):**
```
# Full Name
Title · City, Country · phone · email · https://linkedin.com/in/x · https://github.com/x
## Summary
text lines
## Experience
### Job title — Company, City · 01/2022 – Present
- bullet
## Skills
**Languages:** Go, Python · **Cloud:** AWS
## Education & Certifications
Degree — Institution — Year
```
`parse_resume(md) -> dict`: `{"name", "headline", "contact": [str], "sections": [{"title", "entries": [{"heading", "meta", "bullets": [str], "lines": [str]}]}]}` where an `###` line splits on ` — ` into `heading` (title) and the remainder; ` · ` in the remainder splits `org_loc` and `dates`.

**Outputs:**
- `--docx`: stdlib writer — build `[Content_Types].xml`, `_rels/.rels`, `word/document.xml`, `word/styles.xml`, `word/numbering.xml` with `zipfile`. Single column, styles: Title (name 20pt bold), Heading1 (section 13pt bold, bottom border), Heading2 (job title 11pt bold), Normal 10.5pt Calibri, bullets via numbering definition (no literal `•`), dates right-aligned via a right tab stop. No tables, no headers/footers, no images. Function `docx_bytes(resume: dict) -> bytes`.
- `--html [--template NAME]` (default `chicago`): load `assets/templates/NAME.html`, substitute `{{name}}`, `{{headline}}`, `{{contact_html}}`, `{{sections_html}}`, `{{sidebar_html}}` (skills/certs/languages sections for sidebar templates; empty otherwise), `{{photo_html}}` (`<img>` only when `--photo PATH` given). Function `html_str(resume, template_name, photo=None) -> str`.
- `--pdf`: render the HTML with `playwright` (or `cloakbrowser.launch`) → `page.pdf(format="A4", print_background=True)`; if neither is importable, write the `.html` and print `"PDF skipped: pip install playwright && playwright install chromium (or open the .html and print to PDF)"`, exit 0.
- `--json`: JSON Resume v1 (`basics{name,label,email,phone,location{city},profiles[]}`, `work[]{name,position,startDate,endDate,highlights[]}`, `skills[]{name,keywords[]}`, `education[]{institution,area,endDate}`). Function `json_resume(resume) -> dict`.
- Output paths: next to the input file, same stem; `--out DIR` overrides.

**Templates:** each is a full HTML document with embedded CSS following `resume-revamp.md` typography (body 10pt, headings ~14pt, name ≈ 1.5× heading (1.85× executive), line-height 1.45, one accent color as a CSS variable, `@page { size: A4; margin: 14mm }`). Structural differences per gallery table: chicago single column rules; executive generous margins hairlines; corporate-sidebar 30% tinted left sidebar (`grid-template-columns: 30% 70%`); accent-band full-width solid header band with reversed name; creative-sidebar saturated sidebar with `{{photo_html}}` slot.

- [ ] **Step 1: Tests** — `parse_resume` on the fixture (name, 2 experience entries, dates split); `docx_bytes` output opens with `zipfile`, contains `word/document.xml` with the name and no `<w:tbl>`; extracted text (reuse `ats_check.extract_docx_text` from Task 15 — so implement that helper inside `_common.py` as `docx_text(bytes) -> str` now) contains every bullet; `html_str` for each of the five templates contains the name and the first bullet and `<!doctype html>`; `json_resume` has `basics.name` and `len(work)==2`.
- [ ] **Step 2: Implement; run; commit** — `build_resume.py: markdown → ATS docx (stdlib), five HTML templates → PDF, JSON Resume export`.

