"""Tests for fetch_posting.py.

Nothing here touches the network: the board path is exercised through the
sources' injectable `fetch`, the generic path through an injected `get`, and
the stealth-browser path through a fake `cloakbrowser` module.
"""
import pathlib
import sys

import pytest

ROOT = pathlib.Path(__file__).resolve().parents[1]
SCRIPTS = ROOT / "skills" / "job-hunting" / "scripts"
FIXTURES = pathlib.Path(__file__).resolve().parent / "fixtures" / "recorded"
sys.path.insert(0, str(SCRIPTS))

import fetch_posting as fp  # noqa: E402

MCF_UUID = "74c51e4e07647ca4c27451ce89742e14"


def fx(name: str) -> bytes:
    return (FIXTURES / name).read_bytes()


def getter(status=200, body=b"", record=None):
    """An injectable http_get replacement that always answers (status, body)."""

    def get(url, headers=None, timeout=20):
        if record is not None:
            record.append({"url": url, "headers": headers})
        return status, body

    return get


# --- classify ----------------------------------------------------------------

CLASSIFY_CASES = [
    ("jobstreet-my", "https://my.jobstreet.com/job/94655291",
     ("jobstreet", "94655291", "MY")),
    ("jobstreet-sg", "https://sg.jobstreet.com/job/12345678?type=standout",
     ("jobstreet", "12345678", "SG")),
    ("linkedin-slug",
     "https://my.linkedin.com/jobs/view/senior-software-engineer-at-grab-4455634411",
     ("linkedin", "4455634411", "MY")),
    ("linkedin-bare", "https://www.linkedin.com/jobs/view/4455634411",
     ("linkedin", "4455634411", "")),
    ("mcf", f"https://www.mycareersfuture.gov.sg/job/information-technology/"
            f"software-engineer-creative-labs-{MCF_UUID}",
     ("mcf", MCF_UUID, "SG")),
    ("generic-lever", "https://jobs.lever.co/acme/4567890",
     ("generic", "https://jobs.lever.co/acme/4567890", "")),
    ("generic", "https://boards.greenhouse.io/acme/jobs/4567890",
     ("generic", "https://boards.greenhouse.io/acme/jobs/4567890", "")),
]


@pytest.mark.parametrize(
    "url,expected", [c[1:] for c in CLASSIFY_CASES], ids=[c[0] for c in CLASSIFY_CASES]
)
def test_classify(url, expected):
    assert fp.classify(url) == expected


@pytest.mark.parametrize("url,country", [
    ("https://www.jobstreet.com.sg/en/job/12345678", "SG"),
    ("https://jobstreet.com.sg/job/12345678", "SG"),
    ("https://www.jobstreet.com.my/en/job/12345678", "MY"),
    ("https://jobstreet.com.my/job/12345678", "MY"),
])
def test_classify_jobstreet_country_domains(url, country):
    assert fp.classify(url) == ("jobstreet", "12345678", country)


def test_classify_bare_numeric_id_is_jobstreet_my():
    assert fp.classify("94655291") == ("jobstreet", "94655291", "MY")


def test_classify_bare_32_hex_is_mcf_sg():
    assert fp.classify(MCF_UUID) == ("mcf", MCF_UUID, "SG")


def test_classify_bare_junk_is_generic():
    assert fp.classify("what even is this") == ("generic", "what even is this", "")


# --- generic_extract ---------------------------------------------------------

PAGE = """<html><head><title>Senior Backend Engineer &amp; Lead - Acme</title>
<script>var tracker = 1;</script><style>body{color:red}</style></head>
<body>
<header><h1>Acme Careers</h1><nav>Home | Jobs | Contact</nav></header>
<div>Share this job on social</div>
<main><h2>Senior Backend Engineer</h2><p>We need someone who:</p>
<ul><li>Writes Python</li><li>Likes tests</li></ul>
<p>You will own the billing service end to end, from the schema to the on-call
rotation, and you will be the person other teams ask before they change it.
We ship small and often; nothing waits three weeks for a release train.</p></main>
<footer>Copyright Acme. Cookie policy.</footer>
</body></html>"""


