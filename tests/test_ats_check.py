"""Tests for ats_check.py — text-layer extraction, keyword coverage, 6-second lint, slop scan.

No network. PDF extraction is exercised through monkeypatched backends (pypdf,
pdftotext) plus one real pdftotext run on a hand-built PDF when pdftotext is on
PATH.
"""
import json
import pathlib
import re
import shutil
import subprocess
import sys
import types

import pytest

ROOT = pathlib.Path(__file__).resolve().parents[1]
SCRIPTS = ROOT / "skills" / "job-hunting" / "scripts"
FIXTURES = pathlib.Path(__file__).resolve().parent / "fixtures"
SLOP_FILE = ROOT / "skills" / "job-hunting" / "assets" / "slop-phrases.txt"
sys.path.insert(0, str(SCRIPTS))

import ats_check as ats  # noqa: E402
import build_resume as br  # noqa: E402

SAMPLE = FIXTURES / "resume-sample.md"
SAMPLE_JD = FIXTURES / "sample-jd.md"
FALLBACK = ("Text layer not checked: no PDF text extractor here (pip install pypdf, or install "
            "pdftotext). Check the .docx master instead, or fall back to the pre-delivery "
            "checklist and tell the user the check did not run.")


@pytest.fixture(scope="module")
def sample_docx(tmp_path_factory):
    resume = br.parse_resume(SAMPLE.read_text(encoding="utf-8"))
    path = tmp_path_factory.mktemp("docx") / "arif.docx"
    path.write_bytes(br.docx_bytes(resume))
    return path


@pytest.fixture(scope="module")
def docx_text(sample_docx):
    text, method = ats.extract_text(sample_docx)
    assert method == "docx-xml"
    return text


def _no_pdf_backends(monkeypatch):
    monkeypatch.setattr(ats, "optional_import", lambda name: None)
    monkeypatch.setattr(ats.shutil, "which", lambda name: None)


# --- extract_text ----------------------------------------------------------------------

def test_extract_text_docx_reads_the_text_layer(docx_text):
    assert "arif.rahman@example.com" in docx_text
    assert "- Cut payment webhook failure rate from 2.1% to 0.4%" in docx_text


def test_extract_text_markdown_strips_headings_bold_and_links(tmp_path):
    md = tmp_path / "draft.md"
    md.write_text("# Arif Rahman\n**Languages:** Go · [GitHub](https://github.com/arif)\n"
                  "## Experience\n* Cut failures 80%\n", encoding="utf-8")
    text, method = ats.extract_text(md)
    assert method == "markdown"
    assert text.splitlines() == ["Arif Rahman", "Languages: Go · GitHub", "Experience",
                                 "- Cut failures 80%"]


def test_extract_text_plain_text(tmp_path):
    p = tmp_path / "resume.txt"
    p.write_text("## not a heading here\n", encoding="utf-8")
    assert ats.extract_text(p) == ("## not a heading here\n", "text")


def test_extract_text_pdf_prefers_pypdf(tmp_path, monkeypatch):
    pdf = tmp_path / "r.pdf"
    pdf.write_bytes(b"%PDF-1.4 fake")

    class Page:
        def __init__(self, text):
            self.text = text

        def extract_text(self):
            return self.text

    class Reader:
        def __init__(self, path):
            assert str(path) == str(pdf)
            self.pages = [Page("Arif Rahman"), Page(None), Page("Experience")]

    fake = types.SimpleNamespace(PdfReader=Reader)
    monkeypatch.setattr(ats, "optional_import", lambda name: fake if name == "pypdf" else None)
    monkeypatch.setattr(ats.shutil, "which", lambda name: pytest.fail("pdftotext not needed"))
    text, method = ats.extract_text(pdf)
    assert method == "pypdf"
    assert text.split("\n") == ["Arif Rahman", "", "Experience"]


