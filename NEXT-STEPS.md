# Next Steps — pick up here on Windows

> Written 2026-07-16 on the Mac, right after shipping v5.2. Delete this file
> once everything below is done.

## Where things stand

- **v5.3 shipped (2026-07-17)**, on top of v5.2. Ports from
  MadsLorentzen/ai-job-search (plan:
  `docs/superpowers/specs/2026-07-17-v5.3-ai-job-search-port-plan.md`):
  **referral people-search links** on the job-search shortlist,
  **reviewer pass** + **ATS text-layer check** in the resume builder, and a
  cross-posting **upskill review** (gap heatmap + learning plan) in
  jd-match. v5.2 had added offer-coach, company-dossier, and
  profile-optimizer.
- **Tests: 11/11 cumulative** — A–E (5/5, v5.1), F–H (3/3, v5.2), I–K
  (3/3, v5.3, one hardening fix to jd-match's soft-skill routing).
- **Package rebuilt and committed**: `job-hunting.skill` (v5.3).
- A local scrape rig (clone of ai-job-search) also lives at
  `~/ai-job-search` on the Mac — separate from this repo; run `/setup`
  there once before using its `/scrape`.
- **Remote:** `git@github.com:cincaoais/job-hunter.git` (private). Mac
  history force-pushed over the stale "Initial Commit" on 2026-07-17 —
  pull, don't copy folders anymore.

## Do on Windows

1. [ ] Get the repo: fresh machine →
   `git clone git@github.com:cincaoais/job-hunter.git`; existing copy →
   `git fetch origin && git reset --hard origin/main` **once** (the old
   copy shares no history with the remote; this discards local Windows
   changes). After that, `git pull --rebase origin main` works normally.
   Needs an SSH key for the GitHub account on that machine.
2. [ ] claude.ai → **Settings → Features** → replace the old skill with the
   new `job-hunting.skill` (now v5.3). Until then claude.ai still runs v5.1.
3. [ ] Job Hunting HQ Project → project settings → paste the **updated**
   `PROJECT-DESCRIPTION.md` contents into custom instructions (it now
   mentions dossiers, profile tuning, offer negotiation, and the upskill
   learning plan).
4. [ ] First real run — the tests used a fictional candidate, so validate
   on your real search: ask for a **company dossier** before your next
   interview, run the **profile optimizer** on your actual LinkedIn
   headline/About, and when an offer arrives, paste the letter for the
   **offer coach**.

## Notes

- Rebuild on Windows with `build.cmd` (uses Windows' bundled tar.exe);
  `./build.sh` on macOS/Linux. Always rebuild after editing anything under
  `job-hunting/`.
- Your `candidate-profile.md` in the Project picks up the new §9 Offers
  table automatically the first time a session regenerates the profile —
  no manual edit needed.
