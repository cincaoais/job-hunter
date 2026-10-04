# Interview Capability Implementation Plan

> **For agentic workers:** executed with `/orchestrate` — this session plans and reviews, Sonnet
> subagents implement independent tasks in parallel. Steps use checkbox (`- [ ]`) syntax.
> **No git:** this tree is not a checkout and the owner forbids git and GitHub commands; there
> are no commit steps.

**Goal:** Extend the Coach role with a persisted prep pack, anchored mock scoring, a debrief
flow, a derived question bank and a tested file contract that the career vault reads.

**Architecture:** Option C from the spec. All interview data lives in the workspace's
`interviews/`; one stdlib script `scripts/interview.py` owns file creation (`new`), outcome
updates (`outcome`) and the generated bank (`bank`); judgment stays in `references/interview-*.md`.
`interview.py` imports only `_common.py`.

**Tech Stack:** Python 3.10+ stdlib, pytest, markdown references and assets.

**Status:** approved by owner 2026-10-02 (Gate 3); no release — version stays 6.0.0.

**Spec:** `docs/superpowers/specs/2026-10-01-interview-capability-design.md` (approved
2026-10-02) plus cross-repo items J1–J4 from
`../obsidian-main/docs/2026-10-01-career-vault-design.md` §10 (approved 2026-10-02).

## Global Constraints

- No git or GitHub commands of any kind. Edit files in place.
- Test command (baseline 431 passed, 1 environmental failure):
  `python3 -m pytest -q -m "not network" --deselect tests/test_build.py::test_text_files_check_out_with_lf_everywhere`
  — the deselected test shells out to `git check-attr` and fails outside a checkout.
- Stdlib only. Every write uses `encoding="utf-8", newline="\n"`; files are LF only (`build.py --check` rejects CRLF).
- Scripts call `use_utf8_output()` first; exit 0 with `No workspace found — run: python3 <dir>/workspace.py init` when `pipeline.md` is missing; exit 2 for bad input, message on stdout (`tracker.py` convention).
- C1: `interview.py` imports only `_common`. C2: interview data only under `interviews/`; `pipeline.md` changes only via `tracker.py`. C3: interview references are `interview-*.md`. C4: every interview file carries `contract: 1`.
- Vocabularies, verbatim: kinds `prep mock debrief`; round types `hr-screen behavioral technical coding system-design case assessment final` (`assessment` is not a mock mode); outcomes `pending advanced rejected offer withdrawn`; themes `intro motivation strengths-weaknesses leadership conflict failure pressure initiative technical coding system-design case logistics salary curveball other`; landed `yes partly no`.
- File names: `interviews/<slugify(company + " " + role)>/<date>-<kind>-<round_type>.md`, `-2`, `-3` on repeats, never an overwrite.
- Interview files and templates contain no wikilinks (`[[`).
- Facts policy unchanged. Fixtures are fictional. Never read or write the developer's real workspace: tests set `JOB_HUNT_DIR` (and `HOME`/`USERPROFILE` where resolution is tested) to `tmp_path`.
- Router `SKILL.md` ≤ 500 lines, description ≤ 1024 chars (`build.py --check`).
- No version bump unless the owner approves at Gate 3; never tag.
- Write like the surrounding code: short docstrings, few comments, names from the existing scripts.

## Review Focus

1. Company or role typed with other casing or spacing than the pipeline row → `new` and `outcome` use the row's own text, so the slug and frontmatter are stable (Task 1, the lower-cased company in `test_new_writes_contract_file`).
2. Company names with quotes, colons or non-ASCII → frontmatter round-trips through `parse_frontmatter` (Task 1, `test_frontmatter_round_trips_awkward_names`).
3. Hand-edited debrief tables: `Landed` in capitals, a missing cell, story written as `none` → `bank` still counts correctly (Task 2, fixture rows in `test_bank_aggregates_debriefs`).
4. A workspace initialised before this release has no `interviews/` → `new` and `bank` create it (Task 2, `test_bank_on_a_workspace_without_interviews`).
5. A session started in a vault subfolder with no `JOB_HUNT_DIR` → `where` warns, `init` refuses to create the stray workspace (Task 3).

---

## File structure (after)

| Path | Responsibility |
|---|---|
| `skills/job-hunting/scripts/interview.py` | **new** — `new`, `outcome`, `bank` |
| `skills/job-hunting/scripts/workspace.py` | `interviews` in `DIRS`; stray-workspace warning and init refusal (J1) |
| `skills/job-hunting/assets/interview-prep-template.md` | **new** — prep pack body |
| `skills/job-hunting/assets/interview-mock-template.md` | **new** — mock scorecard body |
| `skills/job-hunting/assets/interview-debrief-template.md` | **new** — debrief body |
| `skills/job-hunting/assets/profile-template.md` | §9 `### Interviews` table; §9 note lists `interviews/` |
| `skills/job-hunting/assets/answers-template.md` | STAR lines carry `(themes: …)` |
| `skills/job-hunting/references/interview-prep.md` | persisted pack, story map and gaps, lessons, dossier freshness, debrief hand-off |
| `skills/job-hunting/references/interview-coach.md` | modes, anchored rubric, self-score first, scorecard |
| `skills/job-hunting/references/interview-debrief.md` | **new** — debrief, outcome, bank, handoffs, chat mode, file contract |
| `skills/job-hunting/references/company-dossier.md` | `_Researched:_` line and 30-day refresh |
| `skills/job-hunting/references/networking.md` | interviewer thank-you template |
| `skills/job-hunting/references/pipeline.md` | debrief-after-every-round line |
| `skills/job-hunting/references/strategy.md` | read career-vault playbooks before revising targets (J2) |
| `skills/job-hunting/references/markets/{_template,my,sg}.md` | §10 interview process norms |
| `skills/job-hunting/SKILL.md`, `skills/interview/SKILL.md`, `skills/help/SKILL.md` | Coach row, modes, init list, `where` warning rule |
| `README.md`, `docs/PROJECT-DESCRIPTION.md`, `docs/followups-v6.0.1.md` | docs |
| `tests/test_interview.py` | **new** |
| `tests/test_workspace.py` | `interviews/` and J1 tests |
| `tests/fixtures/scenarios/r-workspace/` | **new** fictional workspace |
| `tests/behavioral-scenarios.md` | scenarios R–U |

Dependencies: Task 1 → Task 2 (same file). Tasks 3–8 are independent of each other and of
1–2 (they use the CLI as specified here). Task 9 after 1. Task 10 after 4–9. Task 11 after
1, 4–6. Task 12 last.

---

## Phase 1 — Script and workspace (TDD)

### Task 1: `interview.py new` and `outcome`, templates, fixture workspace

**Files:**
- Create: `skills/job-hunting/scripts/interview.py`
- Create: `skills/job-hunting/assets/interview-prep-template.md`, `interview-mock-template.md`, `interview-debrief-template.md`
- Create: `tests/fixtures/scenarios/r-workspace/pipeline.md`
- Create: `tests/fixtures/scenarios/r-workspace/interviews/harbour-payments-senior-backend-engineer/2026-09-12-debrief-hr-screen.md`
- Create: `tests/fixtures/scenarios/r-workspace/interviews/harbour-payments-senior-backend-engineer/2026-09-28-mock-system-design.md`
- Test: `tests/test_interview.py`

