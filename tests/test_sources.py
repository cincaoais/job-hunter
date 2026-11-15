"""Fixture-driven tests for the board source modules.

Every parser here is pure: it is handed recorded bytes from
tests/fixtures/recorded/ and must never touch the network. The only network
paths (`search`/`detail`) are exercised through an injected `fetch`.
"""
import json
import pathlib
import re
import sys

import pytest

ROOT = pathlib.Path(__file__).resolve().parents[1]
SCRIPTS = ROOT / "skills" / "job-hunting" / "scripts"
FIXTURES = pathlib.Path(__file__).resolve().parent / "fixtures" / "recorded"
sys.path.insert(0, str(SCRIPTS))

from sources import jobstreet, linkedin, mcf  # noqa: E402

JOB_KEYS = {
    "id", "source", "title", "company", "location", "mode",
    "salary_min", "salary_max", "currency", "salary_label",
    "posted", "url", "teaser", "applicants", "country",
}
DETAIL_KEYS = {"description_md", "title", "company", "url", "screening_questions",
               "location", "salary_label", "posted"}
DATE_RE = re.compile(r"^\d{4}-\d{2}-\d{2}$")


def fx(name: str) -> bytes:
    return (FIXTURES / name).read_bytes()


def fetcher(status=200, body=b"", record=None):
    """Return an injectable fetch that always answers (status, body)."""

    def fetch(url, headers=None, method="GET", payload=None):
        if record is not None:
            record.append({"url": url, "headers": headers, "method": method, "payload": payload})
        return status, body

    return fetch


# --- parse_search: shape contract across all sources -------------------------

SEARCH_CASES = [
    ("jobstreet-my", jobstreet, "jobstreet_my_search.json", "MY", 10),
    ("jobstreet-sg", jobstreet, "jobstreet_sg_search.json", "SG", 5),
    ("mcf", mcf, "mcf_search.json", "SG", 5),
    ("linkedin", linkedin, "linkedin_search.html", "MY", 10),
]


@pytest.mark.parametrize(
    "mod,fixture,country,count",
    [c[1:] for c in SEARCH_CASES],
    ids=[c[0] for c in SEARCH_CASES],
)
def test_parse_search_returns_normalized_rows(mod, fixture, country, count):
    jobs = mod.parse_search(fx(fixture), country=country)
    assert len(jobs) == count
    for job in jobs:
        assert set(job) == JOB_KEYS
        assert job["source"] == mod.NAME
        assert job["id"].startswith(mod.NAME + ":") and len(job["id"]) > len(mod.NAME) + 1
        assert job["country"] == country
        assert job["url"].startswith("https://")
        assert job["posted"] == "" or DATE_RE.match(job["posted"])
        assert job["mode"] in ("Hybrid", "Remote", "Onsite", "")
        assert job["currency"] in ("MYR", "SGD", "")
        for key in ("salary_min", "salary_max", "applicants"):
            assert job[key] is None or isinstance(job[key], int)
        for key in ("title", "company", "location", "salary_label", "teaser"):
            assert isinstance(job[key], str)


def test_parse_search_accepts_str_as_well_as_bytes():
    text = fx("jobstreet_my_search.json").decode("utf-8")
    assert jobstreet.parse_search(text, country="MY")[0]["id"] == "jobstreet:94655291"


# --- per-source field mapping -------------------------------------------------

def test_jobstreet_parse_search_fields():
    jobs = jobstreet.parse_search(fx("jobstreet_my_search.json"), country="MY")
    first = jobs[0]
    assert first["id"] == "jobstreet:94655291"
    assert first["title"] == "Lead Product Designer"
    assert first["company"] == "Electronic Arts"
    assert first["location"] == "Kuala Lumpur City Centre, Kuala Lumpur"
    assert first["mode"] == "Hybrid"
    assert first["posted"] == "2026-09-15"
    assert first["url"] == "https://my.jobstreet.com/job/94655291"
    assert first["currency"] == "MYR"
    assert (first["salary_min"], first["salary_max"]) == (None, None)
    assert first["teaser"].startswith("We’re looking for a Lead Product Designer")
    assert first["applicants"] is None

    paid = jobs[1]
    assert (paid["salary_min"], paid["salary_max"]) == (15000, 20000)
    assert "15,000" in paid["salary_label"]
    assert jobs[5]["mode"] == "Remote"


