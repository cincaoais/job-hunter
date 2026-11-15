---
name: offer
description: Normalize an offer to true annual comp, compare offers, and coach the negotiation. Runs the job-hunting skill's Negotiator role.
argument-hint: [paste the offer details]
disable-model-invocation: true
---

Use the `job-hunting` skill, role **Negotiator** (`${CLAUDE_SKILL_DIR}/../job-hunting/references/offer-coach.md`), with the comp mechanics from `${CLAUDE_SKILL_DIR}/../job-hunting/references/markets/<cc>.md`. Offer(s): $ARGUMENTS

1. Run `sh ${CLAUDE_SKILL_DIR}/../job-hunting/scripts/jh workspace.py where`; read profile.md §3 expectations and dealbreakers, and pipeline.md first.
2. Normalize each offer to true annual comp (contractual 13th month/AWS only; discretionary bonus as a labeled estimate; EPF/CPF when comparing across countries); flag probation, notice and deadline traps.
3. Compare against the profile and live market data (cited); give an honest accept / negotiate first / decline read and one specific counter on true leverage only.
4. Log the offer in the Offers table in pipeline.md, set the pipeline stage with `sh ${CLAUDE_SKILL_DIR}/../job-hunting/scripts/jh tracker.py set --company "<X>" --role "<Y>" --stage offer`, and offer a mock negotiation.
5. End with the `saved:` line.
