### Task 1: Restructure the repository into plugin layout

**Files:**
- Move: `job-hunting/` → `skills/job-hunting/`
- Move: `PROJECT-DESCRIPTION.md` → `docs/PROJECT-DESCRIPTION.md`
- Delete: `build.sh`, `build.cmd`, `deploy-cc.sh`, `deploy-cc.cmd`, `claude-code/` (whole dir), `job-hunting.skill`, `NEXT-STEPS.md`
- Create: `.claude-plugin/plugin.json`, `.claude-plugin/marketplace.json`
- Modify: `.gitignore`, `.gitattributes`

- [ ] **Step 1: Move and delete with git**

```bash
git mv job-hunting skills/job-hunting 2>/dev/null || (mkdir -p skills && git mv job-hunting skills/job-hunting)
git mv PROJECT-DESCRIPTION.md docs/PROJECT-DESCRIPTION.md
git rm -q build.sh build.cmd deploy-cc.sh deploy-cc.cmd NEXT-STEPS.md job-hunting.skill
git rm -rq claude-code
```

- [ ] **Step 2: Write plugin manifests**

`.claude-plugin/plugin.json`:
```json
{
  "name": "job-hunter",
  "version": "6.0.0",
  "description": "Personal job-search agent and career coach: sourcing, fit checks, resumes, networking, interviews, offers, pipeline — MY/SG first, market-agnostic.",
  "author": { "name": "Johannes Tang" },
  "repository": "https://github.com/cincaoais/job-hunter",
  "license": "MIT",
  "keywords": ["job-search", "career", "resume", "jobstreet", "interview"]
}
```

`.claude-plugin/marketplace.json`:
```json
{
  "name": "job-hunter",
  "owner": { "name": "Johannes Tang" },
  "plugins": [
    {
      "name": "job-hunter",
      "source": "./",
      "description": "Personal job-search agent and career coach (MY/SG first).",
      "version": "6.0.0"
    }
  ]
}
```

- [ ] **Step 3: Update ignore/attributes**

`.gitignore` becomes:
```
.DS_Store
._*
__MACOSX/
Thumbs.db
desktop.ini
dist/
job-hunt/
__pycache__/
*.pyc
.pytest_cache/
.venv/
```

`.gitattributes` becomes:
```
* text=auto
*.py text eol=lf
*.md text eol=lf
*.html text eol=lf
*.json text eol=lf
*.yml text eol=lf
```

- [ ] **Step 4: Verify tree and commit**

Run: `git status --short | head -40 && ls skills/job-hunting`
Expected: renames listed, `SKILL.md assets references` present.

```bash
git add -A
git commit -m "v6 skeleton: plugin layout, drop per-OS build/deploy scripts and command wrappers

Co-Authored-By: Claude Fable 5.1 <noreply@anthropic.com>"
```