def test_extract_text_pdf_falls_back_to_pdftotext_raw(tmp_path, monkeypatch):
    pdf = tmp_path / "r.pdf"
    pdf.write_bytes(b"%PDF-1.4 fake")
    calls = []

    def fake_run(args, **kwargs):
        calls.append((args, kwargs))
        return subprocess.CompletedProcess(args, 0, stdout="Arif Rahman\nGo · PostgreSQL\n\x0cPage two\n".encode(),
                                           stderr=b"")

    monkeypatch.setattr(ats, "optional_import", lambda name: None)
    monkeypatch.setattr(ats.shutil, "which", lambda name: "/opt/bin/pdftotext" if name == "pdftotext" else None)
    monkeypatch.setattr(ats.subprocess, "run", fake_run)
    text, method = ats.extract_text(pdf)
    assert method == "pdftotext-raw"
    assert text == "Arif Rahman\nGo · PostgreSQL\n\nPage two\n"
    (args, kwargs), = calls
    assert args[0] == "/opt/bin/pdftotext" and "-raw" in args and "-layout" not in args
    assert args[-2:] == [str(pdf), "-"]
    assert kwargs.get("timeout")


def test_extract_text_pdftotext_failure_raises_valueerror(tmp_path, monkeypatch):
    pdf = tmp_path / "r.pdf"
    pdf.write_bytes(b"not a pdf")
    monkeypatch.setattr(ats, "optional_import", lambda name: None)
    monkeypatch.setattr(ats.shutil, "which", lambda name: "/opt/bin/pdftotext")
    monkeypatch.setattr(ats.subprocess, "run", lambda args, **kw: subprocess.CompletedProcess(
        args, 1, stdout=b"", stderr=b"Syntax Warning: May not be a PDF file (continuing anyway)\n"
                                    b"Syntax Error: Couldn't find trailer dictionary\n\n"))
    with pytest.raises(ValueError, match="trailer") as e:
        ats.extract_text(pdf)
    assert "Warning" not in str(e.value)  # only the last non-empty stderr line


def test_extract_text_pdf_unavailable(tmp_path, monkeypatch):
    pdf = tmp_path / "r.pdf"
    pdf.write_bytes(b"%PDF-1.4 fake")
    _no_pdf_backends(monkeypatch)
    assert ats.extract_text(pdf) == ("", "unavailable")


def _tiny_pdf(text: str) -> bytes:
    """A one-page PDF with `text` in Helvetica — enough for a real pdftotext run."""
    stream = f"BT /F1 12 Tf 72 720 Td ({text}) Tj ET".encode()
    objs = [b"<< /Type /Catalog /Pages 2 0 R >>",
            b"<< /Type /Pages /Kids [3 0 R] /Count 1 >>",
            b"<< /Type /Page /Parent 2 0 R /MediaBox [0 0 612 792] /Contents 4 0 R "
            b"/Resources << /Font << /F1 5 0 R >> >> >>",
            b"<< /Length %d >>\nstream\n" % len(stream) + stream + b"\nendstream",
            b"<< /Type /Font /Subtype /Type1 /BaseFont /Helvetica >>"]
    out, offsets = bytearray(b"%PDF-1.4\n"), []
    for i, body in enumerate(objs, 1):
        offsets.append(len(out))
        out += b"%d 0 obj\n" % i + body + b"\nendobj\n"
    xref = len(out)
    out += b"xref\n0 %d\n0000000000 65535 f \n" % (len(objs) + 1)
    out += b"".join(b"%010d 00000 n \n" % o for o in offsets)
    out += b"trailer\n<< /Size %d /Root 1 0 R >>\nstartxref\n%d\n%%%%EOF\n" % (len(objs) + 1, xref)
    return bytes(out)


@pytest.mark.skipif(not shutil.which("pdftotext"), reason="pdftotext not installed")
def test_extract_text_real_pdftotext(tmp_path, monkeypatch):
    pdf = tmp_path / "hello.pdf"
    pdf.write_bytes(_tiny_pdf("Hello PostgreSQL 2024"))
    monkeypatch.setattr(ats, "optional_import", lambda name: None)  # force the pdftotext path
    text, method = ats.extract_text(pdf)
    assert method == "pdftotext-raw"
    assert "Hello PostgreSQL 2024" in text


def test_extract_text_bad_docx_raises_valueerror(tmp_path):
    bad = tmp_path / "bad.docx"
    bad.write_bytes(b"not a zip")
    with pytest.raises(ValueError):
        ats.extract_text(bad)


