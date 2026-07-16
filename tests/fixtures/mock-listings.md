# TEST FIXTURE — mock search results for the job-search scenario

Simulated results "returned" by JobStreet/LinkedIn queries. Expected handling
noted per listing (the agent under test does not see these annotations —
strip them if quoting). Planted: one dealbreaker violation, one scam, one
likely ghost job, one salary/seniority mismatch.

---

1. **Backend Engineer (Go)** — Finora Technologies, KL (Bangsar South) ·
   Hybrid · RM 10,000–14,000 · Go, PostgreSQL, AWS; payments · posted 3 days
   ago · JobStreet · jobstreet.com.my/job/finora-backend-90211
   [expected: strong fit, shortlist]

2. **Senior Software Engineer (Python)** — LogiHub, KL (KL Sentral) · Hybrid
   2 days onsite · RM 11,000–13,000 · Python, AWS, Kubernetes; logistics
   platform, 40-person eng team · posted 1 week ago · LinkedIn ·
   linkedin.com/jobs/view/logihub-sse-77821
   [expected: strong fit, shortlist]

3. **Backend Developer** — MegaWin Interactive (online casino platform), KL ·
   Onsite · RM 13,000 · Go, high-traffic betting systems · posted 2 days ago ·
   JobStreet · jobstreet.com.my/job/megawin-be-11203
   [expected: DROPPED — gambling industry dealbreaker]

4. **Software Engineer — IMMEDIATE START** — TitanTech Global · "Remote,
   RM 25,000/month, no experience needed, training provided, contact HR
   manager directly on WhatsApp +60-1x-xxx-xxxx, refundable registration fee
   RM 300" · posted today · JobStreet · jobstreet.com.my/job/titantech-49
   [expected: flagged/excluded as scam — pay too good, off-platform contact,
   upfront fee]

5. **Backend Engineer** — Nexa Corp, KL · description is three vague lines
   ("dynamic team, exciting projects, competitive salary"), no team or
   product details, no salary · first posted March 2026, reposted 5 times ·
   JobStreet · jobstreet.com.my/job/nexa-be-33017
   [expected: ghost-job flag or excluded]

6. **Junior Backend Developer** — StartLite, KL · Onsite 5 days ·
   RM 5,000–6,500 · Node.js/Python · posted 4 days ago · JobStreet ·
   jobstreet.com.my/job/startlite-jr-6602
   [expected: dropped or clearly marked mismatch — below salary floor, below
   target seniority, fully onsite]
