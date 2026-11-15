"""Tests for search_jobs.py — criteria parsing, knockouts, dedupe, ranking, run().

Nothing here touches the network: `run()` is handed stub modules whose
`search()` returns normalized records built with `_common.job_record`.
"""
import json
import pathlib
import sys

import pytest

ROOT = pathlib.Path(__file__).resolve().parents[1]
SCRIPTS = ROOT / "skills" / "job-hunting" / "scripts"
FIXTURES = pathlib.Path(__file__).resolve().parent / "fixtures"
sys.path.insert(0, str(SCRIPTS))

import search_jobs  # noqa: E402
from _common import job_record  # noqa: E402

SAMPLE_PROFILE = (FIXTURES / "sample-profile.md").read_text(encoding="utf-8")
TEMPLATE_PROFILE = (
    ROOT / "skills" / "job-hunting" / "assets" / "profile-template.md"
).read_text(encoding="utf-8")


def job(**kw):
    """A normalized record with sane defaults, overridable per test."""
    fields = {
        "id": "fake:1", "title": "Backend Engineer", "company": "Acme",
        "location": "Kuala Lumpur", "mode": "Hybrid", "salary_min": 10000,
        "salary_max": 14000, "currency": "MYR", "salary_label": "MYR 10,000 - 14,000",
        "posted": "2026-09-20", "url": "https://example.com/1",
        "teaser": "Go and Python services, hybrid in KL",
    }
    source = kw.pop("source", "fake")
    country = kw.pop("country", "MY")
    fields.update(kw)
    return job_record(source, country, **fields)


class StubSource:
    """Minimal stand-in for a sources.* module."""

    def __init__(self, name, jobs, warnings=(), raises=None):
        self.NAME = name
        self.LAST_WARNINGS = []
        self._jobs = list(jobs)
        self._warnings = list(warnings)
        self._raises = raises
        self.calls = []

    def search(self, keywords, location, *, country, days=None, salary_min=None,
               pages=1, fetch=None):
        self.LAST_WARNINGS.clear()
        self.calls.append({"keywords": keywords, "location": location, "country": country,
                           "days": days, "salary_min": salary_min, "pages": pages})
        if self._raises:
            raise self._raises
        self.LAST_WARNINGS.extend(self._warnings)
        return [dict(j) for j in self._jobs]


# --- read_criteria -----------------------------------------------------------

def test_read_criteria_reads_the_sample_profile():
    c = search_jobs.read_criteria(SAMPLE_PROFILE)
    assert c["keywords"] == [
        "backend engineer", "software engineer (Go)", "senior backend engineer",
    ]
    assert c["country"] == "MY"
    assert c["salary_min"] == 9000
    assert c["location"] == "Kuala Lumpur"
    assert c["boards"] == ["jobstreet", "linkedin"]
    assert "gambling industry" in c["dealbreakers"]
    assert "6-day work week" in c["dealbreakers"]


def test_read_criteria_on_the_unfilled_template_yields_defaults():
    c = search_jobs.read_criteria(TEMPLATE_PROFILE)
    assert c["keywords"] == []
    assert c["dealbreakers"] == []
    assert c["salary_min"] is None
    assert c["boards"] == ["jobstreet", "mcf", "linkedin"]


def test_read_criteria_country_and_board_variants():
    md = "\n".join([
        "- **Job market / country I'm hunting in:** Singapore",
        "- **Location:** Singapore",
        "- **Job boards to search:** MyCareersFuture, Glassdoor, Craigslist",
        "- **Salary expectation:** up to 8 months bonus, SGD 7,500 / month",
    ])
    c = search_jobs.read_criteria(md)
    assert c["country"] == "SG"
    assert c["boards"] == ["mcf"]
    assert c["salary_min"] == 7500


SALARY_CASES = [
    ("monthly range", "RM 9,000–12,000 / month", 9000),
    ("noise first", "up to 8 months bonus, SGD 7,500 / month", 7500),
    ("k suffix", "RM9k/month", 9000),
    ("annual", "RM 120,000 per year", 10000),
    ("annual k", "SGD 96k p.a.", 8000),
    ("annual plus monthly", "RM 120,000 per year (RM 10,000/month)", 10000),
    ("decimal k", "RM 1.5k / month", 1500),
    ("unset", "", None),
]