# --- keyword_coverage ------------------------------------------------------------------

def test_keyword_coverage_on_sample_docx(docx_text):
    cov = ats.keyword_coverage(docx_text, ["Go", "PostgreSQL", "gRPC"])
    assert cov["present"] == ["Go", "PostgreSQL"]
    assert cov["missing"] == ["gRPC"]
    assert cov["ratio"] == pytest.approx(2 / 3, abs=0.01)


def test_keyword_coverage_word_boundaries_and_literal_symbols():
    text = "Shipped C++ and Node.js services on .NET; JavaScript at Google; postgresql tuning; on-call"
    cov = ats.keyword_coverage(text, ["C++", "Node.js", ".NET", "C#", "C", "Java", "Go", "PostgreSQL",
                                      "on-call", "SQL"])
    assert cov["present"] == ["C++", "Node.js", ".NET", "PostgreSQL", "on-call"]
    assert cov["missing"] == ["C#", "C", "Java", "Go", "SQL"]


@pytest.mark.parametrize("text,keyword,found", [
    ("We go live on Monday", "Go", False),                # 1-2 letter keywords match case-sensitively
    ("Owned the Go-to-market plan", "Go", False),         # "-" + letter continues the word
    ("Email me at arif@tm.net.my", ".NET", False),        # "." before a dotted keyword is no boundary
    ("Ran the R&D budget", "R", False),
    ("Presented to the C-suite", "C", False),
    ("Handled the rest of the backlog", "REST", False),   # ALL-CAPS keywords match case-sensitively
    ("Built payment services in Go.", "Go", True),
    ("Moved C# services to .NET 8", ".NET", True),
    ("Designed REST APIs", "API", True),                  # plural tolerance, both ways
    ("Owned payment reconciliation", "Payments", True),
    ("Settled Payments daily", "payment", True),
])
def test_keyword_coverage_lookalikes_and_true_positives(text, keyword, found):
    cov = ats.keyword_coverage(text, [keyword])
    assert cov["present" if found else "missing"] == [keyword]


def test_keyword_coverage_phrase_spans_whitespace_and_dedupes():
    cov = ats.keyword_coverage("schema\n design and Query  Tuning", ["schema design", "query tuning",
                                                                     "Query tuning", " "])
    assert cov == {"present": ["schema design", "query tuning"], "missing": [], "ratio": 1.0}


def test_keyword_coverage_empty_list():
    assert ats.keyword_coverage("anything", []) == {"present": [], "missing": [], "ratio": 0.0}


# --- extract_keywords ------------------------------------------------------------------

def test_extract_keywords_sample_jd():
    kws = ats.extract_keywords(SAMPLE_JD.read_text(encoding="utf-8"))
    lowered = [k.lower() for k in kws]
    for want in ("Go", "PostgreSQL", "gRPC", "Kubernetes", "AWS"):
        assert want in kws
    assert len(kws) <= 25 and len(set(lowered)) == len(lowered)
    for generic in ("experience", "strong", "team", "knowledge", "ability"):
        assert generic not in lowered
    # "What we offer" and "About the role" are not requirement sections
    for noise in ("macbook", "esop", "finora", "merchants"):
        assert noise not in lowered


def test_extract_keywords_prefers_description_body_and_heading_forms():
    posting = ("---\ncompany: Oracle\ntitle: Data Engineer\n---\n\n## Description\n\n"
               "About us: we love Terraform-free living.\n\n"
               "### Requirements\n- Python; Django and Kafka\n- 3+ years of experience with dbt\n\n"
               "Benefits\n- Free Snowflake\n\n"
               "Skills: Airflow, BigQuery\n")
    kws = ats.extract_keywords(posting)
    for want in ("Python", "Django", "Kafka", "dbt", "Airflow", "BigQuery"):
        assert want in kws
    assert "Oracle" not in kws and "Snowflake" not in kws


def test_extract_keywords_without_requirement_headings_uses_tech_tokens():
    kws = ats.extract_keywords("We build payment rails in Go with PostgreSQL, gRPC and C++ at scale.")
    assert kws[:4] == ["Go", "PostgreSQL", "gRPC", "C++"]


