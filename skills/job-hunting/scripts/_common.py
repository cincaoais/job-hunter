#!/usr/bin/env python3
"""Shared helpers for the job-hunting skill scripts.

Stdlib only (Python 3.10+), no third-party dependencies. Kept small and
dependency-free so every script under skills/job-hunting/scripts/ can import
it without a virtualenv.
"""
from __future__ import annotations

import datetime
import html as html_mod
import http.client
import importlib
import json
import os
import re
import ssl
import time
import urllib.error
import urllib.request
from pathlib import Path
from urllib.parse import urlparse

UA = "job-hunter-skill/6.0 (+https://github.com/cincaoais/job-hunter)"


def workspace_dir() -> Path:
    """Resolve the job-hunt workspace directory.

    Precedence: $JOB_HUNT_DIR env var -> ./job-hunt (if it already exists) ->
    ~/job-hunt.
    """
    env = os.environ.get("JOB_HUNT_DIR")
    if env:
        return Path(env)
    local = Path.cwd() / "job-hunt"
    if local.exists():
        return local
    return Path.home() / "job-hunt"


def slugify(s: str) -> str:
    """Lowercase, collapse anything that isn't a-z0-9 into single hyphens."""
    s = s.lower()
    s = re.sub(r"[^a-z0-9]+", "-", s)
    return s.strip("-")


def optional_import(name: str):
    """Import `name` if available, else return None (no hard dependency)."""
    try:
        return importlib.import_module(name)
    except ImportError:
        return None


# --- HTTP helpers -----------------------------------------------------------

_last_call: dict[str, float] = {}


def _rate_limit(url: str) -> None:
    """Sleep as needed so a given host gets at most one request per second."""
    host = urlparse(url).netloc
    now = time.monotonic()
    last = _last_call.get(host, 0.0)
    wait = 1.0 - (now - last)
    if wait > 0:
        time.sleep(wait)
    _last_call[host] = time.monotonic()


def _ssl_context() -> ssl.SSLContext:
    """A verifying TLS context, using certifi's CA bundle when it is installed.

    python.org builds ship without a system CA bundle, so plain
    `create_default_context()` fails with CERTIFICATE_VERIFY_FAILED there.
    Verification is never disabled: without certifi we still return the
    default verifying context.
    """
    certifi = optional_import("certifi")
    if certifi is not None:
        return ssl.create_default_context(cafile=certifi.where())
    return ssl.create_default_context()


def _send(req, timeout: int) -> tuple[int, bytes]:
    """Send `req`, turning every transport failure into (0, message)."""
    try:
        with urllib.request.urlopen(req, timeout=timeout, context=_ssl_context()) as resp:
            return resp.status, resp.read()
    except urllib.error.HTTPError as e:
        return e.code, e.read()
    except urllib.error.URLError as e:
        return 0, str(e).encode()
    except http.client.HTTPException as e:
        return 0, f"{e.__class__.__name__}: {e}".encode()
    except OSError as e:
        # timeouts and dropped connections during getresponse()/read()
        return 0, f"{e.__class__.__name__}: {e}".encode()


def http_get(url, headers=None, timeout=20) -> tuple[int, bytes]:
    _rate_limit(url)
    hdrs = {"User-Agent": UA}
    if headers:
        hdrs.update(headers)
    return _send(urllib.request.Request(url, headers=hdrs), timeout)


def http_post_json(url, payload, headers=None, timeout=20) -> tuple[int, bytes]:
    _rate_limit(url)
    hdrs = {"User-Agent": UA, "Content-Type": "application/json"}
    if headers:
        hdrs.update(headers)
    data = json.dumps(payload).encode("utf-8")
    return _send(urllib.request.Request(url, data=data, headers=hdrs, method="POST"), timeout)


def default_fetch(url, headers=None, method="GET", payload=None) -> tuple[int, bytes]:
    """The injectable-fetch shape the board sources use by default."""
    if method.upper() == "POST":
        return http_post_json(url, payload or {}, headers=headers)
    return http_get(url, headers=headers)


# --- HTML -> text ------------------------------------------------------------