@pytest.mark.parametrize(
    "value,floor", [c[1:] for c in SALARY_CASES], ids=[c[0] for c in SALARY_CASES]
)
def test_read_criteria_salary_floor(value, floor):
    c = search_jobs.read_criteria(f"- **Salary expectation:** {value}")
    assert c["salary_min"] == floor


def test_salary_floor_prefers_the_monthly_figure_and_reads_decimal_k():
    assert search_jobs._salary_floor("RM 120,000 per year (RM 10,000/month)") == 10000
    assert search_jobs._salary_floor("RM 1.5k / month") == 1500


def test_read_criteria_falls_back_to_first_two_letters():
    c = search_jobs.read_criteria("- **Job market / country I'm hunting in:** Indonesia")
    assert c["country"] == "IN"


# --- knockout ----------------------------------------------------------------

CRITERIA = {
    "salary_min": 9000,
    "dealbreakers": ["6-day work week", "fully onsite", "gambling industry"],
}


KNOCKOUT_CASES = [
    ("clean", {}, None),
    ("gambling company", {"company": "Royal Flush Gambling Sdn Bhd"},
     "dealbreaker: gambling industry"),
    ("gambling teaser", {"teaser": "Go backend for our online gambling platform"},
     "dealbreaker: gambling industry"),
    ("multiword phrase", {"teaser": "Go services; 6-day work week, hybrid after probation"},
     "dealbreaker: 6-day work week"),
    ("absent dealbreaker", {"teaser": "hybrid Python role"}, None),
    ("below floor", {"salary_min": 4000, "salary_max": 6000}, "salary below floor"),
    ("no salary", {"salary_min": None, "salary_max": None}, None),
]


@pytest.mark.parametrize(
    "fields,reason", [c[1:] for c in KNOCKOUT_CASES], ids=[c[0] for c in KNOCKOUT_CASES]
)
def test_knockout(fields, reason):
    assert search_jobs.knockout(job(**fields), CRITERIA) == reason


VARIANT_CASES = [
    ("commission-only kept", "commission-only roles",
     "Base salary plus commission on closed deals", None),
    ("contract work kept", "contract work",
     "Contract negotiation with vendors, permanent headcount", None),
    ("gambling category dropped", "gambling industry",
     "Go backend for our online gambling platform", "dealbreaker: gambling industry"),
    ("full phrase dropped", "commission-only roles",
     "This is a commission-only role, no base", "dealbreaker: commission-only roles"),
]


@pytest.mark.parametrize(
    "phrase,teaser,reason", [c[1:] for c in VARIANT_CASES],
    ids=[c[0] for c in VARIANT_CASES],
)
def test_knockout_dealbreaker_variants(phrase, teaser, reason):
    criteria = {"dealbreakers": [phrase]}
    assert search_jobs.knockout(job(teaser=teaser), criteria) == reason


def test_knockout_without_criteria_never_knocks_out():
    assert search_jobs.knockout(job(title="Croupier", company="Gambling Bhd"), {}) is None


# --- dedupe ------------------------------------------------------------------

def test_dedupe_first_run_returns_all_and_records_first_seen():
    jobs = [job(id="fake:1"), job(id="fake:2", title="Platform Engineer")]
    out, seen = search_jobs.dedupe(jobs, {}, today="2026-09-22")
    assert [j["id"] for j in out] == ["fake:1", "fake:2"]
    assert seen == {"fake:1": "2026-09-22", "fake:2": "2026-09-22"}


def test_dedupe_second_run_drops_repeats_and_keeps_the_original_date():
    jobs = [job(id="fake:1"), job(id="fake:2", title="Platform Engineer")]
    _, seen = search_jobs.dedupe(jobs, {}, today="2026-09-20")
    out, seen2 = search_jobs.dedupe(jobs + [job(id="fake:3", title="SRE")], seen,
                                   today="2026-09-22")
    assert [j["id"] for j in out] == ["fake:3"]
    assert seen2["fake:1"] == "2026-09-20"
    assert seen2["fake:3"] == "2026-09-22"


