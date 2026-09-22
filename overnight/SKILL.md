---
name: overnight
description: Hand the ready-for-agent queue to the overnight switchboard runner so it keeps working while you are away, shows what would run, confirms, then starts it in the background and reports where the results will land. Use when the user says they are done for the day, wants to queue work overnight, asks to "run the overnight", "kick off the switchboard", "work on this while I'm away", or wants to check whether an overnight run is in progress.
---

# Overnight

Start the switchboard runner on demand, at the end of a working session, so pull
requests are waiting when the user comes back.

> **This is the only trigger.** The 01:00 launchd job was unloaded on 2026-08-24,
> nothing starts a run except this skill. If the user expects nightly automation,
> tell them it is gone by design; they asked for on-command.

## What it actually does

`bin/overnight.sh --now [HH:MM]` in
`~/Developer/04-Toolkit/overnight-switchboard` (a private companion tool).

`--now` does **not** disable the wake guard. It moves the dispatch window so the
window starts at the current time and ends at the deadline. The guard still runs
and still validates the clock; the cap and the deadline are still enforced by
`may_claim_another`. The control that matters, a missed launchd fire replaying
when the laptop is opened, is untouched, because that path never passes `--now`.

## Process

### 1. Show what would run, before starting anything

Run the eligibility preview and show the user the real queue, not a guess:

```bash
bash bin/arm-tonight.sh --status
```

Then list eligible tickets. If **nothing is eligible**, stop and say so. Do not
start a run for an empty queue, say what is blocking (`ready-for-human`,
untagged tier, already claimed) and offer `/triage` instead.

### 2. Confirm before starting

State plainly, and wait for a yes:
- how many tickets it may attempt (the cap, normally 2)
- the deadline dispatch stops at
- that it opens pull requests and **never merges**

The cap is what protects the user's morning. Never raise it because the queue is
long, more PRs than can be reviewed carefully just moves the bottleneck.

### 3. Start it, detached

Run in the background so it survives the session ending, and hold the Mac awake
for the duration:

```bash
cd ~/Developer/04-Toolkit/overnight-switchboard
nohup caffeinate -i -s bash bin/overnight.sh --now 05:00 >> logs/overnight.log 2>&1 &
```

**Lid open, on AC.** `caffeinate` prevents idle sleep, not lid-close sleep. A
closed lid sleeps the Mac and the run dies silently, say this every time.

### 4. Tell them where to look

- Progress: `tail -f logs/overnight.log`
- One notification fires when the run ends
- Pull requests wait for review; nothing is merged

## Checking on a run in progress

```bash
pgrep -fl overnight.sh || echo "no run in progress"
tail -20 logs/overnight.log
```

## Stopping a run

`pkill -f overnight.sh`. The EXIT trap tears down the worktree and releases the
issue claim. Verify the claim actually dropped, a stuck `in-progress` label
makes that ticket invisible to the next run:

```bash
gh issue list --repo OWNER/REPO --label in-progress
```

## What to tell the user honestly

- **The local model is not in the loop.** Ticket 09 (the Aider drafter) was never
  built; `overnight.sh` has zero local-model call sites. Every run is Sonnet for
  gate-and-repair and Opus for synthesis, and it draws on the Claude usage
  window. If they say "Claude and the local model", correct it.
- **A green gate is not a correct change.** Eight defects have been found in this
  system, every one green and wrong. Review the PRs.
