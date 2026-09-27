import zipfile, sys, pathlib
import pytest
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
    (d / "SKILL.md").write_text(header + body, encoding="utf-8")
    return d

def test_check_skill_line_count_boundary(tmp_path):
    ok_dir = _make_skill_with_n_lines(tmp_path, "ok", 500)
    ok_problems = build.check_skill(ok_dir)
    assert not any("lines" in p for p in ok_problems)

    bad_dir = _make_skill_with_n_lines(tmp_path, "bad", 501)
    bad_problems = build.check_skill(bad_dir)
    assert any("lines" in p for p in bad_problems)

def test_link_skills_refuses_real_dir(tmp_path, monkeypatch):
    monkeypatch.setattr(build.Path, "home", lambda: tmp_path)
    dest = tmp_path / ".claude" / "skills" / "job-hunting"
    dest.mkdir(parents=True)
    marker = dest / "keep-me.txt"
    marker.write_text("hello", encoding="utf-8")

    build.link_skills()
    assert marker.exists()
    assert not dest.is_symlink()

    build.link_skills(force=True)
    if sys.platform == "win32":
        assert dest.is_symlink() or (dest.is_dir() and (dest / "SKILL.md").exists())
    else:
        assert dest.is_symlink()

def test_build_zip_is_lf_and_deterministic(tmp_path):
    out1 = build.build_zip(SKILL, tmp_path / "a.skill")
    out2 = build.build_zip(SKILL, tmp_path / "b.skill")
    assert out1.read_bytes() == out2.read_bytes()
    with zipfile.ZipFile(out1) as z:
        names = z.namelist()
        assert "job-hunting/SKILL.md" in names
        assert not any(n.endswith(".DS_Store") or "__pycache__" in n for n in names)
        assert b"\r\n" not in z.read("job-hunting/SKILL.md")

@pytest.mark.parametrize("verb, command", [("today", "today"), ("review", "funnel")])
def test_inline_tracker_command_falls_back_to_python(verb, command):
    text = (ROOT / "skills" / verb / "SKILL.md").read_text(encoding="utf-8")
    body = text.split("\n---\n", 1)[1]
    first = next(line for line in body.splitlines() if line.strip())
    assert first.startswith("!`") and "command -v python3 || command -v python" in first
    assert first.endswith(f"tracker.py {command}`")