**Interfaces:**
- Produces: `interview.main(argv: list[str] | None) -> int`; `interview.parse_frontmatter(text: str) -> dict[str, str]`; constants `KINDS`, `ROUND_TYPES`, `OUTCOMES`, `QUESTION_COLUMNS = ["#", "Question", "Theme", "Story used", "Landed"]`, `SCORE_COLUMNS = ["#", "Question", "Theme", "Self", "Coach", "Evidence"]`. CLI: `new --kind K --company C --role R --round-type T [--round N] [--date D] [--today D]` prints `created: <absolute path>`; `outcome --company C --role R --outcome O` prints `outcome: O — <path>`.

- [ ] **Step 1: Write the fixture workspace**

`tests/fixtures/scenarios/r-workspace/pipeline.md`:

```markdown
# Pipeline

> One row per company+role. Stages: saved · applied · screen · interview · final · offer · accepted · rejected · withdrawn · cold.
> Source = where the posting came from (JobStreet, MCF, LinkedIn, career page, agency, referral). Channel = cold / referral / recruiter-inbound / agency.
> Dates are YYYY-MM-DD. `Due` drives the today view. Never put `|` in a cell.
> TEST FIXTURE — fictional. Dates are relative to `--today 2026-10-01`.

_Last weekly review: 2026-09-28_

| Company | Role | Source | Channel | Applied | Stage | Next action | Due | Last touch | Resume | Notes |
|---|---|---|---|---|---|---|---|---|---|---|
| Harbour Payments | Senior Backend Engineer | career page | cold | 2026-08-25 | interview | Technical interview round 2 (system design) | 2026-10-03 | 2026-09-28 | harbour-backend-v1.md | Posting: postings/harbour-payments-senior-backend-engineer.md; round 1 HR screen passed 2026-09-12 |
| Lumen Logistics | Backend Engineer (Python) | JobStreet | recruiter-inbound | 2026-09-08 | screen | Recruiter screen call | 2026-09-30 | 2026-09-22 | lumen-backend-v1.md | Recruiter: Nadia Karim |
| Orchid Analytics | Backend Engineer | MCF | cold | 2026-08-10 | rejected | Closed | | 2026-09-01 | orchid-backend-v1.md | Rejected by email after the take-home |

## Offers

| Company | Role | Base / month | Bonus (contractual?) | True annual comp | Probation / notice | Deadline | Status |
|---|---|---|---|---|---|---|---|
```

`.../2026-09-12-debrief-hr-screen.md` (the contract fixture; note the hand-edited cells):

```markdown
---
contract: 1
kind: debrief
company: "Harbour Payments"
role: "Senior Backend Engineer"
round: 1
round_type: hr-screen
date: 2026-09-12
outcome: advanced
---

# Debrief — Harbour Payments · Senior Backend Engineer · hr-screen

## Questions asked

| # | Question | Theme | Story used | Landed |
|---|---|---|---|---|
| 1 | Tell me about yourself | intro | | Yes |
| 2 | Why are you leaving Moneta Pay? | motivation | | partly |
| 3 | What are your salary expectations? | salary | | yes |
| 4 | Tell me about a time you disagreed with your lead | conflict | none | no |
| 5 | When could you start? | logistics |

## What landed

The webhook retry-queue numbers.

## What didn't

The disagreement question — no story ready.

## Signals and next round

Round 2 is a system-design session with two senior engineers.

## Promises and follow-ups

Thank-you sent to the recruiter the same day.

## Lessons (your words)

"I need a real conflict story before round 2."
```

`.../2026-09-28-mock-system-design.md`:

```markdown
---
contract: 1
kind: mock
company: "Harbour Payments"
role: "Senior Backend Engineer"
round: 2
round_type: system-design
date: 2026-09-28
---

# Mock — Harbour Payments · Senior Backend Engineer · system-design

## Scores

| # | Question | Theme | Self | Coach | Evidence |
|---|---|---|---|---|---|
| 1 | Design a payout reconciliation service | system-design | 3 | 2 | "we'd just use Kafka" — no trade-off named |
| 2 | How would you handle late webhooks? | system-design | 4 | 4 | named idempotency keys and a replay window |

## Strengths

Idempotency.

## Drills

State two options and a trade-off before choosing.

## Re-run list

Question 1.
```

- [ ] **Step 2: Write the asset templates** (bodies only; the script writes the frontmatter and title)

`assets/interview-prep-template.md`:

```markdown
## Round

_Round type, format (call, video, panel, onsite), who interviews, what the coordinator said it covers, and what it really tests (interview-prep.md stage map)._

## Company brief

_The dossier (dossiers/<company>.md), its research date, and the three lines that matter for this round._

## Likely questions

| # | Question | Theme | Source |
|---|---|---|---|

## Story map

| Theme | Story (answers.md) | Strength |
|---|---|---|

## Story gaps

_Themes the likely questions need that no true story covers yet, each with its next step._

## The six answers

_Pointers into answers.md (tell me about yourself, why this company, strength and weakness, pressure, salary number, notice) and any change for this round._

## Questions to ask them

## Lessons to apply

_From interviews/question-bank.md and, when this workspace sits in a career vault, the wiki playbooks for this round type._
```

`assets/interview-mock-template.md`:

```markdown
## Setup

_Mode, length, language, and whether AI tools are allowed in the real round._

## Scores

_Scale 1–5, anchored at 1, 3 and 5 (interview-coach.md rubric). Self is the user's own score, given first._

| # | Question | Theme | Self | Coach | Evidence |
|---|---|---|---|---|---|

## Strengths

## Drills

_One concrete drill per weak area._

## Re-run list
```

`assets/interview-debrief-template.md`:

```markdown
## Questions asked

_Theme: intro, motivation, strengths-weaknesses, leadership, conflict, failure, pressure, initiative, technical, coding, system-design, case, logistics, salary, curveball, other. Story used: the answers.md story title, or blank. Landed: yes, partly, no._

| # | Question | Theme | Story used | Landed |
|---|---|---|---|---|

## What landed

## What didn't

## Signals and next round

## Promises and follow-ups

## Lessons (your words)

_The user's own words, quoted — never rewritten._
```

- [ ] **Step 3: Write the failing tests** — `tests/test_interview.py`