def test_extract_keywords_survives_unmarked_requirement_lines():
    stripped = re.sub(r"(?m)^- ", "", SAMPLE_JD.read_text(encoding="utf-8"))
    kws = ats.extract_keywords(stripped)
    for want in ("Go", "gRPC", "Kubernetes", "PostgreSQL"):
        assert want in kws


def test_extract_keywords_merges_tech_tokens_when_sections_are_thin():
    posting = "Requirements\nFintech domain\n\nAbout the team\nWe run Go and Kafka on AWS.\n"
    assert ats.extract_keywords(posting) == ["Fintech", "Go", "Kafka", "AWS"]


SECTION_LEAD = "Requirements\nGo, Kafka, Redis, gRPC and Kubernetes\n"  # 5 keywords: no tech-token merge


@pytest.mark.parametrize("line,ends_section", [
    ("Information security fundamentals matter here", False),   # sentences with section words
    ("Package management experience required here", False),
    ("Compensation benchmarking exposure is useful", False),
    ("Duties may vary by project needs", False),
    ("Culture fit matters more than tenure", False),
    ("Additional Information", True),                           # real headings: ≤4 words
    ("Life at Grab", True),
    ("What we offer", True),
    ("Things we would love to see from you:", True),             # colon, ≤8 words
])
def test_extract_keywords_unmarked_heading_rule(line, ends_section):
    kws = ats.extract_keywords(f"{SECTION_LEAD}{line}\nWritten English for client calls\n"
                               "Docker and Terraform\n")
    assert {"English", "Docker", "Terraform"}.isdisjoint(kws) is ends_section


def test_extract_keywords_reviewer_repro_block():
    posting = (SECTION_LEAD + "Package management experience required here\n"
               "Duties may vary by project needs\nInformation security fundamentals matter here\n"
               "Compensation benchmarking exposure is useful\nCulture fit matters more than tenure\n"
               "Written English, Docker and Terraform\n")
    assert {"English", "Docker", "Terraform"} <= set(ats.extract_keywords(posting))


@pytest.mark.parametrize("lead", ["", SECTION_LEAD], ids=["alone", "after-requirements"])
@pytest.mark.parametrize("heading", ["What Essential Skills You Will Need",
                                     "Skills and Experience We Are Looking For"])
def test_extract_keywords_title_case_requirement_heading_opens_section(lead, heading):
    posting = (f"{lead}About the role\nYou will own payment services end to end.\n"
               f"You will mentor two engineers.\n{heading}\n5+ years with Go and PostgreSQL\n"
               "Kafka and Redis in production\nStrong written and spoken English required\n"
               "Docker for local development\nTerraform for infrastructure changes\n")
    assert {"English", "Docker", "Terraform"} <= set(ats.extract_keyword_groups(posting)["must"])


@pytest.mark.parametrize("line,group", [
    ("Strong Python skills preferred for this role", "must"),  # sentence case: content
    ("Nice To Have Skills", "nice"),                            # title case: switches to nice
])
def test_extract_keyword_groups_heading_shape_inside_requirements(line, group):
    groups = ats.extract_keyword_groups(f"Requirements\nGo, Kafka, Redis and gRPC\n{line}\n"
                                        "Kubernetes in production\nDocker and Terraform\n")
    assert {"Kubernetes", "Docker", "Terraform"} <= set(groups[group])
    assert {"Go", "Kafka", "Redis", "gRPC"} <= set(groups["must"])


def test_extract_keywords_title_case_content_line_keeps_section_open():
    posting = ("Requirements\nGo, Kafka, Redis, gRPC and PostgreSQL\n"
               "Own The Full Platform Responsibility Here\n"
               "Docker and Terraform for infra\nEnglish fluency required\n")
    must = ats.extract_keyword_groups(posting)["must"]
    assert {"Go", "Kafka", "Redis", "gRPC", "PostgreSQL", "Docker", "Terraform"} <= set(must)
    assert [k for k in must if k.startswith("English")]      # "English fluency"