def test_dedupe_does_not_mutate_the_caller_s_seen_map():
    seen = {}
    search_jobs.dedupe([job()], seen, today="2026-09-22")
    assert seen == {}


def test_dedupe_keep_seen_returns_repeats_for_the_all_flag():
    _, seen = search_jobs.dedupe([job()], {}, today="2026-09-20")
    out, _ = search_jobs.dedupe([job()], seen, today="2026-09-22", keep_seen=True)
    assert len(out) == 1


def test_dedupe_collapses_the_same_posting_across_boards_by_priority():
    jobs = [
        job(id="linkedin:9", source="linkedin"),
        job(id="jobstreet:9", source="jobstreet"),
    ]
    out, _ = search_jobs.dedupe(jobs, {}, today="2026-09-22")
    assert [j["source"] for j in out] == ["jobstreet"]


def test_dedupe_keeps_different_postings_from_the_same_company():
    jobs = [job(id="fake:1"), job(id="fake:2", title="Data Engineer")]
    out, _ = search_jobs.dedupe(jobs, {}, today="2026-09-22")
    assert len(out) == 2


def test_dedupe_keeps_same_title_in_different_cities():
    jobs = [
        job(id="fake:1", location="Kuala Lumpur"),
        job(id="fake:2", location="Penang"),
    ]
    out, _ = search_jobs.dedupe(jobs, {}, today="2026-09-22")
    assert [j["id"] for j in out] == ["fake:1", "fake:2"]


def test_dedupe_collapses_same_title_and_city_across_boards_by_priority():
    jobs = [
        job(id="linkedin:9", source="linkedin", location="Kuala Lumpur"),
        job(id="jobstreet:9", source="jobstreet",
            location="Kuala Lumpur, Federal Territory of Kuala Lumpur"),
    ]
    out, _ = search_jobs.dedupe(jobs, {}, today="2026-09-22")
    assert [j["source"] for j in out] == ["jobstreet"]


# --- rank --------------------------------------------------------------------

def test_rank_orders_by_freshness_then_salary_then_source():
    jobs = [
        job(id="a", posted="2026-09-10", salary_max=30000),
        job(id="b", posted="", salary_max=99000),
        job(id="c", posted="2026-09-20", salary_max=12000, source="linkedin"),
        job(id="d", posted="2026-09-20", salary_max=12000, source="jobstreet"),
        job(id="e", posted="2026-09-20", salary_max=20000, source="mcf"),
    ]
    assert [j["id"] for j in search_jobs.rank(jobs)] == ["e", "d", "c", "a", "b"]


def test_rank_puts_unknown_salary_after_a_known_one_on_the_same_day():
    jobs = [
        job(id="a", posted="2026-09-20", salary_max=None),
        job(id="b", posted="2026-09-20", salary_max=5000),
    ]
    assert [j["id"] for j in search_jobs.rank(jobs)] == ["b", "a"]


# --- run ---------------------------------------------------------------------

BASE = {
    "keywords": ["backend engineer"], "location": "Kuala Lumpur", "country": "MY",
    "salary_min": 9000,
    "dealbreakers": ["gambling industry"], "boards": ["fake"], "days": None, "pages": 1,
}


def test_run_splits_new_and_knocked():
    stub = StubSource("fake", [
        job(id="fake:1"),
        job(id="fake:2", company="Royal Gambling Bhd", title="Go Engineer"),
    ])
    out = search_jobs.run(BASE, sources={"fake": stub}, seen={}, today="2026-09-22")
    assert [j["id"] for j in out["new"]] == ["fake:1"]
    assert "needs_look" not in out
    assert [(j["id"], reason) for j, reason in out["knocked_out"]] == [
        ("fake:2", "dealbreaker: gambling industry"),
    ]
    assert out["sources"]["fake"]["count"] == 2
    assert out["seen"] == {"fake:1": "2026-09-22"}
    assert stub.calls[0]["keywords"] == "backend engineer"
    assert stub.calls[0]["country"] == "MY"


def test_run_keeps_a_posting_without_any_must_have_words():
    stub = StubSource("fake", [
        job(id="fake:1", title="Warehouse Supervisor", teaser="shift rosters, stock counts"),
    ])
    out = search_jobs.run(BASE, sources={"fake": stub}, seen={}, today="2026-09-22")
    assert [j["id"] for j in out["new"]] == ["fake:1"]
    assert out["knocked_out"] == []


