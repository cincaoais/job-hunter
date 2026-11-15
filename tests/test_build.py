import fnmatch, json, pathlib, re, sys
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[1]))
import build

ROOT = pathlib.Path(__file__).resolve().parents[1]
SKILL = ROOT / "skills" / "job-hunting"

def test_parse_frontmatter_reads_name_and_description():
    fm = build.parse_frontmatter("---\nname: x\ndescription: >-\n  a b\n  c\nmetadata:\n  version: \"1\"\n---\nbody")
    assert fm["name"] == "x"
    assert fm["description"] == "a b c"

def test_check_skill_passes_on_repo_skill():
    assert build.check_skill(SKILL) == []

def test_check_skill_flags_long_description(tmp_path):
    d = tmp_path / "foo"; d.mkdir()
    (d / "SKILL.md").write_text("---\nname: foo\ndescription: " + "x" * 1100 + "\n---\n", encoding="utf-8")
    problems = build.check_skill(d)
    assert any("description" in p for p in problems)

def test_check_skill_flags_name_mismatch(tmp_path):
    d = tmp_path / "foo"; d.mkdir()
    (d / "SKILL.md").write_text("---\nname: bar\ndescription: ok\n---\n", encoding="utf-8")
    assert any("name" in p for p in build.check_skill(d))

def test_check_skill_flags_crlf(tmp_path):
    d = tmp_path / "foo"; d.mkdir()
    (d / "SKILL.md").write_bytes(b"---\r\nname: foo\r\ndescription: ok\r\n---\r\n")
    problems = build.check_skill(d)
    assert any("CRLF" in p for p in problems)

def _make_skill_with_n_lines(root, name, n):
    d = root / name; d.mkdir()
    header = f"---\nname: {name}\ndescription: fine\n---\n"
    header_lines = len(header.splitlines())
    body = "\n".join(f"line {i}" for i in range(n - header_lines)) + "\n"
    (d / "SKILL.md").write_text(header + body, encoding="utf-8", newline="\n")
    return d

def test_text_files_check_out_with_lf_everywhere():
    def resolve(lines, path, attr):
        value = None
        for line in lines:
            line = line.strip()
            if not line or line.startswith("#"):
                continue
            pattern, *attrs = line.split()
            target = path if "/" in pattern else path.rsplit("/", 1)[-1]
            if fnmatch.fnmatchcase(target, pattern.lstrip("/")):
                for a in attrs:
                    if a.startswith(attr + "="):
                        value = a.split("=", 1)[1]
        return value

    assert resolve(["* eol=lf", "*.txt eol=crlf"], "a.txt", "eol") == "crlf"
    lines = (ROOT / ".gitattributes").read_text(encoding="utf-8").splitlines()
    for path in ("skills/job-hunting/assets/slop-phrases.txt", "pytest.ini", ".gitignore"):
        assert resolve(lines, path, "eol") == "lf", path

def test_check_skill_line_count_boundary(tmp_path):
    ok_dir = _make_skill_with_n_lines(tmp_path, "ok", 500)
    ok_problems = build.check_skill(ok_dir)
    assert not any("lines" in p for p in ok_problems)

    bad_dir = _make_skill_with_n_lines(tmp_path, "bad", 501)
    bad_problems = build.check_skill(bad_dir)
    assert any("lines" in p for p in bad_problems)

def test_check_ok_line_counts_only_skill_directories(tmp_path, monkeypatch, capsys):
    for name in ("alpha", "beta"):
        _make_skill_with_n_lines(tmp_path, name, 10)
    (tmp_path / ".DS_Store").write_bytes(b"\0")
    monkeypatch.setattr(build, "SKILLS", tmp_path)
    assert build.main(["--check"]) == 0
    assert "OK: 2 skills pass checks" in capsys.readouterr().out

def test_command_skills_use_the_launcher():
    for skill in sorted((ROOT / "skills").iterdir()):
        text = (skill / "SKILL.md").read_text(encoding="utf-8")
        assert re.search(r"python3?\s+\S*scripts/", text) is None, skill.name
        assert "command -v python" not in text, skill.name
        assert re.search(r"(?:python3?|sh|bash|py -3)\s+\S*scripts/(?!jh )[a-z_]+\.py", text) is None, skill.name

def test_references_use_the_launcher():
    refs = sorted((SKILL / "references").rglob("*.md"))
    assert refs
    patterns = (r"python3?\s+\S*scripts/", r"(?:python3?|sh|bash|py -3)\s+\S*scripts/(?!jh )[a-z_]+\.py")
    for p in refs:
        text = p.read_text(encoding="utf-8")
        assert "command -v python" not in text, str(p.relative_to(ROOT))
        for pattern in patterns:
            m = re.search(pattern, text)
            assert m is None, f"{p.relative_to(ROOT)}:{text.count(chr(10), 0, m.start()) + 1}: {m.group(0)}"

def test_versions_agree():
    plugin = json.loads((ROOT / ".claude-plugin" / "plugin.json").read_text(encoding="utf-8"))
    market = json.loads((ROOT / ".claude-plugin" / "marketplace.json").read_text(encoding="utf-8"))
    entry = next(p for p in market["plugins"] if p["name"] == "job-hunter")
    text = (SKILL / "SKILL.md").read_text(encoding="utf-8")
    m = re.search(r'^\s+version:\s*"([^"]+)"', text, re.M)
    assert m, "metadata.version missing from skills/job-hunting/SKILL.md"
    assert plugin["version"] == entry["version"] == m.group(1)
