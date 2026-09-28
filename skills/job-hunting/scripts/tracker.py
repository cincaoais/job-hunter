#!/usr/bin/env python3
"""Pipeline and contacts CLI over the workspace markdown tables.

Reads and writes the first table in `pipeline.md` (one row per company+role)
and the table in `contacts.md` (the networking CRM), and turns them into the
daily view, the weekly funnel and the weekly review file.

  python3 tracker.py add --company "Apex Digital" --role "Backend Engineer" \
      --source JobStreet --channel cold --stage applied
  python3 tracker.py set --company "Apex Digital" --stage screen --next "Prep the screen" --due 2026-09-23
  python3 tracker.py today [--today 2026-09-16] [--json]
  python3 tracker.py funnel [--json]
  python3 tracker.py digest          # reviews/<today>.md + the last-review line
  python3 tracker.py contacts        # contacts whose Next touch is due
  python3 tracker.py contact --name "Aisyah Rahman" --company Nimbus --next-touch 2026-09-22

Every write sets `Last touch` to today unless `--last-touch` is given, and
`--today YYYY-MM-DD` overrides the clock for every command. Exit codes: 0 on
success — including "no workspace found", because the today/review skills run
this inline and a non-zero exit would abort them — and 2 for bad input.
"""
from __future__ import annotations

import argparse
import datetime
import json
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from _common import read_table, today as today_iso, use_utf8_output, workspace_dir, write_table  # noqa: E402

SCRIPT_DIR = Path(__file__).resolve().parent

# --- vocabulary --------------------------------------------------------------

STAGES = ("saved", "applied", "screen", "interview", "final", "offer",
          "accepted", "rejected", "withdrawn", "cold")
TERMINAL_STAGES = frozenset({"accepted", "rejected", "withdrawn", "cold"})
# Stages a row can go stale in: sent, not yet closed.
OPEN_STAGES = frozenset({"applied", "screen", "interview", "final"})
INTERVIEW_DUE_STAGES = frozenset({"screen", "interview", "final"})
# Funnel buckets. "Sent" is every stage but `saved`; a stage counts for every
# bucket it has already passed through, judged by the row's current stage.
RESPONSE_STAGES = frozenset({"screen", "interview", "final", "offer", "accepted"})
INTERVIEWED_STAGES = frozenset({"interview", "final", "offer", "accepted"})
OFFER_STAGES = frozenset({"offer", "accepted"})
# Stages that mean the application went out and has not been closed — the
# only ones that back-fill an empty `Applied` cell.
SENT_OPEN_STAGES = frozenset({"applied", "screen", "interview", "final", "offer"})
# A `rejected` row only counts as a response when its Notes say a human
# actually answered (see the funnel --help). The lookbehinds keep "no reply",
# "never replied" and "without response" out of the response count.
REPLY_NOTE_RE = re.compile(r"(?<!no )(?<!never )(?<!without )(reply|replied|response|rejected by)",
                           re.I)

PIPELINE_COLUMNS = ["Company", "Role", "Source", "Channel", "Applied", "Stage",
                    "Next action", "Due", "Last touch", "Resume", "Notes"]
CONTACT_COLUMNS = ["Name", "Company", "Role", "Relationship", "Target role",
                   "Last touch", "Next touch", "Status", "Notes"]

STALE_DAYS = 7
AUTO_COLD_DAYS = 21
INTERVIEW_WINDOW_DAYS = 7

BENCHMARKS = "cold ~3% interview, referral ~40%, recruiter-inbound ~25% — Ashby 2025/26"
FRESH_LINE = "run search_jobs.py --days 2 for postings under 48 hours old."
NOTHING_DUE = "Nothing due — run search_jobs.py --days 2 for fresh postings."

FIX_TARGETING = ("Tighten targeting: re-run the knockout pre-check on the last 10 applications "
                 "and move to referral-first outreach (networking.md)")
FIX_SCREEN = ("Screens aren't converting: run a mock recruiter screen (interview-coach.md) "
              "and rework the six prepared answers")
FIX_CLOSE = ("Onsites aren't closing: debrief each final round, run the offer-stage questions, "
             "and rehearse negotiation (offer-coach.md)")
FIX_TOO_SMALL = "Pipeline too small to diagnose (n<10) — keep logging"
FIX_HEALTHY = ("No clear leak — hold the cadence: keep 10–20 targeted applications "
               "and 60/40 outreach per week")

