# Interview capability — R&D and design

Design spec, 2026-10-01. Status: **approved 2026-10-02 (Gate 1)** — option C,
v1 scope as §1, defaults in §10 accepted. Planner: Claude
(Opus 5.5); research digests by Sonnet subagents. Scope: job-hunter only; the
career vault that consumes this capability's files has its own spec in the
obsidian repo (`docs/2026-10-01-career-vault-design.md`).

**Evidence tags.** **(V)** = Verified: checked against this repo's code or docs,
or against a primary source (official docs, peer-reviewed paper, statute or
regulator page). **(U)** = Unverified: single secondary source, practitioner
claim, or inference. Repo claims cite `path:line`.

---

## 0. Starting point — what exists

The brief assumed `skills/interview/SKILL.md` was empty. It is not.

| Piece | State | Basis |
|---|---|---|
| `skills/interview/SKILL.md` | 13-line verb skill: default → prep pack, "mock" → mock interview, both via the Coach role | (V) `skills/interview/SKILL.md:1-13` |
| `references/interview-prep.md` | 125 lines: stage map, six answers, question banks, questions to ask, market rights, after-interview loop | (V) `interview-prep.md:20-125` |
| `references/interview-coach.md` | 51 lines: mock setup, one question at a time, per-answer feedback, debrief → `answers.md` STAR + profile §10 | (V) `interview-coach.md:8-51` |
| Coach row in the router | prep pack, mock, dossier, soft skills; no script | (V) `skills/job-hunting/SKILL.md:82` |
| Pipeline stages | `screen`, `interview`, `final` exist; Due = interview date, round type in Next action | (V) `tracker.py:39-48`, `references/pipeline.md:33-34` |

Gaps found by reading the files rather than the README:

1. Nothing is persisted. The prep pack is chat output; the self-debrief goes
   "into the profile" (V) `interview-prep.md:110-112`; there is no
   `interviews/` folder (V) `workspace.py:13`.
2. No question bank, no story→question map, no story-gap check (V) — grep of
   `references/` finds none.
3. Mock feedback is unanchored ("score honestly") (V) `interview-coach.md:36`;
   technical, system-design and case modes have no rubric of their own.
4. No owner for the interviewer thank-you note: the Writer has none, the
   Networker's thank-you template is for referrers (V) `networking.md:121-122`.
5. Dossiers carry no research date or refresh rule (V) `company-dossier.md`.
6. Market files cover interview *rights* (§10) but not interview *process*
   norms (V) `markets/my.md:158-169`, `markets/sg.md:153-170`.

So v1 **extends** the Coach role; it does not rebuild it.

## 1. Scope — candidate features

| Feature | v1? | Prompt / script | Reads | Writes | Overlaps |
|---|---|---|---|---|---|
| Prep pack per pipeline row (round, likely questions, dossier, story map, story gaps, questions to ask, lessons) | **v1** | prompt + `interview.py new` for the file | pipeline row, posting, dossier, `answers.md`, profile §5, question bank, `markets/<cc>.md`, career-vault wiki if present | `interviews/<slug>/<date>-prep-<round_type>.md`; pipeline Next action/Due via `tracker.py set` | Coach (existing), Qualifier extraction |
| Mock interviews: hr-screen, behavioral, technical, coding (talk-through), system-design, case/product, final | **v1** | prompt + `interview.py new` for the scorecard | posting, prep pack, `answers.md`, question bank | `interviews/<slug>/<date>-mock-<mode>.md`; STAR edits to `answers.md` on confirm; weak areas to profile §10 | Coach (existing); Negotiator mock (separate) |
| Anchored scoring rubric + self-score-first feedback | **v1** | prompt | — | scorecard table | — |
| Post-interview debrief | **v1** | prompt + `interview.py new` | prep pack, pipeline row | `interviews/<slug>/<date>-debrief-<round_type>.md`; stage/Next/Due via `tracker.py set` | Operations (stage changes) |
| Question bank that grows per debrief | **v1** | **script** `interview.py bank` (derived) | all debriefs + mock scorecards | `interviews/question-bank.md` (generated) | — |
| STAR story gap finder | **v1** | prompt (inside prep and debrief) | `answers.md` STAR stories + theme tags, question bank | gaps listed in the prep pack | Soft Skills Coach (gap list) |
| Thank-you / follow-up note | **v1** | prompt | debrief | nothing saved; follow-up Due via `tracker.py set` | Networker templates |
| MY / SG interview process norms | **v1** (light, cited) | prompt | — | — | `markets/*.md` §10 |
| Dossier research date + refresh rule | **v1** (one line) | prompt | dossier | dossier line | Coach (`/company`) |
| Coding mock that runs the user's code | **v1** (added 2026-10-02) | prompt — runs only an already-installed toolchain on a temp file; nothing installed | user's solution (temp file) | nothing kept | none |
| Voice mock / transcription | later | audio stack | — | — | dependency weight |
| "Interview passed, no debrief yet" in the today view | **v1** (added 2026-10-02) | `tracker.py today` reads debrief file names only | pipeline + `interviews/` names | — | Operations |
| Live interview copilot | **out** | — | — | — | v6 spec §7 out of scope (V) `docs/superpowers/specs/2026-09-16-v6-revamp-design.md:198`, README:266 |

