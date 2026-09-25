# Task 13 report — jd-match / resume-builder extensions, feature-guide fold, pointer edits

Status: DONE
Commit: f570be0 `jd-match knockouts + legitimacy cap; builder claims audit, anti-slop and 6-second gates; references re-pointed` (base 1589f80, trailer `Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>`)
13 files, +301 / −147.

## Edits per file (line refs are post-commit)

### references/jd-match.md
- L5–6: the order line (fetch → extract → knockout → score with legitimacy → optimize → record).
- L8–18 **§0 Fetch**: workspace `fetch_posting.py <url> --save`, then read `postings/<slug>.md`; pasted text via `fetch_posting.py --stdin --company "<X>" --title "<role>" --save [--url]`; exit 3 → `sourcing.md` §1 rung 4. Chat mode: pasted text; never claim a URL was read.
- L30–33 §1: new "Who advertised and when" bullet; the Red flags bullet now points to the §2 legitimacy block + `sourcing.md` §5. The "ghost-job/scam rules in SKILL.md" pointer is gone.
- L35–60 **§1.5 Knockout pre-check**: a table of 7 checks (work authorization, location/onsite, years (conservative sum, `strategy.md` §3 reach = hard, stretch = soft), licence/cert, notice (buyout makes it soft, `answer-bank.md` §4), salary floor, language), each with its profile source. A hard fail gives the verdict "skip (knockout: <check>)", reports any visible legitimacy flag, and stops: no score, no edits, no pipeline row. Soft fails go into §2's Constraint conflicts. One shot per company → `sourcing.md` §3 (soft).
- L78–82 §2: Constraint conflicts now takes the §1.5 soft fails. The verdict is applied "after the cap rule below".
- L84–102 **Legitimacy block** (a separate table, never averaged into Fit): ghost/scam → `sourcing.md` §5; repost age → `sourcing.md` §3 rule; salary reliability by advertiser is labelled practice, not data (employer posted band, agency figure indicative until the client and band are named → `networking.md` §6, no figure → `markets/<cc>.md` §3). **Cap rule**: any red flag caps the verdict at stretch and names the flag; a scam goes on to skip (`sourcing.md` §5).
- L115–120 **Literal-term mirror list**: the 8–12 exact Boolean terms, only ones the user has, copied verbatim into the resume and LinkedIn (`profile-optimizer.md` §2).
- L122–124: record now points to §5.
- L152–157 §4 step 4: "§10 table" becomes profile §9 "Soft skills development"; "Step 0 profile regeneration" becomes the closing step for the storage mode (SKILL.md).
- L162–174 **§5 Record**: workspace `tracker.py add --company "<X>" --role "<Y>" --stage saved --source <board or page> --url <url>` plus `--next/--due` (`pipeline.md` §2) and the verdict in `--notes`. Chat mode: a profile §9 Pipeline row. Skips are not recorded. Then the closing step.