def test_jobstreet_parse_search_falls_back_to_bullet_points_for_the_teaser():
    payload = json.dumps({"data": [{
        "id": "1", "title": "Dev", "companyName": "Acme", "teaser": "",
        "bulletPoints": ["Great team", "Real ownership"],
        "listingDate": "2026-09-01T00:00:00Z", "locations": [{"label": "KL"}],
    }]})
    job = jobstreet.parse_search(payload, country="MY")[0]
    assert job["teaser"] == "Great team; Real ownership"
    assert job["mode"] == "" and job["salary_label"] == ""


def test_jobstreet_parse_search_sg_uses_sgd_host_and_currency():
    jobs = jobstreet.parse_search(fx("jobstreet_sg_search.json"), country="SG")
    assert jobs[0]["url"].startswith("https://sg.jobstreet.com/job/")
    assert jobs[0]["currency"] == "SGD"
    assert (jobs[1]["salary_min"], jobs[1]["salary_max"]) == (5000, 5000)


def test_mcf_parse_search_fields():
    jobs = mcf.parse_search(fx("mcf_search.json"), country="SG")
    first = jobs[0]
    assert first["id"] == "mcf:74c51e4e07647ca4c27451ce89742e14"
    assert first["title"] == "Software Engineer"
    assert first["company"] == "CREATIVE LABS PTE. LTD."
    assert first["location"].startswith("D05")
    assert (first["salary_min"], first["salary_max"]) == (4000, 6500)
    assert first["currency"] == "SGD"
    assert "4,000" in first["salary_label"]
    assert first["posted"] == "2026-09-16"
    assert first["applicants"] == 0
    assert first["url"].startswith("https://www.mycareersfuture.gov.sg/job/")
    assert "Junior Executive" in first["teaser"] and "Full Time" in first["teaser"]
    assert first["mode"] == ""


def test_linkedin_parse_search_fields():
    jobs = linkedin.parse_search(fx("linkedin_search.html"), country="MY")
    first = jobs[0]
    assert first["id"] == "linkedin:4455634411"
    assert first["title"] == "Senior Software Engineer, Backend (Fulfillment)"
    assert first["company"] == "Grab"
    assert first["location"] == "Petaling Jaya, Selangor, Malaysia"
    assert first["posted"] == "2026-09-10"
    assert first["url"] == (
        "https://my.linkedin.com/jobs/view/"
        "senior-software-engineer-backend-fulfillment-at-grab-4455634411"
    )
    assert "?" not in first["url"]
    # no salary on these cards -> no currency claim
    assert (first["salary_min"], first["salary_max"], first["currency"]) == (None, None, "")
    assert first["applicants"] is None


def _linkedin_card(title="Engineer", company="Acme", salary=None):
    salary_html = (
        f'<span class="job-search-card__salary-info">{salary}</span>' if salary else "")
    return (
        '<li><a class="base-card__full-link" '
        'href="https://www.linkedin.com/jobs/view/1234567890?refId=abc">x</a>'
        f'<h3 class="base-search-card__title">{title}</h3>'
        f'<h4 class="base-search-card__subtitle">{company}</h4>'
        f'{salary_html}</li>'
    )


@pytest.mark.parametrize("country,label,expected", [
    ("MY", "SGD 5,000.00 - SGD 6,000.00", "SGD"),
    ("SG", "MYR8,000.00 - MYR12,000.00", "MYR"),
])
def test_linkedin_currency_comes_from_card_label(country, label, expected):
    jobs = linkedin.parse_search(_linkedin_card(salary=label), country=country)
    assert jobs[0]["currency"] == expected


def test_linkedin_no_salary_has_no_currency():
    jobs = linkedin.parse_search(_linkedin_card(), country="MY")
    assert jobs[0]["currency"] == ""


def test_linkedin_card_without_title_is_skipped():
    raw = _linkedin_card(title="", salary="SGD 5,000.00") + _linkedin_card()
    jobs = linkedin.parse_search(raw, country="MY")
    assert len(jobs) == 1
    assert jobs[0]["title"] == "Engineer"


def test_linkedin_search_warns_when_cards_found_but_none_parsed():
    broken = (
        b'<li><a class="base-card__full-link" '
        b'href="https://www.linkedin.com/jobs/view/1234567890">x</a></li>')
    jobs = linkedin.search("swe", "KL", country="MY", fetch=fetcher(200, broken))
    assert jobs == []
    assert any("cards found but none parsed" in w for w in linkedin.LAST_WARNINGS)


