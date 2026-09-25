#!/usr/bin/env python3
"""ATS text-layer check: what a parser actually reads from a resume file.

  python3 ats_check.py <file.docx|file.pdf|file.md|file.txt>
                       [--posting postings/<slug>.md | --keywords "a,b,c"]
                       [--lint] [--target-title "<target role>"] [--slop] [--text] [--json]

Extraction (the **Method:** line):
  docx-xml        a .docx text layer from word/document.xml (list paragraphs read "- ")
  pypdf           a .pdf through pypdf, when it is installed
  pdftotext-raw   a .pdf through `pdftotext -raw` (content-stream order), when on PATH
  markdown, text  a draft read as text; markdown loses #, ** and link syntax
With no PDF extractor the declared fallback line is printed and the exit is 2.

Checks (they combine):
  --posting FILE    keyword coverage against keywords taken from a saved posting
                    (requirement-style sections plus tech tokens, at most 25), reported
                    as must-have and nice-to-have when the posting has both
  --keywords LIST   comma-separated keywords to check instead (the jd-match mirror list)
                    Matching ignores case except for ALL-CAPS and 1-2 letter keywords
                    (REST, Go), and a plural "s" is optional both ways.
  --lint            6-second lint: email and phone as literal text, a year in the first
                    15 lines, a number in the first Experience bullet, at most 900 words;
                    on a PDF the date and first-bullet checks print "skip"
  --target-title T  also check that T's words (3+ letters) appear in the first 5 lines;
                    implies --lint
  --slop            banned-phrase scan against assets/slop-phrases.txt
  --text            print the extracted text after the report (the reading-order
                    evidence; the default when no check is asked)
  --json            the same report as one JSON object

Exit codes: 0 whenever text was extracted, FAIL lines included; 2 for bad
arguments, an unreadable file, or no PDF extractor.
"""
from __future__ import annotations

import argparse
import json
import re
import shutil
import subprocess
import sys
import unicodedata
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from _common import docx_text, optional_import  # noqa: E402

SLOP_FILE = Path(__file__).resolve().parent.parent / "assets" / "slop-phrases.txt"
FALLBACK_LINE = ("Text layer not checked: no PDF text extractor here (pip install pypdf, or install "
                 "pdftotext). Check the .docx master instead, or fall back to the pre-delivery "
                 "checklist and tell the user the check did not run.")
PDFTOTEXT_TIMEOUT = 60
MAX_KEYWORDS = 25
MAX_WORDS = 900          # about two pages
TOP_LINES_DATE = 15
TOP_LINES_TITLE = 5

# --- normalising text for matching --------------------------------------------------

_FOLD = str.maketrans({"\u2018": "'", "\u2019": "'", "\u201c": '"', "\u201d": '"',
                       "\u2010": "-", "\u2011": "-", "\u00ad": None})  # soft hyphen dropped


def _fold(text: str) -> str:
    """NFKC (ligatures, no-break spaces) plus straight quotes and plain hyphens."""
    return unicodedata.normalize("NFKC", text or "").translate(_FOLD)


def _one_line(text: str, limit: int = 70) -> str:
    text = " ".join(text.split())
    return text if len(text) <= limit else text[: limit - 1].rstrip() + "…"


# --- extraction -----------------------------------------------------------------------

_MD_HEADING_RE = re.compile(r"^\s{0,3}#{1,6}\s+(.*?)(?:\s+#+)?\s*$")
_MD_STAR_BULLET_RE = re.compile(r"^(\s*)[*+]\s+")
_MD_LINK_RE = re.compile(r"!?\[([^\]]*)\]\(\s*<?([^)\s>]*)>?(?:\s+\"[^\"]*\")?\s*\)")
_MD_AUTOLINK_RE = re.compile(r"<((?:https?://|mailto:)[^>\s]+)>")


def markdown_to_text(md: str) -> str:
    """A markdown draft as a parser would see the built file: no #, ** or link syntax.

    `*` and `+` bullets become "- " so bullets read the same as in a .docx.
    """
    lines = []
    for line in md.splitlines():
        m = _MD_HEADING_RE.match(line)
        if m:
            line = m.group(1)
        line = _MD_STAR_BULLET_RE.sub(r"\1- ", line)
        line = line.replace("**", "")
        line = _MD_LINK_RE.sub(lambda m: m.group(1) or m.group(2), line)
        line = _MD_AUTOLINK_RE.sub(r"\1", line)
        lines.append(line)
    return "\n".join(lines)


