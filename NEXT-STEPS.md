# Next Steps — pick up here on Windows

> Written 2026-07-16 on the Mac, right after shipping v5.2. Delete this file
> once everything below is done.

## Where things stand

- **v5.2 shipped.** Three new modules under `job-hunting/references/`:
  **offer-coach** (true-annual-comp normalization, offer comparison,
  negotiation scripts, mock negotiation), **company-dossier** (cited
  pre-interview research brief), **profile-optimizer** (LinkedIn/JobStreet
  tuning for recruiter search). All wired into SKILL.md; the profile
  template gained an **Offers table under §9**.
- **Tests: 8/8 cumulative** — A–E (5/5, v5.1) plus new F–H (3/3, v5.2, one
  hardening fix to the profile-optimizer intake).
- **Package rebuilt and committed**: `job-hunting.skill` at commit
  `410d7ba` (design spec in `d688c85`).
- **No git remote** — this repo exists only on machines you copy it to.

## Do on Windows

1. [ ] Get this repo (or at least `job-hunting.skill` +
   `PROJECT-DESCRIPTION.md`) onto the machine — copy the folder, or set up
   a private GitHub remote first and clone.
2. [ ] claude.ai → **Settings → Features** → replace the old skill with the
   new `job-hunting.skill`. Until then claude.ai still runs v5.1.
3. [ ] Job Hunting HQ Project → project settings → paste the **updated**
   `PROJECT-DESCRIPTION.md` contents into custom instructions (it now
   mentions dossiers, profile tuning, and offer negotiation).
4. [ ] First real run — the tests used a fictional candidate, so validate
   on your real search: ask for a **company dossier** before your next
   interview, run the **profile optimizer** on your actual LinkedIn
   headline/About, and when an offer arrives, paste the letter for the
   **offer coach**.
5. [ ] Optional: create a private GitHub repo and push, so the Mac and
   Windows copies stay in sync.

## Notes

- Rebuild on Windows with `build.cmd` (uses Windows' bundled tar.exe);
  `./build.sh` on macOS/Linux. Always rebuild after editing anything under
  `job-hunting/`.
- Your `candidate-profile.md` in the Project picks up the new §9 Offers
  table automatically the first time a session regenerates the profile —
  no manual edit needed.
