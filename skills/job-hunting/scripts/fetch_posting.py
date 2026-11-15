#!/usr/bin/env python3
"""Turn a job URL (or a board id) into a clean markdown posting file.

  python3 fetch_posting.py https://my.jobstreet.com/job/94655291 --save
  python3 fetch_posting.py 94655291 --print
  python3 fetch_posting.py --stdin --company Acme --title "Backend Engineer" --save

Known boards go through their own detail API (`sources/`), which gives the
real description instead of a scraped page: JobStreet ids, LinkedIn job ids
and MyCareersFuture uuids (screening questions included). Any
other URL is fetched and reduced to the largest `<main>`/`<article>` block.
When a site answers with a bot challenge the stealth browser
(`pip install cloakbrowser`) is used if it is installed.

Exit codes: 0 ok, 2 bad arguments, 3 blocked by a bot challenge, 4 not found
(no such job, or the page could not be fetched). Network failures are
reported, never raised.
"""
from __future__ import annotations

import argparse
import contextlib
import html as html_mod
import itertools
import re
import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from _common import (  # noqa: E402
    default_fetch, html_to_text, http_get, optional_import, slugify,
    today, use_utf8_output, workspace_dir,
)

# The identified UA first (honest), then one Chrome-shaped retry: a fair
# number of career sites 403 anything that does not look like a browser.
CHROME_UA = ("Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
             "(KHTML, like Gecko) Chrome/125.0.0.0 Safari/537.36")
BROWSER_HEADERS = {
    "User-Agent": CHROME_UA,
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
    "Accept-Language": "en-US,en;q=0.9",
}

BLOCKED_MSG = "blocked; paste the posting text instead (or pip install cloakbrowser)"
# Under this many characters a generic page is assumed to render its posting
# with JavaScript, so the stealth browser is worth a try if it is installed.
MIN_GENERIC_TEXT = 200
# A single-page app paints after DOMContentLoaded, so a thin first read is
# retried once the network goes quiet (or after this long, whichever first).
SETTLE_MS = 3000
BLOCK_STATUSES = (403, 429, 503)
# Lowercased markers of a challenge page served with a 200.
BLOCK_MARKERS = ("cf-chl", "cf-challenge", "just a moment", "prove your humanity",
                 "challenge-platform", "access denied")
# What the stealth browser can still land on (Glassdoor's "Humans only").
BROWSER_BLOCK_MARKERS = BLOCK_MARKERS + (
    "humans only", "prove you are human", "verify you are human", "are you a robot")
BROWSER_MARKER_SPAN = 2000  # a challenge states itself at the top of the page

FRONTMATTER_KEYS = ("source", "url", "company", "title", "location", "salary",
                    "posted", "fetched", "screening_questions")
# Fallback country when the host does not say which market a board id is from.
BOARD_DEFAULT_COUNTRY = {"jobstreet": "MY", "linkedin": "MY", "mcf": "SG"}


# --- classify ----------------------------------------------------------------

_JOBSTREET_RE = re.compile(r"jobstreet\.com(?:\.[a-z]{2})?/(?:[\w.-]+/)*job/(\d+)", re.I)
# The slug form ends in the id ("...-at-grab-4455634411"), the short form is
# just the id; both are the trailing digits of the path segment.
_LINKEDIN_RE = re.compile(r"linkedin\.com/jobs/view/[^/?#]*?(\d{6,})(?:[/?#]|$)", re.I)
_MCF_RE = re.compile(r"mycareersfuture\.gov\.sg/job/.*([0-9a-f]{32})", re.I)

_BARE_ID_RE = re.compile(r"^\d{5,}$")
_BARE_UUID_RE = re.compile(r"^[0-9a-f]{32}$", re.I)
_HOST_RE = re.compile(r"^[a-z][a-z0-9+.-]*://([^/?#]*)", re.I)


def _host(url: str) -> str:
    m = _HOST_RE.match(url or "")
    return (m.group(1) if m else "").lower()