@pytest.mark.parametrize("line", ["Why You Will Love Working Here",         # no section word
                                  "About Our Company And Culture Here"])    # section words
def test_extract_keywords_long_title_case_line_never_ends_section(line):
    """Trade-off of the heading rule: a title-cased line of 5-8 words without a colon can
    open or switch a requirements section but never ends one, so a long unmarked
    section heading of that shape runs on into the requirements list."""
    kws = ats.extract_keywords(f"{SECTION_LEAD}{line}\nWritten English for client calls\n"
                               "Docker and Terraform\n")
    assert {"English", "Docker", "Terraform"} <= set(kws)


def test_extract_keyword_groups_split_must_and_nice():
    groups = ats.extract_keyword_groups(SAMPLE_JD.read_text(encoding="utf-8"))
    assert {"Go", "gRPC", "PostgreSQL"} <= set(groups["must"])
    assert {"Payments", "AWS", "mentoring"} <= set(groups["nice"])
    assert not set(groups["must"]) & set(groups["nice"])
    assert ats.extract_keyword_groups("Requirements:\n- Go, Kafka\n")["nice"] == []


def test_extract_keywords_caps_at_25():
    items = ", ".join(f"Tool{i}X" for i in range(40))
    assert len(ats.extract_keywords(f"**Skills**\n{items}\n")) == 25


# --- lint_six_second -------------------------------------------------------------------

def _fails(findings):
    return [f for f in findings if f.startswith("FAIL")]


def test_lint_passes_on_sample_docx(docx_text):
    findings = ats.lint_six_second(docx_text)
    assert not _fails(findings), findings
    assert {f.split(":")[0].split()[1] for f in findings} == {"contact", "date", "first-bullet", "length"}
    assert any(re.match(r"ok length: \d+ words", f) for f in findings)


@pytest.mark.parametrize("contact_line,missing", [
    ("Data Analyst · +65 9123 4567", "email"),       # the brief's case: no email
    ("jane@example.com · 2019 - 2021", "phone"),     # a year range is not a phone number
    ("jane@example.com · Universiti Malaya (2017 - 2021)", "phone"),
    ("jane@example.com · expected IDR 10.000.000", "phone"),  # currency is not a phone number
])
def test_lint_flags_missing_contact(contact_line, missing):
    text = f"Jane Tan\n{contact_line}\nExperience\nAnalyst — Acme · 2022 – Present\n- Cut report time 40%\n"
    fails = _fails(ats.lint_six_second(text))
    assert len(fails) == 1 and fails[0].startswith("FAIL contact:") and missing in fails[0]


def test_lint_flags_first_bullet_without_number_date_and_length():
    words = " ".join(["word"] * 950)
    text = (f"Jane Tan\njane@example.com +65 9123 4567\nExperience\nAnalyst — Acme\n"
            f"- Owned the weekly reporting\n- Cut report time 40%\n{words}\n")
    fails = _fails(ats.lint_six_second(text))
    checks = {f.split(":")[0] for f in fails}
    assert checks == {"FAIL date", "FAIL first-bullet", "FAIL length"}
    assert any("Owned the weekly reporting" in f for f in fails)
    assert any(re.search(r"\b9\d\d words\b", f) for f in fails)


def test_lint_first_bullet_accepts_round_bullet_and_needs_experience_line():
    ok = ats.lint_six_second("a@b.co 555 1234 567 2024\nWork Experience\n• Grew revenue 3x\n")
    assert "ok first-bullet" in ok
    missing = ats.lint_six_second("a@b.co 555 1234 567 2024\nProjects\n- Built a thing\n")
    assert "FAIL first-bullet: no Experience heading found" in missing
    markerless = ats.lint_six_second("a@b.co 555 1234 567\nEXPERIENCE\nEngineer 2023\nCut costs 40%\n")
    assert 'FAIL first-bullet: no "- " or "• " bullet under the Experience heading' in markerless
    job_title = ats.lint_six_second("a@b.co 555 1234 567 2024\nUser Experience Designer\n- Led design\n")
    assert "FAIL first-bullet: no Experience heading found" in job_title
    labelled = ats.lint_six_second("a@b.co 555 1234 567 2024\nProfessional Experience:\n- Grew 3x\n")
    assert "ok first-bullet" in labelled


