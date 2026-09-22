#!/usr/bin/env python3
"""LinkedIn guest job search (no login, no API key).

The guest endpoints return HTML fragments, so the parsers work over the
recorded markup. LinkedIn throttles hard: at most 3 pages, one page per
PAGE_DELAY seconds, and any non-200 stops the walk with a warning.
"""
from __future__ import annotations

import html as html_mod
import re
import sys
import time
from pathlib import Path
from urllib.parse import urlencode

_SCRIPTS = str(Path(__file__).resolve().parent.parent)
if _SCRIPTS not in sys.path:
    sys.path.insert(0, _SCRIPTS)

from _common import default_fetch, detail_record, html_to_text, job_record  # noqa: E402

NAME = "linkedin"
LAST_WARNINGS: list[str] = []

GUEST_API = "https://www.linkedin.com/jobs-guest/jobs/api"
BROWSER_UA = (
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) "
    "Chrome/124.0 Safari/537.36"
)
CURRENCIES = {"MY": "MYR", "SG": "SGD"}
MAX_PAGES = 3
PAGE_SIZE = 25
PAGE_DELAY = 2.5

_LI_RE = re.compile(r"<li>(.*?)</li>", re.S)
_TITLE_RE = re.compile(r'class="base-search-card__title"[^>]*>(.*?)</h3>', re.S)
_COMPANY_RE = re.compile(r'class="base-search-card__subtitle"[^>]*>(.*?)</h4>', re.S)
_LOCATION_RE = re.compile(r'class="job-search-card__location"[^>]*>(.*?)</span>', re.S)
_DATE_RE = re.compile(r'<time[^>]*datetime="([0-9]{4}-[0-9]{2}-[0-9]{2})"')
_LINK_RE = re.compile(r'class="base-card__full-link[^"]*"[^>]*href="([^"]+)"')
_SALARY_RE = re.compile(r'class="job-search-card__salary-info[^"]*"[^>]*>(.*?)</span>', re.S)
_ID_RE = re.compile(r"(\d+)/?$")
_DETAIL_TITLE_RE = re.compile(r'class="top-card-layout__title[^"]*"[^>]*>(.*?)</h[12]>', re.S)
_DETAIL_COMPANY_RE = re.compile(r'class="topcard__org-name-link[^"]*"[^>]*>(.*?)</a>', re.S)
_DETAIL_URL_RE = re.compile(r'https://[a-z.]*linkedin\.com/jobs/view/[^"?\s]+')
_MARKUP_RE = re.compile(r'<div class="show-more-less-html__markup[^"]*"[^>]*>', re.S)
_NUM_RE = re.compile(r"\d[\d,]*")
_DECIMALS_RE = re.compile(r"\.\d+")


def _text(html: str) -> str:
    """Tag-free, entity-decoded, whitespace-collapsed inline text."""
    s = re.sub(r"<[^>]*>", " ", html or "")
    return re.sub(r"\s+", " ", html_mod.unescape(s)).strip()


def parse_salary(label: str) -> tuple[int | None, int | None]:
    """Guest cards show e.g. "MYR8,000.00 - MYR12,000.00"; no digits -> (None, None)."""
    whole = _DECIMALS_RE.sub("", label or "")
    nums = [int(n.replace(",", "")) for n in _NUM_RE.findall(whole)]
    if not nums:
        return None, None
    if len(nums) == 1:
        return nums[0], nums[0]
    return nums[0], nums[1]


def _job_id(url: str) -> str:
    m = _ID_RE.search(url.rstrip("/"))
    return m.group(1) if m else ""


def _as_text(raw: bytes | str) -> str:
    return raw.decode("utf-8", "replace") if isinstance(raw, bytes) else (raw or "")


def _inner_div(html: str, start: int) -> str:
    """Inner HTML of the <div> whose opening tag ends at `start` (depth-aware)."""
    depth = 1
    for m in re.finditer(r"<div\b|</div\s*>", html[start:]):
        depth += 1 if m.group(0).startswith("<div") else -1
        if depth == 0:
            return html[start:start + m.start()]
    return html[start:]


