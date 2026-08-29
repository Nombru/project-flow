---
name: triage
description: Route raw issues through a state machine — needs-triage to needs-info, ready-for-agent, ready-for-human, or wontfix — giving each exactly one category, a capability tier, and its blocking edges, so an automated runner and a human both know what to pick up. Use after /qa files issues, when an issue queue needs sorting, or when the user asks to triage, sort, or route incoming bugs. Works on local Markdown issues or a GitHub/Linear tracker.
---

# Triage

Take a queue of raw, unclassified issues and leave every one of them in a state that tells a runner or a human exactly what to do with it. Triage decides *who picks it up and when* — it never decides *how to fix it*, and never writes code.

> Closes the loop `/qa` opens. `/qa` files what the user experienced; triage turns that into something `/implement` or a person can grab. Same adaptive output as the rest of the flow: local Markdown by default, a remote tracker only on confirmation.

## Process

Work the queue **one issue at a time**, oldest first. For each:

### 1. Read it as filed, then verify the claim

Explore the codebase before classifying. An issue that reproduces, an issue that was already fixed, and an issue that describes intended behavior all look identical on paper and route completely differently. If a two-minute check settles it, do the check — do not spend the user's turn on a question the repo answers.

### 2. Route it to exactly one state

| State | When | What happens next |
|---|---|---|
| `needs-info` | You cannot reproduce it, or the expected behavior is genuinely ambiguous | Ask the reporter one specific question. Never a checklist |
| `ready-for-agent` | Behavior is unambiguous, the fix is bounded, and a wrong answer would be caught by the gate | Goes to the AFK loop |
| `ready-for-human` | A real decision, a judgment call, a public-facing change, or anything touching money, auth, or data loss | Surfaced for you |
| `wontfix` | Working as intended, out of scope, or superseded | Closed with the reason stated in one line |

**Bias toward `needs-info` over guessing.** A misrouted issue costs an agent a whole context window and files a wrong fix; a question costs one turn.

### 3. Give it exactly one category

`bug` or `enhancement`. Not both, not neither. "It should have done X" is a bug only if something claimed it would.

### 4. Give it a capability tier

`tier:mechanical` · `tier:standard` · `tier:hard`, keyed to **failure-detectability, not difficulty** — would a wrong answer be caught by the gate, or would it merge green and wrong? A broad covered refactor is `mechanical`. A one-line copy change nothing tests is `hard`. Tiers name a tier, never a model; the tier→executor mapping lives in one place in the runner.

*(Distinct from permission tiers like GREEN/YELLOW/RED, which describe how dangerous an action is. Different axis. Never write bare "tier" where both could be meant.)*

### 5. Declare blocking edges

What must be finished first? "None — can start immediately" is a real and common answer, and it is what lets the runner dispatch a whole wave at once. Guessing at dependencies that do not exist serialises the queue for no reason.

### 6. Merge duplicates

Two issues describing one behavior become one issue with both sets of repro steps. Say which you merged and why — a silently closed duplicate looks like a dropped report to whoever filed it.

## Output

Update the issue in place: local `.md` files by default. On a remote tracker, **show the label changes and ask before applying them** — relabelling someone's issue is a visible action.

Finish with a queue summary: how many in each state, and which `ready-for-agent` issues have no blockers (that is the first wave).

## Guardrails

- **Never fix anything.** Noticing the fix is not permission to apply it — that is `/implement`'s job and it needs the ticket to exist first.
- **Never close as `wontfix` without a stated reason**, and never on a remote tracker without asking.
- **Do not re-derive the tier** on an issue that already carries one from `/to-tickets`. It was set with more context than you have.

## ▶ End with the next step

Close your final message with:

> **Flow:** decision-council → grill-me → write-a-prd → to-tickets → implement → code-review → qa → **triage** → okf
> **▶ Next:** `/implement` the first unblocked `ready-for-agent` issue, or hand the `ready-for-human` ones back.