def test_lint_parenthesised_year_range_counts_as_a_date():
    findings = ats.lint_six_second("Jane Tan\njane@example.com +65 9123 4567\nAcme (2019 - 2021)\n")
    assert "ok date" in findings and "ok contact" in findings


PDF_SKIPS = ("skip date: a PDF's text order follows its columns, not the page; "
             "lint the .md draft or .docx master",
             "skip first-bullet: a PDF text layer carries no list markers; "
             "lint the .md draft or .docx master")


@pytest.mark.parametrize("method", ["pypdf", "pdftotext-raw"])
def test_lint_skips_date_and_first_bullet_on_pdf_text(method):
    text = "Jane Tan\nSKILLS\nGo\nEXPERIENCE\nEngineer\nOwned things\njane@example.com +65 9123 4567\n"
    findings = ats.lint_six_second(text, target_title="Engineer", method=method)
    assert findings[:3] == ["ok contact", *PDF_SKIPS]
    assert findings[3].startswith("ok length:") and findings[4] == "ok title"  # the rest still run


def test_lint_target_title_pass_and_fail(docx_text):
    assert "ok title" in ats.lint_six_second(docx_text, target_title="Backend Engineer (Go)")
    fails = _fails(ats.lint_six_second(docx_text, target_title="Head of Frontend Engineering"))
    assert len(fails) == 1 and fails[0].startswith("FAIL title:")
    assert "head" in fails[0].lower() and "frontend" in fails[0].lower()
    assert '"of"' not in fails[0]


@pytest.mark.parametrize("target,title_line", [
    ("Full-Stack Engineer", "Full Stack Engineer"),
    ("Full Stack Engineer", "Full-Stack Engineer"),
])
def test_lint_title_treats_hyphen_and_space_alike(target, title_line):
    assert "ok title" in ats.lint_six_second(f"Jane Tan\n{title_line}\n", target_title=target)


# --- slop_scan -------------------------------------------------------------------------

def test_slop_scan_finds_phrase():
    assert ("passionate about", 1) in ats.slop_scan("I am passionate about distributed systems.")


def test_slop_scan_counts_case_insensitive_word_bounded_sorted():
    text = "Robust design. A ROBUST queue; robustness is not a hit. I’m Passionate About Go. Leveraged."
    assert ats.slop_scan(text) == [("robust", 2), ("passionate about", 1)]


def test_slop_scan_longest_match_wins():
    assert ats.slop_scan("A dynamic team player, and a team player.") == [
        ("dynamic team player", 1), ("team player", 1)]


def test_slop_scan_apostrophes_and_custom_list():
    assert ats.slop_scan("In today’s fast-paced world", ["in today's fast-paced"]) == [
        ("in today's fast-paced", 1)]
    assert ats.slop_scan("clean text", ["synergy"]) == []


def test_slop_phrase_file():
    raw = SLOP_FILE.read_bytes()
    assert b"\r\n" not in raw
    phrases = ats.get_slop_phrases()
    assert len(phrases) >= 40
    assert len({p.lower() for p in phrases}) == len(phrases)
    for want in ("passionate about", "proven track record", "results-driven",
                 "I am writing to express my interest", "in today's fast-paced", "delve",
                 "responsible for", "I believe I would be a great fit", "moreover",
                 "utilizes", "utilised", "utilising", "spearhead", "spearheading", "delved",
                 "I'm confident that"):
        assert want in phrases
    assert not any(p.startswith("#") or not p.strip() for p in phrases)


def test_get_slop_phrases_skips_comments_and_blanks(tmp_path):
    f = tmp_path / "s.txt"
    f.write_text("# header\n\n  synergy  \n#comment\ndelve\n", encoding="utf-8")
    assert ats.get_slop_phrases(f) == ["synergy", "delve"]


# --- CLI -------------------------------------------------------------------------------

