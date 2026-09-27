> **Work in progress — v6 revamp on branch `v6-revamp`.** Paused after Task 16 of 17 on 2026-09-27. To resume on any machine, read [`docs/handoff/HANDOFF.md`](docs/handoff/HANDOFF.md) first. This banner is removed when v6 merges.

# job-hunter

A Claude skill that acts as a personal job-search agent and career coach for
tech roles: positioning, finding live openings, resume/cover-letter tailoring,
networking, interview prep, and pipeline tracking. Built for a Southeast Asia
job market (JobStreet + LinkedIn first), not US-only conventions.

Capabilities (v5.3):

- **Criteria-driven job search** — queries built from saved search criteria,
  hard-filtered, returned as a ranked shortlist with fit scores and red flags
  (ghost-job/scam checks included), plus LinkedIn people-search referral
  links per high-fit entry.
- **Resume & cover-letter builder** (`references/resume-builder.md`) — gap
  questions → inline draft → reviewer pass → approved ATS-safe .docx/PDF
  (two bundled blueprints), verified by an ATS text-layer check on the
  generated file.
- **JD match & optimizer** (`references/jd-match.md`) — paste a posting, get
  a match report (table, missing keywords, real gaps, honest fit verdict)
  and truthful resume edits; cross-posting upskill review turns recurring
  gaps into a heatmap and a prioritized learning plan.
- **Soft skills coach** (`references/soft-skills-coach.md`) — demand-vs-
  supply gap assessment, small practice plans, evidence turned into bullets
  and STAR stories.
- **Interview coach** (`references/interview-coach.md`) — mock interviews
  one question at a time with real-interviewer probing, honest scoring, and
  a debrief that files STAR stories into the profile.
- **Company dossier** (`references/company-dossier.md`) — one-page
  pre-interview brief: product, health, stack, comp intel, likely themes,
  and researched questions to ask — live-searched and cited.
- **Offer coach** (`references/offer-coach.md`) — true-annual-comp
  normalization (contractual vs discretionary 13th month/AWS), side-by-side
  offer comparison, negotiation scripts, and a mock-negotiation loop.
- **Profile optimizer** (`references/profile-optimizer.md`) —
  LinkedIn/JobStreet tuning for recruiter search: keyword-first headline,
  About hook, skills order, and platform settings.
- **Funnel review** — periodic sent→response→interview→offer analysis by
  channel, with one concrete change per review.
- **Market notes** (`references/markets/`: `my.md`, `sg.md`, `_template.md`)
  — JobStreet salary field mechanics, probation/notice/13th-month norms,
  statutory floors, and per-country board guides for MY/SG (+PH/ID/VN).
- **Feature menu** (`/job-hunter:help`, or the role table in the
  job-hunting `SKILL.md`) — say "help", "menu", or "what can you do" to get
  a one-table guide to every capability with example prompts.
- **Interactive by design** — grouped clarifying questions before every
  task; every answer written back to the candidate profile so nothing is
  asked twice. Honesty guardrail throughout: never invents achievements,
  metrics, or titles.

Behavioral tests live in `tests/` (fixtures + scenario checklists, run as
simulated sessions against the packaged skill — 11/11 cumulative: A–E 5/5 on
v5.1, F–H 3/3 on v5.2, I–K 3/3 on v5.3).

## Layout

| Path | What it is |
|---|---|
| `job-hunting/` | The skill source — `SKILL.md` plus bundled `references/` and `assets/`. This directory is zipped as-is into the package. Edit files here only. |
| `job-hunting.skill` | The built package (a zip of `job-hunting/`). Never edit by hand — rebuild it. |
| `PROJECT-DESCRIPTION.md` | Custom instructions to paste into a Claude Project ("Job Hunting HQ") that uses this skill. |
| `build.sh` | Rebuilds the package. |

## Install the skill in Claude

1. Build (or use the committed) `job-hunting.skill`.
2. In claude.ai: **Settings → Features → upload the .skill file**.
3. Optional but recommended: create a Project, paste `PROJECT-DESCRIPTION.md`'s
   contents into its custom instructions, and keep your filled-in
   `candidate-profile.md` in the Project's knowledge files.

## Rebuild the package

```sh
./build.sh    # macOS / Linux
build.cmd     # Windows (uses the tar.exe bundled with Windows 10+)
```

Zips `job-hunting/` into `job-hunting.skill`. Always rebuild after editing
anything under `job-hunting/` — the package is a build artifact, not a second
copy to maintain.

## How the pieces relate

- The **skill package** bundles all reference docs (Application Guide, Tech
  Role Map, resume builder, JD match, soft-skills coach) and the blank
  candidate-profile template, so it works standalone.
- The **Project** holds your personal `candidate-profile.md` (the skill's
  memory of you). If the Project also contains a copy of any reference doc,
  that copy takes precedence over the bundled one.
