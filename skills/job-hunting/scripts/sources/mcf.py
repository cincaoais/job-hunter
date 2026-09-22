#!/usr/bin/env python3
"""MyCareersFuture (Singapore government job bank).

Search is a POST to the public v2 search API, detail a GET per job uuid.
Singapore only.
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

_SCRIPTS = str(Path(__file__).resolve().parent.parent)
if _SCRIPTS not in sys.path:
    sys.path.insert(0, _SCRIPTS)

from _common import default_fetch, detail_record, html_to_text, job_record  # noqa: E402

NAME = "mcf"
LAST_WARNINGS: list[str] = []

API = "https://api.mycareersfuture.gov.sg/v2"
COUNTRY = "SG"
CURRENCY = "SGD"
PAGE_SIZE = 20


def _country(country: str) -> str:
    c = (country or "").upper()
    if c != COUNTRY:
        raise ValueError(f"mcf: unsupported country {country!r} (Singapore only)")
    return c


def _loads(raw: bytes | str):
    if isinstance(raw, bytes):
        raw = raw.decode("utf-8", "replace")
    try:
        return json.loads(raw)
    except (ValueError, TypeError):
        return {}


def _int(value) -> int | None:
    try:
        return int(value)
    except (TypeError, ValueError):
        return None


def _salary_label(low: int | None, high: int | None) -> str:
    if low and high:
        return f"{CURRENCY} {low:,} - {high:,} per month"
    if low or high:
        return f"{CURRENCY} {(low or high):,} per month"
    return ""


def _mode(row: dict) -> str:
    text = " ".join(str(a) for a in (row.get("flexibleWorkArrangements") or [])).lower()
    if "remote" in text or "telecommut" in text or "work from home" in text:
        return "Remote"
    if "hybrid" in text:
        return "Hybrid"
    return ""


def _teaser(row: dict) -> str:
    bits = [p.get("position", "") for p in (row.get("positionLevels") or [])]
    bits += [e.get("employmentType", "") for e in (row.get("employmentTypes") or [])]
    return " · ".join(b.strip() for b in bits if b and b.strip())


def _screening_questions(raw_questions) -> list[str]:
    out = []
    for q in raw_questions or []:
        if isinstance(q, str):
            text = q
        elif isinstance(q, dict):
            text = q.get("question") or q.get("text") or q.get("title") or ""
        else:
            text = str(q)
        text = text.strip()
        if text:
            out.append(text)
    return out


def parse_search(raw: bytes | str, *, country: str) -> list[dict]:
    country = _country(country)
    data = _loads(raw)
    jobs = []
    for row in data.get("results") or []:
        uuid = str(row.get("uuid") or "").strip()
        if not uuid:
            continue
        meta = row.get("metadata") or {}
        salary = row.get("salary") or {}
        low, high = _int(salary.get("minimum")), _int(salary.get("maximum"))
        districts = (row.get("address") or {}).get("districts") or []
        location = (districts[0].get("location") if districts else "") or "Singapore"
        jobs.append(job_record(
            NAME, country,
            id=f"{NAME}:{uuid}",
            title=(row.get("title") or "").strip(),
            company=((row.get("postedCompany") or {}).get("name") or "").strip(),
            location=location.strip(),
            mode=_mode(row),
            salary_min=low,
            salary_max=high,
            currency=CURRENCY,
            salary_label=_salary_label(low, high),
            posted=(meta.get("newPostingDate") or "")[:10],
            url=(meta.get("jobDetailsUrl") or f"https://www.mycareersfuture.gov.sg/job/{uuid}"),
            teaser=_teaser(row),
            applicants=_int(meta.get("totalNumberJobApplication")),
        ))
    return jobs


def search(keywords: str, location: str, *, country: str, days: int | None = None,
           salary_min: int | None = None, pages: int = 1, fetch=None) -> list[dict]:
    """Search MyCareersFuture. `location`/`days` are not query parameters there,
    so they are ignored; never raises on HTTP failure (see LAST_WARNINGS)."""
    LAST_WARNINGS.clear()
    country = _country(country)
    fetch = fetch or default_fetch
    payload = {"search": keywords, "sortBy": ["new_posting_date"]}
    if salary_min:
        payload["salary"] = salary_min
    jobs: list[dict] = []
    for page in range(max(1, pages)):
        url = f"{API}/search?limit={PAGE_SIZE}&page={page}"
        status, body = fetch(url, None, "POST", payload)
        if status != 200:
            LAST_WARNINGS.append(f"{NAME}: HTTP {status} at page {page}, stopped")
            break
        page_jobs = parse_search(body, country=country)
        jobs.extend(page_jobs)
        if len(page_jobs) < PAGE_SIZE:
            break
    return jobs


def parse_detail(raw: bytes | str, *, country: str = COUNTRY) -> dict:
    """Parse a v2 job detail payload. MCF is Singapore-only; `country` is unused."""
    job = _loads(raw)
    uuid = str(job.get("uuid") or "").strip()
    meta = job.get("metadata") or {}
    url = meta.get("jobDetailsUrl") or (
        f"https://www.mycareersfuture.gov.sg/job/{uuid}" if uuid else "")
    return detail_record(
        description_md=html_to_text(job.get("description") or ""),
        title=(job.get("title") or "").strip(),
        company=((job.get("postedCompany") or {}).get("name") or "").strip(),
        url=url,
        screening_questions=_screening_questions(job.get("screeningQuestions")),
    )


def detail(job_id: str, *, country: str, fetch=None) -> dict | None:
    """`job_id` is the MCF uuid; None when the request or job is missing."""
    fetch = fetch or default_fetch
    status, body = fetch(f"{API}/jobs/{job_id}", None, "GET", None)
    if status != 200:
        LAST_WARNINGS.append(f"{NAME}: HTTP {status} for job {job_id}")
        return None
    got = parse_detail(body, country=COUNTRY)
    return got if got["description_md"] or got["title"] else None
