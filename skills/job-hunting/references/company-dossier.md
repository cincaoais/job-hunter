# Company Dossier — pre-interview research brief

Run this when an interview lands on the calendar or the user asks to be
briefed on a company ("tell me about X", "prep me for Friday"). It
produces a one-page brief readable in ten minutes. Everything
time-sensitive comes from live web search — never memory — and anything
unverified is labeled as such.

## 1. Setup (one grouped batch — SKILL.md memory rules)

The pipeline tracker usually already holds company, role, round type, and
date — echo them ("Grab recruiter screen on Friday, payments role — right?")
instead of re-asking. Ask only for what's missing:

- interviewer names/titles if known (shapes the questions to ask),
- what the user most wants to know — or is most worried about,
- how much prep time they have before the round.

## 2. Research (live search, cited)

Search in order of decision value:

- **Product & business** — what it sells, who pays, how it makes money.
- **Health & news** — funding or profitability, layoffs, leadership
  changes, expansion; last 12 months. Layoffs next to a hiring spree is
  worth naming.
- **Tech & team** — stack from the posting, engineering blog, and the
  company's other live ads; team size and structure where visible.
- **Comp intel** — salary data for the role and city (NodeFlair, Glassdoor,
  posted bands — sources per `markets/<cc>.md` §3).
- **Interview process** — round structure and question styles from
  candidate reviews; label as anecdote, not fact.
- **Culture signals** — employee reviews read skeptically: a pattern across
  many reviews is signal, an individual rant or rave is not.

## 3. The dossier (one page)

| | |
|---|---|
| Company / size / stage | |
| Product & who pays | |
| Recent news (12 mo) | |
| Stack & team | |
| Salary intel for the role | |
| Interview process (anecdotal) | |
| Red flags | |

Then three short sections:

- **Why they're hiring** — the best-supported read on what problem this
  role solves for them; that is the interview's real topic.
- **Likely themes** — 3–5 areas to expect, each mapped to the user's
  matching evidence from the profile (reuse the jd-match extraction if one
  exists).
- **Questions to ask** — 3–5 specific, researched questions that prove
  preparation ("How did on-call change after the queue migration your blog
  described?") — never generic ones a search could answer.

## 4. Feed forward

- Offer a mock for this round via `references/interview-coach.md`, sourcing
  questions from the dossier's themes.
- Hand the salary intel to `references/offer-coach.md` when an offer
  follows.
- Save the dossier's one-line takeaway and any red flags to the pipeline
  row's Notes — workspace mode: the dossier as `dossiers/<company>.md` and
  `python3 ${CLAUDE_SKILL_DIR}/scripts/tracker.py set --company "<X>" [--role "<Y>"] --note "…"`;
  chat mode: the profile §9 Pipeline row. Then the closing step for the
  storage mode (SKILL.md).