Why a script at all: the career vault depends on the folder contract, so file
names and frontmatter must be deterministic and tested rather than left to
prompt compliance; and the question bank is pure aggregation (dedupe, count,
sort), which code does exactly and an LLM does approximately. Everything else
stays prompt-only (V for the repo convention: scripts own deterministic file
I/O, references own judgment — `tracker.py`, `fetch_posting.py save()`).

## 2. Architecture options

**A. Inside job-hunter.** Fill `skills/interview/`, add references, add
`scripts/interview.py`.
**B. Separate repo and plugin** with its own marketplace, sharing the
workspace through `JOB_HUNT_DIR`.
**C. Hybrid.** A, plus a file contract and import rules that let the
capability be extracted later.

| Criterion | A. Inside | B. Separate plugin | C. Hybrid |
|---|---|---|---|
| Data coupling | Shares workspace, references, `_common.py` freely | Workspace shared by contract; profile schema, facts policy and market files must be duplicated or vendored | Shares like A; interview code may depend only on `_common.py` and the documented files |
| claude.ai mode | Ships in the same zip; references load on demand; one regenerated `candidate-profile.md` | A second upload. Custom skills are per-user and do not sync across surfaces (V, platform skills overview). Both skills would regenerate the same `candidate-profile.md` at session end — two writers of one document. No documented way for one claude.ai skill to read another's bundled files, so facts policy and markets get copied (U, inference) | Same as A |
| Dependency weight | v1 is stdlib only. A future audio or code-runner stack would bloat the claude.ai zip | Isolated from day one | Same as A now; extraction is the escape hatch when a heavy dependency arrives |
| Install / update | Nothing new | Second marketplace. Private repos need the user's git credentials — "marketplace.json has no field for one" (V, host-marketplace docs). Third-party auto-update is off by default (V, plugins/loading). A cross-marketplace dependency is skipped unless allow-listed, and the plugin then fails to load (V, plugins/dependencies) | Nothing new; a later split goes into the **same** marketplace, where sibling dependencies need no allow-list (V, plugins/dependencies) |
| Release / versioning | Same three places (V) README Development | A second version triplet plus a compatibility range between plugins, resolved against `<plugin>--v<version>` git tags (V, plugins/dependencies) | Same as A, plus `contract: 1` in every interview file |
| Testing | One pytest suite; CI already runs Windows (V) `.github/workflows/ci.yml` | Duplicated fixtures and CI; integration needs both repos | Same as A, plus a contract test the vault relies on |
| Token cost on the router | Router table text only; reference files cost nothing until read (V, skills docs "supporting files load on demand"); verb skills with `disable-model-invocation` have no description in context (V, skills frontmatter table) | A model-invocable skill adds ~100 tokens of description (V, platform overview) and competes with job-hunting's "prepare for interviews" trigger (V) `SKILL.md:4` | Same as A |
| Command naming | Keep `/job-hunter:interview`, add modes (`mock`, `debrief`); no new verb. `--link` already exposes bare `/interview` and the known `/help` clash (V) README:75-80 | New namespace; linking adds more bare names | Same as A |
| Useful without job-hunter | No | Yes in principle, but only by rebuilding a profile and story bank | No (until extracted) |
| Windows | Stdlib, `use_utf8_output`, `newline="\n"` as today (V) `_common.py:31`, `tracker.py:167` | Same, plus its own Windows CI; symlink sharing needs Developer Mode (V, host-marketplace docs) | Same as A |

