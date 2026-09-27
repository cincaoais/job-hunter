#!/usr/bin/env python3
"""Resume markdown -> ATS .docx master, presentation HTML/PDF, JSON Resume.

  python3 build_resume.py resumes/<file>.md --docx [--pdf --template <name>] [--html] [--json]
                          [--photo PATH] [--out DIR]

Reads the builder's Template A or Template B markdown (`# Name`, a
`Title · City · phone · email · links` line, then `##` sections with `###`
entries `Title — Company, City · MM/YYYY – Present` and `-` bullets).

  --docx   single-column ATS master (stdlib zip + XML): real bullets, dates
           on a right tab stop, no tables, images, headers or footers
  --html   presentation copy from assets/templates/<template>.html
  --pdf    that HTML rendered to A4 by headless Chromium (playwright, else
           cloakbrowser); with neither, the .html is written instead and a
           "PDF skipped" line says how to get the PDF
  --json   JSON Resume v1 (for the Reactive Resume MCP import)

Templates: chicago (default), executive, corporate-sidebar, accent-band,
creative-sidebar. --photo goes into the presentation copy only; the .docx
never carries one. Outputs land next to the input with the same stem unless
--out DIR is given, and each written path is printed.
Exit codes: 0 on success (including "PDF skipped"), 2 for bad arguments or
input without a `# Name` line.
"""
from __future__ import annotations

import argparse
import base64
import datetime
import html
import io
import json
import re
import sys
import tempfile
import zipfile
from pathlib import Path
from urllib.parse import urlparse

sys.path.insert(0, str(Path(__file__).resolve().parent))

from _common import optional_import, slugify  # noqa: E402

TEMPLATE_DIR = Path(__file__).resolve().parent.parent / "assets" / "templates"
TEMPLATES = ("chicago", "executive", "corporate-sidebar", "accent-band", "creative-sidebar")
SIDEBAR_TEMPLATES = frozenset({"corporate-sidebar", "creative-sidebar"})
PDF_SKIPPED = ("PDF skipped: pip install playwright && playwright install chromium "
               "(or open the .html and print to PDF)")

# --- markdown -> dict -----------------------------------------------------------

_HEADING_RE = re.compile(r"^(#{1,6})\s+(.*?)(?:\s+#+)?\s*$")
_BULLET_RE = re.compile(r"^\s*[-*+•]\s+(.*)$")
_LABEL_RE = re.compile(r"^\*\*([^*]+?)(?::\*\*|\*\*:)\s*(.*)$")      # **Label:** text / **Label**: text
_RULE_RE = re.compile(r"^(?:[-*_]\s*){3,}$")
_SUMMARY_RE = re.compile(r"summary|profile|about|objective", re.I)
_PROOF_RE = re.compile(r"proof", re.I)
_SKILLS_RE = re.compile(r"skill", re.I)
_SIDEBAR_RE = re.compile(r"skill|certif|languag", re.I)
_MAIN_ONLY_RE = re.compile(r"proof|educat|experien", re.I)
_DATEISH_RE = re.compile(r"\b(?:19|20)\d{2}\b|\b(?:present|current|now)\b", re.I)
_DATE_PART = r"(?:(?:\d{1,2}/)?\d{4}|[A-Za-z]{3,9}\.?\s+\d{4})"
_DATE_ONLY_RE = re.compile(
    rf"{_DATE_PART}(?:\s*[–—-]\s*(?:{_DATE_PART}|present|current|now))?", re.I)


def _create_entry(heading: str = "", meta: str = "") -> dict:
    org_loc, dates = _split_meta(meta)
    return {"heading": heading, "meta": meta, "org_loc": org_loc, "dates": dates,
            "bullets": [], "lines": [], "groups": [], "labeled": False}


def _split_meta(meta: str) -> tuple[str, str]:
    """`Company, City · 01/2022 – Present` -> (org_loc, dates)."""
    for sep in (" · ", " — ", " | "):
        if sep in meta:
            head, tail = meta.rsplit(sep, 1)
            if _DATEISH_RE.search(tail):
                return head.strip(), tail.strip()
    if _DATE_ONLY_RE.fullmatch(meta.strip()):
        return "", meta.strip()
    return meta.strip(), ""


def _split_heading(text: str) -> tuple[str, str]:
    """`Title — rest` -> (title, rest); other dashes only outside the dates."""
    text = text.strip()
    if " — " in text:
        heading, meta = text.split(" — ", 1)
        return heading.strip(), meta.strip()
    body, dates = text, ""
    if " · " in text:
        head, tail = text.rsplit(" · ", 1)
        if _DATEISH_RE.search(tail):
            body, dates = head, tail
    heading, meta = body, ""
    for sep in (" – ", " | ", " - "):
        if sep in body:
            heading, meta = body.split(sep, 1)
            break
    if dates:
        meta = f"{meta.strip()} · {dates}" if meta.strip() else dates
    return heading.strip(), meta.strip()


def _split_items(text: str) -> list[str]:
    """Split on commas and ` · ` that sit outside parentheses."""
    items, depth, buf = [], 0, []
    i = 0
    while i < len(text):
        ch = text[i]
        if ch in "([":
            depth += 1
        elif ch in ")]":
            depth = max(0, depth - 1)
        if depth == 0 and (ch == "," or text.startswith(" · ", i)):
            items.append("".join(buf))
            buf = []
            i += 3 if ch == " " else 1
            continue
        buf.append(ch)
        i += 1
    items.append("".join(buf))
    return [s.strip() for s in items if s.strip()]


def _is_list(text: str) -> bool:
    """Short comma-separated items (a skill list), not a sentence of proof."""
    items = _split_items(text)
    return bool(items) and all(len(_plain(it).split()) <= 5 for it in items)


