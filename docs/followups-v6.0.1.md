# v6.0.1 follow-ups

Minor items the v6.0.0 final review deferred ("fix later"); none blocks the release.

## Scripts

- [ ] `_common.read_table`/`_section_bounds` docstrings: say that `heading` must include its `#` prefix (`## Offers`, not `Offers`) — `skills/job-hunting/scripts/_common.py:308`, `:353`
- [ ] LinkedIn guest-search regexes depend on attribute order and a bare `<li>` — `skills/job-hunting/scripts/sources/linkedin.py:38-46`
- [ ] `_DETAIL_URL_RE` takes the first `/jobs/view/` link on the detail page, which may belong to a "similar jobs" card — `skills/job-hunting/scripts/sources/linkedin.py:48`, `:166`
- [ ] Country validation is inconsistent across sources: JobStreet and MCF raise `ValueError`, LinkedIn and Hiredly accept anything — `sources/jobstreet.py:55`, `sources/mcf.py:31`, `sources/linkedin.py:119`, `sources/hiredly.py:88`
- [ ] `_TAG_RE` does not handle HTML comments (a `>` inside `<!-- -->` leaks text) — `skills/job-hunting/scripts/_common.py:140`
- [ ] Hiredly `detail()` and LinkedIn `detail()` `posted`/`salary_label` are unverified against a live page — `sources/hiredly.py:135`, `sources/linkedin.py:168-177`
- [ ] Dealbreaker matching ignores negation ("no 6-day work week" still knocks a posting out) — `skills/job-hunting/scripts/search_jobs.py:270`
- [ ] `cloakbrowser.launch()` has no timeout of its own; only `goto` is bounded — `skills/job-hunting/scripts/fetch_posting.py:248`
- [ ] Generic extraction's last-resort fallback can leak the `<title>` text into the description when a page has no `<head>` — `skills/job-hunting/scripts/fetch_posting.py:178`
- [ ] No test that the Offers table survives `tracker.py add` — `tests/test_tracker.py`
- [ ] Malformed dates are invisible in `tracker.py today` (the row silently drops out of every section) — `skills/job-hunting/scripts/tracker.py:113`, `:134`
- [ ] `ats_check.py` tech vocabulary includes everyday words (Spring, Swift, Rust, …) that count as keywords in prose — `skills/job-hunting/scripts/ats_check.py:281`

## Resume builder (Task 14 review)

- [ ] The `TypeError` retry around `cloak.launch(stealth_args=False)` can mask an unrelated `TypeError` (backend failure classes are now printed; this retry is the rest) — `skills/job-hunting/scripts/build_resume.py:719`
- [ ] `_skill_groups` is all-or-nothing: one unlabeled item drops the whole line's skills from the JSON Resume export — `skills/job-hunting/scripts/build_resume.py:134`
- [ ] A contact line wrapped over two lines starts its second half with a separator (chicago, accent-band) — `skills/job-hunting/scripts/build_resume.py:239`
- [ ] Template cosmetics: creative-sidebar weight 700, executive date alignment, empty Contact heading, accent band not edge-to-edge under the 14 mm `@page` margin — `skills/job-hunting/assets/templates/`
- [ ] `docx_text` reads a nested paragraph (e.g. inside a text box) twice: once in its own line and again in the enclosing paragraph's runs — `skills/job-hunting/scripts/_common.py:167`
- [ ] A stale docstring in `build_resume.py`, and no direct test for `_safe_href` — `skills/job-hunting/scripts/build_resume.py:556`

## References

- [ ] `interview-prep.md` still carries the Malaysia law sentence that belongs in `markets/my.md` — `skills/job-hunting/references/interview-prep.md:79`
- [ ] `markets/my.md` legal accuracy: the "not to complain" wording vs EA s.69F (`:164`, `:176`); §8 bonus-contribution item (`:144`); the contributions table header vs the EPF Act (`:104`); "EPF Act 1991" attribution unhedged (`:104`)

## Round 4 leftovers (behaviour scenarios)

- [ ] `networking.md`: give the dated new-contact sequence directly under the two search links — `skills/job-hunting/references/networking.md:40`
- [ ] `post-offer.md` §9: print the `withdrawn` tracker line under each withdrawal draft — `skills/job-hunting/references/post-offer.md:145`
- [ ] `networking.md`: list the alumni search link first, to match the warmth order of the referral map — `skills/job-hunting/references/networking.md:22`, `:40`
- [ ] Scenario Q checklist bullet 6 wording (pipeline closed with `tracker.py set`, pending the user's go-ahead) — `tests/behavioral-scenarios.md:345`
- [ ] Run nits recorded in the Round 4 block — `tests/behavioral-scenarios.md:455`
- [ ] Re-run scenarios O and Q after the items above (and after the v6.0.0 references-brief and referral-ask template changes)

## From the final fix-wave re-review (2026-09-27)

- [ ] `fetch_posting.fetch()`: on the HTTP path, treat a thin page with challenge markers as blocked (`if blocked and len(extracted["text"]) < MIN_GENERIC_TEXT: return None, "blocked"`) so a challenge page with the user's IP is never saved. **Do first.**
- [ ] `fetch_posting.py` ~339: when plain HTTP already returned an unblocked short posting, keep it even if the browser render is also thin (return "blocked" only when `blocked or not extracted["text"]`).
- [ ] `fetch_posting.py` ~272-280: browser-path markers checked in the first 2,000 chars reject a real JD mentioning "access denied" early; consider title-only markers for generic phrases.
- [ ] `build_resume.py` ~207/225: exempt `**Label:**` lines from lazy bullet continuation.
- [ ] Windows: the App Execution Alias stub `python3.exe` can satisfy `command -v python3`; replace the inline fallback with a runtime probe (`python3 -c ''` then `python -c ''`) and verify on a real Windows machine.
- [ ] Thin-page browser fallback fires on short valid postings (T8); temp-HTML unlink not OSError-guarded (T14-2); `indeed._MISSING` literal "None"; `Applied` auto-fill edge cases (T9) — confirm or close.
