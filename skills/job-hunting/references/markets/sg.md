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
| MyCareersFuture (MCF) | government | Government portal with real volume; posted min/max band and employer screening questions on every posting | `mcf` |
| LinkedIn | mid-senior | Mid-senior roles, networking, recruiter sourcing | `linkedin` (guest search) |
| NodeFlair | niche | Tech roles, with salary data | — (scoped web search) |
| Glints | niche | Tech and startup roles | — (scoped web search) |
| Indeed | volume | Aggregator | `indeed` (needs `python-jobspy`) |

- **MCF reach**: used by ~1 in 3 fresh graduates and young PMETs; ~6 in 10
  found jobs within six months (MOM PQ reply, Sep 2025).
- **Fair Consideration Framework**: a job ad must be live on MCF for at
  least 14 days before the employer applies for an Employment Pass (MOM).
  Any role an employer may fill with an EP holder therefore surfaces on
  MCF — search it even when the role is also on LinkedIn.
- **JobStreet vs LinkedIn**: the MY split holds — JobStreet to apply,
  LinkedIn for mid-senior roles, sourcing and referral paths
  (`networking.md`).
- **SkillsFuture Jobseeker Support**: up to S$6,000 over 6 months for
  involuntarily unemployed citizens (PRs from Q1 2026), points-based on
  job-search activity (SkillsFuture Jobseeker Support scheme, 2026). Log
  every application, outreach touch and interview — the tracker doubles
  as the activity evidence (`pipeline.md`; chat mode: profile §9).

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

Search live for the role, level and city and cite what is found; never
quote a range from memory (`offer-coach.md` §3).

## 4. Resume conventions

| Item | Norm |
|---|---|
| Length | 1–2 pages |
| NRIC | **Never** on a CV |
| Work status | State it instead: "Singapore Citizen", "PR", "EP holder valid until [date]" (§9) |
| Expected salary | Only if the ad asks; then a range plus "(negotiable)" |
| Photo | A mixed norm: skip for Western MNCs and tech, harmless at local or traditional firms — default no per the photo decision matrix (`resume-revamp.md` Step 3) |

## 5. Application form norms

- **MCF**: fetch the posting to get the employer's screening questions and
  answer each from `answers.md`, in order; the posted band sanity-checks
  the salary number (`answer-bank.md` §5).
- **JobStreet SG**: the same SEEK engine as Malaysia; the expected-salary
  field takes one number — set it near the bottom of the true range, add
  "(negotiable)" where free text allows (full mechanics: `markets/my.md`
  §5).
- **Work-pass questions** (citizen / PR / sponsorship needed) are
  knockouts: answer exactly as `answers.md` states them; a false "yes"
  fails at the pass application (`answer-bank.md` §4).
- **NRIC**: never in a screening field; only in the employer's official
  onboarding step after an offer (`answer-bank.md` §4).
- Current-salary questions: `facts-policy.md` §6.

## 6. Statutory floors

| Item | Floor |
|---|---|
| Minimum wage, hours and overtime, annual / sick / parental leave | Not in the compiled notes — look up the current Employment Act figures on mom.gov.sg before calling any term "below floor" |
| CPF | Applies from day one, probation included; rates vary by age — use the CPF Board's current table when comparing offers |
| CPF on bonuses | Capped by the Additional Wage Ceiling: S$102,000 (2025) → S$110,800 (2026) |
| Written terms | Key Employment Terms (KETs); probation terms must appear in them |

**Contract red flags** — the Malaysian list applies here too
(`markets/my.md` §6), plus: CPF missing from the payslip; probation or
notice terms absent from the KETs; notice far longer than the role's level
(TAFEP flags long notice for junior roles as unfair practice).

## 7. Probation & notice

- **Probation**: not regulated by the Employment Act; 3 months standard, 6
  for senior roles. Terms must appear in the KETs; CPF applies during
  probation as after it.
- **Confirmation** is documented through the KETs and the contract: the
  KETs state the probation terms, so ask HR at offer stage how
  confirmation is notified and get it in writing (`post-offer.md` §1,
  §8).

| Situation | Notice |
|---|---|
| During probation — typical contract | 1–2 weeks |
| Confirmed — typical contract | ~1 month; 1–3 months range, longer for senior roles |
| Contract silent — Employment Act default | Scales with tenure, 1 day → 4 weeks |

- The contract governs. Buyout, unused leave, garden leave and handover:
  `post-offer.md` §3.

## 8. 13th month / bonus wording

- **AWS** (Annual Wage Supplement, the 13th month): not mandatory;
  typically one month's basic salary paid in Nov/Dec; binding once it is
  in the contract.
- Offer cue: a contractual AWS is real pay; a bonus "discretionary /
  subject to performance" counts only as a labelled estimate in true
  annual comp (`offer-coach.md` §2).
- CPF on AWS and bonuses stops at the Additional Wage Ceiling (§6) — it
  matters when comparing packages with a large bonus.

## 9. Work authorization signals

- Work-status wording for the CV and forms: "Singapore Citizen", "PR", or
  "EP holder valid until [date]" — never the NRIC (§4).
- **Check Employment Pass viability per role before applying.** COMPASS
  changed from 1 Jan 2026 (new EPs) and 1 Jul 2026 (renewals): refreshed
  salary benchmarks, a revised qualifications list, and several tech roles
  removed from the Shortage Occupation List (MOM, 2026). Search MOM's
  current COMPASS criteria for the role, offered salary and
  qualifications, and cite the date.
- A job change means the new employer applies for the pass, so the
  new-EP criteria apply (verify on mom.gov.sg).
- Not viable → treat it as a knockout (`jd-match.md`) and say so; do not
  draft an application around it.

## 10. Interview curveballs & rights

- **Workplace Fairness Act**, phased in 2026–27: discrimination in hiring
  on nationality, age and similar characteristics becomes an offence.
  Check which provisions are in force on the interview date before
  telling the user a question is unlawful.
- **TAFEP guidance**: TAFEP's fair-employment guidance expects hiring on
  merit and job-related criteria, and it already flags unfair practices
  such as long notice for junior roles (re-verify the current wording).
- Personal questions — age, marital status, family plans, race, religion,
  nationality — can still come up. The user may answer in one line and
  pivot, or decline politely (frame: `interview-prep.md`, Question banks,
  curveballs).
- Log the question, the interviewer and the date in the pipeline row's
  Notes — the record any complaint needs (§11).
- An NRIC request before an offer: decline; it belongs to onboarding (§5).

## 11. Recourse

- Discrimination or an unfair hiring practice: TAFEP.
- Salary, leave or other Employment Act breaches: MOM. Missing CPF: the
  CPF Board.
- These channels are not in the compiled notes — confirm the current
  filing route on mom.gov.sg before advising a filing.
- Knowing these exist is usually enough leverage; for a real dispute,
  give general information and suggest a qualified professional
  (SKILL.md).