def _decode(data: bytes) -> str:
    return data.decode("utf-8-sig", "replace").replace("\r\n", "\n").replace("\r", "\n")


def _pdf_text(path: Path) -> tuple[str, str]:
    """pypdf if importable, else `pdftotext -raw`, else ("", "unavailable")."""
    problem = ""
    pypdf = optional_import("pypdf")
    if pypdf is not None:
        try:
            reader = pypdf.PdfReader(str(path))
            return "\n".join((page.extract_text() or "") for page in reader.pages), "pypdf"
        except Exception as e:  # pypdf raises many types on damaged or encrypted files
            problem = f"pypdf: {e.__class__.__name__}: {e}"
    exe = shutil.which("pdftotext")
    if exe:
        # -raw keeps content-stream order; the default mode interleaves sidebar columns
        try:
            proc = subprocess.run([exe, "-raw", "-enc", "UTF-8", str(path), "-"],
                                  capture_output=True, timeout=PDFTOTEXT_TIMEOUT)
        except (OSError, subprocess.SubprocessError) as e:
            raise ValueError(f"pdftotext failed: {e}") from None
        if proc.returncode != 0:
            err = [ln.strip() for ln in proc.stderr.decode("utf-8", "replace").splitlines() if ln.strip()]
            raise ValueError(f"pdftotext could not read it: {err[-1] if err else proc.returncode}")
        text = proc.stdout.decode("utf-8", "replace").replace("\r\n", "\n").replace("\f", "\n")
        return text, "pdftotext-raw"
    if problem:
        raise ValueError(f"not a readable .pdf ({problem})")
    return "", "unavailable"


def extract_text(path) -> tuple[str, str]:
    """(text, method) for a .docx, .pdf, .md/.markdown or .txt file.

    method is "docx-xml", "pypdf", "pdftotext-raw", "markdown", "text" or
    "unavailable" (a PDF with no extractor on this machine). Raises OSError
    when the file cannot be read and ValueError when it is not a readable
    document of a supported type.
    """
    path = Path(path)
    data = path.read_bytes()
    suffix = path.suffix.lower()
    if suffix == ".docx" or (suffix != ".pdf" and data.startswith(b"PK\x03\x04")):
        try:
            return docx_text(data), "docx-xml"
        except ValueError:
            raise
        except Exception as e:  # zipfile edge cases: encrypted, unsupported compression
            raise ValueError(f"not a readable .docx ({e.__class__.__name__}: {e})") from None
    if suffix == ".pdf" or data.startswith(b"%PDF"):
        return _pdf_text(path)
    if suffix in (".md", ".markdown"):
        return markdown_to_text(_decode(data)), "markdown"
    if suffix == ".txt":
        return _decode(data), "text"
    raise ValueError(f"unsupported file type {suffix or '(no extension)'}: "
                     "pass a .docx, .pdf, .md or .txt")


# --- keyword coverage -------------------------------------------------------------------

_ALPHA_WORD_RE = re.compile(r"[A-Za-z]+(?:-[A-Za-z]+)*")


def _keyword_regex(keyword: str) -> re.Pattern:
    """How a keyword is found in extracted text.

    Case-insensitive, except ALL-CAPS keywords and those with at most two
    letters (REST is not "rest", Go is not "go"). Word-bounded: "-" or "&"
    joined to a following letter continues the word (Go-to-market, R&D,
    C-suite), and a keyword starting with "." needs a non-word, non-dot char
    before it (.NET is not in tm.net.my). Whitespace inside a keyword matches
    any whitespace; C++, C#, .NET and Node.js stay literal. A purely
    alphabetic last word matches with or without a plural "s" (Payments ~
    payment, API ~ APIs).
    """
    k = _fold(keyword)
    letters = sum(c.isalpha() for c in k)
    exact_case = k.isupper() or letters <= 2
    parts = k.split()
    last, plural = parts[-1], ""
    if letters > 2 and _ALPHA_WORD_RE.fullmatch(last):
        if k.isupper():
            plural = "" if last.endswith("S") else "s?"           # API ~ APIs, never AWS ~ AW
        elif last.endswith("s") and not last.endswith("ss") and len(last) >= 4:
            parts[-1], plural = last[:-1], "s?"                   # Payments ~ payment
        elif not last.endswith("s"):
            plural = "s?"                                         # payment ~ Payments
    body = r"\s+".join(re.escape(part) for part in parts) + plural
    if k.startswith("."):
        left = r"(?<![\w.])"
    else:
        left = r"(?<!\w)" if k[0].isalnum() else ""
    right = r"(?![\w+#]|[-&][^\W\d_])" if k[-1].isalnum() else ""
    return re.compile(left + body + right, 0 if exact_case else re.I)