def _skill_groups(line: str) -> list[dict] | None:
    """`**Languages:** Go, Python · **Cloud:** AWS` -> groups; None when it is prose."""
    parts = re.split(r"\s+·\s+(?=\*\*)", line.strip())
    groups = []
    for part in parts:
        m = _LABEL_RE.match(part)
        label, rest = (m.group(1).strip(), m.group(2)) if m else ("", part)
        if not _is_list(rest):
            return None
        groups.append({"label": label, "items": [_plain(it) for it in _split_items(rest)]})
    return groups


def _section_kind(title: str) -> str:
    if _PROOF_RE.search(title):
        return "proof"
    if _SKILLS_RE.search(title):
        return "skills"
    if _SUMMARY_RE.search(title):
        return "summary"
    return "other"


def parse_resume(md: str) -> dict:
    """Parse builder-template markdown into name/headline/contact/sections.

    Raises ValueError when there is no `# Name` line.
    """
    name = None
    header: list[str] = []
    sections: list[dict] = []
    section = entry = None
    last: tuple[list, int] | None = None   # the string a continuation line extends
    after_bullet = False                    # `last` is a bullet: an unindented hard wrap extends it
    blank = False

    def target_entry() -> dict:
        nonlocal entry
        if entry is None or entry["labeled"]:
            entry = _create_entry()
            section["entries"].append(entry)
        return entry

    for raw in md.replace("\r\n", "\n").replace("\r", "\n").split("\n"):
        line = raw.rstrip()
        stripped = line.strip()
        heading = _HEADING_RE.match(stripped)
        if name is None:
            if heading and len(heading.group(1)) == 1:
                name = heading.group(2)
            continue
        if not stripped or stripped.startswith("<!--") or _RULE_RE.fullmatch(stripped):
            blank = True
            continue
        if heading and len(heading.group(1)) <= 2:
            section = {"title": heading.group(2), "entries": []}
            sections.append(section)
            entry, last, after_bullet, blank = None, None, False, False
            continue
        if heading:
            if section is None:
                section = {"title": "", "entries": []}
                sections.append(section)
            entry = _create_entry(*_split_heading(heading.group(2)))
            section["entries"].append(entry)
            last, after_bullet, blank = None, False, False
            continue
        if section is None:
            header.append(stripped)
            continue

        kind = _section_kind(section["title"])
        bullet = _BULLET_RE.match(line)
        continues = last is not None and not blank and (after_bullet or kind == "summary")
        if bullet:
            text = bullet.group(1).strip()
            label = _LABEL_RE.match(text) if kind in ("proof", "skills") else None
            if kind == "skills" and (groups := _skill_groups(text)):
                target_entry()["groups"].extend(groups)
                last = None
            elif label:
                entry = _create_entry(label.group(1).strip())
                entry["labeled"] = True
                entry["lines"].append(label.group(2).strip())
                section["entries"].append(entry)
                last = (entry["lines"], 0)
            else:
                bullets = target_entry()["bullets"]
                bullets.append(text)
                last = (bullets, len(bullets) - 1)
            after_bullet = last is not None
        elif continues or (last is not None and (raw[:2] == "  " or raw[:1] == "\t")):
            seq, idx = last                  # wrapped continuation of the previous bullet/line
            seq[idx] = f"{seq[idx]} {stripped}"
        elif kind == "skills" and (groups := _skill_groups(stripped)):
            target_entry()["groups"].extend(groups)
            last, after_bullet = None, False
        else:
            lines = target_entry()["lines"]
            lines.append(stripped)
            last, after_bullet = (lines, len(lines) - 1), False
        blank = False

    if not name:
        raise ValueError("no '# Name' line — the resume must start with '# Full Name'")
    items = [_link_target(i.strip()) for i in re.split(r"\s+[·|•]\s+", " · ".join(header)) if i.strip()]
    headline = items.pop(0) if items and _contact_kind(items[0]) == "text" else ""
    return {"name": name, "headline": headline, "contact": items, "sections": sections}


# --- inline markdown and contact items -------------------------------------------

_INLINE_RE = re.compile(
    r"\*\*(?P<b>.+?)\*\*"
    r"|(?<![\w*])\*(?P<i>[^*\s](?:[^*]*[^*\s])?)\*(?![\w*])"
    r"|\[(?P<lt>[^\]]+)\]\((?P<lu>[^)\s]+)\)"
    r"|`(?P<c>[^`]+)`")


def _segments(text: str) -> list[tuple[str, str, str]]:
    """Split inline markdown into (kind, text, url) with kind bold/italic/link/text."""
    out, pos = [], 0
    for m in _INLINE_RE.finditer(text):
        if m.start() > pos:
            out.append(("text", text[pos:m.start()], ""))
        if m.group("b") is not None:
            out.append(("bold", m.group("b"), ""))
        elif m.group("i") is not None:
            out.append(("italic", m.group("i"), ""))
        elif m.group("lt") is not None:
            out.append(("link", m.group("lt"), m.group("lu")))
        else:
            out.append(("text", m.group("c"), ""))
        pos = m.end()
    if pos < len(text):
        out.append(("text", text[pos:], ""))
    return out


def _link_plain(label: str, url: str) -> str:
    shown = re.sub(r"^mailto:", "", url)
    return label if label.strip() in (url, shown) else f"{label} ({shown})"


def _plain(text: str) -> str:
    """Inline markdown stripped to the words an ATS should read."""
    return "".join(_link_plain(t, u) if k == "link" else t for k, t, u in _segments(text or ""))