```python
"""Tests for interview.py — the interviews/ file contract, outcome updates and the question bank.

Dates are pinned: the r-workspace fixture is written against --today 2026-10-01.
"""
import os
import pathlib
import shutil
import subprocess
import sys

import pytest

ROOT = pathlib.Path(__file__).resolve().parents[1]
SCRIPTS = ROOT / "skills" / "job-hunting" / "scripts"
FIXTURES = pathlib.Path(__file__).resolve().parent / "fixtures"
sys.path.insert(0, str(SCRIPTS))

import interview  # noqa: E402
from _common import read_table, write_table  # noqa: E402

TODAY = "2026-10-01"
COMPANY, ROLE = "Harbour Payments", "Senior Backend Engineer"
FOLDER = pathlib.Path("interviews") / "harbour-payments-senior-backend-engineer"


@pytest.fixture
def ws(tmp_path, monkeypatch):
    """A copy of the fictional r-workspace with JOB_HUNT_DIR pointing at it."""
    shutil.copytree(FIXTURES / "scenarios" / "r-workspace", tmp_path, dirs_exist_ok=True)
    monkeypatch.setenv("JOB_HUNT_DIR", str(tmp_path))
    return tmp_path


def run(capsys, *argv):
    """Run the CLI in-process, returning (exit code, stdout)."""
    code = interview.main(list(argv))
    return code, capsys.readouterr().out


def meta(path):
    return interview.parse_frontmatter(path.read_text(encoding="utf-8"))


@pytest.mark.parametrize("kind", interview.KINDS)
def test_new_writes_contract_file(ws, capsys, kind):
    code, out = run(capsys, "new", "--kind", kind, "--company", "harbour  payments", "--role", ROLE,
                    "--round-type", "final", "--round", "3", "--date", "2026-10-09")
    path = ws / FOLDER / f"2026-10-09-{kind}-final.md"
    assert code == 0 and f"created: {path}" in out
    fields = meta(path)
    assert fields["contract"] == "1" and fields["kind"] == kind
    assert (fields["company"], fields["role"]) == (COMPANY, ROLE)
    assert (fields["round"], fields["round_type"], fields["date"]) == ("3", "final", "2026-10-09")
    assert fields.get("outcome") == ("pending" if kind == "debrief" else None)
    assert "[[" not in path.read_text(encoding="utf-8")


def test_new_never_overwrites(ws, capsys):
    argv = ("new", "--kind", "prep", "--company", COMPANY, "--role", ROLE,
            "--round-type", "system-design", "--date", "2026-10-03")
    run(capsys, *argv)
    first = ws / FOLDER / "2026-10-03-prep-system-design.md"
    first.write_text(first.read_text(encoding="utf-8") + "mine\n", encoding="utf-8")
    code, out = run(capsys, *argv)
    assert code == 0 and "2026-10-03-prep-system-design-2.md" in out
    assert first.read_text(encoding="utf-8").endswith("mine\n")


@pytest.mark.parametrize("extra, message", [
    (("--kind", "prep", "--round-type", "onsite"), "Unknown round type 'onsite'"),
    (("--kind", "mock", "--round-type", "assessment"), "not a mock mode"),
    (("--kind", "prep", "--round-type", "final", "--date", "03/10/2026"), "Bad date '03/10/2026'"),
    (("--kind", "prep", "--round-type", "final", "--role", "Data Engineer"), "No pipeline row for 'Harbour Payments' / 'Data Engineer'"),
])
def test_new_rejects_bad_input(ws, capsys, extra, message):
    code, out = run(capsys, "new", "--company", COMPANY, "--role", ROLE, *extra)
    assert code == 2 and message in out
    assert sorted(p.name for p in (ws / FOLDER).iterdir()) == [
        "2026-09-12-debrief-hr-screen.md", "2026-09-28-mock-system-design.md"]


def test_frontmatter_round_trips_awkward_names(ws, capsys):
    company = 'Kedai "Ah Seng": Café # 1'
    pipeline = ws / "pipeline.md"
    columns, rows = read_table(pipeline.read_text(encoding="utf-8"))
    rows.append(dict(rows[0], Company=company, Role="Backend: Go"))
    pipeline.write_text(write_table(pipeline.read_text(encoding="utf-8"), columns, rows), encoding="utf-8")
    code, out = run(capsys, "new", "--kind", "debrief", "--company", company, "--role", "Backend: Go",
                    "--round-type", "technical", "--date", "2026-10-02")
    path = pathlib.Path(out.split("created: ", 1)[1].strip())
    assert code == 0 and path.parent.name == "kedai-ah-seng-caf-1-backend-go"
    assert (meta(path)["company"], meta(path)["role"]) == (company, "Backend: Go")


def test_outcome_updates_only_the_newest_debrief(ws, capsys):
    run(capsys, "new", "--kind", "debrief", "--company", COMPANY, "--role", ROLE,
        "--round-type", "system-design", "--date", "2026-10-03")
    code, out = run(capsys, "outcome", "--company", COMPANY, "--role", ROLE, "--outcome", "rejected")
    assert code == 0 and "outcome: rejected" in out
    assert meta(ws / FOLDER / "2026-10-03-debrief-system-design.md")["outcome"] == "rejected"
    assert meta(ws / FOLDER / "2026-09-12-debrief-hr-screen.md")["outcome"] == "advanced"


@pytest.mark.parametrize("argv", [("bank",), ("outcome", "--company", COMPANY, "--role", ROLE, "--outcome", "offer")])
def test_no_workspace_is_not_an_error(tmp_path, monkeypatch, capsys, argv):
    monkeypatch.setenv("JOB_HUNT_DIR", str(tmp_path))
    code, out = run(capsys, *argv)
    assert code == 0 and "No workspace found — run: python3" in out
```

- [ ] **Step 4: Run them to see them fail**

Run: `python3 -m pytest tests/test_interview.py -q`
Expected: collection error `ModuleNotFoundError: No module named 'interview'`.

- [ ] **Step 5: Implement** — `skills/job-hunting/scripts/interview.py`

