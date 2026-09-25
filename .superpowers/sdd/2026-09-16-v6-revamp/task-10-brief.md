### Task 10: `sourcing.md`, `pipeline.md`, and the `today`/`review` skills' inline commands

**Files:**
- Create: `skills/job-hunting/references/sourcing.md`, `skills/job-hunting/references/pipeline.md`
- Modify: `skills/today/SKILL.md`, `skills/review/SKILL.md` (add the inline `!` command lines), `skills/job-hunting/SKILL.md` (remove any leftover funnel/ghost text now owned by these files)

**`sourcing.md` must contain:** (1) the fallback ladder: `search_jobs.py` → connected MCP job tools (Reactive Resume tracker, LinkedIn MCP, Workopia) → web search scoped per board (`site:my.jobstreet.com`, `site:sg.jobstreet.com`, `site:mycareersfuture.gov.sg`) → user pastes; state which rung was used; (2) freshness rule: run with `--days 2` daily, `--days 7` weekly; postings < 48 h first; recurring digest via `/loop 1d /job-hunter:search` or `/schedule`; (3) route to company career page / direct ATS link when the board is a mirror (Easy Apply converts 1–4%, direct 2–3× better; log Source accordingly); (4) ghost/scam heuristics (moved from SKILL.md): reposted > 30 days, vague team, no hiring manager, pay too good, off-platform contact, upfront fees, MCF applicant count > 200 as a competition signal not a ghost signal; (5) one-shot-per-company rule and weekly cap 10–20 targeted; (6) agency channel per market (link to `markets/*.md`); (7) shortlist presentation table (today's columns plus Posted and Source) and the per-row referral links (`https://www.linkedin.com/search/results/people/?keywords=<Company>%20recruiter` and `<Company>%20<role keyword>`), still framed as searches not found people.

**`pipeline.md` must contain:** schema and stage vocabulary; rules: log every application the day it goes out with Source + Channel + Resume version; Next action + Due always set; follow-up nudge at Due + 7 days, one polite nudge only; auto-cold at 21 days silent; interviews get a Due = interview date; the **today view** (what `tracker.py today` prints and how to act on each section); the **weekly review ritual** (Monday: `tracker.py digest`, read the funnel, apply the one change, set next week's cap and outreach target — ratio 60/40 outreach to applications); **leak diagnosis** table mapping each branch to its fix; benchmarks with sources; **cadence & wellbeing**: weekly cap, batch-and-rest, runway-aware urgency (< 3 months runway → widen targets, add agencies/contract roles; > 6 months → hold the bar), rejection reframing lines, when to suggest a rest week (three rejections in a week or two weeks of zero responses).

- [ ] **Step 1: Write both references; wire the inline commands.**
- [ ] **Step 2: `python3 build.py --check` and pytest pass; commit** — `sourcing.md + pipeline.md: fallback ladder, freshness, cadence, funnel diagnosis; today/review skills run tracker first`.

---

## Phase 3 — New and revised references

