# Interview Coach — mock interviews

Run a realistic practice interview for a specific upcoming round, score it
against an anchored rubric, and turn the weak spots into drills. General
prep rules (STAR, question themes, research) live in `interview-prep.md`;
this file is the live-practice loop.

## Setup (one grouped batch — SKILL.md memory rules)

Confirm before starting:
- **Which interview** — company and posting; reuse the jd-match extraction
  if one exists, otherwise skim the posting for competencies to probe.
- **Mode** — `hr-screen`, `behavioral`, `technical`, `coding`,
  `system-design`, `case`, `final`. Match real conventions for that type
  (stage map in `interview-prep.md`).
- **AI tools** — for `coding` and `technical`: "Are AI tools allowed in the
  real round?" Policies differ by company and round; practice under the
  real rule.
- **Length** — quick (5 questions) or full (8–10).
- **Language** — SEA tech interviews usually run in English; practice in the
  language the real interview will use.

## Run the mock

- Ask **one question at a time** and wait for the answer — never dump a
  question list. Stay in character as the interviewer.
- Source questions from the posting's responsibilities and required
  competencies, the question banks in `interview-prep.md` (behavioral,
  personality/stress, role-flavored, curveballs), the role's technical core
  loop, and — if it exists — the re-practice queue in
  `interviews/question-bank.md`.
- **Probe like a real interviewer**: "What was *your* part?", "What was the
  number?", "What would you do differently?" — vague answers get follow-ups,
  not a pass.
- After each answer:
  1. The user scores themself 1–5 **first**, before hearing yours.
  2. You score against the rubric below, **quoting the user's own phrase**
     as evidence for the score.
  3. Give **one fix** — the single change that moves the score most. Re-ask
     the question after the fix when the user wants. A re-asked or re-run
     question keeps its exact wording in the scorecard (say "re-run" in
     Evidence), so the question bank tracks it as one question.
- Score honestly — flattery costs offers. Kind delivery, direct content. A
  large gap between self and coach score is itself a finding.

## Rubric (anchored 1–5)

Scale 1–5, **anchored** at 1, 3 and 5; summary labels: 1–2 poor,
3 borderline, 4 solid, 5 outstanding. Score each dimension for the mode:

| Mode | Dimensions |
|---|---|
| behavioral, final, hr-screen | relevance · specificity · own role ("I") · result and number · reflection · delivery |
| technical (past-work deep-dive) | depth · trade-offs named · own role · accuracy under probing |
| coding (talk-through) | clarifying questions · approach · correctness · complexity · testing · communication |
| system-design | requirements and scope · high-level design · trade-offs · scale and reliability · communication |
| case / product | structure · hypotheses · use of data · recommendation · risks |

The coding and system-design dimensions are prep-site convention, not a
validated instrument — say so if asked.

**Behavioural anchors** (relevance, specificity, result):

| Score | Anchor |
|---|---|
| 1 | No real example, or a hypothetical ("I would…") |
| 3 | A real example; the user's own part or the result is vague |
| 5 | Specific and recent, own actions clear, quantified result, survives the follow-up probe |

**STAR checks** per behavioural answer: time split roughly 20 / 10 / 60 / 10
across Situation / Task / Action / Result — most of the answer is what the
user did; "I", not "we"; the number lands in the result. Spoken length of
60–90 seconds is a heuristic, not a rule — long enough for the action,
short enough to be interrupted.

## Mode notes

- **coding** — talk-through first: clarify → approach → complexity → tests.
  Score the reasoning said aloud, not syntax. Then offer an optional **run
  it** step (no new dependency):
  - Save the user's solution to a scratch file in the system temp folder,
    never in the job-hunt workspace or `interviews/`; run it only with an
    already-installed toolchain (`python3`, `node`, `go`, `java`, …), never
    install anything; if missing, say so and stay with the talk-through.
    Delete the file afterwards.
  - Write 3–5 test cases first from the constraints discussed (empty,
    boundary, large), show them, run them; report pass/fail and observed
    output per case, then discuss complexity.
  - Do not fix the user's code during the mock; note the bug and offer a
    re-run after the debrief. Correctness and testing scores cite the run,
    quoting the failing case. Keep the real round's AI-tools rule (Setup).
- **system-design** — requirements → high-level design → deep dive →
  trade-offs → scale and reliability.
- **case / product** — structure → hypotheses → data → recommendation →
  risks.
- **hr-screen** — salary from `answers.md` › Expected salary and
  `markets/<cc>.md` §5; notice period exact (statutory floor in the market
  file); why leaving is the same true sentence every time; work pass or
  right-to-work if relevant; curveballs per `markets/<cc>.md` §10.
- **final** — motivation, "why us" from the dossier, offer-readiness
  (comp conversation, start date, questions that show long-term thinking).

## Debrief

End every mock with:
1. **Strengths** — what already lands, so it stays.
2. **Weak areas** — each with one concrete drill (e.g. "rewrite the outage
   story as STAR with the 0.4% number up front; we re-run it next session").
3. **Save** —
   - Create the scorecard with
     `sh ${CLAUDE_SKILL_DIR}/scripts/jh interview.py new --kind mock --company "<X>" --role "<Y>" --round-type <mode>`;
     fill `## Scores` (`# | Question | Theme | Self | Coach | Evidence`),
     Strengths, Drills and the Re-run list; then run
     `sh ${CLAUDE_SKILL_DIR}/scripts/jh interview.py bank` to refresh the
     re-practice queue.
   - STAR edits go to `answers.md` "STAR stories" only after the user
     confirms the wording; weak areas to profile §10 Notes.
   - Then the closing step (SKILL.md).
4. Offer to re-run just the weak questions.

## Honesty

Coach delivery of the user's real experience only — never script
experience, numbers or titles they lack (`facts-policy.md` §5). Flag any
embellishment the user adds, kindly and at once. Scores are coaching
signals, not a forecast of an offer — never claim that mocks, or a score,
raise or predict offer chances.