```python
#!/usr/bin/env python3
"""Interview files in the workspace: create them, record outcomes, build the question bank.

  python3 interview.py new --kind prep --company "Harbour Payments" \
      --role "Senior Backend Engineer" --round-type system-design --round 2 --date 2026-10-03
  python3 interview.py outcome --company "Harbour Payments" --role "Senior Backend Engineer" --outcome advanced
  python3 interview.py bank [--today 2026-10-01]

Files are interviews/<slug>/<date>-<kind>-<round_type>.md, one folder per
pipeline row, frontmatter `contract: 1` (references/interview-debrief.md).
`new` never overwrites; `bank` rewrites interviews/question-bank.md from the
debriefs and mock scorecards. Exit codes follow tracker.py: 0 on success and
on "no workspace found", 2 for bad input.
"""
from __future__ import annotations

import argparse
import datetime
import json
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from _common import read_table, slugify, today, use_utf8_output, workspace_dir, write_table  # noqa: E402

SCRIPT_DIR = Path(__file__).resolve().parent
ASSETS = SCRIPT_DIR.parent / "assets"
KINDS = ("prep", "mock", "debrief")
ROUND_TYPES = ("hr-screen", "behavioral", "technical", "coding", "system-design", "case", "assessment", "final")
OUTCOMES = ("pending", "advanced", "rejected", "offer", "withdrawn")
QUESTION_COLUMNS = ["#", "Question", "Theme", "Story used", "Landed"]
SCORE_COLUMNS = ["#", "Question", "Theme", "Self", "Coach", "Evidence"]
_DATE_RE = re.compile(r"^\d{4}-\d{2}-\d{2}$")
_FRONTMATTER_RE = re.compile(r"\A---\n(.*?)\n---\n", re.S)


def parse_frontmatter(text: str) -> dict:
    """`key: value` pairs from the leading `---` block; double-quoted values are JSON strings."""
    match = _FRONTMATTER_RE.match(text.replace("\r\n", "\n"))
    fields = {}
    for line in match.group(1).splitlines() if match else []:
        key, sep, value = line.partition(":")
        if not sep:
            continue
        value = value.strip()
        if value.startswith('"'):
            try:
                value = json.loads(value)
            except ValueError:
                pass
        fields[key.strip()] = value
    return fields


def _bad_date(value: str | None) -> bool:
    if value is None:
        return False
    try:
        return not _DATE_RE.match(value) or not datetime.date.fromisoformat(value)
    except ValueError:
        return True


def _same(a: str | None, b: str | None) -> bool:
    return " ".join((a or "").lower().split()) == " ".join((b or "").lower().split())


def find_row(ws: Path, company: str, role: str) -> dict | None:
    """The pipeline row for this company and role, ignoring case and spacing."""
    _, rows = read_table((ws / "pipeline.md").read_text(encoding="utf-8"))
    return next((r for r in rows if _same(r.get("Company"), company) and _same(r.get("Role"), role)), None)


def row_folder(ws: Path, row: dict) -> Path:
    return ws / "interviews" / (slugify(f"{row['Company']} {row['Role']}") or "interview")


def free_path(folder: Path, stem: str) -> Path:
    """`<stem>.md`, else `<stem>-2.md`, `-3`… — never an existing file."""
    path, n = folder / f"{stem}.md", 1
    while path.exists():
        n += 1
        path = folder / f"{stem}-{n}.md"
    return path


def render(kind: str, row: dict, round_type: str, round_no: int | None, date: str) -> str:
    fields = {"contract": "1", "kind": kind, "company": json.dumps(row["Company"], ensure_ascii=False),
              "role": json.dumps(row["Role"], ensure_ascii=False), "round": round_no or "",
              "round_type": round_type, "date": date}
    if kind == "debrief":
        fields["outcome"] = "pending"
    head = "\n".join(["---", *(f"{k}: {v}".rstrip() for k, v in fields.items()), "---"])
    title = f"# {kind.capitalize()} — {row['Company']} · {row['Role']} · {round_type}"
    body = (ASSETS / f"interview-{kind}-template.md").read_text(encoding="utf-8")
    return f"{head}\n\n{title}\n\n{body}"


def _write(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, "w", encoding="utf-8", newline="\n") as fh:
        fh.write(text)


def _no_row(args) -> int:
    print(f"No pipeline row for {args.company!r} / {args.role!r} — add it first: "
          f"python3 {SCRIPT_DIR / 'tracker.py'} add --company \"{args.company}\" --role \"{args.role}\"")
    return 2


def records(ws: Path, kind: str) -> list[tuple[dict, str, Path]]:
    """Every interview file of one kind, oldest first by frontmatter date then name."""
    found = []
    for path in (ws / "interviews").glob("*/*.md"):
        text = path.read_text(encoding="utf-8", errors="replace").replace("\r\n", "\n")
        fields = parse_frontmatter(text)
        if fields.get("kind") == kind:
            found.append((fields, text, path))
    return sorted(found, key=lambda r: (r[0].get("date", ""), r[2].name))


def cmd_new(ws: Path, args) -> int:
    if args.round_type not in ROUND_TYPES:
        print(f"Unknown round type {args.round_type!r} — use one of: {', '.join(ROUND_TYPES)}")
        return 2
    if args.kind == "mock" and args.round_type == "assessment":
        print("'assessment' is not a mock mode — mock the case or behavioral part instead")
        return 2
    row = find_row(ws, args.company, args.role)
    if row is None:
        return _no_row(args)
    date = args.date or args.today_ or today()
    path = free_path(row_folder(ws, row), f"{date}-{args.kind}-{args.round_type}")
    _write(path, render(args.kind, row, args.round_type, args.round, date))
    print(f"created: {path}")
    return 0


def cmd_outcome(ws: Path, args) -> int:
    row = find_row(ws, args.company, args.role)
    if row is None:
        return _no_row(args)
    folder = row_folder(ws, row)
    debriefs = [r for r in records(ws, "debrief") if r[2].parent == folder]
    if not debriefs:
        print(f"No debrief yet for {row['Company']} / {row['Role']} — create one with: "
              f"python3 {SCRIPT_DIR / 'interview.py'} new --kind debrief …")
        return 2
    _, text, path = debriefs[-1]
    match = _FRONTMATTER_RE.match(text)
    block = match.group(1)
    if re.search(r"(?m)^outcome:", block):
        block = re.sub(r"(?m)^outcome:.*$", f"outcome: {args.outcome}", block, count=1)
    else:
        block += f"\noutcome: {args.outcome}"
    _write(path, f"---\n{block}\n---\n{text[match.end():]}")
    print(f"outcome: {args.outcome} — {path}")
    return 0
```

Leave `cmd_bank` and `build_bank` to Task 2; register them there. Finish the module with:

```python
def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    sub = parser.add_subparsers(dest="cmd")

    def add(name, help_):
        p = sub.add_parser(name, help=help_)
        p.add_argument("--today", dest="today_", metavar="YYYY-MM-DD")
        return p

    new = add("new", "create a prep, mock or debrief file for a pipeline row")
    new.add_argument("--kind", required=True, choices=KINDS)
    new.add_argument("--company", required=True)
    new.add_argument("--role", required=True)
    new.add_argument("--round-type", dest="round_type", required=True)
    new.add_argument("--round", type=int)
    new.add_argument("--date", metavar="YYYY-MM-DD")
    outcome = add("outcome", "set the newest debrief's outcome for a pipeline row")
    outcome.add_argument("--company", required=True)
    outcome.add_argument("--role", required=True)
    outcome.add_argument("--outcome", required=True, choices=OUTCOMES)
    add("bank", "rebuild interviews/question-bank.md")
    return parser


COMMANDS = {"new": cmd_new, "outcome": cmd_outcome}


def main(argv=None) -> int:
    use_utf8_output()
    parser = build_parser()
    args = parser.parse_args(argv)
    if not args.cmd:
        parser.print_help()
        return 2
    ws = workspace_dir()
    if not (ws / "pipeline.md").exists():
        print(f"No workspace found — run: python3 {SCRIPT_DIR / 'workspace.py'} init")
        return 0
    for value in (getattr(args, "date", None), args.today_):
        if _bad_date(value):
            print(f"Bad date {value!r} — use YYYY-MM-DD")
            return 2
    return COMMANDS[args.cmd](ws, args)


if __name__ == "__main__":
    sys.exit(main())
```

- [ ] **Step 6: Run the tests**

Run: `python3 -m pytest tests/test_interview.py -q`
Expected: 6 test functions, 10 cases, all pass (the `bank` case of `test_no_workspace_is_not_an_error` returns before dispatch).

**Done when:** the four `new`/`outcome` tests pass; no file under `interviews/` lacks `contract: 1`; `grep -rn '\[\[' skills/job-hunting/assets/interview-*` finds nothing.

### Task 2: `interview.py bank`

**Files:**
- Modify: `skills/job-hunting/scripts/interview.py` (add `build_bank`, `cmd_bank`; register `"bank"` in `COMMANDS`)
- Test: `tests/test_interview.py` (append)

**Interfaces:**
- Consumes: `records(ws, kind)`, `QUESTION_COLUMNS`, `SCORE_COLUMNS` from Task 1.
- Produces: `interview.build_bank(debriefs, mocks, date: str) -> str`; file `interviews/question-bank.md` with sections `## Asked in real interviews` (columns `Question | Theme | Times | Companies | Last asked | Landed (yes/partly/no)`), `## Questions with no story` (`Question | Theme | Company | Date`), `## Re-practice queue` (`Question | Theme | Last score | Last practised`). CLI prints `Wrote <path> — N debriefs, M mocks.`

