# SDD ledger — plan: docs/superpowers/plans/2026-09-16-v6-revamp.md

Spec: docs/superpowers/specs/2026-09-16-v6-revamp-design.md (approved 2026-09-16)
Branch: v6-revamp (in-place, from main @ 81143cc). Ruling: work in place on the feature branch instead of a separate worktree — repo is small, no other work in flight; cost if wrong: none beyond a stash.

## Pre-flight scan

| Pair / task | Produces vs consumes | Finding | Ruling |
|---|---|---|---|
| T2 build.py ↔ T5 SKILL.md | check_skill(desc ≤1024, name==dir) vs existing SKILL.md | v5.6.1 description already trimmed <1024; only job-hunting/ exists before T5 | none needed |
| T4 templates ↔ T7 read_criteria | profile-template labels vs parser label strings | parser keys on exact labels from old template | Ruling: T4 keeps §1–§3 labels verbatim from the old template — cost if wrong: read_criteria returns empty and search falls back to flags |
| T4 read_table ↔ T9 tracker | first table vs pipeline.md having two tables (pipeline, Offers) | first table = pipeline; Offers reachable via heading "## Offers" | none needed |
| T4 test env ↔ T3 Windows CI | subprocess env={"PATH": ""} | Windows python needs SYSTEMROOT; bare env breaks | Ruling: tests build env from os.environ + JOB_HUNT_DIR — cost if wrong: none |
| T5 verb skills ↔ T2 --link / plugin install | `${CLAUDE_SKILL_DIR}/../job-hunting/scripts` | resolves in repo, plugin copy, and symlinked install (siblings) | none needed |
| T6 html_to_text, T14 docx_text ↔ T4 _common | helpers added to _common by later tasks | additive | none needed |
| T10 inline `!tracker.py today` ↔ T9 tracker | non-zero exit aborts the skill | missing workspace must not be fatal | Ruling: tracker.py today/funnel print a one-line "no workspace — run workspace.py init" and exit 0 — cost if wrong: skill body runs without numbers |
| T13 deletes feature-guide ↔ T5 help skill | help skill owns the menu | help created in T5 before deletion | none needed |
| T16 test_live ↔ T6 search signature | search(keywords, location, country=) | consistent | none needed |
| T1 removes committed .skill | users download from Releases (T3/T17) | documented in README | none needed |
| Each task self-consistency | tests vs code vs files | T2–T4 carry full code; T5–T17 carry section lists; no contradictions found | — |

