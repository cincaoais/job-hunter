---
name: resume
description: Tailor a resume to a posting, or revamp and HR-score the whole resume; generates ATS .docx and presentation PDF and runs the ATS check. Runs the job-hunting skill's Writer role.
argument-hint: [tailor to <posting> | revamp | score]
disable-model-invocation: true
---

Use the `job-hunting` skill, role **Writer**. Request: $ARGUMENTS

1. Resolve storage mode (workspace: `python3 ${CLAUDE_SKILL_DIR}/../job-hunting/scripts/workspace.py where`); read the profile first; apply `references/facts-policy.md` to every claim.
2. Pick the path (ask if unclear): **revamp / score** → `references/resume-revamp.md`; **tailor to a posting** → `references/resume-builder.md` (run the Qualifier first if no match report exists).
3. Draft inline first. On approval, save the variant as `resumes/<company>-<role>-vN.md` (workspace mode) before anything is built; then claims audit, anti-slop gate and 6-second lint per the builder; then in workspace mode `python3 ${CLAUDE_SKILL_DIR}/../job-hunting/scripts/build_resume.py resumes/<file>.md --docx [--pdf --template <name>]` and `python3 ${CLAUDE_SKILL_DIR}/../job-hunting/scripts/ats_check.py <file> --posting postings/<slug>.md --lint --slop --text`. Chat mode: use the document skills and declare the check's fallback.
4. Record the variant sent: `python3 ${CLAUDE_SKILL_DIR}/../job-hunting/scripts/tracker.py set --company <X> --resume <file>`.