def keyword_coverage(text: str, keywords) -> dict:
    """{"present": [...], "missing": [...], "ratio": present/total} in keyword order.

    Keywords are deduped case-insensitively (first spelling wins); blanks drop.
    """
    folded = _fold(text)
    present, missing, seen = [], [], set()
    for raw in keywords:
        kw = " ".join(str(raw).split())
        if not _fold(kw).strip() or kw.lower() in seen:
            continue
        seen.add(kw.lower())
        (present if _keyword_regex(kw).search(folded) else missing).append(kw)
    total = len(present) + len(missing)
    return {"present": present, "missing": missing,
            "ratio": round(len(present) / total, 3) if total else 0.0}


# --- keywords from a posting ---------------------------------------------------------------

_REQ_HEADING_RE = re.compile(
    r"requirement|qualification|skill|must[\s-]*haves?|nice[\s-]*to[\s-]*haves?"
    r"|what you(?:'ll| will)? need|what you bring|about you|who you are|tech stack", re.I)
_NICE_HEADING_RE = re.compile(
    r"nice[\s-]*to[\s-]*haves?|good[\s-]*to[\s-]*haves?|bonus|preferred|desirable|pluses", re.I)
# Other section names: an unmarked short line reads as a heading only with one of these
# (or a trailing colon), so plain requirement lines stay content.
_SECTION_WORDS_RE = re.compile(
    r"\b(?:responsibilit\w*|benefits?|what we offer|perks?|about|role|company|description"
    r"|information|culture|life at|why join|opportunit\w*|stand for|how to apply|compensation"
    r"|welfare|package|duties|what you(?:'ll| will) do|day[\s-]to[\s-]day|the team|our team"
    r"|who we are)\b", re.I)
_BOLD_LINE_RE = re.compile(r"(\*\*|__)(.+?)\1\s*:?")
_DESCRIPTION_RE = re.compile(r"^##\s+Description\s*$", re.M | re.I)
_FRONTMATTER_RE = re.compile(r"\A---\n.*?\n---[ \t]*(?:\n|\Z)", re.S)
_ANY_BULLET_RE = re.compile(r"^\s*(?:[-*+•●▪◦‣]|\d{1,2}[.)])\s+")
_INLINE_HEADING_RE = re.compile(
    r"^(?:\*\*|__)?([A-Za-z][A-Za-z '/&-]{1,48}?)(?:\*\*|__)?\s*:\s*(?:\*\*|__)?\s*(.*)$")
_SEGMENT_SPLIT_RE = re.compile(r"[,;:()\[\]{}|!?·•—–\"]|\s[/&+-]\s|\.(?=\s|$)")

