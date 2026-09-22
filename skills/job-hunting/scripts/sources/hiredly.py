#!/usr/bin/env python3
"""Hiredly Malaysia (ex-WOBB).

Hiredly is a Next.js app with no public API: the server-rendered listing page
embeds every job in `__NEXT_DATA__`, so one page fetch yields ~30 jobs which
are then keyword-filtered client-side. Malaysia only.
"""
from __future__ import annotations

import html as html_mod
import json
import re
import sys
from pathlib import Path
from urllib.parse import urlencode

_SCRIPTS = str(Path(__file__).resolve().parent.parent)
if _SCRIPTS not in sys.path:
    sys.path.insert(0, _SCRIPTS)

from _common import default_fetch, detail_record, html_to_text, job_record  # noqa: E402

NAME = "hiredly"
LAST_WARNINGS: list[str] = []

BASE = "https://my.hiredly.com"
COUNTRY = "MY"
CURRENCY = "MYR"

_NEXT_DATA_RE = re.compile(
    r'<script id="__NEXT_DATA__"[^>]*>(.*?)</script>', re.S)
_NUM_RE = re.compile(r"\d[\d,]*")


def parse_salary(label: str) -> tuple[int | None, int | None]:
    """"3500 - 4999" -> (3500, 4999); "Undisclosed" -> (None, None)."""
    nums = [int(n.replace(",", "")) for n in _NUM_RE.findall(label or "")]
    if not nums:
        return None, None
    if len(nums) == 1:
        return nums[0], nums[0]
    return nums[0], nums[1]


def _next_data(raw: bytes | str) -> dict:
    text = raw.decode("utf-8", "replace") if isinstance(raw, bytes) else (raw or "")
    m = _NEXT_DATA_RE.search(text)
    if not m:
        return {}
    try:
        return json.loads(m.group(1))
    except ValueError:
        return {}


def _teaser(row: dict) -> str:
    summary = html_mod.unescape(row.get("gptSummary") or "").strip()
    if summary:
        return " ".join(summary.split())
    bits = [str(row.get("careerLevel") or "").strip()]
    years = row.get("minYearsExperience")
    if isinstance(years, int) and years:
        bits.append(f"{years}+ yrs experience")
    return " · ".join(b for b in bits if b)


def parse_search(raw: bytes | str, *, country: str) -> list[dict]:
    country = (country or "").upper()
    props = ((_next_data(raw).get("props") or {}).get("pageProps") or {})
    jobs = []
    for row in props.get("jobs") or []:
        slug = str(row.get("slug") or "").strip()
        if not slug:
            continue
        label = (row.get("salary") or "").strip()
        low, high = parse_salary(label)
        jobs.append(job_record(
            NAME, country,
            id=f"{NAME}:{slug}",
            title=(row.get("title") or "").strip(),
            company=((row.get("company") or {}).get("name")
                     or row.get("aggregatedCompanyName") or "").strip(),
            location=(row.get("stateRegion") or row.get("location") or "").strip(),
            salary_min=low,
            salary_max=high,
            currency=CURRENCY,
            salary_label=label,
            posted=(row.get("activeAt") or "")[:10],
            url=f"{BASE}/jobs/{slug}",
            teaser=_teaser(row),
        ))
    return jobs


def search(keywords: str, location: str, *, country: str, days: int | None = None,
           salary_min: int | None = None, pages: int = 1, fetch=None) -> list[dict]:
    """Fetch one state listing page and filter it locally.

    Hiredly has no search/pagination API worth trusting, so `pages` and `days`
    are ignored; `keywords` is a case-insensitive substring match on the title
    and `salary_min` drops jobs whose parsed maximum is lower. Never raises on
    HTTP failure (see LAST_WARNINGS).
    """
    LAST_WARNINGS.clear()
    if (country or "").upper() != COUNTRY:
        LAST_WARNINGS.append(f"{NAME}: MY only, skipped for {country}")
        return []
    fetch = fetch or default_fetch
    state = location.strip() or "Kuala Lumpur"
    url = f"{BASE}/jobs?" + urlencode({"state": state})
    status, body = fetch(url, None, "GET", None)
    if status != 200:
        LAST_WARNINGS.append(f"{NAME}: HTTP {status} for state {state}, stopped")
        return []
    jobs = parse_search(body, country=COUNTRY)
    needle = (keywords or "").strip().lower()
    if needle:
        jobs = [j for j in jobs if needle in j["title"].lower()]
    if salary_min:
        jobs = [j for j in jobs if j["salary_max"] is None or j["salary_max"] >= salary_min]
    return jobs


def parse_detail(raw: bytes | str, *, country: str) -> dict:
    props = ((_next_data(raw).get("props") or {}).get("pageProps") or {})
    job = props.get("job") or props.get("jobDetail") or {}
    slug = str(job.get("slug") or "").strip()
    return detail_record(
        description_md=html_to_text(job.get("description") or job.get("jobDescription") or ""),
        title=(job.get("title") or "").strip(),
        company=((job.get("company") or {}).get("name") or "").strip(),
        url=f"{BASE}/jobs/{slug}" if slug else "",
        screening_questions=[],
    )


def detail(job_id: str, *, country: str, fetch=None) -> dict | None:
    """`job_id` is the Hiredly slug; None when the request or job is missing."""
    fetch = fetch or default_fetch
    status, body = fetch(f"{BASE}/jobs/{job_id}", None, "GET", None)
    if status != 200:
        LAST_WARNINGS.append(f"{NAME}: HTTP {status} for job {job_id}")
        return None
    got = parse_detail(body, country=COUNTRY)
    if not got["url"]:
        got["url"] = f"{BASE}/jobs/{job_id}"
    return got if got["description_md"] or got["title"] else None