FUNNEL_RULES = """\
counting rules:
  Sent        every row whose Stage is not `saved`
  Responses   Stage in screen/interview/final/offer/accepted, plus `rejected`
              rows whose Notes contain "reply", "replied", "response" or
              "rejected by" (case-insensitive) — a rejection letter is still a
              response, while "no reply" / "never replied" / "without
              response" are not
  Interviews  Stage in interview/final/offer/accepted
  Offers      Stage in offer/accepted
Leak diagnosis: fewer than 10 sent -> too small to diagnose; otherwise the
first failing stage — response % < 10 -> targeting; responses >= 3 and
interviews == 0 -> screen performance; interviews >= 3 and offers == 0 ->
close; nothing failing -> healthy, hold the cadence.
"""

_DATE_RE = re.compile(r"^\d{4}-\d{2}-\d{2}$")
_REVIEW_LINE_RE = re.compile(r"^_Last weekly review:.*_[ \t]*$", re.M)


# --- small helpers -----------------------------------------------------------

def _cell(row: dict, key: str) -> str:
    return (row.get(key) or "").strip()


def _stage(row: dict) -> str:
    """The row's stage, lowercased; a blank stage reads as `saved`."""
    return _cell(row, "Stage").lower() or "saved"


def parse_date(value: str | None) -> datetime.date | None:
    """`YYYY-MM-DD` -> date; None for blank or unparseable cells."""
    value = (value or "").strip()
    if not _DATE_RE.match(value):
        return None
    try:
        return datetime.date.fromisoformat(value)
    except ValueError:
        return None


def _as_date(value) -> datetime.date:
    """Accept a date or an ISO string (so the pure functions take either)."""
    if isinstance(value, datetime.date):
        return value
    parsed = parse_date(str(value))
    if parsed is None:
        raise ValueError(f"bad date: {value!r}")
    return parsed


def _age(row: dict, key: str, date: datetime.date) -> int | None:
    d = parse_date(row.get(key))
    return None if d is None else (date - d).days


def _days(n: int) -> str:
    return "1 day" if abs(n) == 1 else f"{n} days"


def _append_note(existing: str, note: str) -> str:
    existing = existing.strip()
    note = note.strip()
    if not note:
        return existing
    return f"{existing}; {note}" if existing else note


def _pct(part: int, whole: int) -> float:
    return round(part / whole * 100, 1) if whole else 0.0


# --- file I/O ----------------------------------------------------------------

def _read(path: Path, columns: list[str]) -> tuple[list[str], list[dict]]:
    if not path.exists():
        return list(columns), []
    cols, rows = read_table(path.read_text(encoding="utf-8"))
    return (cols or list(columns)), rows


def _write(path: Path, columns: list[str], rows: list[dict]) -> None:
    md = path.read_text(encoding="utf-8") if path.exists() else ""
    out = write_table(md, columns, rows)
    with open(path, "w", encoding="utf-8", newline="\n") as fh:
        fh.write(out)


def pipeline_path(ws: Path) -> Path:
    return ws / "pipeline.md"


def contacts_path(ws: Path) -> Path:
    return ws / "contacts.md"


def load(ws: Path) -> tuple[list[str], list[dict]]:
    """The pipeline table of `ws/pipeline.md` as (columns, rows)."""
    return _read(pipeline_path(ws), PIPELINE_COLUMNS)


def save(ws: Path, columns: list[str], rows: list[dict]) -> None:
    """Write `rows` back into the pipeline table of `ws/pipeline.md`."""
    _write(pipeline_path(ws), columns, rows)


def get_contacts(ws: Path) -> tuple[list[str], list[dict]]:
    return _read(contacts_path(ws), CONTACT_COLUMNS)


def save_contacts(ws: Path, columns: list[str], rows: list[dict]) -> None:
    _write(contacts_path(ws), columns, rows)


def set_review_line(ws: Path, iso: str) -> None:
    """Point the `_Last weekly review: …_` line at `iso` (appending it if absent)."""
    path = pipeline_path(ws)
    md = path.read_text(encoding="utf-8") if path.exists() else ""
    line = f"_Last weekly review: {iso}_"
    out, n = _REVIEW_LINE_RE.subn(line, md, count=1)
    if not n:
        out = (md.rstrip("\n") + "\n\n" + line + "\n") if md.strip() else line + "\n"
    if not out.endswith("\n"):
        out += "\n"
    with open(path, "w", encoding="utf-8", newline="\n") as fh:
        fh.write(out)