def _country_of(url: str) -> str:
    """Market from the host: my./sg. subdomain, a JobStreet country domain, or the board's own market."""
    host = _host(url)
    if "mycareersfuture" in host:
        return "SG"
    for domain, code in (("jobstreet.com.sg", "SG"), ("jobstreet.com.my", "MY")):
        if host == domain or host.endswith("." + domain):
            return code
    for prefix, code in (("my.", "MY"), ("sg.", "SG")):
        if host.startswith(prefix) or ("." + prefix) in host:
            return code
    return ""


def classify(target: str) -> tuple[str, str, str]:
    """`(source, id, country)` for a job URL, or a bare board id.

    A bare number is a JobStreet MY id and a bare 32-hex string an MCF uuid
    (the two ids users copy most). Anything unrecognized comes back as
    `("generic", <target>, "")` for the plain-HTML path.
    """
    text = (target or "").strip()
    if _BARE_ID_RE.match(text):
        return "jobstreet", text, "MY"
    if _BARE_UUID_RE.match(text):
        return "mcf", text.lower(), "SG"
    for source, pattern in (("jobstreet", _JOBSTREET_RE), ("linkedin", _LINKEDIN_RE),
                            ("mcf", _MCF_RE)):
        m = pattern.search(text)
        if m:
            # MCF uuids are hex: the api is case-sensitive, the url is not.
            job_id = m.group(1).lower() if source == "mcf" else m.group(1)
            return source, job_id, _country_of(text)
    return "generic", text, ""


# --- generic extraction ------------------------------------------------------

_TITLE_RE = re.compile(r"<title[^>]*>(.*?)</title\s*>", re.S | re.I)
# Chrome, furniture and head metadata: gone before anything is measured.
# `<form>` is deliberately NOT here: Workday, Lever and SmartRecruiters nest
# the whole description inside the apply form, so dropping it empties the
# page. Only the form's own widgets go.
_DROP_TAGS = ("head", "script", "style", "noscript", "template", "svg", "iframe",
              "nav", "header", "footer", "aside",
              "button", "select", "textarea", "label", "option", "fieldset")
_DROP_RE = re.compile(
    r"<(" + "|".join(_DROP_TAGS) + r")\b[^>]*>.*?</\1\s*>", re.S | re.I)


def _blocks(html: str, tag: str) -> list[str]:
    """Inner HTML of every `<tag>` element, nesting-aware."""
    out = []
    token_re = re.compile(rf"<(/?){tag}\b[^>]*?(/?)>", re.I)
    tokens = list(token_re.finditer(html))
    for i, start in enumerate(tokens):
        if start.group(1) or start.group(2):  # a close or self-closing tag
            continue
        depth = 0
        for token in tokens[i:]:
            depth += -1 if token.group(1) else (0 if token.group(2) else 1)
            if depth == 0:
                out.append(html[start.end():token.start()])
                break
        else:
            out.append(html[start.end():])
    return out


def generic_extract(html: str) -> dict:
    """`{"title", "text"}` from an arbitrary job page.

    The `<title>` tag gives the title. Script/style/nav/header/footer/form
    blocks are dropped, then the largest `<main>`/`<article>` block wins —
    falling back to `<body>`, then to whatever is left — and is flattened to
    markdown-ish text.
    """
    raw = html if isinstance(html, str) else (html or b"").decode("utf-8", "replace")
    title_match = _TITLE_RE.search(raw)
    title = html_to_text(title_match.group(1)) if title_match else ""
    stripped = _DROP_RE.sub("\n", raw)
    candidates = _blocks(stripped, "main") + _blocks(stripped, "article")
    texts = [html_to_text(block) for block in candidates]
    best = max(texts, key=len) if texts else ""
    if not best:
        for block in _blocks(stripped, "body"):
            best = max(best, html_to_text(block), key=len)
    if not best:
        best = html_to_text(stripped)
    return {"title": html_mod.unescape(title).strip(), "text": best}


# --- fetching ----------------------------------------------------------------

def _as_text(body) -> str:
    if isinstance(body, bytes):
        return body.decode("utf-8", "replace")
    return body or ""


def looks_blocked(status: int, body) -> bool:
    """True when this response is a bot challenge rather than the posting."""
    if status in BLOCK_STATUSES:
        return True
    low = _as_text(body)[:200_000].lower()
    return any(marker in low for marker in BLOCK_MARKERS)


