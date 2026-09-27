"""Live smoke tests against the real job boards.

Marked `network`, so CI (`pytest -m "not network"`) skips them; run them by
hand with `python3 -m pytest -q -m network`. Each assertion message carries
the source module's `LAST_WARNINGS`, so a failure says which HTTP call broke.
"""
import pathlib
import sys

import pytest

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[1] / "skills" / "job-hunting" / "scripts"))
pytestmark = pytest.mark.network


@pytest.fixture(scope="module")
def jobstreet_results():
    """One live JobStreet MY search, shared by the tests that need it."""
    from sources import jobstreet
    jobs = jobstreet.search("software engineer", "Kuala Lumpur", country="MY")
    return jobs, list(jobstreet.LAST_WARNINGS)


def test_jobstreet_live(jobstreet_results):
    jobs, warnings = jobstreet_results
    assert len(jobs) >= 1, f"JobStreet MY returned no jobs; LAST_WARNINGS={warnings}"


def test_mcf_live():
    from sources import mcf
    jobs = mcf.search("software engineer", "Singapore", country="SG")
    assert len(jobs) >= 1, f"MCF returned no jobs; LAST_WARNINGS={mcf.LAST_WARNINGS}"


def test_fetch_posting_live_jobstreet_id(jobstreet_results):
    jobs, _ = jobstreet_results
    if not jobs:
        pytest.skip("the live JobStreet search returned nothing to fetch")
    import fetch_posting
    from sources import jobstreet
    job_id = jobs[0]["id"].split(":", 1)[1]
    job, reason = fetch_posting.fetch(job_id)
    assert job is not None, (f"fetch_posting could not fetch JobStreet id {job_id}: {reason}; "
                             f"LAST_WARNINGS={jobstreet.LAST_WARNINGS}")
    assert job["source"] == "jobstreet"
    assert job["description_md"].strip(), f"empty description for JobStreet id {job_id}"
    assert fetch_posting.render_posting(job).startswith("---\nsource: jobstreet\n")
