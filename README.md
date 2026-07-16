# job-hunter

A Claude skill that acts as a personal job-search agent and career coach for
tech roles: positioning, finding live openings, resume/cover-letter tailoring,
networking, interview prep, and pipeline tracking. Built for a Southeast Asia
job market (JobStreet + LinkedIn first), not US-only conventions.

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

- The **skill package** bundles the Application Guide, Tech Role Map, and the
  blank candidate-profile template, so it works standalone.
- The **Project** holds your personal `candidate-profile.md` (the skill's
  memory of you). If the Project also contains copies of the guide/map, those
  take precedence over the bundled ones.