def test_cli_docx_keywords_lint_slop(sample_docx, capsys):
    rc = ats.main([str(sample_docx), "--keywords", "Go,PostgreSQL,gRPC", "--lint", "--slop"])
    out = capsys.readouterr().out
    assert rc == 0
    lines = out.splitlines()
    assert "**Method:** docx-xml" in lines[0]
    assert "**Keywords:** 2/3 present — missing: gRPC" in lines
    assert "**Lint:**" in lines and "ok contact" in lines and "ok first-bullet" in lines
    assert "**Slop:** none found" in lines


def test_cli_posting_splits_must_and_nice_to_have(sample_docx, capsys):
    assert ats.main([str(sample_docx), "--posting", str(SAMPLE_JD)]) == 0
    out = capsys.readouterr().out
    must = re.search(r"^\*\*Keywords \(must-have\):\*\* (\d+)/(\d+) present — missing: (.+)$", out, re.M)
    nice = re.search(r"^\*\*Keywords \(nice-to-have\):\*\* (\d+)/(\d+) present", out, re.M)
    assert must and "gRPC" in must.group(3) and "Go" not in must.group(3).split(", ")
    assert nice and must.start() < nice.start()
    assert "**Lint:**" not in out and "**Slop:**" not in out and "**Text layer:**" not in out


def test_cli_posting_lint_text_prints_all_three_parts(sample_docx, capsys):
    assert ats.main([str(sample_docx), "--posting", str(SAMPLE_JD), "--lint", "--text"]) == 0
    out = capsys.readouterr().out
    assert out.index("**Keywords (must-have):**") < out.index("**Lint:**") < out.index("**Text layer:**")
    assert "arif.rahman@example.com" in out.split("**Text layer:**")[1]


def test_step6_invocations_ask_for_lint_and_text():
    invocation = ("sh ${CLAUDE_SKILL_DIR}/scripts/jh ats_check.py <file> --posting "
                  "postings/<slug>.md --lint --text")
    builder = (ROOT / "skills" / "job-hunting" / "references" / "resume-builder.md").read_text(encoding="utf-8")
    assert builder.count(invocation) == 2
    resume_skill = (ROOT / "skills" / "resume" / "SKILL.md").read_text(encoding="utf-8")
    assert re.search(r"ats_check\.py <file> --posting postings/<slug>\.md[^`]*--text", resume_skill)


def test_cli_markdown_lint_target_title_and_slop_hits(tmp_path, capsys):
    draft = tmp_path / "draft.md"
    draft.write_text(SAMPLE.read_text(encoding="utf-8") + "\nPassionate about robust, robust systems.\n",
                     encoding="utf-8")
    rc = ats.main([str(draft), "--slop", "--target-title", "Frontend Engineer"])
    out = capsys.readouterr().out
    assert rc == 0  # FAIL lines never change the exit code
    assert "**Method:** markdown" in out
    assert "FAIL title:" in out and "ok contact" in out  # --target-title implies --lint
    assert "robust ×2" in out and "passionate about ×1" in out


def test_cli_json(sample_docx, capsys):
    rc = ats.main([str(sample_docx), "--keywords", "Go, gRPC", "--lint", "--slop", "--json"])
    data = json.loads(capsys.readouterr().out)
    assert rc == 0
    assert data["method"] == "docx-xml"
    assert data["keywords"] == {"present": ["Go"], "missing": ["gRPC"], "ratio": 0.5}
    assert all(line.startswith(("ok ", "FAIL ")) for line in data["lint"])
    assert data["slop"] == []


def test_cli_text_flag_and_default_shows_text(sample_docx, capsys):
    assert ats.main([str(sample_docx)]) == 0
    out = capsys.readouterr().out
    assert "**Method:** docx-xml" in out and "arif.rahman@example.com" in out


def test_cli_unavailable_prints_declared_line_and_exits_2(tmp_path, monkeypatch, capsys):
    pdf = tmp_path / "r.pdf"
    pdf.write_bytes(b"%PDF-1.4 fake")
    _no_pdf_backends(monkeypatch)
    assert ats.main([str(pdf), "--lint"]) == 2
    captured = capsys.readouterr()
    assert captured.out == FALLBACK + "\n"


