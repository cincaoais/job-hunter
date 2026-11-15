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

def test_workspace_dir_env_expands_a_leading_tilde(tmp_path, monkeypatch):
    monkeypatch.setenv("HOME", str(tmp_path)); monkeypatch.setenv("USERPROFILE", str(tmp_path))
    monkeypatch.setenv("JOB_HUNT_DIR", "~/hunt")
    assert c.workspace_dir() == tmp_path / "hunt"

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


def test_read_table_keeps_raw_pipe_in_last_cell():
    md = "| A | B |\n|---|---|\n| x | note with | pipe |\n"
    cols, rows = c.read_table(md)
    assert cols == ["A", "B"]
    assert rows == [{"A": "x", "B": "note with | pipe"}]


def test_read_write_read_table_round_trips_raw_pipe_in_last_cell():
    md = "| A | B |\n|---|---|\n| x | note with | pipe |\n"
    cols, rows = c.read_table(md)
    out = c.write_table(md, cols, rows)
    assert c.read_table(out)[1][0]["B"] == "note with | pipe"


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
    monkeypatch.setattr(c.urllib.request, "urlopen", lambda req, timeout=None, context=None: _FakeResp(200, b"body"))
    assert c.http_get("http://example.com/x") == (200, b"body")

def test_http_get_returns_http_error_code_and_body(monkeypatch):
    monkeypatch.setattr(c.time, "sleep", lambda s: None)
    monkeypatch.setattr(c, "_last_call", {})
    def raise_it(req, timeout=None, context=None):
        raise urllib.error.HTTPError("http://example.com/x", 404, "nf", {}, io.BytesIO(b"missing"))
    monkeypatch.setattr(c.urllib.request, "urlopen", raise_it)
    assert c.http_get("http://example.com/x") == (404, b"missing")

def test_http_get_returns_zero_status_on_url_error(monkeypatch):
    monkeypatch.setattr(c.time, "sleep", lambda s: None)
    monkeypatch.setattr(c, "_last_call", {})
    def raise_it(req, timeout=None, context=None):
        raise urllib.error.URLError("boom")
    monkeypatch.setattr(c.urllib.request, "urlopen", raise_it)
    status, body = c.http_get("http://example.com/x")
    assert status == 0
    assert b"boom" in body

def test_http_post_json_sends_content_type_and_json_body(monkeypatch):
    captured = {}
    monkeypatch.setattr(c.time, "sleep", lambda s: None)
    monkeypatch.setattr(c, "_last_call", {})
    def fake_urlopen(req, timeout=None, context=None):
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

def test_html_to_text_flattens_lists_breaks_and_entities():
    html = (
        "<h2>About</h2><p>We build <b>things</b>&nbsp;fast.</p>"
        "<ul><li>Ship code</li><li>Own outcomes &amp; results</li></ul>"
        "<div>Line one<br>Line two</div><script>alert('x')</script>"
    )
    out = c.html_to_text(html)
    assert [line for line in out.splitlines() if line] == [
        "About",
        "We build things fast.",
        "- Ship code",
        "- Own outcomes & results",
        "Line one",
        "Line two",
    ]
    assert "<" not in out

def test_html_to_text_collapses_blank_runs_and_handles_empty():
    assert c.html_to_text("<p>a</p><p></p><p></p><p>b</p>") == "a\n\nb"
    assert c.html_to_text("") == ""

def test_job_record_always_carries_every_key():
    rec = c.job_record("jobstreet", "MY", title="Dev")
    assert set(rec) == set(c.JOB_KEYS)
    assert rec["title"] == "Dev" and rec["source"] == "jobstreet" and rec["country"] == "MY"
    assert rec["salary_min"] is None and rec["applicants"] is None and rec["teaser"] == ""

def test_job_record_rejects_unknown_fields():
    try:
        c.job_record("jobstreet", "MY", salaryMin=1)
    except KeyError as e:
        assert "salaryMin" in str(e)
    else:
        raise AssertionError("expected KeyError")

def test_detail_record_defaults():
    rec = c.detail_record(title="Dev")
    assert set(rec) == set(c.DETAIL_KEYS)
    assert rec["screening_questions"] == [] and rec["description_md"] == ""

