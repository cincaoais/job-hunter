# Company Dossier — Harbour Payments

_Researched: 2026-06-01_

> TEST FIXTURE — fictional company and facts, written for the r-workspace
> scenarios. Not real research.

| | |
|---|---|
| Company / size / stage | Harbour Payments — about 140 staff, Series B, Kuala Lumpur |
| Product & who pays | Payout and settlement APIs for marketplaces; merchants pay a per-payout fee |
| Recent news (12 mo) | Opened a second office in Penang; launched same-day payouts to three banks |
| Stack & team | Go, PostgreSQL, AWS (SQS, RDS); payments platform team of about 12 |
| Salary intel for the role | Senior backend engineer, KL: RM 10,000–13,000 / month (anecdotal, job-board bands) |
| Interview process (anecdotal) | HR screen, then system design with two senior engineers, then a hiring-manager round |
| Red flags | None found; on-call is shared across the whole platform team |

## Why they're hiring
Same-day payouts doubled payout volume, so the payouts service needs a
dedicated owner and reconciliation has to keep pace. That is the interview's
real topic.

## Likely themes
- **Reliability under retries** — idempotent payout and webhook handling (profile §5: webhook retry queue).
- **Reconciliation design** — batch versus near-real-time, trade-offs named.
- **Latency and performance** — query and caching work (profile §5: dashboard API latency).
- **On-call and SLOs** — how incidents were handled and alerting set.

## Questions to ask
- How did on-call change after same-day payouts launched?
- What does reconciliation lag look like today, and who owns closing it?
- Which SLOs does the payouts service carry, and who sets them?