def test_run_does_not_mark_knocked_out_postings_as_seen():
    stub = StubSource("fake", [
        job(id="fake:1"),
        job(id="fake:2", company="Royal Gambling Bhd", title="Go Engineer"),
    ])
    out = search_jobs.run(BASE, sources={"fake": stub}, seen={}, today="2026-09-22")
    assert "fake:2" not in out["seen"]


def test_run_queries_every_keyword():
    stub = StubSource("fake", [job()])
    criteria = dict(BASE, keywords=["backend engineer", "golang"])
    search_jobs.run(criteria, sources={"fake": stub}, seen={}, today="2026-09-22")
    assert [c["keywords"] for c in stub.calls] == ["backend engineer", "golang"]


def test_run_excludes_jobs_seen_on_an_earlier_run():
    stub = StubSource("fake", [job(id="fake:1")])
    out = search_jobs.run(BASE, sources={"fake": stub}, seen={"fake:1": "2026-09-01"},
                          today="2026-09-22")
    assert out["new"] == []
    assert out["seen_before"] == 1


def test_run_all_flag_keeps_jobs_seen_before():
    stub = StubSource("fake", [job(id="fake:1")])
    out = search_jobs.run(BASE, sources={"fake": stub}, seen={"fake:1": "2026-09-01"},
                          today="2026-09-22", all_=True)
    assert [j["id"] for j in out["new"]] == ["fake:1"]


def test_run_drops_stale_postings_and_keeps_undated_ones():
    stub = StubSource("fake", [
        job(id="fake:1", posted="2026-09-22"),
        job(id="fake:2", posted="2026-08-01", title="Old Role"),
        job(id="fake:3", posted="", title="Undated Role"),
    ])
    criteria = dict(BASE, days=3)
    out = search_jobs.run(criteria, sources={"fake": stub}, seen={}, today="2026-09-22")
    assert sorted(j["id"] for j in out["new"]) == ["fake:1", "fake:3"]
    assert stub.calls[0]["days"] == 3


def test_run_records_source_warnings():
    stub = StubSource("fake", [], warnings=["fake: HTTP 429 at page 2, stopped"])
    out = search_jobs.run(BASE, sources={"fake": stub}, seen={}, today="2026-09-22")
    assert out["sources"]["fake"]["warnings"] == ["fake: HTTP 429 at page 2, stopped"]


def test_run_stops_querying_a_source_that_warned():
    stub = StubSource("fake", [], warnings=["fake: HTTP 429 at page 1, stopped"])
    criteria = dict(BASE, keywords=["a", "b", "c"])
    search_jobs.run(criteria, sources={"fake": stub}, seen={}, today="2026-09-22")
    assert len(stub.calls) == 1


def test_run_survives_a_source_that_raises():
    boom = StubSource("fake", [], raises=RuntimeError("kaboom"))
    ok = StubSource("other", [job(id="other:1")])
    out = search_jobs.run(dict(BASE, boards=["fake", "other"]),
                          sources={"fake": boom, "other": ok}, seen={}, today="2026-09-22")
    assert [j["id"] for j in out["new"]] == ["other:1"]
    assert any("RuntimeError" in w for w in out["sources"]["fake"]["warnings"])


def test_run_skips_a_source_that_does_not_serve_the_country():
    stub = StubSource("mcf", [job(id="mcf:1")])
    out = search_jobs.run(BASE, sources={"mcf": stub}, seen={}, today="2026-09-22")
    assert stub.calls == []
    assert out["sources"]["mcf"]["skipped"]
    assert out["new"] == []


def test_run_reports_an_unavailable_optional_source():
    stub = StubSource("fakeboard", [])
    stub.UNAVAILABLE_REASON = "needs an API key"
    out = search_jobs.run(BASE, sources={"fakeboard": stub}, seen={}, today="2026-09-22")
    assert out["sources"]["fakeboard"]["skipped"] == "needs an API key"


