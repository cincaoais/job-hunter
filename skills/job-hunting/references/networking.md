# Networking — the Networker role

A referral turns a ~3% cold application into a ~40% interview chance
(Ashby, 38M applications, 2025/26), and referrals are under 1% of
applications (Pin), so each one is worth real effort. Build the referral
map before applying, run short sequences, and log every touch. Messages
follow `facts-policy.md`: never invent shared history.

## 1. Rule: ask for a referral before applying

- Every target company (`strategy.md` §6) and every shortlist row scoring
  7+ gets a referral attempt before the application goes out.
- **Fresh posting**: send the referral ask to the warmest contact the day it
  is found, skipping the warm-up touches (not yet connected → the ask goes in
  the connection note). No referral by the posting's second day → apply direct
  and tell the contact, who can still flag the name. Recruiters screen day-one
  applicants first and skim again at day two (Blind recruiter AMA 2026).
- **No posting chosen yet, or not fresh**: send the ask now and state the
  apply-direct date in the same reply — no referral by the follow-up date
  (§3; already connected: day 7) → apply direct to the chosen posting that
  day and tell the contact. The same reply carries the §2 map — the warm
  contact plus the recruiter, role-keyword and alumni search links — the §5
  ask, the §3 dates for the contact and for anyone new from the searches,
  and the apply-direct date.
- A referred application is logged with `--channel referral`. Referral
  offer rate 7.3% vs 0.2% inbound (Ashby); referred hires close in 29 vs
  44 days (Pin).

## 2. Referral map per target company

| Path (warmest first) | How to find them |
|---|---|
| Ex-colleagues | the user's own network — ask who has moved there |
| Alumni | people search with `<Company>%20<school>` |
| 2nd-degree | a mutual connection; ask the mutual for the intro first |
| Current employees in the team | people search with `<Company>%20<role keyword>` |
| TA / recruiters | people search with `<Company>%20recruiter` |

Always — even when a warm contact is already on file — give the user two
LinkedIn people-search links to open themselves —
`https://www.linkedin.com/search/results/people/?keywords=<Company>%20recruiter`
(talent acquisition — the referral ask) and the same URL with
`<Company>%20<role keyword>` (likely teammates — the warm intro), keywords
URL-encoded — plus the alumni variant with `<Company>%20<school>`. These are
searches, not found people: never claim a specific person was found and
never fetch the result pages. Add whoever the user names to contacts (§4).

## 3. The sequence — three touches, one follow-up, then stop

Days are absolute, counted from the first touch (0, 2, 5, 12).

| Day | Touch (Status code) | What to send |
|---|---|---|
| 0 | comment (`c`) | a substantive comment on their recent post — a point or a question, never "great post" |
| 2 | connect (`k`) | a connection request with a one-line note naming the shared context |
| 5 | message (`m`) | ≤ 150 words with one specific ask (templates, §5) |
| 12 | follow-up (`f`) | one short follow-up, then stop |

- No recent post → connect on day 0 and keep the later days. Already connected
  (ex-colleague, known alumni) → start at the message; follow up 7 days later.
- Keep messages ≤ 150 words and use the room — reason, one proof, one ask.
  Pin found 150–199 words perform best, so a two-liner is too thin.
- Stop after the follow-up; more touches add little — three touches
  capture ~93% of replies (Pin).
- LinkedIn leads: message replies ~17% vs email ~5–6%. With a work email
  known, send the follow-up by email — email + LinkedIn sequences reach
  ~46% vs ~20% email-only (Pin, 4M messages, Jun 2025–May 2026).

## 4. Log every touch

Workspace mode — upsert the row after each touch and set the next date;
list what is due:

```
python3 ${CLAUDE_SKILL_DIR}/scripts/tracker.py contact --name "Aisyah Rahman" --company Nimbus --relationship alumni --target "Backend Engineer" --status c --next-touch 2026-09-27 --note "commented on post"
python3 ${CLAUDE_SKILL_DIR}/scripts/tracker.py contacts
```

- `contact` matches by name (+ `--company` when one name is at two
  companies); `--note` appends; Last touch defaults to today. `contacts`
  lists rows whose Next touch ≤ today (`today` shows the same list).
- `tracker.py add` / `set` are pipeline-only — never use them for contacts.
- **Status**: the last touch sent (`c`, `k`, `m`, `f`) while the sequence
  runs; `replied`, `referred`, `no reply` or `thanked` when it ends — then
  clear Next touch with `--next-touch ""` so it drops off the due list.
