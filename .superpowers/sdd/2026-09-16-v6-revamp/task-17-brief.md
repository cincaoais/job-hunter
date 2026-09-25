### Task 17: README, PROJECT-DESCRIPTION, version bump, tag

**Files:**
- Rewrite: `README.md`
- Modify: `docs/PROJECT-DESCRIPTION.md`, `skills/job-hunting/SKILL.md` (metadata.version `6.0.0`), `.claude-plugin/plugin.json` (already 6.0.0)

**README sections:** What it is (one paragraph + the nine-role table); Install — Claude Code (`claude plugin marketplace add cincaoais/job-hunter` → `claude plugin install job-hunter@job-hunter`; or clone + `python3 build.py --link`); Install — claude.ai (download `job-hunting.skill` from Releases or `python3 build.py`, upload in Settings → Features, paste `docs/PROJECT-DESCRIPTION.md` into a Project); First run (`/job-hunter:help`, `/job-hunter:today`, `python3 …/workspace.py init`); Scripts table (name, one line, optional extras); Daily/weekly loop (today → search → match → apply/network → review); Windows note (`python build.py`, PowerShell paths, symlink fallback copies); Layout table; Development (pytest, `build.py --check`, release by tag); What it deliberately does not do (auto-apply, interview copilots, logins, scraping blocked boards).

**PROJECT-DESCRIPTION.md:** keep today's voice; update the capability list to the nine roles; state chat-mode memory rule (regenerate profile block); mention that in Claude Code the same skill uses `~/job-hunt` files instead.

- [ ] **Step 1: Write docs; bump version; `python3 build.py --check && python3 -m pytest -q -m "not network" && python3 build.py`** → OK, all pass, zip built.
- [ ] **Step 2: Commit and tag**

```bash
git add -A
git commit -m "v6.0.0: docs, version bump

Co-Authored-By: Claude Fable 5.1 <noreply@anthropic.com>"
git tag -a v6.0.0 -m "v6.0.0 — nine-role job hunter with bundled scripts"
```
(Do not push; the user pushes.)

---

## Self-review

- **Spec coverage:** §1 roles → Tasks 5, 10, 11, 13; §2 layout/build → Tasks 1–3, 17; §3 storage → Task 4, 5; §4 references → Tasks 10–13; §5 scripts → Tasks 6–9, 14, 15; §6 verb skills → Task 5, 10; §7 exclusions → README (Task 17); §8 testing → every task + Task 16; §9 phases → plan order. Gmail/Calendar opportunistic mention → `sourcing.md`/`pipeline.md` one line each (Task 10).
- **Placeholders:** none; markdown-content tasks list the exact required sections and rules.
- **Type consistency:** normalized job dict keys (Task 6) are used unchanged by Tasks 7, 8; `read_table/write_table` (Task 4) used by Task 9; `docx_text` lives in `_common.py` (Task 14) and is reused by Task 15's `extract_text`; stage vocabulary identical across Tasks 4, 9, 10, 13.
