### Task 13: Extend `jd-match.md`, `resume-builder.md`; fold `feature-guide.md`; pointer edits

**Files:**
- Modify: `references/jd-match.md`, `references/resume-builder.md`, `references/resume-revamp.md`, `references/company-dossier.md`, `references/interview-coach.md`, `references/soft-skills-coach.md`, `references/rxresume-mcp.md`, `references/application-guide.md`
- Delete: `references/feature-guide.md` (help skill owns the menu)

**jd-match.md additions:** §0 **Fetch**: if a URL is given in workspace mode run `fetch_posting.py <url> --save` and read the saved file. §1.5 **Knockout pre-check** before scoring: work pass/visa, location/onsite, years asked vs profile (conservative), licence/cert, notice ≤ X, salary floor, language — any hard fail → verdict "skip (knockout: …)" and stop; soft fails go to the report. §2 **Legitimacy block** separate from the fit score: ghost/scam heuristics from `sourcing.md`, salary-reliability by advertiser type, repost age; **cap rule**: any legitimacy red flag caps the verdict at "stretch" regardless of fit. §3 add **literal-term mirror list**: the 8–12 exact terms a recruiter's Boolean search would use, to appear verbatim in resume + LinkedIn. §5 **Record**: `tracker.py add --stage saved` with Source/URL; posting saved to `postings/`.

**resume-builder.md changes:** step 4 reviewer pass → **claims audit** per `facts-policy.md`; new step 4.5 **anti-slop gate** (cover letter requires ≥ 1 user-supplied story and ≥ 1 company-specific fact; run `ats_check.py --slop` on the draft text; banned openers list lives in `assets/slop-phrases.txt`); new step 4.6 **6-second lint** (title line matches target role; first bullet of latest role has a number; single column; every role has dates; progression visible; ≤ 2 pages) — `ats_check.py --lint`; step 5 file generation: workspace mode `build_resume.py resumes/<file>.md --docx [--pdf --template <name>]`; chat mode → Anthropic docx/pdf skills; step 6 `ats_check.py <file> --posting postings/<slug>.md`; **versioning**: tailored resume saved as `resumes/<company>-<role>-vN.md`, and `tracker.py set --resume <file>`.

**resume-revamp.md changes:** template gallery table gains a "File" column naming `assets/templates/<name>.html`; presentation copy built by `build_resume.py --pdf --template <name>`; re-score step runs `ats_check.py --lint` too.

**rxresume-mcp.md:** add "export JSON Resume with `build_resume.py <file>.md --json` and pass it to `import_resume`".

**Pointer edits** in the other files: replace "SKILL.md's ghost-job/scam rules" → `sourcing.md`; "profile §9/§10/§11" → `pipeline.md`/`contacts.md`/`answers.md` or chat-mode sections; "Step 0 closing" → "closing step per storage mode (SKILL.md)"; honesty paragraphs → one line linking `facts-policy.md`; `sea-market-notes.md` → `markets/<cc>.md`.

- [ ] **Step 1: Make the edits; delete feature-guide.md.**
- [ ] **Step 2: `grep -rn "feature-guide\|sea-market-notes\|tech-role-map\|candidate-profile-template\|Step 0 closing" skills/` → empty; `python3 build.py --check` OK. Commit** — `jd-match knockouts + legitimacy cap; builder claims audit, anti-slop and 6-second gates; references re-pointed`.

---

## Phase 4 — Writer scripts

