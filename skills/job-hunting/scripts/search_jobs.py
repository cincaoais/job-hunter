#!/usr/bin/env python3
"""Criteria-driven multi-board job search.

Reads search criteria from the workspace `profile.md` (§1–§3), queries the
board sources in `sources/`, drops stale postings, applies dealbreaker /
salary / must-have knockouts, dedupes against `seen-jobs.json` and prints a
ranked markdown table (or JSON).

  python3 search_jobs.py --markdown
  python3 search_jobs.py --keywords "backend engineer" --country MY --days 3
  python3 search_jobs.py --sources jobstreet,linkedin --pages 2 --json

Flags override the profile. Exit code is 0 even when nothing is found, 2 for
bad flags or missing keywords; network failures are reported as source
warnings, never as tracebacks.
"""
from __future__ import annotations

import argparse
import datetime
import json
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from _common import (  # noqa: E402
    loads_or_empty, slugify, today as today_iso, use_utf8_output, workspace_dir, write_table,
)

# Board priority: which board wins when the same posting shows up twice, and
# the last tie-break when ranking.
SOURCE_PRIORITY = ("jobstreet", "mcf", "linkedin", "hiredly", "indeed")
# Sources that only serve one market; everything else is tried for either.
SOURCE_COUNTRIES = {"mcf": {"SG"}, "hiredly": {"MY"}}
# Sources queried when neither the flags nor the profile name any.
DEFAULT_SOURCES = ("jobstreet", "mcf", "linkedin", "hiredly")
# Profile board names ("JobStreet MY") matched by substring.
BOARD_ALIASES = (
    ("jobstreet", "jobstreet"), ("linkedin", "linkedin"),
    ("mycareersfuture", "mcf"), ("mcf", "mcf"),
    ("hiredly", "hiredly"), ("indeed", "indeed"),
)

# The currency a floor with no stated currency is read in: the search market's.
MARKET_CURRENCY = {"MY": "MYR", "SG": "SGD"}
MISSING_MUST_HAVE = "missing must-have"
# The soft bucket can run into the hundreds on a broad query; the table is a
# digest, so only the top rows are printed (--json carries all of them).
NEEDS_LOOK_ROWS = 10
COLUMNS = ["#", "Posted", "Source", "Company", "Role", "Location / mode", "Salary", "Link"]

_FIELD_RE = re.compile(r"^\s*[-*]\s*\*\*(?P<label>[^*]+?)\*\*\s*:?\s*(?P<value>.*)$")
_SPLIT_RE = re.compile(r"[,;]")
_DATE_RE = re.compile(r"^(\d{4})-(\d{2})-(\d{2})$")
_NUM_RE = re.compile(r"(\d[\d,]*)\s*([kK])?")
_ANNUAL_RE = re.compile(r"per\s*(?:year|annum)|annually|annual|yearly|/\s*yr|\bp\.?\s?a\.?\b")
_MONTHLY_RE = re.compile(r"per\s*month|monthly|/\s*mo|\bp\.?\s?m\.?\b|a month")
_CURRENCY_RE = re.compile(r"\b(?:(rm|myr|ringgit)|(s\$|sg\$|sgd))(?![a-z])")
_WORD_RE = re.compile(r"[a-z0-9+#.]+")
# Pure category nouns: a dealbreaker that ends in one names a field rather
# than a phrase to find verbatim, so "gambling industry" must still catch
# "gambling platform". Only one tail is ever dropped, and only these words —
# "only", "work", "role(s)" and "job(s)" carry meaning ("commission-only
# roles" must not decay into bare "commission").
_CATEGORY_TAILS = {
    "industry", "industries", "sector", "sectors", "company", "companies",
    "firm", "firms", "business", "businesses", "space", "field",
}
# Words carried by must-have phrases that say nothing about a posting.
_STOPWORDS = {
    "a", "an", "and", "any", "are", "as", "at", "be", "but", "by", "for", "from",
    "have", "in", "is", "it", "its", "must", "no", "not", "of", "on", "or", "posting",
    "postings", "primarily", "role", "roles", "that", "the", "to", "with", "within",
}


# --- criteria ----------------------------------------------------------------

