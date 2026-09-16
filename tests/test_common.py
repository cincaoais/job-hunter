import sys, pathlib, os
SCRIPTS = pathlib.Path(__file__).resolve().parents[1] / "skills" / "job-hunting" / "scripts"
sys.path.insert(0, str(SCRIPTS))
import _common as c

MD = """# Pipeline

| Company | Role | Stage |
|---|---|---|
| Grab | SWE | applied |
| GX Bank | Backend | screen |

## Notes
text
"""

def test_read_table_returns_columns_and_rows():
    cols, rows = c.read_table(MD)
    assert cols == ["Company", "Role", "Stage"]
    assert rows[1] == {"Company": "GX Bank", "Role": "Backend", "Stage": "screen"}

def test_write_table_roundtrip_preserves_surroundings():
    cols, rows = c.read_table(MD)
    rows.append({"Company": "Shopee", "Role": "Data", "Stage": "saved"})
    out = c.write_table(MD, cols, rows)
    assert "| Shopee | Data | saved |" in out and out.startswith("# Pipeline") and out.rstrip().endswith("text")
    assert c.read_table(out)[1][2]["Company"] == "Shopee"

def test_slugify():
    assert c.slugify("Grab — Senior SWE (Payments)") == "grab-senior-swe-payments"

def test_workspace_dir_env_wins(tmp_path, monkeypatch):
    monkeypatch.setenv("JOB_HUNT_DIR", str(tmp_path))
    assert c.workspace_dir() == tmp_path

def test_workspace_dir_local_folder(tmp_path, monkeypatch):
    monkeypatch.delenv("JOB_HUNT_DIR", raising=False)
    (tmp_path / "job-hunt").mkdir(); monkeypatch.chdir(tmp_path)
    assert c.workspace_dir() == tmp_path / "job-hunt"
