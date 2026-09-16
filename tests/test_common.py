import io, json as json_mod, sys, pathlib, os, urllib.error
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


# --- table heading scope --------------------------------------------------

MD2 = ("## Pipeline\n"
       "no table here yet\n"
       "\n"
       "## Offers\n"
       "\n"
       "| Company | Status |\n"
       "|---|---|\n"
       "| Grab | pending |\n")

def test_read_table_heading_scope_does_not_leak_into_next_section():
    assert c.read_table(MD2, "## Pipeline") == ([], [])
    assert c.read_table(MD2, "## Offers") == (["Company", "Status"], [{"Company": "Grab", "Status": "pending"}])

def test_write_table_inserts_under_heading_without_touching_other_sections():
    out = c.write_table(MD2, ["Company", "Role"], [{"Company": "Shopee", "Role": "Data"}], heading="## Pipeline")
    assert "| Shopee | Data |" in out
    # Offers section and its row are untouched.
    assert c.read_table(out, "## Offers") == (["Company", "Status"], [{"Company": "Grab", "Status": "pending"}])
    # New table lands inside the Pipeline section, before the Offers heading.
    assert c.read_table(out, "## Pipeline") == (["Company", "Role"], [{"Company": "Shopee", "Role": "Data"}])
    assert out.index("Shopee") < out.index("## Offers")


# --- escaped pipes in cells -------------------------------------------------

def test_write_then_read_table_round_trips_pipe_in_cell():
    md = "| A | Notes |\n|---|---|\n| x | y |\n"
    cols, rows = c.read_table(md)
    rows.append({"A": "x2", "Notes": "A|B"})
    out = c.write_table(md, cols, rows)
    assert c.read_table(out)[1][1]["Notes"] == "A|B"


# --- http helpers ------------------------------------------------------------

class _FakeResp:
    def __init__(self, status, body):
        self.status = status
        self._body = body
    def read(self):
        return self._body
    def __enter__(self):
        return self
    def __exit__(self, *exc):
        return False

def test_http_get_returns_status_and_body(monkeypatch):
    monkeypatch.setattr(c.time, "sleep", lambda s: None)
    monkeypatch.setattr(c, "_last_call", {})
    monkeypatch.setattr(c.urllib.request, "urlopen", lambda req, timeout=None: _FakeResp(200, b"body"))
    assert c.http_get("http://example.com/x") == (200, b"body")

def test_http_get_returns_http_error_code_and_body(monkeypatch):
    monkeypatch.setattr(c.time, "sleep", lambda s: None)
    monkeypatch.setattr(c, "_last_call", {})
    def raise_it(req, timeout=None):
        raise urllib.error.HTTPError("http://example.com/x", 404, "nf", {}, io.BytesIO(b"missing"))
    monkeypatch.setattr(c.urllib.request, "urlopen", raise_it)
    assert c.http_get("http://example.com/x") == (404, b"missing")

def test_http_get_returns_zero_status_on_url_error(monkeypatch):
    monkeypatch.setattr(c.time, "sleep", lambda s: None)
    monkeypatch.setattr(c, "_last_call", {})
    def raise_it(req, timeout=None):
        raise urllib.error.URLError("boom")
    monkeypatch.setattr(c.urllib.request, "urlopen", raise_it)
    status, body = c.http_get("http://example.com/x")
    assert status == 0
    assert b"boom" in body

def test_http_post_json_sends_content_type_and_json_body(monkeypatch):
    captured = {}
    monkeypatch.setattr(c.time, "sleep", lambda s: None)
    monkeypatch.setattr(c, "_last_call", {})
    def fake_urlopen(req, timeout=None):
        captured["req"] = req
        return _FakeResp(200, b"{}")
    monkeypatch.setattr(c.urllib.request, "urlopen", fake_urlopen)
    status, body = c.http_post_json("http://example.com/x", {"a": 1})
    assert (status, body) == (200, b"{}")
    req = captured["req"]
    assert req.get_header("Content-type") == "application/json"
    assert json_mod.loads(req.data.decode("utf-8")) == {"a": 1}

def test_rate_limit_same_host_sleeps_once(monkeypatch):
    c._last_call.clear()
    calls = []
    monkeypatch.setattr(c.time, "sleep", lambda s: calls.append(s))
    times = iter([100.0, 100.0, 100.05, 100.05])
    monkeypatch.setattr(c.time, "monotonic", lambda: next(times))
    c._rate_limit("http://example.com/a")
    c._rate_limit("http://example.com/b")
    assert len(calls) == 1
    assert calls[0] >= 0

def test_rate_limit_different_hosts_do_not_sleep(monkeypatch):
    c._last_call.clear()
    calls = []
    monkeypatch.setattr(c.time, "sleep", lambda s: calls.append(s))
    times = iter([100.0, 100.0, 100.01, 100.01])
    monkeypatch.setattr(c.time, "monotonic", lambda: next(times))
    c._rate_limit("http://example.com/a")
    c._rate_limit("http://other.com/a")
    assert calls == []
