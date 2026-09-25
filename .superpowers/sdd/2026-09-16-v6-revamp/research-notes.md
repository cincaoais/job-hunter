# Research notes (collected 2026-09-16) — for reference-file implementers

Cite the source in parentheses when you quote a number. Do not invent numbers
that are not here; if a claim has no source, state it as practice, not as data.

## Conversion and channel data
- Cold inbound → interview ~3%; referral ~40%; recruiter-sourced ~25%; referral
  offer rate 7.3% vs inbound 0.2% (Ashby, 38M applications, 2025/26).
- Referral volume is <1% of applications, so a referral is rare and valuable;
  referred hires close in 29 vs 44 days (Pin, employee referral data).
- 11–20 applications → ~9% interview rate; 100+ → ~2.6%; 66% of offers land
  within 50 applications; re-applying to the same company halves the rate;
  median search 108 days (Q1) / 82 days (Q2) (Huntr Q1/Q2 2026, 140k apps).
- Interview rate by source: Google Jobs 7.1%, SEEK/JobStreet 4.6%, LinkedIn
  2.9%; Easy Apply 1–4% vs direct 2–3× better; Easy Apply postings average 834
  applicants vs 295 (Huntr Q1 2026; LinkedIn Easy Apply studies).
- Recruiters screen day-one applicants first, skim again at day two, then only
  revisit if the pipeline dries (Blind recruiter AMA 2026).
- 53% of seekers ghosted in the past year; 81% of recruiters admit their
  employer posts ghost jobs; 18% of Huntr users had an offer withdrawn Q1 2026
  (Fortune/Criteria 2026; Huntr Q1 2026).

## Outreach benchmarks (Pin, 4M messages, Jun 2025–May 2026)
- LinkedIn message reply ~17% vs email ~5–6%.
- 150–199 words performs best.
- Two-step email + LinkedIn sequences ~46% vs ~20% email-only.
- Three touches capture ~93% of replies.
- Recruiters search "Open to Work" plus recent activity as intent signals;
  employed candidates should use the recruiters-only Open-to-Work setting.

## Screening reality
- ATS systems rank, they rarely auto-reject on keywords (92% of surveyed
  recruiters configure no content-based auto-reject); knockout questions
  (work pass, location, years, licence, notice) do reject (Hiration/Huntr).
- Recruiter skim 6–10 s on: name, current title, current employer, dates,
  previous title, education, first bullet of latest role; 36% reviewed on
  mobile, two-column layouts break there (Huntr/Careerflow).
- 67% of hiring managers say they spot AI cover letters, 54% view them
  negatively; what stands out: specific numbers, a concrete anecdote, a
  company-specific detail, bullets the candidate can defend in a screen.

## Coaching practice
- Outplacement/coaching flow: assessment → branding → search strategy →
  interview prep → offer → accountability; weekly sessions for 3–6 months.
  People pay for: LinkedIn audit, mock interviews, salary negotiation,
  "why no callbacks" diagnosis, 30-60-90 plans.
- Burnout is the main attrition risk; what works: process goals (~10 quality
  applications/week), batching into interview cycles with deliberate rest,
  tracking; 71% lowered salary expectations; 46% have <3 months runway
  (Duke career centre 2025; Huntr Q1 2026).
- No surveyed commercial product covers onboarding/first 90 days — a gap.

## Malaysia 2026
- Employment Act s.12 statutory notice floor: 4 weeks (<2 yrs), 6 weeks
  (2–5 yrs), 8 weeks (>5 yrs) when the contract is silent; contracts commonly
  1–3 months for professional/managerial. EA covers all employees post-2022.
- Probation 3–6 months typical; confirmation needs a letter; statutory
  notice still applies during probation unless the contract says otherwise.
- Minimum wage RM1,700/month (Feb 2025). EPF employee 11%, employer 12–13%;
  SOCSO + EIS mandatory from day one. EPF for foreign workers 2%/2% from
  October 2025 wages. Gig Workers Act in force 31 Mar 2026.
- Unemployment 2.9%, skills-related underemployment 35.2%; fresh-grad median
  ~RM3,085 (KL ~RM3,435) (Malay Mail, Aug 2026).
