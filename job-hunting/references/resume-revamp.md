# Resume Revamp & HR-Eye Score

For when tailoring edits aren't enough: the resume is technically fine but
visually forgettable, the user says it looks plain / unattractive / "not
something I'd shortlist if I were HR", asks to **revamp**, **redesign**, or
**score** it, or the funnel diagnosis (SKILL.md) points at the 6-second
skim. Score first, then rebuild content **and** design from the ground up —
never patch sentence by sentence. The honesty guardrail applies throughout.

## Step 1 — HR-eye scorecard (0–100)

Read the current resume as its three real readers in sequence: ATS parser →
6-second human skimmer → hiring manager. Five dimensions, 20 points each.
**A heading's presence earns nothing — only content quality counts**, and
the rubric is level-aware (fresher ≠ experienced).

| Dimension | What earns points |
|---|---|
| **First impression** | Differentiators visible in the top third; clear visual hierarchy pulling the eye to them; full page used — no dead bottom third; no generic filler ("dynamic team player") |
| **Impact evidence** | Result-first bullets with truthful numbers or concrete scale; strong verbs; zero duty-verb bullets ("responsible for", "assisted with") |
| **Relevance** | Positioned for the target role and market; posting keywords mirrored (run the JD match if a posting exists); level-appropriate content — fresher: education + certs prominent; experienced: no high-school detail |
| **Credibility & hygiene** | Complete contact block, real links (a `[add URL]` placeholder is an automatic miss), consistent dates, no typos, every claim traceable |
| **Design & ATS** | Typography rules below; parser-safe master file; length, photo, and personal details per market norms |

Output: the score, the table with per-dimension marks, and **max 8
suggestions ranked by impact (high / medium / low), each with a concrete
example rewrite** — never "strengthen your bullets" without showing one
strengthened. Deliver misses as actionable one-liners, not lectures.

**Anti-pattern warning.** Many free "resume score" tools award points for
section *presence* (Objective, Hobbies, Interests, Declaration). Do not:
those sections are filler or actively dated in most markets (MY/SG
included), and presence-scoring is trivially gameable. If the user arrives
with such a score, explain the difference once and move on.

## Step 2 — Revamp, don't patch

If the score is below ~70, or the user asked for a revamp: rebuild from the
profile and the scorecard. Everything is allowed to change — structure,
section order, positioning, wording, design tier — except the facts.
Follow the builder flow (`resume-builder.md`): inline draft → reviewer
pass → files → ATS text-layer check.

Content moves that need no invented numbers:

- Summary cut to 2–3 lines; the differentiators (certs, licenses, languages)
  named in line one, not buried mid-paragraph.
- Mine the **countable truths** already in the profile: number of languages,
  certifications, years/duration, team lead scope, locations covered. "4
  languages" and "2 years across Klang Valley events" are real numbers.
- Fresher layout: education and certifications in the top half; high school
  one line max (or cut once a degree exists).
- Fill a thin page with real substance — expanded leadership/project detail,
  relevant coursework — never font inflation or padding sections.
- Soft skills are **evidenced, not listed**: a "Soft Skills: communication,
  teamwork" line weakens the page; multilingual client work proves it.

## Step 3 — Design: fresh from the gallery, never from the old file

**Master (ATS)** — .docx, single column, parser-safe per
`resume-builder.md`. Always generated; it's what portals and ATS get.

**Presentation copy** — PDF for human readers (referrals, direct email,
career fairs, printed copies). **Never inherit the incoming resume's
layout** — a revamp that keeps the old skeleton reproduces exactly what
scored low. Instead, recommend the two gallery templates that best fit the
target industry, describe each in one line, and let the user pick.