def fetch_html(url: str, *, get=None) -> tuple[int, str]:
    """GET `url` with the identified UA, retrying once as a browser."""
    get = get or http_get
    status, body = get(url, None)
    if status == 200 and not looks_blocked(status, body):
        return status, _as_text(body)
    status2, body2 = get(url, dict(BROWSER_HEADERS))
    if status2 == 200 and not looks_blocked(status2, body2):
        return status2, _as_text(body2)
    # Keep whichever answer is more informative for the caller's diagnosis.
    if status2 in BLOCK_STATUSES or status not in BLOCK_STATUSES:
        return status2, _as_text(body2)
    return status, _as_text(body)


def _page_of(browser):
    """CloakBrowser's launch() may hand back a browser or a page."""
    for name in ("new_page", "newPage", "page"):
        factory = getattr(browser, name, None)
        if callable(factory):
            return factory()
    return browser


def _inner_text(page) -> str:
    return str(page.evaluate("() => document.body.innerText") or "").strip()


def _settle(page) -> None:
    """Give a JavaScript-rendered page a moment to paint."""
    for wait in (lambda: page.wait_for_load_state("networkidle", timeout=15000),
                 lambda: page.wait_for_timeout(SETTLE_MS)):
        try:
            wait()
            return
        except Exception:  # an older/simpler page object: fall through
            continue
    time.sleep(SETTLE_MS / 1000)


def browse(url: str, *, cloak=None) -> dict | None:
    """`{"title", "text"}` via the stealth browser, or None if unavailable."""
    module = cloak if cloak is not None else optional_import("cloakbrowser")
    if module is None:
        return None
    browser = page = None
    try:
        # The browser library prints a banner of its own; stdout belongs to
        # the rendered posting, so its chatter is pushed to stderr.
        with contextlib.redirect_stdout(sys.stderr):
            browser = module.launch(headless=True)
            page = _page_of(browser)
            page.goto(url, wait_until="domcontentloaded", timeout=45000)
            text = _inner_text(page)
            if len(text) < MIN_GENERIC_TEXT:
                # DOMContentLoaded on an app shell is an empty <body>.
                _settle(page)
                text = max(text, _inner_text(page), key=len)
            title = str(page.evaluate("() => document.title") or "").strip()
    except Exception:  # a missing binary, a timeout, an API change: all "blocked"
        text, title = "", ""
    finally:
        for obj in (page, browser):
            closer = getattr(obj, "close", None)
            if callable(closer):
                try:
                    closer()
                except Exception:
                    pass
    if not text:
        return None
    return {"title": title, "text": text}


def is_browser_blocked(got: dict) -> bool:
    """True when the stealth browser still met a wall, or rendered next to nothing.

    Such a page is never saved as a posting: it is a challenge (and may
    carry the user's IP address), not a job description.
    """
    text = str(got.get("text") or "")
    head = (str(got.get("title") or "") + "\n" + text[:BROWSER_MARKER_SPAN]).lower()
    if any(marker in head for marker in BROWSER_BLOCK_MARKERS):
        return True
    return len(text.strip()) < MIN_GENERIC_TEXT


def _source_module(name: str):
    try:
        return __import__(f"sources.{name}", fromlist=[name])
    except Exception:  # a broken source must not crash the fetch
        return None


def fetch_board(source: str, job_id: str, country: str,
                *, detail_fetch=None) -> tuple[dict | None, str]:
    """`(job, "")` from one board's detail API, or `(None, reason)`.

    A board that is down must not look like a job that is gone: a failed
    detail call or a recorded warning gives an `"unavailable: ..."` reason,
    while a 404/410 (or a clean empty answer) means `"not found: ..."`.
    """
    module = _source_module(source)
    if module is None:
        return None, f"unavailable: the {source} module could not be loaded"
    fetch_fn = detail_fetch or default_fetch
    try:
        got = module.detail(job_id, country=country or BOARD_DEFAULT_COUNTRY.get(source, "MY"),
                            fetch=fetch_fn)
    except Exception as exc:  # never a traceback for a network or payload surprise
        return None, (f"unavailable: {source} failed ({type(exc).__name__}: {exc})"
                      " — try again later or paste the posting text")
    if not got:
        warnings = [str(w) for w in (getattr(module, "LAST_WARNINGS", []) or [])]
        if warnings and not all("HTTP 404" in w or "HTTP 410" in w for w in warnings):
            return None, ("unavailable: " + "; ".join(warnings)
                          + " — try again later or paste the posting text")
        return None, f"not found: {source} has no job {job_id}"
    job = dict(got)
    job["source"] = source
    return job, ""


