# v6 revamp — from "coaching prose" to a working job hunter

Design spec, 2026-09-16. Status: **approved 2026-09-16** — all five phases;
Windows stays a supported build/run target; distribution via plugin
marketplace from this repo; default workspace `~/job-hunt`.

## 0. Why revamp

v5.6 is 2,300 lines of well-tested coaching prose and zero code. Every
deterministic job (search a board, fetch a posting, parse a tracker, build a
.docx, extract text for an ATS check, compute funnel numbers) is re-improvised
by the model each session. Research on 2026-09-16 (four parallel surveys:
GitHub landscape, live board-API tests, seeker/recruiter realities, commercial
product features) shows the gap between v5.6 and how a job hunt actually
works:

| Reality (evidence) | v5.6 today |
|---|---|
| Referrals convert ~40% to interview, recruiter-sourced ~25%, cold inbound ~3% (Ashby, 38M applications). | Application-centric; networking is 4 bullets and two LinkedIn search URLs. |
| Recruiters screen day-one applicants first; postings <48h old matter most. | One-shot `site:` web search; no freshness, no recurring sweep, no "seen" memory. |
| JobStreet MY/SG, MyCareersFuture SG and LinkedIn guest search all return JSON/HTML **without login** (tested live today). | Search is a lottery over web-search snippets. |
| Volume kills conversion: 11–20 apps → 9% interview rate, 100+ → 2.6% (Huntr, 140k apps). Median search 82–108 days. | No cadence, cap, or runway awareness. |
| ATS does not auto-reject on keywords; **knockout questions** do. Recruiter skim is 6–10 s on six data points. | "Keyword mirroring" advice; no knockout pre-check; no skim lint. |
| 54% of hiring managers view obvious AI cover letters negatively; specificity and defendable numbers still win. | Honesty guardrail (good) but no anti-slop gate. |
| 53% of seekers ghosted; 81% of recruiters admit ghost postings. | Ghost/scam flags exist; no auto-close or follow-up rules. |
| Every tracker product has due dates, stale detection, follow-up nudges, contacts CRM, resume versioning. | Static markdown table; no dates; no contacts; no versions. |
| Claude Code merged `.claude/commands/*.md` into skills (v2.1.101). | Nine deprecated-format command wrappers, deployed by copy scripts. |
| Committed `job-hunting.skill` was built on Windows (CRLF inside the zip) while source is LF. | Two build scripts (`build.sh`, `build.cmd`) producing different bytes; artifact committed to git. |

## 1. The model: nine roles a job hunter plays

The revamp is organized around what a job hunter *does*, not around
documents. Each role maps to a stage of one loop the user runs weekly.

| # | Role | Stage | v6 owner |
|---|---|---|---|
| 1 | Strategist | Position, target, cadence, runway | `SKILL.md` + `references/strategy.md` (absorbs positioning, tech-role-map → career map) |
| 2 | Scout | Source fresh openings continuously | `scripts/search_jobs.py`, `references/sourcing.md` |
| 3 | Qualifier | Knockout pre-check, legitimacy, fit, one-shot-per-company | `scripts/fetch_posting.py`, `references/jd-match.md` (extended) |
| 4 | Writer | Resume, cover letter, answer bank; anti-slop; ATS check | `scripts/build_resume.py`, `scripts/ats_check.py`, `references/resume-builder.md`, `resume-revamp.md`, `answer-bank.md` |
| 5 | Networker | Referral map before applying, 3-touch sequences, contacts | `references/networking.md` |
| 6 | Coach | Prep pack, mocks, dossier, soft skills | existing `interview-prep.md`, `interview-coach.md`, `company-dossier.md`, `soft-skills-coach.md` |
| 7 | Negotiator | Offers | existing `offer-coach.md` |
| 8 | Operations | Tracker with due dates, today view, weekly review, funnel diagnosis, ghosting rules, wellbeing | `scripts/tracker.py`, `references/pipeline.md` |
| 9 | Onboarder | Resignation/notice, references, 30-60-90 | `references/post-offer.md` (new; no product surveyed has it) |

