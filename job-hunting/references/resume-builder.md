# Resume & Cover Letter Builder

The build flow from candidate profile to polished, ATS-safe document. The
Application Guide holds the writing rules; this file holds the process. The
honesty guardrail applies throughout: strongest **true** form — never invent
metrics, achievements, or titles.

## Flow (resumes and cover letters alike)

1. **Read the candidate profile** and the target posting, if there is one.
   For a resume tailored to a specific posting, run the JD match first
   (`references/jd-match.md`) so the keyword targets are explicit.
2. **Ask the gap questions** — the resume/letter batch defined in SKILL.md
   Step 1.5 — as one grouped batch. Skip anything the profile answers — echo
   the assumption instead. Write answers back to the profile.
3. **Draft inline** in the chat as markdown and ask for reactions. Iterate
   here — it's cheap. Never jump straight to a file.
4. **On approval, generate the file.** Default to **.docx** — safest for ATS
   portals and JobStreet/LinkedIn apply flows; offer **PDF** when the reader
   is human (email to a person, referral, print). Ask once, record the
   preference in the profile.
5. **Run the pre-delivery check** below before handing the file over.

## Resume rules (enforced, from the Application Guide)

- Reverse-chronological by default (Template A); skills-forward (Template B)
  only for career changers or long gaps.
- Every experience bullet is result-first: *Accomplished [X] measured by [Y]
  by doing [Z]* — quantified, truthful, estimates labeled.
- Mirror the posting's exact keywords and phrasing; ATS filters on them.
- Parser-safe: no tables, columns, text boxes, images, or header/footer
  content; standard section headings; standard fonts.
- Market norms decide length, photo, and personal details (Application
  Guide, "Market norms vary"). In Malaysia/SEA: 1–2 pages, photo optional,
  expected salary sometimes requested — ask, don't assume.

## Pre-delivery check

- Every must-have keyword from the posting that the user genuinely has
  appears verbatim somewhere.
- Bullets lead with results; no invented numbers; estimates labeled.
- No parser-breaking formatting; headings are standard words.
- Length, photo, and personal details match the market's norms.
- Contact details present and current.

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

Same flow: read → ask → draft inline → approve → deliver. Always tailored to
one specific posting — if none is named, ask which job this letter is for.

- Beats, length, and rules come from the Application Guide's "Cover letter"
  section — that file is the single source for them.
- The why-you beat maps 2–3 of the resume's quantified wins onto the
  posting's stated needs.
- Specific enough that it couldn't be sent to any other company — if it
  could, rewrite it.
- Delivery: many SEA portals take pasted text rather than an upload — ask
  whether they need a file (.docx/PDF) or clean text to paste.