def test_generic_extract_takes_title_and_main_block():
    got = fp.generic_extract(PAGE)
    assert got["title"] == "Senior Backend Engineer & Lead - Acme"
    assert "- Writes Python" in got["text"]
    assert "We need someone who:" in got["text"]
    for junk in ("var tracker", "color:red", "Home | Jobs", "Cookie policy", "Share this job"):
        assert junk not in got["text"]


def test_generic_extract_prefers_the_largest_block():
    html = ("<title>T</title><article>tiny</article>"
            "<article>" + ("the real description is long. " * 20) + "</article>")
    got = fp.generic_extract(html)
    assert "the real description is long." in got["text"]
    assert got["text"].strip() != "tiny"


def test_generic_extract_falls_back_to_body_without_main():
    html = ("<html><head><title>Role at Foo</title><script>x</script></head>"
            "<body><p>Plain page description.</p><footer>fine print</footer></body></html>")
    got = fp.generic_extract(html)
    assert got["title"] == "Role at Foo"
    assert "Plain page description." in got["text"]
    assert "fine print" not in got["text"]
    assert "Role at Foo" not in got["text"]


def test_generic_extract_on_junk_returns_empty_strings():
    for raw in ("", "not html at all", "<html></html>"):
        got = fp.generic_extract(raw)
        assert set(got) == {"title", "text"}
        assert isinstance(got["title"], str) and isinstance(got["text"], str)


# --- render_posting ----------------------------------------------------------

JOB = {
    "source": "jobstreet",
    "url": "https://my.jobstreet.com/job/94655291",
    "company": "Electronic Arts",
    "title": "Lead Product Designer",
    "location": "Kuala Lumpur",
    "salary": "RM 10,000 - RM 12,000 per month",
    "posted": "2026-09-20",
    "fetched": "2026-09-22",
    "screening_questions": ["Do you have a work permit?", "Notice period: how long?"],
    "description_md": "About the role\n- design things",
}


def _frontmatter(md: str) -> list[str]:
    assert md.startswith("---\n")
    block = md.split("---\n", 2)[1]
    return [line for line in block.splitlines() if line and not line.startswith(" ")]


def test_render_posting_frontmatter_keys_in_order():
    md = fp.render_posting(JOB)
    keys = [line.split(":", 1)[0] for line in _frontmatter(md)]
    assert keys == list(fp.FRONTMATTER_KEYS)


def test_render_posting_body_and_values():
    md = fp.render_posting(JOB)
    assert "source: jobstreet" in md
    assert "url: https://my.jobstreet.com/job/94655291" not in md  # a URL has a colon
    assert 'url: "https://my.jobstreet.com/job/94655291"' in md
    assert "company: Electronic Arts" in md
    assert "fetched: 2026-09-22" in md
    assert "screening_questions:\n  - Do you have a work permit?\n" in md
    assert '  - "Notice period: how long?"' in md
    assert md.count("---\n") == 2
    assert "## Description\n\nAbout the role\n- design things\n" in md
    assert md.endswith("\n")


def test_render_posting_defaults_missing_fields():
    md = fp.render_posting({"source": "pasted", "description_md": "text"})
    assert "screening_questions: []" in md
    assert "location:\n" in md
    assert f"fetched: {fp.today()}" in md


def test_render_posting_accepts_salary_label_and_text_aliases():
    md = fp.render_posting({"source": "generic", "salary_label": "SGD 8k", "text": "pasted body"})
    assert "salary: SGD 8k" in md
    assert "pasted body" in md


# --- save --------------------------------------------------------------------

@pytest.fixture()
def ws(tmp_path, monkeypatch):
    monkeypatch.setenv("JOB_HUNT_DIR", str(tmp_path))
    return tmp_path


def test_save_writes_company_title_slug(ws):
    path = fp.save(JOB)
    assert path == ws / "postings" / "electronic-arts-lead-product-designer.md"
    assert path.read_text(encoding="utf-8") == fp.render_posting(JOB)
    assert "\r" not in path.read_bytes().decode("utf-8")


def test_save_overwrites_the_same_url(ws):
    first = fp.save(JOB)
    again = fp.save({**JOB, "description_md": "updated body"})
    assert again == first
    assert "updated body" in again.read_text(encoding="utf-8")
    assert len(list((ws / "postings").glob("*.md"))) == 1


