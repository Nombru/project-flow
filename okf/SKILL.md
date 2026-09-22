---
name: okf
description: >-
  Create and maintain Open Knowledge Format (OKF) bundles from local Markdown folders.
  Adds type/title/description/timestamp frontmatter (descriptions written by a LOCAL LLM,
  nothing leaves the machine), (re)generates index.md navigation + log.md, validates against
  Google's OKF reference rules, and lints for broken links / stale / orphan / non-conformant docs.
  Use when the user wants to "OKF-ify", enrich, validate, lint, or maintain a folder of notes/docs,
  or mentions the Open Knowledge Format / an OKF bundle. Local and private by default (LM Studio).
---

# OKF bundle maintainer (local, private)

Bring a folder of Markdown to OKF v0.1 and keep it maintained. This is the local, Claude-Code-native
equivalent of Google's OKF "enrichment agent", but it reads the user's real folders, uses their
**local** LLM (never a cloud API unless the user explicitly configures one), and leaves changes
uncommitted for review.

Scripts live next to this file. Run them from anywhere with uv (provides pyyaml in an isolated env):
`uv run --with pyyaml python3 ~/.claude/skills/okf/scripts/<script> ...`
The LLM endpoint is read from `$OPENAI_BASE_URL` (default `http://localhost:1234/v1`) and
`$OPENAI_MODEL` (default `qwen3-coder-next`).

## OKF v0.1 rules this enforces
- Every non-reserved `.md` (a "concept doc") needs YAML frontmatter with a non-empty `type`, `title`,
  `description`, and `timestamp` (the reference validator requires all four, stricter than the spec's
  `type`-only minimum). Always quote `title`/`description` (a `:` in an unquoted value breaks YAML).
- `index.md` = reserved per-folder listing, **no frontmatter** (except the bundle-root `index.md`, which
  may carry a single `okf_version: "0.1"` block). Body: `# Heading` then `* [Title](url) - description`.
- `log.md` = reserved. `# Directory Update Log` + `## YYYY-MM-DD` headings (ISO date, newest first).
- `CLAUDE.md`/`AGENTS.md` are the "schema" layer, left untouched, not treated as concept docs.
- Generated dirs (`graphify-out/`, `dist/`, `build/`, `node_modules/`, `.venv/`) are skipped.

## Operations

**1. Validate (read-only), run this first**
`… scripts/okf_validate.py <folder>`
Google's vendored reference checks, offline. Reports PASS/FAIL per concept doc + reserved-file shape.

**2. Lint (read-only), health check an existing bundle**
`… scripts/okf_lint.py <folder> [--stale-days N]`
Reports: non-conformant frontmatter, broken internal links (OKF treats these as "not yet written"),
orphan docs (not linked from any `index.md`), and stale docs (timestamp older than N days, default 180).

**3. Enrich (mutates), add/refresh frontmatter**
`… scripts/okf_deploy.py frontmatter <folder>`
Adds the four keys to concept docs that lack them (idempotent; preserves existing frontmatter keys).
Descriptions come from the local LLM; falls back to the doc's first sentence if the endpoint is
unreachable. Run `… scripts/okf_deploy.py inventory <folder>` first for a dry-run count.

**4. Index (mutates), (re)generate navigation**
`… scripts/okf_deploy.py indexes <folder>`
Creates an `index.md` in each folder that lacks one (bundle root gets `okf_version`). Never overwrites
an existing `index.md`.

## Recommended workflows
- **OKF-ify a folder:** validate (see gaps) → enrich → indexes → validate (confirm PASS).
- **Maintain a bundle:** lint → act on findings (regenerate indexes for orphans, enrich for missing
  frontmatter, write real links for broken refs, refresh stale docs) → validate.
- **Log a change:** append a `## YYYY-MM-DD` entry (newest first) to the folder's `log.md`.

## Safety (do this every time)
- Before any **mutating** run on files that are not all under git, back them up first:
  `find <folder> -name '*.md' -print0 | tar --null -czf /tmp/okf-backup-<date>.tgz --files-from=-`
- Leave changes **uncommitted**; show the user `git diff` (per repo) and let them commit.
- Never point `$OPENAI_BASE_URL` at a cloud endpoint without the user's explicit go-ahead, that would
  send their content off the machine. Local-first is the default and the point.

---

## ▶ End with the next step

`okf` is stage 8, the last one. Close your final message with:

> **Flow:** decision-council → grill-me → write-a-prd → to-tickets → implement → code-review → qa → triage → **okf**
> **▶ Next:** nothing queued. Start the next feature at `/grill-me`, or `/decision-council` if the direction is genuinely open.