# --- today view (pure) -------------------------------------------------------

def today_data(rows: list[dict], contacts_rows: list[dict], date) -> dict:
    """The today view as structured data — no I/O, no clock."""
    date = _as_date(date)
    horizon = date + datetime.timedelta(days=INTERVIEW_WINDOW_DAYS)
    overdue, due_today, interviews, stale, auto_cold = [], [], [], [], []

    for row in rows:
        stage, due = _stage(row), parse_date(row.get("Due"))
        open_row = stage not in TERMINAL_STAGES
        if due and open_row:
            if due < date:
                overdue.append(row)
            elif due == date:
                due_today.append(row)
            elif due <= horizon and stage in INTERVIEW_DUE_STAGES:
                interviews.append(row)
        touch_age = _age(row, "Last touch", date)
        if touch_age is not None and stage in OPEN_STAGES and touch_age > STALE_DAYS:
            stale.append(row)
        if touch_age is not None and stage == "applied" and touch_age >= AUTO_COLD_DAYS:
            auto_cold.append(row)

    def by_due(row):
        return (row.get("Due") or "", _cell(row, "Company"))

    def by_touch(row):
        return (row.get("Last touch") or "", _cell(row, "Company"))

    contacts_due = [c for c in contacts_rows
                    if (d := parse_date(c.get("Next touch"))) is not None and d <= date]
    return {
        "date": date.isoformat(),
        "overdue": sorted(overdue, key=by_due),
        "due_today": sorted(due_today, key=by_due),
        "interviews": sorted(interviews, key=by_due),
        "stale": sorted(stale, key=by_touch),
        "auto_cold": sorted(auto_cold, key=by_touch),
        "contacts_due": sorted(contacts_due, key=lambda c: (c.get("Next touch") or "",
                                                            _cell(c, "Name"))),
    }


def _who(row: dict) -> str:
    company, role = _cell(row, "Company") or "(no company)", _cell(row, "Role")
    return f"{company} — {role}" if role else company


def _next_action(row: dict) -> str:
    return _cell(row, "Next action") or "(no next action set)"


def _cold_command(row: dict) -> str:
    return (f'tracker.py set --company "{_cell(row, "Company")}" '
            f'--role "{_cell(row, "Role")}" --stage cold')


def _section(title: str, items: list[str], note: str = "") -> list[str]:
    if not items:
        return []
    head = f"**{title} ({len(items)})**" + (f" — {note}" if note else "")
    return [head, *items, ""]


def today_report(rows: list[dict], contacts_rows: list[dict], date) -> str:
    """The today view as markdown — sections omitted when empty."""
    data = today_data(rows, contacts_rows, date)
    day = _as_date(date)
    out = [f"## Today — {data['date']}", ""]

    def line(row, tail):
        return f"- {_who(row)} · {_stage(row)} · {tail}"

    out += _section("Overdue", [
        line(r, f"due {_cell(r, 'Due')} ({_days(_age(r, 'Due', day))} late) · {_next_action(r)}")
        for r in data["overdue"]])
    out += _section("Due today", [line(r, _next_action(r)) for r in data["due_today"]])
    out += _section("Interviews within 7 days", [
        line(r, f"{_cell(r, 'Due')} (in {_days(-_age(r, 'Due', day))}) · {_next_action(r)}")
        for r in data["interviews"]], note=f"due in the next {INTERVIEW_WINDOW_DAYS} days")
    out += _section("Stale", [
        line(r, f"last touch {_cell(r, 'Last touch')} "
                f"({_days(_age(r, 'Last touch', day))} ago) · {_next_action(r)}")
        for r in data["stale"]], note=f"no touch in over {STALE_DAYS} days")
    out += _section("Auto-cold candidates", [
        line(r, f"last touch {_cell(r, 'Last touch')} "
                f"({_days(_age(r, 'Last touch', day))} ago) → `{_cold_command(r)}`")
        for r in data["auto_cold"]], note=f"applied and silent for {AUTO_COLD_DAYS}+ days")
    out += _section("Contacts due", [
        f"- {_cell(c, 'Name')} — {_cell(c, 'Company') or '(no company)'} · "
        f"{_cell(c, 'Relationship') or 'contact'} · next touch {_cell(c, 'Next touch')}"
        f"{' · ' + _cell(c, 'Status') if _cell(c, 'Status') else ''}"
        for c in data["contacts_due"]])

    if len(out) == 2:  # nothing but the header
        return "\n".join(out + [NOTHING_DUE, ""])
    return "\n".join(out + [f"**Fresh postings** — {FRESH_LINE}", ""])