def test_save_suffixes_a_different_url(ws):
    first = fp.save(JOB)
    second = fp.save({**JOB, "url": "https://my.jobstreet.com/job/99999999"})
    third = fp.save({**JOB, "url": "https://my.jobstreet.com/job/77777777"})
    assert second.name == "electronic-arts-lead-product-designer-2.md"
    assert third.name == "electronic-arts-lead-product-designer-3.md"
    assert first.name == "electronic-arts-lead-product-designer.md"


def test_save_falls_back_when_company_and_title_are_empty(ws):
    path = fp.save({"source": "pasted", "description_md": "body"})
    assert path.parent == ws / "postings"
    assert path.suffix == ".md" and path.stem


# --- board routing -----------------------------------------------------------

def test_jobstreet_url_routes_to_the_jobstreet_detail_api():
    calls = []

    def detail_fetch(url, headers=None, method="GET", payload=None):
        calls.append({"url": url, "method": method, "payload": payload})
        return 200, fx("jobstreet_detail.json")

    job, reason = fp.fetch("https://my.jobstreet.com/job/94655291", detail_fetch=detail_fetch)
    assert reason == ""
    assert job["source"] == "jobstreet"
    assert job["title"] == "Lead Product Designer"
    assert job["company"] == "Electronic Arts"
    assert job["url"] == "https://my.jobstreet.com/job/94655291"
    assert job["screening_questions"] == []
    assert len(job["description_md"]) > 200
    assert len(calls) == 1
    assert calls[0]["url"] == "https://my.jobstreet.com/graphql"
    assert calls[0]["payload"]["variables"]["jobId"] == "94655291"
    assert calls[0]["payload"]["variables"]["zone"] == "asia-4"


def test_mcf_uuid_routes_to_the_mcf_detail_api():
    calls = []

    def detail_fetch(url, headers=None, method="GET", payload=None):
        calls.append(url)
        return 200, fx("mcf_detail.json")

    job, reason = fp.fetch(MCF_UUID, detail_fetch=detail_fetch)
    assert reason == ""
    assert job["source"] == "mcf"
    assert job["title"] == "Software Engineer"
    assert calls and calls[0].endswith(f"/jobs/{MCF_UUID}")


def test_board_detail_miss_is_not_found():
    def detail_fetch(url, headers=None, method="GET", payload=None):
        return 404, b"{}"

    job, reason = fp.fetch("https://my.jobstreet.com/job/1", detail_fetch=detail_fetch)
    assert job is None
    assert reason.startswith("not found")


def test_board_detail_404_is_not_found():
    def detail_fetch(url, headers=None, method="GET", payload=None):
        return 404, b"{}"

    job, reason = fp.fetch_board("jobstreet", "1", "MY", detail_fetch=detail_fetch)
    assert job is None
    assert reason.startswith("not found:")


def test_board_detail_warning_is_unavailable():
    def detail_fetch(url, headers=None, method="GET", payload=None):
        return 500, b"{}"

    job, reason = fp.fetch_board("jobstreet", "1", "MY", detail_fetch=detail_fetch)
    assert job is None
    assert reason.startswith("unavailable:")
    assert "HTTP 500" in reason


def test_board_detail_exception_is_unavailable():
    def detail_fetch(url, headers=None, method="GET", payload=None):
        raise RuntimeError("connection reset")

    job, reason = fp.fetch_board("jobstreet", "1", "MY", detail_fetch=detail_fetch)
    assert job is None
    assert reason.startswith("unavailable:")


def test_board_detail_empty_without_warnings_is_not_found():
    def detail_fetch(url, headers=None, method="GET", payload=None):
        return 200, b"{}"

    job, reason = fp.fetch_board("jobstreet", "1", "MY", detail_fetch=detail_fetch)
    assert job is None
    assert reason.startswith("not found:")


def test_main_exit_4_when_the_board_has_no_such_job(monkeypatch, capsys):
    monkeypatch.setattr(fp, "http_get", getter(404, b"{}"))
    monkeypatch.setattr(fp, "default_fetch", lambda *a, **k: (404, b"{}"))
    assert fp.main(["https://my.jobstreet.com/job/1"]) == 4
    assert "not found" in capsys.readouterr().err.lower()


# --- generic fetch, blocking and the browser fallback ------------------------