**Archetype check (mandatory before recommending).** Classify the incoming
resume in one line — column count, header style, accent color and
placement (e.g. "centered name, navy heading rules, single column ≈
Chicago"). Both recommended templates must be **structurally different**
from that archetype: different column structure or accent placement, not
just new fonts and better words. A rebuild that lands back on the old
archetype reads as "nothing changed", however much the content improved —
this is the single most common way a revamp disappoints. When the industry
default *is* the old archetype (plain single-column finance resume →
Chicago), say so explicitly and put the nearest structurally distinct
option (usually Corporate sidebar) first — the user picks the trade-off
between safest-conventional and visibly-redesigned.

### Template gallery

| Template | Layout | Signature look | Fits |
|---|---|---|---|
| **Chicago** | Single column | Black on white; 1pt rules under headings; one muted accent (navy/deep gray) used only structurally; serif or neutral sans; no icons or skill bars | Banking, finance, law, consulting, government — the conservative default |
| **Executive** | Single column, generous margins | Name at ~1.85× heading size; thin hairline rules; near-monochrome; whitespace does the talking | Senior/managerial roles in any conservative industry |
| **Corporate sidebar** | Two-column, light-tint sidebar (25–35% width) | Sidebar holds skills, certs, languages; main column keeps summary + experience + education | Standard corporate, client-facing, HR/ops/sales |
| **Accent band** | Single column + full-width solid accent header band | Name/title reversed out of the band; skill tags as subtle pills; clean sans | Tech, product, data — modern look without a sidebar |
| **Creative sidebar** | Two-column, solid-accent sidebar | Saturated sidebar; skill tags; optional small headshot where the photo matrix allows | Design, marketing, media, startup-facing roles |

All five share the typography numbers below — they differ in structure and
accent placement, so the same content drops into any of them.

Typography numbers that work (any tier):

- Body 10pt — floor is 9pt; below that **cut content, never shrink text**.
  Headings ~14pt; name ≈1.5× heading size (up to 1.85× for an executive
  look); secondary text (dates, locations) 0.875× body; line-height 1.4–1.5.
- Bold means semibold (600), not heavy; hierarchy comes from size and
  weight, not gray-on-gray.
- Dates right-aligned on the same row as the title; one accent color used
  structurally (rules, sidebar tint) and never for body text.
- Spacing on one rhythm: pick a base gap; item gap = 1×, section gap ≈ 2×.
  A consistent rhythm is most of what reads as "designed".

### Presentation-copy build mechanics

The ATS master stays python-docx. But sidebar, accent-band, and photo
layouts do **not** survive docx generation reliably — build the
presentation copy as **HTML/CSS rendered to PDF** (one file, print CSS,
exact page size): multi-column grids, tint blocks, and image placement
hold precisely there. Content stays word-identical to the master; only
the shell differs.

**Or hand off to a real builder.** When the Reactive Resume MCP is
connected — or the user is willing to set it up — offer the handoff in
`references/rxresume-mcp.md`: 15 professionally designed templates with
photo support and a live visual editor beat any generated file when the
user wants to keep tweaking the design themselves.

### Photo decision matrix

Never a photo in the ATS master, regardless of market. For the presentation
copy, decide **market norm × industry norm** and state the decision and its
reason to the user:

| Market norm | Client-facing / local firm (sales, hospitality, reception, insurance, agencies; client-facing roles at local banks — bancassurance, wealth, relationship) | Back-office & analyst roles / tech / engineering / Western MNCs |
|---|---|---|
| **Photo expected** — DE/AT/CH, JP (rirekisho), KR, CN, VN, ID, PH local firms, Middle East | Photo | Photo still conventional locally; skip for Western MNCs |
| **Mixed** — MY, SG, FR | MY local firms and client-facing financial services expect or welcome it; SG defaults to **no** (MOM fair-hiring guidance) unless a local SME clearly welcomes it | No photo — MNC finance, analyst tracks, and Western tech screen it out for bias/compliance |
| **No photo** — US, CA, UK, AU, NZ | No photo (discrimination-liability rejection risk) | No photo |

The split runs on the **role**, not just the employer: a wealth or
relationship role at a Malaysian bank sits in the client-facing column
(photo appropriate); an analyst or back-office role at the same bank sits
in the right column (skip).

Tie-breaker: when unsure, **omit** — a missing photo almost never rejects a
resume; a present one can. **But the user's stated preference wins**: the
matrix is the default, not a veto. If they want a photo where it says skip
(or vice versa), state the trade-off in one line and build what they chose.
If a photo goes in: recent professional headshot,
plain background, business attire, small, top corner of page one.
LinkedIn/JobStreet **profile** photos are a separate matter and always
recommended. `sea-market-notes.md` holds the per-country SEA detail.

## Step 4 — Re-score before delivery

Run the same scorecard on the revamped draft and report **before → after**
per dimension. Ship only when the presentation copy fills one clean page
(fresher) and the master passes the ATS text-layer check. If a dimension
didn't move, say why (usually: a real number only the user can supply —
name exactly which bullet is waiting for it).