# Words that end a keyword run: function words plus the generic posting vocabulary.
_STOP = frozenset("""
a an the and or nor but of in on at to for with without from by as into onto over under about
across within via per than then that this these those such is are be been being was were will
would should can could may might must shall have has had having do does did done you your yours
you'll you're you've we our ours we're we'll us they their them it its it's who whom which what
where when how why all any some each every both either neither other others more most less least
very well also just not no yes if so up out own able like including include includes etc eg ie
e.g i.e plus get make run runs running ideally
experience experienced experiences knowledge knowledgeable ability abilities strong solid good
great excellent exceptional outstanding proven demonstrated demonstrable deep team teams year
years yrs minimum min preferred preferably prefer required require requires requirement
requirements nice bonus advantage advantageous added familiarity familiar understanding
understand comfortable proficiency proficient hands-on working work skills skill production
environment environments background degree degrees bachelor bachelor's bachelors master master's
masters diploma phd field fields discipline disciplines related relevant similar equivalent basic
advanced senior junior mid mid-level level professional practical real clear effective
effectively high highly using use used new willing willingness learn learning attention detail
details communication written spoken verbal interpersonal collaboration collaborative teamwork
problem-solving analytical motivated self-motivated passionate independently independent
ambiguity mindset fast-paced dynamic common best daily
""".split())
# Leading verbs trimmed from a run ("operating gRPC services" -> gRPC, services).
_LEAD_TRIM = frozenset("""
designing operating building developing maintaining writing leading managing scaling owning
delivering driving supporting implementing deploying creating shipping manage
""".split())
# Generic nouns that are no keyword on their own.
_ALONE_DROP = _LEAD_TRIM | frozenset("""
services service systems system tools tool platform platforms domain concepts principles
practices methodologies methodology frameworks technologies technology tech stack programming
language languages certification certifications certified applications application solutions
products product software code coding projects project tasks task processes process engineers
engineer engineering development developer developers
""".split())
# Lowercase tails trimmed from a run ("backend engineering" -> backend).
_SUFFIX_TRIM = frozenset("""
development engineering domain programming language languages concepts principles practices
methodologies methodology certification certifications background
""".split())
# Tech names that look like plain capitalised words (case-sensitive; ALL-CAPS also counts).
_TECH_VOCAB = frozenset("""
Go Golang Python Java Kotlin Swift Rust Ruby Rails Scala Elixir Erlang Haskell Clojure Perl Dart
Flutter Lua Julia MATLAB R C Bash PowerShell JavaScript TypeScript PHP SQL NoSQL HTML CSS
React Angular Vue Svelte Django Flask FastAPI Spring Express Laravel Symfony Hibernate Kubernetes
Docker Terraform Ansible Jenkins Helm Istio Nginx Linux Unix Git GitHub GitLab Bitbucket Jira
Confluence Kafka RabbitMQ Redis Postgres PostgreSQL MySQL MongoDB Cassandra DynamoDB
Elasticsearch OpenSearch Spark Hadoop Airflow Flink Snowflake Databricks BigQuery Redshift dbt
Looker Tableau Excel PowerPoint Figma Photoshop Illustrator Salesforce SAP Oracle HubSpot Shopify
WordPress AWS GCP Azure Firebase Heroku Vercel Cloudflare Pandas NumPy PyTorch TensorFlow Keras
Selenium Cypress Playwright Jest Webpack Prometheus Grafana Datadog Splunk GraphQL gRPC REST
Android iOS Unity Unreal
""".split())
# All-caps tokens that are not skills (currencies, titles, places, filler).
_CAPS_IGNORE = frozenset("""
A I RM SGD USD MYR IDR THB VND EUR GBP HR CEO CTO CFO COO VP OT EPF SOCSO CPF ESOP KL PJ SG
MY US UK EU APAC SEA ETA NA TBC OK
""".split())
_MIXED_CASE_RE = re.compile(r"[a-z][A-Z]")                        # gRPC, PostgreSQL, iOS
_ALL_CAPS_RE = re.compile(r"[A-Z][A-Z0-9]*[A-Z0-9](?:/[A-Z0-9]+)*")  # AWS, EC2, CI/CD
_SYMBOL_RE = re.compile(r"[+#]|^\.[A-Za-z]|[A-Za-z]\.[A-Za-z]")     # C++, C#, .NET, Node.js


def _is_tech(word: str) -> bool:
    if word in _TECH_VOCAB or (word.isupper() and word.capitalize() in _TECH_VOCAB):
        return True
    if word in _CAPS_IGNORE or not re.search(r"[A-Za-z]", word):
        return False
    return bool(_MIXED_CASE_RE.search(word) or _ALL_CAPS_RE.fullmatch(word)
                or re.search(r"\d", word) or _SYMBOL_RE.search(word))


def _strip_md(text: str) -> str:
    return _MD_LINK_RE.sub(lambda m: m.group(1) or m.group(2), text.replace("**", "").replace("`", ""))


def _posting_body(posting_md: str) -> str:
    md = _fold(posting_md).replace("\r\n", "\n")
    m = _DESCRIPTION_RE.search(md)
    if m:
        return md[m.end():]
    return _FRONTMATTER_RE.sub("", md, count=1)