def test_generic_retries_once_with_a_browser_user_agent():
    calls = []

    def get(url, headers=None, timeout=20):
        calls.append(headers)
        if len(calls) == 1:
            return 403, b"forbidden"
        return 200, PAGE.encode()

    job, reason = fp.fetch("https://jobs.example.com/roles/7", get=get)
    assert reason == ""
    assert len(calls) == 2
    assert calls[0] is None or "Mozilla" not in str(calls[0])
    assert "Mozilla" in calls[1]["User-Agent"]
    assert job["source"] == "generic"
    assert job["title"] == "Senior Backend Engineer & Lead - Acme"
    assert "- Writes Python" in job["description_md"]
    assert job["url"] == "https://jobs.example.com/roles/7"


BLOCK_BODIES = [
    (403, b"<html><body>Forbidden</body></html>"),
    (503, b"<html><body>error</body></html>"),
    (429, b"slow down"),
    (200, b"<html><head><title>Just a moment...</title></head><body>cf-chl</body></html>"),
    (200, b"<html><body><div id='challenge-platform'>x</div></body></html>"),
    (200, b"<html><body>Prove your humanity</body></html>"),
    (200, b"<html><body>Access Denied</body></html>"),
]


@pytest.mark.parametrize("status,body", BLOCK_BODIES)
def test_looks_blocked(status, body):
    assert fp.looks_blocked(status, body) is True


def test_looks_blocked_is_false_for_a_normal_page():
    assert fp.looks_blocked(200, PAGE.encode()) is False


def test_main_exits_3_when_blocked_without_cloakbrowser(monkeypatch, capsys):
    monkeypatch.setattr(fp, "optional_import", lambda name: None)
    monkeypatch.setattr(fp, "http_get", getter(403, b"<html><body>Forbidden</body></html>"))
    assert fp.main(["https://jobs.example.com/roles/7"]) == 3
    err = capsys.readouterr().err
    assert "blocked; paste the posting text instead (or pip install cloakbrowser)" in err


BROWSER_JD = ("Real description from the browser. You will own the billing service end "
              "to end, from the schema to the on-call rotation, and you will be the person "
              "other teams ask before they change it. Go, Postgres, Kafka; hybrid in KL.")


class FakePage:
    def __init__(self, text=BROWSER_JD, title="Role at Acme"):
        self.text, self.title, self.goto_args = text, title, None
        self.closed = False
        self.waits = []

    def goto(self, url, wait_until=None, timeout=None):
        self.goto_args = {"url": url, "wait_until": wait_until, "timeout": timeout}

    def evaluate(self, script):
        return self.title if "title" in script else self.text

    def wait_for_load_state(self, state, timeout=None):
        self.waits.append(("load_state", state))

    def wait_for_timeout(self, ms):
        self.waits.append(("timeout", ms))

    def close(self):
        self.closed = True


class FakeCloak:
    def __init__(self, page=None, boom=False):
        self.page, self.boom, self.launch_kwargs = page or FakePage(), boom, None

    def launch(self, **kwargs):
        self.launch_kwargs = kwargs
        if self.boom:
            raise RuntimeError("no browser binary")
        return self.page


def test_blocked_page_falls_back_to_the_stealth_browser(monkeypatch):
    cloak = FakeCloak()
    monkeypatch.setattr(fp, "optional_import", lambda name: cloak)
    monkeypatch.setattr(fp, "http_get", getter(403, b"<html><body>Forbidden</body></html>"))
    job, reason = fp.fetch("https://jobs.example.com/roles/7")
    assert reason == ""
    assert job["description_md"] == BROWSER_JD
    assert job["title"] == "Role at Acme"
    assert cloak.launch_kwargs == {"headless": True}
    assert cloak.page.goto_args == {"url": "https://jobs.example.com/roles/7",
                                    "wait_until": "domcontentloaded", "timeout": 45000}
    assert cloak.page.closed is True


def test_a_browser_failure_counts_as_blocked(monkeypatch):
    monkeypatch.setattr(fp, "optional_import", lambda name: FakeCloak(boom=True))
    monkeypatch.setattr(fp, "http_get", getter(403, b"nope"))
    job, reason = fp.fetch("https://jobs.example.com/roles/7")
    assert job is None
    assert reason == "blocked"


