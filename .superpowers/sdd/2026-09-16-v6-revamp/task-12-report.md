# Task 12 report — markets split

Status: DONE_WITH_CONCERNS (concerns are minor and listed at the end)
Commit: 5fa80bc `markets: per-country notes (MY, SG, template) replace sea-market-notes and the inline rights sheet` (base 07c8f52, trailer `Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>`)

## Files

| File | Lines | Change |
|---|---|---|
| `skills/job-hunting/references/markets/_template.md` | 64 | new: opening-line format, the 11 numbered headings with a "what goes here" line each, a 6-step "any other country: fill from a live search" procedure (cite source + date, label "(unverified)", no statutory numbers from memory, stale-board warning, deliver inline, legal line), PH/ID/VN one-paragraph briefs, each ending "(v5 notes, July 2026 — re-verify)" |
| `skills/job-hunting/references/markets/my.md` | 176 | new: v5 MY content + the whole Malaysia rights sheet + 2026 additions |
| `skills/job-hunting/references/markets/sg.md` | 176 | new: v5 SG content + 2026 additions |
| `skills/job-hunting/references/sea-market-notes.md` | deleted (`git rm`) | content split into the three files above |
| `skills/job-hunting/references/interview-prep.md` | 146 → 122 | rights sheet section replaced by heading + the two-line pointer; the curveballs paragraph stays and gains "What the law says per market: `markets/<cc>.md` §10 (Interview curveballs & rights)."; salary answer "mechanics in `markets/<cc>.md` §5" |
| `offer-coach.md`, `profile-optimizer.md`, `application-guide.md`, `resume-revamp.md` | link lines only | → `references/markets/<cc>.md` (§6–§8) / (§1, §5) / (`my.md`, `sg.md`; `_template.md` for PH/ID/VN and other countries) / `markets/<cc>.md` §4 |
| `README.md` | 3 lines | the "SEA market notes" bullet now names `references/markets/` (see concern 5) |

`my.md` and `sg.md` both open with "Compiled 2026-09; statutory figures drift — re-verify any number before quoting it precisely." and use the template's headings in the same order (checked by script: the heading lists are identical). Headings are numbered (`## 1. Boards & channels` … `## 11. Recourse`), so `<cc>.md` §N points to the same section in every market. LF endings, no CR, trailing newline, no trailing whitespace, no XML tags (only the `<cc>` placeholder SKILL.md already uses).

## Inbound link → heading map

| Inbound link (file:line) | Promise | Delivered in |
|---|---|---|
| `SKILL.md:89` | market norms: boards, salary sources, statutory floors, resume conventions; `_template.md` for other countries | my/sg §1, §3, §6, §4; `_template.md` "Any other country" |
| `post-offer.md:19` | work pass approved where needed (`sg.md`) | sg §9 Work authorization signals |
| `post-offer.md:52` | statutory floors, probation notice, typical contract terms; other countries → template | my/sg §6 Statutory floors + §7 Probation & notice (notice table: statutory default, during probation, confirmed); `_template.md` |
| `post-offer.md:96` | work-status wording | my §9 ("Malaysian citizen" / "Permanent resident" / "[pass type] holder, valid until [date]"); sg §4 + §9 ("Singapore Citizen", "PR", "EP holder valid until [date]") |
| `post-offer.md:116` | how confirmation is documented per market | my §7 **Confirmation** (confirmation letter, not automatic); sg §7 **Confirmation** (KETs + contract, ask how it is notified, in writing) |
| `sourcing.md:85-86`, `networking.md:106` | which agencies (list only; etiquette in networking §6) | my/sg §2 Agencies: list + one line linking `networking.md` §6 for etiquette |
| `answer-bank.md:37` | live market salary sources | my/sg §3 Salary sources |
| `answer-bank.md:70` | SG Employment Pass viability per role | sg §9 (COMPASS 2026 changes, check per role, not viable → knockout) |
| `answer-bank.md:76` | NRIC/IC never a screening field | my §4 + §5 "Other form rules"; sg §4 + §5 **NRIC** |
| `answer-bank.md:84` | JobStreet single-number field mechanics (`my.md`) | my §5 **JobStreet expected-salary field** (v5 text carried over); sg §5 short version linking my §5 |
| `pipeline.md:120` | agencies and contract roles as a runway lever | my/sg §2 ("Ask agencies for contract and contract-to-perm roles … runway lever in `pipeline.md` §6") |
| `offer/SKILL.md:8`, `offer-coach.md:5` (§6–§8) | comp mechanics: 13th month/AWS contractual vs discretionary, EPF/CPF, CPF AW Ceiling, probation and notice | §8 13th month / bonus wording; §6 (EPF rows; CPF + CPF on bonuses rows); §7 |
| `interview/SKILL.md:11`, `interview-prep.md:101` | market rights sheet: statutory floors, contract red flags, curveballs, recourse | §6 (table + **Contract red flags**), §10, §11 |
| `interview-prep.md:48` | salary-expectation mechanics | §5 |
| `interview-prep.md:83` | per-market law on personal questions | §10 Interview curveballs & rights (MY: no law bars them; SG: Workplace Fairness Act 2026–27 + TAFEP guidance) |
| `company/SKILL.md:11` | comp-intel sources | §3 |
| `profile-optimizer.md:7` (§1, §5) | platform mechanics | §1 seekAI ranking; §5 JobStreet field |
| `application-guide.md:79` | JobStreet field, probation/notice, 13th month/AWS, boards per country | §5, §7, §8, §1; PH/ID/VN in `_template.md` |
| `resume-revamp.md:146` (§4) | per-country resume detail | §4 Resume conventions |

