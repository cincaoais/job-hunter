#!/usr/bin/env python3
"""Restore the job-hunter handoff into this machine's Claude Code profile.

  python3 docs/handoff/restore.py             # memory files only
  python3 docs/handoff/restore.py --history   # also unpack the old transcripts
  python3 docs/handoff/restore.py --force     # overwrite existing memory files
  python3 docs/handoff/restore.py --dry-run   # show what would happen

Claude Code keeps per-project memory in ~/.claude/projects/<slug>/memory/,
where <slug> is this checkout's absolute path with every character that is
not a letter or digit replaced by "-". Works on macOS, Linux and Windows.
"""
from __future__ import annotations

import argparse
import re
import shutil
import sys
import tarfile
from pathlib import Path

HANDOFF = Path(__file__).resolve().parent
REPO = HANDOFF.parents[1]
LEDGER = REPO / ".superpowers" / "sdd" / "2026-09-16-v6-revamp" / "progress.md"
HISTORY = HANDOFF / "history" / "claude-session-history.tar.gz"


def project_slug(path: Path) -> str:
    return re.sub(r"[^A-Za-z0-9]", "-", str(path))


def claude_project_dir(home: Path | None = None) -> Path:
    return (home or Path.home()) / ".claude" / "projects" / project_slug(REPO)


def copy_memory(dest: Path, *, force: bool, dry_run: bool) -> list[str]:
    done = []
    for src in sorted((HANDOFF / "memory").glob("*.md")):
        target = dest / src.name
        if target.exists() and not force:
            done.append(f"kept existing {target}")
            continue
        if not dry_run:
            dest.mkdir(parents=True, exist_ok=True)
            shutil.copyfile(src, target)
        done.append(f"copied {src.name} -> {target}")
    return done


def unpack_history(dest: Path, *, dry_run: bool) -> str:
    out = dest / "handoff-history"
    if not HISTORY.exists():
        return f"no history archive at {HISTORY}"
    if not dry_run:
        out.mkdir(parents=True, exist_ok=True)
        with tarfile.open(HISTORY, "r:gz") as tar:
            members = [m for m in tar.getmembers()
                       if not (m.name.startswith("/") or ".." in Path(m.name).parts)]
            tar.extractall(out, members=members)
    return f"unpacked transcripts -> {out} (read-only reference; not a resumable session)"


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--history", action="store_true", help="also unpack the old session transcripts")
    ap.add_argument("--force", action="store_true", help="overwrite memory files that already exist")
    ap.add_argument("--dry-run", action="store_true", help="print actions without writing")
    args = ap.parse_args(argv)

    dest = claude_project_dir()
    print(f"Repo:            {REPO}")
    print(f"Claude project:  {dest}")
    for line in copy_memory(dest / "memory", force=args.force, dry_run=args.dry_run):
        print(" ", line)
    if args.history:
        print(" ", unpack_history(dest, dry_run=args.dry_run))
    print(f"SDD ledger:      {'found' if LEDGER.exists() else 'MISSING'} ({LEDGER.relative_to(REPO)})")
    print("Next: install the environment (docs/handoff/HANDOFF.md section 6), run\n"
          "  python3 -m pytest -q -m \"not network\"  and  python3 build.py --check,\n"
          "then open Claude Code here and say: continue the v6 revamp")
    return 0 if LEDGER.exists() else 1


if __name__ == "__main__":
    sys.exit(main())
