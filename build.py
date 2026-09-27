#!/usr/bin/env python3
"""Build/check/link the job-hunter skills.

  python3 build.py            -> dist/job-hunting.skill (zip for claude.ai upload)
  python3 build.py --check    -> validate SKILL.md files, exit 1 on problems
  python3 build.py --link     -> symlink skills/* into ~/.claude/skills (dev convenience)
Works on macOS, Linux and Windows (python build.py).
"""
from __future__ import annotations
import argparse, os, re, shutil, sys, zipfile
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
    raw = p.read_bytes()
    text = raw.decode("utf-8")
    fm = parse_frontmatter(text)
    name = fm.get("name", "")
    if name != skill_dir.name or not NAME_RE.match(name) or "claude" in name or "anthropic" in name:
        problems.append(f"{p}: name '{name}' must equal dir '{skill_dir.name}', be [a-z0-9-], and avoid reserved words")
    desc = fm.get("description", "")
    if not desc:
        problems.append(f"{p}: description missing")
    elif len(desc) > MAX_DESC:
        problems.append(f"{p}: description is {len(desc)} chars (max {MAX_DESC})")
    n = len(text.splitlines())
    if n > MAX_SKILL_LINES:
        problems.append(f"{p}: {n} lines (max {MAX_SKILL_LINES})")
    if b"\r\n" in raw:
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

def link_skills(force: bool = False) -> list[str]:
    dest_root, done = Path.home() / ".claude" / "skills", []
    dest_root.mkdir(parents=True, exist_ok=True)
    for d in sorted(SKILLS.iterdir()):
        if not (d / "SKILL.md").exists():
            continue
        dest = dest_root / d.name
        if dest.is_symlink() or dest.exists():
            if dest.is_symlink() or dest.is_file():
                dest.unlink()
            elif force:
                shutil.rmtree(dest)
            else:
                done.append(f"SKIP {dest}: exists and is not a symlink (use --force to replace)")
                continue
        try:
            os.symlink(d, dest, target_is_directory=True)
        except OSError:  # Windows without developer mode
            shutil.copytree(d, dest)
        done.append(f"{dest} -> {d}")
    return done

def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--check", action="store_true")
    ap.add_argument("--link", action="store_true")
    ap.add_argument("--force", action="store_true", help="with --link, replace real (non-symlink) directories")
    a = ap.parse_args(argv)
    problems = [p for d in sorted(SKILLS.iterdir()) if d.is_dir() for p in check_skill(d)]
    for p in problems:
        print("PROBLEM:", p)
    if problems:
        return 1
    if a.check:
        count = sum(1 for d in SKILLS.iterdir() if (d / "SKILL.md").is_file())
        print(f"OK: {count} skills pass checks"); return 0
    if a.link:
        print("\n".join(link_skills(force=a.force))); print("Restart Claude Code to pick up the skills."); return 0
    out = build_zip(MAIN, DIST / "job-hunting.skill")
    with zipfile.ZipFile(out) as z:
        print(f"Built {out} ({out.stat().st_size} bytes, {len(z.namelist())} files)")
    return 0

if __name__ == "__main__":
    sys.exit(main())
