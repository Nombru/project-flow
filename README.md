# Project Flow — a staged skill system for agentic coding

A set of [Claude Code](https://claude.com/claude-code) skills that turn "ask an agent to build
something" into a staged process with alignment up front, work sliced small, and a definition of
done that is a shell exit rather than a feeling.

Most agentic-coding failures come from two places. An agent **charges ahead on wrong
assumptions**, or it **reports done before it is done**. The flow fixes the first by front-loading
alignment and slicing work into independent end-to-end units. A separate discipline layer fixes
the second by writing acceptance gates to a file *before* the build starts, and holding review to
them afterward.

## The flow

```
    Fork in the road ··> 0 Decide ──┐
                                    ├─> 1 Align ─> 2 Specify ─> 3 Slice ─┬─AFK─> 4 Build ─┐
    Rough idea ─────────────────────┘                                    │                 ├─> 5 Review
                                                                         └─HITL─> you ─────┘      │
                    8 Record <─ all clear ─ 6 QA <────────────────────────────────────────────────┘
                                              └─ bugs ─> 7 Route ─> back to 3
```

| # | Stage | Skill | Out |
|---|---|---|---|
| 0 | Decide | `decision-council` | Five lenses on a fork with no obvious answer |
| 1 | Align | `grill-me` | Locked decisions, reached by interrogation |
| 2 | Specify | `write-a-prd` | A PRD grounded in the actual codebase |
| 3 | Slice | `to-tickets` | Vertical slices with blocking edges, **AFK/HITL**, capability tier |
| 4 | Build | `implement` + `tdd` | A green commit |
| 5 | Review | `code-review` | Findings, applied or filed |
| 6 | QA | `qa` | Behaviour-focused issues, from using the thing |
| 7 | Route | `triage` | `ready-for-agent` / `ready-for-human` / `needs-info` / `wontfix` |
| 8 | Record | `okf` | An indexed, validated knowledge bundle |

Stages 0–3 are a **funnel**, run once per feature. Stages 4–8 are a **loop**. The feature is done
when a QA pass turns up nothing worth filing.

## The two ideas worth stealing

**Routing decides who may attempt the work, and it is decided once.** At stage 3 every ticket is
stamped `AFK` (an agent may take it) or `HITL` (a human must), plus a capability tier naming which
executor is allowed to try. Nothing downstream re-derives that. A router reads the stamp; it never
second-guesses it. Keeping the decision in one place is what stops an agent from quietly promoting
its own eligibility.

**Done is a file, not a feeling.** The `unlazy` discipline writes acceptance gates *before* stage 4
begins. Each gate carries a `CHECK:` command and an `EXPECT:` match, so completion is a shell exit
code. An agent cannot declare victory past a gate that has not run.

## What it measured

Routing is only worth deciding once if the answer is not obvious. It was not.

Across **168 tickets** on a real iOS project, **14 were ever agent-eligible. That is 8.3%.**

| | Count | Closed | Still open |
|---|---:|---:|---:|
| `ready-for-agent` | 14 | 14 | **0** |
| `ready-for-human` | 97 | 50 | 47 |
| `in-progress` | 3 | 3 | 0 |

The eligibility criterion was fixed at stage 3 before any of this ran, so that is a measured rate
and not a post-hoc rationalisation. The queue did not drift toward being human. It was human from
the start, and slicing more of it only produced more human work.

The unattended overnight runner wrote **3 pull requests** that a human reviewed and merged. It was
retired on 2026-08-03, after three independent passes (a readiness review, a design-review triage,
and slicing one more arc, which produced 13 further tickets and not one of them eligible) found the
eligible queue structurally empty. The 8.3% count was taken on 2026-08-29 and confirmed what the
decision had already assumed.

A loop that fires nightly into an empty queue is a liability rather than a tool. The honest result
of building this router was learning how little of real product work an agent should be handed
unattended.

## Tiers

Every skill is exactly one tier, and the tier decides behaviour rather than importance.

- **Pipeline** — sequenced and stateful, ends by naming the next stage.
- **Discipline** — cross-cutting, changes *how* a stage runs, never names a next stage.
- **Craft** — domain taste, fires only when the work is in that domain.
- **Knowledge** — maintains standing context, produces no code and takes no ticket.

> The test: if a skill ends by pointing at a next stage, it is a stage. If it points somewhere
> *and* wraps other work, it is mislabelled — a discipline claiming to be a stage will fight the
> stage it is wrapping.

## Install

Clone into your Claude Code skills directory:

```bash
git clone https://github.com/Nombru/project-flow ~/.claude/skills
```

Then invoke any stage by name, or run `/flow` to be told where the project currently sits and
which command comes next.

## Notes

- `overnight/` drives a private companion tool and will not run without it. It is kept here
  because it is part of how the flow actually operates, not as a working example.
- The flow chart is also rendered as [`flow-chart.svg`](flow-chart.svg).
- `WORKFLOW.md` is the full standard, including the design lane and the boundaries between stages.

## Credits

Stages 1–5 adapt **Matt Pocock**'s [AI Hero](https://www.aihero.dev) workshop and his
[`mattpocock/skills`](https://github.com/mattpocock/skills) repo (MIT). Stage 0 adapts Dave Brown's
`decision-council`. The discipline layer is [`unlazy`](https://github.com/Leonxlnx/unlazy) (MIT,
Leonxlnx). This repo is a particular assembly of those pieces plus the routing, tiering and gating
that hold them together.