# --- parse_detail -------------------------------------------------------------

def test_jobstreet_parse_detail():
    got = jobstreet.parse_detail(fx("jobstreet_detail.json"), country="MY")
    assert set(got) == DETAIL_KEYS
    assert got["title"] == "Lead Product Designer"
    assert got["company"] == "Electronic Arts"
    assert got["url"] == "https://my.jobstreet.com/job/94655291"
    assert got["screening_questions"] == []
    assert len(got["description_md"]) > 200
    assert "<" not in got["description_md"]
    assert "- Location: Kuala Lumpur" in got["description_md"]
    # the GraphQL payload carries these; fetch_posting puts them in frontmatter
    assert got["location"] == "Kuala Lumpur City Centre, Kuala Lumpur"
    assert got["posted"] == "2026-09-15"
    assert got["salary_label"] == ""  # this advertiser published no salary


def test_mcf_parse_detail():
    got = mcf.parse_detail(fx("mcf_detail.json"), country="SG")
    assert set(got) == DETAIL_KEYS
    assert got["title"] == "Software Engineer"
    assert got["company"] == "CREATIVE LABS PTE. LTD."
    assert got["url"].startswith("https://www.mycareersfuture.gov.sg/job/")
    assert got["screening_questions"] == []
    assert len(got["description_md"]) > 200
    assert "<" not in got["description_md"]
    assert "- Develop, maintain and debug embedded firmware" in got["description_md"]
    assert got["location"] == "D05 Pasir Panjang, Hong Leong Garden, Clementi New Town"
    assert got["posted"] == "2026-09-16"
    assert got["salary_label"] == "SGD 4,000 - 6,500 per month"


def test_linkedin_parse_detail():
    got = linkedin.parse_detail(fx("linkedin_detail.html"), country="MY")
    assert set(got) == DETAIL_KEYS
    assert got["title"] == "Senior Software Engineer, Backend (Fulfillment)"
    assert got["company"] == "Grab"
    assert "/jobs/view/" in got["url"]
    assert got["screening_questions"] == []
    assert len(got["description_md"]) > 200
    assert "<" not in got["description_md"]
    # the guest top card carries the location; it has no date or salary
    assert got["location"] == "Petaling Jaya, Selangor, Malaysia"
    assert got["posted"] == "" and got["salary_label"] == ""


def test_parse_detail_on_junk_returns_empty_record():
    for mod, raw in ((jobstreet, b"{}"), (mcf, b"{}"), (linkedin, b"<html></html>")):
        got = mod.parse_detail(raw, country="MY")
        assert set(got) == DETAIL_KEYS
        assert got["description_md"] == "" and got["screening_questions"] == []
        for key in ("location", "salary_label", "posted"):
            assert got[key] == ""


# --- salary parsing -----------------------------------------------------------

def test_jobstreet_parse_salary_annual_label_is_monthly():
    payload = json.dumps({"data": [{
        "id": "1", "title": "Dev", "companyName": "Acme",
        "salaryLabel": "RM 120,000 - RM 144,000 per year",
        "listingDate": "2026-09-01T00:00:00Z", "locations": [{"label": "KL"}],
    }]})
    job = jobstreet.parse_search(payload, country="MY")[0]
    assert (job["salary_min"], job["salary_max"]) == (10000, 12000)
    assert job["salary_label"] == "RM 120,000 - RM 144,000 per year"


@pytest.mark.parametrize("label,expected", [
    ("RM 15,000 – RM 20,000 per month", (15000, 20000)),
    ("RM 15,000 – RM 20,000 per month", (15000, 20000)),
    ("$4,000 – $6,500 per month", (4000, 6500)),
    ("5000", (5000, 5000)),
    ("World Class Benefits", (None, None)),
    ("", (None, None)),
])
def test_jobstreet_parse_salary(label, expected):
    assert jobstreet.parse_salary(label) == expected


def test_linkedin_parse_search_annual_card_is_monthly():
    jobs = linkedin.parse_search(
        _linkedin_card(salary="SGD 96,000.00 per annum"), country="SG")
    job = jobs[0]
    assert (job["salary_min"], job["salary_max"]) == (8000, 8000)
    assert job["salary_label"] == "SGD 96,000.00 per annum"