def _link_target(item: str) -> str:
    m = re.fullmatch(r"\[([^\]]+)\]\(([^)\s]+)\)", item)
    return re.sub(r"^mailto:", "", m.group(2)) if m else _plain(item)


_EMAIL_RE = re.compile(r"^[^@\s]+@[^@\s]+\.[^@\s]+$")
_URL_RE = re.compile(r"^(?:https?://|www\.)|^(?:[\w-]+\.)*(?:linkedin\.com|github\.com)(?:/|$)", re.I)
_PHONE_RE = re.compile(r"^\+?[\d\s().-]+$")


def _contact_kind(item: str) -> str:
    if "@" in item and _EMAIL_RE.match(item):
        return "email"
    if _URL_RE.match(item):
        return "url"
    if _PHONE_RE.match(item) and len(re.sub(r"\D", "", item)) >= 7:
        return "phone"
    return "text"


def _full_url(item: str) -> str:
    return item if re.match(r"https?://", item, re.I) else f"https://{item}"


def _split_trailing_date(line: str) -> tuple[str, str]:
    """`Degree — School — 2021` -> ("Degree — School", "2021"); ("line", "") otherwise."""
    for sep in (" — ", " · ", " | "):
        if sep in line:
            head, tail = line.rsplit(sep, 1)
            if _DATE_ONLY_RE.fullmatch(tail.strip()):
                return head.strip(), tail.strip()
    return line, ""


# --- dates ------------------------------------------------------------------------

_MONTHS = {m: i for i, m in enumerate(
    ("jan", "feb", "mar", "apr", "may", "jun", "jul", "aug", "sep", "oct", "nov", "dec"), 1)}


def _iso(part: str) -> str | None:
    p = part.strip().rstrip(".")
    if m := re.fullmatch(r"(\d{1,2})[/.](\d{4})", p):
        month, year = int(m.group(1)), m.group(2)
        return f"{year}-{month:02d}" if 1 <= month <= 12 else year
    if m := re.fullmatch(r"(\d{4})-(\d{1,2})", p):
        return f"{m.group(1)}-{int(m.group(2)):02d}"
    if m := re.fullmatch(r"([A-Za-z]{3,9})\.?\s+(\d{4})", p):
        month = _MONTHS.get(m.group(1)[:3].lower())
        return f"{m.group(2)}-{month:02d}" if month else m.group(2)
    if re.fullmatch(r"\d{4}", p):
        return p
    return None


def split_dates(text: str) -> tuple[str | None, str | None]:
    """`MM/YYYY – MM/YYYY|Present` -> (start, end) as JSON Resume `YYYY-MM`/`YYYY`.

    `end` is None for a current role (Present/Current/Now) or a single date.
    """
    t = (text or "").strip()
    parts = re.split(r"\s*[–—]\s*|\s+-\s+|\s+to\s+", t, maxsplit=1)
    if len(parts) == 1 and (m := re.fullmatch(r"(\d{4})-(\d{4}|present|current|now)", t, re.I)):
        parts = [m.group(1), m.group(2)]
    start = _iso(parts[0]) if parts and parts[0] else None
    end = _iso(parts[1]) if len(parts) > 1 else None
    return start, end


# --- .docx (stdlib zip + XML) --------------------------------------------------------

_W_NS = "http://schemas.openxmlformats.org/wordprocessingml/2006/main"
_R_NS = "http://schemas.openxmlformats.org/officeDocument/2006/relationships"
_PKG_REL = "http://schemas.openxmlformats.org/package/2006/relationships"
_DOC_REL = "http://schemas.openxmlformats.org/officeDocument/2006/relationships"
_XML_DECL = '<?xml version="1.0" encoding="UTF-8" standalone="yes"?>\n'
PAGE_W, PAGE_H, MARGIN = 11906, 16838, 1134      # A4 in twips, 20 mm margins
TEXT_W = PAGE_W - 2 * MARGIN                      # 9638: the right tab stop for dates
_ACCENT_HEX = "1F3864"
_XML_BAD_RE = re.compile(r"[\x00-\x08\x0b\x0c\x0e-\x1f]")


def _x(text: str) -> str:
    """XML-escape & < > " ' and drop characters XML 1.0 cannot hold."""
    return html.escape(_XML_BAD_RE.sub("", text.replace("\t", " ")), quote=True)


def _run(text: str, bold: bool | None = None, italic: bool = False) -> str:
    rpr = ""
    if bold is not None or italic:
        rpr = "<w:rPr>" + ("" if bold is None else ("<w:b/>" if bold else '<w:b w:val="0"/>')) \
              + ("<w:i/>" if italic else "") + "</w:rPr>"
    return f'<w:r>{rpr}<w:t xml:space="preserve">{_x(text)}</w:t></w:r>'


def _runs(text: str) -> str:
    out = []
    for kind, t, u in _segments(text):
        if kind == "bold":
            out.append(_run(t, bold=True))
        elif kind == "italic":
            out.append(_run(t, italic=True))
        elif kind == "link":
            out.append(_run(_link_plain(t, u)))
        else:
            out.append(_run(t))
    return "".join(out)


_TAB_RUN = "<w:r><w:tab/></w:r>"


def _p(runs: str, style: str | None = None, bullet: bool = False, right_tab: bool = False) -> str:
    ppr = ""
    if style:
        ppr += f'<w:pStyle w:val="{style}"/>'
    if bullet:
        ppr += '<w:numPr><w:ilvl w:val="0"/><w:numId w:val="1"/></w:numPr>'
    if right_tab:
        ppr += f'<w:tabs><w:tab w:val="right" w:pos="{TEXT_W}"/></w:tabs>'
    return f"<w:p>{f'<w:pPr>{ppr}</w:pPr>' if ppr else ''}{runs}</w:p>"