- [ ] **Step 1: Append the failing tests**

```python
def fill(path, heading, columns, rows):
    path.write_text(write_table(path.read_text(encoding="utf-8"), columns, rows, heading=heading), encoding="utf-8")


def new_file(capsys, kind, company, role, round_type, date):
    _, out = run(capsys, "new", "--kind", kind, "--company", company, "--role", role,
                 "--round-type", round_type, "--date", date)
    return pathlib.Path(out.split("created: ", 1)[1].strip())


def bank_table(ws, heading):
    return read_table((ws / "interviews" / "question-bank.md").read_text(encoding="utf-8"), heading)[1]


def test_bank_aggregates_debriefs(ws, capsys):
    path = new_file(capsys, "debrief", "Lumen Logistics", "Backend Engineer (Python)", "hr-screen", "2026-09-30")
    fill(path, "## Questions asked", interview.QUESTION_COLUMNS, [
        {"#": "1", "Question": "Tell me about yourself.", "Theme": "intro", "Story used": "", "Landed": "yes"},
        {"#": "2", "Question": "Tell me about a time you failed", "Theme": "failure", "Story used": "", "Landed": "no"}])
    code, out = run(capsys, "bank", "--today", TODAY)
    assert code == 0 and "2 debriefs, 1 mocks" in out
    asked = {r["Question"]: r for r in bank_table(ws, "## Asked in real interviews")}
    assert asked["Tell me about yourself."] == {
        "Question": "Tell me about yourself.", "Theme": "intro", "Times": "2",
        "Companies": "Harbour Payments, Lumen Logistics", "Last asked": "2026-09-30",
        "Landed (yes/partly/no)": "2/0/0"}
    assert asked["When could you start?"]["Landed (yes/partly/no)"] == "0/0/0"
    no_story = [(r["Question"], r["Company"]) for r in bank_table(ws, "## Questions with no story")]
    assert no_story == [("Tell me about a time you disagreed with your lead", "Harbour Payments"),
                        ("Tell me about a time you failed", "Lumen Logistics")]


def test_bank_requeues_until_a_later_mock_scores_well(ws, capsys):
    run(capsys, "bank", "--today", TODAY)
    assert [r["Question"] for r in bank_table(ws, "## Re-practice queue")] == ["Design a payout reconciliation service"]
    path = new_file(capsys, "mock", COMPANY, ROLE, "system-design", "2026-10-01")
    fill(path, "## Scores", interview.SCORE_COLUMNS, [
        {"#": "1", "Question": "Design a payout reconciliation service.", "Theme": "system-design",
         "Self": "4", "Coach": "4", "Evidence": "two options, then a trade-off"}])
    run(capsys, "bank", "--today", TODAY)
    assert bank_table(ws, "## Re-practice queue") == []


def test_bank_on_a_workspace_without_interviews(tmp_path, monkeypatch, capsys):
    shutil.copyfile(FIXTURES / "scenarios" / "r-workspace" / "pipeline.md", tmp_path / "pipeline.md")
    monkeypatch.setenv("JOB_HUNT_DIR", str(tmp_path))
    code, _ = run(capsys, "bank", "--today", TODAY)
    text = (tmp_path / "interviews" / "question-bank.md").read_text(encoding="utf-8")
    assert code == 0 and "from 0 debriefs and 0 mocks" in text


def test_cli_runs_as_a_subprocess(ws):
    # a piped stdout on Windows is cp1252, which has no "—"
    r = subprocess.run([sys.executable, str(SCRIPTS / "interview.py"), "bank", "--today", TODAY],
                       capture_output=True, text=True, encoding="utf-8",
                       env={**os.environ, "JOB_HUNT_DIR": str(ws), "PYTHONIOENCODING": "cp1252"})
    assert r.returncode == 0, r.stderr
    assert "—" in r.stdout
```

- [ ] **Step 2: Run them to see them fail**

Run: `python3 -m pytest tests/test_interview.py -q -k bank`
Expected: FAIL — `KeyError: 'bank'` from `COMMANDS`.

- [ ] **Step 3: Implement** — add to `interview.py` above `build_parser`:

```python
def _norm(question: str) -> str:
    return " ".join(re.sub(r"[^a-z0-9]+", " ", question.lower()).split())


def build_bank(debriefs: list, mocks: list, date: str) -> str:
    """The question bank: real questions by theme, questions with no story, the re-practice queue."""
    asked, no_story = {}, []
    for fields, text, _ in debriefs:
        for row in read_table(text, "## Questions asked")[1]:
            question = (row.get("Question") or "").strip()
            if not question:
                continue
            landed = (row.get("Landed") or "").strip().lower()
            theme = (row.get("Theme") or "").strip()
            entry = asked.setdefault(_norm(question), {"times": 0, "companies": set(),
                                                       "landed": dict.fromkeys(("yes", "partly", "no"), 0)})
            entry.update(question=question, theme=theme, last=fields.get("date", ""))
            entry["times"] += 1
            entry["companies"].add(fields.get("company", ""))
            if landed in entry["landed"]:
                entry["landed"][landed] += 1
            if landed == "no" and (row.get("Story used") or "").strip().lower() in ("", "-", "—", "none", "n/a"):
                no_story.append({"Question": question, "Theme": theme,
                                 "Company": fields.get("company", ""), "Date": fields.get("date", "")})
    latest = {}
    for fields, text, _ in mocks:
        for row in read_table(text, "## Scores")[1]:
            question = (row.get("Question") or "").strip()
            if question:
                latest[_norm(question)] = {"Question": question, "Theme": (row.get("Theme") or "").strip(),
                                           "Last score": (row.get("Coach") or "").strip(),
                                           "Last practised": fields.get("date", "")}
    asked_rows = [{"Question": e["question"], "Theme": e["theme"], "Times": str(e["times"]),
                   "Companies": ", ".join(sorted(c for c in e["companies"] if c)), "Last asked": e["last"],
                   "Landed (yes/partly/no)": "/".join(str(n) for n in e["landed"].values())}
                  for e in sorted(asked.values(), key=lambda e: (e["theme"], -e["times"], e["question"].lower()))]
    queue = [r for r in latest.values() if r["Last score"].isdigit() and int(r["Last score"]) <= 2]
    md = (f"# Question bank\n\n_Generated by `interview.py bank` on {date} from {len(debriefs)} debriefs "
          f"and {len(mocks)} mocks. Edit those files, not this one — the next run overwrites it._\n")
    md = write_table(md, ["Question", "Theme", "Times", "Companies", "Last asked", "Landed (yes/partly/no)"],
                     asked_rows, heading="Asked in real interviews")
    md = write_table(md, ["Question", "Theme", "Company", "Date"], no_story, heading="Questions with no story")
    return write_table(md, ["Question", "Theme", "Last score", "Last practised"], queue, heading="Re-practice queue")


def cmd_bank(ws: Path, args) -> int:
    debriefs, mocks = records(ws, "debrief"), records(ws, "mock")
    path = ws / "interviews" / "question-bank.md"
    _write(path, build_bank(debriefs, mocks, args.today_ or today()))
    print(f"Wrote {path} — {len(debriefs)} debriefs, {len(mocks)} mocks.")
    return 0
```