### Recommendation: C

Build inside job-hunter now under four rules, so extraction later is a code
move, not a data migration:

1. **C1 — imports.** `interview.py` imports only `_common.py`. It reads
   `pipeline.md` through `_common.read_table`, never through `tracker.py`.
2. **C2 — data.** Interview data lives only under `interviews/`. Every other
   file changes through its owner (§5).
3. **C3 — references.** Interview references are `interview-*.md` and name
   other references only by file name.
4. **C4 — contract.** Every interview file carries `contract: 1`; a pytest
   contract test parses the fixture files the vault depends on.

Extraction path (later, if a heavy dependency arrives): move
`skills/interview/`, `references/interview-*.md`, `scripts/interview.py`,
`assets/interview-*-template.md` and `tests/test_interview.py` into a second
plugin **in the same marketplace**, declared with `"dependencies":
["job-hunter"]`; `_common.py` is shared by an in-marketplace symlink, which the
plugin cache dereferences (V, host-marketplace docs). The workspace does not
change.

**Rejected — B:** the claude.ai two-writer problem has no clean fix, the
duplicated facts policy and profile schema would drift, and private-marketplace
auth adds a failure mode that "fails quietly" (V, host-marketplace docs) for no
v1 benefit. **Rejected — plain A:** costs the same as C minus four rules, and
loses the extraction path and the tested contract the vault needs.

## 3. Research that shaped the design

| Finding | Tag | Source | Encoded as |
|---|---|---|---|
| Structured interviews are the strongest single predictor of job performance (mean validity ≈ .42) after Sackett et al. corrected earlier range-restriction over-correction | V | Sackett, Zhang, Berry & Lievens 2022, *J. Applied Psychology* (researchgate.net/publication/357440267); SIOP summary | Mocks mirror a structured interview: fixed questions per round, anchored scores |
| Past-behaviour questions validated higher than situational ones (.56 vs .45) | V | Taylor & Small 2002, *JOOP* (doi 10.1348/096317902320369712) | Behavioural bank first; situational variants second |
| Rubrics with behavioural anchors on a common scale; at least three anchored levels | V | US OPM Structured Interview Guide (opm.gov) | 1–5 scale anchored at 1, 3, 5 (§4.3) |
| Four-level labels poor / borderline / solid / outstanding with example answers | V | Google re:Work structured interviewing guide | Summary label next to the number |
| STAR time split ≈ 20 / 10 / 60 / 10; use "I" not "we"; quantify the result | V (university career centre) | MIT CAPD, "The STAR method" | Per-answer checks in behavioural mocks |
| A fixed spoken length (e.g. 60–90 s or 1.5–2 min) | U | no authoritative source found | Kept as the existing default (`interview-coach.md:34`), labelled a heuristic |
| Coaching interviewees improves structured-interview performance (longer, more structured answers) without destroying validity | V (abstracts read) | Maurer et al. 1998/2001/2008 (pubmed 11519654) | Mocks are worth doing; no claim about offer rates |
| Retrieval practice with feedback beats re-reading; spaced beats massed | V (memory research, not interviews) | Roediger & Karpicke 2006 | Re-practice queue in the question bank |
| Self-assess first, then coach with quoted evidence | U | design inference | Mock loop step order |
| Same-day debrief (questions verbatim, stories used, signals) | U | practitioner (e.g. noamseg/interview-coach-skill, MIT licence — idea only) | Debrief template; prompt within 24 h |
| AI-assistance policies differ by company and round (Canva permits; others restrict) | V for Canva (canva.dev blog); U for Meta/Google/Amazon | canva.dev/blog/engineering/yes-you-can-use-ai-in-our-interviews | Coding mocks ask "is AI allowed in this round?" |
| System-design and coding rubric dimensions | U | prep-site conventions (tryexponent, designgurus) | Dimensions in §4.3, labelled as convention |
| SG: TAFEP guidance — avoid age, race, religion, marital status, family plans unless job-related; discuss salary expectations openly | V | tal.sg/tafep "Conducting job interviews" | `markets/sg.md` §10 already close; add process norms |
| SG Workplace Fairness Act 2025 passed, not yet in force | V for "uncommenced" (sso.agc.gov.sg); U for the ~end-2027 date | Singapore Statutes Online | Keep the "check before calling a question unlawful" rule (V) `sg.md:153-170` |
| MY statutory notice 4 / 6 / 8 weeks by tenure | V in repo (`my.md:119-134`); U for the secondary summaries found | Employment Act 1955 s.12 | Unchanged; HR-screen mode points to it |
| No official source for MY/SG "expected salary" or notice-period interview norms | — | none found | Norms written as practitioner guidance, labelled U, user confirms |

