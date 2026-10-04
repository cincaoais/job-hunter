import sys, pathlib, subprocess, os
SCRIPTS = pathlib.Path(__file__).resolve().parents[1] / "skills" / "job-hunting" / "scripts"

def test_init_creates_files(tmp_path):
    env = {**os.environ, "JOB_HUNT_DIR": str(tmp_path)}
    r = subprocess.run([sys.executable, str(SCRIPTS / "workspace.py"), "init"], env=env, capture_output=True, text=True, encoding="utf-8")
    assert r.returncode == 0, r.stderr
    for f in ["profile.md", "pipeline.md", "contacts.md", "answers.md", "seen-jobs.json"]:
        assert (tmp_path / f).exists()
    for d in ["postings", "resumes", "letters", "dossiers", "reviews", "interviews"]:
        assert (tmp_path / d).is_dir()

def test_init_is_idempotent(tmp_path):
    env = {**os.environ, "JOB_HUNT_DIR": str(tmp_path)}
    subprocess.run([sys.executable, str(SCRIPTS / "workspace.py"), "init"], env=env, check=True)
    (tmp_path / "profile.md").write_text("mine", encoding="utf-8")
    subprocess.run([sys.executable, str(SCRIPTS / "workspace.py"), "init"], env=env, check=True)
    assert (tmp_path / "profile.md").read_text(encoding="utf-8") == "mine"

def _isolated_env(tmp_path):
    env = {k: v for k, v in os.environ.items() if k != "JOB_HUNT_DIR"}
    return {**env, "HOME": str(tmp_path / "home"), "USERPROFILE": str(tmp_path / "home")}

def test_where_warns_when_started_below_a_vault(tmp_path):
    (tmp_path / "vault" / "job-hunt").mkdir(parents=True)
    (tmp_path / "vault" / "wiki").mkdir()
    r = subprocess.run([sys.executable, str(SCRIPTS / "workspace.py"), "where"], cwd=tmp_path / "vault" / "wiki",
                       env=_isolated_env(tmp_path), capture_output=True, text=True, encoding="utf-8")
    assert r.returncode == 0 and r.stdout.strip() == str(tmp_path / "home" / "job-hunt")
    assert "warning:" in r.stderr and "vault" in r.stderr

def test_init_refuses_to_create_a_stray_workspace(tmp_path):
    (tmp_path / "vault" / "job-hunt").mkdir(parents=True)
    (tmp_path / "vault" / "wiki").mkdir()
    r = subprocess.run([sys.executable, str(SCRIPTS / "workspace.py"), "init"], cwd=tmp_path / "vault" / "wiki",
                       env=_isolated_env(tmp_path), capture_output=True, text=True, encoding="utf-8")
    assert r.returncode == 2 and "warning:" in r.stderr
    assert not (tmp_path / "home" / "job-hunt").exists()
