"""Tests for build_resume.py — markdown parse, stdlib docx, HTML templates, JSON Resume, CLI.

No network. The one real PDF render skips itself when no Chromium backend
(playwright or cloakbrowser) can launch on this machine.
"""
import io
import json
import pathlib
import re
import shutil
import subprocess
import sys
import xml.etree.ElementTree as ET
import zipfile
from urllib.parse import urlparse
from urllib.request import url2pathname

import pytest

ROOT = pathlib.Path(__file__).resolve().parents[1]
SCRIPTS = ROOT / "skills" / "job-hunting" / "scripts"
FIXTURES = pathlib.Path(__file__).resolve().parent / "fixtures"
sys.path.insert(0, str(SCRIPTS))

import build_resume as br  # noqa: E402
from _common import docx_text  # noqa: E402

SAMPLE = FIXTURES / "resume-sample.md"
SAMPLE_B = FIXTURES / "resume-sample-b.md"
TEMPLATES = ("chicago", "executive", "corporate-sidebar", "accent-band", "creative-sidebar")
SKIP_LINE = ("PDF skipped: pip install playwright && playwright install chromium "
             "(or open the .html and print to PDF)")


@pytest.fixture(scope="module")
def resume():
    return br.parse_resume(SAMPLE.read_text(encoding="utf-8"))


@pytest.fixture(scope="module")
def resume_b():
    return br.parse_resume(SAMPLE_B.read_text(encoding="utf-8"))


def _section(resume, word):
    return next(s for s in resume["sections"] if word.lower() in s["title"].lower())


def _fixture_bullets(path):
    return [ln[2:].strip() for ln in path.read_text(encoding="utf-8").splitlines() if ln.startswith("- ")]


# --- parse_resume -------------------------------------------------------------

def test_parse_header(resume):
    assert resume["name"] == "Arif Rahman"
    assert resume["headline"] == "Backend Engineer"
    assert resume["contact"] == [
        "Kuala Lumpur, Malaysia", "+60 12-345 6789", "arif.rahman@example.com",
        "https://linkedin.com/in/arif-rahman-example", "https://github.com/arif-rahman-example",
    ]
    assert [s["title"] for s in resume["sections"]] == [
        "Summary", "Experience", "Skills", "Education & Certifications"]


def test_parse_experience_entries_and_dates(resume):
    entries = [e for e in _section(resume, "experience")["entries"] if e["heading"]]
    assert len(entries) == 2
    first, second = entries
    assert first["heading"] == "Software Engineer"
    assert first["meta"] == "Moneta Pay, Kuala Lumpur · 03/2023 – Present"
    assert first["org_loc"] == "Moneta Pay, Kuala Lumpur"
    assert first["dates"] == "03/2023 – Present"
    assert len(first["bullets"]) == 3
    assert second["heading"] == "Junior Software Engineer"
    assert second["dates"] == "06/2021 – 02/2023"


def test_parse_skill_groups(resume):
    groups = [g for e in _section(resume, "skills")["entries"] for g in e["groups"]]
    assert [g["label"] for g in groups] == ["Languages", "Cloud & data"]
    assert groups[0]["items"] == ["Go", "Python", "SQL"]
    # commas inside parentheses do not split an item
    assert groups[1]["items"][0] == "AWS (EC2, RDS, SQS)"


def test_parse_template_b(resume_b):
    assert resume_b["name"] == "Mei Ling Tan"
    assert resume_b["headline"] == "Data Analyst"
    assert "linkedin.com/in/meiling-tan-example" in resume_b["contact"]
    summary = _section(resume_b, "summary")["entries"][0]["lines"]
    assert summary == ["Former secondary-school maths teacher moving into data analysis: eight years "
                       "turning results data into decisions, now certified in SQL and Power BI."]
    core = _section(resume_b, "proof")["entries"]
    assert [e["heading"] for e in core] == [
        "SQL & data cleaning", "Dashboards (Power BI)", "Stakeholder communication"]
    assert all(e["labeled"] for e in core)
    assert core[1]["lines"] == ["built a cohort dashboard used by 40 teachers each term"]
    exp = [e for e in _section(resume_b, "experience")["entries"] if e["heading"]]
    assert len(exp) == 1 and exp[0]["dates"] == "01/2017 – 06/2025"


