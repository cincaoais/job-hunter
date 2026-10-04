"""Tests for tracker.py — add/set round-trip, today view, funnel, diagnosis, digest, contacts.

No network and no clock dependency: every date-sensitive assertion pins
`--today 2026-09-16`, which is what `fixtures/pipeline-sample.md` and
`fixtures/contacts-sample.md` are written against.
"""
import datetime
import json
import pathlib
import shutil
import sys

import pytest

ROOT = pathlib.Path(__file__).resolve().parents[1]
SCRIPTS = ROOT / "skills" / "job-hunting" / "scripts"
ASSETS = ROOT / "skills" / "job-hunting" / "assets"
FIXTURES = pathlib.Path(__file__).resolve().parent / "fixtures"
sys.path.insert(0, str(SCRIPTS))

import tracker  # noqa: E402
from _common import read_table  # noqa: E402

TODAY = "2026-09-16"
DATE = datetime.date(2026, 9, 16)


@pytest.fixture
def ws(tmp_path, monkeypatch):
    """An empty-but-initialized workspace (templates copied, like workspace.py init)."""
    shutil.copyfile(ASSETS / "pipeline-template.md", tmp_path / "pipeline.md")
    shutil.copyfile(ASSETS / "contacts-template.md", tmp_path / "contacts.md")
    (tmp_path / "reviews").mkdir()
    monkeypatch.setenv("JOB_HUNT_DIR", str(tmp_path))
    return tmp_path


@pytest.fixture
def filled(tmp_path, monkeypatch):
    """A workspace holding the 8-row sample pipeline and the sample contacts."""
    shutil.copyfile(FIXTURES / "pipeline-sample.md", tmp_path / "pipeline.md")
    shutil.copyfile(FIXTURES / "contacts-sample.md", tmp_path / "contacts.md")
    (tmp_path / "reviews").mkdir()
    monkeypatch.setenv("JOB_HUNT_DIR", str(tmp_path))
    return tmp_path


def run(capsys, *argv):
    """Run the CLI in-process, returning (exit code, stdout)."""
    code = tracker.main(list(argv))
    return code, capsys.readouterr().out


def pipeline_rows(ws):
    return read_table((ws / "pipeline.md").read_text(encoding="utf-8"))[1]


SAMPLE_ROWS = read_table((FIXTURES / "pipeline-sample.md").read_text(encoding="utf-8"))[1]
SAMPLE_CONTACTS = read_table((FIXTURES / "contacts-sample.md").read_text(encoding="utf-8"))[1]


# --- add / set ---------------------------------------------------------------

def test_add_writes_a_row_with_last_touch_today(ws, capsys):
    code, out = run(capsys, "add", "--company", "Apex Digital", "--role", "Backend Engineer",
                    "--source", "JobStreet", "--channel", "cold", "--next", "Apply with v1 resume",
                    "--due", "2026-09-18", "--today", TODAY)
    assert code == 0, out
    rows = pipeline_rows(ws)
    assert len(rows) == 1
    row = rows[0]
    assert row["Company"] == "Apex Digital"
    assert row["Role"] == "Backend Engineer"
    assert row["Source"] == "JobStreet"
    assert row["Channel"] == "cold"
    assert row["Stage"] == "saved"
    assert row["Next action"] == "Apply with v1 resume"
    assert row["Due"] == "2026-09-18"
    assert row["Last touch"] == TODAY
    assert row["Applied"] == ""  # saved rows were never sent


def test_add_then_set_round_trip(ws, capsys):
    run(capsys, "add", "--company", "Apex Digital", "--role", "Backend Engineer", "--today", TODAY)
    code, out = run(capsys, "set", "--company", "apex digital", "--stage", "applied",
                    "--next", "Send the one polite nudge", "--due", "2026-09-23",
                    "--resume", "apex-backend-v1.md", "--note", "Applied via board",
                    "--today", "2026-09-17")
    assert code == 0, out
    rows = pipeline_rows(ws)
    assert len(rows) == 1
    row = rows[0]
    assert row["Stage"] == "applied"
    assert row["Next action"] == "Send the one polite nudge"
    assert row["Due"] == "2026-09-23"
    assert row["Resume"] == "apex-backend-v1.md"
    assert row["Applied"] == "2026-09-17"  # filled when the stage leaves `saved`
    assert row["Last touch"] == "2026-09-17"
    assert "Applied via board" in row["Notes"]