## 2. Repository layout (after)

```
job-hunter/
├── .claude-plugin/
│   ├── plugin.json              # name: job-hunter
│   └── marketplace.json         # lets `claude plugin marketplace add` work from this repo
├── skills/
│   ├── job-hunting/             # THE skill (also zipped for claude.ai)
│   │   ├── SKILL.md             # router + memory rules + principles, <300 lines
│   │   ├── references/          # one file per role/flow (see §1, §4)
│   │   │   └── markets/         # my.md, sg.md, _template.md (split from sea-market-notes)
│   │   ├── scripts/             # python3, stdlib-only core; optional extras degrade
│   │   └── assets/              # profile template, pipeline template, resume HTML templates
│   ├── search/SKILL.md          # thin verb skills → /job-hunter:search etc.
│   ├── match/SKILL.md
│   ├── resume/SKILL.md
│   ├── cover/SKILL.md
│   ├── network/SKILL.md
│   ├── interview/SKILL.md
│   ├── company/SKILL.md
│   ├── offer/SKILL.md
│   ├── today/SKILL.md           # daily operations view (new)
│   ├── review/SKILL.md          # weekly funnel review (new)
│   └── help/SKILL.md
├── build.py                     # one cross-platform build: zip + optional local install
├── .github/workflows/ci.yml     # pytest on scripts; build zip; attach to release on tag
├── tests/                       # pytest for scripts (recorded fixtures) + behavioral scenarios
├── docs/                        # specs, PROJECT-DESCRIPTION.md (claude.ai custom instructions)
└── README.md
```

Removed: `build.sh`, `build.cmd`, `deploy-cc.sh`, `deploy-cc.cmd`,
`claude-code/commands/*`, committed `job-hunting.skill`, `NEXT-STEPS.md`.

### Build and install

- **Claude Code:** `claude plugin marketplace add <repo>` then
  `claude plugin install job-hunter@job-hunter`. Or for a local checkout:
  `python3 build.py --link` symlinks `skills/*` into `~/.claude/skills/`
  (symlinks are supported; edits are live, no redeploy step).
- **claude.ai:** `python3 build.py` writes `dist/job-hunting.skill`
  (LF-normalized, deterministic zip of `skills/job-hunting/`). Not
  committed; CI attaches it to a GitHub release on every `v*` tag.
- `build.cmd` answer: it existed only because the artifact was rebuilt on a
  Windows machine. With `build.py` (Python runs on both) and CI-built
  releases, no per-OS scripts are needed. If Windows is still in use,
  `python build.py` is the same command there.

## 3. Memory and storage

Two modes, one schema.

**Workspace mode (Claude Code).** A `job-hunt/` directory (default:
`~/job-hunt`, overridable by `JOB_HUNT_DIR` or a `job-hunt/` folder in the
current project) holds:

```
job-hunt/
├── profile.md        # facts about the person (§1–§8 of today's template); edited in place
├── pipeline.md       # applications tracker table (fixed columns, scripts read/write it)
├── contacts.md       # networking CRM table
├── answers.md        # screening-question answer bank
├── seen-jobs.json    # ids/urls already shown, with first-seen date (scripts only)
├── postings/         # saved JDs as markdown: <company>-<role>.md
├── resumes/          # master.md + per-application variants and generated files
├── letters/          # cover letters
├── dossiers/         # company briefs
└── reviews/          # weekly funnel reviews
```

Rule change: in workspace mode the skill **edits files in place** with tools
and never regenerates the whole profile as a chat block. Each session ends
with a one-line "saved: profile §3, pipeline +1 row" summary.

**Chat mode (claude.ai).** No filesystem between sessions, so
`candidate-profile.md` in Project knowledge stays the single document and
the existing "regenerate the full profile at the end" rule stays. The
pipeline, contacts, and answers tables live as sections of that file.
Scripts that need network cannot run in the claude.ai sandbox (package
sources only); the skill declares this and degrades to "paste the posting"
and web search.

