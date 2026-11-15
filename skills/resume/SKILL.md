---
name: resume
description: Tailor a resume to a posting, revamp and HR-score the whole resume, or (with `cover`) write a cover letter, outreach note or screening answers. Builds the ATS .docx and presentation PDF and runs the ATS check. Runs the job-hunting skill's Writer role.
argument-hint: [tailor <posting> | revamp | score | cover <company/role>]
disable-model-invocation: true
---

Use the `job-hunting` skill, role **Writer**. Request: $ARGUMENTS

1. Run `sh ${CLAUDE_SKILL_DIR}/../job-hunting/scripts/jh workspace.py where`; read `profile.md` (and `answers.md` for cover letters) first; apply `${CLAUDE_SKILL_DIR}/../job-hunting/references/facts-policy.md` to every claim.
2. Pick the path (ask if unclear): **revamp / score** → `${CLAUDE_SKILL_DIR}/../job-hunting/references/resume-revamp.md`; **tailor** → `${CLAUDE_SKILL_DIR}/../job-hunting/references/resume-builder.md` (run `/job-hunter:match` first if no match report exists); **cover** → `${CLAUDE_SKILL_DIR}/../job-hunting/references/resume-builder.md` "Cover letters" + `${CLAUDE_SKILL_DIR}/../job-hunting/references/answer-bank.md`.
3. Resume path, in this order: draft inline → reviewer pass (fresh-context read-only subagent with the posting and the draft inline; revise on its findings) → on approval save `resumes/<company>-<role>-vN.md` → claims audit, anti-slop gate and 6-second lint on that saved markdown (per the builder; a hit means edit the .md and re-run) → build with `sh ${CLAUDE_SKILL_DIR}/../job-hunting/scripts/jh build_resume.py resumes/<file>.md --docx [--pdf --template <name>]` → `sh ${CLAUDE_SKILL_DIR}/../job-hunting/scripts/jh ats_check.py <file> --posting postings/<slug>.md --lint --slop --text` on the built file as the final check. Record the variant with `sh ${CLAUDE_SKILL_DIR}/../job-hunting/scripts/jh tracker.py set --company <X> --role <Y> --resume <file>`.
4. Cover path: if no company or posting is named, ask which job this is for. Anti-slop gate before drafting: one user-supplied story (offer options from the profile's evidence) and one company-specific fact (dossier or posting) — no story or no fact → no letter. Draft in the Application Guide's four beats and save as `letters/<company>-<role>-vN.md`; then a reviewer pass (fresh-context read-only subagent with the posting and the letter inline; revise on its findings); then the claims audit and `sh ${CLAUDE_SKILL_DIR}/../job-hunting/scripts/jh ats_check.py <file> --slop`, replacing every hit — all before the user sees it. Show it inline with the one-line audit result and the scan result; iterating overwrites the same file and re-runs both gates; log the touch in the pipeline.
5. End with the `saved:` line (SKILL.md closing step).
