# Claude Code integration

Slash-command launchers for the `job-hunting` skill, so you can drive the whole
job hunt from Claude Code. Each command in `commands/` is a thin wrapper that
routes into the skill — no feature logic is duplicated here; the skill and its
`references/` own that.

## Commands

Type `/job` in Claude Code to see them all.

| Command | What it does |
|---|---|
| `/job-help` | Show the full feature menu, then pick one. The "what can this do again?" entry. |
| `/job-guide` | Guided, one-step-at-a-time walk through the whole hunt. |
| `/job-search` | Ranked shortlist of live openings from your saved criteria. |
| `/job-match` | Paste a posting → fit scorecard + honest apply/stretch/skip verdict. |
| `/job-resume` | Revamp & HR-eye score, or tailor your resume for a posting. |
| `/job-cover` | Draft/refine a tailored cover letter or outreach note. |
| `/job-interview` | Interview prep pack for a round, or a live mock. |
| `/job-company` | One-page cited company dossier before an interview. |
| `/job-offer` | Normalize comp, compare, and negotiate an offer. |

Everything without its own command (soft-skills coach, profile optimizer, funnel
review, networking, Reactive Resume handoff) is reachable via `/job-help` or
plain English.

## Install / redeploy

The skill and commands are installed to your **user** Claude Code scope
(`~/.claude/skills/job-hunting/` and `~/.claude/commands/`) so they work in every
session, anywhere. After editing anything under `job-hunting/` or
`commands/`, redeploy:

```
deploy-cc.cmd     # Windows
./deploy-cc.sh    # macOS / Linux
```

Then restart Claude Code so it re-reads the commands and skill.

## Where's my candidate profile?

The skill reads a `candidate-profile.md` as its single source of truth. In Claude
Code there's no claude.ai Project, so keep your filled-in profile in the folder
you run Claude Code from (or hand it to the skill in the conversation). If none
exists, `/job-guide` will start one from the bundled template.
