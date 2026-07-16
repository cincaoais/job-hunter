# job-hunter

A Claude skill that acts as a personal job-search agent and career coach for
tech roles: positioning, finding live openings, resume/cover-letter tailoring,
networking, interview prep, and pipeline tracking. Built for a Southeast Asia
job market (JobStreet + LinkedIn first), not US-only conventions.

Capabilities (v5.0):

- **Criteria-driven job search** — queries built from saved search criteria,
  hard-filtered, returned as a ranked shortlist with fit scores and red flags
  (ghost-job/scam checks included).
- **Resume & cover-letter builder** (`references/resume-builder.md`) — gap
  questions → inline draft → approved ATS-safe .docx/PDF, with two bundled
  resume blueprints.
- **JD match & optimizer** (`references/jd-match.md`) — paste a posting, get
  a match report (table, missing keywords, real gaps, honest fit verdict)
  and truthful resume edits.
- **Soft skills coach** (`references/soft-skills-coach.md`) — demand-vs-
  supply gap assessment, small practice plans, evidence turned into bullets
  and STAR stories.
- **Interactive by design** — grouped clarifying questions before every
  task; every answer written back to the candidate profile so nothing is
  asked twice. Honesty guardrail throughout: never invents achievements,
  metrics, or titles.

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
./build.sh
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