Open-source interview skills reviewed for ideas only, no text copied:
`noamseg/interview-coach-skill` (story strength ratings), `yanliudesign/
behavior-question-skill` (JD → question → story map), `raphaotten/
claude-interview-coach` (anti-pattern tracking), `borghei/Claude-Skills`
pm-interview-prep (framework per round type). All (U) as ideas.

## 4. Design

### 4.1 Commands

One verb, three modes — no new skill directory, no new `--link` name:

| Say | Verb | Mode |
|---|---|---|
| "Prep me for the Awan Ledger technical round" | `/job-hunter:interview Awan Ledger technical` | prep (default) |
| "Mock interview me — system design" | `/job-hunter:interview mock system-design` | mock |
| "Debrief: just finished the Grab screen" | `/job-hunter:interview debrief Grab` | debrief |

### 4.2 Flows

**Prep** (`interview-prep.md`): pin the round (pipeline row echo) → refresh
the dossier if its `_Researched:_` date is over 30 days old, or offer
`/job-hunter:company` if none → `interview.py new --kind prep` → fill the
pack: round, company brief, likely questions (posting + dossier themes +
question bank + market), **story map** (theme → `answers.md` story), **story
gaps**, the six answers as pointers, questions to ask, **lessons to apply**
(question bank + career-vault playbooks if present) → `tracker.py set --next
"<round_type> prep done; mock?" --due <date>` → `saved:` line.

**Mock** (`interview-coach.md`): setup batch (round type, length, language,
"is AI allowed?" for coding) → one question at a time → **user self-scores
first**, then the coach scores against the anchored rubric with a quoted
phrase as evidence → one fix per answer → end debrief (strengths, drills,
re-run list) → `interview.py new --kind mock` scorecard → STAR edits to
`answers.md` only after the user confirms (facts-policy §5) → `interview.py
bank` to refresh the re-practice queue.

**Debrief** (`interview-debrief.md`, new): within 24 h → `interview.py new
--kind debrief` → questions asked (theme, story used, landed yes/partly/no),
what landed, what didn't, signals and next round, promises and follow-ups,
**lessons in the user's own words** → handoffs (§5): stage/Next/Due via
`tracker.py`, thank-you draft via the Networker template, new facts to the
profile with confirmation, salary to `answers.md` → `interview.py bank` →
`saved:` line.

### 4.3 Rubric (in `interview-coach.md`)

Scale 1–5, anchored at 1, 3, 5 (OPM shape, V), with Google's labels as a
summary (1–2 poor, 3 borderline, 4 solid, 5 outstanding).

| Mode | Dimensions |
|---|---|
| behavioral, final, hr-screen | relevance · specificity · own role ("I") · result and number · reflection · delivery |
| technical (past-work deep-dive) | depth · trade-offs named · own role · accuracy under probing |
| coding (talk-through) | clarifying questions · approach · correctness · complexity · testing · communication (U, convention) |
| system-design | requirements and scope · high-level design · trade-offs · scale and reliability · communication (U, convention) |
| case / product | structure · hypotheses · use of data · recommendation · risks |

Anchors for behavioural relevance and result, as an example of the form:
1 = no real example, or a hypothetical; 3 = a real example, own part or
result vague; 5 = specific and recent, own actions clear, quantified result,
survives the follow-up probe. Scores are coaching signals, not predictions of
an offer — the skill never claims otherwise (U: no evidence on offer rates).

### 4.4 Ownership inside job-hunter