def test_parse_without_name_raises():
    with pytest.raises(ValueError):
        br.parse_resume("Just some text\n## Experience\n- a bullet\n")


def test_parse_edge_cases():
    md = ("# A B\nEngineer · a@b.co\n## Experience\n### Dev — Acme, KL · 2019 - 2021\n- x\n"
          "  wrapped tail\n## Skills: Go & C#\n- Go, C#, AWS\n"
          "## Volunteering\n### Mentor — Code Club · 2022\n- taught kids\n")
    r = br.parse_resume(md)
    dev = _section(r, "experience")["entries"][0]
    assert dev["dates"] == "2019 - 2021" and dev["bullets"] == ["x wrapped tail"]
    skills = _section(r, "skills")
    assert skills["title"] == "Skills: Go & C#"
    assert skills["entries"][0]["groups"] == [{"label": "", "items": ["Go", "C#", "AWS"]}]
    vol = _section(r, "volunteering")
    assert vol["entries"][0]["heading"] == "Mentor" and vol["entries"][0]["bullets"] == ["taught kids"]


# --- dates --------------------------------------------------------------------

@pytest.mark.parametrize("text, expected", [
    ("03/2023 – Present", ("2023-03", None)),
    ("06/2021 - 02/2023", ("2021-06", "2023-02")),
    ("6/2021 — 2/2023", ("2021-06", "2023-02")),
    ("Jan 2020 – Mar 2021", ("2020-01", "2021-03")),
    ("2019 – 2021", ("2019", "2021")),
    ("2019-2021", ("2019", "2021")),
    ("2024", ("2024", None)),
])
def test_split_dates(text, expected):
    assert br.split_dates(text) == expected


# --- docx ---------------------------------------------------------------------

def _parts(data):
    with zipfile.ZipFile(io.BytesIO(data)) as z:
        return {n: z.read(n) for n in z.namelist()}


def test_docx_package_structure(resume):
    parts = _parts(br.docx_bytes(resume))
    for name in ("[Content_Types].xml", "_rels/.rels", "word/document.xml", "word/styles.xml",
                 "word/numbering.xml", "word/_rels/document.xml.rels", "docProps/core.xml"):
        assert name in parts, name
    for name, raw in parts.items():  # every part is well-formed XML
        ET.fromstring(raw)
    doc = parts["word/document.xml"].decode("utf-8")
    assert "Arif Rahman" in doc
    assert "<w:tbl" not in doc and "<w:drawing" not in doc and "headerReference" not in doc
    assert "•" not in doc and "•" not in parts["word/numbering.xml"].decode("utf-8")
    assert "<w:numPr>" in doc
    assert 'w:val="bullet"' in parts["word/numbering.xml"].decode("utf-8")
    ctypes = parts["[Content_Types].xml"].decode("utf-8")
    for name in parts:
        if not name.endswith(".rels") and name != "[Content_Types].xml":
            assert f'PartName="/{name}"' in ctypes, name
    rels = parts["word/_rels/document.xml.rels"].decode("utf-8")
    assert 'Target="styles.xml"' in rels and 'Target="numbering.xml"' in rels
    assert "<dc:title>Arif Rahman</dc:title>" in parts["docProps/core.xml"].decode("utf-8")


