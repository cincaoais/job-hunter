# Task 17 report — README, PROJECT-DESCRIPTION

Status: DONE_WITH_CONCERNS
Commit: 60ebb4b `v6.0.0: README, project description` (trailer `Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>`). No tag created, nothing pushed. `progress.md` (controller's edit) left unstaged; this report is not committed.

## Files changed

- `README.md` — rewritten. Line 1 is the existing banner, unchanged.
- `docs/PROJECT-DESCRIPTION.md` — updated, same voice and "paste below the line" structure.
- `.claude-plugin/marketplace.json` — one line added: top-level `"description"`, to clear the only `claude plugin validate .` warning.
- `SKILL.md` metadata.version and `plugin.json` were already `6.0.0`, so no change.

## Sections written

README: banner; What it is (one paragraph plus the nine-role table: role, what it does, "try saying", verb); Install — Claude Code (shorthand + install, private-repo access: SSH-first shorthand, SSH URL form, SSH/HTTPS needs, `CLAUDE_CODE_PLUGIN_PREFER_HTTPS=1`, `#ref` pinning, updates, and `build.py --link` from a clone with the no-prefix/`/help` clash note); Install — claude.ai (Releases or `python3 build.py`, upload path, Project setup, chat-mode memory rule); First run (`/job-hunter:help`, `/job-hunter:today`, `workspace.py init`, plugin cache path, workspace resolution plus a workspace file table); Scripts (table: name, one line with real flags, optional extras; optional-install block; python.org macOS TLS note); The daily and weekly loop (today → search → match → network → resume/cover → review; one Ashby statistic cited the way `networking.md` cites it; `/loop 1d`); Windows; Layout; Development (pytest offline and live, `--check`, build, validate, how to release by tag); Behaviour tests line (Round 4: M, N, O, P pass with minor gaps; Q fails one checklist item); What it deliberately does not do (auto-apply, interview copilots, logins, scraping Glassdoor/Glints/NodeFlair, inventing facts).

PROJECT-DESCRIPTION: the header adds the upload path and one sentence saying that in Claude Code the same skill uses the `~/job-hunt` files instead. The capability paragraph is now a nine-role list. "Keep my memory current" now states the chat-mode rule: regenerate the full profile block at the end of every session that changed anything, and it is not optional. "Ground everything" says the scripts cannot reach the boards from claude.ai. The Mode and Formatting paragraphs are unchanged.

## Deviation from the brief (facts over the brief)

The brief says "upload in Settings → Features". Anthropic's current help article (support.claude.com, "Using Skills in Claude", fetched 2026-09-27) gives a different path: turn on code execution under Settings → Capabilities, then Customize → Skills → + → Create skill → Upload a skill, with a ZIP file. The README and PROJECT-DESCRIPTION use that path. Because the article names ZIP, the README says to rename `.skill` to `.zip` if the file picker accepts only `.zip`.

## Every command verified

Plugin install was tested in isolated `CLAUDE_CONFIG_DIR`s in the scratchpad. The user's `~/.claude` was not touched, and the scratch configs were deleted afterwards.

| README command | How verified | Result |
|---|---|---|
| `claude plugin marketplace add cincaoais/job-hunter` | ran as `cincaoais/job-hunter#v6-revamp` | `Cloning repository: git@github.com:cincaoais/job-hunter.git (ref: v6-revamp)` … `✔ Successfully added marketplace: job-hunter`. Without `#ref` today: `✘ Failed to add marketplace: Marketplace file not found …` because `main` is still v5. Expected until merge; see concerns. |
| `claude plugin install job-hunter@job-hunter` | ran | `✔ Successfully installed plugin: job-hunter@job-hunter (scope: user)`; `plugin details`: `Skills (12) company, cover, help, interview, job-hunting, match, network, offer, resume, review, search, today` |
| `claude plugin marketplace add git@github.com:cincaoais/job-hunter.git` | ran with `#v6-revamp` | added; `marketplace list`: `Source: Git (git@github.com:cincaoais/job-hunter.git@v6-revamp)`; install ok |
| `#<branch-or-tag>` pinning | the two runs above | works with both forms |
| `claude plugin marketplace update job-hunter` / `claude plugin update job-hunter@job-hunter` | ran | `✔ Successfully updated marketplace: job-hunter` / `✔ job-hunter is already at the latest version (6.0.0).` |
| `gh auth login`, `gh auth setup-git`, `CLAUDE_CODE_PLUGIN_PREFER_HTTPS=1`, ssh-agent/known_hosts, auto-update under Marketplaces in `/plugin` | `gh … --help`; code.claude.com host-marketplace doc | as documented |
| `git clone git@github.com:cincaoais/job-hunter.git` | `git ls-remote` ok (main e75c433, v6-revamp 38a9ec5); the SSH marketplace add cloned it | ok |
| `python3 build.py --link` (+ `--force`, skip rule) | `HOME=<scratch>` | 12 symlinks, `Restart Claude Code to pick up the skills.`; an existing real `today/` dir skipped, then replaced with `--force` |
| plugin cache path `~/.claude/plugins/cache/job-hunter/job-hunter/<version>/skills/job-hunting/scripts/` | isolated install | present at `…/cache/job-hunter/job-hunter/6.0.0/…`; `tracker.py today` from there printed the init hint |
| `/job-hunter:today` with no workspace | `JOB_HUNT_DIR=<missing> tracker.py today` | `No workspace found — run: python3 …/workspace.py init`, exit 0 |
| `python3 skills/job-hunting/scripts/workspace.py init` / `where` | scratch `JOB_HUNT_DIR` | `Created: profile.md, pipeline.md, contacts.md, answers.md, seen-jobs.json, postings/, resumes/, letters/, dossiers/, reviews/`; `where` checked for all three: env, `./job-hunt` in cwd, `$HOME/job-hunt` |
| `search_jobs.py` flags | `--help`; live `--keywords "backend engineer" --country MY --days 3 --sources jobstreet,indeed --no-seen --markdown`; `--sources mcf --country SG --json` | `## 78 new postings …`, exit 0; MCF JSON rows |
| `fetch_posting.py --stdin --company --title --url --save` | fixture JD | `Saved …/postings/finora-backend-engineer.md`, exit 0 |
| `build_resume.py --docx --html --json --template executive`; `--pdf --template chicago` | fixture resume | `.docx/.html/.json` written; PDF rendered via the cloakbrowser fallback (confirms "playwright, else cloakbrowser") |
| `ats_check.py … --posting … --lint --slop`; `.pdf --target-title … --json` | built files | `Method: docx-xml`, must-have/nice-to-have split, lint ok, `Slop: none found`; PDF `method: pdftotext-raw`, date/first-bullet `skip` |
| `tracker.py add/set/contact/today/contacts/funnel/digest` | scratch workspace | all exit 0; `Wrote …/reviews/2026-09-27.md` |
| optional installs (`certifi`, `python-jobspy`, `cloakbrowser`, `playwright` + `python3 -m playwright install chromium`, `pypdf`, poppler `pdftotext`) | PyPI JSON API returned 200 for all five packages; `python3 -m playwright install --help` ok; `pdftotext` on PATH | names correct (nothing installed) |
| `/Applications/Python 3.x/Install Certificates.command` | `ls "/Applications/Python 3.13/"` | present |
| `python3 -m pytest -q -m "not network"` | ran | `403 passed, 3 deselected` |
| `python3 -m pytest -q -m network` | ran | `3 passed, 403 deselected` (test_jobstreet_live, test_mcf_live, test_fetch_posting_live_jobstreet_id) |
| `python3 build.py --check` / `python3 build.py` | ran | `OK: 12 skills pass checks` / `Built …/dist/job-hunting.skill (156996 bytes, 45 files)`; zip has no CRLF in .md/.py; `dist/` gitignored |
| `claude plugin validate .` | ran | see below |
| Python 3.10 claim | `ast.parse(…, feature_version=(3,10))` over every script and `build.py` | all parse |
| Not runnable here | `/job-hunter:*` verbs and `/loop 1d /job-hunter:search` (in-session; checked against the skill files and `references/sourcing.md`); Windows lines (`python build.py`, PowerShell `$env:`/`setx`, symlink-to-copy fallback checked by reading `build.py` `link_skills`) | — |

## `claude plugin validate .`

Before the fix:
```
Validating marketplace manifest: …/.claude-plugin/marketplace.json
⚠ Found 1 warning:
  ❯ description: No marketplace description provided. Adding a description helps users understand what this marketplace offers
✔ Validation passed with warnings
```
After adding the top-level `"description"` (the docs' walkthrough puts it there):
```
Validating marketplace manifest: /Users/snapdec/Documents/workspace/job-hunter/.claude-plugin/marketplace.json

✔ Validation passed
```
`--strict` also passes. `claude plugin validate .claude-plugin/plugin.json` → `✔ Validation passed`.

## Check / test / build (final, at 60ebb4b)

`OK: 12 skills pass checks` · `403 passed, 3 deselected` · `Built dist/job-hunting.skill (156996 bytes, 45 files)` · validate `✔ Validation passed`.

## Self-review

- Every README claim was traced to the code, a `--help`, a skill file or the Claude Code docs. Wording caught and fixed along the way: the resume draft is shown before its audit (only cover letters are gated first); the §9 Answers is a section, not a table; the Q failure covers two things (the references brief and the `withdrawn` commands), not one; `help` prints role/phrase/verb, not the README's five-column table.
- No marketing adjectives. The only statistic is Ashby's, cited as in `networking.md`. No test counts in the README.
- LF only; no XML-like tags outside code spans; the banner line is byte-identical.
- Scope: the only manifest change is the validator-driven description line.

## Concerns

1. **The plain install command fails until v6 is on `main`.** `claude plugin marketplace add cincaoais/job-hunter` clones the default branch, which is still v5 with no `.claude-plugin/`. It works as documented once v6 merges. Until then use `#v6-revamp`.
2. **Stale banner.** The banner kept on line 1 still says "Paused after Task 16 of 17". It is kept as instructed and is removed at release.
3. **`fetch_posting.py` treats a block page as a posting (found while verifying, out of scope).** With cloakbrowser installed, a Glassdoor URL returns exit 0 and writes Glassdoor's "Humans only / Security | Glassdoor" block page as the posting, including the user's IP address. `BLOCK_MARKERS` lacks these markers. Recommend it for the final review.
4. **Windows `python3`.** The skills call `python3`. The README tells users to check it and names the Microsoft Store build, but Windows CI runs only pytest and `--check`, never the inline `python3` commands.
5. **Version is set twice.** It is in both `plugin.json` and the marketplace entry. The docs advise setting it in one place, and `plugin.json` wins silently. Both say 6.0.0, so the validator does not warn. I left it and documented that all three version fields are bumped together.
6. **claude.ai upload path differs from the brief** (see Deviation above).
