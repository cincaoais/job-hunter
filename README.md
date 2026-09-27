> **Work in progress — v6 revamp on branch `v6-revamp`.** Paused after Task 16 of 17 on 2026-09-27. To resume on any machine, read [`docs/handoff/HANDOFF.md`](docs/handoff/HANDOFF.md) first. This banner is removed when v6 merges.

# job-hunter

job-hunter is a Claude skill that acts as a job-search agent and career coach
for tech and other white-collar roles. Malaysia and Singapore come first
(JobStreet, MyCareersFuture, LinkedIn, local salary and notice norms); other
countries use a per-market template. It runs in two places. In Claude Code it
is a plugin: your profile, pipeline and contacts are markdown files in
`~/job-hunt` by default, and bundled Python scripts search the boards, fetch postings,
track applications, build resume files and check them. On claude.ai it is an
uploaded skill: one `candidate-profile.md` in a Project holds the same data,
and web search and pasted postings stand in for the scripts. It reads your
profile before it answers, asks only about gaps, and drafts only from facts in
that profile (`references/facts-policy.md`). Every request goes to one of nine
roles:

| # | Role | What it does | Try saying | Claude Code verb |
|---|---|---|---|---|
| 1 | Strategist | Target roles, positioning, career map, cadence and runway | "What roles should I aim for?" | (plain English) |
| 2 | Scout | Fresh openings from the boards, daily digest, shortlist | "Find me fresh openings this week" | `/job-hunter:search` |
| 3 | Qualifier | Knockout check, legitimacy check, fit score, apply / stretch / skip | "Am I a fit for this?" + posting | `/job-hunter:match` |
| 4 | Writer | Resume tailor or revamp, HR-eye score, cover letter, screening answers | "Tailor my resume for this posting" | `/job-hunter:resume`, `/job-hunter:cover` |
| 5 | Networker | Referral map before applying, outreach, contacts CRM | "Who can refer me at Grab?" | `/job-hunter:network` |
| 6 | Coach | Interview prep pack, mock interview, company dossier, soft skills | "Mock interview me for Friday" | `/job-hunter:interview`, `/job-hunter:company` |
| 7 | Negotiator | True annual comp, offer comparison, negotiation | "I got an offer — should I take it?" | `/job-hunter:offer` |
| 8 | Operations | Today view, weekly funnel review, stale and silent applications | "What should I do today?" | `/job-hunter:today`, `/job-hunter:review` |
| 9 | Onboarder | Resignation, notice, references, background check, 30-60-90 plan | "I accepted — what now?" | (plain English) |

In Claude Code, `/job-hunter:help` prints the roles with a phrase and a
verb for each. Every role also answers plain English, with or without the
verb.

## Install — Claude Code

Needs Claude Code, `git`, and Python 3.10 or later available as `python3`.

```sh
claude plugin marketplace add cincaoais/job-hunter
claude plugin install job-hunter@job-hunter
```

Start a new session afterwards. The repository `cincaoais/job-hunter` is
private: you need read access to it on GitHub, and Claude Code clones it with
`git` using the credentials already on your machine (it never prompts).

- The `owner/repo` shorthand tries SSH first and falls back to HTTPS. To use
  SSH explicitly, add the marketplace by its SSH URL:

  ```sh
  claude plugin marketplace add git@github.com:cincaoais/job-hunter.git
  ```

  SSH needs a key that works without a passphrase prompt (for example one
  loaded in `ssh-agent`) and github.com in `known_hosts`.
- HTTPS needs a stored credential: `gh auth login`, then `gh auth setup-git`.
  On a machine without a GitHub SSH key, set
  `CLAUDE_CODE_PLUGIN_PREFER_HTTPS=1` to skip the SSH attempt.
- Append `#<branch-or-tag>` to either form to pin a ref, for example
  `cincaoais/job-hunter#v6.0.0`.

Updates: `claude plugin marketplace update job-hunter`, then
`claude plugin update job-hunter@job-hunter` and restart; or turn on
auto-update for the marketplace under **Marketplaces** in `/plugin`. An
installed copy changes only when the plugin's `version` changes.

**From a clone** (for working on the skill itself):

```sh
git clone git@github.com:cincaoais/job-hunter.git
cd job-hunter
python3 build.py --link
```