### references/resume-builder.md
- L3–6: the honesty sentence now links `facts-policy.md`.
- L13–16 step 2: one grouped batch (SKILL.md memory rules). A missing number is asked, never estimated (`facts-policy.md` §2). This replaces the dead "SKILL.md Step 1.5" pointer.
- L17–21 step 3: once approved, workspace mode saves the draft as `resumes/<company>-<role>-vN.md` (letters go under `letters/`). This is the file that the gates and the build read.
- L22–25 steps 4 / 4.5 / 4.6: claims audit, anti-slop gate, 6-second lint (the lint is resume-only).
- L26–34 step 5: workspace `build_resume.py resumes/<file>.md --docx [--pdf --template <name>]`; chat mode uses the Anthropic docx/pdf skills.
- L35–36 step 6: `ats_check.py <file> --posting postings/<slug>.md`.
- L38–41 step 8 (new): `tracker.py set --company "<X>" --role "<Y>" --resume resumes/<company>-<role>-vN.md`. Chat mode fills the profile §9 Resume cell. Then the closing step.
- L43–45: binding gate order (claims audit → anti-slop → lint → file → ATS check). Chat mode says which checks ran by reading and which script checks could not run.
- L47–65 **Claims audit (step 4)**: runs `facts-policy.md` §4 and reports in that format. An open ask stops the flow. The existing reviewer-read bullets are kept, with a link to the mirror list.
- L67–80 **Anti-slop gate (4.5)**: a cover letter needs at least 1 user-supplied story (profile §5 / `answers.md` STAR stories / chat §9 Answers) and at least 1 company-specific fact (posting or dossier). Every draft gets `ats_check.py <draft.md> --slop`, and the list lives in `assets/slop-phrases.txt`. Chat mode reads the draft against the list instead.
- L82–97 **6-second lint (4.6)**: the six checks from the brief, with the Huntr/Careerflow skim citation (from research-notes). Runs `ats_check.py <draft.md> --lint`; single column and progression are checked by reading the layout.
- L99–123 ATS text-layer check: workspace `ats_check.py <file.docx|file.pdf> --posting postings/<slug>.md`, or `--keywords "a,b"` with the mirror list; chat uses the sandbox. L119–123 add the **declared fallback line** (a blockquote) that `ats_check.py` prints before exit 2. Task 15's brief says the script prints "the declared fallback line from resume-builder.md", so this line is its source.
- L129–136: estimates are written "~N" (`facts-policy.md` §3). Market norms now point to `markets/<cc>.md` §4. The stale "expected salary sometimes requested" line is removed because it contradicted `my.md` §4.
- L142–144 pre-delivery: estimates "~N"; new check that the audit, slop scan and lint ran (or were declared as reads).
- L151–158 **Versioning** (new): `resumes/<company>-<role>-vN.md`, never overwritten after sending. The pipeline Resume cell names the version that went out.
- L211–215 Cover letters: the flow now includes the claims audit and the anti-slop gate.

### references/resume-revamp.md
- L6–9: funnel diagnosis now points to `pipeline.md` §5; honesty sentence now links `facts-policy.md`.
- L42–43: builder flow is now claims audit, anti-slop and lint.
- L62–64: master built with `build_resume.py resumes/<file>.md --docx`.
- L87–93: gallery table gains a **File** column (`assets/templates/{chicago,executive,corporate-sidebar,accent-band,creative-sidebar}.html`).
- L112, L119–126: "python-docx" becomes ".docx". Presentation copy: `build_resume.py resumes/<file>.md --docx --pdf --template <name>` with the five names; "PDF skipped" → follow the printed line. Chat mode: fill the gallery file by hand and use the pdf skill.
- L160–169 Step 4: the re-score adds `ats_check.py <file> --lint` (chat mode: a read per builder 4.6), and shipping requires the lint to pass.

### references/rxresume-mcp.md
- L38–41: the input is the draft after its claims audit; links `facts-policy.md`.
- L47–52: `build_resume.py resumes/<file>.md --json` → `import_resume`. If the import rejects it, fall back to `create_resume` + `apply_resume_patch`.

### Deleted
- `references/feature-guide.md` (`git rm`). The help skill and the SKILL.md role table own the menu.

### Other files re-pointed (spec §4 lists them as "edited only to point at the new files")
- company-dossier.md L9, L30, L65–69
- interview-coach.md L8, L44–47, L50–51
- soft-skills-coach.md L4–5, L14–17, L37–41
- application-guide.md L28–29, L39–41, L85–87
- offer-coach.md L9, L16, L34–36, L65–66, L76, L88–95
- profile-optimizer.md L8, L10, L38–39, L43, L51–52, L61–65
- interview-prep.md L53–56, L121, L124–125
- README.md L42–44

## Pointer fixes

