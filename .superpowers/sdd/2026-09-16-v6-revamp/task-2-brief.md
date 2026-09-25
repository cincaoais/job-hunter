### Task 2: `build.py` — check, zip, link

**Files:**
- Create: `build.py`
- Test: `tests/test_build.py`

**Interfaces:**
- Produces: `python3 build.py --check` (exit 1 on violations), `python3 build.py` (writes `dist/job-hunting.skill`), `python3 build.py --link` (symlinks/junctions `skills/*` into `~/.claude/skills/`). Importable functions: `parse_frontmatter(text) -> dict`, `check_skill(skill_dir: Path) -> list[str]`, `build_zip(skill_dir: Path, out: Path) -> Path`.

- [ ] **Step 1: Write the failing tests**

`tests/test_build.py`:
```python
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
```

- [ ] **Step 2: Run to verify failure**

Run: `python3 -m pytest tests/test_build.py -q`
Expected: FAIL with `ModuleNotFoundError: No module named 'build'`.

- [ ] **Step 3: Implement `build.py`**

```python
#!/usr/bin/env python3
"""Build/check/link the job-hunter skills.

  python3 build.py            -> dist/job-hunting.skill (zip for claude.ai upload)
  python3 build.py --check    -> validate SKILL.md files, exit 1 on problems
  python3 build.py --link     -> symlink skills/* into ~/.claude/skills (dev convenience)
Works on macOS, Linux and Windows (python build.py).
"""
from __future__ import annotations
import argparse, os, re, sys, zipfile
from pathlib import Path

ROOT = Path(__file__).resolve().parent
SKILLS = ROOT / "skills"
MAIN = SKILLS / "job-hunting"
DIST = ROOT / "dist"
EXCLUDE_NAMES = {".DS_Store", "Thumbs.db", "desktop.ini", "__pycache__", ".pytest_cache"}
TEXT_SUFFIXES = {".md", ".py", ".html", ".json", ".txt", ".yml", ".yaml", ".css"}
MAX_SKILL_LINES, MAX_DESC = 500, 1024
NAME_RE = re.compile(r"^[a-z0-9]+(-[a-z0-9]+)*$")

def parse_frontmatter(text: str) -> dict:
    m = re.match(r"^---\r?\n(.*?)\r?\n---", text, re.S)
    if not m:
        return {}
    fm, key, buf, out = m.group(1).splitlines(), None, [], {}
    def flush():
        if key is not None:
            out[key] = " ".join(s.strip() for s in buf).strip()
    for line in fm:
        if line and not line.startswith((" ", "\t")):
            flush()
            k, _, v = line.partition(":")
            key, buf = k.strip(), [] if v.strip() in (">-", ">", "|", "|-", "") else [v.strip()]
        elif key is not None:
            buf.append(line)
    flush()
    return out

def check_skill(skill_dir: Path) -> list[str]:
    p, problems = skill_dir / "SKILL.md", []
    if not p.exists():
        return [f"{skill_dir}: missing SKILL.md"]
    text = p.read_text(encoding="utf-8")
    fm = parse_frontmatter(text)
    name = fm.get("name", "")
    if name != skill_dir.name or not NAME_RE.match(name) or "claude" in name or "anthropic" in name:
        problems.append(f"{p}: name '{name}' must equal dir '{skill_dir.name}', be [a-z0-9-], and avoid reserved words")
    desc = fm.get("description", "")
    if not desc:
        problems.append(f"{p}: description missing")
    elif len(desc) > MAX_DESC:
        problems.append(f"{p}: description is {len(desc)} chars (max {MAX_DESC})")
    n = text.count("\n") + 1
    if n > MAX_SKILL_LINES:
        problems.append(f"{p}: {n} lines (max {MAX_SKILL_LINES})")
    if "\r\n" in text:
        problems.append(f"{p}: CRLF line endings")
    return problems

def _iter_files(skill_dir: Path):
    for f in sorted(skill_dir.rglob("*")):
        if f.is_file() and not (set(f.parts) & EXCLUDE_NAMES) and not f.name.startswith("._"):
            yield f

def build_zip(skill_dir: Path, out: Path) -> Path:
    out.parent.mkdir(parents=True, exist_ok=True)
    with zipfile.ZipFile(out, "w", zipfile.ZIP_DEFLATED) as z:
        for f in _iter_files(skill_dir):
            data = f.read_bytes()
            if f.suffix in TEXT_SUFFIXES:
                data = data.replace(b"\r\n", b"\n")
            info = zipfile.ZipInfo(f"{skill_dir.name}/{f.relative_to(skill_dir).as_posix()}", date_time=(2020, 1, 1, 0, 0, 0))
            info.compress_type = zipfile.ZIP_DEFLATED
            info.external_attr = 0o644 << 16
            z.writestr(info, data)
    return out

def link_skills() -> list[str]:
    dest_root, done = Path.home() / ".claude" / "skills", []
    dest_root.mkdir(parents=True, exist_ok=True)
    for d in sorted(SKILLS.iterdir()):
        if not (d / "SKILL.md").exists():
            continue
        dest = dest_root / d.name
        if dest.is_symlink() or dest.exists():
            if dest.is_symlink() or dest.is_file():
                dest.unlink()
            else:
                import shutil; shutil.rmtree(dest)
        try:
            os.symlink(d, dest, target_is_directory=True)
        except OSError:  # Windows without developer mode
            import shutil; shutil.copytree(d, dest)
        done.append(f"{dest} -> {d}")
    return done

def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--check", action="store_true")
    ap.add_argument("--link", action="store_true")
    a = ap.parse_args(argv)
    problems = [p for d in sorted(SKILLS.iterdir()) if d.is_dir() for p in check_skill(d)]
    for p in problems:
        print("PROBLEM:", p)
    if problems:
        return 1
    if a.check:
        print(f"OK: {len(list(SKILLS.iterdir()))} skills pass checks"); return 0
    if a.link:
        print("\n".join(link_skills())); print("Restart Claude Code to pick up the skills."); return 0
    out = build_zip(MAIN, DIST / "job-hunting.skill")
    with zipfile.ZipFile(out) as z:
        print(f"Built {out} ({out.stat().st_size} bytes, {len(z.namelist())} files)")
    return 0

if __name__ == "__main__":
    sys.exit(main())
```

- [ ] **Step 4: Run tests**

Run: `python3 -m pytest tests/test_build.py -q`
Expected: 5 passed. (If `test_check_skill_passes_on_repo_skill` fails on description length, that is fixed in Task 5 when SKILL.md is rewritten — mark xfail until then is NOT allowed; instead shorten the description now to ≤ 1024 chars.)

- [ ] **Step 5: Commit**

```bash
git add build.py tests/test_build.py
git commit -m "build.py: cross-platform check/zip/link replaces four shell scripts

Co-Authored-By: Claude Fable 5.1 <noreply@anthropic.com>"
```