def _docx_entry(e: dict) -> list[str]:
    out = []
    if e["labeled"]:
        out.append(_p(_run(f"{_plain(e['heading'])}: ", bold=True) + _runs(" ".join(e["lines"])), bullet=True))
    else:
        if e["heading"]:
            runs = _run(_plain(e["heading"]))
            if e["org_loc"]:
                runs += _run(f" — {_plain(e['org_loc'])}", bold=False)
            if e["dates"]:
                runs += _TAB_RUN + _run(e["dates"], bold=False)
            out.append(_p(runs, style="Heading2"))
        for line in e["lines"]:
            text, date = _split_trailing_date(line)
            out.append(_p(_runs(text) + (_TAB_RUN + _run(date) if date else ""), right_tab=bool(date)))
        for g in e["groups"]:
            label = _run(f"{g['label']}: ", bold=True) if g["label"] else ""
            out.append(_p(label + _run(", ".join(g["items"]))))
    out.extend(_p(_runs(b), bullet=True) for b in e["bullets"])
    return out


def _docx_document(resume: dict) -> str:
    body = [_p(_run(_plain(resume["name"])), style="Title")]
    if resume["headline"]:
        body.append(_p(_run(_plain(resume["headline"])), style="Subtitle"))
    if resume["contact"]:
        body.append(_p(_run(" | ".join(resume["contact"]))))
    for section in resume["sections"]:
        if section["title"]:
            body.append(_p(_run(_plain(section["title"])), style="Heading1"))
        for e in section["entries"]:
            body.extend(_docx_entry(e))
    sect = (f'<w:sectPr><w:pgSz w:w="{PAGE_W}" w:h="{PAGE_H}"/>'
            f'<w:pgMar w:top="{MARGIN}" w:right="{MARGIN}" w:bottom="{MARGIN}" w:left="{MARGIN}" '
            'w:header="709" w:footer="709" w:gutter="0"/></w:sectPr>')
    return (f'{_XML_DECL}<w:document xmlns:w="{_W_NS}" xmlns:r="{_R_NS}"><w:body>'
            f'{"".join(body)}{sect}</w:body></w:document>')


def _rpr(size_half_pts: int, bold: bool = False, color: str | None = None) -> str:
    return ("<w:rPr>" + ("<w:b/><w:bCs/>" if bold else "") + (f'<w:color w:val="{color}"/>' if color else "")
            + f'<w:sz w:val="{size_half_pts}"/><w:szCs w:val="{size_half_pts}"/></w:rPr>')


def _style(style_id: str, name: str, ppr: str, rpr: str, default: bool = False, ui: int = 0) -> str:
    return (f'<w:style w:type="paragraph"{" w:default=\"1\"" if default else ""} w:styleId="{style_id}">'
            f'<w:name w:val="{name}"/>' + ("" if default else '<w:basedOn w:val="Normal"/><w:next w:val="Normal"/>')
            + (f'<w:uiPriority w:val="{ui}"/>' if ui else "") + f"<w:qFormat/><w:pPr>{ppr}</w:pPr>{rpr}</w:style>")


def _docx_styles() -> str:
    font = '<w:rFonts w:ascii="Calibri" w:hAnsi="Calibri" w:eastAsia="Calibri" w:cs="Calibri"/>'
    return (f'{_XML_DECL}<w:styles xmlns:w="{_W_NS}"><w:docDefaults>'
            f'<w:rPrDefault><w:rPr>{font}<w:sz w:val="21"/><w:szCs w:val="21"/><w:lang w:val="en-US"/></w:rPr></w:rPrDefault>'
            '<w:pPrDefault><w:pPr><w:spacing w:after="40" w:line="259" w:lineRule="auto"/></w:pPr></w:pPrDefault>'
            "</w:docDefaults>"
            + _style("Normal", "Normal", '<w:spacing w:after="40"/>', _rpr(21), default=True)
            + _style("Title", "Title", '<w:spacing w:after="20"/>', _rpr(40, bold=True), ui=10)
            + _style("Subtitle", "Subtitle", '<w:spacing w:after="20"/>', _rpr(24, color=_ACCENT_HEX), ui=11)
            + _style("Heading1", "heading 1",
                     f'<w:keepNext/><w:pBdr><w:bottom w:val="single" w:sz="6" w:space="1" w:color="{_ACCENT_HEX}"/>'
                     '</w:pBdr><w:spacing w:before="220" w:after="80"/><w:outlineLvl w:val="0"/>',
                     _rpr(26, bold=True, color=_ACCENT_HEX), ui=9)
            + _style("Heading2", "heading 2",
                     f'<w:keepNext/><w:tabs><w:tab w:val="right" w:pos="{TEXT_W}"/></w:tabs>'
                     '<w:spacing w:before="140" w:after="20"/><w:outlineLvl w:val="1"/>',
                     _rpr(22, bold=True), ui=9)
            + "</w:styles>")


def _docx_numbering() -> str:
    # U+F0B7 in the Symbol font is Word's own bullet glyph: no literal "•" in the XML.
    return (f'{_XML_DECL}<w:numbering xmlns:w="{_W_NS}"><w:abstractNum w:abstractNumId="0">'
            '<w:multiLevelType w:val="singleLevel"/><w:lvl w:ilvl="0"><w:start w:val="1"/>'
            '<w:numFmt w:val="bullet"/><w:lvlText w:val="&#xF0B7;"/><w:lvlJc w:val="left"/>'
            '<w:pPr><w:ind w:left="357" w:hanging="357"/></w:pPr>'
            '<w:rPr><w:rFonts w:ascii="Symbol" w:hAnsi="Symbol" w:hint="default"/></w:rPr></w:lvl>'
            '</w:abstractNum><w:num w:numId="1"><w:abstractNumId w:val="0"/></w:num></w:numbering>')