_DROP_RE = re.compile(r"<(script|style)\b.*?</\1\s*>", re.S | re.I)
_LI_RE = re.compile(r"<\s*li[^>]*>\s*", re.I)
_BREAK_RE = re.compile(
    r"<\s*br\s*/?>"
    r"|<\s*/\s*(?:p|div|li|ul|ol|tr|table|section|blockquote|h[1-6])\s*>"
    r"|<\s*(?:p|h[1-6])[^>]*>",
    re.I,
)
_TAG_RE = re.compile(r"<[^>]*>")


def html_to_text(html: str) -> str:
    """Flatten a job-description HTML blob into readable markdown-ish text.

    `<li>` becomes "- ", block ends and `<br>` become newlines, every other
    tag is dropped, entities are unescaped and runs of blank lines collapse
    to one.
    """
    if not html:
        return ""
    s = _DROP_RE.sub("", html)
    s = _LI_RE.sub("\n- ", s)
    s = _BREAK_RE.sub("\n", s)
    s = _TAG_RE.sub("", s)
    s = html_mod.unescape(s)
    s = s.replace(" ", " ").replace("\r\n", "\n").replace("\r", "\n")
    s = "\n".join(re.sub(r"[ \t]+", " ", line).strip() for line in s.split("\n"))
    return re.sub(r"\n{3,}", "\n\n", s).strip()


# --- Parsing helpers shared by the board sources -----------------------------

_FIRST_INTS_RE = re.compile(r"\d[\d,]*")


def first_two_ints(label: str) -> tuple[int | None, int | None]:
    """First two integers in `label` as (min, max).

    One number means both bounds; no digits at all means (None, None). Used
    for the boards' free-text salary labels.
    """
    nums = [int(n.replace(",", "")) for n in _FIRST_INTS_RE.findall(label or "")]
    if not nums:
        return None, None
    if len(nums) == 1:
        return nums[0], nums[0]
    return nums[0], nums[1]


def loads_or_empty(raw: bytes | str):
    """Decode JSON from bytes or str, returning {} for anything unparseable."""
    if isinstance(raw, bytes):
        raw = raw.decode("utf-8", "replace")
    try:
        return json.loads(raw)
    except (ValueError, TypeError):
        return {}


def dict_at(container, *keys) -> dict:
    """Walk nested dict keys, returning {} as soon as anything is not a dict."""
    current = container
    for key in keys:
        if not isinstance(current, dict):
            return {}
        current = current.get(key)
    return current if isinstance(current, dict) else {}


def rows_of(container, key: str) -> list:
    """`container[key]` when it is a list, else [] — payload-shape guard."""
    if not isinstance(container, dict):
        return []
    rows = container.get(key)
    return rows if isinstance(rows, list) else []


# --- Normalized records shared by the board sources --------------------------

JOB_KEYS = (
    "id", "source", "title", "company", "location", "mode",
    "salary_min", "salary_max", "currency", "salary_label",
    "posted", "url", "teaser", "applicants", "country",
)
DETAIL_KEYS = ("description_md", "title", "company", "url", "screening_questions")


def job_record(source: str, country: str, **fields) -> dict:
    """A normalized job dict with every key present ("" / None when unknown)."""
    rec = dict.fromkeys(JOB_KEYS, "")
    rec.update(source=source, country=country, salary_min=None, salary_max=None, applicants=None)
    unknown = sorted(set(fields) - set(JOB_KEYS))
    if unknown:
        raise KeyError(f"unknown job fields: {unknown}")
    rec.update(fields)
    return rec


def detail_record(**fields) -> dict:
    """A normalized job-detail dict with every key present."""
    rec = dict.fromkeys(DETAIL_KEYS, "")
    rec["screening_questions"] = []
    unknown = sorted(set(fields) - set(DETAIL_KEYS))
    if unknown:
        raise KeyError(f"unknown detail fields: {unknown}")
    rec.update(fields)
    return rec


def finish_detail(got: dict) -> dict | None:
    """A parsed detail is only worth returning if it found a description or title."""
    return got if got["description_md"] or got["title"] else None


# --- Markdown table helpers --------------------------------------------------

_SEP_RE = re.compile(r"^\|?\s*:?-{3,}")


def _is_separator_line(line: str) -> bool:
    s = line.strip()
    if not s or not _SEP_RE.match(s):
        return False
    return all(ch in "|-: \t" for ch in s)