def test_docx_styles_and_layout(resume):
    parts = _parts(br.docx_bytes(resume))
    styles = parts["word/styles.xml"].decode("utf-8")
    for style_id in ("Title", "Heading1", "Heading2", "Normal"):
        assert f'w:styleId="{style_id}"' in styles
    assert "<w:pBdr><w:bottom" in styles                    # heading rule
    doc = parts["word/document.xml"].decode("utf-8")
    assert 'w:val="right" w:pos="9638"' in doc + styles     # right tab at the A4/20 mm text edge
    assert 'w:w="11906"' in doc and 'w:left="1134"' in doc


def test_docx_text_has_every_bullet_and_reading_order(resume):
    text = docx_text(br.docx_bytes(resume))
    for bullet in _fixture_bullets(SAMPLE):
        assert bullet in text, bullet
    lines = text.splitlines()
    assert lines[0] == "Arif Rahman"
    order = [text.index(h) for h in ("Summary", "Experience", "Skills", "Education & Certifications")]
    assert order == sorted(order)
    assert "Software Engineer — Moneta Pay, Kuala Lumpur\t03/2023 – Present" in lines
    assert "- Cut payment webhook failure rate from 2.1% to 0.4% by designing an idempotent retry queue (Go, AWS SQS)" in lines
    assert "arif.rahman@example.com" in text and "+60 12-345 6789" in text


def test_docx_escapes_xml_specials():
    md = "# Tom & <Jerry>\nQA · t@j.co\n## Experience\n### QA — Cat & Mouse Co · 2020 – 2021\n- Cut costs & latency <50ms for \"key\" 'paths'\n"
    data = br.docx_bytes(br.parse_resume(md))
    parts = _parts(data)
    for raw in parts.values():
        ET.fromstring(raw)
    doc = parts["word/document.xml"].decode("utf-8")
    assert "Cut costs &amp; latency &lt;50ms" in doc
    text = docx_text(data)
    assert "Cut costs & latency <50ms for \"key\" 'paths'" in text
    assert text.splitlines()[0] == "Tom & <Jerry>"


def test_docx_text_rejects_non_docx():
    with pytest.raises(ValueError):
        docx_text(b"not a zip")


# --- HTML ---------------------------------------------------------------------

@pytest.mark.parametrize("template", TEMPLATES)
def test_html_each_template(resume, template):
    out = br.html_str(resume, template)
    assert out.lstrip().lower().startswith("<!doctype html>")
    assert "Arif Rahman" in out
    assert _fixture_bullets(SAMPLE)[0] in out
    assert "{{" not in out and "}}" not in out
    assert "<img" not in out                      # no photo unless asked
    assert "Cloud &amp; data" in out              # text is escaped
    assert "@page" in out and "size: A4" in out and "--accent" in out
    assert not re.search(r"<link[^>]+stylesheet|<script\b|@import|fonts\.googleapis", out)


@pytest.mark.parametrize("template, sidebar", [
    ("chicago", False), ("executive", False), ("accent-band", False),
    ("corporate-sidebar", True), ("creative-sidebar", True)])
def test_html_sidebar_split(resume, template, sidebar):
    out = br.html_str(resume, template)
    m = re.search(r'<aside\b[^>]*class="[^"]*sidebar[^"]*"[^>]*>(.*?)</aside>', out, re.S)
    skills_in_sidebar = bool(m and "Cloud &amp; data" in m.group(1))
    assert skills_in_sidebar is sidebar
    if sidebar:
        # education and experience stay in the main column
        assert "Universiti Malaya" not in m.group(1) and "Moneta Pay" not in m.group(1)


def test_html_escapes_text():
    r = br.parse_resume("# Eve <script>alert(1)</script>\nDev · e@x.io\n## Summary\nI like <b> & \"quotes\"\n")
    out = br.html_str(r, "chicago")
    assert "<script>alert" not in out
    assert "Eve &lt;script&gt;alert(1)&lt;/script&gt;" in out
    assert "I like &lt;b&gt; &amp; &quot;quotes&quot;" in out