def fetch(target: str, *, get=None, detail_fetch=None) -> tuple[dict | None, str]:
    """`(job, "")` for a posting, or `(None, reason)`.

    `reason` is `"blocked"` when only a bot challenge came back,
    `"unavailable: ..."` when the board failed (it is down, not the job), or
    `"not found: ..."` when the board has no such job / the page would not
    load. Pure apart from the injected `get` (generic HTTP) and
    `detail_fetch` (the board APIs).
    """
    source, job_id, country = classify(target)
    if source != "generic":
        job, reason = fetch_board(source, job_id, country, detail_fetch=detail_fetch)
        if job is None:
            return None, reason
        job.setdefault("url", "")
        if not job["url"] and "://" in target:
            job["url"] = target
        return job, ""

    url = target
    if "://" not in url:
        return None, f"not found: {url!r} is not a URL or a known job id"
    status, body = fetch_html(url, get=get)
    blocked = looks_blocked(status, body)
    # A 200 body is parsed even when it trips a challenge marker: a security
    # engineer's JD may simply contain the words "access denied". The browser
    # is only worth starting when what came back is too thin to be a posting.
    extracted = generic_extract(body) if status == 200 else {"title": "", "text": ""}
    if len(extracted["text"]) < MIN_GENERIC_TEXT and (blocked or status == 200):
        got = browse(url)
        if got and is_browser_blocked(got):
            return None, "blocked"
        if got and len(got["text"]) > len(extracted["text"]):
            extracted = {"title": got["title"] or extracted["title"], "text": got["text"]}
    # A thin page that still trips a challenge marker is a challenge page, not
    # a posting: never let its text through as a job description.
    if blocked and len(extracted["text"]) < MIN_GENERIC_TEXT:
        return None, "blocked"
    if not extracted["text"]:
        if blocked:
            return None, "blocked"
        if status != 200:
            return None, f"not found: HTTP {status} for {url}"
        return None, (f"not found: no posting text at {url} "
                      f"(the page may need JavaScript; paste the text instead)")
    return {"source": "generic", "url": url, "title": extracted["title"],
            "description_md": extracted["text"]}, ""


# --- rendering and saving ----------------------------------------------------

_NEEDS_QUOTE = ":#&*!|>%@`\"'{}[],"
# YAML 1.1 (still what many parsers do) reads these bare words as booleans or
# null, so a title of "No" or a location of "On" must stay a string.
_RESERVED_WORDS = {"yes", "no", "true", "false", "null", "on", "off", "~", "y", "n"}


def _scalar(value) -> str:
    """A YAML-safe one-line scalar: quoted only when it has to be."""
    text = "" if value is None else str(value).strip()
    text = re.sub(r"\s+", " ", text)
    if not text:
        return ""
    if (any(ch in text for ch in _NEEDS_QUOTE)
            or text.startswith(("-", "?"))
            or text.lower() in _RESERVED_WORDS):
        return '"' + text.replace("\\", "\\\\").replace('"', '\\"') + '"'
    return text


def _value_of(job: dict, key: str):
    if key == "fetched":
        return job.get("fetched") or today()
    if key == "salary":
        return job.get("salary") or job.get("salary_label")
    return job.get(key)