## Every new number and its source

All 2026 additions come from `research-notes.md`; the rest is carried over unchanged from `sea-market-notes.md` (v5) or the interview-prep rights sheet (July 2026).

| Figure | File § | Cited as | research-notes origin |
|---|---|---|---|
| EA s.12 default 4 / 6 / 8 weeks (<2, 2–5, >5 yrs) when contract silent; contracts commonly 1–3 months professional/managerial; applies in probation unless the contract says otherwise | my §7 | (Employment Act s.12) | Malaysia 2026 |
| Probation 3–6 months typical | my §7 | unmarked (merges v5 "3, 6 for senior") | Malaysia 2026 |
| EA covers all employees since 2022 | my §6 | unmarked | Malaysia 2026 |
| EPF for foreign workers 2% / 2% from Oct 2025 wages | my §6 | (EPF) | Malaysia 2026 |
| Gig Workers Act in force 31 Mar 2026 | my §6 | the Act named in text | Malaysia 2026 |
| Fresh-grad median ~RM3,085, KL ~RM3,435; unemployment 2.9%; skills-related underemployment 35.2% | my §3 | (Malay Mail, Aug 2026) | Malaysia 2026 |
| seekAI inputs, Top Applicant, predictive approachability | my §1 | (SEEK, 2026) | Malaysia 2026 (no source given; SEEK named as product owner) |
| MauKerja/JobStore rated poorly | my §1 | "Lowyat forum users" in text | Malaysia 2026 |
| Salary guides 2026 (Hays Asia, Robert Walters, Michael Page), JobStreet salary labels | my §3, sg §3 | names in text | Malaysia 2026 |
| Agencies list | my §2, sg §2 | list | Malaysia 2026 |
| Q3 2026 NEO +13%, weakest since 2021; 22% plan cuts; agency postings −18%, direct flat | sg §1, §2 | (ManpowerGroup via HRO, 2026) | Singapore 2026 |
| MCF used by ~1 in 3 fresh grads/young PMETs; ~6 in 10 found jobs within six months | sg §1 | (MOM PQ reply, Sep 2025) | Singapore 2026 |
| FCF: ad ≥14 days on MCF before an EP application | sg §1 | (MOM) | Singapore 2026 |
| COMPASS: 1 Jan 2026 new EPs / 1 Jul 2026 renewals; benchmarks, qualifications list, tech roles off the SOL | sg §9 | (MOM, 2026) | Singapore 2026 |
| SkillsFuture Jobseeker Support: up to S$6,000 over 6 months; citizens, PRs from Q1 2026; points-based | sg §1 | (SkillsFuture Jobseeker Support scheme, 2026) | Singapore 2026 |
| Workplace Fairness Act phase-in 2026–27 | sg §10 | the Act named in text | Singapore 2026 |
| Probation 3 months standard, 6 senior; notice 1–2 weeks in probation, ~1 month after; statutory 1 day → 4 weeks | sg §7 | unmarked (v5 + Singapore 2026) | Singapore 2026 |
| CPF AW Ceiling S$102,000 (2025) → S$110,800 (2026) | sg §6, §8 | unmarked (v5, repeated in notes) | Singapore 2026 |

Practice rules, not data: "runway under 3 months" (pipeline.md §6 threshold); "1–3 months range" and probation/notice norms are the v5 compilation. No number outside research-notes or v5 was introduced.

