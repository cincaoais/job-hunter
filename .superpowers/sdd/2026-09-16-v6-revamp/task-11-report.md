# Task 11 report — facts-policy, strategy, networking, answer-bank, post-offer

Status: DONE_WITH_CONCERNS (concerns are minor; listed at the end)
Commit: a152c8d `references: facts policy, strategy/career map, networking sequences, answer bank, post-offer` (base 8668a2f, trailer `Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>`)

## Files

| File | Lines | Notes |
|---|---|---|
| `skills/job-hunting/references/facts-policy.md` | 119 | new: one source of facts, ask-don't-estimate, estimates "(est.)", claims audit (list → cite → keep/soften/ask/drop → one-line report), interviews, negotiation, decline table, record |
| `skills/job-hunting/references/strategy.md` | 149 | new: intake, through-line, level check, career map (30 roles as adjacency rows + S/M/L gap rule + non-tech instruction), cadence contract on §8, target list 15–25, when to revisit |
| `skills/job-hunting/references/networking.md` | 132 | new: referral-first rule (with fresh-posting fast path), referral map + LinkedIn links, day 0/2/5/12 sequence, logging with `tracker.py contact`/`contacts`, 5 templates, MY/SG recruiter etiquette, Open to Work |
| `skills/job-hunting/references/answer-bank.md` | 103 | new: where answers live per mode, intake table, per-posting tailoring, knockouts, form mechanics (Workday, Greenhouse/Lever, JobStreet, MCF `screening_questions`, Easy Apply), never auto-submit, refresh |
| `skills/job-hunting/references/post-offer.md` | 148 | new: accept-in-writing checklist, resignation letter, notice (MY/SG + buyout, leave, garden leave, handover), counter-offer, references, background check, 30-60-90, probation, pipeline closure + withdrawal template |
| `skills/job-hunting/assets/profile-template.md` | +2 / ~1 | §8 gains `- **Weekly application cap:** (10–20 targeted; see strategy.md)` and `- **Weekly outreach target:** (e.g. 6 touches; 60/40 outreach to applications)`; §2 hint "see the role map" → "see the career map in strategy.md" |
| `skills/job-hunting/references/tech-role-map.md` | deleted (`git rm`) | content restructured into strategy.md §4 |

All five within the brief's 60–150 budget; LF endings; no XML tags; trailing newline; no trailing whitespace. Template word counts (networking): referral ask 85, informational 84, recruiter reply 62, re-engage 71, thank-you 63; post-offer withdrawal 36; resignation letter ~60 — all ≤150.

## Every statistic used, with its source (all from research-notes.md)

| Figure | Where | Source cited |
|---|---|---|
| 11–20 apps → ~9% interview, 100+ → ~2.6% | strategy §5 | Huntr Q1 2026, 140k applications (matches sourcing.md) |
| 66% of offers within 50 applications | strategy §5 | Huntr Q1/Q2 2026 |
| median search 82–108 days | strategy §5 | Huntr Q1/Q2 2026 |
| burnout main attrition risk; process goals + batching + rest | strategy §5 | Duke career centre 2025; Huntr Q1 2026 |
| 46% have under 3 months runway | strategy §5 | Duke career centre 2025; Huntr Q1 2026 |
| targeting leak = response <10% after 10+ sent | strategy §7 | tracker.py rule (pipeline.md §5) |
| cold ~3% vs referral ~40% interview | networking intro | Ashby, 38M applications, 2025/26 |
| referrals <1% of applications | networking intro | Pin |
| day-one screened first, day-two skim | networking §1 | Blind recruiter AMA 2026 |
| referral offer rate 7.3% vs 0.2% | networking §1 | Ashby |
| referred hires close 29 vs 44 days | networking §1 | Pin |
| 150–199 words perform best | networking §3 | Pin |
| three touches capture ~93% of replies | networking §3 | Pin |
| LinkedIn ~17% vs email ~5–6%; email+LinkedIn ~46% vs ~20% email-only | networking §3 | Pin, 4M messages, Jun 2025–May 2026 |
| recruiter-sourced ~25% interview | networking §6 | Ashby |
| SG agency postings −18%, direct flat | networking §6 | ManpowerGroup via HRO, 2026 |
| Open to Work + activity as intent signals; recruiters-only when employed | networking §7 | Pin |
| 92% of recruiters configure no content-based auto-reject; knockouts reject | answer-bank §4 | Hiration/Huntr |
| 18% of Huntr users had an offer withdrawn | post-offer §1 | Huntr Q1 2026 |
| MY notice floor 4/6/8 weeks (<2, 2–5, >5 yrs); contracts commonly 1–3 months; notice applies in probation unless contract says otherwise | post-offer §3 | Employment Act s.12 (research-notes, Malaysia 2026) |
| SG 1–2 weeks in probation, ~1 month after; statutory 1 day → 4 weeks; TAFEP flags long junior notice | post-offer §3 | Employment Act (research-notes, Singapore 2026) |