# --- funnel (pure) -----------------------------------------------------------

def _is_response(row: dict) -> bool:
    stage = _stage(row)
    if stage in RESPONSE_STAGES:
        return True
    return stage == "rejected" and bool(REPLY_NOTE_RE.search(_cell(row, "Notes")))


def _bucket(key: str, rows: list[dict]) -> dict:
    sent = [r for r in rows if _stage(r) != "saved"]
    responses = [r for r in sent if _is_response(r)]
    interviews = [r for r in sent if _stage(r) in INTERVIEWED_STAGES]
    offers = [r for r in sent if _stage(r) in OFFER_STAGES]
    return {
        "key": key, "rows": len(rows), "sent": len(sent), "responses": len(responses),
        "interviews": len(interviews), "offers": len(offers),
        "response_pct": _pct(len(responses), len(sent)),
        "interview_pct": _pct(len(interviews), len(sent)),
    }


def _group(rows: list[dict], column: str) -> list[dict]:
    groups: dict[str, tuple[str, list[dict]]] = {}
    for row in rows:
        if not _cell(row, column) and _stage(row) == "saved":
            continue  # never sent: an "(unset)" bucket of zeros says nothing
        label = _cell(row, column) or "(unset)"
        _, members = groups.setdefault(label.lower(), (label, []))
        members.append(row)
    buckets = [_bucket(label, members) for label, members in groups.values()]
    return sorted(buckets, key=lambda b: (-b["sent"], b["key"].lower()))


def funnel(rows: list[dict]) -> dict:
    """Sent -> response -> interview -> offer counts by channel and by source."""
    return {
        "channels": _group(rows, "Channel"),
        "sources": _group(rows, "Source"),
        "total": _bucket("All", rows),
    }


def diagnose(f: dict) -> tuple[str, str]:
    """(leak stage, the one recommended change) — takes a funnel or a totals dict."""
    c = f.get("total", f)
    sent, responses = int(c.get("sent", 0)), int(c.get("responses", 0))
    interviews, offers = int(c.get("interviews", 0)), int(c.get("offers", 0))
    response_pct = c.get("response_pct", _pct(responses, sent))
    if sent < 10:
        return "too small", FIX_TOO_SMALL
    if response_pct < 10:
        return "targeting", FIX_TARGETING
    if responses >= 3 and interviews == 0:
        return "screen performance", FIX_SCREEN
    if interviews >= 3 and offers == 0:
        return "close", FIX_CLOSE
    return "healthy", FIX_HEALTHY


def _funnel_table(label: str, buckets: list[dict], total: dict) -> str:
    columns = [label, "Sent", "Responses", "Interviews", "Offers", "Response %", "Interview %"]

    def row(b, key):
        return {label: key, "Sent": b["sent"], "Responses": b["responses"],
                "Interviews": b["interviews"], "Offers": b["offers"],
                "Response %": f"{b['response_pct']:.0f}%",
                "Interview %": f"{b['interview_pct']:.0f}%"}

    rows = [row(b, b["key"]) for b in buckets] + [row(total, "**All**")]
    return write_table("", columns, rows).rstrip("\n")


def funnel_report(rows: list[dict], date) -> str:
    """The funnel as markdown: two tables, the benchmarks line, the leak diagnosis."""
    f = funnel(rows)
    leak, fix = diagnose(f)
    return "\n".join([
        f"## Funnel — {_as_date(date).isoformat()}",
        "",
        _funnel_table("Channel", f["channels"], f["total"]),
        "",
        _funnel_table("Source", f["sources"], f["total"]),
        "",
        f"Benchmarks: {BENCHMARKS}",
        f"Leak: {leak} — {fix}",
        "",
    ])


