# Offer Coach — evaluate, compare, negotiate

Run this when an offer arrives, when the user is weighing more than one, or
when they ask "should I accept?" / "can I negotiate?". Market comp mechanics
live in `references/markets/<cc>.md` (§6–§8); this file is the decision and
negotiation loop. Salary data changes constantly — verify market ranges with
a live search, never from memory.

## 1. Intake (one grouped batch — SKILL.md memory rules)

Ask only what the offer letter and profile don't answer:

- **The paper** — have them paste the offer letter/email if they haven't.
- **Money** — base; bonus and its exact contract wording (guaranteed 13th
  month / AWS vs "discretionary, subject to performance" — the wording
  decides whether it's real pay, `markets/<cc>.md` §8); sign-on; equity.
- **Terms** — probation length and notice during/after it, leave, medical,
  learning budget, modality, on-call expectations.
- **Pressure** — the acceptance deadline, and whether other offers or final
  rounds are still in flight.
- **Baseline** — current total comp (for the delta) if not already in the
  profile; the profile's §3 salary expectation.

## 2. Normalize to true annual comp

Employers quote monthly base; offers only compare as annual totals.

- **True annual comp** = base × 12, plus 13th month / AWS *only if
  contractual*, plus discretionary bonus as a labeled estimate (not a
  promise), plus sign-on amortized over its first year.
- Statutory employer contributions (EPF/CPF) are real money — include them
  when comparing offers across countries, where rates differ; CPF covers
  Singapore Citizens and PRs only, not EP/S Pass holders.
- Flag wording traps (`markets/<cc>.md` §7–§8): "13th month
  (discretionary)" is a bonus, not a 13th month; a long probation changes
  when notice and confirmation protections kick in.

## 3. Compare and verdict

- **Against the profile:** §3 salary expectation, modality, dealbreakers,
  company-size preference; §2 goals — does this role move the positioning
  forward or sideways?
- **Against the market:** live-search current ranges for the role, level,
  and city (NodeFlair, Glassdoor, posted bands on MyCareersFuture/
  JobStreet). Cite what you find.
- **Multiple offers:** one side-by-side table —

| | Offer A | Offer B |
|---|---------|---------|
| Base / month | | |
| True annual comp | | |
| Probation / notice | | |
| Modality / commute | | |
| Growth & stack fit | | |
| Risk flags | | |

Close with an honest verdict — **accept** / **negotiate first** /
**decline** — and what would change it. The decision stays with the user.

## 4. Negotiate

- **What moves in MY/SG:** base, sign-on, extra leave, start date, learning
  budget, title. Statutory terms and company-wide AWS/13th-month policy
  rarely move; equity bands barely move below senior.
- **Leverage honestly:** a real competing offer, a market data point, a
  specific quantified achievement (`facts-policy.md` §6).
- **The script:** enthusiasm first, then one specific ask with a reason
  ("market data for [role] in [city] centers on X — can we close the gap on
  base?"), then stop talking. Get the final package in writing before
  accepting anything.
- **Timing:** never accept on the call — thank them, confirm the deadline,
  take at least a day. An exploding deadline (under a week) is a pressure
  tactic; a polite extension request naming the date you can answer by is
  normal and usually granted.
- **Red flags:** verbal-only offers, refusal to put terms in writing, pay
  far above market for vague work (scam signals, `sourcing.md` §5), guilt
  responses to a counter.

## 5. Mock negotiation (optional)

Run it like `references/interview-coach.md`: stay in character as the hiring
manager or HR, one exchange at a time, push back realistically ("that's
above our band for this level"), then debrief — what landed, what to
tighten, one drill to re-run.

## 6. Record

Log every offer in the Offers table — `pipeline.md` `## Offers`:
company, base, bonus type,
true annual comp, probation/notice, deadline, status — and run the closing
step (SKILL.md). On acceptance, update the pipeline
stage and make the notice-period countdown the next action
(`post-offer.md`).

Negotiate hard on true facts only (`facts-policy.md` §6).