- Chat mode: edit the Contacts table in profile §9 (same columns) and read
  the due Next touch dates by hand.
- Each week, send the number of touches on profile §8 "Weekly outreach
  target:" (`strategy.md` §5); check it at the weekly review
  (`pipeline.md` §4).

## 5. Templates — ≤ 150 words, fill every [placeholder] from the profile

Scan every drafted message with `ats_check.py --slop` (workspace mode; chat
mode: read it against `assets/slop-phrases.txt`) and replace every hit. Before
showing a referral ask, check it has exactly one result from profile §5 and
one question — a second result or an 'or …?' alternative is a hit; fix it.

**Referral ask**
> Hi [Name] — [shared context]. I'm applying for [role] on [team] at [Company] ([link]). I've spent [n] years on [Y], most recently [one sourced result from profile §5], which lines up with [one line from the posting]. Would you be open to referring me? I've attached my resume and a three-line summary you can forward as-is, so it takes two minutes. If the timing is wrong, no problem at all — thank you either way. [Your name]

One ask only. No posting chosen → keep [role], [link] and the posting line
as marked placeholders; don't turn the ask into a 'who's hiring' question.
Employers and tenure exactly as profile §5 states them.

**Application nudge** (≤ 60 words)
> Hi [Name] — I applied for [role] on [date] via [source]. [One sourced result from profile §5, as stated.] Is there an update on where it stands? Thanks, [Your name]

Quote the result as a plain past fact — no 'since then' or 'most recently'
the profile doesn't date.

**Informational chat**
> Hi [Name] — your [post / talk] on [topic] stuck with me, especially [one specific point]. I'm [one-line identity from profile §8], looking at [area] roles at [Company] and teams like it. Could I ask you three questions over 15 minutes in the next two weeks — how the team works, what a strong first year looks like, and what you'd want to see from a candidate? Happy to work around your calendar, or keep it to messages if that's easier. Thanks, [Your name]

**Recruiter reply**
> Hi [Name], thanks for reaching out — [role] sounds relevant; I'm [one-line identity]. Before I send my CV, could you share the client's name, the salary band and the work arrangement? My expected range is [range from answers.md] and my notice is [notice]. Please check with me before submitting my CV anywhere. I'm free to talk [two slots]. Best, [Your name]

**Re-engage**
> Hi [Name] — it's been a while since [last shared context]; [one genuine note about their news]. A quick update from me: [one sourced change — new role, shipped project]. I'm now looking at [target role] roles, and [Company] is on my list because [one company fact]. Could you point me to the right person on [team]? No pressure either way. [Your name]

**Thank-you**
> Hi [Name] — thank you for [the referral / the chat / the intro]. [One specific thing that helped and how you used it.] [Outcome so far: applied / screen on [date] / accepted an offer at [Company].] I'll keep you posted, and if I can return the favour — [a specific offer: an intro, a review] — just say. [Your name]

## 6. Recruiters and agencies — MY / SG etiquette

- Which agencies matter: `markets/my.md`, `markets/sg.md`. Answer good
  recruiter inbound fast: recruiter-sourced candidates interview at ~25%
  (Ashby).
- **Exclusivity**: one agency per employer. Ask for the client's name before
  any submission; never let two agencies submit the same CV to the same
  employer. Log with `--channel agency` and the client in Notes. Agree to
  market-wide exclusivity only for a named, short window.
- **Salary**: give the expected range from `answers.md`; never disclose
  current salary unless a form or rule requires it — then truthfully
  (`facts-policy.md` §6).
- **Counter-offers**: the agency is paid when the placement closes, so
  its advice leans that way; a counter from the current employer is
  handled in `post-offer.md` §4.
- **WhatsApp**: verify the recruiter first (LinkedIn profile, agency site,
  company email). Keep WhatsApp for scheduling; send the CV by email or
  the agency portal; never send an NRIC/IC or bank details before an
  offer. WhatsApp-first contact from an unverifiable sender is a scam
  signal (`sourcing.md` §5).
- **SG**: agency postings fell 18% while direct employers held flat — go
  direct first (ManpowerGroup via HRO, 2026).

## 7. Open to Work

Recruiters search "Open to Work" plus recent activity as intent signals
(Pin): the day-0 comments double as activity. Employed → the
recruiters-only setting; the public banner only when openness is safe.
Headline and settings: `profile-optimizer.md`.

Record: workspace mode ends with the `saved:` line (contacts +N); chat
mode regenerates the profile block.
