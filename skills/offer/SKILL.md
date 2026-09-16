---
name: offer
description: Normalize an offer to true annual comp, compare offers, and coach the negotiation. Runs the job-hunting skill's Negotiator role.
argument-hint: [paste the offer details]
disable-model-invocation: true
---

Use the `job-hunting` skill, role **Negotiator** (`references/offer-coach.md`), with the comp mechanics from `references/markets/<cc>.md`. Offer(s): $ARGUMENTS

1. Resolve storage mode (workspace: `python3 ${CLAUDE_SKILL_DIR}/../job-hunting/scripts/workspace.py where`); read the profile (§3 expectations, dealbreakers) and the pipeline first.
2. Normalize each offer to true annual comp (contractual 13th month/AWS only; discretionary bonus as a labeled estimate; EPF/CPF when comparing across countries); flag probation, notice and deadline traps.
3. Compare against the profile and live market data (cited); give an honest accept / negotiate first / decline read and one specific counter on true leverage only.
4. Log the offer in the Offers table, set the pipeline stage to `offer`, and offer a mock negotiation.