def test_fallback_line_matches_resume_builder_reference():
    ref = (ROOT / "skills" / "job-hunting" / "references" / "resume-builder.md").read_text(encoding="utf-8")
    assert "> " + FALLBACK in ref
    assert ats.FALLBACK_LINE == FALLBACK


def test_cli_pdf_via_pdftotext(tmp_path, monkeypatch, capsys):
    pdf = tmp_path / "r.pdf"
    pdf.write_bytes(b"%PDF-1.4 fake")
    monkeypatch.setattr(ats, "optional_import", lambda name: None)
    monkeypatch.setattr(ats.shutil, "which", lambda name: "/opt/bin/pdftotext")
    monkeypatch.setattr(ats.subprocess, "run", lambda args, **kw: subprocess.CompletedProcess(
        args, 0, stdout=b"Arif Rahman\nGo and PostgreSQL\n", stderr=b""))
    assert ats.main([str(pdf), "--keywords", "Go,gRPC"]) == 0
    out = capsys.readouterr().out
    assert "**Method:** pdftotext-raw" in out and "**Keywords:** 1/2 present — missing: gRPC" in out
    assert ats.main([str(pdf), "--lint", "--json"]) == 0
    lint = json.loads(capsys.readouterr().out)["lint"]
    assert [line.split(":")[0] for line in lint] == ["FAIL contact", "skip date", "skip first-bullet",
                                                     "ok length"]


def test_cli_empty_text_layer_is_reported(tmp_path, monkeypatch, capsys):
    pdf = tmp_path / "scan.pdf"
    pdf.write_bytes(b"%PDF-1.4 fake")
    monkeypatch.setattr(ats, "optional_import", lambda name: None)
    monkeypatch.setattr(ats.shutil, "which", lambda name: "/opt/bin/pdftotext")
    monkeypatch.setattr(ats.subprocess, "run", lambda args, **kw: subprocess.CompletedProcess(
        args, 0, stdout=b"\x0c", stderr=b""))
    assert ats.main([str(pdf), "--lint"]) == 0
    assert "empty" in capsys.readouterr().out.lower()


@pytest.mark.parametrize("argv_tail,needle", [
    (["--posting", "nope.md"], "nope.md"),
    (["--keywords", " , "], "--keywords"),
])
def test_cli_bad_inputs_exit_2(sample_docx, capsys, argv_tail, needle):
    assert ats.main([str(sample_docx), *argv_tail]) == 2
    assert needle in capsys.readouterr().err


def test_cli_unreadable_files_exit_2(tmp_path, monkeypatch, capsys):
    bad_list = tmp_path / "slop.txt"
    bad_list.write_bytes(b"synergy\n\xff\xfe broken\n")
    monkeypatch.setattr(ats, "SLOP_FILE", bad_list)
    md = tmp_path / "draft.md"
    md.write_text("fine", encoding="utf-8")
    assert ats.main([str(md), "--slop"]) == 2
    assert "slop.txt" in capsys.readouterr().err
    bad = tmp_path / "bad.docx"
    bad.write_bytes(b"not a zip")
    assert ats.main([str(bad), "--lint"]) == 2
    assert ats.main([str(tmp_path / "missing.docx")]) == 2
    odd = tmp_path / "resume.doc"
    odd.write_bytes(b"\xd0\xcf\x11\xe0 old word binary \xff\xfe")
    assert ats.main([str(odd)]) == 2
    err = capsys.readouterr().err
    assert "bad.docx" in err and "missing.docx" in err and "resume.doc" in err
    assert "Traceback" not in err


def test_cli_posting_and_keywords_are_exclusive(sample_docx, capsys):
    with pytest.raises(SystemExit) as e:
        ats.main([str(sample_docx), "--posting", str(SAMPLE_JD), "--keywords", "Go"])
    assert e.value.code == 2


def test_script_runs_as_a_subprocess(sample_docx):
    proc = subprocess.run([sys.executable, str(SCRIPTS / "ats_check.py"), str(sample_docx),
                           "--keywords", "Go,gRPC", "--lint"],
                          capture_output=True, text=True, encoding="utf-8", timeout=60)
    assert proc.returncode == 0, proc.stderr
    assert "**Keywords:** 1/2 present — missing: gRPC" in proc.stdout
