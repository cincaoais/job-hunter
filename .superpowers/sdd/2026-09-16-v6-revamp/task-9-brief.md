### Task 9: `tracker.py`

**Files:**
- Create: `skills/job-hunting/scripts/tracker.py`
- Test: `tests/test_tracker.py`, fixture `tests/fixtures/pipeline-sample.md` (8 rows across stages/channels/sources with dates relative to a fixed `--today 2026-09-16`)

**Interfaces (CLI):**
- `tracker.py add --company X --role Y [--source S] [--channel C] [--stage saved] [--url U] [--next "..."] [--due D] [--resume R] [--notes N]` → appends row (Last touch = today).
- `tracker.py set --company X [--role Y] --stage S | --next "..." --due D | --note "..." | --resume R | --applied D` → updates matching row(s), Last touch = today.
- `tracker.py today [--today YYYY-MM-DD]` → sections: **Overdue** (Due < today, stage not terminal), **Due today**, **Interviews within 7 days** (stage in screen/interview/final with Due within 7d), **Stale** (Last touch > 7 days, stage applied/screen/interview/final), **Auto-cold candidates** (stage applied, Last touch ≥ 21 days) with the exact `set` command to apply, **Contacts due** (from contacts.md Next touch ≤ today), **Fresh postings**: line telling the user to run `search_jobs.py --days 2`.
- `tracker.py funnel [--today D]` → table `Channel | Sent | Responses | Interviews | Offers | Response % | Interview %` (channel = Channel column; "Sent" = stage ≠ saved; Responses = stage ≥ screen or rejected-after-applied is ambiguous → count rejected as response only if Notes contains "reply"/"rejected by"; keep rule simple and documented), same by Source, benchmarks line (`cold ~3% interview, referral ~40%, recruiter-inbound ~25% — Ashby 2025/26`), **leak diagnosis**: pick the first failing stage: sent ≥ 10 and response % < 10 → "targeting/resume"; responses ≥ 3 and interviews == 0 → "screen performance"; interviews ≥ 3 and offers == 0 → "close/negotiation"; else "pipeline too small to diagnose (n<10)"; one recommended change per diagnosis (fixed strings from `references/pipeline.md`).
- `tracker.py digest [--today D]` → writes `reviews/<today>.md` containing funnel + today sections + "Last weekly review" line updated in `pipeline.md`.
- `tracker.py contacts [--today D]` → contacts whose Next touch ≤ today, sorted.
- Functions: `load(ws) -> (cols, rows)`, `save(ws, cols, rows)`, `today_report(rows, contacts_rows, today: date) -> str`, `funnel(rows) -> dict`, `diagnose(f: dict) -> tuple[str, str]`.

- [ ] **Step 1: Tests** — add then set round-trip in a tmp workspace; `today_report` on the fixture lists the planted overdue/stale/auto-cold rows and not the terminal ones; `funnel` counts per channel match hand-computed numbers; `diagnose` returns each of the four branches on crafted dicts; `digest` writes the file and updates the review line.
- [ ] **Step 2: Implement, run, commit** — `tracker.py: pipeline add/set/today/funnel/digest/contacts over markdown tables`.

