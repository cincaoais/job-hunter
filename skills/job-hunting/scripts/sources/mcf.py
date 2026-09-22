#!/usr/bin/env python3
"""MyCareersFuture (Singapore government job bank).

Search is a POST to the public v2 search API, detail a GET per job uuid.
Singapore only.
"""
from __future__ import annotations

import sys
from pathlib import Path

_SCRIPTS = str(Path(__file__).resolve().parent.parent)
if _SCRIPTS not in sys.path:
    sys.path.insert(0, _SCRIPTS)

from _common import (  # noqa: E402
    default_fetch, detail_record, dict_at, finish_detail, html_to_text, job_record,
    loads_or_empty, rows_of,
)

NAME = "mcf"
LAST_WARNINGS: list[str] = []

API = "https://api.mycareersfuture.gov.sg/v2"
SITE = "https://www.mycareersfuture.gov.sg"
COUNTRY = "SG"
CURRENCY = "SGD"
PAGE_SIZE = 20


def _country(country: str) -> str:
    c = (country or "").upper()
    if c != COUNTRY:
        raise ValueError(f"mcf: unsupported country {country!r} (Singapore only)")
    return c


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


def _location(row: dict) -> str:
    """The first listed district; every MCF job is in Singapore, so that is
    the fallback — but an empty payload stays empty rather than claiming one."""
    districts = rows_of(dict_at(row, "address"), "districts")
    first = dict_at(districts[0] if districts else None)
    named = str(first.get("location") or "").strip()
    return named or ("Singapore" if row else "")


def _mode(row: dict) -> str:
    text = " ".join(str(a) for a in rows_of(row, "flexibleWorkArrangements")).lower()
    if "remote" in text or "telecommut" in text or "work from home" in text:
        return "Remote"
    if "hybrid" in text:
        return "Hybrid"
    return ""


def _teaser(row: dict) -> str:
    bits = [dict_at(p).get("position", "") for p in rows_of(row, "positionLevels")]
    bits += [dict_at(e).get("employmentType", "") for e in rows_of(row, "employmentTypes")]
    return " · ".join(str(b).strip() for b in bits if b and str(b).strip())


def _screening_questions(raw_questions) -> list[str]:
    out = []
    for q in (raw_questions if isinstance(raw_questions, list) else []):
        if isinstance(q, str):
            text = q
        elif isinstance(q, dict):
            text = str(q.get("question") or q.get("text") or q.get("title") or "")
        else:
            continue  # numbers, nulls: nothing a human would read back
        text = text.strip()
        if text:
            out.append(text)
    return out


def parse_search(raw: bytes | str, *, country: str) -> list[dict]:
    country = _country(country)
    jobs = []
    for row in rows_of(loads_or_empty(raw), "results"):
        if not isinstance(row, dict):
            continue
        uuid = str(row.get("uuid") or "").strip()
        if not uuid:
            continue
        meta = dict_at(row, "metadata")
        salary = dict_at(row, "salary")
        low, high = _int(salary.get("minimum")), _int(salary.get("maximum"))
        jobs.append(job_record(
            NAME, country,
            id=f"{NAME}:{uuid}",
            title=str(row.get("title") or "").strip(),
            company=str(dict_at(row, "postedCompany").get("name") or "").strip(),
            location=_location(row),
            mode=_mode(row),
            salary_min=low,
            salary_max=high,
            currency=CURRENCY,
            salary_label=_salary_label(low, high),
            posted=str(meta.get("newPostingDate") or "")[:10],
            url=str(meta.get("jobDetailsUrl") or "") or f"{SITE}/job/{uuid}",
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
    job = dict_at(loads_or_empty(raw))
    uuid = str(job.get("uuid") or "").strip()
    meta = dict_at(job, "metadata")
    url = str(meta.get("jobDetailsUrl") or "") or (f"{SITE}/job/{uuid}" if uuid else "")
    salary = dict_at(job, "salary")
    return detail_record(
        description_md=html_to_text(str(job.get("description") or "")),
        title=str(job.get("title") or "").strip(),
        company=str(dict_at(job, "postedCompany").get("name") or "").strip(),
        url=url,
        screening_questions=_screening_questions(job.get("screeningQuestions")),
        location=_location(job),
        salary_label=_salary_label(_int(salary.get("minimum")), _int(salary.get("maximum"))),
        posted=str(meta.get("newPostingDate") or "")[:10],
    )


def detail(job_id: str, *, country: str, fetch=None) -> dict | None:
    """`job_id` is the MCF uuid; None when the request or job is missing."""
    LAST_WARNINGS.clear()
    fetch = fetch or default_fetch
    status, body = fetch(f"{API}/jobs/{job_id}", None, "GET", None)
    if status != 200:
        LAST_WARNINGS.append(f"{NAME}: HTTP {status} for job {job_id}")
        return None
    return finish_detail(parse_detail(body, country=COUNTRY))