def test_network_failure_is_reported_not_raised(monkeypatch, capsys):
    monkeypatch.setattr(fp, "http_get", getter(0, b"<urlopen error timed out>"))
    assert fp.main(["https://jobs.example.com/roles/7"]) == 4
    assert capsys.readouterr().err.strip()


# --- CLI ---------------------------------------------------------------------

def test_main_prints_markdown_by_default(monkeypatch, capsys):
    monkeypatch.setattr(fp, "http_get", getter(200, PAGE.encode()))
    assert fp.main(["https://jobs.example.com/roles/7"]) == 0
    out = capsys.readouterr().out
    assert out.startswith("---\n")
    assert "## Description" in out


def test_main_save_writes_the_file(ws, monkeypatch, capsys):
    monkeypatch.setattr(fp, "http_get", getter(200, PAGE.encode()))
    assert fp.main(["https://jobs.example.com/roles/7", "--save", "--company", "Acme"]) == 0
    files = list((ws / "postings").glob("*.md"))
    assert len(files) == 1
    body = files[0].read_text(encoding="utf-8")
    assert "company: Acme" in body
    assert "- Writes Python" in body
    assert str(files[0]) in capsys.readouterr().out


def test_main_stdin_makes_a_pasted_posting(ws, monkeypatch, capsys):
    monkeypatch.setattr("sys.stdin", __import__("io").StringIO("Pasted JD body\n- one bullet\n"))
    code = fp.main(["--stdin", "--company", "Acme", "--title", "Backend Engineer", "--save"])
    assert code == 0
    path = ws / "postings" / "acme-backend-engineer.md"
    body = path.read_text(encoding="utf-8")
    assert "source: pasted" in body
    assert "Pasted JD body" in body
    assert str(path) in capsys.readouterr().out


def test_main_without_a_target_is_a_usage_error(capsys):
    assert fp.main([]) == 2
    assert capsys.readouterr().err.strip()


def test_main_rejects_an_empty_stdin(monkeypatch, capsys):
    monkeypatch.setattr("sys.stdin", __import__("io").StringIO("   \n"))
    assert fp.main(["--stdin"]) == 2
    assert capsys.readouterr().err.strip()


def test_browser_chatter_stays_off_stdout(monkeypatch, capsys):
    class Noisy(FakeCloak):
        def launch(self, **kwargs):
            print("CloakBrowser - stealth Chromium banner")
            return super().launch(**kwargs)

    monkeypatch.setattr(fp, "optional_import", lambda name: Noisy())
    monkeypatch.setattr(fp, "http_get", getter(403, b"nope"))
    assert fp.main(["https://jobs.example.com/roles/7"]) == 0
    captured = capsys.readouterr()
    assert captured.out.startswith("---\n")
    assert "banner" not in captured.out
    assert "banner" in captured.err


THIN_PAGE = (b"<html><head><title>Careers at Acme</title></head>"
             b"<body><div id='root'></div></body></html>")


def test_a_javascript_only_page_falls_back_to_the_browser(monkeypatch):
    rendered = "The whole job description, rendered by the browser. " * 5
    cloak = FakeCloak(FakePage(text=rendered.strip()))
    monkeypatch.setattr(fp, "optional_import", lambda name: cloak)
    monkeypatch.setattr(fp, "http_get", getter(200, THIN_PAGE))
    job, reason = fp.fetch("https://jobs.example.com/roles/7")
    assert reason == ""
    assert job["description_md"] == rendered.strip()
    assert cloak.page.goto_args["url"] == "https://jobs.example.com/roles/7"


def test_an_empty_page_without_a_browser_is_not_found(monkeypatch, capsys):
    monkeypatch.setattr(fp, "optional_import", lambda name: None)
    monkeypatch.setattr(fp, "http_get", getter(200, THIN_PAGE))
    assert fp.main(["https://jobs.example.com/roles/7"]) == 4
    assert "no posting text" in capsys.readouterr().err


def test_a_full_page_never_starts_the_browser(monkeypatch):
    def boom(name):
        raise AssertionError("the browser must not be used for a page that parsed")

    monkeypatch.setattr(fp, "optional_import", boom)
    monkeypatch.setattr(fp, "http_get", getter(200, PAGE.encode()))
    job, reason = fp.fetch("https://jobs.example.com/roles/7")
    assert reason == "" and len(job["description_md"]) > fp.MIN_GENERIC_TEXT


