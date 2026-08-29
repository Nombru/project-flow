# Orchestrated mode: leaves as fresh agents

For tree depth 4+ or any build clearly beyond one sitting. The core insight:
the stall-at-80-percent failure is an end-of-long-context disease. Attention,
not time, is the scarce resource, and a fresh subagent per leaf resets it.

## The driver loop

You (the main session) are the driver. You do not implement leaves; you
plan, dispatch, verify, and integrate.

1. **Plan.** Write PLAN.md (contract, tree, gates file per leaf and branch)
   from templates/PLAN.md. This is the only step where the whole task must
   fit in one head. The contract must assign every leaf its own files, and
   the tree must record each leaf's **wave** — see Wave dispatch below.
2. **Dispatch the whole ready wave, concurrently.** The ready wave is every
   leaf whose blocking leaves are already verified. Spawn them together, up
   to the harness concurrency cap, not one at a time. Each subagent's entire
   brief is:
   - the contract section of PLAN.md (not the whole file, not your history)
   - its own gates file, verbatim
   - the instruction: work the four passes until every gate is met with
     evidence, then stop; if a gate is impossible, ABANDON it with a reason.
3. **Verify, never trust.** As each leaf returns, re-run its checks
   yourself: `node <skill-dir>/scripts/gate-check.mjs --status gates/leaf-x.md`
   and rerun a spot-check of the CHECK commands. A leaf that checked its own
   boxes without evidence gets sent back with the specific unmet gates named.
   This is the layer that makes self-certification worthless, and it does not
   get cheaper because ten leaves returned at once. Verify all ten.
4. **Log and advance.** Append one line to PLAN.md's status log per leaf. A
   verified leaf may unblock others: recompute the ready wave and dispatch it
   without waiting for the rest of the current wave to finish. When all
   children of a branch are verified, work the branch's integration gates
   yourself (or dispatch an integration leaf for it).
5. **Report.** Only when the root's gates are met. Paste the ledger, N of N,
   with every ABANDON line surfaced, and re-measure every number you state.

## Wave dispatch

*Local amendment (2026-08-20). Upstream v2 states the driver loop as "dispatch
one leaf ... dispatch the next leaf", with concurrency mentioned afterwards as
something that `can` happen. Followed literally that serialises a build: a
reported test run spent three to four hours and produced a login page. The
contract already guarantees disjoint file ownership, so the permission was
always safe — it just was not an instruction. It is one now.*

Dispatch is concurrent by default and sequential only by exception.

- A **wave** is the set of leaves whose blockers are all verified. Compute it,
  dispatch all of it, recompute as leaves land. Do not walk the tree in order.
- **Batch to the cap, do not fan out unbounded.** Harnesses cap concurrent
  subagents; Claude Code's workflow runner sits at `min(16, CPUs - 2)`. Fill
  the cap, queue the rest. A wave larger than the cap is fine; it drains.
- **Serialise only where ownership genuinely overlaps.** If two ready leaves
  want the same file, the split is wrong. Fix the plan; do not coordinate
  through hope, and do not fall back to running the whole tree in series
  because one pair collided.
- **Isolate where the harness offers it.** A worktree or branch per leaf turns
  file ownership from a promise into a guarantee, and costs a few hundred
  milliseconds of setup.
- Parallelism buys wall-clock time, not token savings, and never buys a
  shortcut through step 3.

## Verification hierarchy

Three layers, weakest to strongest, each catching what the layer below
misses:

1. **Leaf self-check**: gate-check run by the leaf itself. Catches honest
   incompleteness, misses self-deception.
2. **Parent re-run**: the driver re-executes the checks. Catches
   self-deception and environment differences.
3. **Stop-hook** (Claude Code, optional): structurally blocks a session from
   ending while gates are unmet. Catches the driver itself drifting into
   report mode.

Prose discipline is layer zero and it is the weakest; that is the lesson v2
is built on. Prefer moving any repeated judgment call up this hierarchy:
if you find yourself re-checking the same thing twice by reading, write a
CHECK command for it.

## Model and effort tiering

Where the harness allows choosing a model or reasoning effort per subagent,
tier by leaf type. Mechanical leaves (rename sweeps, fixture generation,
applying a decided pattern across files) go to a cheaper model or lower
effort. Design leaves, integration branches, and every verification pass
stay on the strong model. The driver stays on the strong model always; a
weak driver invalidates every verification above layer one.

## When NOT to orchestrate

Below roughly half an hour of real work, subagent overhead (context
re-establishment per leaf) costs more than it buys. Stay solo: one GATES.md,
one session, same discipline. The gates still do their job; you just skip
the dispatch machinery.