def test_default_fetch_routes_get_and_post(monkeypatch):
    calls = []
    monkeypatch.setattr(c, "http_get", lambda url, headers=None: calls.append(("GET", url, headers)) or (200, b"g"))
    monkeypatch.setattr(c, "http_post_json", lambda url, payload, headers=None: calls.append(("POST", url, payload)) or (200, b"p"))
    assert c.default_fetch("http://x/1", {"User-Agent": "ua"}) == (200, b"g")
    assert c.default_fetch("http://x/2", None, "POST", {"a": 1}) == (200, b"p")
    assert calls == [("GET", "http://x/1", {"User-Agent": "ua"}), ("POST", "http://x/2", {"a": 1})]

def test_http_get_turns_a_timeout_into_status_zero(monkeypatch):
    monkeypatch.setattr(c.time, "sleep", lambda s: None)
    monkeypatch.setattr(c, "_last_call", {})
    def raise_timeout(req, timeout=None, context=None):
        raise TimeoutError("timed out")
    monkeypatch.setattr(c.urllib.request, "urlopen", raise_timeout)
    status, body = c.http_get("http://example.com/x")
    assert status == 0 and b"timed out" in body

def test_http_post_json_turns_a_dropped_connection_into_status_zero(monkeypatch):
    monkeypatch.setattr(c.time, "sleep", lambda s: None)
    monkeypatch.setattr(c, "_last_call", {})
    def raise_disconnected(req, timeout=None, context=None):
        raise c.http.client.RemoteDisconnected("closed")
    monkeypatch.setattr(c.urllib.request, "urlopen", raise_disconnected)
    assert c.http_post_json("http://example.com/x", {})[0] == 0

def test_ssl_context_verifies():
    ctx = c._ssl_context()
    assert isinstance(ctx, c.ssl.SSLContext)
    assert ctx.verify_mode == c.ssl.CERT_REQUIRED and ctx.check_hostname

def test_ssl_context_without_certifi_still_verifies(monkeypatch):
    monkeypatch.setattr(c, "optional_import", lambda name: None)
    ctx = c._ssl_context()
    assert isinstance(ctx, c.ssl.SSLContext) and ctx.verify_mode == c.ssl.CERT_REQUIRED

def test_first_two_ints():
    assert c.first_two_ints("RM 15,000 - RM 20,000 per month") == (15000, 20000)
    assert c.first_two_ints("5000") == (5000, 5000)
    assert c.first_two_ints("Undisclosed") == (None, None)
    assert c.first_two_ints("") == (None, None)

def test_to_monthly():
    assert c.to_monthly(120000, 120000, "RM 120,000 per year") == (10000, 10000)
    assert c.to_monthly(50, 50, "50 per hour") == (8650, 8650)
    assert c.to_monthly(8000, 12000, "MYR8,000 - MYR12,000 per month") == (8000, 12000)
    assert c.to_monthly(None, None, "") == (None, None)


def test_loads_or_empty_and_shape_guards():
    assert c.loads_or_empty(b'{"a": 1}') == {"a": 1}
    assert c.loads_or_empty("not json") == {}
    assert c.loads_or_empty(b"[1]") == [1]
    assert c.dict_at({"a": {"b": {"c": 1}}}, "a", "b") == {"c": 1}
    assert c.dict_at({"a": "oops"}, "a", "b") == {}
    assert c.dict_at(None) == {}
    assert c.rows_of({"data": [1, 2]}, "data") == [1, 2]
    assert c.rows_of({"data": "oops"}, "data") == []
    assert c.rows_of("oops", "data") == []

def test_finish_detail_drops_empty_records():
    assert c.finish_detail(c.detail_record()) is None
    assert c.finish_detail(c.detail_record(title="Dev"))["title"] == "Dev"
    assert c.finish_detail(c.detail_record(description_md="long text")) is not None


def test_write_text_atomic_writes_and_overwrites(tmp_path):
    path = tmp_path / "nested" / "pipeline.md"
    c.write_text_atomic(path, "# Pipeline\n")
    assert path.read_text(encoding="utf-8") == "# Pipeline\n"
    c.write_text_atomic(path, "# Pipeline\n| A | B |\n")
    assert path.read_text(encoding="utf-8") == "# Pipeline\n| A | B |\n"


def test_write_text_atomic_leaves_no_extra_files(tmp_path):
    path = tmp_path / "pipeline.md"
    c.write_text_atomic(path, "text\n")
    assert sorted(p.name for p in tmp_path.iterdir()) == ["pipeline.md"]


def test_write_text_atomic_uses_lf_newlines(tmp_path):
    path = tmp_path / "review.md"
    c.write_text_atomic(path, "a\nb\n")
    assert path.read_bytes() == b"a\nb\n"