def _fields(profile_md: str) -> dict[str, str]:
    """Every `- **Label:** value` line of the profile, keyed by lowercased label.

    A value that is nothing but a template hint ("(e.g. ...)") or "TBD" counts
    as unset. First occurrence of a label wins.
    """
    out: dict[str, str] = {}
    for line in (profile_md or "").splitlines():
        m = _FIELD_RE.match(line)
        if not m:
            continue
        label = m.group("label").strip().rstrip(":").strip().lower()
        value = m.group("value").strip()
        if value.startswith("(") and value.endswith(")"):
            value = ""
        if value.lower() in {"tbd", "n/a", "none", "-", "—"}:
            value = ""
        out.setdefault(label, value)
    return out


def _split(value: str) -> list[str]:
    """Split a profile list value on commas/semicolons, dropping quotes."""
    parts = (p.strip().strip('"').strip("'").strip() for p in _SPLIT_RE.split(value or ""))
    return [p for p in parts if p]


def _country_of(value: str) -> str:
    """"Malaysia (KL); remote for Singapore firms" -> "MY" (first one named)."""
    text = (value or "").lower()
    hits = [(text.find(name), code)
            for name, code in (("singapore", "SG"), ("malaysia", "MY"))
            if text.find(name) >= 0]
    if hits:
        return min(hits)[1]
    letters = re.sub(r"[^a-z]", "", text)
    return letters[:2].upper()


def _salary_floor(value: str) -> int | None:
    """Monthly floor from a salary expectation line.

    The first number worth >= 1000 wins, so leading noise ("up to 8 months
    bonus") is skipped. A `k`/`K` suffix multiplies by 1000 ("RM9k" -> 9000),
    and a line that says per year / annual / p.a. / yr — and does not also say
    per month — is divided by 12 ("RM 120,000 per year" -> 10000).
    """
    text = (value or "").lower()
    annual = bool(_ANNUAL_RE.search(text)) and not _MONTHLY_RE.search(text)
    for raw, suffix in _NUM_RE.findall(text):
        n = int(raw.replace(",", "")) * (1000 if suffix else 1)
        if n >= 1000:
            return round(n / 12) if annual else n
    return None


def _salary_currency(value: str) -> str:
    """"RM 9,000" -> "MYR", "S$8k" -> "SGD"; "" when the line names no currency."""
    m = _CURRENCY_RE.search((value or "").lower())
    if not m:
        return ""
    return "MYR" if m.group(1) else "SGD"


def _boards(value: str) -> list[str]:
    """Profile board names -> known source names, in priority order."""
    found = []
    for token in _split(value.lower() if value else ""):
        for needle, name in BOARD_ALIASES:
            if needle in token and name not in found:
                found.append(name)
    if not found:
        return list(DEFAULT_SOURCES)
    return [name for name in SOURCE_PRIORITY if name in found]


def _location_of(value: str) -> str:
    """"Kuala Lumpur, Malaysia" -> "Kuala Lumpur" (boards want the city/state)."""
    loc = (value or "").strip()
    for country in ("malaysia", "singapore"):
        if loc.lower().endswith("," + country) or loc.lower().endswith(", " + country):
            loc = loc.rsplit(",", 1)[0].strip()
    return loc


def read_criteria(profile_md: str) -> dict:
    """Search criteria from a profile.md body (§1 location/market, §2, §3)."""
    f = _fields(profile_md)
    return {
        "keywords": _split(f.get("search keywords / title variants", "")),
        "location": _location_of(f.get("location", "")),
        "country": _country_of(f.get("job market / country i'm hunting in", "")) or "MY",
        "salary_min": _salary_floor(f.get("salary expectation", "")),
        "salary_currency": _salary_currency(f.get("salary expectation", "")),
        "must_have": _split(f.get("must-haves in a posting", "")),
        "dealbreakers": _split(f.get("dealbreakers (must avoid)", "")),
        "boards": _boards(f.get("job boards to search", "")),
    }


# --- knockouts ---------------------------------------------------------------

def _plural_tolerant(word: str) -> str:
    """`word` as a pattern that matches its singular and plural form.

    A dealbreaker is written either way ("commission-only roles" against a
    posting's "commission-only role"), so the last word of a phrase carries an
    optional "s". Words already ending in "ss" ("business") are left alone.
    """
    stem = word[:-1] if len(word) > 3 and word.endswith("s") and not word.endswith("ss") else word
    if stem.endswith("s"):
        return re.escape(stem)
    return re.escape(stem) + "s?"