Non-statistical market facts used, all from research-notes: seekAI ranking inputs and the approachability signal (MY boards bullet), MCF min/max bands and screening questions, JobStreet single-number salary field (via v5 notes, linked to `markets/my.md`), MY confirmation letter, SG KETs, NRIC never on a CV / SG work-status wording.

Numbers that are practice rules or binding decisions, not data: weekly cap 10–20, 60/40, "e.g. 6 touches" (controller), 15–25 companies, day 0/2/5/12 and ≤150 words (controller), follow-up 7 days after a direct message (same 7-day gap as the table), "5–10 target postings" for the level check, example numbers inside templates/examples (placeholders or illustrative).

## Commands and output

```
$ grep -rn "tech-role-map" skills/        → no output (exit 1)
$ python3 build.py --check               → OK: 12 skills pass checks
$ python3 -m pytest -q -m "not network"  → 275 passed in 0.74s
$ wc -l references/{facts-policy,strategy,networking,answer-bank,post-offer}.md
  119 / 149 / 132 / 103 / 148
```

Also verified in a scratch workspace (`JOB_HUNT_DIR` in the scratchpad): `tracker.py contact … --next-touch 2026-09-27 --status c` creates the row, `tracker.py contacts --today 2026-09-28` lists it, and `tracker.py contact --name … --company … --next-touch "" --status "no reply"` clears it off the due list — the "then stop" instruction in networking.md §4 works as written. Help text for `contact`, `contacts`, `set` checked; every flag cited exists.

## Self-review

- **Sources**: every number above carries its research-notes source in parentheses; no number outside research-notes was introduced as data.
- **SKILL.md**: storage modes honoured in every file (workspace: `${CLAUDE_SKILL_DIR}/scripts/…` commands + `saved:` line; chat: profile §9 tables, regenerate block, never claim a script ran — said explicitly in facts-policy §4 and answer-bank §6). Grouped-batch asking, never re-ask, conservative reading and write-back rules are reused, not restated. Nine-role table: Strategist → strategy.md, Networker → networking.md (+ `tracker.py contacts / contact`), Writer → answer-bank.md, Onboarder → post-offer.md topics all covered.
- **facts-policy is the single owner**: the other four files link it in one line (plus targeted section links such as "facts-policy §6" for salary/leverage) rather than restating the mechanism.
- **sourcing.md**: LinkedIn people-search link text copied verbatim (plus an alumni variant in the same pattern); "7+ rows get a referral path", one shot per company, legitimacy checks and fallback ladder referenced, not redefined.
- **pipeline.md**: §8 line labels match pipeline.md §4 exactly; Offers table location (`## Offers` in pipeline.md) matches; stage vocabulary (`accepted`, `withdrawn`, `referral`, `agency` channels) matches; runway/rest rules linked to pipeline.md §6 instead of restated; follow-up after acceptance uses `--next`/`--due` consistent with offer-coach's "notice countdown as next action".
- **Forbidden links**: none of feature-guide / tech-role-map / sea-market-notes / candidate-profile-template appear. Links used: existing references, SKILL.md, `markets/my.md`, `markets/sg.md`, `markets/_template.md`, `markets/<cc>.md`, workspace files.

## Concerns

1. **Word-count tension (networking §3)**: the binding cap is ≤150 words, while Pin's best band is 150–199. I kept the cap and wrote "use the room … Pin found 150–199 words perform best, so a two-liner is too thin" rather than hide the data. If the controller prefers, drop the Pin sentence or lift the cap.
2. **"(est.)" in sent documents (facts-policy §3)**: the label is mandatory in profile, drafts and audit; in the version the user sends it may become a visible approximation ("~150", "about 150") but never a bare precise figure. Reviewer may want "(est.)" kept verbatim everywhere.
3. **Chat-mode Answers section**: answer-bank and facts-policy put chat-mode answers in an `### Answers` section under profile §9 (per the design spec, "answers tables live as sections of that file"), but `profile-template.md` §9 has no such section yet. A later task (13 or 17) may want to add it to the template.
4. **Target-list home**: strategy §6 records the tiered 15–25 list on the existing §2 "Dream companies" line as three `Dream:/Realistic:/Fallback:` lines — no new template field was added (brief allowed only the two §8 lines).
5. **Overlap with Task 12**: sourcing.md says agency handling lives in `markets/my.md`/`sg.md`; networking §6 now holds the etiquette (per this brief) and links markets files for the agency list. Task 12 should list agencies and point to networking.md §6 for etiquette rather than duplicate it.
6. **Out of scope, noticed**: `README.md:85` still mentions "Role Map" (README is outside `skills/`; Task 17). `application-guide.md` still says "help them estimate honestly" and links sea-market-notes — Task 13 pointer edits should replace that with the facts-policy link.
7. Career-map Gap letters (S/M/L) are judgment labels, not data; the file tells the model to recompute them from the profile.