def test_html_photo_only_when_given(resume, tmp_path):
    png = tmp_path / "me.png"
    png.write_bytes(b"\x89PNG\r\n\x1a\n" + b"\x00" * 16)
    out = br.html_str(resume, "creative-sidebar", photo=png)
    assert re.search(r'<img [^>]*src="data:image/png;base64,', out)
    for template in TEMPLATES:
        assert "<img" in br.html_str(resume, template, photo=png)


def test_html_unknown_template_raises(resume):
    with pytest.raises(ValueError):
        br.html_str(resume, "nope")


def test_html_template_b_labeled_entries(resume_b):
    out = br.html_str(resume_b, "accent-band")
    assert "SQL &amp; data cleaning" in out and "cutting report prep from 3 days to 4 hours" in out


# --- JSON Resume ----------------------------------------------------------------

def test_json_resume(resume):
    j = br.json_resume(resume)
    b = j["basics"]
    assert b["name"] == "Arif Rahman" and b["label"] == "Backend Engineer"
    assert b["email"] == "arif.rahman@example.com" and b["phone"] == "+60 12-345 6789"
    assert b["location"]["city"] == "Kuala Lumpur"
    assert {p["network"] for p in b["profiles"]} == {"LinkedIn", "GitHub"}
    assert b["summary"].startswith("Backend engineer with 4 years")
    assert len(j["work"]) == 2
    w0, w1 = j["work"]
    assert (w0["name"], w0["position"], w0["startDate"]) == ("Moneta Pay", "Software Engineer", "2023-03")
    assert "endDate" not in w0
    assert (w1["startDate"], w1["endDate"]) == ("2021-06", "2023-02")
    assert len(w0["highlights"]) == 3
    assert j["skills"][0] == {"name": "Languages", "keywords": ["Go", "Python", "SQL"]}
    assert j["education"] == [{"institution": "Universiti Malaya", "area": "BSc Computer Science",
                               "endDate": "2021"}]
    assert j["certificates"][0]["name"] == "AWS Solutions Architect – Associate"
    json.dumps(j)  # serializable


def test_json_resume_template_b(resume_b):
    j = br.json_resume(resume_b)
    assert j["basics"]["profiles"][0]["url"] == "https://linkedin.com/in/meiling-tan-example"
    assert j["basics"]["location"]["city"] == "Singapore"
    assert j["work"][0]["startDate"] == "2017-01" and j["work"][0]["endDate"] == "2025-06"
    assert [s["name"] for s in j["skills"]][0] == "SQL & data cleaning"
    assert j["education"][0]["institution"] == "National University of Singapore"
    assert j["certificates"][0]["issuer"] == "Coursera"


# --- CLI ------------------------------------------------------------------------

@pytest.fixture
def md_copy(tmp_path):
    dst = tmp_path / "resumes" / "moneta-backend-v1.md"
    dst.parent.mkdir()
    shutil.copyfile(SAMPLE, dst)
    return dst


def test_cli_writes_next_to_input(md_copy, capsys):
    assert br.main([str(md_copy), "--docx", "--html", "--json", "--template", "accent-band"]) == 0
    printed = capsys.readouterr().out.split()
    stem = md_copy.with_suffix("")
    for ext in (".docx", ".html", ".json"):
        path = stem.with_suffix(ext)
        assert path.exists() and str(path) in printed
    assert "accent" in stem.with_suffix(".html").read_text(encoding="utf-8")
    assert json.loads(stem.with_suffix(".json").read_text(encoding="utf-8"))["basics"]["name"] == "Arif Rahman"
    assert sorted(p.name for p in md_copy.parent.iterdir()) == [
        "moneta-backend-v1.docx", "moneta-backend-v1.html", "moneta-backend-v1.json", "moneta-backend-v1.md"]


def test_cli_out_dir(md_copy, tmp_path, capsys):
    out = tmp_path / "build" / "nested"
    assert br.main([str(md_copy), "--docx", "--out", str(out)]) == 0
    assert (out / "moneta-backend-v1.docx").exists()
    assert not md_copy.with_suffix(".docx").exists()