and change `COMMANDS = {"new": cmd_new, "outcome": cmd_outcome, "bank": cmd_bank}`.

- [ ] **Step 4: Run the whole file**

Run: `python3 -m pytest tests/test_interview.py -q`
Expected: all pass (13 test cases with parametrization).

**Done when:** `tests/test_interview.py` passes; running `bank` twice gives byte-identical files.

### Task 3: `workspace.py` — `interviews/` and the stray-workspace guard (J1)

**Files:**
- Modify: `skills/job-hunting/scripts/workspace.py:13` (DIRS), `:28-39` (main)
- Test: `tests/test_workspace.py`

**Interfaces:**
- Produces: `workspace.stray_workspace(ws: Path, cwd: Path) -> Path | None`. `where` prints the path on stdout, and on a stray, `warning: …` on stderr, exit 0. `init` with a stray, a missing workspace and no `JOB_HUNT_DIR` prints the warning, creates nothing and returns 2 (an explicit `JOB_HUNT_DIR` is trusted — that is the migration path).

- [ ] **Step 1: Update and add tests** — in `tests/test_workspace.py` change the directory list in `test_init_creates_files` to `["postings", "resumes", "letters", "dossiers", "reviews", "interviews"]`, then append:

```python
def _isolated_env(tmp_path):
    env = {k: v for k, v in os.environ.items() if k != "JOB_HUNT_DIR"}
    return {**env, "HOME": str(tmp_path / "home"), "USERPROFILE": str(tmp_path / "home")}

def test_where_warns_when_started_below_a_vault(tmp_path):
    (tmp_path / "vault" / "job-hunt").mkdir(parents=True)
    (tmp_path / "vault" / "wiki").mkdir()
    r = subprocess.run([sys.executable, str(SCRIPTS / "workspace.py"), "where"], cwd=tmp_path / "vault" / "wiki",
                       env=_isolated_env(tmp_path), capture_output=True, text=True, encoding="utf-8")
    assert r.returncode == 0 and r.stdout.strip() == str(tmp_path / "home" / "job-hunt")
    assert "warning:" in r.stderr and "vault" in r.stderr

def test_init_refuses_to_create_a_stray_workspace(tmp_path):
    (tmp_path / "vault" / "job-hunt").mkdir(parents=True)
    (tmp_path / "vault" / "wiki").mkdir()
    r = subprocess.run([sys.executable, str(SCRIPTS / "workspace.py"), "init"], cwd=tmp_path / "vault" / "wiki",
                       env=_isolated_env(tmp_path), capture_output=True, text=True, encoding="utf-8")
    assert r.returncode == 2 and "warning:" in r.stderr
    assert not (tmp_path / "home" / "job-hunt").exists()
```

- [ ] **Step 2: Run to see them fail**

Run: `python3 -m pytest tests/test_workspace.py -q`
Expected: 3 failures (no `interviews/`; no warning; init creates the stray).

- [ ] **Step 3: Implement** — `import os` beside `shutil, sys`; `DIRS = ["postings", "resumes", "letters", "dossiers", "reviews", "interviews"]`, then:

```python
def stray_workspace(ws: Path, cwd: Path) -> Path | None:
    """The nearest `job-hunt/` at or above `cwd` when it is not `ws` — a session started in a vault subfolder."""
    for folder in (cwd, *cwd.parents):
        candidate = folder / "job-hunt"
        if candidate.is_dir():
            return None if candidate.resolve() == ws.resolve() else candidate
    return None

def main(argv):
    use_utf8_output()
    cmd = argv[0] if argv else "where"
    ws = workspace_dir()
    stray = stray_workspace(ws, Path.cwd())
    if stray:
        print(f"warning: {stray} is above the current folder but the workspace in use is {ws} — "
              f"set JOB_HUNT_DIR to {stray} or start from {stray.parent}", file=sys.stderr)
    if cmd == "init":
        if stray and not ws.exists() and not os.environ.get("JOB_HUNT_DIR"):
            return 2
        created = init(ws)
        print(f"Workspace: {ws}\nCreated: {', '.join(created) or 'nothing (already initialized)'}")
    elif cmd == "where":
        print(ws)
    else:
        print(__doc__); return 2
    return 0
```

- [ ] **Step 4: Run** `python3 -m pytest tests/test_workspace.py -q` → 4 passed.

**Done when:** tests pass; `init` on a fresh `JOB_HUNT_DIR` still creates `interviews/` and never overwrites (existing idempotency test).

---

## Phase 2 — References (markdown content)

Each task lists the exact content requirements. Keep the house style: second person to the
agent, short sections, tables where structure helps, every cross-reference by file name.
Verification for every Phase 2 task: `python3 build.py --check` prints `OK`, the listed greps
match, and no line in the edited files contains `[[`.

### Task 4: `interview-prep.md`, `company-dossier.md`

**Files:** Modify `skills/job-hunting/references/interview-prep.md`, `skills/job-hunting/references/company-dossier.md`, `docs/followups-v6.0.1.md`.

Content requirements, `interview-prep.md`:
1. Step 0 echoes the pipeline row (stage, Next action, Due) instead of asking, then — workspace mode — creates the pack with `python3 ${CLAUDE_SKILL_DIR}/scripts/interview.py new --kind prep --company "<X>" --role "<Y>" --round-type <type> [--round N] --date <interview date>` and fills its sections in place. Round types listed verbatim.
2. Dossier freshness: the dossier's `_Researched: YYYY-MM-DD_` line; older than 30 days → refresh its news section via `/job-hunter:company` before prep; no dossier → offer one.
3. New section **Story map and gaps**: map each likely question's theme to an `answers.md` STAR story (theme tags `(themes: …)`); strength strong / usable / weak; the five STAR themes (leadership, conflict, failure, pressure, initiative) are always checked; a gap gets one next step — draw the story out of profile §5 by asking (facts-policy §2) or, with no real event, `soft-skills-coach.md`. Never script a story.
4. New section **Lessons to apply**: read `interviews/question-bank.md` (repeat questions, "Questions with no story", re-practice queue); if the workspace's parent folder holds `wiki/_index.md` (a career vault), read `wiki/hot.md` and the index rows whose Topics include `interview` or this round type, cite them by article name, read-only; none → write "no lessons file".
5. "After each interview": step 2 becomes "Debrief within 24 hours — `interview-debrief.md`"; step 1 thank-you points to the Networker's "Interviewer thank-you" template in `networking.md`; steps 4–5 add `interview.py outcome --outcome advanced|rejected` beside the stage change.
6. Delete the sentence that states Malaysian law in the Curveballs paragraph (currently "no law bars them in Malaysian private-sector hiring", around line 79); keep the pointer to `markets/<cc>.md` §10, which already carries the law (`markets/my.md` §10).
7. Close: `tracker.py set --company "<X>" --role "<Y>" --next "<round_type> prep done — mock?" --due <date>`, then the storage-mode closing step. Chat mode: deliver the pack in chat; nothing stored but the closing step.