---

## Fix round 1 — commit 07c8f52 `references: link markets instead of copying, template homes for answers and target list`

Status: DONE (10 of 10 items addressed; nothing still open)

| # | Finding / ruling | Fix |
|---|---|---|
| 1 (Important) | post-offer restated MY/SG notice floors | §3's MY and SG bullets are replaced by one line: "Statutory floors, probation notice and typical contract terms: `markets/my.md`, `markets/sg.md` (other countries: `markets/_template.md` plus a live search)". Kept only the market-neutral mechanics: buyout, unused-leave offset, garden leave, handover. §6 SG work-status wording → "Work-status wording: `markets/my.md`, `markets/sg.md`". §8 MY confirmation letter / SG KETs → "How confirmation is documented per market: `markets/my.md`, `markets/sg.md`". The Employment Act and TAFEP figures are no longer in post-offer.md. |
| 2 (Important) | sourcing.md agency pointer | Now reads "Agencies are a real channel in MY/SG — which agencies: `markets/my.md`, `markets/sg.md`; how to work with them: `networking.md` §6." |
| 3 | "(est.)" wording | facts-policy §3: **internal records** (profile, `answers.md` / chat-mode Answers section, the claims-audit table) always carry "(est.)"; **outbound text** (resume, cover letter, outreach, the form answers the user submits) writes "~150" or "about 150", never a bare figure. |
| 4 | template homes | profile-template: `- **Target list:** (15–25 companies: dream / realistic / fallback — see strategy.md)` after Dream companies; `### Answers` subsection under §9 with the given one-line blockquote (placed after Contacts); the §9 note "keep the three tables below" → "keep the sections below" (it was already inaccurate, since there were four tables). strategy §6 now records on the profile §2 "Target list:" line. SKILL.md chat-mode sentence now lists "…soft-skills tables and the Answers section" (one edit; description untouched; 138 lines). |
| 5 | bare § numbers | Every profile section reference in strategy.md and answer-bank.md now reads "profile §N". The remaining bare § numbers are the file's own sections or `file.md` §N links. Also applied to facts-policy's audit examples, post-offer §6/§9 and networking's informational template. |
| 6 | networking | "Days are absolute, counted from the first touch (0, 2, 5, 12)" above the table; "keep the later days"; fast path: "not yet connected → the ask goes in the connection note". Referral-ask template now asks only "Would you be open to referring me?". Re-engage asks only "Could you point me to the right person on [team]?". Status vocabulary gains `thanked`. |
| 7 | answer-bank headings | The intake table column is now "Heading in `answers.md`", using the template's exact headings (Notice period / earliest start, Why leaving (current/last role), Years in each tool / skill). Added `## Essay prompts` (heading + one-line hint + `-`) to `answers-template.md` between STAR stories and References. The table order matches the template. |
| 8 | facts-policy option (a) | "(a) has no floor → write it without the number." |
| 9 | strategy | Hours a week go on the profile §8 "Weekly application cap:" line (e.g. "12 — 8 h/week"). The three bullets that restated pipeline.md §6 (90 days, batch-and-rest, runway) are collapsed into one link line: "**Pacing** — the ~90-day expectation, batch-and-rest, rest weeks and runway-aware urgency: agree them from `pipeline.md` §6." Typical-stack hints are back in the role labels (React / Vue / Angular; Java, Go, Python, Node, C#; Swift / Kotlin / Flutter; C / C++, Rust; Unity / Unreal; SQL + Tableau / Power BI / Looker; dbt; Spark / Airflow / dbt; CI/CD, Terraform; AWS / GCP / Azure + Terraform) with the note "Parentheses give the typical stack". The label is now "ML engineer / applied scientist". |
| 10 | post-offer contacts status | "…then set their Status to `thanked` and clear Next touch (`tracker.py contact --name … --status thanked --next-touch ""`; chat mode: the Contacts table)." |

Statistics after the fix: the three Duke/Huntr lines left strategy.md with the pacing paragraph, namely "median 82–108 days", "burnout main attrition risk" and "46% under 3 months runway". pipeline.md §6 still carries the 82–108 figure. post-offer no longer quotes any notice figures. No new numbers were added.

Verification:

```
$ grep -rn "tech-role-map" skills/        → no output (exit 1)
$ python3 build.py --check               → OK: 12 skills pass checks
$ python3 -m pytest -q -m "not network"  → 275 passed in 0.62s
$ wc -l facts-policy / strategy / networking / answer-bank / post-offer → 121 / 146 / 135 / 104 / 143 (SKILL.md 138)
CRLF: none; forbidden links: none
```

Templates after the fix (words): referral ask 78, informational 85, recruiter reply 62, re-engage 64, thank-you 63, all within the 150-word limit.
