import zipfile, sys, pathlib
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

def test_build_zip_is_lf_and_deterministic(tmp_path):
    out1 = build.build_zip(SKILL, tmp_path / "a.skill")
    out2 = build.build_zip(SKILL, tmp_path / "b.skill")
    assert out1.read_bytes() == out2.read_bytes()
    with zipfile.ZipFile(out1) as z:
        names = z.namelist()
        assert "job-hunting/SKILL.md" in names
        assert not any(n.endswith(".DS_Store") or "__pycache__" in n for n in names)
        assert b"\r\n" not in z.read("job-hunting/SKILL.md")
