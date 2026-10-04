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