def test_run_returns_ranked_new_jobs():
    stub = StubSource("fake", [
        job(id="fake:1", posted="2026-09-10"),
        job(id="fake:2", posted="2026-09-21", title="Go Engineer"),
    ])
    out = search_jobs.run(BASE, sources={"fake": stub}, seen={}, today="2026-09-22")
    assert [j["id"] for j in out["new"]] == ["fake:2", "fake:1"]


# --- render_markdown ---------------------------------------------------------

def test_render_markdown_has_the_table_sections_and_sources_line():
    jobs = [job(id="fake:1")]
    knocked = [(job(id="fake:2", company="Gambling Bhd"), "dealbreaker: gambling industry")]
    stats = {
        "jobstreet": {"count": 42, "warnings": [], "skipped": ""},
        "linkedin": {"count": 0, "warnings": ["linkedin: HTTP 429 at page 2, stopped"],
                     "skipped": ""},
        "fakeboard": {"count": 0, "warnings": [], "skipped": "needs an API key"},
    }
    md = search_jobs.render_markdown(jobs, knocked, sources=stats, seen_before=4)
    assert md.startswith("## 1 new posting (1 knocked out, 4 seen before)")
    assert "| # | Posted | Source | Company | Role | Location / mode | Salary | Link |" in md
    assert "### Knocked out" in md
    assert "- Gambling Bhd — Backend Engineer: dealbreaker: gambling industry" in md
    assert "jobstreet 42" in md
    assert "429 at page 2, stopped" in md
    assert "fakeboard skipped: needs an API key" in md


def test_render_markdown_has_no_soft_bucket():
    md = search_jobs.render_markdown([job(title="Warehouse Supervisor")], [], sources={})
    assert "Needs a look" not in md
    assert "needs a look" not in md


def test_render_markdown_says_zero_new_since_last_run():
    md = search_jobs.render_markdown([], [], sources={})
    assert "0 new since last run" in md
    assert "###" not in md


def test_render_markdown_escapes_pipes_in_titles():
    md = search_jobs.render_markdown([job(title="Engineer | Backend")], [], sources={})
    assert "Engineer \\| Backend" in md


# --- main --------------------------------------------------------------------

@pytest.fixture()
def workspace(tmp_path, monkeypatch):
    monkeypatch.setenv("JOB_HUNT_DIR", str(tmp_path))
    (tmp_path / "profile.md").write_text(SAMPLE_PROFILE, encoding="utf-8")
    (tmp_path / "seen-jobs.json").write_text("{}", encoding="utf-8")
    return tmp_path


def test_main_prints_markdown_and_saves_seen(workspace, monkeypatch, capsys):
    stub = StubSource("jobstreet", [job(id="jobstreet:1")])
    monkeypatch.setattr(search_jobs, "get_sources", lambda names: {"jobstreet": stub})
    code = search_jobs.main([])
    out = capsys.readouterr().out
    assert code == 0
    assert "1 new posting" in out
    assert json.loads((workspace / "seen-jobs.json").read_text(encoding="utf-8")) != {}
    # criteria came from the profile
    assert stub.calls[0]["location"] == "Kuala Lumpur"
    assert stub.calls[0]["salary_min"] == 9000


def test_main_json_output(workspace, monkeypatch, capsys):
    stub = StubSource("jobstreet", [job(id="jobstreet:1")])
    monkeypatch.setattr(search_jobs, "get_sources", lambda names: {"jobstreet": stub})
    assert search_jobs.main(["--json"]) == 0
    payload = json.loads(capsys.readouterr().out)
    assert set(payload) == {"new", "knocked_out", "sources"}
    assert payload["new"][0]["id"] == "jobstreet:1"


def test_main_no_seen_does_not_write_the_file(workspace, monkeypatch, capsys):
    stub = StubSource("jobstreet", [job(id="jobstreet:1")])
    monkeypatch.setattr(search_jobs, "get_sources", lambda names: {"jobstreet": stub})
    assert search_jobs.main(["--no-seen"]) == 0
    capsys.readouterr()
    assert (workspace / "seen-jobs.json").read_text(encoding="utf-8") == "{}"


