#!/usr/bin/env python3
"""Interview files in the workspace: create them, record outcomes, build the question bank.

  python3 interview.py new --kind prep --company "Harbour Payments" \
      --role "Senior Backend Engineer" --round-type system-design --round 2 --date 2026-10-03
  python3 interview.py outcome --company "Harbour Payments" --role "Senior Backend Engineer" --outcome advanced
  python3 interview.py bank [--today 2026-10-01]

Files are interviews/<slug>/<date>-<kind>-<round_type>.md, one folder per
pipeline row, frontmatter `contract: 1` (references/interview-debrief.md).
`new` never overwrites; `bank` rewrites interviews/question-bank.md from the
debriefs and mock scorecards. Exit codes follow tracker.py: 0 on success (and
`bank` with no workspace found), 2 for bad input or a `new`/`outcome` write with
no workspace.
"""
from __future__ import annotations

import argparse
import datetime
import json
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from _common import (  # noqa: E402
    read_table, slugify, today, use_utf8_output, workspace_dir, write_table, write_text_atomic)

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
    write_text_atomic(path, text)


def _no_row(args) -> int:
    print(f"No pipeline row for {args.company!r} / {args.role!r} — add it first: "
          f"sh {SCRIPT_DIR / 'jh'} tracker.py add --company \"{args.company}\" --role \"{args.role}\"")
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
              f"sh {SCRIPT_DIR / 'jh'} interview.py new --kind debrief …")
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


COMMANDS = {"new": cmd_new, "outcome": cmd_outcome, "bank": cmd_bank}


def main(argv=None) -> int:
    use_utf8_output()
    parser = build_parser()
    args = parser.parse_args(argv)
    if not args.cmd:
        parser.print_help()
        return 2
    ws = workspace_dir()
    if not (ws / "pipeline.md").exists():
        print(f"No workspace found — run: sh {SCRIPT_DIR / 'jh'} workspace.py init")
        return 2 if args.cmd in ("new", "outcome") else 0
    for value in (getattr(args, "date", None), args.today_):
        if _bad_date(value):
            print(f"Bad date {value!r} — use YYYY-MM-DD")
            return 2
    return COMMANDS[args.cmd](ws, args)


if __name__ == "__main__":
    sys.exit(main())