Both modes share one schema; `assets/` ships templates for every file.

### Pipeline table schema (breaking change to §9)

| Company | Role | Source | Channel | Applied | Stage | Next action | Due | Last touch | Resume | Notes |

- `Source` = board/site the posting came from (JobStreet, MCF, LinkedIn,
  career page, agency) — needed for per-channel conversion.
- `Channel` = cold / referral / recruiter-inbound / agency.
- `Stage` ∈ saved · applied · screen · interview · final · offer · accepted ·
  rejected · withdrawn · cold (auto after 21 days silent).
- `Due` drives the today view; `Resume` names the variant file sent.

## 4. Reference documents (what changes)

| File | Change |
|---|---|
| `strategy.md` (new) | Positioning through-line; career map (adjacent roles from the profile with gap deltas — extends tech-role-map); cadence contract (weekly cap 10–20 targeted, one shot per company, batch-and-rest, 90-day expectation, runway-aware urgency); rejection reframing. |
| `sourcing.md` (new) | Fallback ladder: `search_jobs.py` → connected MCP (Reactive Resume, LinkedIn MCP, Workopia) → web search → paste. Freshness rule (<48h first). Company-career-page routing over Easy Apply. Agency list per market. Recurring digest via `/loop` or `/schedule`. Ghost/scam heuristics moved here from SKILL.md. |
| `jd-match.md` | Add **knockout pre-check** (visa/pass, location, years, licence, notice, salary floor) before scoring; separate **legitimacy block** from fit score with a cap rule (a red-flag posting cannot score above "stretch"); literal-term mirror list for recruiter Boolean search; record the posting to `postings/`. Upskill review unchanged. |
| `resume-builder.md` | Flow now calls `build_resume.py` (workspace) or the docx/pdf skills (chat); reviewer pass becomes a **claims audit** against `profile.md` (every number traceable or removed); **anti-slop gate**: no cover letter without one user-supplied story and one company-specific fact; banned-phrase lint; **6-second lint** (title alignment, metric in first bullet, single column, dates/progression). Versioning: every tailored resume is `resumes/<company>-<role>-vN.md` and named in the pipeline row. |
| `resume-revamp.md` | Keep scorecard and gallery; templates become real HTML/CSS files in `assets/templates/` rendered by `build_resume.py --pdf`; archetype check and photo matrix unchanged. |
| `answer-bank.md` (new) | The recurring screening set (salary expectation, notice, work pass/sponsorship, why us, why leaving, relocation, earliest start, years-in-tool, essay prompts) stored truthfully per market in `answers.md`, tailored per posting on request. The honest substitute for auto-apply. |
| `networking.md` (new) | Referral map per target company (alumni, ex-colleagues, 2nd-degree, recruiters) and the rule **ask for a referral before applying**; 3-touch sequence (comment → connect → 150-word message → follow-up at +5 days); reply-rate benchmarks; recruiter/agency etiquette (exclusivity, salary disclosure, counter-offers); Open-to-Work mode choice; contacts table with last/next touch. Absorbs the LinkedIn people-search links. |
| `pipeline.md` (new) | Tracker schema, stage rules, auto-cold after 21 days, follow-up cadence (+7 days polite nudge), today view, weekly review ritual, funnel diagnosis by leak stage (no views → targeting/ghosts; views no screens → resume; screens no onsite → interviewing; onsites no offers → close/negotiation), per-channel conversion vs benchmarks, wellbeing check. Replaces the funnel section of SKILL.md. |
| `post-offer.md` (new) | Resignation letter and notice handling (MY/SG norms, buyout, garden leave), counter-offer from current employer, reference prep (permission script, brief per referee), background-check readiness, 30-60-90 plan, probation-review prep. |
| `facts-policy.md` (new) | The no-fabrication **mechanism**: `profile.md` is the immutable facts source; ask a question rather than estimate; estimates labeled; reviewer audit lists every claim → source line. Referenced by every writing flow instead of repeating the guardrail paragraph. |
| `markets/my.md`, `markets/sg.md`, `markets/_template.md` | Split `sea-market-notes.md` + the Malaysia rights sheet; add 2026 updates found today (MY: EA notice floors, Gig Workers Act 2026, EPF for foreign workers; SG: Workplace Fairness Act phase-in, COMPASS 2026 changes, SkillsFuture Jobseeker Support, MCF 14-day ad rule). PH/ID/VN stay as a brief in `_template.md` examples. Salary sources per market (Hays, Robert Walters, Michael Page, NodeFlair, MCF salary field, JobStreet salary label). |
| `application-guide.md`, `interview-prep.md`, `interview-coach.md`, `company-dossier.md`, `offer-coach.md`, `profile-optimizer.md`, `soft-skills-coach.md`, `rxresume-mcp.md` | Kept; edited only to point at the new files, the storage modes, and the facts policy. `rxresume-mcp.md` gains a JSON-Resume export path from `build_resume.py --json`. |
| `feature-guide.md`, `tech-role-map.md`, `sea-market-notes.md` | Folded into `help/SKILL.md`, `strategy.md`, `markets/`. |