_CT = "application/vnd.openxmlformats-officedocument"
_PARTS_CT = {
    "word/document.xml": f"{_CT}.wordprocessingml.document.main+xml",
    "word/styles.xml": f"{_CT}.wordprocessingml.styles+xml",
    "word/numbering.xml": f"{_CT}.wordprocessingml.numbering+xml",
    "word/settings.xml": f"{_CT}.wordprocessingml.settings+xml",
    "docProps/core.xml": "application/vnd.openxmlformats-package.core-properties+xml",
    "docProps/app.xml": f"{_CT}.extended-properties+xml",
}


def _rels(rels: list[tuple[str, str]]) -> str:
    items = "".join(f'<Relationship Id="rId{i}" Type="{t}" Target="{target}"/>'
                    for i, (t, target) in enumerate(rels, 1))
    return f'{_XML_DECL}<Relationships xmlns="{_PKG_REL}">{items}</Relationships>'


def docx_bytes(resume: dict) -> bytes:
    """The ATS master as .docx bytes: single column, styles, real bullets, right-tab dates."""
    name = _x(_plain(resume["name"]))
    now = datetime.datetime.now(datetime.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    overrides = "".join(f'<Override PartName="/{p}" ContentType="{ct}"/>' for p, ct in _PARTS_CT.items())
    parts = {
        "[Content_Types].xml": (
            f'{_XML_DECL}<Types xmlns="http://schemas.openxmlformats.org/package/2006/content-types">'
            '<Default Extension="rels" ContentType="application/vnd.openxmlformats-package.relationships+xml"/>'
            f'<Default Extension="xml" ContentType="application/xml"/>{overrides}</Types>'),
        "_rels/.rels": _rels([
            (f"{_DOC_REL}/officeDocument", "word/document.xml"),
            (f"{_PKG_REL}/metadata/core-properties", "docProps/core.xml"),
            (f"{_DOC_REL}/extended-properties", "docProps/app.xml")]),
        "word/_rels/document.xml.rels": _rels([
            (f"{_DOC_REL}/styles", "styles.xml"),
            (f"{_DOC_REL}/numbering", "numbering.xml"),
            (f"{_DOC_REL}/settings", "settings.xml")]),
        "word/document.xml": _docx_document(resume),
        "word/styles.xml": _docx_styles(),
        "word/numbering.xml": _docx_numbering(),
        "word/settings.xml": (
            f'{_XML_DECL}<w:settings xmlns:w="{_W_NS}"><w:defaultTabStop w:val="720"/>'
            '<w:characterSpacingControl w:val="doNotCompress"/><w:compat><w:compatSetting '
            'w:name="compatibilityMode" w:uri="http://schemas.microsoft.com/office/word" w:val="15"/>'
            "</w:compat></w:settings>"),
        "docProps/core.xml": (
            f'{_XML_DECL}<cp:coreProperties xmlns:cp="http://schemas.openxmlformats.org/package/2006/metadata/'
            'core-properties" xmlns:dc="http://purl.org/dc/elements/1.1/" xmlns:dcterms="http://purl.org/dc/terms/" '
            'xmlns:dcmitype="http://purl.org/dc/dcmitype/" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance">'
            f"<dc:title>{name}</dc:title><dc:creator>{name}</dc:creator>"
            f'<dcterms:created xsi:type="dcterms:W3CDTF">{now}</dcterms:created>'
            f'<dcterms:modified xsi:type="dcterms:W3CDTF">{now}</dcterms:modified></cp:coreProperties>'),
        "docProps/app.xml": (
            f'{_XML_DECL}<Properties xmlns="http://schemas.openxmlformats.org/officeDocument/2006/'
            'extended-properties"><Application>job-hunter build_resume.py</Application></Properties>'),
    }
    buf = io.BytesIO()
    with zipfile.ZipFile(buf, "w", zipfile.ZIP_DEFLATED) as z:
        for part, xml in parts.items():
            info = zipfile.ZipInfo(part, date_time=(2020, 1, 1, 0, 0, 0))
            info.compress_type = zipfile.ZIP_DEFLATED
            z.writestr(info, xml.encode("utf-8"))
    return buf.getvalue()


# --- HTML -------------------------------------------------------------------------------

def _esc(text: str) -> str:
    return html.escape(text or "", quote=True)


def _safe_href(url: str) -> str:
    if re.match(r"(?:https?:|mailto:|tel:)", url, re.I):
        return url
    return _full_url(url) if _URL_RE.match(url) else ""


def _inline_html(text: str) -> str:
    out = []
    for kind, t, u in _segments(text or ""):
        if kind == "bold":
            out.append(f"<strong>{_esc(t)}</strong>")
        elif kind == "italic":
            out.append(f"<em>{_esc(t)}</em>")
        elif kind == "link" and (href := _safe_href(u)):
            out.append(f'<a href="{_esc(href)}">{_esc(t)}</a>')
        else:
            out.append(_esc(t))
    return "".join(out)


def _groups_html(groups: list[dict]) -> str:
    rows = []
    for g in groups:
        label = (f'<span class="skill-label">{_esc(g["label"])}</span><span class="skill-colon">: </span>'
                 if g["label"] else "")
        n = len(g["items"])
        items = "".join(f'<li>{_esc(it)}{"<span class=\"sep\">, </span>" if i < n - 1 else ""}</li>'
                        for i, it in enumerate(g["items"]))
        rows.append(f'<div class="skill-group">{label}<ul class="tags">{items}</ul></div>')
    return f'<div class="skills">{"".join(rows)}</div>'


def _line_html(line: str) -> str:
    text, date = _split_trailing_date(line)
    if date:
        return (f'<p class="line dated"><span class="line-text">{_inline_html(text)}</span>'
                f'<span class="dates">{_esc(date)}</span></p>')
    return f'<p class="line">{_inline_html(line)}</p>'


def _entry_html(e: dict) -> str:
    head = ""
    if e["heading"]:
        org = (f'<span class="org-sep"> — </span><span class="org">{_inline_html(e["org_loc"])}</span>'
               if e["org_loc"] else "")
        dates = f'<span class="dates">{_esc(e["dates"])}</span>' if e["dates"] else ""
        head = (f'<div class="entry-head"><h3 class="entry-title"><span class="role">'
                f'{_inline_html(e["heading"])}</span>{org}</h3>{dates}</div>')
    lines = "".join(_line_html(line) for line in e["lines"])
    groups = _groups_html(e["groups"]) if e["groups"] else ""
    bullets = ("<ul class=\"bullets\">" + "".join(f"<li>{_inline_html(b)}</li>" for b in e["bullets"])
               + "</ul>") if e["bullets"] else ""
    return f'<div class="entry">{head}{lines}{groups}{bullets}</div>'


def _section_html(section: dict) -> str:
    out = [f'<section class="section section-{slugify(section["title"]) or "intro"}">']
    if section["title"]:
        out.append(f'<h2 class="section-title">{_inline_html(section["title"])}</h2>')
    proof: list[str] = []
    for e in section["entries"] + [None]:
        if e is not None and e["labeled"]:
            proof.append(f'<li><strong class="proof-label">{_inline_html(e["heading"])}:</strong> '
                         f'{_inline_html(" ".join(e["lines"]))}</li>')
            continue
        if proof:
            out.append(f'<ul class="bullets proof">{"".join(proof)}</ul>')
            proof = []
        if e is not None:
            out.append(_entry_html(e))
    out.append("</section>")
    return "".join(out)


def _contact_html(items: list[str]) -> str:
    lis = []
    for item in items:
        kind = _contact_kind(item)
        if kind == "email":
            lis.append(f'<li class="contact-email"><a href="mailto:{_esc(item)}">{_esc(item)}</a></li>')
        elif kind == "url":
            shown = re.sub(r"^(?:https?://)?(?:www\.)?", "", item, flags=re.I).rstrip("/")
            lis.append(f'<li class="contact-url"><a href="{_esc(_full_url(item))}">{_esc(shown)}</a></li>')
        elif kind == "phone":
            lis.append(f'<li class="contact-phone">{_esc(item)}</li>')
        else:
            lis.append(f'<li class="contact-location">{_esc(item)}</li>')
    return f'<ul class="contact">{"".join(lis)}</ul>' if lis else ""


_PHOTO_TYPES = {".jpg": "image/jpeg", ".jpeg": "image/jpeg", ".png": "image/png", ".webp": "image/webp"}


def _photo_html(photo, name: str) -> str:
    path = Path(photo)
    mime = _PHOTO_TYPES.get(path.suffix.lower())
    if mime is None:
        raise ValueError(f"photo must be .jpg, .png or .webp: {path}")
    data = base64.b64encode(path.read_bytes()).decode("ascii")
    return f'<img class="photo" src="data:{mime};base64,{data}" alt="Headshot of {_esc(_plain(name))}">'


def is_sidebar_section(title: str) -> bool:
    """Skills, certifications and languages go to a sidebar template's side column."""
    return bool(_SIDEBAR_RE.search(title)) and not _MAIN_ONLY_RE.search(title)


def html_str(resume: dict, template_name: str, photo=None) -> str:
    """Fill assets/templates/<template_name>.html; `photo` is an image path or None."""
    if template_name not in TEMPLATES:
        raise ValueError(f"unknown template {template_name!r} (choose: {', '.join(TEMPLATES)})")
    template = (TEMPLATE_DIR / f"{template_name}.html").read_text(encoding="utf-8")
    to_side = [template_name in SIDEBAR_TEMPLATES and is_sidebar_section(s["title"])
               for s in resume["sections"]]
    values = {
        "name": _esc(_plain(resume["name"])),
        "headline": _esc(_plain(resume["headline"])),
        "contact_html": _contact_html(resume["contact"]),
        "sections_html": "\n".join(_section_html(s) for s, side in zip(resume["sections"], to_side) if not side),
        "sidebar_html": "\n".join(_section_html(s) for s, side in zip(resume["sections"], to_side) if side),
        "photo_html": _photo_html(photo, resume["name"]) if photo else "",
    }
    return re.sub(r"\{\{\s*(\w+)\s*\}\}", lambda m: values.get(m.group(1), ""), template)


# --- PDF ---------------------------------------------------------------------------------

def _print_pdf(browser, page_url: str, out: Path) -> None:
    try:
        page = browser.new_page()
        page.goto(page_url, wait_until="load")
        page.pdf(path=str(out), format="A4", print_background=True, prefer_css_page_size=True)
    finally:
        browser.close()


def render_pdf(html_text: str, out: Path, failures: list[str] | None = None) -> str | None:
    """Render with playwright's Chromium, else cloakbrowser; the backend used, or None.

    The page loads from a transient file next to `out` (cloakbrowser's
    Chromium hangs on `set_content`), removed again afterwards. A backend
    that imports but fails is recorded in `failures` as "name (ErrorClass)".
    """
    failures = [] if failures is None else failures
    with tempfile.NamedTemporaryFile("w", encoding="utf-8", suffix=".html", prefix=f".{out.stem}-",
                                     dir=out.parent, delete=False) as tmp:
        tmp.write(html_text)
    page_url = Path(tmp.name).resolve().as_uri()
    try:
        sync_api = optional_import("playwright.sync_api")
        if sync_api is not None:
            try:
                with sync_api.sync_playwright() as pw:
                    _print_pdf(pw.chromium.launch(headless=True), page_url, out)
                return "playwright"
            except Exception as exc:  # noqa: BLE001 — missing browser build, sandbox, event loop: next backend
                failures.append(f"playwright ({exc.__class__.__name__})")
        cloak = optional_import("cloakbrowser")
        if cloak is not None:
            try:
                try:  # no fingerprint spoofing: it can hide installed fonts from the print
                    browser = cloak.launch(headless=True, stealth_args=False)
                except TypeError:
                    browser = cloak.launch(headless=True)
                _print_pdf(browser, page_url, out)
                return "cloakbrowser"
            except Exception as exc:  # noqa: BLE001
                failures.append(f"cloakbrowser ({exc.__class__.__name__})")
        return None
    finally:
        Path(tmp.name).unlink(missing_ok=True)


# --- JSON Resume --------------------------------------------------------------------------

_EXPERIENCE_RE = re.compile(r"experience|employment|work history|career history", re.I)
_EDU_RE = re.compile(r"educat|qualification", re.I)
_CERT_RE = re.compile(r"certif|licen[cs]", re.I)
_LANG_RE = re.compile(r"languag", re.I)
_PROJECT_RE = re.compile(r"project", re.I)
_DEGREE_RE = re.compile(
    r"\b(?:B\.?\s?(?:Sc|A|Eng|Tech|Com|Ed|BA|IT|CS)|M\.?\s?(?:Sc|A|Eng|Tech|Phil|Ed|BA)|Ph\.?\s?D|BBA|MBA|"
    r"Bachelor|Master|Doctor(?:ate)?|Diploma|Degree|Associate(?:'s)? (?:Degree|of)|A-?Levels?|STPM|SPM|"
    r"Matriculation|Foundation in|High School|Secondary School)\b", re.I)
_CORP_SUFFIX_RE = re.compile(
    r"(?:inc|ltd|llc|llp|plc|co|corp|gmbh|bhd|sdn\.? bhd|pte\.? ltd|pty\.? ltd|s\.a|b\.v)\.?", re.I)
_NETWORKS = {"linkedin.com": "LinkedIn", "github.com": "GitHub", "gitlab.com": "GitLab",
             "behance.net": "Behance", "dribbble.com": "Dribbble", "x.com": "X", "twitter.com": "X"}
_SCHEMA = "https://raw.githubusercontent.com/jsonresume/resume-schema/v1.0.0/schema.json"


def _org_and_location(org_loc: str) -> tuple[str, str]:
    org_loc = _plain(org_loc)
    if ", " in org_loc:
        org, loc = org_loc.rsplit(", ", 1)
        if not _CORP_SUFFIX_RE.fullmatch(loc.strip()):
            return org.strip(), loc.strip()
    return org_loc.strip(), ""


def _with_dates(item: dict, dates: str, single_is_end: bool = False) -> dict:
    start, end = split_dates(dates)
    if single_is_end and end is None and not re.search(r"present|current|now", dates or "", re.I):
        start, end = None, start
    if start:
        item["startDate"] = start
    if end:
        item["endDate"] = end
    return item


def _edu_or_cert(line: str, title: str) -> tuple[str, dict]:
    text, date = _split_trailing_date(_plain(line))
    parts = [p.strip() for p in re.split(r"\s+[—|·]\s+", text) if p.strip()] or [text]
    start, end = split_dates(date) if date else (None, None)
    end = end or start
    is_degree = bool(_DEGREE_RE.search(text))
    if _CERT_RE.search(title) and not (_EDU_RE.search(title) and is_degree):
        cert = {"name": parts[0]}
        if len(parts) > 1:
            cert["issuer"] = parts[1]
        if end:
            cert["date"] = end
        return "certificates", cert
    if len(parts) > 1 and not _DEGREE_RE.search(parts[0]) and _DEGREE_RE.search(parts[1]):
        parts[0], parts[1] = parts[1], parts[0]
    edu = {"institution": parts[1]} if len(parts) > 1 else {}
    edu["area"] = parts[0]
    if end:
        edu["endDate"] = end
    return "education", edu


def _languages(text: str) -> list[dict]:
    out = []
    for item in _split_items(_plain(text)):
        m = re.fullmatch(r"(.+?)\s*(?:\((.+)\)|[:—–-]\s*(.+))", item)
        if m:
            out.append({"language": m.group(1).strip(), "fluency": (m.group(2) or m.group(3)).strip()})
        else:
            out.append({"language": item})
    return out


def json_resume(resume: dict) -> dict:
    """JSON Resume v1: basics, work, education, skills (+ certificates/languages/projects when present)."""
    basics: dict = {"name": _plain(resume["name"]), "label": _plain(resume["headline"])}
    profiles, location = [], None
    for item in resume["contact"]:
        kind = _contact_kind(item)
        if kind in ("email", "phone"):
            basics.setdefault(kind, item)
        elif kind == "url":
            url = _full_url(item)
            host = urlparse(url).netloc.lower().removeprefix("www.")
            network = next((n for h, n in _NETWORKS.items() if host == h or host.endswith("." + h)), None)
            if network:
                username = urlparse(url).path.rstrip("/").rsplit("/", 1)[-1]
                profiles.append({"network": network, "username": username, "url": url})
            else:
                basics.setdefault("url", url)
        elif location is None:
            location = item
    if location:
        basics["location"] = {"city": location.split(",")[0].strip()}
    basics["profiles"] = profiles

    out: dict = {"$schema": _SCHEMA, "basics": basics, "work": [], "education": [], "skills": []}
    extra: dict[str, list] = {"certificates": [], "languages": [], "projects": []}
    summary = []
    for section in resume["sections"]:
        title, kind = section["title"], _section_kind(section["title"])
        for e in section["entries"]:
            highlights = [_plain(b) for b in e["bullets"]]
            if kind == "summary":
                summary.extend(_plain(line) for line in e["lines"])
            elif kind == "proof" and e["labeled"]:
                out["skills"].append({"name": _plain(e["heading"]), "keywords": [_plain(" ".join(e["lines"]))]})
            elif kind == "skills" and e["groups"]:
                out["skills"].extend({"name": g["label"] or "Skills", "keywords": g["items"]} for g in e["groups"])
            elif _EXPERIENCE_RE.search(title) and e["heading"]:
                org, loc = _org_and_location(e["org_loc"])
                work = {"name": org, "position": _plain(e["heading"])}
                if loc:
                    work["location"] = loc
                _with_dates(work, e["dates"])
                if e["lines"]:
                    work["summary"] = " ".join(_plain(line) for line in e["lines"])
                work["highlights"] = highlights
                out["work"].append(work)
            elif _EDU_RE.search(title) or _CERT_RE.search(title):
                if e["heading"]:
                    org, _ = _org_and_location(e["org_loc"])
                    key, item = _edu_or_cert(f"{e['heading']} — {org}", title)
                    (out if key in out else extra)[key].append(_with_dates(item, e["dates"], single_is_end=True))
                for line in e["lines"] + e["bullets"]:
                    key, item = _edu_or_cert(line, title)
                    (out if key in out else extra)[key].append(item)
            elif _LANG_RE.search(title):
                for text in e["lines"] + e["bullets"]:
                    extra["languages"].extend(_languages(text))
            elif _PROJECT_RE.search(title) and e["heading"]:
                project = {"name": _plain(e["heading"])}
                if e["org_loc"] or e["lines"]:
                    project["description"] = " ".join(_plain(t) for t in [e["org_loc"], *e["lines"]] if t)
                _with_dates(project, e["dates"])
                project["highlights"] = highlights
                extra["projects"].append(project)
    if summary:
        basics["summary"] = " ".join(summary)
    out.update({k: v for k, v in extra.items() if v})
    return out


# --- CLI ------------------------------------------------------------------------------------

def _fail(msg: str) -> int:
    print(f"build_resume.py: {msg}", file=sys.stderr)
    return 2


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(prog="build_resume.py", description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("input", type=Path, help="resume markdown, e.g. resumes/<company>-<role>-v1.md")
    ap.add_argument("--docx", action="store_true", help="ATS master .docx")
    ap.add_argument("--pdf", action="store_true", help="presentation PDF from --template")
    ap.add_argument("--html", action="store_true", help="presentation HTML from --template")
    ap.add_argument("--json", action="store_true", help="JSON Resume v1 export")
    ap.add_argument("--template", choices=TEMPLATES, default="chicago", help="presentation template")
    ap.add_argument("--photo", type=Path, help="headshot for the presentation copy only")
    ap.add_argument("--out", type=Path, help="output directory (default: next to the input)")
    a = ap.parse_args(argv)
    if not (a.docx or a.pdf or a.html or a.json):
        ap.error("nothing to build: pass --docx, --pdf, --html and/or --json")

    try:
        resume = parse_resume(a.input.read_text(encoding="utf-8-sig"))
    except (OSError, UnicodeDecodeError) as e:
        return _fail(f"cannot read {a.input}: {getattr(e, 'strerror', None) or e}")
    except ValueError as e:
        return _fail(f"{a.input}: {e}")

    html_text = None
    if a.pdf or a.html:
        if a.photo and not a.photo.is_file():
            return _fail(f"photo not found: {a.photo}")
        if a.photo and a.photo.suffix.lower() not in _PHOTO_TYPES:
            return _fail(f"photo must be .jpg, .png or .webp: {a.photo}")
        try:
            html_text = html_str(resume, a.template, photo=a.photo)
        except OSError as e:
            return _fail(f"cannot build the {a.template} template: {e.strerror or e}")
    elif a.photo:
        print("note: --photo only applies to --pdf/--html; the .docx master never carries a photo",
              file=sys.stderr)

    out_dir = a.out or a.input.parent
    stem = a.input.stem

    def write(ext: str, data) -> Path:
        path = out_dir / f"{stem}{ext}"
        if isinstance(data, bytes):
            path.write_bytes(data)
        else:
            path.write_text(data, encoding="utf-8", newline="\n")
        print(path)
        return path

    try:
        out_dir.mkdir(parents=True, exist_ok=True)
        if a.docx:
            write(".docx", docx_bytes(resume))
        if a.html:
            write(".html", html_text)
        if a.pdf:
            pdf_path = out_dir / f"{stem}.pdf"
            failures: list[str] = []
            if render_pdf(html_text, pdf_path, failures):
                print(pdf_path)
            else:
                if not a.html:
                    write(".html", html_text)
                print(PDF_SKIPPED)
                if failures:
                    print(f"note: installed but failed: {', '.join(failures)}", file=sys.stderr)
        if a.json:
            write(".json", json.dumps(json_resume(resume), indent=2, ensure_ascii=False) + "\n")
    except OSError as e:
        return _fail(f"cannot write to {out_dir}: {e.strerror or e}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
