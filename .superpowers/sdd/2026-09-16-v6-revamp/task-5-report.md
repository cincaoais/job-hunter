# Task 5 report — SKILL.md rewrite + eleven verb skills

## What I wrote
- `skills/job-hunting/SKILL.md` rewritten from scratch: 127 lines (cap 300/500). Frontmatter `name: job-hunting`, description 1022 chars (≤1024) keeping v5 trigger phrases and adding daily job digest, who to contact for a referral, what should I do today, resignation letter, 30-60-90 days; `metadata.version 6.0.0`, author "Johannes Tang + Claude".
  Sections: Storage modes (workspace vs chat, detection rule, `workspace.py where/init`, in-place edits, `saved:` line, chat-mode regeneration), Memory rules (read first, ingest before asking, grouped questions, echo assumptions, never re-ask, contradictions → conservative, immediate write-back, facts immutable → facts-policy.md), The loop — nine roles (table: #, Role, Triggers when, Say, Reference, Script; markets/<cc>.md note), Sourcing in one breath (search_jobs.py command + fallback ladder), Honesty guardrail (→ facts-policy.md), Principles (original six + referral-before-application, fresh beats broad, ten targeted a week, log every touch), legal line, Closing step per mode.
- Eleven verb skills at `skills/{search,match,resume,cover,network,interview,company,offer,today,review,help}/SKILL.md`, 13–21 lines each, `name` = dir, `disable-model-invocation: true`, `argument-hint` on all except help, `$ARGUMENTS` in the body. `today` and `review` start their body with the inline `!`python3 ${CLAUDE_SKILL_DIR}/../job-hunting/scripts/tracker.py today|funnel`` line. Script paths use `${CLAUDE_SKILL_DIR}/../job-hunting/scripts/...`.
- No links to `tech-role-map.md`, `sea-market-notes.md`, `feature-guide.md` (grep clean). Forward references to Task 10–13 files (`sourcing.md`, `pipeline.md`, `strategy.md`, `networking.md`, `answer-bank.md`, `post-offer.md`, `facts-policy.md`, `markets/<cc>.md`) are intentional per the dispatch.

## Checks
- `python3 build.py --check` → `OK: 12 skills pass checks` (first run flagged description at 1066 chars; trimmed to 1022).
- `python3 -m pytest -q` → 24 passed in 0.20s.
- `file` → LF, UTF-8.

## Commit
- `SKILL.md v6 router (nine roles, storage modes) + verb skills replacing commands` (see git log).

## Self-review
- Every brief item 1–8 present; verb table's role/reference/script mapping matches the brief.
- The `help` skill has no `argument-hint` (none needed).
- The verb skills mention `tracker.py add/set`, `fetch_posting.py`, `build_resume.py`, `ats_check.py`, `search_jobs.py` flags (`--days`, `--markdown`, `--save`, `--posting`, `--lint`, `--slop`, `--docx`, `--pdf --template`) exactly as the plan's later tasks specify; Tasks 7–9, 14–15 must keep those flag names.

## Concerns
- None blocking. The SKILL.md description had to drop the literal phrase "how to get a referral" to fit 1024 chars; "who they should contact for a referral" remains.

## Fix round 1

Findings from review, each with what changed and where (paths relative to repo root):

1. **Feature menu unreachable in chat mode.** `skills/job-hunting/SKILL.md:84-85` — added a router line right after the nine-role table: "If the user asks what this skill can do (\"help\", \"menu\", \"what can you do\"), print the table above (the Say column included) and ask which role they want."

2. **Achievement elicitation dropped.** `skills/job-hunting/SKILL.md:59-64` — added a "Draw out achievements" bullet to Memory rules: ask what *changed* (before/after, time saved, volume, users/people affected, money moved, errors reduced, scope owned), convert duties into scale, and label anything estimated from the user's inputs "(est.)" per `references/facts-policy.md`.

3. **`network` verb cited the wrong tracker command for contacts.** `skills/network/SKILL.md:10,13` — step 1's "list touches due" line no longer invents a `tracker.py contacts` subcommand; it now says to read the contacts table (`contacts.md` in workspace mode) and note due Next-touch dates. Step 4 now cites the ruled command verbatim: `python3 ${CLAUDE_SKILL_DIR}/../job-hunting/scripts/tracker.py contact --name X [--company C --role R --relationship REL --target T --last-touch D --next-touch D --status S --note N]` (upsert by Name+Company) for workspace mode, "edit the contacts table in the profile" for chat mode, and an explicit note that `tracker.py add`/`set` are pipeline-only and must not be used for contacts. For consistency (same wrong command, file already in scope), also fixed `skills/job-hunting/SKILL.md:78` — the Networker row's Script column, from `scripts/tracker.py contacts` to `scripts/tracker.py contact`.

4. **`cover` verb + `ats_check.py --slop`** — no change, per ruling; `skills/cover/SKILL.md` untouched.

Cheap minors:
(a) `skills/job-hunting/SKILL.md:4` — reworded the description to fold in the literal phrases "who should I contact", "30-60-90 plan", "revamp my resume", and "job title" (as "pick a job title"), trimming other wording to land at 1015 chars (≤1024).
(b) `skills/job-hunting/SKILL.md:18-28` — reworded the workspace detection rule: run `workspace.py where`; if the printed path has no `profile.md`, offer `init`; if the user declines, fall back to chat mode for the rest of the session.
(c) `skills/job-hunting/SKILL.md:76` — added "what to learn, recurring skill gaps" to the Qualifier row's triggers.
(d) `skills/job-hunting/SKILL.md:117-118` — reader-side principle now reads "knockout questions → ATS/recruiter search → 6-second skim → hiring manager judging outcomes. Optimize for all four."

### Checks
- `python3 build.py --check` → `OK: 12 skills pass checks`
- `python3 -m pytest -q -m "not network"` → `24 passed in 0.24s`
- Description lengths verified via YAML parse: job-hunting 1015 chars, network 149 chars (unchanged).
- `grep -c $'\r'` on both files → 0 (LF only).
- Final line counts: `skills/job-hunting/SKILL.md` 137 lines, `skills/network/SKILL.md` 13 lines (both < 300).

### Commit
- `SKILL.md: home the menu and achievement elicitation, fix verb script contracts` (7e60a533d83d6b0452ecc4fcd93b6768f5744d09).

## Fix round 2

Re-review flagged one new Important from the round-1 diff:

**`tracker.py contacts` (plural, lists touches due) was dropped.** It is a real planned command (Task 9) and was correct in `skills/network/SKILL.md` step 1 before round 1's change — round 1 over-corrected by removing it while fixing the separate "add/set must not be used for contacts" issue. Restored it:
- `skills/network/SKILL.md:10` — step 1 now reads: workspace mode runs `python3 ${CLAUDE_SKILL_DIR}/../job-hunting/scripts/tracker.py contacts` to list touches due; chat mode falls back to reading the contacts table in the profile. Step 4 is unchanged from round 1 — still cites `tracker.py contact` (singular, upsert) for logging/setting Next touch.
- `skills/job-hunting/SKILL.md:78` — Networker row's Script column changed from `scripts/tracker.py contact` to `scripts/tracker.py contacts / contact`, matching the Operations row's `today / funnel / digest` style (list command / upsert command, both real).

### Checks
- `python3 build.py --check` → `OK: 12 skills pass checks`
- `python3 -m pytest -q -m "not network"` → `24 passed in 0.19s`
- Final line counts unchanged: `skills/job-hunting/SKILL.md` 137 lines, `skills/network/SKILL.md` 13 lines.

### Commit
- `network: list due touches with tracker.py contacts, log with contact` (84b180c72bdbac8ce25d4db61e3e85071041fa24).