def _heading(line: str) -> tuple[str, str] | None:
    """(heading, rest of line) when `line` reads as a section heading, else None."""
    s = line.strip()
    m = _MD_HEADING_RE.match(s)
    if m:
        return _strip_md(m.group(1)).strip().rstrip(":").strip(), ""
    if not s or _ANY_BULLET_RE.match(s):
        return None
    m = _INLINE_HEADING_RE.match(s)          # "Skills: Go, Python", "**Must have:** Kafka"
    if m and _section_kind(m.group(1)):
        return m.group(1).strip(), m.group(2).strip()
    m = _BOLD_LINE_RE.fullmatch(s)           # "**Requirements**", "**What we offer**"
    if m:
        return m.group(2).strip().rstrip(":").strip(), ""
    plain = _strip_md(s).strip()
    words = plain.rstrip(":").strip()
    if (words[:1].isupper() and len(words.split()) <= 8 and not re.search(r"[,;.!?:]", words)
            and (plain.endswith(":") or _section_kind(words) or _SECTION_WORDS_RE.search(words))):
        return words, ""                       # "Qualifications", "Key Responsibilities", "Perks:"
    return None


def _section_kind(title: str) -> str | None:
    """"nice", "must", or None for a heading that is no requirement section."""
    if _NICE_HEADING_RE.search(title):
        return "nice"
    return "must" if _REQ_HEADING_RE.search(title) else None


def _segments(line: str) -> list[list[str]]:
    """A line split at punctuation into lists of cleaned words."""
    line = _strip_md(_ANY_BULLET_RE.sub("", line))
    out = []
    for seg in _SEGMENT_SPLIT_RE.split(line):
        words = [w.strip("'\"`*_") for w in seg.split()]
        words = [w for w in words if w]
        if words:
            out.append(words)
    return out


def _chunks(words: list[str]) -> list[str]:
    """Keyword candidates in one segment: tech tokens alone, other runs between stopwords."""
    found, run = [], []

    def flush():
        while run and run[0].lower() in _LEAD_TRIM:
            run.pop(0)
        while run and run[-1] in _SUFFIX_TRIM:
            run.pop()
        capitalised = all(w[:1].isupper() for w in run)
        if (run and not all(w.lower() in _ALONE_DROP for w in run)
                and len(run) <= (5 if capitalised else 3)
                and len(" ".join(run)) > 1):
            found.append(" ".join(run))
        run.clear()

    for w in words:
        if w.lower() in _STOP or w in _CAPS_IGNORE or not re.search(r"[A-Za-z]", w):
            flush()
        elif _is_tech(w):
            flush()
            found.append(w)
        else:
            run.append(w)
    flush()
    return found


def _dedupe(items: list[str], seen: set | None = None) -> list[str]:
    seen = set() if seen is None else seen
    out = []
    for item in items:
        if item.lower() not in seen:
            seen.add(item.lower())
            out.append(item)
    return out


def extract_keyword_groups(posting_md: str) -> dict:
    """{"must": [...], "nice": [...]}: a saved posting's keywords, at most 25 in all.

    Reads the body after `## Description` when there is one. Under
    requirement-style headings (Requirements, Qualifications, Skills, Must
    have, What you'll need…) every comma/semicolon/"and"-separated item
    becomes a candidate: tech tokens (Go, PostgreSQL, gRPC, AWS, C++…) on
    their own, other runs trimmed of generic words (experience, strong,
    team…). Nice-to-have/preferred/bonus sections fill "nice". When the
    sections give fewer than 5 keywords, the posting's tech tokens are added
    to "must". Deduped case-insensitively, in the posting's own spelling.
    """
    lines = _posting_body(posting_md).split("\n")
    found = {"must": [], "nice": []}
    section = None
    for line in lines:
        head = _heading(line)
        if head is not None:
            title, rest = head
            section = _section_kind(title)
            if not (section and rest):
                continue
            line = rest
        if section:
            found[section] += [c for words in _segments(line) for c in _chunks(words)]
    seen: set = set()
    must = _dedupe(found["must"], seen)
    nice = _dedupe(found["nice"], seen)
    if len(must) + len(nice) < 5:
        must += _dedupe([w for line in lines for words in _segments(line) for w in words
                         if w.lower() not in _STOP and _is_tech(w)], seen)
    must = must[:MAX_KEYWORDS]
    return {"must": must, "nice": nice[:MAX_KEYWORDS - len(must)]}


def extract_keywords(posting_md: str) -> list[str]:
    """Up to 25 keywords from a saved posting: must-haves first, then nice-to-haves."""
    groups = extract_keyword_groups(posting_md)
    return groups["must"] + groups["nice"]


# --- 6-second lint ------------------------------------------------------------------------