def render_posting(job: dict) -> str:
    """The saved posting: YAML frontmatter then a `## Description` body."""
    job = job or {}
    lines = ["---"]
    for key in FRONTMATTER_KEYS:
        if key == "screening_questions":
            questions = [q for q in (job.get("screening_questions") or []) if str(q).strip()]
            if not questions:
                lines.append("screening_questions: []")
            else:
                lines.append("screening_questions:")
                lines += [f"  - {_scalar(q)}" for q in questions]
            continue
        value = _scalar(_value_of(job, key))
        lines.append(f"{key}: {value}" if value else f"{key}:")
    body = str(job.get("description_md") or job.get("text") or "").strip()
    lines += ["---", "", "## Description", "", body]
    return "\n".join(lines).rstrip("\n") + "\n"


_URL_LINE_RE = re.compile(r"^url:\s*(.*?)\s*$", re.M)


def _saved_url(path: Path) -> str:
    try:
        text = path.read_text(encoding="utf-8", errors="replace")
    except OSError:
        return ""
    m = _URL_LINE_RE.search(text.split("\n---", 1)[0])
    return (m.group(1).strip().strip('"').strip("'") if m else "")


def posting_slug(job: dict) -> str:
    """`<company>-<title>` slug, with a usable fallback when both are blank."""
    job = job or {}
    slug = slugify(f"{job.get('company') or ''} {job.get('title') or ''}")
    return slug or slugify(f"{job.get('source') or ''} posting") or "posting"


def save(job: dict, *, ws: Path | None = None) -> Path:
    """Write `postings/<company>-<title>.md`; `-2`, `-3`… for a different url.

    Re-fetching the same url overwrites its file, so a posting never piles up
    duplicates, while two different jobs with the same company and title get
    their own files.
    """
    root = (ws or workspace_dir()) / "postings"
    root.mkdir(parents=True, exist_ok=True)
    slug = posting_slug(job)
    url = str((job or {}).get("url") or "").strip()
    body = render_posting(job)
    for n in itertools.count(1):
        path = root / (f"{slug}.md" if n == 1 else f"{slug}-{n}.md")
        if path.exists() and _saved_url(path) != url:
            continue
        with open(path, "w", encoding="utf-8", newline="\n") as fh:
            fh.write(body)
        return path
    raise AssertionError("unreachable")  # pragma: no cover


# --- CLI ---------------------------------------------------------------------

def build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(
        prog="fetch_posting.py",
        description="Fetch a job posting into markdown (postings/<slug>.md).")
    p.add_argument("target", nargs="?", help="job URL, or a JobStreet id / MCF uuid")
    p.add_argument("--stdin", action="store_true",
                   help="read the posting text from stdin instead of fetching")
    p.add_argument("--save", action="store_true", help="write postings/<slug>.md")
    p.add_argument("--print", action="store_true", dest="print_",
                   help="print the markdown (the default when --save is not given)")
    p.add_argument("--company", help="override the company name (used for the filename)")
    p.add_argument("--title", help="override the job title (used for the filename)")
    p.add_argument("--url", help="the posting's url, for --stdin")
    return p


def _apply_overrides(job: dict, args) -> dict:
    for key in ("company", "title", "url"):
        value = getattr(args, key, None)
        if value:
            job[key] = value.strip()
    return job


def main(argv=None) -> int:
    use_utf8_output()
    parser = build_parser()
    args = parser.parse_args(argv)

    if args.stdin:
        text = sys.stdin.read().strip()
        if not text:
            print("Nothing on stdin. Paste the posting text, or pass a URL.", file=sys.stderr)
            return 2
        job = {"source": "pasted", "url": "", "description_md": text}
    else:
        if not args.target:
            parser.print_usage(sys.stderr)
            print("fetch_posting.py: a job URL or id is required (or --stdin).",
                  file=sys.stderr)
            return 2
        job, reason = fetch(args.target)
        if job is None:
            if reason == "blocked":
                print(BLOCKED_MSG, file=sys.stderr)
                return 3
            print(reason, file=sys.stderr)
            return 4

    job = _apply_overrides(job, args)
    markdown = render_posting(job)
    if args.print_ or not args.save:
        print(markdown, end="")
    if args.save:
        try:
            path = save(job)
        except OSError as exc:
            print(f"could not write the posting: {exc}", file=sys.stderr)
            return 4
        print(f"Saved {path}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
