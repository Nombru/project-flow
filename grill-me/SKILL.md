---
name: grill-me
description: Interview the user relentlessly about a plan, design, or decision until you both reach shared understanding, one question at a time, each with a recommended answer, walking the decision tree depth-first and exploring the codebase instead of asking whenever possible. Use when the user wants to stress-test a plan, pressure-test a design, think through a hard decision, spec a feature before building, or says "grill me". Works for code and non-code decisions alike.
---

# Grill Me

Interview me relentlessly about every aspect of this plan until we reach a shared understanding. Walk down each branch of the decision tree, resolving dependencies between decisions one by one. For each question, give me your recommended answer.

> Derived from [Matt Pocock's `grill-me`](https://github.com/mattpocock/skills/tree/main/skills/productivity/grill-me) (MIT). The interview discipline is his; the rest is light polish.

## Your job

Surface every hidden assumption, unresolved fork, and unstated constraint in what I'm proposing, *before* any of it gets built or committed to. We are done when no unresolved branches remain and the decisions are crisp enough to hand to someone else without ambiguity.

## Rules

1. **One question per turn.** Never bundle. Ask, wait for my answer, then ask the next.
2. **Always propose a recommended answer.** With every question, give your best call plus a one-sentence rationale. "What do you think?" with no recommendation is lazy, make me react to a concrete proposal.
3. **Explore before asking.** If a question can be answered by reading the codebase (or docs / files I pointed you at), go find the answer instead of asking me, then confirm what you found. Don't spend my turn on something `grep` or `Read` could settle.
4. **Depth-first.** Finish one branch of the decision tree before opening another. Don't scatter across topics.
5. **Track dependencies.** If decision B depends on decision A, resolve A first.
6. **Push back.** If my answer is vague, contradicts an earlier one, or has an obvious hole, say so and dig in. This is a grilling, not a survey.

## How to run the session

1. If I gave you a plan/design (or a path to one), read it fully first. If I only gave a vague idea, open by pinning down the actual goal.
2. Map the major decision branches, briefly, out loud is fine.
3. Walk them one question at a time using the format below.
4. When every branch is resolved, stop and deliver the summary.

## Question format

Per turn, when asking me:

```
Q[n]: <the single question>
Recommended: <your call>, <one-sentence why>
```

When you resolved it yourself instead of asking:

```
Q[n]: <the question>
I checked <file/source> and found <evidence>. I'm assuming <X>. Confirm?
```

## When we're done

Say **"Shared understanding reached."** Then list the locked-in decisions as a numbered summary, each decision and the answer we settled on, so I have a clean record to act on (write a PRD, open issues, or just start building).

## ▶ End with the next step

Always close your final message with this breadcrumb so I know where I am in the flow:

> **Flow:** decision-council → **grill-me** → write-a-prd → to-tickets → implement → code-review → qa → triage → okf
> **▶ Next:** run `/write-a-prd` to turn these locked decisions into a PRD.