def test_set_note_appends_to_existing_notes(ws, capsys):
    run(capsys, "add", "--company", "Apex", "--role", "Backend Engineer",
        "--notes", "first note", "--today", TODAY)
    run(capsys, "set", "--company", "Apex", "--note", "second note", "--today", TODAY)
    assert pipeline_rows(ws)[0]["Notes"] == "first note; second note"


def test_add_existing_pair_updates_instead_of_duplicating(ws, capsys):
    run(capsys, "add", "--company", "Apex Digital", "--role", "Backend Engineer", "--today", TODAY)
    code, out = run(capsys, "add", "--company", "APEX DIGITAL", "--role", "backend engineer",
                    "--stage", "applied", "--today", TODAY)
    assert code == 0
    assert "updated existing row" in out
    rows = pipeline_rows(ws)
    assert len(rows) == 1
    assert rows[0]["Stage"] == "applied"
    assert rows[0]["Company"] == "Apex Digital"  # original casing kept


def test_add_on_an_existing_row_keeps_the_stage_it_had(ws, capsys):
    run(capsys, "add", "--company", "Apex Digital", "--role", "Backend Engineer", "--today", TODAY)
    run(capsys, "set", "--company", "Apex Digital", "--stage", "screen", "--today", TODAY)
    run(capsys, "add", "--company", "Apex Digital", "--role", "Backend Engineer",
        "--source", "LinkedIn", "--today", TODAY)
    row = pipeline_rows(ws)[0]
    assert row["Stage"] == "screen"  # no --stage given -> not reset to saved
    assert row["Source"] == "LinkedIn"


def test_set_bad_stage_exits_2_and_lists_the_vocabulary(ws, capsys):
    run(capsys, "add", "--company", "Apex", "--role", "Backend Engineer", "--today", TODAY)
    code, out = run(capsys, "set", "--company", "Apex", "--stage", "ghosted", "--today", TODAY)
    assert code == 2
    assert "ghosted" in out
    for stage in tracker.STAGES:
        assert stage in out
    assert pipeline_rows(ws)[0]["Stage"] == "saved"  # nothing written


def test_add_bad_stage_exits_2(ws, capsys):
    code, out = run(capsys, "add", "--company", "Apex", "--role", "BE", "--stage", "nope")
    assert code == 2
    assert "nope" in out
    assert pipeline_rows(ws) == []


def test_set_ambiguous_company_lists_candidates_and_exits_2(ws, capsys):
    run(capsys, "add", "--company", "Apex Digital", "--role", "Backend Engineer", "--today", TODAY)
    run(capsys, "add", "--company", "Apex Digital", "--role", "Platform Engineer", "--today", TODAY)
    code, out = run(capsys, "set", "--company", "Apex Digital", "--stage", "applied", "--today", TODAY)
    assert code == 2
    assert "Backend Engineer" in out and "Platform Engineer" in out
    assert all(r["Stage"] == "saved" for r in pipeline_rows(ws))
    code, out = run(capsys, "set", "--company", "Apex Digital", "--role", "Platform Engineer",
                    "--stage", "applied", "--today", TODAY)
    assert code == 0, out
    stages = {r["Role"]: r["Stage"] for r in pipeline_rows(ws)}
    assert stages == {"Backend Engineer": "saved", "Platform Engineer": "applied"}


def test_set_unknown_company_exits_2(ws, capsys):
    code, out = run(capsys, "set", "--company", "Nowhere", "--stage", "applied", "--today", TODAY)
    assert code == 2
    assert "Nowhere" in out


def test_set_with_nothing_to_change_exits_2(ws, capsys):
    run(capsys, "add", "--company", "Apex", "--role", "BE", "--today", TODAY)
    code, out = run(capsys, "set", "--company", "Apex", "--today", TODAY)
    assert code == 2
    assert "nothing to set" in out.lower()


def test_applied_stays_empty_when_a_saved_row_is_closed(ws, capsys):
    run(capsys, "add", "--company", "Apex", "--role", "BE", "--today", TODAY)
    run(capsys, "set", "--company", "Apex", "--stage", "cold", "--today", TODAY)
    row = pipeline_rows(ws)[0]
    assert (row["Stage"], row["Applied"]) == ("cold", "")
    run(capsys, "set", "--company", "Apex", "--stage", "screen", "--today", TODAY)
    assert pipeline_rows(ws)[0]["Applied"] == TODAY  # an open sent stage does back-fill


