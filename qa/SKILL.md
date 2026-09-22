---
name: qa
description: Interactive QA session, the user reports bugs conversationally, the agent clarifies lightly, explores the codebase in the background for domain language, and files durable, user-focused issues (local Markdown by default, or GitHub with confirmation). Loops until done, feeding issues back into /to-tickets. Use to report bugs, do QA, file issues conversationally, or when the user mentions a "QA session".
---

# QA Session

Run an interactive QA session. The user describes problems they hit; you clarify lightly, explore the codebase for context in the background, and file durable, user-focused issues that use the project's domain language. Filed issues then loop back into `/to-tickets`.

> Derived from [Matt Pocock's `qa`](https://github.com/mattpocock/skills) (MIT). The loop and templates are his; the one deliberate change is ours, write local issues freely, but **confirm before filing to a remote tracker** (creating public issues is an external action).

## For each issue the user raises

### 1. Listen and lightly clarify
Let the user describe the problem in their own words. Ask **at most 2–3 short clarifying questions**: expected vs. actual, steps to reproduce (if not obvious), consistent or intermittent. Do NOT over-interview, if it's clear enough to file, move on.

### 2. Explore in the background
Kick off an `Explore` subagent to understand the relevant area. The goal is NOT to find a fix, it's to learn the domain language (check `UBIQUITOUS_LANGUAGE.md`), understand what the feature is supposed to do, and find the user-facing behavior boundary. This context sharpens the issue; the issue itself must not reference files, line numbers, or internals.

### 3. Assess scope: single issue or breakdown?
Break down when the fix spans multiple independent areas, when there are separable concerns different people could grab in parallel, or when there are multiple distinct failure modes. Keep as a single issue when it's one wrong behavior in one place, or symptoms sharing a single root cause. Prefer many thin issues over few thick ones.

### 4. File the issue(s), adaptive
Decide the destination and **confirm before writing to a remote tracker:**

- **Local (default)** → write one file per issue under `.scratch/qa/<NN>-<slug>.md` using the templates below. Fast, no confirmation needed.
- **GitHub (only if inside a git repo with `gh`)** → draft the issue(s), show them to the user, and on an explicit yes create them with `gh issue create`, in dependency order (blockers first) so "Blocked by" can reference real numbers. Apply `ready-for-agent` / `ready-for-human` as appropriate. Print the URLs.

#### Single-issue template
```
## What happened
[The actual behavior the user experienced, in plain language]

## What I expected
[The expected behavior]

## Steps to reproduce
1. [Concrete, numbered steps a developer can follow]
2. [Domain terms from the codebase, not internal module names]
3. [Relevant inputs, flags, or configuration]

## Additional context
[Observations from the user or codebase exploration that frame the issue, domain language, don't cite files]
```

#### Breakdown template (one per sub-issue)
```
## Parent
#<parent-issue-number> or "Reported during QA session"

## What's wrong
[Just this slice, not the whole report]

## What I expected
[Expected behavior for this specific slice]

## Steps to reproduce
1. [Steps specific to THIS issue]

## Blocked by
- #<issue-number>, or "None, can start immediately"

## Additional context
[Observations relevant to this slice]
```

### 5. Rules for every issue body
- **No file paths or line numbers**: they go stale.
- **Describe behaviors, not code**: "the sync service fails to apply the patch," not "applyPatch() throws on line 42."
- **Use the project's domain language** (check `UBIQUITOUS_LANGUAGE.md`).
- **Reproduction steps are mandatory**: if you can't determine them, ask the user.
- **Durable and concise**: a developer should read it in 30 seconds, and it should still make sense after a major refactor.

### 6. Continue the session
After filing, summarize what was filed (and any blocking edges), then ask: **"Next issue, or are we done?"** Each issue is independent, don't batch. Keep going until the user says they're done.

## ▶ End with the next step

Always close your final message with this breadcrumb so I know where I am in the flow:

> **Flow:** decision-council → grill-me → write-a-prd → to-tickets → implement → code-review → **qa** → triage → okf
> **▶ Next:** `/to-tickets` to slice the new issues (tag AFK/HITL, add blocking edges), then `/implement`.