## Commands and output

```
$ grep -rn "sea-market-notes" skills/        → no output (exit 1)
$ python3 build.py --check                  → OK: 12 skills pass checks
$ python3 -m pytest -q -m "not network"     → 275 passed in 0.55s
$ wc -l references/markets/{_template,my,sg}.md → 64 / 176 / 176
$ build_zip → job-hunting/references/markets/{_template,my,sg}.md packaged; no sea-market-notes
$ heading-order script → my.md and sg.md headings == _template.md table (True, True)
$ grep CR in markets/*.md → 0 each
```

## Self-review

- **Every new number sourced?** Yes — table above; each traces to research-notes, and cited ones carry source + date where research-notes gave one.
- **Agency etiquette duplicated?** No. my/sg §2 hold the list, the contract-role runway line and one link line naming the topics ("exclusivity, salary disclosure, counter-offers, WhatsApp: `networking.md` §6"). The SG "agency postings −18% → go direct" fact appears in both networking §6 (existing) and sg §2 — the brief asks for it in sg.md; it is a market fact, not etiquette.
- **Notice tables duplicated elsewhere?** No. `grep` for RM1,700, 8 weeks, 1 day → 4, 110,800, e-Aduan, Industrial Relations, 98 days, 45 h/week outside `markets/` → no hits. post-offer §3 keeps only buyout/leave/garden-leave/handover, and my/sg §7 link back to it instead of restating them.
- **Rights sheet moved wholly**: table (all 8 rows verbatim), contract red flags (verbatim), recourse (verbatim, legal line kept) are in my.md §6/§11; interview-prep keeps a heading plus the exact two-line pointer.
- **interview-prep curveballs paragraph** unchanged except the added pointer sentence.
- Other files: only link lines changed.

## Concerns

1. **CPF Additional Wage Ceiling figure.** The v5 and research-notes value "S$102,000 (2025) → S$110,800 (2026)" is carried over as instructed. My understanding is that the CPF *annual salary ceiling* is S$102,000, with the AW ceiling being S$102,000 minus ordinary wages, and that the monthly OW ceiling is what steps up over 2025–26. I could not check this without a new source, so the figure stands under the file's re-verify line. Worth a live check before release.
2. **SG statutory floors are thin by design.** research-notes has no SG minimum-wage, hours or leave figures. sg §6 has one row that says "Not in the compiled notes — look up … on mom.gov.sg" rather than numbers from memory. CPF, the AW ceiling and the KETs are filled.
3. **Unsourced but non-numeric items, labelled:** MYFutureJobs (my §1, "(unverified)"); SG recourse bodies TAFEP / MOM / CPF Board (sg §11, with "not in the compiled notes — confirm the current filing route"); TAFEP guidance wording (sg §10, "(re-verify the current wording)"); "a job change means the new employer applies for the pass" (sg §9, "(verify on mom.gov.sg)"); SG agencies are the MY regional list with "confirm each one's Singapore desk". Source attributions I derived: "(SEEK, 2026)", "(EPF)", "(MOM)", "(MOM, 2026)" and "(SkillsFuture Jobseeker Support scheme, 2026)" name the issuing body because research-notes gave none.
4. **Contract red flags placement.** The template has no separate heading for them, so they sit at the end of §6 Statutory floors, and the template's §6 line says so. sg §6 reuses the MY list by link and adds CPF, KETs and TAFEP long notice.
5. **README.md** (outside `skills/`) also linked `sea-market-notes.md`. I re-pointed that single bullet so the repo has no dangling path. Task 17 rewrites README anyway, so revert it if the controller wants README untouched until then. Historical docs (`docs/superpowers/specs|plans`) still name the old file; they are records and were left alone.
6. answer-bank.md:84 still restates the JobStreet field mechanics inline and links `markets/my.md`. That was already there and is out of scope here.

---

## Fix round 1 — commit 1589f80 `markets: correct CPF ceilings and eligibility, WFA status, label unverified attributions`

Status: DONE (10 of 10 items addressed). Facts come from the corrected `research-notes.md` Singapore section. Items the reviewer supplied that are not in research-notes carry "(2026-09 notes — verify)".