def _phrase_re(phrase: str) -> re.Pattern | None:
    """A word-boundary regex for a dealbreaker phrase, or None if it is empty.

    Whitespace and hyphens are interchangeable so "6-day work week" also
    matches "6 day work week", and the final word matches either number.
    """
    words = _WORD_RE.findall(phrase.lower())
    if not words:
        return None
    parts = [re.escape(w) for w in words[:-1]] + [_plural_tolerant(words[-1])]
    return re.compile(r"\b" + r"[\s\-/]+".join(parts) + r"\b")


def _dealbreaker_res(phrase: str) -> list[re.Pattern]:
    """Patterns that count as a hit for one dealbreaker entry.

    The phrase itself, plus — at most once — the phrase without a trailing
    category noun, so "gambling industry" also catches "our online gambling
    platform" while "commission-only roles" stays a whole phrase and leaves a
    posting offering "base salary plus commission" alone.
    """
    words = _WORD_RE.findall(phrase.lower())
    variants = [words]
    if len(words) > 1 and words[-1] in _CATEGORY_TAILS:
        variants.append(words[:-1])
    out = []
    for variant in variants:
        pattern = _phrase_re(" ".join(variant))
        if pattern is not None:
            out.append(pattern)
    return out


def _must_have_tokens(phrases) -> set[str]:
    """Significant words of the must-have entries ("hybrid or remote" -> both)."""
    tokens = set()
    for phrase in phrases or []:
        for word in _WORD_RE.findall(str(phrase).lower()):
            if word not in _STOPWORDS and len(word) > 1:
                tokens.add(word)
    return tokens


def _floor_currency(criteria: dict) -> str:
    """The floor's currency: stated in the profile, else the search market's ("" if neither)."""
    stated = str(criteria.get("salary_currency") or "").upper()
    return stated or MARKET_CURRENCY.get(str(criteria.get("country") or "").upper(), "")


def _is_floor_comparable(job: dict, criteria: dict) -> bool:
    """True when the posting's pay is in the floor's currency.

    A posting without a currency counts when its market uses the floor's
    currency. A floor with no currency at all is compared with everything.
    """
    floor_currency = _floor_currency(criteria)
    if not floor_currency:
        return True
    currency = str(job.get("currency") or "").strip().upper()
    if currency:
        return currency == floor_currency
    return MARKET_CURRENCY.get(str(job.get("country") or "").upper()) == floor_currency


def knockout(job: dict, criteria: dict) -> str | None:
    """Why this posting is out, or None to keep it.

    Dealbreakers are matched against title + company + teaser, must-haves
    against title + teaser only (a must-have is about the work, not the
    employer). The salary floor only applies to pay in its own currency.
    "missing must-have" is soft: callers put those rows in a "needs a look"
    list instead of dropping them.
    """
    haystack = " ".join(str(job.get(k) or "") for k in ("title", "company", "teaser")).lower()
    for phrase in criteria.get("dealbreakers") or []:
        if any(p.search(haystack) for p in _dealbreaker_res(str(phrase))):
            return f"dealbreaker: {phrase}"

    floor = criteria.get("salary_min")
    top = job.get("salary_max")
    if (floor and isinstance(top, (int, float)) and top < floor
            and _is_floor_comparable(job, criteria)):
        return "salary below floor"

    tokens = _must_have_tokens(criteria.get("must_have"))
    if tokens:
        text = " ".join(str(job.get(k) or "") for k in ("title", "teaser")).lower()
        words = set(_WORD_RE.findall(text))
        if not (tokens & words):
            return MISSING_MUST_HAVE
    return None


# --- ranking and dedupe ------------------------------------------------------

def _priority(job: dict) -> int:
    source = str(job.get("source") or "")
    return SOURCE_PRIORITY.index(source) if source in SOURCE_PRIORITY else len(SOURCE_PRIORITY)


def _posted_date(job: dict) -> datetime.date | None:
    m = _DATE_RE.match(str(job.get("posted") or "")[:10])
    if not m:
        return None
    try:
        return datetime.date(*(int(g) for g in m.groups()))
    except ValueError:
        return None


def _freshness_key(job: dict) -> tuple:
    """Newest first; postings with no usable date sort last."""
    d = _posted_date(job)
    if d is None:
        return (1, 0, 0, 0)
    return (0, -d.year, -d.month, -d.day)


def rank(jobs: list[dict]) -> list[dict]:
    """Freshness desc, then salary_max desc (unknown last), then board priority."""
    out = sorted(jobs, key=_priority)
    out.sort(key=lambda j: (j.get("salary_max") is None, -(j.get("salary_max") or 0)))
    out.sort(key=_freshness_key)
    return out