`--link` symlinks each folder under `skills/` into `~/.claude/skills/`, and
skips a folder that already exists there as a real directory unless you add
`--force`. Restart Claude Code afterwards. Linked skills are personal skills,
so the verbs lose the plugin prefix (`/today`, `/search`, …); `help` shares
its name with Claude Code's built-in `/help`, so ask "what can you do?"
instead. Use either the plugin or `--link`, not both.

## Install — claude.ai

1. Get `job-hunting.skill`: download it from the repository's GitHub
   Releases page (CI attaches it to every `v*` tag; the same read access
   applies), or build it from a clone with `python3 build.py`, which writes
   `dist/job-hunting.skill`.
2. Turn on code execution (Settings → Capabilities), then upload the file:
   Customize → Skills → **+** → Create skill → Upload a skill. The `.skill`
   file is a zip of the `job-hunting/` folder; rename it to
   `job-hunting.zip` if the file picker accepts only `.zip`.
3. Create a Project, paste everything below the line in
   [`docs/PROJECT-DESCRIPTION.md`](docs/PROJECT-DESCRIPTION.md) into its
   instructions, and add your `candidate-profile.md` to the Project's
   knowledge. Start it from `skills/job-hunting/assets/profile-template.md`,
   or let the skill start one from your resume.

Chat mode has no files to edit, so the profile carries everything: its §9
Tracking section holds the pipeline, offers, contacts and soft-skills tables
and the Answers section. At the end of every session that changed anything,
the skill prints the whole updated profile as one markdown block; replace the
Project file with it, or the next session starts from stale data. Scripts
cannot reach the job boards from the claude.ai sandbox, so the Scout works
from web search and pasted postings, and resume files come from Anthropic's
docx and pdf skills.

## First run

In Claude Code:

1. `/job-hunter:help` — the nine roles, a phrase to try for each, and the
   verbs.
2. `/job-hunter:today` — runs `tracker.py today`. With no workspace yet it
   prints `No workspace found — run: python3 …/workspace.py init`; say yes
   when Claude offers to run it. From a clone you can run it yourself:

   ```sh
   python3 skills/job-hunting/scripts/workspace.py init
   ```

   The installed plugin keeps its copy under
   `~/.claude/plugins/cache/job-hunter/job-hunter/<version>/skills/job-hunting/scripts/`.
3. Give it your resume (paste it or name the file) and say what you are
   looking for. It fills `profile.md` from the resume first, then asks one
   grouped batch of questions about what is missing.

`workspace.py where` prints the workspace it will use: `$JOB_HUNT_DIR` if
set, else `./job-hunt/` if that folder exists in the current directory, else
`~/job-hunt`. `init` creates only what is missing and never overwrites:

| Path | Holds |
|---|---|
| `profile.md` | Snapshot, targets and search criteria (§1–§3 feed `search_jobs.py`), skills, experience, positioning, weekly cap |
| `pipeline.md` | One row per company and role: source, channel, stage, next action, due date, resume sent; an Offers table |
| `contacts.md` | Networking CRM: relationship, last touch, next touch, status |
| `answers.md` | Screening answers (salary, notice, work authorization, …), STAR stories, references |
| `seen-jobs.json` | Postings already shown, so each search lists only new ones |
| `postings/` | Saved postings (`fetch_posting.py --save`) |
| `resumes/`, `letters/` | Versioned resume and cover-letter drafts and the built files |
| `dossiers/` | Company briefs |
| `reviews/` | Weekly review files (`tracker.py digest`) |

Each workspace session ends with one `saved: …` line naming the files and
sections it changed.

## Scripts

In `skills/job-hunting/scripts/`. The core uses only the Python standard
library; an optional package that is missing is named in the output, and the
script carries on without it. Each script prints its usage with `--help`. The
skills run them for you.