@pytest.mark.parametrize("label,expected", [
    ("MYR8,000.00 - MYR12,000.00", (8000, 12000)),
    ("SGD5,500.00", (5500, 5500)),
    ("", (None, None)),
])
def test_linkedin_parse_salary_ignores_decimals(label, expected):
    assert linkedin.parse_salary(label) == expected


# --- search(): request shape, fetch injection, warnings -----------------------

def test_jobstreet_search_builds_v5_query_and_parses():
    calls = []
    jobs = jobstreet.search(
        "software engineer", "Kuala Lumpur", country="MY", days=7, salary_min=8000,
        fetch=fetcher(200, fx("jobstreet_my_search.json"), calls),
    )
    assert len(jobs) == 10 and jobstreet.LAST_WARNINGS == []
    url = calls[0]["url"]
    assert url.startswith("https://my.jobstreet.com/api/jobsearch/v5/search?")
    for part in ("siteKey=MY-Main", "sourcesystem=houston", "locale=en-MY",
                 "keywords=software+engineer", "where=Kuala+Lumpur", "page=1",
                 "pageSize=100", "sortmode=ListedDate", "daterange=7",
                 "salaryrange=8000-", "salarytype=monthly"):
        assert part in url
    assert calls[0]["method"] == "GET"


def test_jobstreet_search_http_error_warns_and_returns_partial():
    jobs = jobstreet.search("swe", "KL", country="MY", fetch=fetcher(429, b""))
    assert jobs == []
    assert any("429" in w for w in jobstreet.LAST_WARNINGS)
    assert jobstreet.LAST_WARNINGS[0].startswith("jobstreet:")


def test_mcf_search_posts_expected_payload():
    calls = []
    jobs = mcf.search("software engineer", "Singapore", country="SG", salary_min=5000,
                      fetch=fetcher(200, fx("mcf_search.json"), calls))
    assert len(jobs) == 5
    assert calls[0]["method"] == "POST"
    assert calls[0]["url"] == "https://api.mycareersfuture.gov.sg/v2/search?limit=20&page=0"
    assert calls[0]["payload"] == {
        "search": "software engineer", "sortBy": ["new_posting_date"], "salary": 5000,
    }


def test_linkedin_search_pages_and_stops_on_429():
    calls = []
    responses = [(200, fx("linkedin_search.html")), (429, b"")]

    def fetch(url, headers=None, method="GET", payload=None):
        calls.append(url)
        return responses[min(len(calls) - 1, len(responses) - 1)]

    naps = []
    jobs = linkedin.search("software engineer", "Kuala Lumpur", country="MY", days=7,
                           pages=3, fetch=fetch, sleep=naps.append)
    assert len(jobs) == 10
    assert len(calls) == 2
    assert "start=0" in calls[0] and "start=25" in calls[1]
    assert "f_TPR=r604800" in calls[0]
    assert naps == [linkedin.PAGE_DELAY]  # paused before page 2, not before page 1
    assert any("429" in w for w in linkedin.LAST_WARNINGS)


def test_detail_uses_injected_fetch():
    calls = []
    got = jobstreet.detail("94655291", country="MY",
                           fetch=fetcher(200, fx("jobstreet_detail.json"), calls))
    assert got["title"] == "Lead Product Designer"
    assert calls[0]["url"] == "https://my.jobstreet.com/graphql"
    assert calls[0]["method"] == "POST"
    payload = calls[0]["payload"]
    assert payload["operationName"] == "jobDetails"
    assert payload["variables"] == {
        "jobId": "94655291", "locale": "en-MY", "zone": "asia-4",
        "timezone": "Asia/Kuala_Lumpur",
    }
    assert payload["query"].startswith("query jobDetails($jobId: ID!")

    sg_calls = []
    mcf.detail("74c51e4e07647ca4c27451ce89742e14", country="SG",
               fetch=fetcher(200, fx("mcf_detail.json"), sg_calls))
    assert sg_calls[0]["url"] == (
        "https://api.mycareersfuture.gov.sg/v2/jobs/74c51e4e07647ca4c27451ce89742e14"
    )


def test_detail_returns_none_on_http_error():
    for mod in (jobstreet, mcf, linkedin):
        assert mod.detail("1", country="MY", fetch=fetcher(500, b"")) is None


def test_every_source_exposes_the_same_interface():
    for mod in (jobstreet, mcf, linkedin):
        assert isinstance(mod.NAME, str) and mod.NAME
        assert isinstance(mod.LAST_WARNINGS, list)
        for fn in ("search", "parse_search", "detail", "parse_detail"):
            assert callable(getattr(mod, fn))