def contacts_report(contacts_rows: list[dict], date) -> str:
    """Contacts whose Next touch is due, oldest first."""
    due = today_data([], contacts_rows, date)["contacts_due"]
    day = _as_date(date).isoformat()
    if not due:
        return f"## Contacts due — {day}\n\nNothing due — pick two targets and set a next touch.\n"
    lines = [f"## Contacts due — {day}", ""]
    for c in due:
        target = _cell(c, "Target role")
        lines.append(
            f"- {_cell(c, 'Name')} — {_cell(c, 'Company') or '(no company)'} · "
            f"{_cell(c, 'Relationship') or 'contact'} · next touch {_cell(c, 'Next touch')}"
            f"{' · for ' + target if target else ''}"
            f"{' · ' + _cell(c, 'Notes') if _cell(c, 'Notes') else ''}")
    return "\n".join(lines + [""])


# --- commands ----------------------------------------------------------------

def _has_workspace(ws: Path) -> bool:
    return pipeline_path(ws).exists()


def _bad_stage(stage: str) -> str | None:
    if stage is None or stage.lower() in STAGES:
        return None
    return f"Unknown stage {stage!r} — use one of: {', '.join(STAGES)}"


def _bad_dates(args) -> str | None:
    for flag in ("due", "applied", "last_touch", "next_touch", "today_"):
        value = getattr(args, flag, None)
        if value and parse_date(value) is None:
            return f"Bad date {value!r} for --{flag.rstrip('_').replace('_', '-')} — use YYYY-MM-DD"
    return None


def _is_same(a: str, b: str) -> bool:
    return (a or "").strip().lower() == (b or "").strip().lower()


def _matches(rows: list[dict], field: str, value: str) -> list[dict]:
    """Exact case-insensitive matches, falling back to substring matches."""
    needle = (value or "").strip().lower()
    exact = [r for r in rows if _is_same(r.get(field), needle)]
    if exact:
        return exact
    return [r for r in rows if needle and needle in _cell(r, field).lower()]


def _apply_fields(row: dict, args, touch: str, *, creating: bool) -> None:
    """Copy the given flags onto `row`; Last touch always becomes `touch`."""
    for flag, column in (("source", "Source"), ("channel", "Channel"),
                         ("next_", "Next action"), ("due", "Due"), ("resume", "Resume"),
                         ("applied", "Applied")):
        value = getattr(args, flag, None)
        if value is not None:
            row[column] = value
    stage = getattr(args, "stage", None)
    if stage:
        row["Stage"] = stage.lower()
    notes = getattr(args, "notes", None)
    if notes is not None:
        row["Notes"] = notes if creating else _append_note(_cell(row, "Notes"), notes)
    for extra in (getattr(args, "note", None), getattr(args, "url", None)):
        if extra:
            row["Notes"] = _append_note(_cell(row, "Notes"), extra)
    # An open sent row carries the date it went out; a row closed straight
    # from `saved` (cold, withdrawn) never had one.
    if not _cell(row, "Applied") and _stage(row) in SENT_OPEN_STAGES:
        row["Applied"] = touch
    row["Last touch"] = touch


def cmd_add(ws: Path, args, touch: str) -> int:
    columns, rows = load(ws)
    existing = [r for r in rows
                if _is_same(r.get("Company"), args.company) and _is_same(r.get("Role"), args.role)]
    if existing:
        row, created = existing[0], False
    else:
        row = dict.fromkeys(columns, "")
        row["Company"], row["Role"], row["Stage"] = args.company, args.role, "saved"
        rows.append(row)
        created = True
    _apply_fields(row, args, touch, creating=created)
    save(ws, columns, rows)
    verb = "added" if created else "updated existing row"
    print(f"{verb}: {_who(row)} · {_stage(row)} · last touch {row['Last touch']}")
    return 0


SET_FLAGS = ("stage", "next_", "due", "note", "resume", "applied", "source", "channel", "url")