`company-dossier.md`: the saved dossier carries `_Researched: YYYY-MM-DD_` under its title; §4 adds "Older than 30 days before an interview → refresh Health & news first."

`docs/followups-v6.0.1.md`: tick the interview-prep.md:79 item (`- [x]`).

Verify: `grep -n "interview.py new --kind prep" references/interview-prep.md`; `grep -n "_Researched:" references/company-dossier.md`; `grep -n "no law bars" references/interview-prep.md` returns nothing.

**Done when:** all seven requirements are present and the greps pass.

### Task 5: `interview-coach.md` — modes and the anchored rubric

**Files:** Modify `skills/job-hunting/references/interview-coach.md`.

Content requirements:
1. Setup adds the mode (`hr-screen`, `behavioral`, `technical`, `coding`, `system-design`, `case`, `final`) and, for `coding`/`technical`, "Are AI tools allowed in the real round?" — policies differ by company and round.
2. Loop: one question at a time; after each answer the user scores themself 1–5 **first**; then the coach scores against the rubric, quoting the user's own phrase as evidence, and gives one fix. Re-ask the question after a fix when the user wants.
3. **Rubric** section: scale 1–5 anchored at 1, 3 and 5; summary labels 1–2 poor, 3 borderline, 4 solid, 5 outstanding. Dimension table per mode exactly as spec §4.3. Behavioural anchors: 1 = no real example, or a hypothetical; 3 = a real example, own part or result vague; 5 = specific and recent, own actions clear, quantified result, survives the follow-up probe. STAR checks: roughly 20/10/60/10 Situation/Task/Action/Result, "I" not "we", the number in the result; spoken length 60–90 s is a heuristic, not a rule.
4. Mode notes, one short paragraph each: coding is a talk-through (clarify → approach → complexity → tests; no code runner); system-design (requirements → high-level → deep dive → trade-offs → scale and reliability); case/product (structure → hypotheses → data → recommendation → risks); hr-screen (salary from `answers.md` › Expected salary and `markets/<cc>.md` §5, notice exact, why leaving the same true sentence every time, work pass, curveballs per `markets/<cc>.md` §10); final (motivation, "why us" from the dossier, offer-readiness).
5. Debrief: workspace mode creates the scorecard with `interview.py new --kind mock --company … --role … --round-type <mode>`, fills `## Scores` (`# | Question | Theme | Self | Coach | Evidence`), Strengths, Drills, Re-run list, then runs `interview.py bank`. STAR edits go to `answers.md` only after the user confirms; weak areas to profile §10. Chat mode: scorecard in chat only.
6. Honesty: flag any embellishment the user adds at once (facts-policy §5). Scores are coaching signals, not a forecast of an offer — never claim otherwise.

Verify: `grep -n "Self" references/interview-coach.md`, `grep -n "anchored" references/interview-coach.md`, `grep -n "interview.py new --kind mock" references/interview-coach.md`.

**Done when:** all six requirements are present.

### Task 6: `interview-debrief.md` (new), `networking.md`, `pipeline.md`

**Files:** Create `skills/job-hunting/references/interview-debrief.md`; modify `references/networking.md` (§5 templates), `references/pipeline.md` (Logging section).

Content requirements, `interview-debrief.md` (target 80–110 lines):
1. When: within 24 hours of any round; triggers ("debrief", "just finished the … interview", "how did my screen go").
2. Workspace flow: echo the pipeline row; `python3 ${CLAUDE_SKILL_DIR}/scripts/interview.py new --kind debrief --company "<X>" --role "<Y>" --round-type <type> [--round N] --date <interview date>`; fill **Questions asked** (`# | Question | Theme | Story used | Landed`, themes and landed values verbatim from Global Constraints, Story used = the `answers.md` title or blank), What landed, What didn't, Signals and next round, Promises and follow-ups, **Lessons (your words)** — the user's words quoted, never rewritten.
3. Handoffs table — rows exactly as spec §5 (Operations via `tracker.py set`, `/job-hunter:company`, salary via `answers.md` then `offer-coach.md`, Networker thank-you, STAR edits on confirm, new achievement → profile §5 first per facts-policy §1, Soft Skills Coach, third same-stage rejection → `pipeline.md` §5, career vault reads in place).
4. Outcome: when the result is known — now or later — run `interview.py outcome --company … --role … --outcome advanced|rejected|offer|withdrawn` together with the matching `tracker.py set --stage …`. The career vault's harvest waits for this.
5. Question bank: run `python3 ${CLAUDE_SKILL_DIR}/scripts/interview.py bank`; read "Questions with no story" back to the user as story gaps.
6. Thank-you: same day, the Networker's "Interviewer thank-you" template, ≤ 4 lines, slop scan; follow-up Due via `tracker.py set --due`.
7. Third parties: interviewer names only as the user gives them, optional, never guessed; no personal details about them.
8. Chat mode: append a row to profile §9 `### Interviews` (`Date | Company | Role | Round | Outcome | Asked (themes) | Landed / missed | Next`); keep the newest 12 rows, fold older ones into one "Interview patterns" line in §10; compute a bank from that table only when asked; never claim a script ran.
9. **File contract** section: layout (`interviews/<slug>/<date>-<kind>-<round_type>.md`, `question-bank.md` generated), frontmatter fields with `contract: 1`, vocabularies, "no wikilinks", and "a breaking change bumps `contract`" — the career vault depends on it.
10. Closing step for the storage mode.

`networking.md` §5: add **Interviewer thank-you** — same day, 2–4 lines: thanks, one specific point from the conversation, reaffirmed interest; via the recruiter if there is no direct address; no new claims (facts-policy §4); `ats_check.py --slop`.

`pipeline.md` Logging: one line — "After every interview round, debrief within 24 hours (`interview-debrief.md`); when the stage changes after a debrief, also run `interview.py outcome`."

Verify: `test -f references/interview-debrief.md`; `grep -n "contract: 1" references/interview-debrief.md`; `grep -n "Interviewer thank-you" references/networking.md`; `grep -n "interview-debrief.md" references/pipeline.md`.

**Done when:** all requirements are present and `build.py --check` passes.

### Task 7: Market interview-process norms

**Files:** Modify `skills/job-hunting/references/markets/_template.md`, `markets/my.md`, `markets/sg.md` (§10 only).