_EMAIL_RE = re.compile(r"[A-Za-z0-9._%+-]+@[A-Za-z0-9-]+(?:\.[A-Za-z0-9-]+)*\.[A-Za-z]{2,}")
_PHONE_RE = re.compile(r"(?<![\w/.])\+?\(?\d[\d \t().-]{5,}\d(?![\w/])")
_DATE_RANGE_RE = re.compile(
    r"(?:\d{1,2}[./-])?(?:19|20)\d\d[ \t]*[-.][ \t]*(?:\d{1,2}[./-])?(?:19|20)\d\d")
_URL_RE = re.compile(r"(?:https?://|www\.)\S+", re.I)
_YEAR_RE = re.compile(r"(?<!\d)(?:19|20)\d\d(?!\d)")
_PAREN_YEAR_RE = re.compile(r"\([^()\n]*?(?<!\d)(?:19|20)\d\d(?!\d)[^()\n]*\)")
_CURRENCY_BEFORE_RE = re.compile(
    r"(?:\b(?:RM|Rp|IDR|SGD|USD|MYR|PHP|THB|VND|EUR|GBP|INR|AUD|HKD|CNY|JPY)|[$€£¥₹])[ \t]?$")
_EXPERIENCE_HEADING_RE = re.compile(
    r"(?:work |professional )?(?:experience|employment(?: history)?|work history|career history):?",
    re.I)
PDF_METHODS = frozenset({"pypdf", "pdftotext-raw"})
SKIP_DATE = ("skip date: a PDF's text order follows its columns, not the page; "
             "lint the .md draft or .docx master")
SKIP_FIRST_BULLET = ("skip first-bullet: a PDF text layer carries no list markers; "
                     "lint the .md draft or .docx master")
_LINT_BULLET_RE = re.compile(r"^\s*[-•*●▪◦‣]\s+")
_TITLE_SKIP = frozenset({"and", "of", "the"})


def _blank(m: re.Match) -> str:
    return " " * len(m.group())


def _phones(text: str) -> list[str]:
    """Phone-like runs of 7–15 digits.

    Year ranges ("2019 - 2021"), parenthesised years ("(2017 - 2021)") and
    amounts after a currency ("IDR 10.000.000") do not count.
    """
    cleaned = _DATE_RANGE_RE.sub(_blank, _PAREN_YEAR_RE.sub(_blank, text))
    out = []
    for m in _PHONE_RE.finditer(cleaned):
        s = m.group().strip()
        if (7 <= len(re.sub(r"\D", "", s)) <= 15
                and not _CURRENCY_BEFORE_RE.search(cleaned[max(0, m.start() - 5):m.start()])):
            out.append(s)
    return out


def _first_experience_bullet(lines: list[str]) -> tuple[bool, str | None]:
    """(found an Experience heading, text of the first bullet after it or None)."""
    for i, line in enumerate(lines):
        if _EXPERIENCE_HEADING_RE.fullmatch(line.strip()):
            for later in lines[i + 1:]:
                m = _LINT_BULLET_RE.match(later)
                if m:
                    return True, later[m.end():].strip()
            return True, None
    return False, None


