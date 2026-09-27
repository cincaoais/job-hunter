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
    """fetch_posting turns a live JobStreet id into a posting.

    Tries the first three search results, so one expired or odd listing
    does not fail the test; every miss is reported if none fetches.
    """
    jobs, _ = jobstreet_results
    if not jobs:
        pytest.skip("the live JobStreet search returned nothing to fetch")
    import fetch_posting
    from sources import jobstreet
    misses = []
    for record in jobs[:3]:
        raw_id = str(record.get("id") or "")
        prefix, _, job_id = raw_id.partition(":")
        if prefix != "jobstreet" or not job_id.isdigit():
            misses.append(f"{raw_id!r}: not a jobstreet:<digits> id")
            continue
        job, reason = fetch_posting.fetch(job_id)
        if job is None or not str(job.get("description_md") or "").strip():
            misses.append(f"{job_id}: {reason or 'empty description'}; "
                          f"LAST_WARNINGS={list(jobstreet.LAST_WARNINGS)}")
            continue
        assert job["source"] == "jobstreet", f"{job_id}: source {job['source']!r}"
        assert fetch_posting.render_posting(job).startswith("---\nsource: jobstreet\n")
        return
    pytest.fail("fetch_posting fetched none of the first 3 JobStreet results: " + " | ".join(misses))