Content requirements:
1. `_template.md` §10 heading becomes "Interview process, curveballs & rights" with a new first sub-part "Process" listing: typical rounds and order, timeline, assessments, salary-expectation handling, notice talk, language, AI-tool policy, source.
2. `my.md` and `sg.md` gain a "Process" sub-part with those bullets. Every external claim carries a source URL and a tag — `(verified)` or `(practitioner norm — confirm locally)`. Verified items available: SG TAFEP "Conducting job interviews" (https://www.tal.sg/tafep/employment-practices/recruitment/conducting-job-interviews) — avoid personal questions unless job-related, discuss salary expectations openly; SG Workplace Fairness Act 2025 uncommenced as of 2026-09-29 (https://sso.agc.gov.sg/Act/WFA2025/Uncommenced/20250304073414?DocDate=20250213) — keep "check before calling a question unlawful". Round structure, timelines, salary-range handling, notice talk and language are practitioner norms.
3. Keep consistency with each file's §5 (salary field mechanics) and §7 (notice); do not restate §7's statutory table — point to it.
4. Do not change any other section.

Verify: `grep -n "Interview process" references/markets/*.md` (3 hits); each new bullet in my/sg has `verified` or `practitioner norm`.

**Done when:** all four requirements hold.

### Task 8: Strategist reads career-vault playbooks (J2)

**Files:** Modify `skills/job-hunting/references/strategy.md`.

Content requirements: a short section "Lessons from a career vault (optional)": if the workspace's parent folder holds `wiki/_index.md`, read `wiki/hot.md` and index rows whose Topics include `targeting`, `sourcing`, `materials` or `networking` before revising targets; cite articles by name; propose changes to profile §2/§8 and write only on the user's confirmation; a lesson is never a fact about the user (facts-policy §1); no vault → skip silently; never write to the vault.

Verify: `grep -n "wiki/_index.md" references/strategy.md`.

**Done when:** the section exists and nothing else in the file changes.

---

## Phase 3 — Entry points, assets, docs

### Task 9: Skills and assets

**Files:** Modify `skills/interview/SKILL.md`, `skills/job-hunting/SKILL.md`, `skills/help/SKILL.md`, `skills/job-hunting/assets/profile-template.md`, `skills/job-hunting/assets/answers-template.md`.

Content requirements:
1. `skills/interview/SKILL.md`: description names prep pack, mock with anchored scoring, and debrief; `argument-hint: [company, role, round — or "mock <mode>" or "debrief"]`; steps: resolve storage mode; read profile + pipeline row; default → `interview-prep.md`; "mock" → `interview-coach.md`; "debrief" → `interview-debrief.md`; interview files only via `scripts/interview.py`; facts policy; closing step. Keep `disable-model-invocation: true`. ≤ 20 lines.
2. Router `SKILL.md`: the init sentence lists `interviews/`; after the `where` sentence add "If `where` prints a warning, show it to the user and stop before writing anything."; Coach row: triggers "Interview scheduled or just finished: prep pack, mock, debrief, company dossier, soft-skill gaps", references add `interview-debrief.md`, script `scripts/interview.py new / outcome / bank`; description (≤ 1024 chars) gains "debrief an interview". Version string unchanged.
3. `help/SKILL.md` Coach row: "Coach — prep pack, mock, debrief, company dossier, soft skills" with verbs `/job-hunter:interview [mock|debrief]`, `/job-hunter:company`.
4. `profile-template.md` §9: the note lists `interviews/` for workspace mode; add after `### Answers`:

```markdown
### Interviews
> Chat mode: one row per debriefed round, newest 12 kept (older rows fold into one line in §10). Workspace mode: see `interviews/`.

| Date | Company | Role | Round | Outcome | Asked (themes) | Landed / missed | Next |
|---|---|---|---|---|---|---|---|
```

5. `answers-template.md` STAR stories: lines become `1. **Title:** — one line (themes: …)` and the note says themes come from the debrief vocabulary.

Verify: `python3 build.py --check` → OK; `grep -n "interview-debrief.md" skills/job-hunting/SKILL.md`; `grep -n "### Interviews" skills/job-hunting/assets/profile-template.md`.

**Done when:** requirements hold and `build.py --check` passes.

### Task 10: README and project description

**Files:** Modify `README.md`, `docs/PROJECT-DESCRIPTION.md`.

Content requirements: README roles table Coach row adds "debrief"; layout table adds `scripts/interview.py`, `references/interview-debrief.md`, `assets/interview-*-template.md`; the workspace description lists `interviews/` with one line on the file contract and the career vault that reads it; the scenarios line says A–U. PROJECT-DESCRIPTION Coach line adds "debriefs after each round, kept in my profile's §9 Interviews table". No version change.

Verify: `grep -n "interviews/" README.md`; `grep -n "debrief" docs/PROJECT-DESCRIPTION.md`.

**Done when:** both files updated; nothing outside these lines changes.

---

## Phase 4 — Scenarios and verification

### Task 11: Behavioural scenarios R–U and the rest of r-workspace

**Files:** Create `tests/fixtures/scenarios/r-workspace/profile.md` (copy of `q-workspace/profile.md` with its fixture note updated), `answers.md` (from `assets/answers-template.md`: Expected salary RM 11,000 single / RM 10,000–12,500 range; notice 1 month; three STAR stories from profile §5 — webhook retry queue (themes: pressure, initiative), dashboard latency (themes: initiative), dispatch reporting automation (themes: initiative); no failure or conflict story), `dossiers/harbour-payments.md` (one-page dossier, `_Researched: 2026-06-01_`, fictional), `postings/harbour-payments-senior-backend-engineer.md` (posting frontmatter like `q-workspace/postings/…`, three responsibilities: payouts service, reconciliation, on-call); modify `tests/behavioral-scenarios.md`.

Content requirements: scenarios R (prep pack), S (system-design mock), T (debrief after the Lumen Logistics HR screen, with a salary question and a newly mentioned achievement), U (chat-mode debrief on `fixtures/sample-profile.md`), each with "Workspace: a copy of `scenarios/r-workspace/`; today is 2026-10-01." (U: chat mode) and the `Expected:` bullets from spec §9, in the existing scenario format. Update the preamble's scenario range to A–U.

Verify: `grep -n "^## [R-U] —" tests/behavioral-scenarios.md` → 4 hits; `python3 -m pytest tests/test_interview.py -q` still passes with the added fixture files.

**Done when:** the four scenarios and fixture files exist and are fictional (no real names beyond the existing fixture cast).

### Task 12: Verification against the baseline

**Files:** none modified unless a check fails.

- [ ] Run the test command from Global Constraints → expect 431 + new tests passed, 0 failed (the git test deselected).
- [ ] `python3 build.py --check` → `OK: 12 skills pass checks`.
- [ ] `claude plugin validate .` → `✔ Validation passed`.
- [ ] `python3 build.py` into a scratch copy, then list the zip: it contains `job-hunting/references/interview-debrief.md`, `job-hunting/scripts/interview.py`, `job-hunting/assets/interview-debrief-template.md`; delete the scratch `dist/` afterwards.
- [ ] `grep -rn '\[\[' skills/job-hunting/assets skills/job-hunting/references` → only the pre-existing non-link hit, if any.
- [ ] Router `SKILL.md` line count ≤ 500; description ≤ 1024 chars.
- [ ] Record results against the Phase 0 baseline in the final report.

**Done when:** every check passes or each deviation is explained in the final report.

## Self-review

- Spec coverage: §1 v1 features → Tasks 1–2 (files, bank), 4 (prep, story map, gaps, dossier freshness, lessons), 5 (modes, rubric), 6 (debrief, thank-you, handoffs, chat mode, contract), 7 (markets); §4.1 commands → Task 9; §6 contract → Tasks 1, 2, 6; §7 claude.ai → Tasks 6, 9, 10; §8 files → all; §9 tests → Tasks 1–3, 11; vault J1 → Task 3, J2 → Task 8, J3 → Task 1 (`outcome`), J4 → Tasks 1, 12.
- Placeholders: none; markdown tasks list required content and verifying greps.
- Names: `records`, `parse_frontmatter`, `QUESTION_COLUMNS`, `SCORE_COLUMNS`, `build_bank`, `stray_workspace` are used consistently across Tasks 1–3.