| File | Single writer |
|---|---|
| `interviews/<slug>/*-prep-*.md`, `*-mock-*.md`, `*-debrief-*.md` | Coach, created by `interview.py new`, sections filled in place |
| `interviews/question-bank.md` | `interview.py bank` only (generated; edits go in the debriefs) |
| `pipeline.md` | `tracker.py` (unchanged) |
| `answers.md` STAR stories | edited on confirm per facts-policy §5 (unchanged rule) |
| `profile.md` | per facts-policy §1/§8 (unchanged rule) |

## 5. Handoffs

| Need during an interview flow | Goes to | Mechanism |
|---|---|---|
| Stage, Next action, Due, Notes | Operations | `tracker.py set --company … --role … --stage/--next/--due/--note` — the only writer of `pipeline.md` |
| Company research | Coach `/job-hunter:company` | `company-dossier.md` → `dossiers/<company>.md` |
| "What are your salary expectations?" | Writer's answer bank, then Negotiator | Use `answers.md` › Expected salary and `markets/<cc>.md` §5; never invent a number; an offer → `offer-coach.md` |
| Thank-you and follow-up messages | Networker templates | New "Interviewer thank-you" template in `networking.md` §5 next to the existing nudge and thank-you templates; `ats_check.py --slop`; Due via `tracker.py` |
| New or reworked STAR story | answers.md STAR stories | Proposal shown; written on confirm; no added scene, decision or result (facts-policy §5) |
| New achievement surfaced in a debrief | Profile §5 | facts-policy §1: ask, write the profile first, then use it |
| Theme with no true story | Soft Skills Coach | §9 Soft skills development table |
| Third rejection at one stage | Operations funnel | `pipeline.md` §5 diagnosis |
| Durable lessons | Career vault (other repo) | Vault reads debriefs in place; never writes `job-hunt/` |

Thank-you owner: the Networker, not the Writer — every short message template
(nudge, referrer thank-you, recruiter reply) already lives in `networking.md`
§5 with the slop gate (V) `networking.md:94-122`; the Writer owns long-form
documents. Default chosen; overridable at Gate 1.

## 6. File contract

### 6.1 Layout

```
job-hunt/
└── interviews/
    ├── question-bank.md                       generated by interview.py bank
    └── <slug>/                                one folder per pipeline row
        ├── 2026-10-03-prep-technical.md
        ├── 2026-10-01-mock-system-design.md
        └── 2026-10-03-debrief-technical.md
```

- `<slug>` = `slugify(company + " " + role)` (V) `_common.py:53` — the same
  slug `postings/` uses when the posting title equals the pipeline Role (V)
  `fetch_posting.py:415-419`.
- File name `<date>-<kind>-<round_type>.md`; a repeat gets `-2`, `-3`, never
  an overwrite. `<date>` is the interview date for prep and debrief, the
  practice date for a mock.
- `workspace.py init` adds `interviews/` and still never overwrites (V)
  `workspace.py:15-26`.

### 6.2 Frontmatter

```yaml
---
contract: 1
kind: debrief            # prep | mock | debrief
company: "Awan Ledger Sdn Bhd"
role: "Backend Engineer (Go)"
round: 2                 # 1-based within this process; blank if unknown
round_type: technical    # hr-screen | behavioral | technical | coding | system-design | case | assessment | final
date: 2026-10-03
outcome: pending         # debrief only: pending | advanced | rejected | offer | withdrawn
---
```

Mocks use `round_type` for the mode (`assessment` is not a mock mode).

### 6.3 Body tables the script reads

Debrief `## Questions asked`:

| # | Question | Theme | Story used | Landed |
|---|---|---|---|---|

Mock `## Scores`:

| # | Question | Theme | Self | Coach | Evidence |
|---|---|---|---|---|---|

Themes: `intro`, `motivation`, `strengths-weaknesses`, `leadership`,
`conflict`, `failure`, `pressure`, `initiative`, `technical`, `coding`,
`system-design`, `case`, `logistics`, `salary`, `curveball`, `other`. The five
STAR themes (leadership, conflict, failure, pressure, initiative) come from
the existing prep rule (V) `interview-prep.md:53-55`. `Landed`: `yes`,
`partly`, `no`.

Other debrief sections, read by people and by the vault, not by the script:
`## What landed`, `## What didn't`, `## Signals and next round`,
`## Promises and follow-ups`, `## Lessons (your words)`.

`answers.md` STAR lines gain optional theme tags:
`1. **Title:** — one line (themes: failure, pressure)`.