def test_bad_date_exits_2(ws, capsys):
    code, out = run(capsys, "add", "--company", "Apex", "--role", "BE", "--due", "18/09/2026")
    assert code == 2
    assert "YYYY-MM-DD" in out


# --- today view --------------------------------------------------------------

def test_today_report_sections_list_the_planted_rows(capsys):
    report = tracker.today_report(SAMPLE_ROWS, SAMPLE_CONTACTS, DATE)
    sections = {}
    current = None
    for line in report.splitlines():
        if line.startswith("**"):
            current = line.strip("*").split(" (")[0]
            sections[current] = []
        elif line.startswith("- ") and current:
            sections[current].append(line)

    def body(name):
        return "\n".join(sections[name])

    assert "Apex Digital" in body("Overdue")
    assert "Nimbus Logistics" in body("Due today")
    assert "Selangor Cloud" in body("Interviews within 7 days")
    assert "**Interviews within 7 days (1)** — due in the next 7 days" in report
    stale = body("Stale")
    assert "Harbour Fintech" in stale and "Pulse Retail" in stale
    assert "Apex Digital" not in stale  # last touch is exactly 7 days old
    cold = body("Auto-cold candidates")
    assert "Pulse Retail" in cold and "Harbour Fintech" not in cold
    assert 'tracker.py set --company "Pulse Retail" --role "Backend Engineer" --stage cold' in cold
    assert "Aisyah Rahman" in body("Contacts due")
    assert "Daniel Lim" not in report and "Priya Nair" not in report
    assert "search_jobs.py --days 2" in report


def test_today_report_hides_terminal_and_saved_rows(capsys):
    report = tracker.today_report(SAMPLE_ROWS, SAMPLE_CONTACTS, DATE)
    for company in ("Orion Systems", "Kuala Data", "Straits Media"):
        assert company not in report


def test_today_report_empty_pipeline_says_nothing_due():
    report = tracker.today_report([], [], DATE)
    assert "Nothing due — run search_jobs.py --days 2 for fresh postings." in report
    assert "Overdue" not in report


def test_today_command_and_json(filled, capsys):
    code, out = run(capsys, "today", "--today", TODAY)
    assert code == 0
    assert "Apex Digital" in out and "Kuala Data" not in out
    code, out = run(capsys, "today", "--today", TODAY, "--json")
    assert code == 0
    data = json.loads(out)
    assert data["date"] == TODAY
    assert [r["Company"] for r in data["overdue"]] == ["Apex Digital"]
    assert [r["Company"] for r in data["due_today"]] == ["Nimbus Logistics"]
    assert [r["Company"] for r in data["interviews"]] == ["Selangor Cloud"]
    assert {r["Company"] for r in data["stale"]} == {"Harbour Fintech", "Pulse Retail"}
    assert [r["Company"] for r in data["auto_cold"]] == ["Pulse Retail"]
    assert [c["Name"] for c in data["contacts_due"]] == ["Aisyah Rahman"]


@pytest.mark.parametrize("due, debriefs, listed", [
    ("2026-09-15", None, True),                                  # yesterday, no debrief
    ("2026-09-15", {"apex-digital-backend-engineer": "2026-09-15"}, False),  # debriefed
    ("2026-09-06", None, False),                                 # 10 days late: plain overdue
])
def test_today_data_debriefs_due(due, debriefs, listed):
    row = {"Company": "Apex Digital", "Role": "Backend Engineer", "Stage": "interview",
           "Due": due, "Last touch": "2026-09-01"}
    data = tracker.today_data([row], [], DATE, debriefs=debriefs)
    assert [r["Company"] for r in data["debriefs_due"]] == (["Apex Digital"] if listed else [])
    assert [r["Company"] for r in data["overdue"]] == ([] if listed else ["Apex Digital"])


