# Job-Description Match & Resume Optimizer

Run this when the user shares a job posting (JobStreet, LinkedIn, anywhere)
and wants to know whether they fit or wants their resume tailored to it.

## 1. Extract

From the posting, pull:
- **Required skills** vs **nice-to-have skills** (postings usually separate
  "requirements" from "advantages/plus points" — keep the split).
- **Exact keywords and phrasing** an ATS would filter on.
- **Seniority** signals (title, years asked, scope described).
- **Core responsibilities** — what the job actually is day to day.
- **Hard constraints** if stated: location/onsite, visa/work authorization,
  languages, salary.
- **Red flags**, using the ghost-job/scam rules in SKILL.md.

## 2. Score

Compare the extraction against the candidate profile (and current resume, if
one exists). Report as:

| Requirement | Status | Evidence from profile |
|-------------|--------|-----------------------|
| ...         | ✓ / ~ / ✗ | the specific experience, or "—" |

(✓ have it, ~ partial/adjacent, ✗ missing.)

Then three lists and a verdict:
- **Missing keywords** — things the user *has* but the resume doesn't say in
  the posting's words. These are free wins.
- **Real gaps** — requirements the user doesn't meet. Say so plainly;
  flattery costs interviews.
- **Constraint conflicts** — location, visa, salary mismatches, if any.
- **Overall fit: X/10** with an honest verdict: **apply** / **apply after
  edits** / **stretch** (apply, but expect the gaps to be probed) / **skip**.

## 3. Optimize — truthfully

Propose specific resume edits, each traceable to real experience:
- **Reword** bullets to mirror the posting's exact phrasing (their "CI/CD",
  not your "build pipelines").
- **Reorder** so the wins this posting cares about come first.
- **Cut** content this posting doesn't care about.
- A real gap is never closed by wording: no adding skills, metrics, or
  titles the user doesn't have. Gaps get addressed by learning, or framed
  honestly in the cover letter — not keyword-stuffed.

Show the edits as before → after pairs. Then offer to regenerate the
tailored resume via `references/resume-builder.md`, and record the posting
and outcome in the profile's pipeline tracker.