def test_fixtures_are_verbatim_recordings():
    """Guard against accidental re-encoding of the recorded fixtures."""
    assert json.loads(fx("jobstreet_my_search.json"))["totalCount"] > 0
    assert json.loads(fx("jobstreet_detail.json"))["data"]["jobDetails"]["job"]["id"] == "94655291"
    assert json.loads(fx("mcf_search.json"))["total"] > 0


# --- never-raise guards -------------------------------------------------------

MALFORMED = [b"", b"not json at all", b"[1, 2, 3]", b'"just a string"', b"null"]


@pytest.mark.parametrize("mod,country,container", [
    (jobstreet, "MY", "data"),
    (mcf, "SG", "results"),
])
def test_json_parse_search_survives_malformed_payloads(mod, country, container):
    for raw in MALFORMED + [json.dumps({container: "oops"}).encode(),
                            json.dumps({container: [None, 7, "x"]}).encode()]:
        assert mod.parse_search(raw, country=country) == []


def test_search_survives_malformed_bodies_without_raising():
    assert jobstreet.search("swe", "KL", country="MY", fetch=fetcher(200, b"not json")) == []
    assert mcf.search("swe", "SG", country="SG", fetch=fetcher(200, b"not json")) == []
    assert linkedin.search("swe", "KL", country="MY", fetch=fetcher(200, b"<html>"),
                           sleep=lambda s: None) == []


@pytest.mark.parametrize("field,value", [
    ("positionLevels", "oops"),
    ("employmentTypes", "oops"),
    ("positionLevels", [None, 7, "x"]),
    ("employmentTypes", [{"nope": 1}]),
    ("flexibleWorkArrangements", "oops"),
    ("screeningQuestions", "oops"),
    ("address", "oops"),
    ("salary", "oops"),
    ("postedCompany", "oops"),
    ("metadata", "oops"),
])
def test_mcf_parse_search_guards_nested_list_and_dict_fields(field, value):
    """A string where the API normally sends a list/dict must not raise."""
    row = {"uuid": "u1", "title": "Dev", field: value}
    jobs = mcf.parse_search(json.dumps({"results": [row]}), country="SG")
    assert len(jobs) == 1
    assert set(jobs[0]) == JOB_KEYS
    assert jobs[0]["id"] == "mcf:u1" and jobs[0]["title"] == "Dev"


def test_mcf_parse_detail_guards_nested_fields():
    for field, value in (("screeningQuestions", "oops"), ("postedCompany", "oops"),
                         ("metadata", "oops"), ("screeningQuestions", [None, 3])):
        got = mcf.parse_detail(json.dumps({"uuid": "u1", "title": "Dev", field: value}),
                               country="SG")
        assert set(got) == DETAIL_KEYS and got["screening_questions"] == []


# --- mode mapping -------------------------------------------------------------

@pytest.mark.parametrize("display,expected", [
    ("On-site", "Onsite"), ("Hybrid", "Hybrid"), ("Remote", "Remote"),
    ("Something else", ""), (None, ""),
])
def test_jobstreet_mode_mapping(display, expected):
    payload = json.dumps({"data": [{
        "id": "1", "title": "Dev", "companyName": "Acme",
        "workArrangements": {"displayText": display},
    }]})
    assert jobstreet.parse_search(payload, country="MY")[0]["mode"] == expected


@pytest.mark.parametrize("arrangements,expected", [
    (["Telecommuting"], "Remote"),
    (["Work from home"], "Remote"),
    (["Hybrid working"], "Hybrid"),
    (["Flexi-time"], ""),
    ([], ""),
])
def test_mcf_mode_mapping(arrangements, expected):
    payload = json.dumps({"results": [{
        "uuid": "u1", "title": "Dev", "flexibleWorkArrangements": arrangements,
    }]})
    assert mcf.parse_search(payload, country="SG")[0]["mode"] == expected


# --- warnings hygiene ---------------------------------------------------------

def test_detail_clears_stale_warnings():
    for mod, country in ((jobstreet, "MY"), (mcf, "SG"), (linkedin, "MY")):
        mod.LAST_WARNINGS.append("stale")
        mod.detail("1", country=country, fetch=fetcher(500, b""))
        assert "stale" not in mod.LAST_WARNINGS
