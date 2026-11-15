# Interview Prep Pack — rounds, question banks, rights

For when an interview lands — first round, second, or final — or the user
asks "what will they ask me", "how do I answer", or "what should I ask
them". This file is the preparation layer; live practice is
`interview-coach.md`, company research is `company-dossier.md`, and offer
evaluation is `offer-coach.md`. Works for any industry — pull role flavor
from the posting, not from assumptions.

## Step 0 — pin the round (one grouped batch)

Echo the pipeline row first (stage, Next action, Due) — "Grab, recruiter
screen, due Friday — right?" — and ask only for what it lacks:

- **Company & role** — reuse the jd-match extraction and dossier if they
  exist; otherwise skim the posting now.
- **Round** — which number, what format (call / video / panel / assessment
  centre), who's interviewing if known, and anything the coordinator said
  it covers. If they didn't say, tell the user it's normal to ask.
- **Round type** — one of `hr-screen` `behavioral` `technical` `coding`
  `system-design` `case` `assessment` `final`.
- **Date** — how much prep time exists; prioritize accordingly.
- **Language** — prep in the language the interview will run in.

**Dossier freshness.** Read the dossier's `_Researched: YYYY-MM-DD_` line.
Older than 30 days → refresh its news section via
`/job-hunter:interview company <name>` before prep. No dossier → offer one.

Create the pack, then fill its sections in place:

`sh ${CLAUDE_SKILL_DIR}/scripts/jh interview.py new --kind prep --company "<X>" --role "<Y>" --round-type <type> [--round N] --date <interview date>`

## Stage map — what each round is really testing

| Round | Who | Really testing | Prepare |
|---|---|---|---|
| Recruiter / HR screen | TA or HR | Resume walkthrough, salary fit, availability, communication | 60–90s self-intro; salary number; notice period; logistics answers |
| Assessment / case / hackathon (common in MY–SG bank, consulting, grad programmes) | Assessors | Structured thinking under pressure, visible collaboration | Free aptitude-test practice; case skeleton: problem → who's affected → 2–3 options → recommendation → risks; volunteer to organize or present |
| First interview | Hiring manager | Can you do the job; will the team want you | STAR stories mapped to the posting's competencies; role-flavored questions below |
| Second / panel / technical | Panel or senior staff | Depth and consistency — they compare notes with round one | Same stories one level deeper (numbers, trade-offs); handling disagreement live; technical core of the role |
| Final | Senior leader / HR | Motivation, culture, offer parameters | Company-level "why us" (dossier); comp conversation readiness; questions that show long-term thinking |

Between rounds, always have the user ask the coordinator what the next
round covers — a normal question that removes guesswork.

## The six answers to prepare before any round

1. **"Tell me about yourself"** — 60–90 seconds: present (who you are in
   one line) → proof (strongest relevant evidence) → why here. Rehearse
   aloud; this answer sets the interview's tone.
2. **Why this company / this role** — built from the dossier; must name
   something specific enough that it couldn't be said to a competitor.
3. **Strength / weakness** — strength with evidence, not adjectives.
   Weakness: a real one plus the fix in progress — never "I'm a
   perfectionist", interviewers have heard it a thousand times.
4. **Stress, pressure, personality questions** — answer with a *system*,
   not a claim: trigger → your mechanism (prioritize, break down, ask
   early, recover) → one recent example → result. The same frame carries
   "how do you handle conflict / failure / criticism".
5. **Salary expectation** — a single number near the bottom of the true
   range plus "(negotiable)"; mechanics in `markets/<cc>.md` §5. In round
   one it's fine to deflect once ("I'd like to understand the role first —
   my range is around X if that helps") but have the number ready.
6. **Availability / notice** — exact, no hedging.

Items 1, 3 and 4 (and 5, 6) live in `answers.md` under those headings; the
pack points to them rather than copying.

Plus **3–5 STAR stories** from `answers.md` "STAR stories" covering
leadership, conflict, failure, pressure, and initiative. One story may serve
two themes. Rehearsed aloud beats re-read silently.

## Story map and gaps

Map each likely question's theme to a story in `answers.md` (each carries
`(themes: …)` tags). Themes in the pack use the debrief vocabulary
(`interview-debrief.md` §1) so the question bank and the gaps line up.

| Theme | Story | Strength |
|---|---|---|
| leadership | title, or "none" | strong / usable / weak |

