# Resume & Cover Letter Builder

The build flow from candidate profile to polished, ATS-safe document. The
Application Guide holds the writing rules; this file holds the process.
Every claim is the strongest **true** form of a profile fact —
`facts-policy.md` holds the mechanism.

## Flow (resumes and cover letters alike)

1. **Read the candidate profile** and the target posting, if there is one.
   For a resume tailored to a specific posting, run the JD match first
   (`references/jd-match.md`) so the keyword targets are explicit.
2. **Ask the gap questions** as one grouped batch (SKILL.md memory rules);
   a missing number is asked with options, never estimated
   (`facts-policy.md` §2). Skip anything the profile answers — echo
   the assumption instead. Write answers back to the profile.
3. **Draft inline** in the chat as markdown and ask for reactions. Iterate
   here — it's cheap. Never jump straight to a generated .docx/PDF. Once
   approved, workspace mode saves the draft as
   `resumes/<company>-<role>-vN.md` (a letter under `letters/`; Versioning
   below) — the file every gate and the build read.
4. **Claims audit** (below) on the approved draft — a fresh critical read
   before any file exists.
   - 4.5 **Anti-slop gate** (below).
   - 4.6 **6-second lint** (below) — resumes only.
5. **Generate the file.** Default to **.docx** — safest for ATS portals and
   JobStreet/LinkedIn apply flows; offer **PDF** when the reader is human
   (email to a person, referral, print). Ask once, record the preference in
   the profile.
   - Workspace mode:
     `python3 ${CLAUDE_SKILL_DIR}/scripts/build_resume.py resumes/<file>.md --docx [--pdf --template <name>]`
     — templates are the gallery in `resume-revamp.md` Step 3.
   - Chat mode: the Anthropic docx / pdf skills, from the same approved
     markdown.
6. **ATS text-layer check** (below) on the generated file:
   `python3 ${CLAUDE_SKILL_DIR}/scripts/ats_check.py <file> --posting postings/<slug>.md`.
7. **Run the pre-delivery check** below before handing the file over.
8. **Record the version** sent: workspace mode
   `python3 ${CLAUDE_SKILL_DIR}/scripts/tracker.py set --company "<X>" --role "<Y>" --resume resumes/<company>-<role>-vN.md`;
   chat mode, the Resume cell of the profile §9 Pipeline row. Then the
   closing step for the storage mode (SKILL.md).

Gates run in this order and none that applies is skipped: claims audit →
anti-slop gate → 6-second lint → file → ATS text-layer check. Chat mode:
say which checks ran by reading and which script checks could not run.

## Claims audit (step 4)

After approval, before generating anything, run the claims audit in
`facts-policy.md` §4 on the final draft and report it in that section's
format. An open ask stops the flow here until the user answers.

In the same pass, reread it the way a skeptical second reviewer would —
against the posting, not from memory of writing it:

- Posting keywords the profile genuinely supports but the draft doesn't say
  in the posting's words — free wins still on the table (the literal-term
  mirror list, `jd-match.md` §3).
- Phrasing that could be sent to any other company — too generic, rewrite.
- Bullets that drifted off result-first form.
- Cover letter ↔ resume consistency (same numbers, same titles), if both
  exist.

Fix what this finds and tell the user in one line what changed (or that
nothing did). Only re-open the inline-draft loop if something material moved.

## Anti-slop gate (step 4.5)

- **Cover letters** need at least one **user-supplied story** — a specific
  event the user tells, or picks from options drawn from profile §5 and the
  STAR stories in `answers.md` (chat mode: the profile §9 Answers section) —
  and at least one **company-specific fact** from the saved posting or the
  dossier (`company-dossier.md`). Check both before drafting a letter and
  confirm them here: no story or no fact → no letter; ask, or build the
  dossier.
- **Every draft** gets the banned-phrase scan: workspace mode
  `python3 ${CLAUDE_SKILL_DIR}/scripts/ats_check.py <draft.md> --slop`; the
  list lives in `assets/slop-phrases.txt`. Replace each hit with a
  specific — a number, a named system, a result — never a synonym. Chat
  mode: read the draft against the same list and say the scan was a read.

## 6-second lint (step 4.6)

A recruiter's first skim is 6–10 seconds on name, current title and
employer, dates, previous title, education and the first bullet of the
latest role (Huntr/Careerflow). Before any file exists, the draft passes:

- The title line under the name matches the target role, truthfully.
- The first bullet of the latest role has a number.
- Single column — sidebars belong only to the presentation copy.
- Every role has dates.
- Progression is visible (title or scope grows across roles).
- At most 2 pages (market norms: `markets/<cc>.md` §4).

Workspace mode:
`python3 ${CLAUDE_SKILL_DIR}/scripts/ats_check.py <draft.md> --lint --target-title "<target role>"`
checks contact email and phone as literal text, a date near the top, a
number in the first experience bullet, length, and the title words in the
first lines when `--target-title` is given. Single column, dates on every
role and visible progression are checked by reading. Chat mode: all six by
reading, and say so.