| # | Finding | Fix |
|---|---|---|
| 1 | CPF AW Ceiling row wrong | sg §6 "CPF on bonuses" row replaced by **CPF wage ceilings**: OW ceiling S$8,000/month from 1 Jan 2026 (S$7,400 in 2025), which also caps monthly CPF on base pay; annual salary ceiling S$102,000, unchanged; AW ceiling = S$102,000 − total OW subject to CPF for the year (CPF Board; Vialto, verified 2026-09-25). sg §8 now says: "For citizens and PRs, CPF on AWS and bonuses stops at the Additional Wage ceiling — S$102,000 minus the year's OW subject to CPF — and CPF on base pay stops at the OW ceiling (§6)." |
| 2 | CPF treated as universal | The sg §6 row is now **CPF eligibility**: "Singapore Citizens and PRs only — EP/S Pass holders have no CPF (CPF Board; Vialto, verified 2026-09-25)". The red flag reads "CPF missing from the payslip of a citizen or PR". §7 probation now says "CPF (citizens and PRs)", and the §11 recourse line says "Missing CPF (citizens and PRs)". `offer-coach.md:31-33` gains one clause: "CPF covers Singapore Citizens and PRs only, not EP/S Pass holders" (nothing else in that file changed). |
| 3 | WFA status | sg §10: passed 2025, expected in force around end-2027; covers recruitment, promotion, appraisal, training and dismissal; employers with fewer than 25 staff are exempt at first; breaches are civil contraventions with penalties (HSF Kramer; Mayer Brown; Hawksford, verified 2026-09-25). The "check which provisions are in force" hedge is kept. |
| 4 | Attributions | "(SEEK, 2026)", "(EPF)", "(MOM)", "(MOM, 2026)" and "(SkillsFuture Jobseeker Support scheme, 2026)" all become "(2026-09 notes — verify)". The Gig Workers Act date gains "(2026-09 notes — verify)". A grep for the old labels in `skills/` finds only an unrelated docstring in `jobstreet.py`. Sources research-notes does name are kept: Employment Act s.12, Malay Mail, MOM PQ reply, ManpowerGroup via HRO. |
| 5 | SG statutory floors | sg §6 splits the old row into three. **Minimum wage**: no general minimum wage, only the sectoral Progressive Wage Model; never call an SG offer "below floor" on pay alone. **Hours and overtime**: the Employment Act part covers lower-paid staff only; look up the MOM thresholds. **Leave**: look up the current MOM figures. The first two rows are labelled "(2026-09 notes — verify)". |
| 6 | FCF / MCF wording | "Any role" → "Most roles … exemptions exist (small firms, high-salary and short-term roles, intra-corporate transferees)". The MCF row now says screening questions appear "on some" postings, and §5 says "any employer screening questions". |
| 7 | Jobseeker Support | Added "Check eligibility first — the scheme has prior-income and housing caps." before the tracker-as-evidence advice. |
| 8 | my §10 | "At the interview stage the right is to decline gracefully, not to complain … Once employed, EA s.69F gives JTK a route for discrimination disputes (2026-09 notes — verify)." my §11 gains "Discrimination once employed: JTK under EA s.69F (§10)." |
| 9 | my §8 / §6 header | §8 adds that EPF applies to bonuses and the 13th month because they count as wages (2026-09 notes — verify). Rates on bonus pay are not compiled, so no rate is guessed; check KWSP's current table. In §6 the EA table keeps the EA rows only. A second table, "Contributions (EPF Act 1991; SOCSO and EIS under their own Acts)", holds the EPF/SOCSO/EIS row and the foreign-worker EPF row. |
| 10 | interview-prep pointer | Now "`markets/my.md`, `markets/sg.md` (other countries: `markets/_template.md` plus a live search)", which matches post-offer.md:52. |

Trims to stay in budget (no content lost): the notice "contract governs" line, the MY LinkedIn and salary-label bullets, the MY confirmation and non-citizen bullets, the SG confirmation bullet, and the SG personal-questions and recourse bullets were reworded more tightly.

Verification:

```
$ grep -rn "110,800\|sea-market-notes" skills/   → no output (exit 1)
$ python3 build.py --check                      → OK: 12 skills pass checks
$ python3 -m pytest -q -m "not network"         → 275 passed in 0.54s
$ wc -l markets/{_template,my,sg}.md            → 64 / 178 / 179
CR count 0 in all touched files; heading order unchanged (11 headings, same as the template)
```

Remaining concerns: sg.md is 179 lines, one under the ceiling, so any later addition needs an equal trim. Reviewer-supplied facts that research-notes does not hold are labelled "(2026-09 notes — verify)": PWM, the EA hours coverage, the FCF exemptions, the Jobseeker Support caps, EA s.69F and EPF on bonuses. Consider adding them to research-notes if they were verified.