| Script | What it does | Optional extras |
|---|---|---|
| `workspace.py` | `init` creates the workspace from the templates; `where` prints the resolved path | — |
| `search_jobs.py` | Searches JobStreet MY/SG, MyCareersFuture (SG), LinkedIn guest search and Hiredly (MY) with the profile's criteria (flags override: `--keywords --location --country --days --salary-min --sources --pages --all --no-seen`), drops seen postings and knockouts, ranks by freshness; `--markdown` or `--json` | `python-jobspy` (the Indeed source, opt-in via `--sources` or the profile) |
| `fetch_posting.py` | A posting URL, JobStreet id or MyCareersFuture uuid → markdown in `postings/<slug>.md` (`--save`); `--stdin` takes pasted text; exit 3 when the page is blocked | `cloakbrowser` (pages behind a bot challenge) |
| `tracker.py` | `add`, `set` (pipeline rows), `today`, `funnel`, `digest` (writes `reviews/<date>.md`), `contacts` (touches due), `contact` (upsert a contact); `--today YYYY-MM-DD` overrides the date | — |
| `build_resume.py` | Resume markdown → ATS `.docx` (`--docx`, standard library only), presentation `--html`/`--pdf` from five templates (`--template chicago`, `executive`, `corporate-sidebar`, `accent-band`, `creative-sidebar`), JSON Resume (`--json`) | `playwright` with Chromium for `--pdf`, else `cloakbrowser`; with neither it writes the `.html` and prints "PDF skipped" |
| `ats_check.py` | What a parser reads from a `.docx`, `.pdf`, `.md` or `.txt`: keyword coverage (`--posting` or `--keywords`), 6-second lint (`--lint`, `--target-title`), banned-phrase scan (`--slop`), extracted text (`--text`), `--json` | `pypdf` or poppler's `pdftotext` for PDFs; with neither, a PDF check exits 2 and says so |

Optional installs:

```sh
python3 -m pip install certifi         # TLS on python.org Python for macOS
python3 -m pip install python-jobspy   # Indeed source
python3 -m pip install cloakbrowser    # blocked posting pages; PDF fallback
python3 -m pip install playwright && python3 -m playwright install chromium   # PDF rendering
python3 -m pip install pypdf           # PDF text for ats_check.py (or install poppler for pdftotext)
```

On Python from python.org's macOS installer, board requests fail with
`CERTIFICATE_VERIFY_FAILED` until you run
`/Applications/Python 3.x/Install Certificates.command` or install
`certifi`, which the scripts use when present. They never turn TLS
verification off.

## The daily and weekly loop

| When | Run | What happens |
|---|---|---|
| Daily | `/job-hunter:today` | Overdue and due follow-ups, interviews this week, stale rows, auto-cold candidates, contacts due; Claude drafts the follow-ups and asks before marking a row cold |
| Daily | `/job-hunter:search` | New postings only (`--days 2` for the daily digest), knockouts applied, fit reasoning and a referral path per row |
| Per posting | `/job-hunter:match <url>` | Saves the posting, runs the knockout pre-check, legitimacy check and fit score, gives an apply / stretch / skip verdict |
| Before applying | `/job-hunter:network <company>` | Referral map (people searches as LinkedIn links), one outreach message, the touch logged in `contacts.md` |
| To apply | `/job-hunter:resume tailor to <posting>`, `/job-hunter:cover <company and role>` | Resume: inline draft, then on approval a claims audit, banned-phrase scan and 6-second lint, `build_resume.py` and `ats_check.py`; the resume sent is recorded on the pipeline row. Cover letter: saved, claims-audited and scanned before you see it |
| Weekly | `/job-hunter:review` | Sent → response → interview → offer by channel and source, the first leaking stage, one change for next week; writes `reviews/<date>.md` |
| As they come | `/job-hunter:interview`, `/job-hunter:company`, `/job-hunter:offer`, "I accepted — what now?" | Prep pack or mock, company dossier, offer read, post-offer steps |

Referral comes before application because a referral turns a ~3% cold
application into a ~40% interview chance (Ashby, 38M applications, 2025/26).
The weekly application cap and outreach target live in profile §8. For a
recurring digest, run `/loop 1d /job-hunter:search` in Claude Code.

## Windows

- Build with `python build.py` (and `python build.py --check`). CI runs the
  test suite and `--check` on Windows as well as Ubuntu.
- Run scripts from PowerShell with backslash paths, for example
  `python skills\job-hunting\scripts\workspace.py init`. The default
  workspace is `$env:USERPROFILE\job-hunt`; to put it elsewhere, set
  `$env:JOB_HUNT_DIR = "D:\job-hunt"` for the session or
  `setx JOB_HUNT_DIR D:\job-hunt` for new shells.
