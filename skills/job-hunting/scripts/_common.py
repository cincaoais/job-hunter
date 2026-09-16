#!/usr/bin/env python3
"""Shared helpers for the job-hunting skill scripts.

Stdlib only (Python 3.10+), no third-party dependencies. Kept small and
dependency-free so every script under skills/job-hunting/scripts/ can import
it without a virtualenv.
"""
from __future__ import annotations

import datetime
import importlib
import json
import os
import re
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


def http_get(url, headers=None, timeout=20) -> tuple[int, bytes]:
    _rate_limit(url)
    hdrs = {"User-Agent": UA}
    if headers:
        hdrs.update(headers)
    req = urllib.request.Request(url, headers=hdrs)
    try:
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            return resp.status, resp.read()
    except urllib.error.HTTPError as e:
        return e.code, e.read()
    except urllib.error.URLError as e:
        return 0, str(e).encode()


def http_post_json(url, payload, headers=None, timeout=20) -> tuple[int, bytes]:
    _rate_limit(url)
    hdrs = {"User-Agent": UA, "Content-Type": "application/json"}
    if headers:
        hdrs.update(headers)
    data = json.dumps(payload).encode("utf-8")
    req = urllib.request.Request(url, data=data, headers=hdrs, method="POST")
    try:
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            return resp.status, resp.read()
    except urllib.error.HTTPError as e:
        return e.code, e.read()
    except urllib.error.URLError as e:
        return 0, str(e).encode()


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
