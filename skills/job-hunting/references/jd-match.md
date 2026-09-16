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

## 4. Upskill review — cross-posting mode

Run this when the user asks what to learn ("what should I study to land
these roles?", career planning between applications) or when the same ✗/~
keeps recurring across match reports. One posting tells you about that job;
the pattern across postings tells you what the market is pricing.

1. **Gather requirements** from every posting the user is actually
   targeting: pipeline entries, recent match reports, current shortlist. If
   fewer than ~3 postings are on hand, ask the user to paste 2–3
   representative ones — a heatmap from one JD is just a match report.
2. **Aggregate into a heatmap** — one row per skill the postings ask for
   that the profile lacks (✗) or only partially covers (~):

   | Skill | Asked by (n of postings) | Status | Priority |

   Priority weighs how many postings ask for it, ✗ over ~, and how central
   it is to the target role — a skill every posting requires outranks one
   nice-to-have mention. Skills the profile already covers stay out; this
   is a gap map, not an inventory.
3. **Learning plan for the top 2–4 only** (a ten-item plan is a wish list).
   Per skill: live-searched resources (course, docs, a build-something
   project — cited, not from memory), a realistic time estimate at the
   user's stated pace, and the **provable artifact** that ends the plan — a
   cert, a shipped repo, production use — because that artifact is what
   becomes a truthful resume bullet later.
4. **Route and record.** Soft-skill gaps — mentoring, stakeholder
   communication, and similar people skills, wherever the posting lists
   them — go to `references/soft-skills-coach.md`, not this heatmap. Write the chosen
   goals and artifacts into the profile (§10 table for soft skills, a
   learning-goals note under §8 for technical ones) and close with the
   Step 0 profile regeneration.

Honesty rule unchanged: a gap is closed by learning and proof, never by
wording. The heatmap never becomes resume content until the artifact exists.