class LazyPage(FakePage):
    """An app shell: innerText is empty until the page has settled.

    `waiter` names the only wait call this page supports; the other one
    raises, the way a simpler page object would.
    """

    def __init__(self, waiter="wait_for_load_state"):
        super().__init__(text="Rendered after hydration. " * 12)
        self.settled = False
        self.waiter = waiter

    def evaluate(self, script):
        if "title" in script:
            return self.title
        return self.text if self.settled else ""

    def _wait(self, name):
        if name != self.waiter:
            raise RuntimeError(f"{name} is not supported by this page")
        self.settled = True

    def wait_for_load_state(self, state, timeout=None):
        self._wait("wait_for_load_state")

    def wait_for_timeout(self, ms):
        self._wait("wait_for_timeout")


@pytest.mark.parametrize("waiter", ["wait_for_load_state", "wait_for_timeout"])
def test_browser_waits_for_a_single_page_app_to_paint(monkeypatch, waiter):
    page = LazyPage(waiter)
    monkeypatch.setattr(fp, "optional_import", lambda name: FakeCloak(page))
    monkeypatch.setattr(fp, "http_get", getter(200, THIN_PAGE))
    job, reason = fp.fetch("https://jobs.example.com/roles/7")
    assert reason == ""
    assert page.settled is True
    assert "Rendered after hydration." in job["description_md"]


def test_settle_sleeps_when_the_page_cannot_wait(monkeypatch):
    slept = []
    monkeypatch.setattr(fp.time, "sleep", lambda s: slept.append(s))
    fp._settle(object())
    assert slept == [fp.SETTLE_MS / 1000]


# --- fix round 1 -------------------------------------------------------------

FORM_WRAPPED = (
    "<html><head><title>Staff Engineer at Workday Inc</title></head><body><form>"
    "<main><h2>Staff Engineer</h2>"
    + "<p>You will own the ledger service and the people who depend on it.</p>" * 15
    + "<label>Resume/CV</label><button>Apply</button><select><option>Yes</option></select>"
    "</main></form></body></html>")


def test_generic_extract_keeps_a_form_wrapped_description(monkeypatch):
    """Workday/Lever/SmartRecruiters nest the JD inside the apply <form>."""
    def boom(name):
        raise AssertionError("a form-wrapped page must not need the browser")

    monkeypatch.setattr(fp, "optional_import", boom)
    got = fp.generic_extract(FORM_WRAPPED)
    assert got["title"] == "Staff Engineer at Workday Inc"
    assert "You will own the ledger service" in got["text"]
    assert len(got["text"]) > fp.MIN_GENERIC_TEXT
    for chrome in ("Resume/CV", "Apply", "Yes"):
        assert chrome not in got["text"]

    monkeypatch.setattr(fp, "http_get", getter(200, FORM_WRAPPED.encode()))
    job, reason = fp.fetch("https://acme.wd5.myworkdayjobs.com/en-US/acme/job/7")
    assert reason == "" and "ledger service" in job["description_md"]


def test_a_200_page_that_says_access_denied_is_still_parsed(monkeypatch):
    def boom(name):
        raise AssertionError("a page that parsed must not start the browser")

    monkeypatch.setattr(fp, "optional_import", boom)
    page = ("<html><head><title>Security Engineer</title></head><body><main>"
            "<p>You will write the Access Denied rules for our WAF and own the "
            "challenge-platform integration end to end, with real production "
            "traffic behind it from your first week on the team. You will also "
            "run the quarterly red-team exercise, review every rule change that "
            "touches the edge, and mentor two engineers who are new to the "
            "security side of the stack.</p></main></body></html>")
    assert fp.looks_blocked(200, page) is True  # the words are in the JD
    monkeypatch.setattr(fp, "http_get", getter(200, page.encode()))
    job, reason = fp.fetch("https://acme.com/jobs/security-engineer")
    assert reason == ""
    assert "Access Denied rules" in job["description_md"]


def test_a_short_challenge_page_is_never_a_posting(monkeypatch):
    challenge = (b"<html><head><title>Just a moment...</title></head>"
                 b"<body><p>Checking your browser before accessing the site.</p>"
                 b"</body></html>")
    monkeypatch.setattr(fp, "browse", lambda url, **kwargs: None)
    monkeypatch.setattr(fp, "http_get", getter(200, challenge))
    assert fp.looks_blocked(200, challenge) is True
    job, reason = fp.fetch("https://jobs.example.com/roles/7")
    assert job is None
    assert reason == "blocked"


