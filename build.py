#!/usr/bin/env python3
"""Validate the job-hunter SKILL.md files.

  python build.py            -> same as --check
  python build.py --check    -> validate SKILL.md files, exit 1 on problems
Works on macOS, Linux and Windows (python build.py).
"""
from __future__ import annotations
import argparse, re, sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent
SKILLS = ROOT / "skills"
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

def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--check", action="store_true", help="validate SKILL.md files (the default action)")
    ap.parse_args(argv)
    problems = [p for d in sorted(SKILLS.iterdir()) if d.is_dir() for p in check_skill(d)]
    for p in problems:
        print("PROBLEM:", p)
    if problems:
        return 1
    count = sum(1 for d in SKILLS.iterdir() if (d / "SKILL.md").is_file())
    print(f"OK: {count} skills pass checks")
    return 0

if __name__ == "__main__":
    sys.exit(main())