# Backlog

Open items carried over from the v6.0.1 follow-ups list, pruned for v7.0.0.
Each is small and none blocks use. Line numbers are approximate.

## Scripts

- [ ] `_common.read_table` / `_section_bounds` docstrings: say that `heading` includes its `#` prefix (`## Offers`, not `Offers`).
- [ ] LinkedIn guest-search regexes depend on attribute order and a bare `<li>`; a drift now prints a "cards found but none parsed" warning, but the parser itself is still brittle — `sources/linkedin.py`.
- [ ] LinkedIn `_DETAIL_URL_RE` takes the first `/jobs/view/` link, which may belong to a "similar jobs" card; its `detail()` `posted` / `salary_label` are unverified against a live page.
- [ ] Country validation: JobStreet and MCF raise `ValueError` on an unknown country, LinkedIn accepts anything.
- [ ] `_TAG_RE` does not handle HTML comments (a `>` inside `<!-- -->` leaks text) — `_common.py`.
- [ ] Dealbreaker matching ignores negation ("no 6-day work week" still knocks a posting out) — `search_jobs.py` `knockout`.
- [ ] `cloakbrowser.launch()` has no timeout of its own; only `goto` is bounded — `fetch_posting.py`.
- [ ] Generic extraction's last-resort fallback can leak `<title>` text into the description when a page has no `<head>` — `fetch_posting.py`.
- [ ] When plain HTTP already returned an unblocked short posting, keep it even if the browser render is also thin — `fetch_posting.py` `fetch`.
- [ ] Browser-path challenge markers checked in the first 2,000 characters can reject a real JD that mentions "access denied" early; consider title-only markers for generic phrases.
- [ ] Malformed dates are invisible in `tracker.py today` (the row silently drops out of every section).
- [ ] `ats_check.py` tech vocabulary includes everyday words (Spring, Swift, Rust, Express, Rails …) that count as keywords in prose.

## Resume builder

- [ ] The `TypeError` retry around `cloak.launch(stealth_args=False)` can mask an unrelated `TypeError` — `build_resume.py`.
- [ ] `_skill_groups` is all-or-nothing: one unlabeled item drops the whole line's skills from the JSON Resume export.
- [ ] A contact line wrapped over two lines starts its second half with a separator (chicago, accent-band).
- [ ] `**Label:**` lines under a bullet merge into the bullet (lazy continuation) — exempt them.
- [ ] Temp-HTML `unlink` after PDF rendering is not guarded against `OSError`.
- [ ] Template cosmetics: creative-sidebar weight 700, executive date alignment, empty Contact heading, accent band not edge-to-edge under the 14 mm `@page` margin — `assets/templates/`.
- [ ] `docx_text` reads a nested paragraph (e.g. in a text box) twice — `_common.py`.
- [ ] No direct test for `_safe_href`.

## References

- [ ] `markets/my.md` legal accuracy: the "not to complain" wording vs EA s.69F; the §8 bonus-contribution item; the contributions table header vs the EPF Act; "EPF Act 1991" attribution unhedged.
- [ ] `networking.md`: give the dated new-contact sequence directly under the two search links, and list the alumni search link first.
- [ ] Re-run behaviour scenarios O and Q (`tests/behavioral-scenarios.md`) against the v7 commands.