def _pair_key(job: dict) -> str:
    return slugify(f"{job.get('company') or ''} {job.get('title') or ''}")


def dedupe(jobs: list[dict], seen: dict, *, today: str | None = None,
           keep_seen: bool = False) -> tuple[list[dict], dict]:
    """Collapse duplicates and drop postings seen on an earlier run.

    Duplicate ids and same-company-same-title pairs across boards collapse to
    one row (the highest-priority board wins). Returns the kept rows plus a
    copy of `seen` with `seen[id] = first_seen_date` for every row that was
    not already in it; the caller's dict is left alone.
    """
    stamp = today or today_iso()
    updated = dict(seen or {})
    ids: set[str] = set()
    pairs: set[str] = set()
    out: list[dict] = []
    for job in sorted(jobs, key=_priority):
        job_id = str(job.get("id") or "")
        pair = _pair_key(job)
        if (job_id and job_id in ids) or (pair and pair in pairs):
            continue
        if job_id:
            ids.add(job_id)
        if pair:
            pairs.add(pair)
        already = job_id in updated
        if job_id:
            updated.setdefault(job_id, stamp)
        if already and not keep_seen:
            continue
        out.append(job)
    return out, updated


# --- gathering ---------------------------------------------------------------

def _source_skip(name: str, country: str) -> str:
    markets = SOURCE_COUNTRIES.get(name)
    if markets and country not in markets:
        return f"{'/'.join(sorted(markets))} only"
    return ""


def _gather(criteria: dict, sources: dict) -> tuple[list[dict], dict]:
    """Query every source for every keyword; collect jobs plus per-source stats.

    A source that warns (HTTP error, rate limit) is not queried again for the
    remaining keywords, and one that raises is reported instead of crashing
    the run.
    """
    country = str(criteria.get("country") or "").upper()
    keywords = [k for k in (criteria.get("keywords") or []) if str(k).strip()] or [""]
    # A board filters on the bare number, so a floor in another currency stays local.
    salary_min = (criteria.get("salary_min")
                  if _floor_currency(criteria) in ("", MARKET_CURRENCY.get(country, "")) else None)
    jobs: list[dict] = []
    stats: dict[str, dict] = {}
    for name in sorted(sources, key=lambda n: (_priority({"source": n}), n)):
        module = sources[name]
        stat = {"count": 0, "warnings": [], "skipped": ""}
        stats[name] = stat
        stat["skipped"] = _source_skip(name, country)
        if stat["skipped"]:
            continue
        for keyword in keywords:
            try:
                found = module.search(
                    keyword, criteria.get("location") or "", country=country,
                    days=criteria.get("days"), salary_min=salary_min,
                    pages=int(criteria.get("pages") or 1),
                )
            except ValueError as exc:
                problem = (f"unsupported country {country or '(none)'}"
                           if "unsupported country" in str(exc) else "search failed (ValueError)")
                stat["warnings"].append(f"{name}: {problem}")
                break
            except Exception as exc:  # a source must never take the run down
                stat["warnings"].append(f"{name}: search failed ({exc.__class__.__name__})")
                break
            warnings = list(getattr(module, "LAST_WARNINGS", []) or [])
            for warning in warnings:
                if warning not in stat["warnings"]:
                    stat["warnings"].append(warning)
            rows = [j for j in (found or []) if isinstance(j, dict)]
            stat["count"] += len(rows)
            jobs.extend(rows)
            reason = str(getattr(module, "UNAVAILABLE_REASON", "") or "")
            if reason:
                stat["skipped"] = reason
                stat["warnings"] = []
                break
            if warnings:
                break
    return jobs, stats


def _is_fresh(job: dict, days, today: str) -> bool:
    """Within the freshness window; an undated posting counts as fresh."""
    if not days:
        return True
    posted = _posted_date(job)
    if posted is None:
        return True
    try:
        cutoff = datetime.date.fromisoformat(today) - datetime.timedelta(days=int(days))
    except (TypeError, ValueError):
        return True
    return posted >= cutoff


