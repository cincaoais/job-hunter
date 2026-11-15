# Sourcing — the Scout role

Find fresh openings continuously, filter hard, and hand every survivor to the
Qualifier with its referral path attached. Recruiters screen day-one
applicants first and rarely revisit a pile; a posting under 48 hours old is
worth more than ten week-old ones.

## 1. The fallback ladder — say which rung you used

Work down this ladder and state the rung in the first line of the shortlist
("Source: search_jobs.py, 3 boards, --days 2").

1. **`search_jobs.py`**. Reads profile §1–§3 (location,
   market, keywords, boards, salary, dealbreakers), queries
   JobStreet MY/SG, MyCareersFuture (SG) and LinkedIn guest search, dedupes
   against `seen-jobs.json`, applies knockouts, and ranks by freshness:

   ```
   sh ${CLAUDE_SKILL_DIR}/scripts/jh search_jobs.py --markdown --days 2
   sh ${CLAUDE_SKILL_DIR}/scripts/jh search_jobs.py --keywords "data engineer" --country SG --days 7
   ```

   Flags: `--keywords --location --country MY|SG --days --salary-min
   --sources --pages --all --no-seen --json`. Defaults come from the
   profile; flags override. A second run the same day prints
   `0 new since last run` — add `--all` to see everything again.
2. **Scoped web search** — `site:my.jobstreet.com <role> <city>`,
   `site:sg.jobstreet.com …`, `site:mycareersfuture.gov.sg …`,
   `site:linkedin.com/jobs …`. Web search sees public listing pages only,
   never a logged-in feed; say so.
3. **The user pastes** postings or URLs. Save each with
   `sh ${CLAUDE_SKILL_DIR}/scripts/jh fetch_posting.py <url> --save`
   so the Qualifier has the full text; `--stdin` accepts pasted text; exit 3
   means the page is blocked — ask for the text or suggest
   `pip install cloakbrowser`. Exit 4 with a message starting `unavailable:`
   means the board did not answer (try later or paste the text), while
   `not found:` means the job is gone.

Never answer from memory: listings and salaries change daily.

## 2. Reading the script's output

`search_jobs.py --markdown` prints:

- `## N new postings (M knocked out, S seen before)`
- the main table `# | Posted | Source | Company | Role | Location / mode |
  Salary | Link` — fresh first, then by salary, then by board priority
- `### Knocked out` — `Company — Role: reason`, where the reason is
  `dealbreaker: <phrase>` or `salary below floor` (checked only against pay
  in the floor's currency — the profile's, else the market's).
  Postings older than `--days` are dropped silently before this step and
  never listed. Knocked-out rows are not remembered as seen, so they
  reappear if the criteria change.
- `Sources: jobstreet 42 · mcf 10 · linkedin 12 (HTTP 429 at page 2,
  stopped) · mcf skipped: SG only` — count first, warnings in parentheses.
  Read this line every time; a board that stopped early means the shortlist
  is partial. A source line that says "cards found but none parsed — the
  page format may have changed" means that board's results are missing this
  run; tell the user rather than reporting a quiet market.

## 3. Freshness and cadence

- Daily: `--days 2`. Weekly sweep: `--days 7`. Postings under 48 hours old
  go first; anything older than 30 days is a repost until proven otherwise.
- Optional: a recurring digest with Claude Code's
  `/loop 1d /job-hunter:search` or a `/schedule` routine; each run shows
  only what is new since the last.
- Weekly cap: 10–20 targeted applications. 11–20 applications → ~9%
  interview rate, 100+ → ~2.6% (Huntr Q1 2026, 140k applications); the
  freed time goes to outreach (`networking.md`).
- One shot per company: never apply twice to the same company in one search
  cycle; re-applying to the same company halves the response rate (Huntr Q1
  2026). Check `pipeline.md` first.

## 4. Route to the direct channel

A board listing is often a mirror of the company's own careers page. Before
applying, find the direct posting (career page, Greenhouse/Lever/Workday
link) and apply there: Easy Apply 1–4% vs direct 2–3× (Huntr/LinkedIn
data). Log `Source` as the place the application actually went (`career
page`, not `LinkedIn`).

Agencies are a real channel in MY/SG — which agencies: `markets/my.md`,
`markets/sg.md`; how to work with them: `networking.md` §6.

## 5. Legitimacy — flag it, never present it clean

Check every shortlist row; a hit goes in the Red flags column, and a scam
stays off the shortlist entirely.

Ghost-job signals: reposted for more than 30 days; vague team or scope; no
hiring manager or named team; "always hiring" evergreen wording; the same
ad across many cities. Scam signals: pay far above market for vague work;
off-platform contact (WhatsApp/Telegram first); requests for personal or
banking details before an interview; upfront fees for training, kit or
"processing"; pressure to decide today. A MyCareersFuture applicant count
above 200 is a competition signal, not a ghost signal — mention it, do not
drop the row.

## 6. Present the shortlist

Add the judgment columns to the script's table and keep it short — a
high-fit dozen beats a noisy fifty, with one or two stretch targets:

| # | Posted | Source | Company | Role | Location / mode | Salary | Fit /10 | Why it matches | Red flags | Link |

- `Fit /10` scores against §2/§3; `Why it matches` names the must-haves
  hit and any stretch; `Red flags` holds §5 findings or "—".
- For every row scoring 7+, give the referral path (`networking.md`): two
  LinkedIn people-search links the user opens themselves —
  `https://www.linkedin.com/search/results/people/?keywords=<Company>%20recruiter`
  (talent acquisition — the referral ask) and the same URL with
  `<Company>%20<role keyword>` (likely teammates — the warm intro), keywords
  URL-encoded. These are searches, not found people: never claim a specific
  person was found and never fetch the result pages.
- Offer to save chosen rows (`tracker.py add --company X --role Y --source S
  --channel cold --stage saved`) and to fetch the full posting for the
  Qualifier (`sh ${CLAUDE_SKILL_DIR}/scripts/jh fetch_posting.py <url>
  --save`).

## 7. Feed forward

- Saved rows go to `jd-match.md` for the knockout pre-check before anything
  is drafted.
- Every high-fit row gets a referral attempt logged in `contacts.md` before
  the application goes out (`networking.md`).
- A search that keeps returning the same knockouts or an empty main table is
  a targeting signal — hand it to `strategy.md`, not to more searching.
- Keep politeness: every host is rate-limited to about one request per
  second. LinkedIn additionally pauses 2.5 s between pages and stops at 3
  pages, so `--pages` above 3 has no effect there. Board APIs and a
  posting's first fetch attempt identify as `job-hunter-skill`; LinkedIn's
  guest pages and the generic-page retry send a browser User-Agent, because
  those pages return nothing to a non-browser client.