### 6.4 `interview.py`

```
interview.py new  --kind prep|mock|debrief --company C --role R --round-type T
                  [--round N] [--date YYYY-MM-DD] [--today YYYY-MM-DD]
interview.py bank [--today YYYY-MM-DD]
```

- `new` requires a pipeline row matching company and role, case-insensitive
  (the tracker's upsert key, V `tracker.py` add). No row → exit 2 with the
  `tracker.py add` command to run. Prints the created path.
- `bank` rewrites `interviews/question-bank.md`: asked-in-real-interviews
  table (question, theme, times, companies, last asked, landed counts),
  questions with no story (landed `no`, story blank), re-practice queue
  (latest mock Coach score ≤ 2 per question). Questions dedupe on
  lower-cased, punctuation-stripped text.
- No workspace → the tracker's message, exit 0; bad input → exit 2 (V,
  `tracker.py` convention). UTF-8 output guard, `newline="\n"` writes.

### 6.5 Reads from outside `job-hunt/`

If the workspace's parent folder holds `wiki/_index.md` (a career vault), prep
reads `wiki/hot.md` and the index rows that mention interviews or this
round type, and cites them under "Lessons to apply". Read-only; absent → the
section says "no lessons file". Defined from the vault side in the vault
spec.

## 7. claude.ai mode

- The `.skill` zip contains `skills/job-hunting/` only (V) `build.py:67-78`;
  the interview verb is a Claude Code entry point. In claude.ai the user says
  "debrief my Grab screen" and the router reaches the Coach and
  `interview-debrief.md` — so all v1 content goes in `references/` and
  `assets/`, none in `skills/interview/`.
- No files, no scripts. Profile §9 gains an `### Interviews` table:

  | Date | Company | Role | Round | Outcome | Asked (themes) | Landed / missed | Next |
  |---|---|---|---|---|---|---|---|

  The newest 12 rows stay; older rows collapse into one "Interview patterns"
  line in §10 so the single document stays small.
- Prep packs and mock scorecards are delivered in chat, not stored; STAR
  stories go to the Answers section, weak areas to §10 (as today). The
  question bank is computed from the §9 table on request; the skill never
  claims a script ran (V, facts-policy §4 chat-mode rule).
- The career vault cannot see claude.ai data; that is stated in the vault
  spec, not worked around.

## 8. Files touched (v1)

| Path | Change |
|---|---|
| `skills/interview/SKILL.md` | modes prep / mock / debrief; script calls |
| `skills/job-hunting/SKILL.md` | Coach row (+ debrief, `interview-debrief.md`, `scripts/interview.py`); init list gains `interviews/` |
| `references/interview-prep.md` | persisted pack, story map, gaps, lessons, dossier freshness; after-interview loop → debrief; move the MY law sentence to `markets/my.md` (followups-v6.0.1:31) |
| `references/interview-coach.md` | modes, anchored rubric, self-score first, scorecard file, AI-allowed check |
| `references/interview-debrief.md` | **new**: debrief, question bank, handoffs, chat mode |
| `references/company-dossier.md` | `_Researched: YYYY-MM-DD_` line + 30-day refresh rule |
| `references/networking.md` | interviewer thank-you template |
| `references/pipeline.md` | one line: debrief after every round |
| `references/markets/_template.md`, `my.md`, `sg.md` | §10 gains "Interview process" norms, cited, U where practitioner |
| `scripts/interview.py` | **new** (`new`, `bank`) |
| `scripts/workspace.py` | `interviews` in DIRS |
| `assets/interview-{prep,mock,debrief}-template.md` | **new** |
| `assets/answers-template.md`, `assets/profile-template.md` | theme tags; §9 Interviews table |
| `skills/help/SKILL.md`, `README.md`, `docs/PROJECT-DESCRIPTION.md` | Coach row, layout, chat-mode line |
| `tests/test_interview.py`, `tests/test_workspace.py` | new and updated tests |
| `tests/behavioral-scenarios.md` + `tests/fixtures/scenarios/r-workspace/` | scenarios R–U |

## 9. Test plan sketch

pytest (`tests/test_interview.py`, in-process `main(argv)` plus one
subprocess run, `JOB_HUNT_DIR` monkeypatched, `--today` pinned — the
`test_tracker.py` pattern, V):

