---
name: implement
description: Implement one ticket or spec end-to-end, TDD at pre-agreed seams, run typechecks and tests as you go, keep CI green, review, then commit. Includes the AFK ("Ralph") loop for running autonomously over a queue of ready-for-agent tickets. Invoke explicitly with /implement <ticket>.
disable-model-invocation: true
---

# Implement

Implement one ticket (or a small set) end-to-end, keeping the build green the whole way. Invoked explicitly with `/implement <ticket>`: it writes and commits code, so it never auto-triggers.

> Derived from [Matt Pocock's `implement`](https://github.com/mattpocock/skills) (MIT). The core discipline (TDD at seams, typecheck/test cadence, `/code-review`, commit) is his; the graceful fallbacks, guardrails, and AFK-loop section are ours.

## Per-ticket workflow

1. **Load the ticket.** Read the issue/spec, a path, an issue number, or the description the user gives. Pull out the end-to-end behavior and the acceptance criteria; that's your definition of done. If one of its blockers isn't finished, stop and say so.

2. **Understand the seam.** Skim the relevant code and the domain language (`UBIQUITOUS_LANGUAGE.md` if present) so you build in the project's idiom. Do the smallest prefactor that makes the change easy, if one is obvious.

3. **TDD at pre-agreed seams.** Use the `/tdd` skill if it's installed; otherwise do it directly, write a failing test that pins the *external behavior* at the seam, then make it pass. Test behavior, not implementation details.

4. **Keep the loop tight.** Run typechecking regularly and single test files as you go. Run the **full test suite once at the end**. Keep CI green throughout, never leave the tree red between steps.

5. **Review.** Use the `/code-review` skill if available; otherwise do a focused self-review against the acceptance criteria and the project's conventions, and fix what it turns up.

6. **Finish.** Commit to the current branch with a clear message. On a repo that works in PRs, open one against the ticket; otherwise leave a clean commit. Tick the acceptance criteria and report what changed.

## The AFK ("Ralph") loop

To run agents over the whole `ready-for-agent` queue while you're away:

1. Pick the next AFK ticket whose blockers are all done, work the *frontier* (see `/to-tickets`).
2. Run the per-ticket workflow above to green.
3. Open the PR / commit and mark the ticket done.
4. Repeat until no `ready-for-agent` ticket has its blockers satisfied.

In Claude Code the simplest harness is the `/loop` skill driving a prompt like *"pick up the next ready-for-agent ticket whose blockers are done, implement it to green with /implement, then stop"*, re-running until the queue is dry. Give each ticket a **fresh context window**. Leave **HITL** tickets for a human. When several run in parallel, use isolated branches or git worktrees so they don't collide.

## Guardrails

- **Stay inside the ticket's scope.** New problems you spot become `/qa` issues, not surprise commits.
- **If acceptance is ambiguous or a real decision surfaces, stop** and treat it as HITL rather than guessing.
- **Never commit secrets.** Don't push or merge unless the user has explicitly asked you to, a clean local commit or an opened PR is the default finish line.

## ▶ End with the next step

Always close your final message with this breadcrumb so I know where I am in the flow:

> **Flow:** decision-council → grill-me → write-a-prd → to-tickets → **implement** → code-review → qa → triage → okf
> **▶ Next:** pick up the next `ready-for-agent` ticket, or run `/qa` once there's something to test.