## Progress
Tasks 1–3 (batched): implemented cb77aac..d663084; review: 3 Important (CRLF check dead via read_text; line count off-by-one; --link rmtree outside workspace), minors deferred.
Ruling: `--link` writing to ~/.claude/skills is the spec-sanctioned exception to "never write outside the workspace" (spec §2 names it); keep it but refuse to replace a real non-symlink directory unless `--force` — cost if wrong: a dev has to pass one flag.
Tasks 1–3: minor (deferred): zip create_system byte differs across OS (comment only); --check treats every skills/ dir as a skill; OK-count message cosmetic; link_skills untested; ci.yml lacks permissions block (fix in this round anyway); duplicate inline `import shutil`.
Tasks 1–3: fix round 1/5 (3 addressed, 1 new open — link test asserts symlink on windows-latest; commits d663084..9c7c9f6)
Tasks 1–3: fix round 2/5 (1 addressed, 0 open; commits 9c7c9f6..bfef953)
Task 1: complete (commits 81143cc..bfef953, review clean)
Task 2: complete (commits 81143cc..bfef953, review clean)
Task 3: complete (commits 81143cc..bfef953, review clean)
Task 4: implemented bfef953..b037ef9; review: 1 Critical (heading scope unbounded → clobbers next table), 2 Important (escaped-pipe round-trip asymmetric; http_* untested). Minors deferred: unused `json` import in workspace.py (plan-mandated); heading must include `#` prefix (docstring).
Task 4: fix round 1/5 (3 addressed per implementer, re-review pending; commits b037ef9..50ddffe)
Task 4: fix round 1/5 (3 addressed, 0 open; commits b037ef9..50ddffe)
Task 4: complete (commits bfef953..50ddffe, review clean)
Task 5: implemented 50ddffe..23b3f7a; review: 4 Important (help/menu unreachable in chat mode; achievement-elicitation technique dropped; network verb points tracker.py add/set at contacts.md; cover verb runs ats_check on .md).
Ruling: ats_check.py accepts .md/.txt input — plan Task 15 already specifies `<file.docx|file.pdf|file.md>`; no change to the cover verb — cost if wrong: none.
Ruling: contacts writes get a real command — Task 9 adds `tracker.py contact --name X [--company C --role R --relationship REL --target T --last-touch D --next-touch D --status S --note N]` (upsert by Name+Company); network verb cites it — cost if wrong: one extra subcommand.
Task 5: minor (deferred): "revamp my resume"/"job title" dropped from description; ATS gate dropped from reader-chain principle; today→search passes a raw flag as $ARGUMENTS; profile-optimizer listed under two roles; mixed-mode offer and "don't rely on Project Memory" rules dropped; Script column bare paths.
Task 5: fix round 1/5 — first implementer (fork) died on a 429 before committing; re-dispatched to a fresh sonnet implementer with the same findings (2026-09-22)
PAUSED 2026-09-22: user asked to pause; Task 5 fix-round implementer stopped before committing. Resume at: Task 5 fix round 1 (findings in the entry above), then Task 6.
RESUMED 2026-09-22: user asked to continue through Task 10, then pause.
Task 5: fix round 1/5 (4+4 addressed, 1 new open — network step 1 and Networker row dropped `tracker.py contacts`; commits 23b3f7a..7e60a53)
Task 5: fix round 2/5 (1 addressed, 0 open; commits 7e60a53..84b180c)
Task 5: complete (commits 50ddffe..84b180c, review clean)
Task 6: implemented 84b180c..a975e67 (71 tests green); review pending. Implementer concerns: Hiredly detail unverified; MCF ignores location/days, Hiredly ignores pages/days (aggregator must not assume); LAST_WARNINGS is module state.
Ruling: this Mac's python.org Python has no CA bundle (urllib HTTPS → CERTIFICATE_VERIFY_FAILED) but `certifi` is installed — Task 7 adds `_common._ssl_context()` using `certifi.where()` when importable, else the default context, and documents "Install Certificates.command" in the README (Task 17). Never fall back to unverified TLS. Cost if wrong: live search fails on machines with neither, with a clear message.
Task 6: review Approved with 4 Important (parse_search not list-guarded + transport OSError escapes → search() can raise; byte-identical parse_salary/_loads/detail-epilogue across modules; LinkedIn 2.5 s delay gated on fetch is None; mode mappings untested). Minors deferred: LinkedIn regexes depend on attribute order/bare <li>; _DETAIL_URL_RE takes first /jobs/view/; detail() never clears LAST_WARNINGS (folded into fix round); inconsistent country validation; indeed._MISSING blanks literal "None"; _TAG_RE vs comments; loose lists.
Ruling: the certifi TLS fix moves from Task 7 into this fix round (it is a _common change and the same implementer found it) — cost if wrong: none.
Task 6: fix round 1/5 (6 addressed per implementer, re-review pending; commits a975e67..77d93a4)
Task 6: fix round 1/5 (5 addressed, 1 partially open — mcf._teaser positionLevels/employmentTypes not list-guarded; commits a975e67..77d93a4)
Task 6: fix round 2/5 (1 addressed, 0 open; commits 77d93a4..c8eb35d)
Task 6: complete (commits 84b180c..c8eb35d, review clean). Deferred minors carried: Hiredly detail unverified; LinkedIn regex attribute-order fragility; _DETAIL_URL_RE first-match; inconsistent country validation; indeed._MISSING literal strings; _TAG_RE vs comments.
Task 7: implemented c8eb35d..0379416 (150 tests, live smoke 93 postings); review pending. Implementer concerns: needs-a-look bucket large on broad queries; seen-jobs.json unbounded; per-keyword requests; exact-slug cross-board dedupe; country = earliest mention; dealbreaker tail-stripping heuristic.
Task 7: review Approved with 1 Important (_CATEGORY_TAILS strips "commission-only roles" → "commission", hard-dropping wanted postings). Minors deferred: negation-unaware dealbreaker match; NEEDS_LOOK_ROWS=10 cap invented; profile-template must-have wording contradicts soft semantics (fold in); knocked-out ids not written to seen (document); salary floor misses "RM9k" and per-year (fold in); empty board filter falls back to defaults; cosmetic counts; test gaps; 598-line file.
Task 7: fix round 1/5 (4 addressed per implementer, re-review pending; commits 0379416..69d6f10)
Task 7: fix round 1/5 (4 addressed, 0 open; commits 0379416..69d6f10)
Task 7: complete (commits c8eb35d..69d6f10, review clean)
Task 8: implemented 69d6f10..6f2b68c (212 tests green; live smokes: JobStreet id, MCF uuid, Greenhouse generic, Glassdoor 403 via CloakBrowser, Ashby JS-only page); review pending. Implementer concerns: board details carry no location/salary/posted (sources/ parse_detail only returns the 5 DETAIL_KEYS); generic title = page <title> and no company; MIN_GENERIC_TEXT/SETTLE_MS invented; brief trailer swapped for the harness attribution line (Opus 5).
Task 8: implemented 69d6f10..6f2b68c (212 tests; live smokes JobStreet/MCF/Greenhouse/Glassdoor→CloakBrowser/Ashby); review pending. Implementer concerns: detail() drops location/salary/posted; thin-page browser fallback + settle added beyond brief; generic path has no company; WRONG commit trailer (Opus) — must be amended to Fable 5.1 in the fix round.
Task 8: review Approved with 3 Important (<form> in _DROP_TAGS zeroes form-wrapped ATS pages; location/salary/posted dead on board path because DETAIL_KEYS is 5 keys; wrong commit trailer). Minors deferred: thin-page fallback fires on short valid postings; launch() has no timeout; redirect_stdout is Python-level only; bare-id ≥5-digit floor undocumented; last-resort fallback can leak <title>; dead unreachable raise.
Ruling: wiring location/salary_label/posted through DETAIL_KEYS + the four board parse_detail functions is done in this fix round (small, data already in payloads, jd-match reads the schema) — cost if wrong: a source-module change reviewed in a re-review rather than a task review.
Task 8: fix round 1/5 (3 Important + 4 minors addressed, 0 open; commit amended 69d6f10..e418dd5, 225 tests green). Carried: Greenhouse apply-form prose now included as the cost of keeping <form>; LinkedIn detail posted/salary selectors unproven on a live page; Hiredly detail still unverified.
Task 8: fix round 1/5 (7 addressed per implementer, commit amended 6f2b68c→e418dd5, re-review pending)
Task 8: fix round 1/5 (7 addressed, 0 open; amended commit e418dd5)
Task 8: complete (commits 69d6f10..e418dd5, review clean). Deferred: LinkedIn detail posted/salary unproven live; Hiredly detail unverified; Greenhouse EEO prose retained in generic extract.
Task 9: implemented e418dd5..9b698a8 (262 tests); review pending. Implementer notes: 'no reply' counts as a response under the literal rule; diagnose else-branch wording; interviews window excludes today; add --stage default-on-create fix.
Task 9: review Needs fixes — 3 Important (contact --name without --company duplicates rows; diagnose returns "too small" for healthy n≥10 funnels (plan-mandated); "no reply" notes count as responses). Minors deferred: interview-window note; validation before workspace check; Response % rounding vs threshold; no Offers-survives-add test; malformed dates invisible; Applied auto-filled on saved→cold.
Ruling: deviate from the brief's diagnose ladder — when sent ≥ 10 and no branch fires, return ("healthy", "No clear leak — hold the cadence: keep 10–20 targeted applications and 60/40 outreach per week") and reserve the n<10 string for sent < 10; pipeline.md (Task 10) must quote all five FIX strings verbatim — cost if wrong: one string.
Ruling: the reply rule excludes negated phrases ("no reply", "never replied", "no response") — cost if wrong: a rare response under-count.
Task 9: fix round 1/5 (6 addressed per implementer, re-review pending; commits 9b698a8..6e1e7e1)
Task 9: fix round 1/5 (6 addressed, 0 open; commits 9b698a8..6e1e7e1)
Task 9: complete (commits e418dd5..6e1e7e1, review clean)
Task 10: implemented 6e1e7e1..8fe5cc0; review pending
Task 10: review Needs fixes — 5 Important (sourcing.md lists "staleness" as a knockout reason the script never emits; Sources: line example malformed; invented "one request per second per board"; pipeline.md omits `tracker.py contacts`; unsourced/extrapolated statistics). Minors deferred: NOTHING_DUE wrapped across lines; Needs-a-look 10-row cap unmentioned; §1 also read by read_criteria; bare fetch_posting.py invocations; cap/outreach target has no profile field (strategy.md/Task 11 must add one); Gmail/Calendar combined line; 60/40 not restated in §6.
Ruling: "re-applying to the same company halves the rate" is a real Huntr Q1 2026 finding from the research (not in the spec) — keep it, cite Huntr; the "past 20/week halves" claim is replaced by Huntr's actual datapoints (11–20 apps → ~9% interview rate, 100+ → ~2.6%); median search quoted as 82–108 days (Huntr Q1/Q2 2026). Cost if wrong: a citation.
Ruling: the weekly cap and outreach target get a home in profile §8 as two labeled lines ("Weekly application cap:", "Weekly outreach target:") added to profile-template.md in Task 11 with strategy.md — cost if wrong: two template lines.
Task 10: fix round 1/5 (5 addressed per implementer, re-review pending; commits 8fe5cc0..8668a2f)
Task 10: fix round 1/5 (5+6 addressed, 0 open; commits 8fe5cc0..8668a2f)
Task 10: complete (commits 6e1e7e1..8668a2f, review clean)
PAUSED 2026-09-22 after Task 10 per user request. Resume at Task 11 (facts-policy, strategy, networking, answer-bank, post-offer; add "Weekly application cap:" / "Weekly outreach target:" lines to profile §8 per Task 10 ruling).
RESUMED 2026-09-25: user said continue (no stop point given — run to completion).
Ruling: commit trailer for all new commits is now `Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>` per the harness attribution update; earlier commits keep theirs — cost if wrong: trailer text only.
Task 11: dispatched (base 8668a2f) with research-notes.md as the only source of numbers
Task 11: implemented 8668a2f..a152c8d; review pending. Implementer concerns: ≤150-word cap vs Pin 150–199; chat-mode ### Answers section missing from template; target list lives on §2 Dream companies line; stale README/application-guide pointers (Tasks 13/17).
Task 11: review Needs fixes — 2 Important (post-offer.md §3 duplicates MY/SG notice floors instead of linking markets/*.md; sourcing.md:85-86 points agency etiquette at markets while networking.md §6 owns it).
Ruling: "(est.)" stays on internal records (profile, answers.md, audit table); outbound text (resume, cover letter, messages) writes "~N" or "about N", never a bare figure — facts-policy names the artefacts — cost if wrong: a label style.
Ruling: profile-template gains a chat-mode `### Answers` subsection under §9 and a `**Target list:**` line in §2, and SKILL.md's chat-mode sentence lists the Answers section — load-bearing for answer-bank/strategy — cost if wrong: two template lines.
Task 11: minor (deferred): bare § numbers ambiguous in strategy/answer-bank (fold in); ≤150 wording; networking day-gap wording and either/or asks (fold in); answer-bank field names vs template (fold in); facts-policy option (a); strategy hours/week unrecorded and cadence text duplicates pipeline.md §6; post-offer Status value.
Task 11: fix round 1/5 (10 addressed per implementer, re-review pending; commits a152c8d..07c8f52). Note: runway/burnout figures now appear in no file (pipeline.md §6 keeps runway-aware rules) — minor, deferred.
Task 11: fix round 1/5 (10 addressed, 0 open; commits a152c8d..07c8f52)
Task 11: complete (commits 8668a2f..07c8f52, review clean)
Task 12: dispatched (base 07c8f52) with the inbound-link promise list
Task 12: implemented 07c8f52..5fa80bc; review pending. Implementer concerns: CPF AW ceiling figure suspect; SG wage/hours/leave not in research-notes (points to mom.gov.sg); some labelled non-research items; README bullet re-pointed.
Ruling: CPF fact corrected (verified 2026-09-25 via web search, CPF Board + Vialto): OW ceiling S$8,000/month from 1 Jan 2026 (S$7,400 in 2025); annual salary ceiling S$102,000 unchanged; AW ceiling = S$102,000 − total OW subject to CPF for the year. The v5 "AW ceiling S$102,000 → S$110,800" line was wrong and must not survive anywhere — cost if wrong: none, it is sourced.
Ruling: README.md re-point kept (Task 17 rewrites README anyway) — cost if wrong: none.
Task 12: review Needs fixes — 2 Important (AW ceiling wrong at sg.md:97/132; CPF written as universal incl. a "CPF missing" red flag that misfires for EP holders).
Ruling: research-notes.md corrected by the controller (CPF eligibility + ceilings; WFA expected in force ~end-2027, <25 staff exempt initially, civil contraventions — HSF Kramer/Mayer Brown/Hawksford, verified 2026-09-25) — cost if wrong: none, sourced.
Task 12: minor (deferred unless folded): attributions naming bodies not verified (fold in: relabel "(2026-09 notes)"); SG has no general minimum wage (fold in); FCF "any role" overreach and "every posting" screening questions (fold in); SkillsFuture eligibility caveat (fold in); agency −18% duplicated in networking.md; interview-prep keeps MY law sentence; my.md "not to complain" vs EA s.69F; my.md §8 bonus contribution item; my.md table header vs EPF Act; interview-prep pointer omits _template.
Task 12: fix round 1/5 (10 addressed per implementer, re-review pending; commits 5fa80bc..1589f80). Six reviewer-supplied facts labelled '(2026-09 notes — verify)' — acceptable per sourcing policy.
Task 12: fix round 1/5 (10 addressed, 0 open; commits 5fa80bc..1589f80)
Task 12: complete (commits 07c8f52..1589f80, review clean). Deferred minors: my.md "EPF Act 1991" attribution unhedged; sg.md at 179/180 lines; agency −18% duplicated in networking.md; interview-prep keeps MY law sentence.
Task 13: dispatched (base 1589f80) with script contracts for build_resume/ats_check and the stale-pointer map
Task 13: implemented 1589f80..f570be0; review pending. Implementer concerns: resume-builder.md:123 fallback line must be printed verbatim by ats_check.py (Task 15); JSON Resume vs Reactive Resume import format unconfirmed (patch fallback added); --lint lacks a target-title flag.
Ruling: Task 15 adds `ats_check.py --target-title "<title>"` feeding lint_six_second(target_title=…) and prints the resume-builder.md fallback line verbatim on exit 2 — cost if wrong: one flag.
Task 13: review Needs fixes — 1 Important (jd-match one-shot-per-company soft fail fires on the posting's own saved row and weakens sourcing.md §3's "never apply twice").
Ruling: one-shot rule = ignore this posting's own row; another row at the company at stage applied or later this cycle → skip (knockout: one shot per company); another saved row → soft note — cost if wrong: none, it restores sourcing.md §3.
Task 13: fix round 1/5 (8 addressed per implementer, re-review pending; commits f570be0..c91126b)
Task 13: fix round 1/5 (8 addressed, 0 open; commits f570be0..c91126b)
Task 13: complete (commits 1589f80..c91126b, review clean)
Task 14: dispatched (base c91126b) with visual PDF check requirement
User 2026-09-25: pause once Task 14 is complete (after review).
Task 14: implemented c91126b..4ee02cc (318 tests; 5 templates rendered 1-page A4 via cloakbrowser, viewed); review pending. Implementer concerns: playwright Chromium build mismatch (needs playwright install chromium); cloakbrowser set_content hang → temp file load; stealth off; no edge-to-edge colour (14mm margin); pdftotext default mixes sidebar columns → Task 15 use -raw or pypdf; docx unrendered in Word; docx_text prefixes bullets with '- '.
Task 14: complete (commits c91126b..4ee02cc, review clean — Approved, no Critical/Important)
Task 14: minor (deferred, final review to triage — fix before merge recommended for 1, 2, 5): (1) hard-wrapped bullets outside Summary become entry lines rendered above bullets; (2) temp HTML created before try, unlink not OSError-guarded; (3) PDF backend failures swallowed, TypeError retry can mask errors; (4) _skill_groups all-or-nothing drops skills from JSON; (5) wrapped contact line starts with a separator (chicago, accent-band); (6) creative-sidebar weight 700, executive date alignment, empty Contact heading; (7) accent band not edge-to-edge under 14mm @page; (8) docx_text double-counts nested paragraphs; (9) stale test docstring, no _safe_href test, urlparse ValueError path; (10) build_resume.py 942 lines — docx writer/JSON Resume could split out.
Env note: playwright's Chromium build is stale on this Mac (run `playwright install chromium`); PDFs currently render through cloakbrowser.
PAUSED 2026-09-25 after Task 14 per user request. Resume at Task 15 (ats_check.py: add --target-title; print resume-builder.md:123 fallback verbatim; use pdftotext -raw or pypdf for column order; reuse _common.docx_text).
RESUMED 2026-09-25: user said continue — run Tasks 15–17 and the final review.
Task 15: dispatched (base 4ee02cc). Ruling: PDF extraction pypdf → pdftotext -raw (sidebar column order) → unavailable (exact fallback line, exit 2) — cost if wrong: extraction order only.
Task 15: implemented 4ee02cc..22575a4 (360 tests; e2e docx+sidebar PDF); review pending. Implementer concerns: PDF lint always fails first-bullet (no glyphs); sidebar PDF fails date-near-top (sidebar text first); sidebar wraps URLs across lines in the PDF text layer; "Go" matches "go"; keyword noise from prose; extras --text, present: line, empty-text notice.
Task 15: review Needs fixes — 5 Important (PDF lint false FAILs on first-bullet/date; keyword false passes Go/.NET/R/C/REST; extract_keywords collapses on unmarked requirement lines; step-6 invocation yields no contact/reading-order evidence; year range in parentheses read as a phone).
Ruling: PDF inputs (pypdf/pdftotext-raw) print `skip first-bullet: …` and `skip date: …` instead of FAIL; contact/length/title still run — cost if wrong: a PDF-only layout issue goes unflagged (the .md/.docx lint still catches it).
Ruling: keywords that are all-caps or have ≤2 letters match case-sensitively, and a leading "." keyword needs a non-word, non-dot left boundary — deviates from the bound "case-insensitive" — cost if wrong: "Rest API"-style false negatives, which only prompt using the posting's spelling.
Ruling: step 6 = `ats_check.py <file> --posting postings/<slug>.md --lint --text`; `--text` combines with checks; resume-builder.md and skills/resume/SKILL.md updated to match — cost if wrong: a longer report.
Task 15: fix round 1/5 (10 addressed per implementer, re-review pending; commits 22575a4..562d25e). Accepted trade-offs: ASP.NET ≠ .NET, GO ≠ Go.
Task 15: fix round 1/5 (10 addressed, 1 new open — expanded section vocabulary truncates unmarked requirement sections; commits 22575a4..562d25e)
Ruling: a plain unmarked line is a section heading only if it ends with ":" (≤8 words) or has ≤4 words and matches the section/requirement vocabulary — cost if wrong: a 5+-word section title without a colon is read as content.
User 2026-09-25: pause once Task 15 is complete (after review).
Task 15: fix round 2/5 (1 addressed per implementer, re-review pending; commits 562d25e..bee8338)
Task 15: fix round 2/5 (1 addressed, 1 new open — ≤4-word cap stops 5–8-word unmarked requirement headings like "What Essential Skills You Will Need" from opening the section; commits 562d25e..bee8338)
Ruling: add a heading-shape signal instead of a wider cap — an unmarked line of ≤8 words with no terminal punctuation is a heading when it is title-cased (≥2 words of 4+ letters, ≥75% of them capitalised) and matches requirement/nice/section vocabulary; sentence-case lines stay content. Keep colon (≤8) and ≤4-word rules. Keep the added generic stopwords — cost if wrong: an all-title-case requirement bullet is misread as a heading.
Task 15: fix round 3/5 (1 addressed per implementer, re-review pending; commits bee8338..530ecc7)
Task 15: fix round 3/5 (1 addressed, 1 new open — rule (c) also admits generic section-ending vocabulary, so a title-cased content line like "Own The Full Platform Responsibility Here" ends the section; commits bee8338..530ecc7)
Ruling: rule (c) applies only to requirement/nice-to-have vocabulary (lines that open or switch a requirements section); section-ending vocabulary needs rule (a) colon or rule (b) ≤4 words — cost if wrong: a 5–8-word title-cased non-requirement heading without a colon ("Why You Will Love Working Here") keeps the previous section open.
Task 15: fix round 4/5 (fresh fable implementer; 1 addressed per implementer, re-review pending; commits 530ecc7..2d8c074)
User 2026-09-25: after Task 15, build a handoff package (memory, SDD workspace, history, env) and push to GitHub so another device/account can resume. Do NOT start Task 16.
Task 15: fix round 4/5 (1 addressed, 0 open; commits 530ecc7..2d8c074)
Task 15: complete (commits 4ee02cc..2d8c074, review clean). Deferred minors: keyword code ~190 lines could split out; _EXPERIENCE_RE/_MD_HEADING_RE duplicated with build_resume.py; "English fluency" extracted as a run rather than "English"; tech vocab includes everyday words (Spring, Swift, Rust…).
HANDOFF 2026-09-25: user is moving to another device and Claude account. Handoff package in docs/handoff/ + this workspace force-added to git; branch v6-revamp pushed to origin. Resume at Task 16.
