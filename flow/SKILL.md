---
name: flow
description: Diagnose where a project sits in the nine-stage flow and route to the right next skill, inventories the PRDs, ticket queue, tracker labels, git state, and gates, then names the stage and the exact command to run. Use at the start of any work session, when picking up an unfamiliar or in-flight project, when unsure what to do next, when the user asks "where are we", "what's next", or wants to realign a project with the workflow standard. Read-only: it never edits, files, or commits anything.
---

# Flow

Tell the user exactly where this project sits in the flow and what to run next. This is the
entry point to the standard in `~/.claude/skills/WORKFLOW.md`: the breadcrumbs guide you
forward from inside a stage; `/flow` guides you in from a cold start.

**Read-only.** Diagnose and recommend. Never edit, file, label, or commit anything from here.

## 1 · Inventory, look before asking

Gather the evidence cheaply, in parallel where possible. Never ask the user something the
project answers:

| Evidence | How |
|---|---|
| A PRD | `prds/*.md`, `docs/PRD*.md`, `docs/prds/` |
| Ticket drafts | `.scratch/*/issues/*.md`: **check for a supersession note**: a drafts folder whose index says "the tracker is authoritative" means the tracker, not the drafts |
| A live tracker | `gh issue list --state open --json number,title,labels` (inside a git repo with `gh`), count `ready-for-agent` vs `ready-for-human`, `needs-triage`, `needs-info` |
| Unfinished gates | `GATES.md` / `gates/*.md` with unchecked boxes, an interrupted unlazy run resumes before anything else |
| Working state | `git status`, current branch, recent log, uncommitted work means a stage is mid-flight |
| The project's own docs | `CLAUDE.md`, `README.md`, a `WORKFLOW`/`PICKUP` file, a project's own conventions beat the general rule |
| Standing context | `business-memory/`, `design-language/`, a design system, note what stage 2 and 4 should read |

## 2 · Diagnose, first stage whose input is missing

Walk the chain in order and stop at the first gap. The stage before the gap is where the
project is; the gap is where to enter.

| Found | Missing | Enter at |
|---|---|---|
| An idea, a fork, competing directions | Locked decisions | **0 `/decision-council`** (genuinely open) or **1 `/grill-me`** |
| Decisions or code, but no spec | A PRD | **2 `/write-a-prd`**: code without a PRD enters at **1** first: surface the implicit decisions, don't rationalise them |
| A PRD | A ticket queue | **3 `/to-tickets`** |
| Unblocked `ready-for-agent` tickets | Their implementation | **4 `/implement`** (`/tdd` at the agreed seams) |
| An uncommitted or unreviewed diff | Review | **5 `/code-review`** |
| A finished build | Someone using it | **6 `/qa`** |
| Raw / `needs-triage` issues | Routing | **7 `/triage`** |
| Shipped work, lessons in heads | A record | **8 `/okf`** |

Special states that beat the table:
- **Unmet gates on disk** → resume that unlazy run first. The ledger outranks everything.
- **Every ticket is `ready-for-human`** → the queue is not agent-food; say so and surface the
  smallest HITL item rather than recommending `/implement`.
- **A stale draft queue contradicting the tracker** → flag it for deletion (the tracker wins),
  then diagnose from the tracker.

## 3 · Report, short, and end with one command

Format, always under ~15 lines:

1. **One sentence**: what this project is and its momentum (from its own docs, not invention).
2. **The evidence**: 2–4 bullets of what was found, counts, not prose ("14 open issues, 0
   `ready-for-agent`; PRD at `docs/PRD-v1.0.md`; suite green at 628").
3. **The position**, marked on the flow line:
   > **Flow:** decision-council → grill-me → write-a-prd → to-tickets → **▶ implement** → code-review → qa → triage → okf
4. **▶ Next:** exactly one recommended command with a one-line reason, plus at most one
   alternative if the diagnosis is genuinely ambiguous, with the question that decides it.

If work is worth doing **DONE WELL**, recommend wrapping the stage in `/unlazy` (gates
before work); note it in one line, don't relitigate the standard.

## What this skill is not

Not a status dashboard, not a project manager, not a place to make the decision itself. One
diagnosis, one recommendation, hand off. The stage skills do the work.
