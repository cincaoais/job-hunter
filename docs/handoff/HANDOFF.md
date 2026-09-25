# Handoff — job-hunter v6 revamp (paused after Task 15)

Written 2026-09-25 on the original Mac, right before the user moved to a new
device and a new Claude account. Everything a fresh Claude Code session needs
to continue is in this repository on branch `v6-revamp`. Read this file top to
bottom once, then follow **Resume procedure**.

## 1. What the user asked for (the mandate)

The user (repo owner, GitHub `cincaoais`) asked Claude to revamp the whole
job-hunter project from first principles: research how job hunting really works
(roles, how jobs are found, what recruiters screen for), look at GitHub repos,
Reddit and the web for references (CloakBrowser encouraged for bot walls), add
missing features, and question whether the old `build.cmd` build scripts were
needed. They said not to treat the previous work as correct.

The user approved the design on 2026-09-16 with these answers:

| Question | Answer |
|---|---|
| Scope | Build all five phases (17 tasks) |
| Windows | Keep Windows working (build.py and scripts must run there) |
| Claude Code install | Plugin marketplace from this repo |
| Default workspace | `~/job-hunt` |

Working style the user showed: they check in between tasks and set explicit
stop points ("continue until task 10, then pause", "pause once task 15 is
done"). Honour stop points exactly, and end each stop with a short progress
table plus what is next.

## 2. Where the authoritative documents are

| Document | Path | Role |
|---|---|---|
| Design spec (approved) | `docs/superpowers/specs/2026-09-16-v6-revamp-design.md` | Binding authority |
| Implementation plan | `docs/superpowers/plans/2026-09-16-v6-revamp.md` | 17 tasks, 5 phases |
| SDD ledger | `.superpowers/sdd/2026-09-16-v6-revamp/progress.md` | Every task's commits, review outcome, fix rounds, rulings, deferred minors |
| Task briefs and reports | `.superpowers/sdd/2026-09-16-v6-revamp/task-N-{brief,report}.md` | Per-task requirements and implementer evidence |
| Research notes | `.superpowers/sdd/2026-09-16-v6-revamp/research-notes.md` | The only allowed source for statistics and market facts in reference files |
| Session history (optional) | `docs/handoff/history/claude-session-history.tar.gz` | Raw transcripts, only if the user exported them (see section 10) |

The ledger's first line names the plan file, so the
`superpowers:subagent-driven-development` skill recognises it and resumes at
the first task without a `Task N: complete` line. Review-package diffs
(`review-*.diff`) were not committed; regenerate them with the skill's
`scripts/review-package` when needed.

## 3. State at handoff

- Branch `v6-revamp`, pushed to `origin` (`git@github.com:cincaoais/job-hunter.git`, private). `main` is untouched on the remote.
- Tasks 1–15: **complete**, each implemented by a subagent, reviewed (spec + quality), fix-looped until clean.
- Tests: `python3 -m pytest -q -m "not network"` → 403 passed. `python3 build.py --check` → `OK: 12 skills pass checks`.
- Remaining: **Task 16**, **Task 17**, then the **final whole-branch review**, then **finishing the branch** (merge / PR decision is the user's).

What exists now:

| Area | Files |
|---|---|
| Plugin + build | `.claude-plugin/{plugin,marketplace}.json`, `build.py` (`--check`, zip to `dist/`, `--link [--force]`), `.github/workflows/ci.yml` (ubuntu + windows) |
| Main skill | `skills/job-hunting/SKILL.md` (router, nine roles, storage modes) |
| Verb skills | `skills/{search,match,resume,cover,network,interview,company,offer,today,review,help}/SKILL.md` |
| Scripts | `skills/job-hunting/scripts/`: `_common.py`, `workspace.py`, `sources/{jobstreet,mcf,linkedin,hiredly,indeed}.py`, `search_jobs.py`, `fetch_posting.py`, `tracker.py`, `build_resume.py`, `ats_check.py` |
| References | `references/`: `facts-policy`, `strategy`, `sourcing`, `jd-match`, `resume-builder`, `resume-revamp`, `answer-bank`, `networking`, `interview-prep`, `interview-coach`, `company-dossier`, `soft-skills-coach`, `offer-coach`, `post-offer`, `pipeline`, `profile-optimizer`, `application-guide`, `rxresume-mcp`, `markets/{_template,my,sg}.md` |
| Assets | `assets/{profile,pipeline,contacts,answers}-template.md`, `assets/templates/*.html` (5 resume templates), `assets/slop-phrases.txt` |
| Tests | `tests/test_*.py`, `tests/fixtures/` incl. `recorded/` board responses |

Deleted on purpose: `build.sh`, `build.cmd`, `deploy-cc.*`, `claude-code/` command
wrappers, committed `job-hunting.skill`, `NEXT-STEPS.md`, `tech-role-map.md`,
`sea-market-notes.md`, `feature-guide.md`.

## 4. Resume procedure (new device, new account)

1. Clone and check out the branch:
   ```
   git clone git@github.com:cincaoais/job-hunter.git
   cd job-hunter
   git checkout v6-revamp
   ```
2. If the user exported memory and history (section 10), restore them into
   the new Claude Code profile; otherwise skip this step — sections 1 and 7
   carry the same working rules:
   ```
   python3 docs/handoff/restore.py            # memory only
   python3 docs/handoff/restore.py --history  # also unpack transcripts for audit
   ```
   It computes the project slug from this checkout's absolute path and copies
   `docs/handoff/memory/*` into `~/.claude/projects/<slug>/memory/` without
   overwriting existing files (use `--force` to overwrite).
3. Install the environment (section 6), then verify:
   ```
   python3 -m pytest -q -m "not network"   # expect 403 passed
   python3 build.py --check                 # expect OK: 12 skills
   ```
4. Start Claude Code in the repo root and say:
   **"Read docs/handoff/HANDOFF.md and the ledger, then continue the v6 revamp
   with superpowers:subagent-driven-development from Task 16."**
   The session should confirm the branch is `v6-revamp`, read this file and
   `.superpowers/sdd/2026-09-16-v6-revamp/progress.md`, and resume at the first
   task without a `Task N: complete` line (Task 16). Never re-dispatch a
   completed task. (A project `CLAUDE.md` was not added: a hook on the old
   machine reserves that file for architecture sessions.)

Resuming the old transcript with `claude --resume` is not expected to work
across accounts; the handoff files replace it.

## 5. What to do next, in order

1. **Task 16** — brief: `.superpowers/sdd/2026-09-16-v6-revamp/task-16-brief.md`.
   `tests/test_live.py` (network-marked JobStreet + MCF smoke), append
   behavioural scenarios M–Q to `tests/behavioral-scenarios.md`, align
   `tests/fixtures/sample-profile.md` with the new template numbering (keep the
   planted 4-vs-5-years tension). Planned controller addition: after Task 16,
   run scenarios M–Q as simulated sessions (fresh agent + packaged skill +
   fixtures, Sonnet-class) and record a "Round 4" results block, as rounds 1–3
   in that file did.
2. **Task 17** — brief: `task-17-brief.md`. Rewrite `README.md`, update
   `docs/PROJECT-DESCRIPTION.md`, confirm version `6.0.0`, build, tag
   `v6.0.0` locally (the user pushes tags). README must mention: Windows
   `python build.py`; `playwright install chromium`; python.org Python on macOS
   needs `Install Certificates.command` or `certifi`; what the skill will not
   do (auto-apply, interview copilots, logins, scraping blocked boards).
3. **Final whole-branch review** on the most capable model with
   `requesting-code-review`'s code-reviewer prompt over
   `git merge-base main HEAD..HEAD`. Point it at every "minor (deferred)" and
   "Deferred minors" line in the ledger. Recommended to fix before merge: Task 14
   items 1 (hard-wrapped bullets detach), 2 (temp HTML before `try`),
   5 (wrapped contact line starts with a separator).
4. **Finish**: `superpowers:finishing-a-development-branch`. Before merging,
   remove the handoff scaffolding: `docs/handoff/`, the handoff banner at the
   top of `README.md` (Task 17 rewrites README anyway), and `.superpowers/` from git
   (`git rm -r --cached .superpowers`). List every ledger `Ruling:` line to the
   user under "Rulings I made" (the skill requires it).

## 6. Environment the next machine needs

| Need | How |
|---|---|
| Python ≥ 3.10 | Scripts are stdlib-only at the core |
| pytest | `python3 -m pip install pytest` |
| certifi | `python3 -m pip install certifi` (TLS on python.org macOS builds; `_common._ssl_context()` uses it) |
| PDF rendering | `python3 -m pip install playwright && python3 -m playwright install chromium` (on the old Mac the bundled Chromium was stale; `cloakbrowser` was the working fallback) |
| CloakBrowser (optional) | `python3 -m pip install cloakbrowser` — stealth Chromium for blocked pages; free tier = one session at a time; see `docs/handoff/tools/cfetch.py` |
| pdftotext (optional) | poppler (`brew install poppler` / apt `poppler-utils`); `ats_check.py` uses `pdftotext -raw` when `pypdf` is absent |
| python-jobspy (optional) | Indeed source only |
| Claude Code plugins | `superpowers@claude-plugins-official` (required for the SDD workflow), `context7@claude-plugins-official`; the old machine also used `snapclaude` from `git@github.com:Snapdec/snapclaude.git`, which the new account may not reach — it is not needed for this repo |

Old-machine Claude settings were: model Fable 5.1 with high effort, plugins
superpowers, context7 and snapclaude enabled, theme auto.

## 7. Process rules the next session must keep

- **Subagent-driven development**: one implementer per task (never parallel
  implementers), then a task review (spec + quality), then fix rounds with
  scoped re-reviews; rounds 1–3 resume the implementer, rounds 4–5 use a fresh
  implementer on a stronger model. Record every decision in the ledger as
  `Ruling: <decision> — <why> — <cost if wrong>`.
- **Commit trailer**: use whatever attribution the new harness specifies. The
  last trailer used here was `Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>`.
- **Facts policy**: statistics and market facts in reference files must come
  from `research-notes.md` with a cited source, or be labelled
  "(2026-09 notes — verify)". Never invent numbers.
- **Research access**: Reddit blocks direct fetches even through CloakBrowser;
  use search snippets. JobStreet v5, MyCareersFuture v2 and LinkedIn guest APIs
  work over plain HTTP (see `sources/*.py`).
- Do not push to `main`, do not merge, and do not push tags without the
  user's go-ahead.

## 8. Rulings made so far (full text in the ledger)

- Worked in place on `v6-revamp` rather than a worktree.
- Profile template §1–§3 labels kept verbatim so `search_jobs.read_criteria` parses them.
- `tracker.py today/funnel` exit 0 with an init hint when no workspace exists (inline skill commands must not abort).
- `build.py --link` may write to `~/.claude/skills` but refuses to replace a real directory without `--force`.
- `ats_check.py` accepts `.md`/`.txt`; `tracker.py contact` (upsert) added alongside `contacts` (list).
- TLS via `certifi` when present; never unverified TLS.
- `DETAIL_KEYS` extended with `location`, `salary_label`, `posted`.
- Funnel `diagnose` returns "healthy" for n ≥ 10 without a leak; "no reply" notes do not count as responses.
- Huntr/Ashby/Pin statistics kept only with citations.
- Profile §8 gained "Weekly application cap:" and "Weekly outreach target:"; §2 gained "Target list:"; §9 gained a chat-mode "Answers" section.
- "(est.)" on internal records; outbound text uses "~N"/"about N".
- Singapore CPF facts corrected (OW ceiling S$8,000/month from 2026; annual ceiling S$102,000; CPF for citizens/PRs only). Workplace Fairness Act: expected in force ~end-2027, <25 staff exempt initially.
- jd-match one-shot rule: ignore the posting's own row; another row past `saved` at the same company this cycle → skip.
- `ats_check.py`: `--target-title`; PDF extraction pypdf → `pdftotext -raw` → declared fallback (exit 2); PDF lint skips first-bullet/date; short/all-caps keywords match case-sensitively; step 6 uses `--posting … --lint --text`; unmarked headings need a colon, ≤ 4 words, or (for requirement/nice vocabulary only) a title-cased ≤ 8-word line.
- Commit trailer switched to the Opus 5.5 line when the harness changed it.

## 9. Known open items (not blockers)

- Hiredly `detail()` parsing unverified against a live job page; LinkedIn guest parsing depends on current markup.
- The `.docx` master has never been opened in Word or LibreOffice (checked structurally and by text extraction only).
- Playwright's bundled Chromium was stale on the old Mac; PDFs rendered through CloakBrowser.
- Template previews from the visual check are in `docs/handoff/reference/template-previews/`.

## 10. Memory and history

Claude Code's auto-mode safety check blocked copying files from `~/.claude`
(memory, settings, transcripts) into this repo on the old machine, so they are
not part of this commit unless the user added them separately. Nothing depends
on them: the ledger, briefs, reports, research notes and this file are the
working record, and sections 1 and 7 carry the user's working preferences.
