### Task 4: `_common.py` + `workspace.py` + workspace templates

**Files:**
- Create: `skills/job-hunting/scripts/_common.py`, `skills/job-hunting/scripts/workspace.py`
- Create: `skills/job-hunting/assets/profile-template.md` (from `candidate-profile-template.md`, §9 pipeline and §10 removed → separate files; add §9 "Answers & cadence" pointer), `assets/pipeline-template.md`, `assets/contacts-template.md`, `assets/answers-template.md`
- Delete: `skills/job-hunting/assets/candidate-profile-template.md`
- Test: `tests/test_common.py`, `tests/test_workspace.py`

**Interfaces (Produces):**
```python
# _common.py
def workspace_dir() -> Path                     # JOB_HUNT_DIR → ./job-hunt (if exists) → ~/job-hunt
def slugify(s: str) -> str                      # "Grab — Senior SWE" -> "grab-senior-swe"
def optional_import(name: str)                  # returns module or None
def http_get(url, headers=None, timeout=20) -> tuple[int, bytes]
def http_post_json(url, payload, headers=None, timeout=20) -> tuple[int, bytes]
UA = "job-hunter-skill/6.0 (+https://github.com/cincaoais/job-hunter)"
def read_table(md: str, heading: str | None = None) -> tuple[list[str], list[dict]]   # first table (or the one under heading)
def write_table(md: str, columns: list[str], rows: list[dict], heading: str | None = None) -> str  # replaces that table in place
def today() -> str  # ISO date
```

- [ ] **Step 1: Write failing tests**

`tests/test_common.py`:
```python
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
```

`tests/test_workspace.py`:
```python
import sys, pathlib, subprocess
SCRIPTS = pathlib.Path(__file__).resolve().parents[1] / "skills" / "job-hunting" / "scripts"

def test_init_creates_files(tmp_path):
    r = subprocess.run([sys.executable, str(SCRIPTS / "workspace.py"), "init"], env={"JOB_HUNT_DIR": str(tmp_path), "PATH": ""}, capture_output=True, text=True)
    assert r.returncode == 0, r.stderr
    for f in ["profile.md", "pipeline.md", "contacts.md", "answers.md", "seen-jobs.json"]:
        assert (tmp_path / f).exists()
    for d in ["postings", "resumes", "letters", "dossiers", "reviews"]:
        assert (tmp_path / d).is_dir()

def test_init_is_idempotent(tmp_path):
    env = {"JOB_HUNT_DIR": str(tmp_path), "PATH": ""}
    subprocess.run([sys.executable, str(SCRIPTS / "workspace.py"), "init"], env=env, check=True)
    (tmp_path / "profile.md").write_text("mine", encoding="utf-8")
    subprocess.run([sys.executable, str(SCRIPTS / "workspace.py"), "init"], env=env, check=True)
    assert (tmp_path / "profile.md").read_text(encoding="utf-8") == "mine"
```

- [ ] **Step 2: Run to verify failure** — `python3 -m pytest tests/test_common.py tests/test_workspace.py -q` → ImportError / FileNotFoundError.

- [ ] **Step 3: Implement `_common.py`**

Key implementation notes (write the full module):
- `read_table`: scan lines; a table starts at a line beginning with `|` whose next line matches `^\|?\s*:?-{3,}`; if `heading` given, only look after the first line equal to that heading. Split cells on `|`, strip, ignore leading/trailing empties. Return `(columns, rows)`; rows are dicts keyed by column (missing → "").
- `write_table`: locate the same table span (start line index → last consecutive `|` line) and replace it with a rendered table (`| a | b |` rows, header separator `|---|---|`). Cells: replace `|` with `\|` and newlines with space. If no table exists and `heading` is given, append `\n## {heading}\n\n<table>\n` at end.
- `http_get`/`http_post_json`: `urllib.request` with UA header default, return `(status, body)`; on `HTTPError` return `(e.code, e.read())`; on `URLError` return `(0, str(e).encode())`. Add module-level `_last_call: dict[str, float]` and sleep so each host gets ≤ 1 req/s.
- `optional_import`: `importlib.import_module` in try/except → `None`.