def cmd_set(ws: Path, args, touch: str) -> int:
    if not any(getattr(args, flag, None) for flag in SET_FLAGS) and not args.last_touch:
        print("nothing to set — pass at least one of "
              "--stage/--next/--due/--note/--resume/--applied/--source/--channel/--last-touch")
        return 2
    columns, rows = load(ws)
    found = _matches(rows, "Company", args.company)
    if args.role:
        found = _matches(found, "Role", args.role)
    if not found:
        role = f" and role {args.role!r}" if args.role else ""
        print(f"No pipeline row for company {args.company!r}{role} — run `tracker.py add` first.")
        return 2
    if len(found) > 1:
        print(f"{len(found)} rows match company {args.company!r} — add --role to pick one:")
        for row in found:
            print(f"  - {_who(row)} · {_stage(row)}")
        return 2
    row = found[0]
    _apply_fields(row, args, touch, creating=False)
    save(ws, columns, rows)
    print(f"updated: {_who(row)} · {_stage(row)} · next {_next_action(row)} "
          f"· due {_cell(row, 'Due') or '—'} · last touch {row['Last touch']}")
    return 0


def cmd_contact(ws: Path, args, touch: str) -> int:
    columns, rows = get_contacts(ws)
    found = [r for r in rows if _is_same(r.get("Name"), args.name)]
    if args.company is not None:
        found = [r for r in found if _is_same(r.get("Company"), args.company)]
    elif len(found) > 1:
        print(f"{len(found)} contacts named {args.name!r} — add --company to pick one:")
        for row in found:
            print(f"  - {_cell(row, 'Name')} — {_cell(row, 'Company') or '(no company)'}")
        return 2
    if found:
        row, created = found[0], False
    else:
        row, created = dict.fromkeys(columns, ""), True
        row["Name"], row["Company"] = args.name, args.company or ""
        rows.append(row)
    for flag, column in (("role", "Role"), ("relationship", "Relationship"),
                         ("target", "Target role"), ("next_touch", "Next touch"),
                         ("status", "Status")):
        value = getattr(args, flag, None)
        if value is not None:
            row[column] = value
    if args.note:
        row["Notes"] = _append_note(_cell(row, "Notes"), args.note)
    row["Last touch"] = touch
    save_contacts(ws, columns, rows)
    verb = "added contact" if created else "updated contact"
    print(f"{verb}: {_cell(row, 'Name')} — {_cell(row, 'Company') or '(no company)'} "
          f"· last touch {row['Last touch']} · next touch {_cell(row, 'Next touch') or '—'}")
    return 0


def cmd_today(ws: Path, args, date: datetime.date) -> int:
    _, rows = load(ws)
    _, contacts_rows = get_contacts(ws)
    if args.as_json:
        print(json.dumps(today_data(rows, contacts_rows, date), indent=2))
    else:
        print(today_report(rows, contacts_rows, date))
    return 0


def cmd_funnel(ws: Path, args, date: datetime.date) -> int:
    _, rows = load(ws)
    if args.as_json:
        data = funnel(rows)
        leak, fix = diagnose(data)
        data["leak"], data["recommendation"], data["benchmarks"] = leak, fix, BENCHMARKS
        print(json.dumps(data, indent=2))
    else:
        print(funnel_report(rows, date))
    return 0


def cmd_contacts(ws: Path, args, date: datetime.date) -> int:
    _, contacts_rows = get_contacts(ws)
    print(contacts_report(contacts_rows, date))
    return 0


def cmd_digest(ws: Path, args, date: datetime.date) -> int:
    _, rows = load(ws)
    _, contacts_rows = get_contacts(ws)
    iso = date.isoformat()
    text = "\n".join([
        f"# Weekly review — {iso}",
        "",
        funnel_report(rows, date),
        today_report(rows, contacts_rows, date),
        "_Next: apply the one recommended change, then set this week's application cap "
        "and outreach target._",
        "",
    ])
    out = ws / "reviews" / f"{iso}.md"
    out.parent.mkdir(parents=True, exist_ok=True)
    with open(out, "w", encoding="utf-8", newline="\n") as fh:
        fh.write(text)
    set_review_line(ws, iso)
    print(f"Wrote {out}\nLast weekly review in pipeline.md is now {iso}.")
    return 0


# --- CLI ---------------------------------------------------------------------