| Old | New | Where |
|---|---|---|
| "ghost-job/scam rules in SKILL.md" | legitimacy block + `sourcing.md` §5 | jd-match L32 |
| "scam rules in SKILL.md apply" | `sourcing.md` §5 | offer-coach L76 |
| "standard Step 0 closing" / "Step 0 profile regeneration" | closing step for the storage mode (SKILL.md) | jd-match §4, company-dossier, interview-coach, offer-coach, profile-optimizer, interview-prep |
| interview-coach "evidence bank (profile §10) … notes (§11)" | `answers.md` "STAR stories" (chat: profile §9 Answers) + profile §10 Notes | interview-coach L44–47 |
| profile-optimizer "§11" | profile §10 Notes | L61–62 |
| jd-match "§10 table for soft skills" | profile §9 "Soft skills development" | jd-match L155 |
| "profile's evidence bank" | `answers.md` STAR stories / chat §9 Answers | interview-prep L53; soft-skills-coach L37–40 |
| "profile's §9 Offers table" (workspace-blind) | `pipeline.md` `## Offers` (workspace) or profile §9 Offers (chat) | offer-coach L88–90 |
| "funnel diagnosis (SKILL.md)" | `pipeline.md` §5 | interview-prep L121, resume-revamp L6 |
| "Step 1.5 style" / "batch defined in SKILL.md Step 1.5" (SKILL.md no longer has a Step 1.5) | SKILL.md memory rules | company-dossier, interview-coach, soft-skills-coach, offer-coach, profile-optimizer, resume-builder |
| "the market notes" | `markets/<cc>.md` §3 / §5 / §7–§8 / §1 | company-dossier, offer-coach, profile-optimizer |
| JobStreet salary mechanics restated in profile-optimizer | `markets/<cc>.md` §5 | profile-optimizer L51–52 |
| "Application Guide, Market norms vary … expected salary sometimes requested" | `markets/<cc>.md` §4 | resume-builder L135–136 |
| README `references/feature-guide.md` | `/job-hunter:help` / SKILL.md role table | README L42 |

Honesty paragraphs → one sentence + `facts-policy.md` link: application-guide (the "estimate honestly" line and the Honesty section), resume-builder, interview-coach (§5), offer-coach (§6, including the Leverage bullet), profile-optimizer, soft-skills-coach, resume-revamp, rxresume-mcp. The guardrail itself stays in every file.

## Verification output

```
$ grep -rn "feature-guide\|sea-market-notes\|tech-role-map\|candidate-profile-template\|Step 0 closing" skills/
(empty)
$ grep -rn "SKILL.md's ghost\|scam rules in SKILL" skills/
(empty)
$ grep -rn 'Step 0 profile\|standard Step 0\|Step 1\.5\|evidence bank\|ghost-job/scam\|funnel diagnosis (SKILL\|the market notes' skills/
(empty)
$ grep -rn "feature-guide" . --exclude-dir=.git --exclude-dir=.superpowers --exclude-dir=docs
(empty — only docs/superpowers plan/spec history mention it)
$ python3 build.py --check
OK: 12 skills pass checks
$ python3 -m pytest -q -m "not network"
275 passed in 0.72s
```
No CR bytes in any edited file, and no XML tags added.

## Self-review

- **Script flags checked against the contracts and `--help`:** `fetch_posting.py <url> --save`, `--stdin --company --title --save --url` ✓. `tracker.py add --company --role --stage saved --source --url --next --due --notes` ✓. `tracker.py set --company --role --resume` and `set --company --note` ✓. `build_resume.py resumes/<file>.md --docx [--pdf --template <name>]`, `--docx`, `--docx --pdf --template <name>`, `--json` ✓. `ats_check.py <draft.md> --slop`, `<draft.md> --lint`, `<file> --lint`, `<file> --posting postings/<slug>.md`, `--keywords "a,b"` ✓. All use `python3 ${CLAUDE_SKILL_DIR}/scripts/…`. They match the resume and cover skills, which pass the same flags from `../job-hunting/scripts/`.
- **Restated rules:** the ghost/scam signals, the repost threshold, the claims-audit format, the "(est.)" / "~N" rule, the JobStreet salary mechanics and market resume norms are now pointers, not copies. New content that only these files own: the knockout table, salary reliability by advertiser (labelled practice), the cap rule, the mirror list, the gate order, the anti-slop gate, the 6-second lint, versioning and the fallback line.
- **Scenario N (Task 16):** the knockout row is named "Work authorization (pass / visa)", so the verdict reads "skip (knockout: work authorization …)". The repost flag is still reported, and no edits follow.

## Concerns