- [ ] **Step 4: Implement `workspace.py`**

```python
#!/usr/bin/env python3
"""Create or locate the job-hunt workspace.
  python3 workspace.py init   # create ~/job-hunt (or $JOB_HUNT_DIR) from templates, never overwrites
  python3 workspace.py where  # print the resolved path
"""
import json, shutil, sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent))
from _common import workspace_dir
ASSETS = Path(__file__).resolve().parents[1] / "assets"
FILES = {"profile.md": "profile-template.md", "pipeline.md": "pipeline-template.md",
         "contacts.md": "contacts-template.md", "answers.md": "answers-template.md"}
DIRS = ["postings", "resumes", "letters", "dossiers", "reviews"]

def init(ws: Path) -> list[str]:
    created = []
    ws.mkdir(parents=True, exist_ok=True)
    for name, tpl in FILES.items():
        if not (ws / name).exists():
            shutil.copyfile(ASSETS / tpl, ws / name); created.append(name)
    if not (ws / "seen-jobs.json").exists():
        (ws / "seen-jobs.json").write_text("{}", encoding="utf-8"); created.append("seen-jobs.json")
    for d in DIRS:
        if not (ws / d).exists():
            (ws / d).mkdir(); created.append(d + "/")
    return created

def main(argv):
    cmd = argv[0] if argv else "where"
    ws = workspace_dir()
    if cmd == "init":
        created = init(ws)
        print(f"Workspace: {ws}\nCreated: {', '.join(created) or 'nothing (already initialized)'}")
    elif cmd == "where":
        print(ws)
    else:
        print(__doc__); return 2
    return 0

if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
```

- [ ] **Step 5: Write the four templates**

`pipeline-template.md`:
```markdown
# Pipeline

> One row per company+role. Stages: saved · applied · screen · interview · final · offer · accepted · rejected · withdrawn · cold.
> Source = where the posting came from (JobStreet, MCF, LinkedIn, career page, agency, referral). Channel = cold / referral / recruiter-inbound / agency.
> Dates are YYYY-MM-DD. `Due` drives the today view. Never put `|` in a cell.

_Last weekly review: —_

| Company | Role | Source | Channel | Applied | Stage | Next action | Due | Last touch | Resume | Notes |
|---|---|---|---|---|---|---|---|---|---|---|

## Offers

| Company | Role | Base / month | Bonus (contractual?) | True annual comp | Probation / notice | Deadline | Status |
|---|---|---|---|---|---|---|---|
```

`contacts-template.md`:
```markdown
# Contacts

> Networking CRM. Relationship: alumni / ex-colleague / recruiter / hiring-manager / peer / 2nd-degree. Touches: c = comment, k = connect, m = message, f = follow-up.

| Name | Company | Role | Relationship | Target role | Last touch | Next touch | Status | Notes |
|---|---|---|---|---|---|---|---|---|
```

`answers-template.md`: sections with blank truthful answers for: expected salary (per market, single number + range), notice period / earliest start, work authorization per country, why this company (pattern, filled per posting), why leaving, relocation, years-in-tool table, three STAR stories (title + one line), references (name, relationship, permission asked Y/N).

`profile-template.md`: today's §1–§8 and §11 verbatim, renumbered; §9 becomes "See pipeline.md / contacts.md / answers.md (workspace) — or the sections below in chat mode" followed by the three tables copied so chat mode still has them in one file.

- [ ] **Step 6: Run tests, commit**

Run: `python3 -m pytest tests/test_common.py tests/test_workspace.py -q` → all pass.

```bash
git add skills/job-hunting/scripts skills/job-hunting/assets tests
git commit -m "workspace: ~/job-hunt layout, templates, markdown-table helpers

Co-Authored-By: Claude Fable 5.1 <noreply@anthropic.com>"
```