def build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(prog="tracker.py", description=__doc__,
                                formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = p.add_subparsers(dest="cmd")

    common = argparse.ArgumentParser(add_help=False)
    common.add_argument("--today", dest="today_", metavar="YYYY-MM-DD",
                        help="pretend today is this date (default: the system date)")

    def add_sub(name, help_, **kw):
        return sub.add_parser(name, parents=[common], help=help_, description=help_, **kw)

    a = add_sub("add", "add a pipeline row (or update the matching company+role)")
    a.add_argument("--company", required=True)
    a.add_argument("--role", required=True)
    a.add_argument("--source", help="JobStreet, MCF, LinkedIn, career page, agency, referral")
    a.add_argument("--channel", help="cold / referral / recruiter-inbound / agency")
    a.add_argument("--stage", help=f"one of: {', '.join(STAGES)} (default: saved on a new row)")
    a.add_argument("--url", help="posting URL — appended to Notes (the table has no URL column)")
    a.add_argument("--next", dest="next_", metavar="TEXT", help="next action")
    a.add_argument("--due", metavar="YYYY-MM-DD", help="when the next action is due")
    a.add_argument("--applied", metavar="YYYY-MM-DD",
                   help="date the application went out (default: today for any stage past saved)")
    a.add_argument("--resume", help="resume file used")
    a.add_argument("--notes", help="Notes cell (appended when the row already exists)")
    a.add_argument("--last-touch", dest="last_touch", metavar="YYYY-MM-DD",
                   help="override Last touch (default: today)")

    s = add_sub("set", "update the matching pipeline row")
    s.add_argument("--company", required=True)
    s.add_argument("--role", help="required when the company matches more than one row")
    s.add_argument("--stage", help=f"one of: {', '.join(STAGES)}")
    s.add_argument("--next", dest="next_", metavar="TEXT")
    s.add_argument("--due", metavar="YYYY-MM-DD")
    s.add_argument("--note", metavar="TEXT", help="appended to Notes with '; '")
    s.add_argument("--resume")
    s.add_argument("--applied", metavar="YYYY-MM-DD")
    s.add_argument("--source")
    s.add_argument("--channel")
    s.add_argument("--url", help="appended to Notes")
    s.add_argument("--last-touch", dest="last_touch", metavar="YYYY-MM-DD")

    t = add_sub("today", "overdue, due today, interviews, stale, auto-cold, contacts due")
    t.add_argument("--json", dest="as_json", action="store_true", help="structured output")

    f = add_sub("funnel", "sent -> response -> interview -> offer by channel and source",
                epilog=FUNNEL_RULES, formatter_class=argparse.RawDescriptionHelpFormatter)
    f.add_argument("--json", dest="as_json", action="store_true", help="structured output")

    add_sub("digest", "write reviews/<today>.md and update the last-review line")
    add_sub("contacts", "contacts whose Next touch is due")

    c = add_sub("contact", "upsert a contact row (matched by name + company)")
    c.add_argument("--name", required=True)
    c.add_argument("--company", help="required only when one name appears at two companies")
    c.add_argument("--role")
    c.add_argument("--relationship",
                   help="alumni / ex-colleague / recruiter / hiring-manager / peer / 2nd-degree")
    c.add_argument("--target", metavar="ROLE", help="target role at that company")
    c.add_argument("--last-touch", dest="last_touch", metavar="YYYY-MM-DD")
    c.add_argument("--next-touch", dest="next_touch", metavar="YYYY-MM-DD")
    c.add_argument("--status")
    c.add_argument("--note", metavar="TEXT", help="appended to Notes with '; '")
    return p


WRITERS = {"add": cmd_add, "set": cmd_set, "contact": cmd_contact}
READERS = {"today": cmd_today, "funnel": cmd_funnel, "contacts": cmd_contacts,
           "digest": cmd_digest}


def main(argv=None) -> int:
    use_utf8_output()
    parser = build_parser()
    args = parser.parse_args(argv)
    if not args.cmd:
        parser.print_help()
        return 2

    ws = workspace_dir()
    if not _has_workspace(ws):
        print(f"No workspace found — run: python3 {SCRIPT_DIR / 'workspace.py'} init")
        return 0

    problem = _bad_dates(args) or _bad_stage(getattr(args, "stage", None))
    if problem:
        print(problem)
        return 2

    date = parse_date(args.today_) or datetime.date.fromisoformat(today_iso())
    if args.cmd in WRITERS:
        touch = getattr(args, "last_touch", None) or date.isoformat()
        return WRITERS[args.cmd](ws, args, touch)
    return READERS[args.cmd](ws, args, date)


if __name__ == "__main__":
    sys.exit(main())