- Boards: JobStreet by SEEK (volume default; seekAI ranks applicants using
  resume + JD + employer past behaviour, "Top Applicant" badge, a
  "predictive approachability" signal driven by profile completeness and
  activity); LinkedIn (mid-senior, sourcing, referrals); Hiredly (junior–mid,
  startups); Glints (tech/startup). Lowyat users rate MauKerja/JobStore poorly.
- Agencies: Robert Walters, Michael Page, Hays, Randstad, JAC Recruitment,
  PERSOLKELLY, Reeracoen; Hiredly also acts as a hybrid board/headhunter.
- Salary guides: Hays Asia Salary Guide 2026, Robert Walters Salary Survey
  2026, Michael Page Salary Guide 2026; JobStreet salary labels on postings.
- Recourse: Jabatan Tenaga Kerja (Labour Department, e-Aduan); unfair
  dismissal → Industrial Relations Department.

## Singapore 2026
- Notice: 1–2 weeks during probation typical, ~1 month after; statutory
  defaults scale with tenure (1 day → 4 weeks) but contracts govern; TAFEP
  flags long notice for junior roles. Probation 3 months standard, 6 for
  senior; terms in the Key Employment Terms (KETs); CPF applies in probation.
- AWS (13th month) not mandatory; binding once in the contract. CPF applies to
  Singapore Citizens and PRs only (EP/S Pass holders have none). From 1 Jan 2026
  the Ordinary Wage ceiling is S$8,000/month (S$7,400 in 2025); the annual salary
  ceiling stays S$102,000; Additional Wage ceiling = S$102,000 − total OW subject
  to CPF for the year (CPF Board; Vialto, verified 2026-09-25).
- Workplace Fairness Act: passed 2025, expected in force around end-2027;
  covers recruitment, promotion, appraisal, training and dismissal; employers
  with fewer than 25 staff exempt initially; breaches are civil contraventions
  with penalties (HSF Kramer; Mayer Brown; Hawksford, verified 2026-09-25).
- Fair Consideration Framework: job ads live ≥14 days on MyCareersFuture
  before an Employment Pass application.
- COMPASS updates from 1 Jan 2026 (new EPs) / 1 Jul 2026 (renewals):
  refreshed salary benchmarks, revised qualifications list, several tech roles
  removed from the Shortage Occupation List — non-citizens should check EP
  viability per role.
- SkillsFuture Jobseeker Support: up to S$6,000 over 6 months for
  involuntarily unemployed citizens (PRs from Q1 2026), points-based on
  job-search activity — the tracker doubles as evidence.
- MyCareersFuture used by ~1 in 3 fresh grads/young PMETs; ~6 in 10 found jobs
  within six months (MOM PQ reply, Sep 2025).
- Q3 2026 Net Employment Outlook +13%, weakest since 2021; 22% of employers
  plan cuts; agency postings down 18% while direct employers flat → go direct
  (ManpowerGroup via HRO, 2026).
- Never put the NRIC on a CV; state work status ("Singapore Citizen", "PR",
  "EP holder valid until …"). Salary sources: NodeFlair (tech, free),
  Levels.fyi SG, Glassdoor, MCF posted bands (min/max on every posting).
- Boards: JobStreet, MyCareersFuture (government portal, real volume),
  LinkedIn (mid-senior), NodeFlair (tech), Glints, Indeed.

## PH / ID / VN brief (from v5 sea-market-notes)
- PH: 13th-month pay mandatory for rank-and-file (by Dec 24); Kalibrr for
  tech; 2x2 photo still conventional at local firms.
- ID: probation max 3 months on permanent contracts; THR (~1 month, religious
  holiday allowance) is the 13th-month equivalent.
- VN: probation up to 60 days for degree-required roles (180 managerial);
  post-probation notice 30–45 days; ITviec/TopDev/VietnamWorks; referrals
  often beat boards.

## Things the skill deliberately does not do
- Auto-apply bots, live interview copilots, logging in to boards, scraping
  Glassdoor/Glints/NodeFlair/Kalibrr (blocked or wrong-country in tests).