def parse_search(raw: bytes | str, *, country: str) -> list[dict]:
    country = (country or "").upper()
    jobs = []
    for block in _LI_RE.findall(_as_text(raw)):
        link = _LINK_RE.search(block)
        if not link:
            continue
        url = html_mod.unescape(link.group(1)).split("?")[0]
        job_id = _job_id(url)
        if not job_id:
            continue
        salary_match = _SALARY_RE.search(block)
        label = _text(salary_match.group(1)) if salary_match else ""
        low, high = parse_salary(label)
        title_match = _TITLE_RE.search(block)
        company_match = _COMPANY_RE.search(block)
        location_match = _LOCATION_RE.search(block)
        date_match = _DATE_RE.search(block)
        jobs.append(job_record(
            NAME, country,
            id=f"{NAME}:{job_id}",
            title=_text(title_match.group(1)) if title_match else "",
            company=_text(company_match.group(1)) if company_match else "",
            location=_text(location_match.group(1)) if location_match else "",
            salary_min=low,
            salary_max=high,
            currency=CURRENCIES.get(country, "") if (low or high) else "",
            salary_label=label,
            posted=date_match.group(1) if date_match else "",
            url=url,
        ))
    return jobs


def search(keywords: str, location: str, *, country: str, days: int | None = None,
           salary_min: int | None = None, pages: int = 1, fetch=None) -> list[dict]:
    """Walk the guest search pages. `salary_min` has no guest filter and is
    ignored; never raises on HTTP failure (see LAST_WARNINGS)."""
    LAST_WARNINGS.clear()
    country = (country or "").upper()
    live = fetch is None
    fetch = fetch or default_fetch
    jobs: list[dict] = []
    for page in range(min(max(1, pages), MAX_PAGES)):
        if page and live:
            time.sleep(PAGE_DELAY)
        params = {"keywords": keywords, "location": location, "start": page * PAGE_SIZE}
        url = f"{GUEST_API}/seeMoreJobPostings/search?" + urlencode(params)
        if days:
            url += f"&f_TPR=r{int(days) * 86400}"
        status, body = fetch(url, {"User-Agent": BROWSER_UA}, "GET", None)
        if status != 200:
            LAST_WARNINGS.append(f"{NAME}: HTTP {status} at page {page + 1}, stopped")
            break
        page_jobs = parse_search(body, country=country)
        jobs.extend(page_jobs)
        if not page_jobs:
            break
    return jobs


def parse_detail(raw: bytes | str, *, country: str) -> dict:
    html = _as_text(raw)
    markup = _MARKUP_RE.search(html)
    description = html_to_text(_inner_div(html, markup.end())) if markup else ""
    title_match = _DETAIL_TITLE_RE.search(html)
    company_match = _DETAIL_COMPANY_RE.search(html)
    url_match = _DETAIL_URL_RE.search(html)
    return detail_record(
        description_md=description,
        title=_text(title_match.group(1)) if title_match else "",
        company=_text(company_match.group(1)) if company_match else "",
        url=html_mod.unescape(url_match.group(0)) if url_match else "",
        screening_questions=[],
    )


def detail(job_id: str, *, country: str, fetch=None) -> dict | None:
    """Fetch the guest jobPosting fragment; None when the request or job is missing."""
    fetch = fetch or default_fetch
    status, body = fetch(f"{GUEST_API}/jobPosting/{job_id}", {"User-Agent": BROWSER_UA},
                         "GET", None)
    if status != 200:
        LAST_WARNINGS.append(f"{NAME}: HTTP {status} for job {job_id}")
        return None
    got = parse_detail(body, country=country)
    if not got["url"]:
        got["url"] = f"https://www.linkedin.com/jobs/view/{job_id}"
    return got if got["description_md"] or got["title"] else None