def test_classify_lowercases_an_uppercase_mcf_uuid():
    upper = MCF_UUID.upper()
    assert fp.classify(upper) == ("mcf", MCF_UUID, "SG")
    assert fp.classify(f"https://www.mycareersfuture.gov.sg/job/it/dev-{upper}") == (
        "mcf", MCF_UUID, "SG")


@pytest.mark.parametrize("value", ["No", "yes", "TRUE", "off", "null", "~", "y"])
def test_scalar_quotes_yaml_reserved_words(value):
    assert fp._scalar(value) == f'"{value}"'


def test_scalar_quotes_a_leading_question_mark():
    assert fp._scalar("? maybe") == '"? maybe"'


def test_board_location_salary_and_posted_reach_the_frontmatter():
    def detail_fetch(url, headers=None, method="GET", payload=None):
        return 200, fx("mcf_detail.json")

    job, reason = fp.fetch(MCF_UUID, detail_fetch=detail_fetch)
    assert reason == ""
    assert job["location"] == "D05 Pasir Panjang, Hong Leong Garden, Clementi New Town"
    assert job["posted"] == "2026-09-16"
    md = fp.render_posting(job)
    assert '\nlocation: "D05 Pasir Panjang, Hong Leong Garden, Clementi New Town"\n' in md
    assert "\nsalary: SGD 4,000 - 6,500 per month\n" not in md  # it has a comma
    assert '\nsalary: "SGD 4,000 - 6,500 per month"\n' in md
    assert "\nposted: 2026-09-16\n" in md


def test_jobstreet_location_and_posted_reach_the_frontmatter():
    def detail_fetch(url, headers=None, method="GET", payload=None):
        return 200, fx("jobstreet_detail.json")

    job, _ = fp.fetch("https://my.jobstreet.com/job/94655291", detail_fetch=detail_fetch)
    md = fp.render_posting(job)
    assert '\nlocation: "Kuala Lumpur City Centre, Kuala Lumpur"\n' in md
    assert "\nposted: 2026-09-15\n" in md
    assert "\nsalary:\n" in md  # this advertiser published none


# --- final review: a still-blocked browser page is never a posting ------------

GLASSDOOR_WALL = (
    "Help Us Protect Glassdoor\n"
    "Humans only. We have received a high volume of requests from your network. "
    "Please verify you are a human to continue using Glassdoor, the site where "
    "people share salaries, interviews and reviews of their employers.\n"
    "Your IP address: 203.0.113.42\nRay ID: 8c1f2e3d4a5b6c7d")


def test_main_exits_3_and_saves_nothing_when_the_browser_is_walled(ws, monkeypatch, capsys):
    page = FakePage(text=GLASSDOOR_WALL, title="Security | Glassdoor")
    monkeypatch.setattr(fp, "optional_import", lambda name: FakeCloak(page))
    monkeypatch.setattr(fp, "http_get", getter(403, b"<html><body>Forbidden</body></html>"))
    url = "https://www.glassdoor.com/job-listing/backend-engineer-acme-JV_IC123.htm"
    assert fp.main([url, "--save"]) == 3
    captured = capsys.readouterr()
    assert fp.BLOCKED_MSG in captured.err
    assert "203.0.113.42" not in captured.out + captured.err
    assert not list(ws.rglob("postings/*"))


LATE_MENTION = BROWSER_JD + " " + "Own IAM policy reviews. " * 100 + "Triage access denied alerts."


@pytest.mark.parametrize("text,title,blocked", [
    ("Just a moment...", "Checking your browser", True),
    ("Are you a robot? Tick the box to continue. " * 6, "", True),
    ("Loading", "Careers at Acme", True),
    (BROWSER_JD, "Role at Acme", False),
    (LATE_MENTION, "Security Engineer at Acme", False),
], ids=["cloudflare", "robot-check", "thin-shell", "posting", "late-access-denied"])
def test_is_browser_blocked(text, title, blocked):
    assert fp.is_browser_blocked({"text": text, "title": title}) is blocked
