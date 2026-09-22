#!/usr/bin/env python3
"""JobStreet (SEEK) Malaysia + Singapore.

Search uses the public jobsearch v5 JSON API; detail uses the `jobDetails`
GraphQL operation. Parsers are pure so they can be tested on recorded
fixtures; only `search`/`detail` touch the network, through an injectable
`fetch(url, headers, method, payload) -> (status, bytes)`.
"""
from __future__ import annotations

import json
import re
import sys
from pathlib import Path
from urllib.parse import urlencode

_SCRIPTS = str(Path(__file__).resolve().parent.parent)
if _SCRIPTS not in sys.path:
    sys.path.insert(0, _SCRIPTS)

from _common import default_fetch, detail_record, html_to_text, job_record  # noqa: E402

NAME = "jobstreet"
LAST_WARNINGS: list[str] = []

HOSTS = {"MY": "my.jobstreet.com", "SG": "sg.jobstreet.com"}
SITE_KEYS = {"MY": "MY-Main", "SG": "SG-Main"}
LOCALES = {"MY": "en-MY", "SG": "en-SG"}
ZONES = {"MY": "asia-4", "SG": "asia-5"}
TIMEZONES = {"MY": "Asia/Kuala_Lumpur", "SG": "Asia/Singapore"}
CURRENCIES = {"MY": "MYR", "SG": "SGD"}
PAGE_SIZE = 100

JOB_DETAILS_QUERY = (
    "query jobDetails($jobId: ID!, $zone: Zone!, $locale: Locale!, $timezone: Timezone!) "
    "{ jobDetails(id: $jobId) { job { id title isExpired "
    "shareLink(platform: WEB, zone: $zone, locale: $locale) "
    "advertiser { id name(locale: $locale) } content(platform: WEB) abstract "
    "location { label(locale: $locale, type: LONG) } "
    "salary { label currencyLabel(zone: $zone) } "
    "listedAt { label(context: JOB_POSTED, length: SHORT, timezone: $timezone, locale: $locale) "
    "dateTimeUtc } workTypes { label(locale: $locale) } products { bullets } } } }"
)

_MODES = {"hybrid": "Hybrid", "remote": "Remote", "on-site": "Onsite", "on site": "Onsite",
          "onsite": "Onsite"}
_NUM_RE = re.compile(r"\d[\d,]*")


def parse_salary(label: str) -> tuple[int | None, int | None]:
    """"RM 15,000 - RM 20,000 per month" -> (15000, 20000); no digits -> (None, None)."""
    nums = [int(n.replace(",", "")) for n in _NUM_RE.findall(label or "")]
    if not nums:
        return None, None
    if len(nums) == 1:
        return nums[0], nums[0]
    return nums[0], nums[1]


def _country(country: str) -> str:
    c = (country or "").upper()
    if c not in HOSTS:
        raise ValueError(f"jobstreet: unsupported country {country!r} (expected MY or SG)")
    return c


def _mode(job: dict) -> str:
    text = ((job.get("workArrangements") or {}).get("displayText") or "").strip().lower()
    return _MODES.get(text, "")


def _loads(raw: bytes | str):
    if isinstance(raw, bytes):
        raw = raw.decode("utf-8", "replace")
    try:
        return json.loads(raw)
    except (ValueError, TypeError):
        return {}


def parse_search(raw: bytes | str, *, country: str) -> list[dict]:
    country = _country(country)
    host = HOSTS[country]
    data = _loads(raw)
    jobs = []
    for row in data.get("data") or []:
        job_id = str(row.get("id") or "").strip()
        if not job_id:
            continue
        label = row.get("salaryLabel") or ""
        low, high = parse_salary(label)
        teaser = (row.get("teaser") or "").strip()
        if not teaser:
            teaser = "; ".join(b.strip() for b in (row.get("bulletPoints") or []) if b)
        locations = row.get("locations") or [{}]
        jobs.append(job_record(
            NAME, country,
            id=f"{NAME}:{job_id}",
            title=(row.get("title") or "").strip(),
            company=(row.get("companyName") or "").strip(),
            location=(locations[0].get("label") or "").strip(),
            mode=_mode(row),
            salary_min=low,
            salary_max=high,
            currency=CURRENCIES[country],
            salary_label=label.replace(" ", " ").strip(),
            posted=(row.get("listingDate") or "")[:10],
            url=f"https://{host}/job/{job_id}",
            teaser=teaser,
        ))
    return jobs


def search(keywords: str, location: str, *, country: str, days: int | None = None,
           salary_min: int | None = None, pages: int = 1, fetch=None) -> list[dict]:
    """Search JobStreet; never raises on HTTP failure (see LAST_WARNINGS)."""
    LAST_WARNINGS.clear()
    country = _country(country)
    fetch = fetch or default_fetch
    jobs: list[dict] = []
    for page in range(1, max(1, pages) + 1):
        params = {
            "siteKey": SITE_KEYS[country],
            "sourcesystem": "houston",
            "locale": LOCALES[country],
            "keywords": keywords,
            "where": location,
            "page": page,
            "pageSize": PAGE_SIZE,
            "sortmode": "ListedDate",
        }
        if days:
            params["daterange"] = days
        if salary_min:
            params["salaryrange"] = f"{salary_min}-"
            params["salarytype"] = "monthly"
        url = f"https://{HOSTS[country]}/api/jobsearch/v5/search?" + urlencode(params)
        status, body = fetch(url, None, "GET", None)
        if status != 200:
            LAST_WARNINGS.append(f"{NAME}: HTTP {status} at page {page}, stopped")
            break
        page_jobs = parse_search(body, country=country)
        jobs.extend(page_jobs)
        if len(page_jobs) < PAGE_SIZE:
            break
    return jobs


def parse_detail(raw: bytes | str, *, country: str) -> dict:
    country = _country(country)
    job = ((_loads(raw).get("data") or {}).get("jobDetails") or {}).get("job") or {}
    job_id = str(job.get("id") or "").strip()
    url = f"https://{HOSTS[country]}/job/{job_id}" if job_id else ""
    return detail_record(
        description_md=html_to_text(job.get("content") or ""),
        title=(job.get("title") or "").strip(),
        company=((job.get("advertiser") or {}).get("name") or "").strip(),
        url=url,
        screening_questions=[],
    )


def detail(job_id: str, *, country: str, fetch=None) -> dict | None:
    """Fetch one job's full description; None when the request or job is missing."""
    country = _country(country)
    fetch = fetch or default_fetch
    payload = {
        "operationName": "jobDetails",
        "variables": {
            "jobId": str(job_id),
            "locale": LOCALES[country],
            "zone": ZONES[country],
            "timezone": TIMEZONES[country],
        },
        "query": JOB_DETAILS_QUERY,
    }
    status, body = fetch(f"https://{HOSTS[country]}/graphql", None, "POST", payload)
    if status != 200:
        LAST_WARNINGS.append(f"{NAME}: HTTP {status} for job {job_id}")
        return None
    got = parse_detail(body, country=country)
    return got if got["description_md"] or got["title"] else None
