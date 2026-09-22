#!/usr/bin/env python3
"""Indeed, via the optional `python-jobspy` package.

Indeed has no usable public API, so this source is a thin adapter over
jobspy's scraper. Without jobspy installed `search()` returns [] and
UNAVAILABLE_REASON says what to install; the parser works on plain row dicts
either way.
"""
from __future__ import annotations

import re
import sys
from pathlib import Path

_SCRIPTS = str(Path(__file__).resolve().parent.parent)
if _SCRIPTS not in sys.path:
    sys.path.insert(0, _SCRIPTS)

from _common import (  # noqa: E402
    detail_record, html_to_text, job_record, loads_or_empty, optional_import, slugify,
)

NAME = "indeed"
LAST_WARNINGS: list[str] = []
UNAVAILABLE_REASON = ""

COUNTRIES = {"MY": "malaysia", "SG": "singapore"}
CURRENCIES = {"MY": "MYR", "SG": "SGD"}
RESULTS_WANTED = 25
TEASER_CHARS = 300

_MISSING = {"", "nan", "none", "nat", "null", "<na>"}
_JK_RE = re.compile(r"[?&]jk=([^&]+)")


def _is_blank(value) -> bool:
    return value is None or str(value).strip().lower() in _MISSING


def _str(value) -> str:
    return "" if _is_blank(value) else str(value).strip()


def _int(value) -> int | None:
    if _is_blank(value):
        return None
    try:
        return int(float(value))
    except (TypeError, ValueError):
        return None


def _rows(raw) -> list[dict]:
    """Accept jobspy's DataFrame, a list of row dicts, or recorded JSON."""
    if raw is None:
        return []
    if hasattr(raw, "to_dict"):
        return raw.to_dict("records")
    if isinstance(raw, (bytes, str)):
        raw = loads_or_empty(raw)
    if isinstance(raw, dict):
        raw = raw.get("jobs") or raw.get("results") or []
    if not isinstance(raw, list):
        return []
    return [row for row in raw if isinstance(row, dict)]


def _job_id(row: dict) -> str:
    for candidate in (_str(row.get("id")), _str(row.get("job_id"))):
        if candidate:
            return candidate
    url = _str(row.get("job_url"))
    m = _JK_RE.search(url)
    if m:
        return m.group(1)
    return slugify(f"{_str(row.get('title'))} {_str(row.get('company'))}") or "unknown"


def _salary_label(low: int | None, high: int | None, currency: str, interval: str) -> str:
    unit = f" per {interval}" if interval else ""
    prefix = f"{currency} " if currency else ""
    if low and high and low != high:
        return f"{prefix}{low:,} - {high:,}{unit}"
    if low or high:
        return f"{prefix}{(low or high):,}{unit}"
    return ""


def parse_search(raw, *, country: str) -> list[dict]:
    country = (country or "").upper()
    jobs = []
    for row in _rows(raw):
        low, high = _int(row.get("min_amount")), _int(row.get("max_amount"))
        if low or high:
            currency = _str(row.get("currency")) or CURRENCIES.get(country, "")
        else:
            currency = ""
        teaser = html_to_text(_str(row.get("description")))[:TEASER_CHARS].strip()
        jobs.append(job_record(
            NAME, country,
            id=f"{NAME}:{_job_id(row)}",
            title=_str(row.get("title")),
            company=_str(row.get("company")),
            location=_str(row.get("location")),
            salary_min=low,
            salary_max=high,
            currency=currency,
            salary_label=_salary_label(low, high, currency, _str(row.get("interval"))),
            posted=_str(row.get("date_posted"))[:10],
            url=_str(row.get("job_url")),
            teaser=teaser,
        ))
    return jobs


def search(keywords: str, location: str, *, country: str, days: int | None = None,
           salary_min: int | None = None, pages: int = 1, fetch=None) -> list[dict]:
    """Scrape Indeed through jobspy. `fetch` is unused (jobspy owns its HTTP);
    never raises — missing package or scraper errors land in LAST_WARNINGS."""
    global UNAVAILABLE_REASON
    LAST_WARNINGS.clear()
    country = (country or "").upper()
    jobspy = optional_import("jobspy")
    if jobspy is None:
        UNAVAILABLE_REASON = "pip install python-jobspy"
        LAST_WARNINGS.append(f"{NAME}: jobspy not installed ({UNAVAILABLE_REASON})")
        return []
    UNAVAILABLE_REASON = ""
    kwargs = {
        "site_name": ["indeed"],
        "search_term": keywords,
        "location": location,
        "results_wanted": RESULTS_WANTED * max(1, pages),
        "country_indeed": COUNTRIES.get(country, "malaysia"),
    }
    if days:
        kwargs["hours_old"] = int(days) * 24
    try:
        frame = jobspy.scrape_jobs(**kwargs)
    except Exception as exc:  # jobspy raises whatever its scrapers raise
        LAST_WARNINGS.append(f"{NAME}: scrape failed ({exc.__class__.__name__}), stopped")
        return []
    jobs = parse_search(frame, country=country)
    if salary_min:
        jobs = [j for j in jobs if j["salary_max"] is None or j["salary_max"] >= salary_min]
    return jobs


def parse_detail(raw, *, country: str) -> dict:
    """Indeed rows already carry the full description; parse one row into a detail."""
    rows = _rows(raw)
    row = rows[0] if rows else {}
    return detail_record(
        description_md=html_to_text(_str(row.get("description"))),
        title=_str(row.get("title")),
        company=_str(row.get("company")),
        url=_str(row.get("job_url")),
        screening_questions=[],
    )


def detail(job_id: str, *, country: str, fetch=None) -> dict | None:
    """jobspy has no per-id endpoint: descriptions arrive with the search rows."""
    LAST_WARNINGS.clear()
    LAST_WARNINGS.append(f"{NAME}: no detail endpoint, use the search row for {job_id}")
    return None
