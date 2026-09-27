# Post-offer — the Onboarder role

From "I accepted" to confirmed in the new role: accept in writing, resign,
serve notice, handle a counter-offer, brief references, clear the
background check, plan the first 90 days, pass probation, close the
pipeline. Letters and plans follow `facts-policy.md`. Contract or legal
questions: general information, then suggest a qualified professional.

## 1. Accept in writing — before resigning

Offers do get withdrawn — 18% of Huntr users had an offer withdrawn
(Huntr Q1 2026) — so the user resigns only when every box is ticked:

- [ ] Written offer or contract signed: title, base, bonus wording
      (contractual or discretionary), allowances, start date.
- [ ] Probation length, notice during and after it, confirmation criteria
      (ask now if missing — §8); leave, medical, work arrangement.
- [ ] Conditions (background check, references) cleared or dated; work
      pass approved where one is needed (`markets/sg.md`).
- [ ] Start date fits the user's real notice (§3) — state the last working
      day if resigning today and the earliest start (first working day after
      it).

Set the Offers table Status to `accepted` (workspace: the `## Offers` table
in `pipeline.md`; chat mode: profile §9).

## 2. Resign

Tell the manager first, in a meeting or call, then send the letter the same
day. No reasons, no criticism, no new employer's name unless the user wants
to share it. Save the letter as `letters/resignation-<company>.md`
(workspace) or deliver it inline (chat). Fill both dates: effective = the
planned resignation day (today if none given); last working day computed
from the contract notice. Say they move if a buyout or new start date is
agreed.

```
Subject: Resignation — [Full name]

Dear [Manager's name],

Please accept this letter as notice of my resignation from my position as
[title], effective [date]. In line with my [notice period] notice period,
my last working day will be [date].

I will complete a full handover before I leave. Thank you for the
opportunities during my time at [Company].

Yours sincerely,
[Full name]
```

## 3. Notice mechanics

The contract governs; read its clause for both probation and confirmed
status. Statutory floors, probation notice and typical contract terms:
`markets/my.md`, `markets/sg.md` (other countries: `markets/_template.md`
plus a live search).

- **Buyout**: if the contract allows payment in lieu of notice, the user —
  or the new employer, if it agrees — pays salary for the unserved days to
  leave early. Ask the new employer before resigning; get the agreed last
  day in writing.
- **Unused leave**: ask HR whether it offsets notice or is paid out.
  **Garden leave**: still employed and paid until the last day, so no
  start at the new job before then; align the start date.
- **Handover doc** (shared in the first week of notice): responsibilities
  and recurring tasks with their next owner; in-flight work with status and
  next step; systems and access to transfer through IT (never passwords in
  the doc); key contacts; where the docs live; known risks.

## 4. Counter-offer from the current employer

Before the resignation meeting, write down why the user started looking.
Decision rule: the reasons for leaving rarely change — pay may move; the
manager, scope and direction usually don't. Consider a counter only if it
fixes the top reason, in writing, with a date; otherwise decline in one
line: "Thank you — I've made my decision, and I'll focus on a good
handover." Use a counter as leverage only if it is real (facts-policy §6).

## 5. References

- Brief references now, together with the acceptance checklist — the
  background check (§1) may call them before the start date. No references
  on file → ask for names and permission in the same batch and give the
  brief with [placeholders].
- Ask each referee's permission before giving their details; record it in
  the References table of `answers.md` (chat mode: the Answers section).
  The current manager only after resigning, and only if the user chooses.
- Brief each referee in one message: the role and company, when to expect
  the call, and two points they can speak to from the user's real work
  (profile §5) — never scripted praise.
- Thank each one after the check (`networking.md` §5, thank-you template).

## 6. Background-check readiness

- Degree certificates, transcripts and profile §4 certifications as digital
  copies.
- Employment dates and titles exactly as on the CV — the check compares
  them; fix any mismatch now. Past-employer contacts or verification letters.
- Payslips only when a legal requirement is stated; otherwise offer an
  employment-verification letter.
- NRIC/IC: never on the CV; give it only through the employer's official
  onboarding or check form after the offer — never by chat or to an agency.
  Work-status wording: `markets/my.md`, `markets/sg.md`.

## 7. 30-60-90 plan

Take the top three responsibilities from the posting (`postings/<slug>.md`
or the pasted JD) and the dossier through three phases:

| Phase | Aim | Per JD responsibility | Evidence at the review |
|---|---|---|---|
| Days 1–30 — **learn** | people, systems, metrics | who owns it, how it is measured, the current pain | a written summary the manager agrees with |
| Days 31–60 — **contribute** | first shipped work | one small, visible improvement | the shipped item and its effect |
| Days 61–90 — **own** | an area end to end | an outcome agreed with the manager | the outcome vs the agreed target |

Share it with the manager in week one and adjust. Save as
`dossiers/<company>-30-60-90.md` (workspace) or deliver it inline (chat).

## 8. Probation review

- Confirmation criteria were asked at offer stage (§1); still unknown →
  ask the manager in week one. How confirmation is documented per market:
  `markets/my.md`, `markets/sg.md`.
- Keep an evidence log — shipped work, numbers, feedback — and add it to
  profile §5 as it happens; it becomes the next resume.
- Book a mid-probation check-in: "Am I on track for confirmation? What
  would you want to see more of?"

## 9. Close the pipeline

Workspace mode:

```
python3 ${CLAUDE_SKILL_DIR}/scripts/tracker.py set --company "X" --stage accepted --next "Serve notice; start at X" --due <start-date>
python3 ${CLAUDE_SKILL_DIR}/scripts/tracker.py set --company "Y" --stage withdrawn --note "withdrew after accepting X"
```

Chat mode: set Stage in the profile §9 pipeline table by hand. Draft a
withdrawal for every other open process now; send each once the background
check clears and the start date is agreed in writing, then set `withdrawn`.
Scan every drafted message with `ats_check.py --slop` (workspace mode; chat
mode: read it against `assets/slop-phrases.txt`) and replace every hit.

> Hi [Name], thank you for your time on the [role] process. I've accepted another offer and am withdrawing my application. I enjoyed [one specific thing], and I'd be glad to stay in touch. [Your name]

- Thank referrers and helpful contacts (`networking.md` §5), then set
  their Status to `thanked` and clear Next touch
  (`tracker.py contact --name … --status thanked --next-touch ""`; chat
  mode: the Contacts table).
- Update profile §1 (current title, Search status) and profile §5 (the
  new role); stop any recurring `/loop` or `/schedule` search digest.
- Workspace mode ends with the `saved:` line; chat mode regenerates the
  profile block.
