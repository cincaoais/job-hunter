# Reactive Resume Handoff (MCP)

For when a generated file isn't enough: the user wants a **designed**
resume — real templates, sidebar layouts, a photo — that they can keep
editing visually, share by link, and maintain long-term. Hand the approved
content off to Reactive Resume, an open-source resume builder with an MCP
server. The built-in builder flow keeps owning the ATS master .docx; this
handoff replaces or augments the presentation copy.

## What it is (verified from source + docs, July 2026)

- Open-source (MIT), free hosted instance at **rxresu.me**, or self-hosted
  via Docker for privacy-sensitive users.
- 15 professionally designed templates with photo support, a live visual
  editor, PDF export, public share links — plus its own job-application
  tracker.
- MCP server at `<instance>/mcp` exposing ~30 tools, resume-schema
  resources, and prompts.
  Docs: https://docs.rxresu.me/guides/using-the-mcp-server

## Connecting

The user needs a free account first (or a self-hosted instance).

- **claude.ai** — Settings → Connectors → Add custom connector →
  `https://rxresu.me/mcp` → sign in via OAuth.
- **Claude Code** —
  `claude mcp add --transport http reactive-resume https://rxresu.me/mcp`
  then authenticate via `/mcp`; API-key fallback: append
  `--header "x-api-key: <key>"` (key from the app's Settings → API Keys).
- **Self-hosted** — same commands with the instance's own domain.

Tools returning 401 = not authenticated; walk the user through the steps
above rather than retrying.

## Handoff workflow

1. **Content first, as usual.** The approved inline draft from
   `resume-builder.md`, after its claims audit, is the input — same words
   as the ATS master. The handoff changes the shell, never the facts
   (`facts-policy.md`).
2. **Read `resume://_meta/schema` once** before writing anything — patches
   must match the schema, and rich-text fields (summary, descriptions)
   take HTML strings, not markdown.
3. **Create and fill:** `create_resume` (name it
   "<Name> — <Track> <Year>"), then `apply_resume_patch` (RFC 6902)
   section by section; or `import_resume` with one full ResumeData JSON
   (watch client payload limits on big resumes). Workspace mode: export
   JSON Resume with
   `python3 ${CLAUDE_SKILL_DIR}/scripts/build_resume.py resumes/<file>.md --json`
   and pass it to `import_resume`; if the import rejects it, fall back to
   `create_resume` + `apply_resume_patch`.
4. **Template and photo:** set `metadata.template` via patch. Designed
   picks that stay credible in conservative industries: **bronzor**
   (two-column, tagged Finance/Consulting), **glalie** (sidebar,
   Finance/Legal, understated), **gengar** (business/operations),
   **chikorita** (client-facing, right sidebar). Modern/tech: azurill,
   ditgar, pikachu. Conservative single-column: lapras, scizor, meowth
   (inline-header, CN/JP/KR style). Most templates render the top-level
   `picture` when one is set — the user uploads it in the app's Basics
   panel. Apply the photo decision matrix from `resume-revamp.md` before
   suggesting one, and state the reasoning.
5. **Hand over the URL** for visual fine-tuning — colors, typography,
   spacing, and section layout are all live controls in the builder's
   right panel.
6. **Export:** PDF from the app's export menu (or the
   `download_resume_pdf` tool). Portals still get the ATS master .docx;
   this PDF is for humans — referrals, email, printing, career fairs.

## Application tracker (optional)

Reactive Resume also tracks applications (stages, contacts, notes,
timelines) with MCP tools: `create_application`, `update_application`,
`add_application_note`, `autofill_application_from_job`,
`score_application_match`, `tailor_resume_for_application`,
`draft_application_message`. If the user adopts it, the **candidate
profile stays the single source of truth** — mirror submitted applications
into the tracker, never maintain two divergent pipelines. Its AI tools run
on the user's own configured provider key; review anything they generate
against the profile before it's kept (honesty guardrail).

## Guardrails

- `delete_resume`, `delete_application`, and the bulk deletes are
  **irreversible** — only on explicit user confirmation naming the exact
  item.
- 403 = the resume is locked (user unlocks in the dashboard); 404 = stale
  ID — re-run `list_resumes`, don't guess.
- **Share links are public.** `update_resume` with `isPublic` exposes the
  resume (name, contact details, history) to anyone holding the URL — say
  so before setting it.
- Hosted means the resume lives on rxresu.me's servers. A
  privacy-sensitive user can self-host instead:
  https://docs.rxresu.me/self-hosting/docker