def run(criteria: dict, *, sources: dict, seen: dict, today: str | None = None,
        all_: bool = False) -> dict:
    """Search every source and split the results into new / needs-look / out.

    Pure apart from the injected source modules: `sources` maps a name to
    anything with the `search()` signature, so tests use stubs.
    """
    stamp = today or today_iso()
    raw, stats = _gather(criteria, sources)
    fresh = [j for j in raw if _is_fresh(j, criteria.get("days"), stamp)]

    # Rows are marked by object identity: dedupe/rank pass the same dicts
    # through, and nothing is written into the records themselves.
    soft_rows: set[int] = set()
    knocked: list[tuple[dict, str]] = []
    kept: list[dict] = []
    for job in fresh:
        reason = knockout(job, criteria)
        if reason is None:
            kept.append(job)
        elif reason == MISSING_MUST_HAVE:
            soft_rows.add(id(job))
            kept.append(job)
        else:
            knocked.append((job, reason))

    known = set(seen or {})
    kept_ids = {str(j.get("id") or "") for j in kept}
    # Only the rows that survived the knockouts are deduped, so a knocked-out
    # posting is never written to `seen` and is re-evaluated on the next run
    # once the profile's dealbreakers or salary floor change.
    survivors, updated = dedupe(kept, seen or {}, today=stamp, keep_seen=all_)
    ranked = rank(survivors)
    new = [j for j in ranked if id(j) not in soft_rows]
    needs_look = [j for j in ranked if id(j) in soft_rows]
    return {
        "new": new,
        "needs_look": needs_look,
        "knocked_out": [[job, reason] for job, reason in knocked],
        "sources": stats,
        "seen": updated,
        "seen_before": len(kept_ids & known),
    }


# --- output ------------------------------------------------------------------

def _salary_cell(job: dict) -> str:
    label = str(job.get("salary_label") or "").strip()
    if label:
        return label
    low, high = job.get("salary_min"), job.get("salary_max")
    currency = str(job.get("currency") or "").strip()
    if not low and not high:
        return "—"
    if low and high and low != high:
        body = f"{low:,} - {high:,}"
    else:
        body = f"{(low or high):,}"
    return f"{currency} {body}".strip()


def _row(index: int, job: dict) -> dict:
    where = str(job.get("location") or "").strip()
    mode = str(job.get("mode") or "").strip()
    url = str(job.get("url") or "").strip()
    return {
        "#": index,
        "Posted": str(job.get("posted") or "").strip() or "—",
        "Source": job.get("source") or "",
        "Company": job.get("company") or "",
        "Role": job.get("title") or "",
        "Location / mode": " · ".join(p for p in (where, mode) if p) or "—",
        "Salary": _salary_cell(job),
        "Link": f"[open]({url})" if url else "—",
    }


def _table(jobs: list[dict]) -> str:
    rows = [_row(i, job) for i, job in enumerate(jobs, 1)]
    return write_table("", COLUMNS, rows).rstrip("\n")


def _sources_line(sources: dict | None) -> str:
    """"Sources: jobstreet 42 · indeed skipped: pip install python-jobspy"."""
    parts = []
    for name in sorted(sources or {}, key=lambda n: (_priority({"source": n}), n)):
        stat = (sources or {}).get(name) or {}
        skipped = str(stat.get("skipped") or "")
        if skipped:
            parts.append(f"{name} skipped: {skipped}")
            continue
        text = f"{name} {stat.get('count', 0)}"
        warnings = [re.sub(rf"^{re.escape(name)}:\s*", "", w) for w in stat.get("warnings") or []]
        if warnings:
            text += " (" + "; ".join(warnings) + ")"
        parts.append(text)
    return "Sources: " + (" · ".join(parts) if parts else "none")


def render_markdown(jobs: list[dict], knocked: list, *, needs_look=(), sources=None,
                    seen_before: int = 0) -> str:
    """The shortlist: headline, ranked table, needs-a-look, knockouts, sources."""
    needs_look = list(needs_look or [])
    knocked = list(knocked or [])
    count = len(jobs)
    noun = "posting" if count == 1 else "postings"
    headline = f"{count} new {noun}" if count else "0 new since last run"
    tail = (f"{len(knocked)} knocked out, {len(needs_look)} needs a look, "
            f"{seen_before} seen before")
    out = [f"## {headline} ({tail})", ""]
    if jobs:
        out += [_table(jobs), ""]
    if needs_look:
        shown = needs_look[:NEEDS_LOOK_ROWS]
        out += ["### Needs a look", "",
                "Missing every must-have from the profile — check before skipping.", "",
                _table(shown), ""]
        if len(needs_look) > len(shown):
            out += [f"… and {len(needs_look) - len(shown)} more (--json for the rest).", ""]
    if knocked:
        out += ["### Knocked out", ""]
        for job, reason in knocked:
            company = str(job.get("company") or "?")
            title = str(job.get("title") or "?")
            out.append(f"- {company} — {title}: {reason}")
        out.append("")
    out.append(_sources_line(sources))
    return "\n".join(out) + "\n"