def lint_six_second(text: str, target_title: str | None = None, method: str | None = None) -> list[str]:
    """The recruiter's-skim lint: "ok <check>", "FAIL <check>: <why>" or "skip <check>: <why>".

    Checks: contact (email and a 7+ digit phone as literal text), date (a
    19xx/20xx year in the first 15 lines), first-bullet (a digit or % in the
    first bullet under an Experience heading), length (at most 900 words,
    about two pages) and, with `target_title`, title (every 3+ letter word of
    it, bar and/of/the, in the first 5 lines; "-" and space alike). With a PDF
    `method` ("pypdf", "pdftotext-raw") date and first-bullet are skipped: a
    PDF's text follows its columns and carries no list markers.
    """
    pdf = method in PDF_METHODS
    text = _fold(text)
    lines = [ln.strip() for ln in text.splitlines() if ln.strip()]
    findings = []

    has_email, has_phone = bool(_EMAIL_RE.search(text)), bool(_phones(text))
    if has_email and has_phone:
        findings.append("ok contact")
    else:
        missing = " or ".join(w for w, ok in (("email address", has_email),
                                                ("phone number (7+ digits)", has_phone)) if not ok)
        findings.append(f"FAIL contact: no {missing} as literal text")

    top = "\n".join(lines[:TOP_LINES_DATE])
    for pattern in (_EMAIL_RE, _URL_RE):
        top = pattern.sub(" ", top)
    for phone in _phones(top):
        top = top.replace(phone, " ")
    if pdf:
        findings.append(SKIP_DATE)
    elif _YEAR_RE.search(top):
        findings.append("ok date")
    else:
        findings.append(f"FAIL date: no year (19xx/20xx) in the first {TOP_LINES_DATE} lines")

    has_heading, bullet = _first_experience_bullet(lines)
    if pdf:
        findings.append(SKIP_FIRST_BULLET)
    elif bullet is not None and re.search(r"[\d%]", bullet):
        findings.append("ok first-bullet")
    elif bullet is not None:
        findings.append(f'FAIL first-bullet: no number in "{_one_line(bullet)}"')
    elif has_heading:
        findings.append('FAIL first-bullet: no "- " or "• " bullet under the Experience heading')
    else:
        findings.append("FAIL first-bullet: no Experience heading found")

    words = sum(1 for tok in text.split() if re.search(r"\w", tok))
    if words <= MAX_WORDS:
        findings.append(f"ok length: {words} words (limit {MAX_WORDS}, about 2 pages)")
    else:
        findings.append(f"FAIL length: {words} words, over the {MAX_WORDS}-word limit (about 2 pages)")

    if target_title is not None:
        wanted, seen = [], set()
        for w in re.findall(r"[^\W\d_]+(?:['-][^\W\d_]+)*", _fold(target_title)):
            letters = sum(c.isalpha() for c in w)
            if letters >= 3 and w.lower() not in _TITLE_SKIP and w.lower() not in seen:
                seen.add(w.lower())
                wanted.append(w)
        head = "\n".join(lines[:TOP_LINES_TITLE])
        absent = [w for w in wanted
                  if not re.search(r"(?<!\w)" + re.escape(w).replace(r"\-", r"[-\s]") + r"(?!\w)",
                                   head, re.I)]
        if not wanted:
            findings.append(f'FAIL title: "{target_title}" has no word of 3+ letters to check')
        elif absent:
            quoted = ", ".join(f'"{w}"' for w in absent)
            findings.append(f"FAIL title: {quoted} not in the first {TOP_LINES_TITLE} lines")
        else:
            findings.append("ok title")
    return findings


# --- anti-slop scan ---------------------------------------------------------------------------

def get_slop_phrases(path=None) -> list[str]:
    """The phrase list, one per line; blank lines and # comments skipped."""
    raw = Path(path or SLOP_FILE).read_text(encoding="utf-8-sig")
    return [s for s in (line.strip() for line in raw.splitlines()) if s and not s.startswith("#")]


def _phrase_regex(phrase: str) -> re.Pattern:
    p = _fold(phrase).strip()
    body = r"\s+".join(re.escape(w) for w in p.split()).replace(r"\-", r"[-\s]")
    left = r"(?<![^\W\d_])" if p[:1].isalpha() else ""
    right = r"(?![^\W\d_])" if p[-1:].isalpha() else ""
    return re.compile(left + body + right, re.I)


def slop_scan(text: str, phrases=None) -> list[tuple[str, int]]:
    """[(phrase, count)] for every banned phrase in `text`, most frequent first.

    Overlapping hits count once, for the longest phrase ("dynamic team
    player" is not also a "team player"); ties keep the list's order.
    """
    if phrases is None:
        phrases = get_slop_phrases()
    folded = _fold(text)
    order = {}
    spans = []
    for phrase in (p.strip() for p in phrases):
        if phrase and phrase not in order:
            order[phrase] = len(order)
            spans += [(m.start(), m.end(), phrase) for m in _phrase_regex(phrase).finditer(folded)]
    spans.sort(key=lambda sp: (sp[0] - sp[1], sp[0]))          # longest first, then leftmost
    taken, counts = [], {}
    for start, end, phrase in spans:
        if not any(start < t_end and t_start < end for t_start, t_end in taken):
            taken.append((start, end))
            counts[phrase] = counts.get(phrase, 0) + 1
    return sorted(counts.items(), key=lambda hit: (-hit[1], order[hit[0]]))


# --- report -------------------------------------------------------------------------------

