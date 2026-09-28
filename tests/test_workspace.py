import sys, pathlib, subprocess, os
SCRIPTS = pathlib.Path(__file__).resolve().parents[1] / "skills" / "job-hunting" / "scripts"

def test_init_creates_files(tmp_path):
    env = {**os.environ, "JOB_HUNT_DIR": str(tmp_path)}
    r = subprocess.run([sys.executable, str(SCRIPTS / "workspace.py"), "init"], env=env, capture_output=True, text=True, encoding="utf-8")
    assert r.returncode == 0, r.stderr
    for f in ["profile.md", "pipeline.md", "contacts.md", "answers.md", "seen-jobs.json"]:
        assert (tmp_path / f).exists()
    for d in ["postings", "resumes", "letters", "dossiers", "reviews"]:
        assert (tmp_path / d).is_dir()

def test_init_is_idempotent(tmp_path):
    env = {**os.environ, "JOB_HUNT_DIR": str(tmp_path)}
    subprocess.run([sys.executable, str(SCRIPTS / "workspace.py"), "init"], env=env, check=True)
    (tmp_path / "profile.md").write_text("mine", encoding="utf-8")
    subprocess.run([sys.executable, str(SCRIPTS / "workspace.py"), "init"], env=env, check=True)
    assert (tmp_path / "profile.md").read_text(encoding="utf-8") == "mine"
