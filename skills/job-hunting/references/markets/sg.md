# Singapore (SG) — market notes

Compiled 2026-09; statutory figures drift — re-verify any number before quoting it precisely.

Headings follow `markets/_template.md`. Unmarked facts carry over from the
July 2026 notes or come from the 2026-09 compilation; named sources are in
parentheses. Visa, contract or legal questions: general information, then
suggest a qualified professional (SKILL.md).

## 1. Boards & channels

**Market pulse**: Q3 2026 Net Employment Outlook +13%, the weakest since
2021; 22% of employers plan cuts (ManpowerGroup via HRO, 2026). Expect
slower processes and keep the pipeline wide.

| Channel | Tier | Use it for | `search_jobs.py` source |
|---|---|---|---|
| JobStreet | volume | All-rounder; the default apply channel | `jobstreet` |
| MyCareersFuture (MCF) | government | Government portal with real volume; posted min/max band on every posting, employer screening questions on some | `mcf` |
| LinkedIn | mid-senior | Mid-senior roles, networking, recruiter sourcing | `linkedin` (guest search) |
| NodeFlair | niche | Tech roles, with salary data | — (scoped web search) |
| Glints | niche | Tech and startup roles | — (scoped web search) |
| Indeed | volume | Aggregator | `indeed` (needs `python-jobspy`) |

- **MCF reach**: used by ~1 in 3 fresh graduates and young PMETs; ~6 in 10
  found jobs within six months (MOM PQ reply, Sep 2025).
- **Fair Consideration Framework**: a job ad must be live on MCF for at
  least 14 days before the employer applies for an Employment Pass
  (2026-09 notes — verify). Most roles an employer may fill with an EP
  holder therefore surface on MCF — exemptions exist (small firms,
  high-salary and short-term roles, intra-corporate transferees) — so
  search it even when the role is also on LinkedIn.
- **JobStreet vs LinkedIn**: the MY split holds — JobStreet to apply,
  LinkedIn for mid-senior roles, sourcing and referrals (`networking.md`).
- **SkillsFuture Jobseeker Support**: up to S$6,000 over 6 months for
  involuntarily unemployed citizens (PRs from Q1 2026), points-based on
  job-search activity (2026-09 notes — verify). Check eligibility first —
  the scheme has prior-income and housing caps. Then log every application,
  touch and interview: the tracker doubles as the activity evidence
  (`pipeline.md`; chat mode: profile §9).

## 2. Agencies

- **Go direct first**: agency postings fell 18% while direct employers held
  flat (ManpowerGroup via HRO, 2026).
- Robert Walters, Michael Page, Hays, Randstad, JAC Recruitment,
  PERSOLKELLY, Reeracoen — the regional agencies of `markets/my.md` §2;
  confirm each one's Singapore desk for the user's field.
- Ask them for contract and contract-to-perm roles as well — the runway
  lever in `pipeline.md` §6 when runway is under 3 months.
- How to work with them — exclusivity, salary disclosure, counter-offers,
  WhatsApp: `networking.md` §6.

## 3. Salary sources

| Source | Use it for |
|---|---|
| MCF posted band | Min/max on every posting — the employer's own band for that role |
| NodeFlair | Tech salaries, free |
| Levels.fyi (Singapore) | Tech total comp by company and level |
| Glassdoor | Company-level reports; small samples — treat as anecdote |
| Agency salary guides — Hays Asia Salary Guide 2026, Robert Walters Salary Survey 2026, Michael Page Salary Guide 2026 | The Singapore tables for the role and level |

Search live for role, level and city and cite it; never quote a range
from memory (`offer-coach.md` §3).

## 4. Resume conventions

| Item | Norm |
|---|---|
| Length | 1–2 pages |
| NRIC | **Never** on a CV |
| Work status | State it instead: "Singapore Citizen", "PR", "EP holder valid until [date]" (§9) |
| Expected salary | Only if the ad asks; then a range plus "(negotiable)" |
| Photo | A mixed norm: skip for Western MNCs and tech, harmless at local or traditional firms — default no per the photo decision matrix (`resume-revamp.md` Step 3) |

## 5. Application form norms

- **MCF**: fetch the posting to get any employer screening questions and
  answer each from `answers.md`, in order; the posted band sanity-checks
  the salary number (`answer-bank.md` §5).
- **JobStreet SG**: the same SEEK engine as Malaysia; the expected-salary
  field takes one number — near the bottom of the true range, plus
  "(negotiable)" where free text allows (mechanics: `markets/my.md` §5).
- **Work-pass questions** (citizen / PR / sponsorship needed) are
  knockouts: answer exactly as `answers.md` states them; a false "yes"
  fails at the pass application (`answer-bank.md` §4).
- **NRIC**: never in a screening field; only in the employer's official
  onboarding step after an offer (`answer-bank.md` §4).
- Current-salary questions: `facts-policy.md` §6.

## 6. Statutory floors

| Item | Floor |
|---|---|
| Minimum wage | No general minimum wage — sectoral Progressive Wage Model only (2026-09 notes — verify). Never call an SG offer "below floor" on pay alone |
| Hours and overtime | The Employment Act's hours and overtime part covers lower-paid staff only (2026-09 notes — verify) — look up the current MOM thresholds |
| Annual, sick and parental leave | Not in the compiled notes — look up the current MOM figures |
| CPF eligibility | Singapore Citizens and PRs only — EP/S Pass holders have no CPF (CPF Board; Vialto, verified 2026-09-25). From day one, probation included; rates vary by age — use the CPF Board's current table |
| CPF wage ceilings | Ordinary Wage (OW) ceiling S$8,000/month from 1 Jan 2026 (S$7,400 in 2025) — it caps monthly CPF on base pay too; annual salary ceiling S$102,000, unchanged; Additional Wage ceiling = S$102,000 − total OW subject to CPF for the year (CPF Board; Vialto, verified 2026-09-25) |
| Written terms | Key Employment Terms (KETs); probation terms must appear in them |