## ATS text-layer check (step 6)

An ATS reads the file's extracted text, not the rendered page — and
generation can silently produce files whose text layer differs from the
draft. After generating, extract the file's raw text and verify what a
parser actually sees. Workspace mode:
`python3 ${CLAUDE_SKILL_DIR}/scripts/ats_check.py <file.docx|file.pdf> --posting postings/<slug>.md`
(no saved posting: `--keywords "a,b"` with the `jd-match.md` §3 mirror
list). Chat mode: extract it in the analysis sandbox (e.g. python-docx /
pypdf) where one exists.

- Contact details present as literal text; no garbled or missing characters.
- Reading order is sane — sections in sequence, no interleaved lines.
- Every must-have keyword from the posting that the user genuinely has
  appears in the extraction. Report coverage plainly ("9/10 must-have
  keywords present; 'gRPC' absent — that's a real gap, not a wording fix").

A supported keyword missing from the extraction → fix and regenerate. A real
gap → stays visible and honest, never keyword-stuffed. If extraction isn't
possible in this session, fall back to the pre-delivery checklist and say so
rather than claiming the check ran. The declared fallback line — what
`ats_check.py` prints before exiting 2 when no PDF text extractor is
available:

> Text layer not checked: no PDF text extractor here (pip install pypdf, or install pdftotext). Check the .docx master instead, or fall back to the pre-delivery checklist and tell the user the check did not run.

## Resume rules (enforced, from the Application Guide)

- Reverse-chronological by default (Template A); skills-forward (Template B)
  only for career changers or long gaps.
- Every experience bullet is result-first: *Accomplished [X] measured by [Y]
  by doing [Z]* — quantified from the profile; a user-supplied estimate
  reads "~N" (`facts-policy.md` §3).
- Mirror the posting's exact keywords and phrasing; ATS filters on them.
- Parser-safe: no tables, columns, text boxes, images, or header/footer
  content; standard section headings; standard fonts.
- Market norms decide length, photo, and personal details:
  `markets/<cc>.md` §4 — ask, don't assume.

## Pre-delivery check

- Every must-have keyword from the posting that the user genuinely has
  appears verbatim somewhere.
- Bullets lead with results; no invented numbers; estimates read "~N".
- The claims-audit line was reported, the slop scan is clean and the
  6-second lint passed — or each was declared as a read in chat mode.
- No parser-breaking formatting; headings are standard words.
- Length, photo, and personal details match the market's norms.
- Contact details present and current.
- The ATS text-layer check ran on the generated file — or its fallback was
  declared to the user.

## Versioning

- Every tailored resume is its own file: `resumes/<company>-<role>-vN.md`
  (v1 first; a change after a version went out is v2, never an overwrite).
  Cover letters sit under `letters/` with the same naming.
- The pipeline row names the version actually sent (step 8,
  `pipeline.md` §1), so a screen can be prepped from the exact text the
  recruiter holds.

## Template A — Reverse-chronological (default)

```markdown
# [Full Name]
[Target-role title] · [City, Country] · [phone] · [email] · [LinkedIn] · [GitHub/portfolio]

## Summary
[2–3 lines, tailored: identity + strongest quantified proof + what you're
aiming at. Cut the section if it adds no signal.]

## Experience
### [Job title] — [Company], [City] · [MM/YYYY – MM/YYYY]
- [Result-first bullet with a number]
- [Result-first bullet with a number]
- [Scope / stack context, one line]

### [Earlier title] — [Company], [City] · [MM/YYYY – MM/YYYY]
- [Result-first bullet]
- [Result-first bullet]

## Skills
**Languages:** … · **Frameworks:** … · **Cloud / tools:** …

## Education & Certifications
[Degree — Institution — Year]
[Certification — Issuer — Year]
```

## Template B — Skills-forward hybrid (career changers, long gaps)

```markdown
# [Full Name]
[Target-role title] · [City, Country] · [phone] · [email] · [LinkedIn]

## Summary
[2–3 lines: the bridge — what you did before, what carries over, what you're
targeting now.]

## Core skills & proof
- **[Skill cluster from the posting]:** [one-line quantified proof it's real]
- **[Skill cluster]:** [proof]
- **[Skill cluster]:** [proof]

## Experience
[Reverse-chronological entries as in Template A, with briefer bullets — the
proof already leads above.]

## Education & Certifications
[As in Template A. Recent retraining/certs go first for career changers.]
```

## Cover letters

Same flow: read → ask → draft inline → approve → claims audit and
anti-slop gate → deliver (the 6-second lint is resume-only). Always
tailored to one specific posting — if none is named, ask which job this
letter is for.

- Beats, length, and rules come from the Application Guide's "Cover letter"
  section — that file is the single source for them.
- The why-you beat maps 2–3 of the resume's quantified wins onto the
  posting's stated needs.
- Specific enough that it couldn't be sent to any other company — if it
  could, rewrite it.
- Delivery: many SEA portals take pasted text rather than an upload — ask
  whether they need a file (.docx/PDF) or clean text to paste.
