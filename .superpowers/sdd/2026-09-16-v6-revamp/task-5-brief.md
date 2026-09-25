### Task 5: Rewrite `SKILL.md` and create the eleven verb skills

**Files:**
- Rewrite: `skills/job-hunting/SKILL.md`
- Create: `skills/{search,match,resume,cover,network,interview,company,offer,today,review,help}/SKILL.md`

**SKILL.md content requirements (write it, < 300 lines):**
1. Frontmatter: `name: job-hunting`; `description` ≤ 1024 chars, third person, keeps today's trigger phrases and adds "daily job digest", "who should I contact", "what should I do today", "resignation letter", "30-60-90 plan"; `metadata: {version: "6.0.0", author: "Johannes Tang + Claude"}`.
2. **Storage modes** section: workspace mode (Claude Code; run `python3 ${CLAUDE_SKILL_DIR}/scripts/workspace.py where` at session start; if missing offer `init`; edit files in place; end with a one-line "saved:" summary) vs chat mode (claude.ai; `candidate-profile.md` in Project knowledge; regenerate full profile block at end). Detection rule: file tools available and a workspace resolves → workspace mode; otherwise chat mode.
3. **Memory rules** (from today's Step 0/1/1.5, condensed): read profile first; ingest documents before asking; grouped questions with options; echo assumptions; never re-ask; contradiction → conservative reading; facts policy link.
4. **The loop — nine roles** table: role → when it triggers → reference file → script (if any). Exactly the spec §1 table plus a "Say" column with one example phrase each.
5. **Sourcing summary** (3 lines) pointing at `references/sourcing.md` and the `search_jobs.py` command line.
6. **Honesty guardrail** one paragraph pointing at `references/facts-policy.md`.
7. **Principles** (keep today's six, add: "Referral before application", "Fresh beats broad: postings < 48 h first", "Ten targeted a week beats fifty sprayed", "Log every touch — the funnel is the coach").
8. Closing step per mode.

**Verb skill template** (each file; adjust `argument-hint`, the role line, and the reference name):

```markdown
---
name: search
description: Find fresh job openings matching the saved criteria, ranked with fit and red flags. Runs the job-hunting skill's Scout role.
argument-hint: [role or location tweaks]
disable-model-invocation: true
---

Use the `job-hunting` skill, role **Scout** (`references/sourcing.md`). Tweaks: $ARGUMENTS

1. Resolve storage mode (workspace: `python3 ${CLAUDE_SKILL_DIR}/../job-hunting/scripts/workspace.py where`).
2. Read the profile's search criteria; echo them in one line; apply tweaks.
3. Workspace mode: run `python3 ${CLAUDE_SKILL_DIR}/../job-hunting/scripts/search_jobs.py --markdown` and present the shortlist it prints, adding fit reasoning and referral paths per `references/networking.md`. Chat mode: follow the fallback ladder in `references/sourcing.md`.
4. Offer to save chosen rows to the pipeline (`tracker.py add`) and to fetch full postings (`fetch_posting.py`).
```

Verb → role → reference → script:
| verb | role | reference | script |
|---|---|---|---|
| search | Scout | sourcing.md | search_jobs.py |
| match | Qualifier | jd-match.md | fetch_posting.py (if a URL is given) |
| resume | Writer | resume-builder.md / resume-revamp.md | build_resume.py, ats_check.py |
| cover | Writer | resume-builder.md (cover letters) + answer-bank.md | — |
| network | Networker | networking.md | tracker.py contacts |
| interview | Coach | interview-prep.md / interview-coach.md ("mock") | — |
| company | Coach | company-dossier.md | — |
| offer | Negotiator | offer-coach.md | — |
| today | Operations | pipeline.md | `!python3 ${CLAUDE_SKILL_DIR}/../job-hunting/scripts/tracker.py today` inline before the body |
| review | Operations | pipeline.md | `!python3 ${CLAUDE_SKILL_DIR}/../job-hunting/scripts/tracker.py funnel` inline |
| help | — | the nine-role table in SKILL.md | — |

`help/SKILL.md` body: print the nine-role table with a "Say" column and the `/job-hunter:*` verbs, then ask which one.

- [ ] **Step 1: Write SKILL.md and the eleven verb skills as specified.**
- [ ] **Step 2: Run `python3 build.py --check`** → `OK: 12 skills pass checks`.
- [ ] **Step 3: Run `python3 -m pytest -q`** → all pass.
- [ ] **Step 4: Commit**

```bash
git add skills
git commit -m "SKILL.md v6 router (nine roles, storage modes) + verb skills replacing commands

Co-Authored-By: Claude Fable 5.1 <noreply@anthropic.com>"
```

---

## Phase 2 — Scout & Operations scripts