- **strong** — specific, recent, own actions clear, a number. **usable** —
  real but vague on your part or the result. **weak** — thin or old.
- Always check the five STAR themes — leadership, conflict, failure,
  pressure, initiative — whatever the posting says.
- Every gap (no story, or weak) gets one next step: draw a real event out
  of profile §5 by asking (`facts-policy.md` §2), or, with no real event,
  `soft-skills-coach.md`. Never script a story.

## Question banks

**Behavioral classics** — conflict with a teammate; a failure and what
changed after it; leading without authority; competing deadlines; a
decision others disagreed with; going beyond the job scope.

**Personality / HR** — describe yourself in three words; how do you handle
stress (frame above); how would colleagues describe you; what motivates
you; where do you see yourself in five years; team vs solo work; how you
take criticism. These are asked in *every* market — prepping them is not
optional.

**Role-flavored** — mine the posting: every stated requirement becomes
"tell me about a time you [requirement]". Client-facing finance gets "pitch
this product to a hesitant client", "explain [concept] to a layperson",
"how do you handle rejection", plus light market awareness. Tech gets the
stack's core loop plus a debugging or design story. Build the list from the
JD, not from a generic bank.

**Curveballs & personal questions (SEA reality)** — age, marital status,
family plans, race, and religion still get asked at local firms in MY and
much of SEA. Prep a
calm one-line answer plus pivot ("Single, and fully mobile for this role —
on the job itself…"). Declining gracefully is legitimate; note it may cost
rapport at traditional firms, and let the user pick their comfort level. An
interviewer who pushes hard here is data about the employer. What the law
says per market: `markets/<cc>.md` §10 (Interview curveballs & rights).

## Questions to ask them — by stage

| Stage | Safe and smart asks |
|---|---|
| Any round | What does success look like in the first six months? Why is the position open? How is the team structured? What separates good from great in this role? |
| HR round, or once they raise comp | Salary structure — basic vs allowances vs commission; bonus contractual or discretionary; EPF above statutory?; medical coverage (inpatient/outpatient/dental, dependants); OT policy and claims; hybrid/flexi arrangement; transport, parking, or travel allowances; probation length **and confirmation criteria**; notice period; annual-leave days; training or certification support |
| Final round | Growth path from this role; the team's biggest challenge this year; offer timeline and next steps |

Rules: don't open round one with salary and leave — but once HR raises
comp, asking benefit specifics is normal and expected in MY/SG. Anything
promised verbally goes into the written offer before accepting
(`offer-coach.md`).

## Lessons to apply

Before finalising the pack, read `interviews/question-bank.md` if it
exists: repeat questions, "Questions with no story", and the re-practice
queue feed the likely-questions list and the story gaps. No bank or no
matching rows → one line: "no lessons yet".

## Market rights sheet — before signing

Before signing, check the market's statutory floors and contract red flags:
`markets/my.md`, `markets/sg.md` (other countries: `markets/_template.md`
plus a live search).

## After each interview

1. **Same day** — thank-you email or message, 2–4 lines: thanks, one
   specific point from the conversation, reaffirmed interest. Use the
   Networker's "Interviewer thank-you" template in `networking.md`; via the
   recruiter if no direct address.
2. **Debrief within 24 hours** — `interview-debrief.md`: questions asked,
   answers that wobbled, promises made, interviewer names. This feeds the
   next round's mock.
3. **Silence** — follow up at the stated timeline + 2–3 working days
   (or ~1 week if none was given). One polite nudge, then keep the
   pipeline moving — never park the search on one company.
4. **Advanced** — ask what the next round covers; set the stage change and
   `sh ${CLAUDE_SKILL_DIR}/scripts/jh interview.py outcome --company "<X>" --role "<Y>" --outcome advanced`;
   re-run the dossier's themes and a targeted mock
   (`interview-coach.md`) on the weak areas from the debrief.
5. **Rejected** — brief thanks + ask for feedback (sometimes answered);
   log it in the tracker with the stage change and
   `interview.py outcome --outcome rejected`. Three rejections at the same
   stage → run the funnel diagnosis (`pipeline.md` §5).
6. **Offer** — switch to `offer-coach.md`.

Close every prep session:
`sh ${CLAUDE_SKILL_DIR}/scripts/jh tracker.py set --company "<X>" --role "<Y>" --next "<round_type> prep done — mock?" --due <date>`,
then the closing step (SKILL.md).
