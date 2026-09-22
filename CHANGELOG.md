# Changelog

All notable changes to the project-flow skill group. Versions are git tags on this
repo; the canonical checkout is `~/.claude/skills` (live-loaded by Claude Code),
pushed to `Nombru/claude-skills`.

## v1.0.0, 2026-08-20

The first bundled release: the nine-stage standard, its front door, the discipline
layer, and the design lane, proven end to end on a real iOS project, ticket through merged PR.

**Stages (tier 1):** `decision-council` · `grill-me` · `write-a-prd` · `to-tickets` ·
`implement` · `tdd` · `qa` · `triage` · `okf`

**Front door:** `flow`: read-only diagnosis, routes into the first stage whose
input is missing.

**Discipline (tier 2):** `unlazy`, vendored with the wave-dispatch amendment
(concurrent frontier dispatch; upstream serialised). Stop hook installed globally.

**Craft routing:** `imagegen`: HF Spaces (`flux1_schnell` Apache-2.0, Qwen-Image
for text-in-image) vs local SDXL.

**Docs:** `WORKFLOW.md` (the standard: tiers, wrappers, boundaries, the design
lane, mid-flow entry) · `flow-chart.svg` (the rendered map, light + dark).

Companion plugin, versioned separately: `taste-skill` 1.0.1 at
`04-Toolkit/taste-skill` (local policy: presets explicit-invoke).
