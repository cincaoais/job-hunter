#!/usr/bin/env python3
"""Create or locate the job-hunt workspace.
  python3 workspace.py init   # create ~/job-hunt (or $JOB_HUNT_DIR) from templates, never overwrites
  python3 workspace.py where  # print the resolved path
"""
import shutil, sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent))
from _common import workspace_dir
ASSETS = Path(__file__).resolve().parents[1] / "assets"
FILES = {"profile.md": "profile-template.md", "pipeline.md": "pipeline-template.md",
         "contacts.md": "contacts-template.md", "answers.md": "answers-template.md"}
DIRS = ["postings", "resumes", "letters", "dossiers", "reviews"]

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

def main(argv):
    cmd = argv[0] if argv else "where"
    ws = workspace_dir()
    if cmd == "init":
        created = init(ws)
        print(f"Workspace: {ws}\nCreated: {', '.join(created) or 'nothing (already initialized)'}")
    elif cmd == "where":
        print(ws)
    else:
        print(__doc__); return 2
    return 0

if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