def test_today_command_lists_debriefs_due(ws, capsys):
    run(capsys, "add", "--company", "Apex Digital", "--role", "Backend Engineer",
        "--stage", "interview", "--due", "2026-09-15", "--today", TODAY)
    code, out = run(capsys, "today", "--today", TODAY)
    assert code == 0
    assert "**Debriefs due (1)**" in out and "Apex Digital" in out
    assert "/job-hunter:interview debrief" in out and "**Overdue" not in out
    folder = ws / "interviews" / "apex-digital-backend-engineer"
    folder.mkdir(parents=True)
    (folder / "2026-09-15-debrief-technical.md").write_text("x", encoding="utf-8")
    code, out = run(capsys, "today", "--today", TODAY, "--json")
    assert json.loads(out)["debriefs_due"] == []


# --- funnel ------------------------------------------------------------------

def test_funnel_channel_counts_match_hand_computed():
    f = tracker.funnel(SAMPLE_ROWS)
    by_channel = {r["key"]: r for r in f["channels"]}
    assert set(by_channel) == {"cold", "referral", "recruiter-inbound"}
    cold = by_channel["cold"]
    assert (cold["sent"], cold["responses"], cold["interviews"], cold["offers"]) == (3, 0, 0, 0)
    ref = by_channel["referral"]
    assert (ref["sent"], ref["responses"], ref["interviews"], ref["offers"]) == (2, 2, 1, 0)
    inb = by_channel["recruiter-inbound"]
    assert (inb["sent"], inb["responses"], inb["interviews"], inb["offers"]) == (2, 2, 1, 1)
    assert inb["response_pct"] == 100.0
    assert cold["response_pct"] == 0.0
    total = f["total"]
    assert (total["sent"], total["responses"], total["interviews"], total["offers"]) == (7, 4, 2, 1)


def test_funnel_source_counts_match_hand_computed():
    by_source = {r["key"]: r for r in tracker.funnel(SAMPLE_ROWS)["sources"]}
    assert set(by_source) == {"JobStreet", "LinkedIn", "MCF", "career page"}
    assert (by_source["JobStreet"]["sent"], by_source["JobStreet"]["responses"]) == (2, 0)
    assert (by_source["LinkedIn"]["sent"], by_source["LinkedIn"]["responses"],
            by_source["LinkedIn"]["interviews"]) == (2, 2, 0)
    assert (by_source["MCF"]["sent"], by_source["MCF"]["responses"],
            by_source["MCF"]["offers"]) == (2, 1, 1)
    assert (by_source["career page"]["sent"], by_source["career page"]["interviews"]) == (1, 1)


@pytest.mark.parametrize("notes, counts_as_response", [
    ("Rejected by email after the take-home", True),
    ("replied with a template", True),
    ("some response from the recruiter", True),
    ("no reply after 3 weeks", False),
    ("never replied", False),
    ("closed it myself without response", False),
    ("ghosted", False),
    ("no word, closed it myself", False),
])
def test_funnel_counts_a_rejection_as_a_response_only_when_a_human_answered(notes, counts_as_response):
    rows = [{"Company": "A", "Role": "R", "Source": "S", "Channel": "cold",
             "Stage": "rejected", "Notes": notes}]
    total = tracker.funnel(rows)["total"]
    assert (total["sent"], total["responses"]) == (1, int(counts_as_response))


def test_funnel_report_has_both_tables_benchmarks_and_leak(filled, capsys):
    code, out = run(capsys, "funnel", "--today", TODAY)
    assert code == 0
    assert "| Channel | Sent | Responses | Interviews | Offers | Response % | Interview % |" in out
    assert "| Source | Sent | Responses | Interviews | Offers | Response % | Interview % |" in out
    assert "cold ~3% interview, referral ~40%, recruiter-inbound ~25% — Ashby 2025/26" in out
    assert "Leak: too small — " + tracker.FIX_TOO_SMALL in out
    code, out = run(capsys, "funnel", "--today", TODAY, "--json")
    assert json.loads(out)["total"]["sent"] == 7


# --- diagnosis ---------------------------------------------------------------

def counts(sent, responses, interviews, offers):
    return {"sent": sent, "responses": responses, "interviews": interviews, "offers": offers,
            "response_pct": (responses / sent * 100) if sent else 0.0}


def test_diagnose_targeting_branch():
    assert tracker.diagnose(counts(20, 1, 0, 0)) == ("targeting", tracker.FIX_TARGETING)


def test_diagnose_screen_performance_branch():
    assert tracker.diagnose(counts(12, 5, 0, 0)) == ("screen performance", tracker.FIX_SCREEN)