**Contract red flags** — the Malaysian list applies here too
(`markets/my.md` §6), plus: CPF missing from the payslip of a citizen or
PR; probation or notice terms absent from the KETs; notice far longer than
the role's level (TAFEP flags long notice for junior roles as unfair
practice).

## 7. Probation & notice

- **Probation**: not regulated by the Employment Act; 3 months standard, 6
  for senior roles; terms must appear in the KETs. CPF (citizens and PRs)
  applies during probation as after it.
- **Confirmation** is documented through the KETs and the contract: ask HR
  at offer stage how confirmation is notified and get it in writing
  (`post-offer.md` §1, §8).

| Situation | Notice |
|---|---|
| During probation — typical contract | 1–2 weeks |
| Confirmed — typical contract | ~1 month; 1–3 months range, longer for senior roles |
| Contract silent — Employment Act default | Scales with tenure, 1 day → 4 weeks |

- The contract governs; buyout, leave and handover: `post-offer.md` §3.

## 8. 13th month / bonus wording

- **AWS** (Annual Wage Supplement, the 13th month): not mandatory;
  typically one month's basic salary paid in Nov/Dec; binding once it is
  in the contract.
- Offer cue: a contractual AWS is real pay; a bonus "discretionary /
  subject to performance" counts only as a labelled estimate in true
  annual comp (`offer-coach.md` §2).
- For citizens and PRs, CPF on AWS and bonuses stops at the Additional
  Wage ceiling — S$102,000 minus the year's OW subject to CPF — and CPF on
  base pay stops at the OW ceiling (§6). It matters when comparing
  packages with a high base or a large bonus.

## 9. Work authorization signals

- Work-status wording for the CV and forms: "Singapore Citizen", "PR", or
  "EP holder valid until [date]" — never the NRIC (§4).
- **Check Employment Pass viability per role before applying.** COMPASS
  changed from 1 Jan 2026 (new EPs) and 1 Jul 2026 (renewals): refreshed
  salary benchmarks, a revised qualifications list, and several tech roles
  removed from the Shortage Occupation List (2026-09 notes — verify).
  Search MOM's current COMPASS criteria for the role, offered salary and
  qualifications, and cite the date.
- A job change means the new employer applies for the pass, so the
  new-EP criteria apply (verify on mom.gov.sg).
- Not viable → a knockout (`jd-match.md`); say so and draft nothing.

## 10. Interview process, curveballs & rights

**Process** — only the TAFEP and Workplace Fairness Act points are
verified; round structure and timing are practitioner norms.

- **Rounds and order**: recruiter or HR screen, hiring manager, technical
  or panel round, then a final; banks and MNCs may add an assessment
  (practitioner norm — confirm locally).
- **Timeline**: expect two to six weeks from first screen to offer; ask for
  the next step at the end of each round (practitioner norm — confirm
  locally).
- **Assessments**: aptitude, case or coding tests at banks, MNCs and
  graduate programmes (practitioner norm — confirm locally).
- **Salary expectation**: TAFEP guidance says to avoid personal questions
  unless job-related and to discuss salary expectations openly
  (https://www.tal.sg/tafep/employment-practices/recruitment/conducting-job-interviews)
  (verified). Answer with the number from `answers.md`; field mechanics in
  §5. Giving a range versus a single number in the interview is a
  practitioner norm — confirm locally.
- **Notice talk**: state the notice exactly; the contract and statutory
  default are in §7, not restated here (practitioner norm — confirm
  locally).
- **Language**: English in most rounds; Mandarin may appear at local firms
  (practitioner norm — confirm locally).
- **AI-tool policy**: set per company and round; ask before a coding or
  take-home round (practitioner norm — confirm locally).
- **Source**: TAFEP above; the Workplace Fairness Act 2025 was still
  uncommenced as of 2026-09-29
  (https://sso.agc.gov.sg/Act/WFA2025/Uncommenced/20250304073414?DocDate=20250213)
  (verified), so check which provisions are in force before calling a
  question unlawful (see below).

**Curveballs and rights**

- **Workplace Fairness Act**: passed 2025, expected in force around
  end-2027; covers recruitment, promotion, appraisal, training and
  dismissal; employers with fewer than 25 staff are exempt initially;
  breaches are civil contraventions with penalties (HSF Kramer; Mayer
  Brown; Hawksford, verified 2026-09-25). Check which provisions are in
  force on the interview date before telling the user a question is
  unlawful.
- **TAFEP guidance**: TAFEP's fair-employment guidance expects hiring on
  merit and job-related criteria, and it already flags unfair practices
  such as long notice for junior roles (re-verify the current wording).
- Personal questions — age, marital status, family plans, race, religion,
  nationality — can still come up: answer in one line and pivot, or
  decline politely (`interview-prep.md`, Question banks, curveballs).
- Log the question, the interviewer and the date in the pipeline row's
  Notes — the record any complaint needs (§11).
- An NRIC request before an offer: decline; it belongs to onboarding (§5).

## 11. Recourse

- Discrimination or an unfair hiring practice: TAFEP. Salary, leave or
  other Employment Act breaches: MOM. Missing CPF (citizens and PRs): the
  CPF Board. These channels are not in the compiled notes — confirm the
  current filing route on mom.gov.sg before advising a filing.
- Knowing these exist is usually enough leverage; for a real dispute, give
  general information and suggest a qualified professional (SKILL.md).