`SKILL.md` shrinks to: trigger description, memory/storage rules, the
nine-role loop as a router table, principles, and the closing step. Target
under 300 lines so it survives Claude Code's 5k-token per-skill cap.

## 5. Scripts

All Python 3.10+, stdlib-only core (`urllib`, `json`, `re`, `html.parser`,
`zipfile`), so they run on a bare Mac/Windows/Linux and in the claude.ai
sandbox when network is allowed. Optional extras are detected at runtime and
named in the output when missing.

| Script | Does | Optional extras |
|---|---|---|
| `search_jobs.py` | Reads criteria from `profile.md` §2/§3 (or flags); queries **JobStreet MY/SG v5** (verified: `/api/jobsearch/v5/search`, `siteKey=MY-Main`/`SG-Main`, salary/date/worktype filters), **MyCareersFuture** (`POST api.mycareersfuture.gov.sg/v2/search`, salary ranges, applicant counts), **LinkedIn guest** (HTML cards, ≤3 pages, 2–3 s sleep, graceful on 429); optional Indeed via `python-jobspy` and Hiredly SSR feed. Normalizes to one record (id, title, company, location, mode, salary min/max/currency, posted, source, url, teaser); dedupes against `seen-jobs.json`; applies must-have/dealbreaker/salary-floor knockouts; sorts by freshness; emits markdown table + JSON. Polite: ≤1 req/s, identified UA, few pages per query. | `python-jobspy` |
| `fetch_posting.py` | URL or id → clean markdown JD saved to `postings/`. JobStreet id → GraphQL `jobDetails` (verified today, `platform: WEB`, zone `asia-4`/`asia-5`); LinkedIn id → guest `jobPosting`; MCF uuid → `/v2/jobs/<uuid>` (includes screening questions); any other URL → readability extraction; **CloakBrowser fallback** (`from cloakbrowser import launch`) when installed and the page returns a bot challenge. | `cloakbrowser` |
| `tracker.py` | `add`, `set`, `today` (overdue/due follow-ups, stale >7 days, interviews within 7 days, auto-cold candidates), `funnel` (sent → response → interview → offer by channel and source vs benchmarks, leak stage, one recommended change), `digest` (markdown weekly review saved to `reviews/`), `contacts` (next-touch list). Parses/writes the markdown tables in place. | — |
| `build_resume.py` | `resumes/x.md` → ATS `.docx` (python-docx, single column, real bullets, no tables/headers) and → presentation PDF from `assets/templates/<name>.html` rendered by headless Chromium (playwright/cloakbrowser if present, else `--html` only); `--json` emits JSON Resume for the Reactive Resume MCP `import_resume`. In chat mode the skill uses Anthropic's docx/pdf skills instead. | `python-docx`, `playwright` |
| `ats_check.py` | Extracts the text layer from `.docx` (zip XML) or `.pdf` (pypdf if present, else `pdftotext`, else declares fallback); verifies contact literals and reading order; keyword coverage vs a posting file; 6-second lint (single column, metric in first bullet, dates present, title matches target); anti-slop phrase scan. | `pypdf` |