def _coverage_lines(label: str, cov: dict) -> list[str]:
    total = len(cov["present"]) + len(cov["missing"])
    if not total:
        return [f'**{label}:** none found in the posting; pass --keywords "a,b" '
                "(the jd-match mirror list)"]
    line = f"**{label}:** {len(cov['present'])}/{total} present"
    if cov["missing"]:
        line += " — missing: " + ", ".join(cov["missing"])
    return [line] + (["present: " + ", ".join(cov["present"])] if cov["present"] else [])


def render_report(result: dict) -> str:
    out = [f"**Method:** {result['method']} ({result['file']})"]
    if result["empty"]:
        out.append("**Text layer:** empty, so an ATS would read nothing (image-only or flattened file)")
    if "keywords" in result:
        kw = result["keywords"]
        if "must_have" in kw:
            out += _coverage_lines("Keywords (must-have)", kw["must_have"])
            out += _coverage_lines("Keywords (nice-to-have)", kw["nice_to_have"])
        else:
            out += _coverage_lines("Keywords", kw)
    if "lint" in result:
        out.append("**Lint:**")
        out += result["lint"]
    if "slop" in result:
        if result["slop"]:
            out.append("**Slop:**")
            out += [f"{hit['phrase']} ×{hit['count']}" for hit in result["slop"]]
        else:
            out.append("**Slop:** none found")
    if "text" in result:
        out += ["**Text layer:**", "```text", result["text"].rstrip("\n"), "```"]
    return "\n".join(out)


def _fail(msg: str) -> int:
    print(f"ats_check.py: {msg}", file=sys.stderr)
    return 2


def main(argv=None) -> int:
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    ap = argparse.ArgumentParser(prog="ats_check.py", description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("file", type=Path, help="the built .docx/.pdf, or a .md/.txt draft")
    source = ap.add_mutually_exclusive_group()
    source.add_argument("--posting", type=Path, help="saved posting, e.g. postings/<slug>.md")
    source.add_argument("--keywords", help='comma-separated keywords, e.g. "Go,PostgreSQL,gRPC"')
    ap.add_argument("--lint", action="store_true", help="6-second lint")
    ap.add_argument("--target-title", help="target role title for the lint's title check")
    ap.add_argument("--slop", action="store_true", help="banned-phrase scan")
    ap.add_argument("--text", action="store_true", help="print the extracted text too")
    ap.add_argument("--json", action="store_true", help="print the report as JSON")
    a = ap.parse_args(argv)

    keywords, groups = None, None
    if a.keywords is not None:
        keywords = [k.strip() for k in re.split(r"[,;\n]", a.keywords) if k.strip()]
        if not keywords:
            return _fail("--keywords is empty: pass a comma-separated list")
    elif a.posting is not None:
        try:
            groups = extract_keyword_groups(a.posting.read_text(encoding="utf-8-sig", errors="replace"))
        except OSError as e:
            return _fail(f"cannot read the posting {a.posting}: {e.strerror or e}")
        keywords = groups["must"] + groups["nice"]
    phrases = None
    if a.slop:
        try:
            phrases = get_slop_phrases()
        except OSError as e:
            return _fail(f"cannot read the phrase list {SLOP_FILE}: {e.strerror or e}")
        except UnicodeDecodeError:
            return _fail(f"cannot read the phrase list {SLOP_FILE}: it is not UTF-8 text")

    try:
        text, method = extract_text(a.file)
    except OSError as e:
        return _fail(f"cannot read {a.file}: {e.strerror or e}")
    except ValueError as e:
        return _fail(f"{a.file}: {e}")
    if method == "unavailable":
        print(FALLBACK_LINE)
        return 2

    lint = a.lint or a.target_title is not None
    result = {"file": str(a.file), "method": method, "empty": not text.strip()}
    if keywords is not None:
        result["keywords"] = keyword_coverage(text, keywords)
        if groups and groups["nice"]:
            result["keywords"]["must_have"] = keyword_coverage(text, groups["must"])
            result["keywords"]["nice_to_have"] = keyword_coverage(text, groups["nice"])
    if lint:
        result["lint"] = lint_six_second(text, target_title=a.target_title or None, method=method)
    if phrases is not None:
        result["slop"] = [{"phrase": p, "count": n} for p, n in slop_scan(text, phrases)]
    if a.text or not (keywords is not None or lint or phrases is not None):
        result["text"] = text
    print(json.dumps(result, indent=2, ensure_ascii=False) if a.json else render_report(result))
    return 0


if __name__ == "__main__":
    sys.exit(main())