_UNESCAPED_PIPE_RE = re.compile(r"(?<!\\)\|")


def _split_row(line: str) -> list[str]:
    s = line.strip()
    if s.startswith("|"):
        s = s[1:]
    if s.endswith("|"):
        s = s[:-1]
    return [cell.strip().replace("\\|", "|") for cell in _UNESCAPED_PIPE_RE.split(s)]


def _section_bounds(lines: list[str], heading: str | None):
    """Return (start, end) exclusive-end bounds to search within.

    With no heading, that's the whole document. With a heading, it's the
    lines strictly between that heading line and the next line starting with
    `#` (any level) — or the end of the document if there is none. Returns
    None if `heading` is given but not found anywhere in `lines`.
    """
    if heading is None:
        return 0, len(lines)
    for i, line in enumerate(lines):
        if line.strip() == heading:
            start = i + 1
            break
    else:
        return None
    end = len(lines)
    for j in range(start, len(lines)):
        if lines[j].lstrip().startswith("#"):
            end = j
            break
    return start, end


def _find_table(lines: list[str], heading: str | None):
    """Return (start_idx, end_idx_inclusive) of the header row through the
    last consecutive body row, or None if no matching table is found.

    When `heading` is given, the search is bounded to that heading's own
    section (up to, but not including, the next heading line) so a table
    under a later heading is never mistaken for the one being looked up.
    """
    bounds = _section_bounds(lines, heading)
    if bounds is None:
        return None
    start_search, limit = bounds
    for i in range(start_search, limit - 1):
        if lines[i].lstrip().startswith("|") and _is_separator_line(lines[i + 1]):
            j = i + 2
            while j < limit and lines[j].lstrip().startswith("|"):
                j += 1
            return i, j - 1
    return None


def read_table(md: str, heading: str | None = None) -> tuple[list[str], list[dict]]:
    """Read the first markdown table in `md` (or the one under `heading`)."""
    lines = md.splitlines()
    found = _find_table(lines, heading)
    if not found:
        return [], []
    start, end = found
    columns = _split_row(lines[start])
    rows = []
    for line in lines[start + 2 : end + 1]:
        cells = _split_row(line)
        rows.append({col: (cells[idx] if idx < len(cells) else "") for idx, col in enumerate(columns)})
    return columns, rows


def _render_table(columns: list[str], rows: list[dict]) -> list[str]:
    def esc(v) -> str:
        return str(v).replace("|", "\\|").replace("\n", " ")

    lines = ["| " + " | ".join(columns) + " |", "|" + "|".join(["---"] * len(columns)) + "|"]
    for row in rows:
        cells = [esc(row.get(col, "")) for col in columns]
        lines.append("| " + " | ".join(cells) + " |")
    return lines


def write_table(md: str, columns: list[str], rows: list[dict], heading: str | None = None) -> str:
    """Replace the table found by read_table's rules with a rendered one.

    If no such table exists: with a `heading` that is present in `md`, the
    new table is inserted at the end of that heading's section (before the
    next heading), separated by blank lines, leaving the rest of the
    document untouched. With a `heading` not present in `md`, a new
    `## heading` section is appended at the end. With no `heading`, the
    table is simply appended at the end.
    """
    lines = md.splitlines()
    found = _find_table(lines, heading)
    table_lines = _render_table(columns, rows)
    if found:
        start, end = found
        new_lines = lines[:start] + table_lines + lines[end + 1 :]
        out = "\n".join(new_lines)
        if md.endswith("\n"):
            out += "\n"
        return out

    bounds = _section_bounds(lines, heading) if heading is not None else None
    if heading is not None and bounds is not None:
        start, limit = bounds
        section = lines[start:limit]
        while section and section[-1].strip() == "":
            section.pop()
        new_section = section + [""] + table_lines
        new_lines = lines[:start] + new_section
        tail = lines[limit:]
        new_lines += ([""] + tail) if tail else tail
        out = "\n".join(new_lines)
        if md.endswith("\n"):
            out += "\n"
        return out

    block = ([f"## {heading}", ""] if heading is not None else []) + table_lines
    out = md.rstrip("\n")
    if out:
        out += "\n\n"
    return out + "\n".join(block) + "\n"


def today() -> str:
    return datetime.date.today().isoformat()
