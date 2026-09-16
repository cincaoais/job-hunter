---
name: help
description: Show what the job-hunting skill can do — the nine roles and the /job-hunter verbs — then ask which one to run.
disable-model-invocation: true
---

Use the `job-hunting` skill. Print this table, then ask which role the user wants (plain English works too — every role is also reachable by describing the task):

| Role | Say | Verb |
|---|---|---|
| Strategist — positioning, career map, cadence | "What roles should I aim for?" | (plain English) |
| Scout — fresh openings, daily digest | "Find me fresh openings this week" | `/job-hunter:search` |
| Qualifier — knockout check, legitimacy, fit verdict | "Am I a fit for this?" + posting | `/job-hunter:match` |
| Writer — resume tailor/revamp, HR-eye score, cover letter, answer bank | "Tailor my resume for this posting" | `/job-hunter:resume`, `/job-hunter:cover` |
| Networker — referral map, outreach, contacts | "Who can refer me at Grab?" | `/job-hunter:network` |
| Coach — prep pack, mock interview, company dossier, soft skills | "Mock interview me for Friday" | `/job-hunter:interview`, `/job-hunter:company` |
| Negotiator — true annual comp, compare, negotiate | "I got an offer — should I take it?" | `/job-hunter:offer` |
| Operations — today view, weekly funnel review | "What should I do today?" | `/job-hunter:today`, `/job-hunter:review` |
| Onboarder — resignation, references, 30-60-90 | "I accepted — what now?" | (plain English) |

Remind the user of the two ground rules: the profile (or `~/job-hunt` workspace) is the memory — every answer is written back; and the honesty guardrail — strongest true version of their experience, never invented metrics, titles or achievements. Then route into the chosen role's real flow rather than re-explaining it.
