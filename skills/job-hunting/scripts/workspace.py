#!/usr/bin/env python3
"""Create or locate the job-hunt workspace.
  python3 workspace.py init   # create ~/job-hunt (or $JOB_HUNT_DIR) from templates, never overwrites
  python3 workspace.py where  # print the resolved path
"""
import os, shutil, sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent))
from _common import use_utf8_output, workspace_dir
ASSETS = Path(__file__).resolve().parents[1] / "assets"
FILES = {"profile.md": "profile-template.md", "pipeline.md": "pipeline-template.md",
         "contacts.md": "contacts-template.md", "answers.md": "answers-template.md"}
DIRS = ["postings", "resumes", "letters", "dossiers", "reviews", "interviews"]

def init(ws: Path) -> list[str]:
    created = []
    ws.mkdir(parents=True, exist_ok=True)
    for name, tpl in FILES.items():
        if not (ws / name).exists():
            shutil.copyfile(ASSETS / tpl, ws / name); created.append(name)
    if not (ws / "seen-jobs.json").exists():
        (ws / "seen-jobs.json").write_text("{}", encoding="utf-8"); created.append("seen-jobs.json")
    for d in DIRS:
        if not (ws / d).exists():
            (ws / d).mkdir(); created.append(d + "/")
    return created

def stray_workspace(ws: Path, cwd: Path) -> Path | None:
    """The nearest `job-hunt/` at or above `cwd` when it is not `ws` — a session started in a vault subfolder."""
    for folder in (cwd, *cwd.parents):
        candidate = folder / "job-hunt"
        if candidate.is_dir():
            return None if candidate.resolve() == ws.resolve() else candidate
    return None

def main(argv):
    use_utf8_output()
    cmd = argv[0] if argv else "where"
    ws = workspace_dir()
    stray = stray_workspace(ws, Path.cwd())
    if stray:
        print(f"warning: {stray} is above the current folder but the workspace in use is {ws} — "
              f"set JOB_HUNT_DIR to {stray} or start from {stray.parent}", file=sys.stderr)
    if cmd == "init":
        if stray and not ws.exists() and not os.environ.get("JOB_HUNT_DIR"):
            return 2
        created = init(ws)
        print(f"Workspace: {ws}\nCreated: {', '.join(created) or 'nothing (already initialized)'}")
    elif cmd == "where":
        print(ws)
    else:
        print(__doc__); return 2
    return 0

if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