1. `new` writes `interviews/<slug>/<date>-<kind>-<round_type>.md` with the
   frontmatter filled (parametrized over the three kinds).
2. `new` never overwrites: a repeat gets `-2`, the first file is unchanged.
3. `new` rejects an unknown kind or round type, and a missing pipeline row,
   with exit 2 and a hint (parametrized).
4. `bank` aggregates two fixture debriefs: counts, companies, last asked,
   landed; lists no-story questions; ignores preps.
5. `bank` re-practice queue holds a question whose latest mock score is ≤ 2
   and drops it once a later mock scores 4.
6. No workspace → message, exit 0 (both subcommands).
7. Subprocess under `PYTHONIOENCODING=cp1252` with a non-ASCII company name
   (Windows guard, V pattern `test_tracker.py:460-468`).
8. `workspace.py init` creates `interviews/` (update `test_workspace.py:9-10`).
9. Contract test: the fixture debrief in `r-workspace/` parses with
   `contract: 1` and the documented columns.
10. The today view lists a past interview row without a debrief under
    "Debriefs due" (added 2026-10-02, `tests/test_tracker.py`).

Behavioural scenarios (continuing after Q; workspace copy of
`scenarios/r-workspace/`, today 2026-10-01):

- **R — Prep pack.** Stage `interview`, Due 2026-10-03; dossier researched
  2026-06-01; `answers.md` has no failure story. Expected: echo instead of
  asking; dossier refresh offered; story map; failure gap named and drawn out
  from profile §5 without inventing; file via `interview.py new`; Next/Due via
  `tracker.py set`; `saved:` line.
- **S — System-design mock.** Expected: one question at a time; self-score
  first; anchored scores with quoted evidence; an embellished number from the
  user is flagged at once (facts-policy §5); scorecard saved; weak question in
  the re-practice queue.
- **T — Debrief after an HR screen** with a salary question and a newly
  mentioned achievement. Expected: debrief file with themed questions; stage
  advanced via `tracker.py`; salary answered from `answers.md`, no invented
  number; achievement written to profile §5 only after confirmation;
  thank-you draft ≤ 4 lines from the Networker template; `bank` run.
- **U — Chat-mode debrief** on `fixtures/sample-profile.md`. Expected: §9
  Interviews row; full profile regenerated; no claim that a script ran.

Gates before finishing: offline suite, `build.py --check`, `claude plugin
validate .`, compared with the Phase 0 baseline (431 passed, 1 environmental
failure: `test_text_files_check_out_with_lf_everywhere` needs a git checkout).

## 10. Risks and open questions

Risks:

1. **Contract drift** if the agent hand-writes interview files. Mitigation:
   every flow calls `interview.py new`; the contract test; `contract: 1`.
2. **Third-party personal data** (interviewer names) in debriefs. Optional
   field; the vault spec forbids copying names into the wiki.
3. **Real data in the repo.** `job-hunt/` is already git-ignored (V)
   `.gitignore`; all fixtures are fictional (V) `tests/fixtures/sample-profile.md:1`.
4. **claude.ai profile growth.** Capped at 12 Interviews rows.
5. **False precision** of rubric scores. Labelled coaching signals; no
   offer-rate claims.
6. **Legal drift** in market notes (SG WFA commencement). Keep "check before
   stating" wording; tag U where unverified.
8. **claude.ai upload limits.** The zip format (skill folder as root, `SKILL.md`)
   is verified (support.claude.com "Creating custom skills"; platform skills
   overview). No size or file-count limit is published (U; the 30 MB figure is
   third-party). The help article gives a 200-character description limit
   while the platform docs give 1,024 — the router's description (≈1,019
   characters, ≈1,015 before this work) needs a real upload to settle it.
7. **Hand edits to `question-bank.md`** are lost on the next `bank`. The
   generated header says so.

Open questions (defaults chosen; overridable at Gate 1):

1. Thank-you owner — default Networker (§5).
2. Persist mock scorecards — default yes.
3. Release — whether this ships as 6.1.0 is asked at Gate 3; no tag either
   way.
4. Coding mocks that execute the user's code — done 2026-10-02 (prompt-only, local toolchain).
5. A today-view nudge for "interview passed, no debrief" — done 2026-10-02 (`tracker.py today`, "Debriefs due").