- The skills call `python3`. A python.org install on Windows provides only
  `python` and `py`, so `python3 --version` fails in the shell Claude Code
  uses. Either install Python from the Microsoft Store, which adds a
  `python3` command, or run the commands with `python` (or `py -3`) in
  place of `python3`; the skill tells Claude to do the same when `python3`
  is not found. The inline commands of `/job-hunter:today` and
  `/job-hunter:review` already fall back to `python`.
- `build.py --link` needs Developer Mode or an elevated shell to create
  symlinks. Without either it copies the folders instead; copies do not
  follow your edits, so re-run `python build.py --link --force` after
  changing or pulling the skills.
- `.gitattributes` keeps `.py`, `.md`, `.html`, `.json` and `.yml` files LF,
  and `build.py` writes LF into the zip on any host.

## Layout

| Path | What it is |
|---|---|
| `.claude-plugin/plugin.json` | Plugin manifest: name `job-hunter`, version |
| `.claude-plugin/marketplace.json` | The marketplace that lists the plugin, so `claude plugin marketplace add` works on this repo |
| `skills/job-hunting/SKILL.md` | The main skill: storage modes, memory rules, the nine-role router, principles |
| `skills/job-hunting/references/` | One file per role or flow; `markets/` holds `my.md`, `sg.md` and `_template.md` for other countries |
| `skills/job-hunting/scripts/` | The six scripts, `_common.py`, and `sources/` (one module per board) |
| `skills/job-hunting/assets/` | Workspace and profile templates, five resume HTML templates, `slop-phrases.txt` |
| `skills/<verb>/SKILL.md` | The eleven verb skills: `company`, `cover`, `help`, `interview`, `match`, `network`, `offer`, `resume`, `review`, `search`, `today` |
| `build.py` | `--check`, zip build to `dist/job-hunting.skill` (gitignored), `--link [--force]` |
| `docs/PROJECT-DESCRIPTION.md` | Instructions to paste into a claude.ai Project |
| `docs/superpowers/` | v6 design spec and implementation plan |
| `tests/` | pytest suites, `fixtures/` (including recorded board responses), `behavioral-scenarios.md` |
| `.github/workflows/ci.yml` | Tests and `--check` on Ubuntu and Windows; build; release on `v*` tags |

## Development

```sh
python3 -m pip install pytest
python3 -m pytest -q -m "not network"   # offline suite, as CI runs it
python3 -m pytest -q -m network         # live: a JobStreet search, a MyCareersFuture search, a JobStreet posting fetch
python3 build.py --check                # SKILL.md names, descriptions ≤ 1024 chars, ≤ 500 lines, no CRLF
python3 build.py                        # dist/job-hunting.skill
claude plugin validate .                # plugin and marketplace manifests
```

The skill's content lives only under `skills/`; `dist/job-hunting.skill` is
a build output, so rebuild it rather than editing it. To release, set the
same version in `.claude-plugin/plugin.json`, the entry in
`.claude-plugin/marketplace.json` and `metadata.version` in
`skills/job-hunting/SKILL.md`; merge to `main`, the branch that
`claude plugin marketplace add` clones unless a `#ref` is given; then push a
`v<version>` tag. CI runs the offline tests and `--check` on Ubuntu and
Windows, builds the zip, and attaches it to a GitHub release for the tag.

Behaviour tests: [`tests/behavioral-scenarios.md`](tests/behavioral-scenarios.md)
holds scenarios A–Q, run as fresh-agent sessions and graded against a
checklist, with results for rounds 1–4. In Round 4 (the v6 workspace-mode
scenarios, 2026-09-27) M, N, O and P passed with minor gaps and Q failed one
checklist item: the references brief was described, not drafted, and the
`withdrawn` tracker commands were promised, not shown.

## What it deliberately does not do

- **Auto-apply bots.** It drafts; you submit. `answers.md` keeps truthful
  screening answers ready to paste instead.
- **Live interview copilots.** Coaching happens before the interview, not
  during it.
- **Logging in to job boards.** The scripts use public board APIs and pages
  only; there is no login automation anywhere.
- **Scraping boards that block bots.** Glassdoor, Glints and NodeFlair are
  not scraped; salary data from them is read through live web search and
  cited.
- **Inventing facts.** No invented metrics, achievements, titles, competing
  offers or constraints. A missing number is asked for, and an estimate you
  supply is labelled as one.
