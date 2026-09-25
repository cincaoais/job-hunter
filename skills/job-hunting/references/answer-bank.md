# Answer bank — screening answers for the Writer

The questions every form asks — salary, notice, work pass, why us, why
leaving — answered once, truthfully and per market, then tailored per
posting. This is the honest substitute for auto-apply: the skill drafts,
the user submits. Every answer follows `facts-policy.md`.

## 1. Where the answers live

- Workspace mode: `answers.md` (created from `assets/answers-template.md`).
- Chat mode: the `### Answers` section in profile §9
  (`candidate-profile.md`), with the same headings.
- Each answer traces to a profile line: salary → profile §3, notice and
  work authorization → profile §1, relocation → profile §3, years and
  stories → profile §5. On a conflict the profile wins; ask which is
  current.

## 2. Intake — fill it in one batch

Pre-fill what the profile answers, echo it in one line, and ask only the
gaps, with options to pick:

| Heading in `answers.md` | Source, or the question to ask | Differs per market? |
|---|---|---|
| Expected salary | profile §3 range → "the single number you'd say out loud?" | yes — currency and the market's quoting norm |
| Notice period / earliest start | contract notice; probation or confirmed? | no |
| Work authorization | citizen / PR / pass held (valid until) / sponsorship needed | yes — one row per country |
| Why this company | a reusable pattern; the hook is filled per posting (§3) | — |
| Why leaving (current/last role) | one forward-looking, true sentence | no |
| Relocation | profile §3 Open to relocation | yes |
| Years in each tool / skill | profile §5 dated roles that used it; overlaps count once | no |
| STAR stories | at least three titles, one line each, from profile §5 | no |
| Essay prompts | "greatest achievement", "why you" — built from the STAR titles | — |
| References | names and permission (`post-offer.md` §5) | no |

Salary numbers come from the user's profile §3 range checked against live
market sources in `markets/<cc>.md` — never from memory.

## 3. Tailor per posting

- Read the saved posting (`postings/<slug>.md`, or the pasted text) and the
  dossier (`dossiers/<company>.md`) first.
- **Why us must cite one company fact** from the posting or the dossier —
  a product, team, stack or market move. No fact → no answer: ask the user,
  or build the dossier (`company-dossier.md`).
- **Why leaving**: the same true sentence every time — interviews test
  consistency; never criticise the employer.
- **Years**: answer the exact question ("years of Python" → the profile §5
  roles that used Python), rounded down.
- **Salary**: the single number for that market; a range only where free
  text allows.
- Respect field limits; plain text, no formatting, paste-ready.
- Log what was stated so the offer stage matches:
  `python3 ${CLAUDE_SKILL_DIR}/scripts/tracker.py set --company "X" --note "answers: [salary]; notice [n]"`
  (chat mode: the pipeline row's Notes).

## 4. Knockout questions — answer honestly

ATS systems rank rather than auto-reject on keywords (92% of surveyed
recruiters configure no content-based auto-reject), but knockout questions
— work pass, location, years, licence, notice — do reject
(Hiration/Huntr). A false "yes" clears the form and fails at the screen or
the background check.

- The honest answer is a knockout → skip the posting (`jd-match.md`), or,
  where the form allows detail, give the true fact and the real
  mitigation ("1 month notice; buyout possible" — only when the contract
  allows it, `post-offer.md` §3).
- Work authorization: exactly as `answers.md` states it. Non-citizens in
  SG check Employment Pass viability per role first (`markets/sg.md`).
- Notice: the contractual notice, never a shorter one the user hopes to
  negotiate; a possible buyout goes in the detail field, not the number.
- Location / onsite: the profile §3 modality; never a "yes" to relocation
  the profile does not support.
- NRIC/IC numbers go only into an official identity step after an offer,
  never a screening field (`markets/my.md`, `markets/sg.md`).

## 5. Form mechanics

| Form | What to do |
|---|---|
| Workday | Expect an account per employer. The resume parse pre-fills fields — check every parsed title and date against the profile before saving. Paste answers as plain text. |
| Greenhouse / Lever | One page; custom questions follow the standard fields. Optional fields stay optional; voluntary demographic questions are the user's call. |
| JobStreet (MY / SG) | The expected-salary field takes **one number**: set it near the bottom of the true range so band-matching does not exclude the user; add "(negotiable)" where free text allows; leave it blank when optional and the user prefers (`markets/my.md`). seekAI ranks applicants on resume + JD + the employer's past behaviour, and profile completeness feeds its approachability signal — keep the profile complete (`profile-optimizer.md`). |
| MyCareersFuture | Workspace mode: `python3 ${CLAUDE_SKILL_DIR}/scripts/fetch_posting.py <url> --save` writes the employer's questions to `screening_questions:` in the posting's frontmatter — answer each from `answers.md`, in order, before applying. The posted min/max band sanity-checks the salary number. Chat mode: ask the user to paste the questions from the apply page. |
| LinkedIn Easy Apply | Prefer the direct posting (`sourcing.md` §4); if Easy Apply is the only route, reuse the same answers. |

## 6. Never auto-submit

The skill drafts; the user reviews, pastes and presses submit. No logging
in to boards, no form-filling, no submitting on the user's behalf. In chat
mode never claim a posting was fetched or a form was read — ask for the
paste.

## 7. Keep it current

- Profile §1 or profile §3 changes (salary, availability, work
  authorization, relocation, modality) → update the answers in the same
  session and say which ones changed.
- A new market → add a row to each per-market table.
- Before each use, echo the load-bearing answers in one line ("RM [n],
  1 month notice, Malaysian citizen — still right?").
- Workspace mode: edit `answers.md` in place and name it in the `saved:`
  line. Chat mode: regenerate the profile block.