# --- CLI ---------------------------------------------------------------------

def default_sources(country: str) -> list[str]:
    """The default board list for a market (Indeed only when asked for)."""
    c = (country or "").upper()
    return [n for n in DEFAULT_SOURCES if not _source_skip(n, c)]


def get_sources(names) -> dict:
    """Import the named source modules; unknown or broken imports are skipped."""
    mods = {}
    for name in names:
        if name not in SOURCE_PRIORITY:
            continue
        try:
            mods[name] = __import__(f"sources.{name}", fromlist=[name])
        except Exception as exc:  # a broken module must not stop the search
            print(f"warning: source {name} failed to import ({exc.__class__.__name__})",
                  file=sys.stderr)
    return mods


def build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(
        prog="search_jobs.py", description="Search the job boards with the profile's criteria.")
    p.add_argument("--keywords", help="comma-separated title variants (overrides profile)")
    p.add_argument("--location", help="city or state to search in")
    p.add_argument("--country", choices=["MY", "SG", "my", "sg"], help="job market")
    p.add_argument("--days", type=int, help="only postings this fresh")
    p.add_argument("--salary-min", type=int, dest="salary_min",
                   help="monthly salary floor, in the market's currency")
    p.add_argument("--sources", help=f"comma-separated: {','.join(SOURCE_PRIORITY)}")
    p.add_argument("--pages", type=int, default=1, help="pages per board (default 1)")
    p.add_argument("--all", action="store_true", dest="all_",
                   help="include postings already in seen-jobs.json")
    p.add_argument("--no-seen", action="store_true", dest="no_seen",
                   help="do not write seen-jobs.json")
    out = p.add_mutually_exclusive_group()
    out.add_argument("--markdown", action="store_true", help="markdown output (default)")
    out.add_argument("--json", action="store_true", dest="as_json", help="JSON output")
    return p


def _criteria_from(args, profile_md: str) -> dict:
    criteria = read_criteria(profile_md)
    if args.keywords:
        criteria["keywords"] = _split(args.keywords)
    if args.location:
        criteria["location"] = args.location.strip()
    if args.country:
        criteria["country"] = args.country.upper()
    if args.salary_min is not None:
        criteria["salary_min"] = args.salary_min
        criteria["salary_currency"] = ""  # a bare number: the market's currency
    criteria["days"] = args.days
    criteria["pages"] = max(1, args.pages or 1)
    return criteria


def main(argv=None) -> int:
    use_utf8_output()
    parser = build_parser()
    args = parser.parse_args(argv)

    ws = workspace_dir()
    profile = ws / "profile.md"
    profile_md = profile.read_text(encoding="utf-8") if profile.exists() else ""
    criteria = _criteria_from(args, profile_md)

    if not criteria["keywords"]:
        print(f"No search keywords. Fill '§2 Search keywords / title variants' in "
              f"{profile} or pass --keywords \"backend engineer\".", file=sys.stderr)
        return 2

    if args.sources:
        names = [n.strip().lower() for n in _SPLIT_RE.split(args.sources) if n.strip()]
        unknown = [n for n in names if n not in SOURCE_PRIORITY]
        if unknown:
            parser.error(f"unknown source(s): {', '.join(unknown)} "
                         f"(known: {', '.join(SOURCE_PRIORITY)})")
    else:
        names = [n for n in criteria["boards"] if not _source_skip(n, criteria["country"])]
        names = names or default_sources(criteria["country"])

    seen_path = ws / "seen-jobs.json"
    seen = loads_or_empty(seen_path.read_text(encoding="utf-8")) if seen_path.exists() else {}
    if not isinstance(seen, dict):
        seen = {}

    result = run(criteria, sources=get_sources(names), seen=seen, all_=args.all_)

    if args.as_json:
        print(json.dumps({k: result[k] for k in ("new", "needs_look", "knocked_out", "sources")},
                         indent=2))
    else:
        print(render_markdown(result["new"], result["knocked_out"],
                              needs_look=result["needs_look"], sources=result["sources"],
                              seen_before=result["seen_before"]), end="")

    if not args.no_seen and ws.exists():
        seen_path.write_text(json.dumps(result["seen"], indent=2, sort_keys=True) + "\n",
                             encoding="utf-8")
    return 0


if __name__ == "__main__":
    sys.exit(main())
