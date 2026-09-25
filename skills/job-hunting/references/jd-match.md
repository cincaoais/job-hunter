# Job-Description Match & Resume Optimizer

Run this when the user shares a job posting (JobStreet, LinkedIn, anywhere)
and wants to know whether they fit or wants their resume tailored to it.
Order: fetch → extract → knockout pre-check → score → legitimacy block →
optimize → record.

## 0. Fetch

- **Workspace mode, a URL given:** run
  `python3 ${CLAUDE_SKILL_DIR}/scripts/fetch_posting.py <url> --save` and
  read the saved `postings/<slug>.md` — score the full posting, never a
  search teaser. Pasted text goes on file the same way:
  `python3 ${CLAUDE_SKILL_DIR}/scripts/fetch_posting.py --stdin --company "<X>" --title "<role>" --save`
  (add `--url <url>` when there is one). Exit 3 means the page is blocked
  — `sourcing.md` §1, rung 4.
- **Chat mode:** work from the pasted text; given only a URL, ask for the
  text rather than claiming the posting was read.

## 1. Extract

From the posting, pull:
- **Required skills** vs **nice-to-have skills** (postings usually separate
  "requirements" from "advantages/plus points" — keep the split).
- **Exact keywords and phrasing** an ATS would filter on.
- **Seniority** signals (title, years asked, scope described).
- **Core responsibilities** — what the job actually is day to day.
- **Hard constraints** if stated: location/onsite, visa/work authorization,
  languages, salary.
- **Who advertised and when** — employer or agency, posted date, salary
  label; the legitimacy block (§2) reads them.
- **Red flags** — checked in the legitimacy block (§2) against
  `sourcing.md` §5.

## 1.5 Knockout pre-check — before any scoring

Knockout questions reject where keywords only rank (`answer-bank.md` §4).
Check every hard constraint the posting states against the profile:

| Check | Profile source | Hard fail when |
|---|---|---|
| Work authorization (pass / visa) | §1 Work authorization; `answers.md` Work authorization | the posting requires a status the user lacks and will not sponsor ("Singapore Citizen / PR only") |
| Location / onsite | §1 Location; §3 Work modality, Open to relocation | onsite or hybrid in a place the user will not work in or move to |
| Years asked | §5 dated roles, summed conservatively (`strategy.md` §3) | the level check reads **reach**; **stretch** is a soft fail |
| Licence / certification | §4 Certifications | a required licence or cert the user does not hold; "preferred" is soft |
| Notice | §1 Availability; `answers.md` Notice period | the posting needs a start sooner than the contractual notice allows (a buyout the contract allows makes it soft — `answer-bank.md` §4) |
| Salary floor | §3 Salary expectation | the posted maximum is below the user's floor |
| Language | §4 Spoken languages | a required language the user does not speak at the stated level |

- Read every ambiguity conservatively (SKILL.md memory rules). If the
  profile line looks stale, echo it and ask before failing the posting.
- **Any hard fail → verdict "skip (knockout: <check>)".** Report any
  legitimacy flag already visible (§2), then stop: no score, no resume
  edits, no pipeline row. If the user corrects the profile, update it and
  re-run the check.
- **Soft fails** — "preferred", "advantage", a stretch on years, a salary
  band that only just reaches the floor — go into the §2 report as
  constraint conflicts.
- **One shot per company** (`sourcing.md` §3) — ignore this posting's own
  row (the Scout may have saved it already). Another row at the same
  company at any stage past `saved` in the current search cycle is a hard
  fail: "skip (knockout: one shot per company)". Another `saved` row at the
  company is a soft note: pick one.

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
- **Constraint conflicts** — every §1.5 soft fail, if any.
- **Overall fit: X/10** with an honest verdict, after the cap rule below:
  **apply** / **apply after edits** / **stretch** (apply, but expect the
  gaps to be probed) / **skip**.

**Legitimacy block** — reported on its own, never averaged into Fit:

| Check | Finding |
|---|---|
| Ghost-job and scam signals (`sourcing.md` §5) | each hit, or "none" |
| Repost age | posted date and age; a repost under the `sourcing.md` §3 rule is a flag |
| Salary reliability, by advertiser | see below |

Salary reliability is practice, not data: an employer's own posted band
(MyCareersFuture min/max, a JobStreet salary label on a direct ad) is that
employer's band for the role; an agency's figure is indicative until the
agency confirms it is the client's band; no figure, or "competitive",
means unknown — check the sources in `markets/<cc>.md` §3 before the
screen. A figure that trips a `sourcing.md` §5 scam signal is a flag, not
a salary.

**Cap rule:** any legitimacy red flag caps the verdict at **stretch**,
however high the fit — name the flag that capped it. A scam signal goes
further: skip, and keep it off the shortlist (`sourcing.md` §5).

## 3. Optimize — truthfully

Propose specific resume edits, each traceable to real experience:
- **Reword** bullets to mirror the posting's exact phrasing (their "CI/CD",
  not your "build pipelines").
- **Reorder** so the wins this posting cares about come first.
- **Cut** content this posting doesn't care about.
- A real gap is never closed by wording: no adding skills, metrics, or
  titles the user doesn't have. Gaps get addressed by learning, or framed
  honestly in the cover letter — not keyword-stuffed.

**Literal-term mirror list** — the 8–12 exact terms a recruiter's Boolean
search for this role would use: title variants, core tools, certifications,
domain nouns (`"backend engineer" AND (Go OR Golang) AND PostgreSQL`).
List only terms the user genuinely has; each appears verbatim in the resume
and on LinkedIn (headline, skills, experience — `profile-optimizer.md` §2).
A term the user lacks stays under Real gaps.

Show the edits as before → after pairs. Then offer to regenerate the
tailored resume via `references/resume-builder.md`, and record the posting
(§5).

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
   goals and artifacts into the profile (the §9 "Soft skills development"
   table for soft skills, a learning-goals note under §8 for technical
   ones) and end with the closing step for the storage mode (SKILL.md).

A gap closes by learning and proof, never by wording — the heatmap becomes
resume content only once the artifact exists (`facts-policy.md`).

## 5. Record

Record every posting the user will pursue — any verdict except skip.

- **Workspace mode:** the posting is already in `postings/` (§0). Add the
  row:
  `python3 ${CLAUDE_SKILL_DIR}/scripts/tracker.py add --company "<X>" --role "<Y>" --stage saved --source <board or page> --url <url>`
  and set its Next action and Due in the same call (`--next "…" --due
  YYYY-MM-DD`, `pipeline.md` §2); put the verdict in `--notes` ("fit 7/10,
  stretch: repost 45 days").
- **Chat mode:** add the same row to the profile §9 Pipeline table (Stage
  `saved`, URL and verdict in Notes).
- Then the closing step for the storage mode (SKILL.md).
