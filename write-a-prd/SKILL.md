---
name: write-a-prd
description: Create a Product Requirements Document through a detailed user interview, codebase exploration, deep-module design, and (for UI features) a design/UX step with a generated mockup, then output it as a local Markdown file or (inside a git repo) a GitHub issue. Use when the user wants to write a PRD, create a product requirements document, spec out or plan a new feature, or turn a rough idea into an implementation-ready doc.
---

# Write a PRD

Turn a rough feature idea into a north-star PRD the user (or an agent) can build from. You may skip steps if you genuinely don't need them, but don't skip the interview.

> Derived from [Matt Pocock's `write-a-prd`](https://github.com/mattpocock/skills/tree/main/skills) (MIT). Steps and template are his; the light polish, the adaptive output step, and the optional design/UX step are ours. Pairs with the `grill-me` skill, step 3 *is* a grilling.

## Process

1. **Get the raw brief.** Ask the user for a long, detailed description of the problem they want to solve and any ideas they already have for solutions. Encourage them to over-share.

2. **Explore the codebase.** Verify their assertions and understand the current state of the code before forming opinions. Use `Read` / `grep` / `Glob`. Don't ask the user things the repo can already tell you.

3. **Interview relentlessly** (this is the `grill-me` discipline). Interview the user about every aspect of the plan until you reach shared understanding. Walk down each branch of the design tree, resolving dependencies between decisions one-by-one. **One question per turn**, and give your **recommended answer** with each. If the codebase can answer it, go check instead of asking.

4. **Sketch the modules.** Lay out the major modules you'll build or modify. Actively hunt for **deep modules**: ones that hide a lot of functionality behind a simple, stable, testable interface that rarely changes (as opposed to shallow modules, which leak complexity through their interface). Then:
   - Confirm with the user that this module breakdown matches their expectations.
   - Ask which modules they want tests written for.

5. **Design the UI, only if the feature has one.** After the decisions are locked, sketch the design: the **key screens/surfaces**, the **primary flow**, and the important **states** (empty / loading / error / success). For UI-heavy features, offer to generate a quick **mockup** so the user can validate the flow visually, a self-contained **Artifact** by default (inline HTML/React; follow the `artifact-design` guidance when you build it), or generate/sync into **Figma** if that's their design source of truth. Keep it lightweight, confirm the direction before building, and link the result in the PRD's *Design / UX* section. **Skip this entirely for backend, CLI, data, or infra features.**

6. **Write the PRD** using the template below, then output it (see *Output*, confirm the destination with the user first).

## PRD Template

```markdown
## Problem Statement

The problem the user is facing, from the user's perspective.

## Solution

The solution to the problem, from the user's perspective.

## User Stories

A LONG, numbered list of user stories, each in the format:

1. As an <actor>, I want <feature>, so that <benefit>

Example:
1. As a mobile bank customer, I want to see the balance on my accounts, so that I can make better-informed decisions about my spending.

Be extensive, cover every aspect of the feature.

## Design / UX

*(UI features only, omit for backend / CLI / data / infra.)*

- **Key screens / surfaces:** the main views this feature introduces or changes.
- **Primary flow:** the happy-path steps the user walks through.
- **States:** empty, loading, error, and success states to handle.
- **Mockup:** link to the generated mockup (Artifact URL or Figma link), if one was made, and describe the intent in words too, since the link and the pixels may not outlive each other.

## Implementation Decisions

The decisions that were made. May include:
- Modules to be built/modified
- The interfaces of those modules
- Technical clarifications from the developer
- Architectural decisions, schema changes, API contracts, specific interactions

Do NOT include specific file paths or code snippets, they go stale fast.

## Testing Decisions

- What makes a good test here (test external behavior, not implementation details)
- Which modules will be tested
- Prior art, similar tests already in the codebase

## Out of Scope

What this PRD deliberately excludes.

## Further Notes

Anything else worth recording.
```

## Output (adaptive)

Once the PRD is written, pick the destination and **confirm it with the user before creating anything**:

- **Default, local Markdown file.** Write to `./prds/<kebab-case-feature-name>.md` (create the `prds/` directory if needed). Tell the user the path.
- **If inside a git repo**: run `git rev-parse --is-inside-work-tree` to check, and `gh auth status` to see if the GitHub CLI is available and authenticated. If both pass, offer to open a GitHub issue instead: `gh issue create --title "<feature>" --body-file <path>`. **Creating the issue is an external, published action, always show the user the title + body and get an explicit yes before running it.** If they decline, fall back to the local file.

Either way, end by giving the user the exact path or issue URL so they have their north-star doc in hand.

## ▶ End with the next step

Always close your final message with this breadcrumb so I know where I am in the flow:

> **Flow:** decision-council → grill-me → **write-a-prd** → to-tickets → implement → code-review → qa → triage → okf
> **▶ Next:** run `/to-tickets` to slice this PRD into vertical-slice tickets.