Every script: `--help`, JSON and markdown output, non-zero exit with a
plain-English message on failure, no secrets, no writes outside
`JOB_HUNT_DIR`. No auto-apply and no login automation anywhere.

## 6. Thin verb skills (Claude Code)

Each is ~10 lines: frontmatter (`argument-hint`, `disable-model-invocation:
true`), then "Use the job-hunting skill, role N, with `$ARGUMENTS`". The
`today` and `review` skills run `tracker.py` first via an inline
`` !`python3 ${CLAUDE_SKILL_DIR}/../job-hunting/scripts/tracker.py today` ``
so the numbers are in context before the model speaks. `search` can be
scheduled with `/loop 1d /job-hunter:search` for a daily fresh-postings
digest.

## 7. Explicitly out of scope

- Auto-apply / form-filling bots (LinkedIn/SEEK ToS, conflicts with
  targeted-over-spray; the answer bank is the honest substitute).
- Live interview copilots (detectable, ethically off).
- Gmail/Calendar sync as a core feature — mentioned as opportunistic when
  the user has those MCP connectors; not built.
- Scraping Glassdoor, Glints, NodeFlair, Kalibrr, foundit (blocked or
  wrong-country in tests).
- A database or web UI. Markdown files + scripts, by design.

## 8. Testing

- `tests/test_scripts.py` (pytest): tracker parsing/round-trip and funnel
  math on fixtures; `search_jobs` and `fetch_posting` parsers against
  recorded JSON/HTML fixtures (no network in CI); `ats_check` on a fixture
  .docx; `build_resume` docx structure (no tables, headings present).
- `tests/test_live.py` marked `network` (skipped in CI): one real JobStreet
  and one MCF query return ≥1 row.
- `tests/behavioral-scenarios.md`: A–L kept; add M (today view), N
  (knockout pre-check + legitimacy cap), O (referral-before-apply), P
  (anti-slop cover-letter gate), Q (post-offer 30-60-90).
- `build.py --check` fails if `SKILL.md` exceeds 500 lines or the
  description exceeds 1024 characters.

## 9. Phases

1. **Skeleton** — plugin layout, `build.py`, CI, move files, delete
   `*.cmd`/`*.sh`/commands, storage modes + new templates, SKILL.md rewrite.
2. **Scout & Ops scripts** — `search_jobs.py`, `fetch_posting.py`,
   `tracker.py` + `sourcing.md`, `pipeline.md`, `today`/`review` skills.
3. **New references** — `strategy.md`, `networking.md`, `answer-bank.md`,
   `post-offer.md`, `facts-policy.md`, `markets/*`; edits to jd-match.
4. **Writer scripts** — `build_resume.py`, `ats_check.py`, HTML templates,
   builder/revamp edits, JSON Resume export.
5. **Verification & docs** — pytest, live smoke, behavioral M–Q, README,
   PROJECT-DESCRIPTION, tag v6.0.0.

Each phase ends with `python3 build.py --check` and tests green.

## 10. Decisions (answered 2026-09-16)

1. Direction approved: plugin + scripts + nine-role restructure, all five
   phases.
2. Windows stays supported: scripts use `pathlib`, no shell-isms, LF in the
   zip regardless of host; README documents `python build.py` for Windows;
   `.gitattributes` keeps `*.py`/`*.md` LF.
3. Distribution: plugin marketplace from this repo (`.claude-plugin/`);
   `build.py --link` kept as a developer convenience.
4. Default workspace: `~/job-hunt` (`JOB_HUNT_DIR` overrides; a `job-hunt/`
   folder in the current directory wins when present).