def test_diagnose_close_branch():
    assert tracker.diagnose(counts(20, 8, 4, 0)) == ("close", tracker.FIX_CLOSE)


def test_diagnose_too_small_branch():
    assert tracker.diagnose(counts(4, 1, 1, 0)) == ("too small", tracker.FIX_TOO_SMALL)
    assert tracker.diagnose(counts(0, 0, 0, 0)) == ("too small", tracker.FIX_TOO_SMALL)


def test_diagnose_too_small_wins_below_ten_sent_however_bad_the_ratios():
    # 9 sent with no offer after 5 interviews would read as `close` at n >= 10.
    assert tracker.diagnose(counts(9, 9, 5, 0)) == ("too small", tracker.FIX_TOO_SMALL)
    assert tracker.diagnose(counts(9, 0, 0, 0)) == ("too small", tracker.FIX_TOO_SMALL)


def test_diagnose_healthy_branch():
    assert tracker.diagnose(counts(20, 10, 5, 2)) == ("healthy", tracker.FIX_HEALTHY)
    assert tracker.diagnose(counts(10, 2, 1, 1)) == ("healthy", tracker.FIX_HEALTHY)


def test_diagnose_accepts_a_whole_funnel_dict():
    assert tracker.diagnose(tracker.funnel(SAMPLE_ROWS))[0] == "too small"


# --- digest ------------------------------------------------------------------

def test_digest_writes_the_review_file_and_updates_the_review_line(filled, capsys):
    code, out = run(capsys, "digest", "--today", TODAY)
    assert code == 0, out
    review = filled / "reviews" / f"{TODAY}.md"
    assert review.exists()
    text = review.read_text(encoding="utf-8")
    assert "Leak:" in text
    assert "| Channel | Sent |" in text
    assert "Apex Digital" in text  # the today sections travel with the funnel
    assert str(review) in out
    pipeline = (filled / "pipeline.md").read_text(encoding="utf-8")
    assert f"_Last weekly review: {TODAY}_" in pipeline
    assert "_Last weekly review: 2026-09-07_" not in pipeline
    assert len(pipeline_rows(filled)) == 8  # rows untouched


def test_digest_on_a_fresh_workspace_sets_the_review_line(ws, capsys):
    code, out = run(capsys, "digest", "--today", TODAY)
    assert code == 0, out
    assert f"_Last weekly review: {TODAY}_" in (ws / "pipeline.md").read_text(encoding="utf-8")


# --- contacts ----------------------------------------------------------------

def test_contacts_lists_only_those_due(filled, capsys):
    code, out = run(capsys, "contacts", "--today", TODAY)
    assert code == 0
    assert "Aisyah Rahman" in out
    assert "Daniel Lim" not in out and "Priya Nair" not in out


def test_contact_creates_then_upserts(ws, capsys):
    code, out = run(capsys, "contact", "--name", "Aisyah Rahman", "--company", "Nimbus Logistics",
                    "--role", "Engineering Manager", "--relationship", "ex-colleague",
                    "--target", "Senior Backend Engineer", "--next-touch", "2026-09-22",
                    "--status", "connected", "--note", "asked about the team", "--today", TODAY)
    assert code == 0, out
    rows = read_table((ws / "contacts.md").read_text(encoding="utf-8"))[1]
    assert len(rows) == 1
    assert rows[0]["Name"] == "Aisyah Rahman"
    assert rows[0]["Last touch"] == TODAY
    assert rows[0]["Next touch"] == "2026-09-22"
    assert rows[0]["Notes"] == "asked about the team"

    code, out = run(capsys, "contact", "--name", "aisyah rahman", "--company", "nimbus logistics",
                    "--status", "referral asked", "--note", "she will flag my CV",
                    "--today", "2026-09-18")
    assert code == 0, out
    assert "updated" in out.lower()
    rows = read_table((ws / "contacts.md").read_text(encoding="utf-8"))[1]
    assert len(rows) == 1
    assert rows[0]["Name"] == "Aisyah Rahman"  # original casing kept
    assert rows[0]["Status"] == "referral asked"
    assert rows[0]["Relationship"] == "ex-colleague"  # untouched fields survive
    assert rows[0]["Last touch"] == "2026-09-18"
    assert rows[0]["Notes"] == "asked about the team; she will flag my CV"