1. **Declared fallback line.** Task 15's brief says `ats_check.py` prints "the declared fallback line from `resume-builder.md`". I wrote that line (resume-builder L123, blockquote). Task 15 should copy it verbatim, or change both together.
2. **JSON Resume vs ResumeData.** rxresume-mcp step 3 already says `import_resume` takes Reactive Resume's own ResumeData JSON. `build_resume.py --json` emits JSON Resume v1, and whether `import_resume` accepts that format is unverified. I added a fallback: if the import is rejected, patch section by section.
3. **Lint scope.** Task 15's `lint_six_second` has no CLI flag for a target title and checks only one date. The builder therefore says the script "checks what the text can show", and that single column and progression are checked by reading. It does not promise per-item coverage.
4. **Beyond the brief's file list.** I also edited offer-coach, profile-optimizer and interview-prep, because the controller's decisions and spec §4 name them. I fixed the dead "Step 1.5" pointers across 6 files (SKILL.md no longer has that step), and re-pointed README L42 so nothing links feature-guide. Task 17 rewrites README anyway.
5. **Two choices I made in jd-match:** a skip verdict does not create a pipeline row, and the years knockout reuses `strategy.md` §3's reach/stretch reading instead of inventing a numeric threshold.

---

## Fix round 1/5 — commit c91126b `jd-match one-shot rule matches sourcing; builder and verb wording fixes`

9 files changed, +48 / −41. Trailer: `Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>`.

| # | Finding | Fix (post-commit line refs) |
|---|---|---|
| 1 (Important) | The one-shot soft fail fired on the posting's own `saved` row and weakened `sourcing.md` §3 | jd-match L59–63: ignore this posting's own row. Another row at the company at any stage past `saved` in the current cycle is a hard fail, "skip (knockout: one shot per company)". Another `saved` row is a soft note: pick one. |
| 2 | "no story and no fact" | resume-builder L74 and cover/SKILL.md L11 now read "no story or no fact". application-guide L39–40 is a one-line pointer to `resume-builder.md` step 4.5. |
| 3 | Lint citation | resume-builder L95–101: `ats_check.py <draft.md> --lint --target-title "<target role>"`. The text lists what the script checks: contact email and phone as literal text, a date near the top, a number in the first experience bullet, length, and title words in the first lines when `--target-title` is given. Single column, dates on every role and visible progression are checked by reading. |
| 4 | JSON Resume import | rxresume-mcp L50–54: says `import_resume` support for JSON Resume is unverified. Try it first; fall back to `create_resume` + `apply_resume_patch` section by section. |
| 5 | Verb order and save timing | match/SKILL.md L13: fetch → extract → knockout pre-check → score → legitimacy block → optimize → record. jd-match L5–6 is aligned to the same wording. resume/SKILL.md L12–13: the variant `resumes/<company>-<role>-vN.md` is saved on approval, before anything is built; step 4 only records it. |
| 6 | Dossier and revamp pointers | company-dossier L4–5: dropped the "search flow's quick company check" clause. L67: `tracker.py set --company "<X>" [--role "<Y>"] --note "…"`. resume-revamp L6–7 now points to a `pipeline.md` §5 targeting or screen leak with the resume as the likely cause. |
| 7 | jd-match restatements | L81: "every §1.5 soft fail". L96–100: the `networking.md` §6 citation is dropped (the agency figure stays indicative until the agency confirms the client's band), and the restated scam signal becomes a pointer to `sourcing.md` §5. L161–162: one sentence plus `facts-policy.md`. |
| 8 | Builder wording | resume-builder L18: "Never jump straight to a generated .docx/PDF". L43: "none that applies is skipped". |

Verification:
```
$ grep -rn "feature-guide\|sea-market-notes\|tech-role-map\|candidate-profile-template\|Step 0 closing" skills/
(empty)
$ grep -rn "SKILL.md's ghost\|scam rules in SKILL" skills/
(empty)
$ python3 build.py --check
OK: 12 skills pass checks
$ python3 -m pytest -q -m "not network"
275 passed in 0.53s
```
No CR bytes in any file.

Carried concern: Task 15 must add `--target-title` (per the controller's ruling) and print the declared fallback line from resume-builder L123 verbatim.