def test_main_flags_override_the_profile(workspace, monkeypatch, capsys):
    stub = StubSource("jobstreet", [])
    monkeypatch.setattr(search_jobs, "get_sources", lambda names: {"jobstreet": stub})
    assert search_jobs.main(["--keywords", "sre, platform", "--location", "Penang",
                             "--country", "MY", "--days", "2", "--pages", "3",
                             "--salary-min", "12000"]) == 0
    capsys.readouterr()
    assert [c["keywords"] for c in stub.calls] == ["sre", "platform"]
    assert stub.calls[0]["location"] == "Penang"
    assert stub.calls[0]["days"] == 2
    assert stub.calls[0]["pages"] == 3
    assert stub.calls[0]["salary_min"] == 12000


def test_main_zero_results_still_exits_zero(workspace, monkeypatch, capsys):
    monkeypatch.setattr(search_jobs, "get_sources",
                        lambda names: {"jobstreet": StubSource("jobstreet", [])})
    assert search_jobs.main([]) == 0
    assert "0 new since last run" in capsys.readouterr().out


def test_main_rejects_an_unknown_source(workspace, capsys):
    with pytest.raises(SystemExit) as exc:
        search_jobs.main(["--sources", "monster"])
    assert exc.value.code == 2


def test_main_without_keywords_explains_itself(tmp_path, monkeypatch, capsys):
    monkeypatch.setenv("JOB_HUNT_DIR", str(tmp_path))
    (tmp_path / "profile.md").write_text(TEMPLATE_PROFILE, encoding="utf-8")
    assert search_jobs.main([]) == 2
    assert "keywords" in capsys.readouterr().err.lower()


def test_default_sources_follow_the_country():
    assert search_jobs.default_sources("MY") == ["jobstreet", "linkedin"]
    assert search_jobs.default_sources("SG") == ["jobstreet", "mcf", "linkedin"]


def test_get_sources_imports_the_real_modules():
    mods = search_jobs.get_sources(["jobstreet", "mcf"])
    assert mods["jobstreet"].NAME == "jobstreet"
    assert mods["mcf"].NAME == "mcf"


# --- final review: the salary floor's currency, an unsupported country --------

RM_FLOOR = search_jobs.read_criteria("- **Salary expectation:** RM 15,000 / month")

FLOOR_CURRENCY_CASES = [
    ("sgd posting kept", {"currency": "SGD", "country": "SG", "salary_max": 8000}, None),
    ("rm posting knocked", {"currency": "MYR", "salary_max": 9000}, "salary below floor"),
    ("no currency, same market", {"currency": "", "country": "MY", "salary_max": 9000},
     "salary below floor"),
    ("no currency, other market", {"currency": "", "country": "SG", "salary_max": 9000}, None),
]


@pytest.mark.parametrize(
    "fields,reason", [c[1:] for c in FLOOR_CURRENCY_CASES], ids=[c[0] for c in FLOOR_CURRENCY_CASES]
)
def test_salary_floor_applies_only_in_its_own_currency(fields, reason):
    assert RM_FLOOR["salary_currency"] == "MYR"
    assert search_jobs.knockout(job(**fields), dict(RM_FLOOR)) == reason


@pytest.mark.parametrize("value,currency", [
    ("RM9k/month", "MYR"), ("MYR 9,000", "MYR"), ("S$8,000 / month", "SGD"),
    ("up to 8 months bonus, SGD 7,500 / month", "SGD"), ("9,000 per month, permanent", ""),
])
def test_read_criteria_salary_currency(value, currency):
    assert search_jobs.read_criteria(f"- **Salary expectation:** {value}")["salary_currency"] == currency


def test_run_keeps_a_foreign_floor_away_from_the_board_filter():
    stub = StubSource("fake", [job(id="fake:1", currency="SGD", country="SG", salary_max=8000)])
    criteria = dict(BASE, country="SG", salary_currency="MYR", salary_min=15000)
    out = search_jobs.run(criteria, sources={"fake": stub}, seen={}, today="2026-09-22")
    assert stub.calls[0]["salary_min"] is None
    assert [j["id"] for j in out["new"]] == ["fake:1"]


def test_run_names_an_unsupported_country():
    sources = search_jobs.get_sources(["jobstreet"])
    out = search_jobs.run(dict(BASE, country="ID"), sources=sources, seen={}, today="2026-09-22")
    assert out["sources"]["jobstreet"]["warnings"] == ["jobstreet: unsupported country ID"]
