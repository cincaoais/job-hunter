### Task 16: Live smoke tests and behavioral scenarios M–Q

**Files:**
- Create: `tests/test_live.py`
- Modify: `tests/behavioral-scenarios.md` (append M–Q + a "v6 fixtures" note), `tests/fixtures/sample-profile.md` (align with the new template numbering; keep the planted 4-vs-5-years tension)

`tests/test_live.py`:
```python
import pytest, sys, pathlib
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[1] / "skills" / "job-hunting" / "scripts"))
pytestmark = pytest.mark.network

def test_jobstreet_live():
    from sources import jobstreet
    assert len(jobstreet.search("software engineer", "Kuala Lumpur", country="MY")) >= 1

def test_mcf_live():
    from sources import mcf
    assert len(mcf.search("software engineer", "Singapore", country="SG")) >= 1
```

Scenarios to append (same format as A–L):
- **M — Today view**: fixture pipeline with one overdue, one stale, one auto-cold candidate, one interview in 3 days; expected: runs `tracker.py today` (workspace) or computes from the table (chat), lists each with the concrete next action, drafts the follow-up for the overdue row on request, applies auto-cold only after confirmation.
- **N — Knockout + legitimacy cap**: posting requires "Singapore Citizen/PR only" for an MY-based candidate without SG status, and is reposted 60 days; expected: verdict "skip (knockout: work authorization)", the repost flag reported, no resume edits proposed.
- **O — Referral before apply**: "Apply to Grab for me"; expected: builds the referral map first (people-search links, ex-colleague check from contacts/profile), drafts the ≤150-word ask, proposes the 3-touch sequence with dates, only then the application; logs contacts with Next touch.
- **P — Anti-slop gate**: "Write a cover letter for this posting" with no story provided; expected: asks for one specific story with options from the profile evidence bank and one company fact (or fetches one via dossier), draft contains no phrase from `slop-phrases.txt`, references a concrete number from the profile.
- **Q — Post-offer**: "I accepted, what now?"; expected: acceptance-in-writing checklist, resignation letter draft with correct MY notice from `markets/my.md`, withdrawal messages for the other pipeline rows, references brief, 30-60-90 skeleton tied to the JD, pipeline set to accepted and others withdrawn.

- [ ] **Step 1: Write files; run `python3 -m pytest -q -m network`** → 2 passed (needs internet). `python3 -m pytest -q -m "not network"` → all pass.
- [ ] **Step 2: Commit** — `tests: live board smoke (network-marked), behavioral scenarios M–Q`.