def test_cli_pdf_skipped_without_renderer(md_copy, monkeypatch, capsys):
    monkeypatch.setattr(br, "optional_import", lambda name: None)
    assert br.main([str(md_copy), "--pdf", "--template", "executive"]) == 0
    out = capsys.readouterr().out
    assert SKIP_LINE in out
    assert md_copy.with_suffix(".html").exists() and not md_copy.with_suffix(".pdf").exists()


@pytest.mark.parametrize("argv_tail, needle", [
    (["--docx", "--template", "nope"], "invalid choice"),
    ([], "nothing to build"),
])
def test_cli_bad_args_exit_2(md_copy, capsys, argv_tail, needle):
    with pytest.raises(SystemExit) as exc:
        code = br.main([str(md_copy)] + argv_tail)
        raise SystemExit(code)
    assert exc.value.code == 2
    assert needle in capsys.readouterr().err


def test_cli_missing_name_and_missing_file_exit_2(tmp_path):
    bad = tmp_path / "bad.md"
    bad.write_text("## Experience\n- no name line\n", encoding="utf-8")
    for target in (bad, tmp_path / "missing.md"):
        proc = subprocess.run([sys.executable, str(SCRIPTS / "build_resume.py"), str(target), "--docx"],
                              capture_output=True, text=True)
        assert proc.returncode == 2
        assert "Traceback" not in proc.stderr and proc.stderr.strip()
    assert not (tmp_path / "bad.docx").exists()


def test_cli_missing_photo_exit_2(md_copy, capsys):
    assert br.main([str(md_copy), "--html", "--photo", str(md_copy.parent / "nope.jpg")]) == 2
    assert "photo" in capsys.readouterr().err.lower()


class _FakePage:
    def goto(self, url, wait_until=None):
        page_file = pathlib.Path(url2pathname(urlparse(url).path))
        assert "Arif Rahman" in page_file.read_text(encoding="utf-8")

    def pdf(self, path=None, **kw):
        pathlib.Path(path).write_bytes(b"%PDF-1.7 fake " + kw["format"].encode())


class _FakeBrowser:
    def __init__(self, log):
        self.log = log

    def new_page(self):
        return _FakePage()

    def close(self):
        self.log.append("closed")


def _fake_modules(log, playwright_ok):
    class Chromium:
        def launch(self, **kw):
            if not playwright_ok:
                raise RuntimeError("Executable doesn't exist")
            log.append("playwright")
            return _FakeBrowser(log)

    class _PW:
        chromium = Chromium()

        def __enter__(self):
            return self

        def __exit__(self, *exc):
            return False

    def launch(headless=True, **kw):
        log.append("cloakbrowser")
        return _FakeBrowser(log)

    return {"playwright.sync_api": type("M", (), {"sync_playwright": staticmethod(lambda: _PW())}),
            "cloakbrowser": type("M", (), {"launch": staticmethod(launch)})}


@pytest.mark.parametrize("playwright_ok, backend", [(True, "playwright"), (False, "cloakbrowser")])
def test_cli_pdf_backend_order_and_close(md_copy, monkeypatch, capsys, playwright_ok, backend):
    log = []
    mods = _fake_modules(log, playwright_ok)
    monkeypatch.setattr(br, "optional_import", lambda name: mods.get(name))
    assert br.main([str(md_copy), "--pdf", "--template", "creative-sidebar"]) == 0
    pdf = md_copy.with_suffix(".pdf")
    assert pdf.read_bytes() == b"%PDF-1.7 fake A4" and str(pdf) in capsys.readouterr().out
    assert log == [backend, "closed"]
    assert sorted(p.name for p in md_copy.parent.iterdir()) == ["moneta-backend-v1.md", "moneta-backend-v1.pdf"]
