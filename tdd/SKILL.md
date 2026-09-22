---
name: tdd
description: Drive a change test-first at a pre-agreed seam, write a failing test that pins external behavior, make it pass, then refactor under a green bar. Use when implementing a ticket or spec that has agreed testing decisions, when the user asks to work test-first or "do TDD", or when called by /implement step 3. Not for exploratory spikes or throwaway scripts.
---

# TDD

Drive one change test-first, at a **seam that was agreed before the work started**: in the PRD's Testing Decisions section, or in the ticket. TDD is not "write tests for everything"; it is a design tool applied where the design already said it belongs.

> Fills the `/tdd` reference `/implement` makes at step 3. The seam discipline is the same one `write-a-prd` locks in its Testing Decisions section, this skill is where that decision gets executed.

## Before writing a test

**Find the agreed seam.** Read the ticket's acceptance criteria and the PRD's Testing Decisions. If neither names a seam for this change, stop and ask, do not invent one. A seam chosen mid-implementation is chosen to match the implementation, which is the failure mode this whole discipline exists to prevent.

**Test external behavior, never implementation details.** The test should survive a rewrite of the thing it tests. If renaming a private function breaks the test, the test is at the wrong level. Ask: *would a user of this module notice if this behavior changed?* If no, it does not get a test here.

**Match the project's idiom.** Read a neighbouring test file first, its framework, naming, fixtures, and how it sets up state. A correct test in a foreign style is a review comment waiting to happen.

## The loop

1. **Red.** Write one failing test that pins the behavior the acceptance criterion describes. Run it. **Watch it fail, and read the failure**: a test that passes before the code exists is testing nothing, and a test that fails for the wrong reason is worse than no test. Confirm the message names the missing behavior.
2. **Green.** Write the least code that makes it pass. Not the elegant version, the passing version. Run the single test file, not the suite.
3. **Refactor.** Now make it good, with the bar green the whole way. This is where the design work happens; steps 1 and 2 only bought you the safety to do it.
4. **Repeat** for the next acceptance criterion. One criterion, one loop.

Run **typecheck** every loop or two. Run the **full suite once**, at the end.

## What not to test

- Framework behavior, library internals, or the language itself.
- Private helpers reachable only through the thing you already tested.
- Anything whose test would need to know *how* the code works to stay passing.
- Generated code, config files, and pure data, unless the generation is the behavior.

A criterion you genuinely cannot test at the seam is not a silent skip. Say so, and say why, in the ticket.

## When to stop and hand back

- The agreed seam does not exist yet, or the change does not cross it.
- Making the test pass requires a decision the ticket does not settle, that is HITL.
- The test you would have to write couples to implementation and you cannot find one that does not. That is a design signal, not a testing problem; raise it.

## ▶ End with the next step

Close your final message with:

> **Flow:** decision-council → grill-me → write-a-prd → to-tickets → **implement (tdd)** → code-review → qa → triage → okf
> **▶ Next:** continue `/implement`: remaining criteria, then the full suite, then `/code-review`.
