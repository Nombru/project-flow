---
name: to-tickets
description: Break a PRD, spec, plan, or the current conversation into vertical-slice tickets, each a complete end-to-end path through every layer, declaring its blocking edges, tagged AFK (agent-grabbable) or HITL (needs a human), and given a capability tier so an automated runner knows which executor should attempt it. Output as local Markdown files by default, or GitHub/Linear issues. Use after /write-a-prd, or whenever the user wants to break work into tickets/issues, slice a feature, or plan implementation.
---

# To Tickets

Break a plan, spec, PRD, or the current conversation into a set of **tickets**: tracer-bullet *vertical slices*, each declaring the tickets that **block** it, and each tagged so an agent or a human knows who picks it up.

> Derived from [Matt Pocock's `to-tickets`](https://github.com/mattpocock/skills) (MIT). The slicing rules and templates are his; the explicit AFK/HITL tagging comes from the workshop, and the adaptive local-first output is ours. Runs after `/write-a-prd`; feeds `/implement`.

## Process

### 1. Gather context
Work from whatever's already in the conversation. If the user passes a reference, a PRD path, an issue number or URL, fetch it and read the full body and comments.

### 2. Explore the codebase (optional)
If you haven't already, explore to understand the current state. Ticket titles and descriptions should use the project's domain vocabulary (check `UBIQUITOUS_LANGUAGE.md` if present) and respect existing architecture decisions. Look for **prefactoring** that makes the change easier: *"make the change easy, then make the easy change."*

### 3. Draft vertical slices
Break the work into **tracer-bullet** tickets:

<vertical-slice-rules>
- Each slice cuts a narrow but COMPLETE path through every layer (schema, API, UI, tests), vertical, NOT a horizontal slice of one layer.
- A completed slice is demoable or verifiable on its own.
- Each slice is sized to fit in a single fresh context window.
- Any prefactoring is done first.
</vertical-slice-rules>

Give each ticket its **blocking edges**: the other tickets that must finish before it can start. A ticket with no blockers can start immediately.

**Wide refactors are the exception to vertical slicing.** A wide refactor is one mechanical change (rename a column, retype a shared symbol) whose blast radius fans across the codebase, so a single edit breaks thousands of call sites and no vertical slice can land green. Sequence it as **expand → migrate → contract**: first *expand*, add the new form beside the old so nothing breaks; then *migrate* call sites in batches sized by blast radius (per package, per directory), each batch its own ticket blocked by the expand, keeping CI green because the old form still exists; finally *contract*, delete the old form once no caller remains, in a ticket blocked by every migrate batch. If even the batches can't stay green alone, keep the sequence but let them share an integration branch that all block a final integrate-and-verify ticket, green is promised only there.

### 4. Classify each ticket: AFK or HITL
- **AFK**: *away from keyboard*, label `ready-for-agent`. Self-contained enough that an agent can implement and merge it unattended. Tickets are agent-grabbable by construction, so this is the default.
- **HITL**: *human in the loop*, label `ready-for-human`. Needs a decision, judgment call, credentials, or a design choice only the user can make.

### 5. Tag each ticket with a capability tier

Give each ticket a **capability tier**: `mechanical`, `standard`, or `hard`. An automated runner reads the tier to decide *which executor* should attempt the work; a human picking the ticket up can ignore it.

**The tier answers one question: if this goes wrong, will the project's automated gate say so?** It is keyed to **failure-detectability, not difficulty**: which inverts the intuition in useful ways:

- A 300-line mechanical rename with full test coverage is `mechanical`: large, but trivially verified.
- A one-line copy change is `hard`: tiny, but its correctness is a judgment no test encodes.

| Tier | Meaning |
|---|---|
| `mechanical` | A wrong answer fails the gate. Verifiable without judgment. |
| `standard` | The gate catches most of it, but some judgment is involved. |
| `hard` | Correctness depends on judgment the gate cannot express. |

**Never name a model in a ticket.** Tiers are capability levels; the tier-to-executor mapping belongs in one configurable place in the runner, so a new model release is a one-line remap rather than a find-and-replace across the whole backlog. A ticket reading `model: <some-model-id>` is wrong even if it happens to work today.

If the project maintains a list of areas excluded from unattended work, that list **overrides** the tier, check it before tagging.

**A tier is optional.** If the project has no automated runner, or you genuinely can't judge, leave it off. Absence means "classify later", not an error.

### 6. Quiz the user
Present the breakdown as a numbered list. For each ticket show **Title**, **Blocked by**, **What it delivers** (the end-to-end behavior), **AFK/HITL**, and **Tier**. Then ask, one point at a time:
- Does the granularity feel right (too coarse / too fine)?
- Are the blocking edges correct, does each ticket only depend on tickets that genuinely gate it?
- Should any be merged or split? Is any AFK ticket really HITL?
- Are the tiers right? Remember the test is whether a wrong answer would be *caught*, not how hard the work looks.

Iterate until the user approves the breakdown.

### 7. Publish (adaptive)
Publish in **dependency order** (blockers first), working the *frontier*, any ticket whose blockers are all done. Confirm the destination first, and **get an explicit yes before creating anything on a remote tracker.**

- **Local (default)** → one file per ticket under `.scratch/<feature-slug>/issues/<NN>-<slug>.md`, numbered from `01` in dependency order. Use the local template below, one ticket per file, never a combined file. (`.scratch/` is easy to gitignore.)
- **GitHub / Linear (only if inside a git repo with `gh` / a tracker MCP available)** → offer to publish one issue per ticket in dependency order, using the platform's native blocking / sub-issue relationship where it has one (otherwise a "Blocked by" line), applying the `ready-for-agent` or `ready-for-human` label **and the tier label**. Show the user the full set and confirm before filing. If a tier label doesn't exist on the tracker yet, say so rather than silently dropping the tier, an automated runner reads it.

Do NOT close or modify any parent issue.

<local-ticket-template>
# <NN>, <Ticket title>

**What to build:** the end-to-end behavior this ticket makes work, from the user's perspective, not a layer-by-layer implementation list.

**Blocked by:** the numbers/titles of the tickets that gate this one, or "None, can start immediately".

**Who picks it up:** AFK (`ready-for-agent`) or HITL (`ready-for-human`)

**Tier:** `mechanical` | `standard` | `hard`: omit the line entirely if untiered.

- [ ] Acceptance criterion 1
- [ ] Acceptance criterion 2
</local-ticket-template>

<issue-template>
## Parent
A reference to the parent issue on the tracker (if the source was an existing issue; otherwise omit).

## What to build
The end-to-end behavior this ticket makes work, from the user's perspective, not layer-by-layer implementation.

## Acceptance criteria
- [ ] Criterion 1
- [ ] Criterion 2

## Blocked by
- A reference to each blocking ticket, or "None, can start immediately".

## Tier
`mechanical` | `standard` | `hard`: omit this section entirely if untiered.
</issue-template>

**Avoid specific file paths or code snippets**: they go stale fast. Exception: if a decision is captured more precisely by a small snippet (a state machine, reducer, schema, or type shape) than by prose, inline just the decision-rich part and note that it came from a prototype.

## ▶ End with the next step

Always close your final message with this breadcrumb so I know where I am in the flow:

> **Flow:** decision-council → grill-me → write-a-prd → **to-tickets** → implement → code-review → qa → triage → okf
> **▶ Next:** `/implement <ticket>` on an AFK (`ready-for-agent`) ticket, or run the AFK loop over the queue. HITL tickets are yours. (Bugs found later in `/qa` come back here.)