def test_contact_updates_by_name_when_company_is_omitted(ws, capsys):
    run(capsys, "contact", "--name", "Aisyah Rahman", "--company", "Nimbus Logistics",
        "--relationship", "ex-colleague", "--today", TODAY)
    code, out = run(capsys, "contact", "--name", "aisyah rahman", "--status", "referral asked",
                    "--today", "2026-09-18")
    assert code == 0, out
    rows = read_table((ws / "contacts.md").read_text(encoding="utf-8"))[1]
    assert len(rows) == 1
    assert rows[0]["Company"] == "Nimbus Logistics"  # company not blanked
    assert rows[0]["Status"] == "referral asked"
    assert rows[0]["Last touch"] == "2026-09-18"


def test_contact_ambiguous_name_without_company_lists_candidates_and_exits_2(ws, capsys):
    run(capsys, "contact", "--name", "Sam Tan", "--company", "Apex Digital", "--today", TODAY)
    run(capsys, "contact", "--name", "Sam Tan", "--company", "Nimbus Logistics", "--today", TODAY)
    code, out = run(capsys, "contact", "--name", "Sam Tan", "--status", "messaged", "--today", TODAY)
    assert code == 2
    assert "Apex Digital" in out and "Nimbus Logistics" in out
    rows = read_table((ws / "contacts.md").read_text(encoding="utf-8"))[1]
    assert len(rows) == 2
    assert all(r["Status"] == "" for r in rows)  # nothing written


def test_contact_same_name_different_company_is_a_new_row(ws, capsys):
    run(capsys, "contact", "--name", "Sam Tan", "--company", "Apex Digital", "--today", TODAY)
    run(capsys, "contact", "--name", "Sam Tan", "--company", "Nimbus Logistics", "--today", TODAY)
    rows = read_table((ws / "contacts.md").read_text(encoding="utf-8"))[1]
    assert [r["Company"] for r in rows] == ["Apex Digital", "Nimbus Logistics"]


# --- no workspace ------------------------------------------------------------

@pytest.mark.parametrize("argv", [
    ["today"], ["funnel"], ["contacts"], ["digest"],
    ["add", "--company", "Apex", "--role", "BE"],
    ["set", "--company", "Apex", "--stage", "applied"],
    ["contact", "--name", "Sam Tan"],
])
def test_no_workspace_prints_hint_and_exits_zero(tmp_path, monkeypatch, capsys, argv):
    monkeypatch.setenv("JOB_HUNT_DIR", str(tmp_path / "missing"))
    code, out = run(capsys, *argv)
    assert code == 0, out
    assert "No workspace found — run: python3" in out
    assert "workspace.py init" in out


def test_no_workspace_beats_bad_input(tmp_path, monkeypatch, capsys):
    monkeypatch.setenv("JOB_HUNT_DIR", str(tmp_path / "missing"))
    code, out = run(capsys, "set", "--company", "Apex", "--stage", "ghosted", "--due", "nope")
    assert code == 0, out
    assert "No workspace found — run: python3" in out


def test_cli_runs_as_a_subprocess(filled):
    import os
    import subprocess
    # a piped stdout on Windows is cp1252, which has no "→"
    r = subprocess.run([sys.executable, str(SCRIPTS / "tracker.py"), "today", "--today", TODAY],
                       capture_output=True, text=True, encoding="utf-8",
                       env={**os.environ, "JOB_HUNT_DIR": str(filled), "PYTHONIOENCODING": "cp1252"})
    assert r.returncode == 0, r.stderr
    assert "Apex Digital" in r.stdout and "→" in r.stdout


def test_funnel_has_no_unset_bucket_for_rows_never_sent():
    rows = [{"Company": "A", "Role": "R", "Source": "JobStreet", "Channel": "cold", "Stage": "applied"},
            {"Company": "B", "Role": "R", "Source": "", "Channel": "", "Stage": "saved"}]
    f = tracker.funnel(rows)
    assert [b["key"] for b in f["channels"]] == ["cold"]
    assert [b["key"] for b in f["sources"]] == ["JobStreet"]
    assert f["total"]["rows"] == 2
    sent_unset = [dict(rows[1], Stage="applied")]
    assert [b["key"] for b in tracker.funnel(sent_unset)["channels"]] == ["(unset)"]
