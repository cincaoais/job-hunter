### Task 3: CI workflow

**Files:**
- Create: `.github/workflows/ci.yml`

- [ ] **Step 1: Write the workflow**

```yaml
name: ci
on:
  push: { branches: [main], tags: ["v*"] }
  pull_request:
jobs:
  test:
    strategy:
      matrix: { os: [ubuntu-latest, windows-latest] }
    runs-on: ${{ matrix.os }}
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v5
        with: { python-version: "3.12" }
      - run: python -m pip install pytest
      - run: python -m pytest -q -m "not network"
      - run: python build.py --check
  build:
    needs: test
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v5
        with: { python-version: "3.12" }
      - run: python build.py
      - uses: actions/upload-artifact@v4
        with: { name: job-hunting.skill, path: dist/job-hunting.skill }
      - if: startsWith(github.ref, 'refs/tags/v')
        uses: softprops/action-gh-release@v2
        with: { files: dist/job-hunting.skill }
```

- [ ] **Step 2: Add pytest marker config**

Create `pytest.ini`:
```ini
[pytest]
markers =
    network: hits real job boards (skipped in CI)
testpaths = tests
```

- [ ] **Step 3: Commit**

```bash
git add .github/workflows/ci.yml pytest.ini
git commit -m "ci: pytest on ubuntu+windows, build check, release asset on tags

Co-Authored-By: Claude Fable 5.1 <noreply@anthropic.com>"
```

