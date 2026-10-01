# Jev in the AnkiScape pipeline: decision (2026-09-23)

Source: the Jev grill of 2026-09-22 and 2026-09-23, started from `memory-bank/handoffs/2026-09-22-jev-grill.md`.

## Decision

This repo has no Jev build. No judgment in the AnkiScape pipeline passes both the fit tests for Jev and the quota goal below. The quota goes to audits and to orchestrator turns at the harness level, so the one quota prompt in this record goes to the fleet thread.

## Goal

The owner's goal, in the owner's words: "I wanted to plug Jev into the process/SDLC for this project to make it faster/cheaper." The measure is less Claude quota. The owner set these limits:

- Jev costs at most $1 per day.
- No trial period: "I'd rather just get tangible effects from the getgo and calibrate from there."

## Context

Jev is TypeSafe's System One model. It reads a text state of at most 32K tokens and answers typed questions: Choice, Noul (probability of yes), and Score. A call takes about 0.2 seconds and costs $0.042 per million input tokens. Jev keeps no memory between calls.

Jev can make a **glance check**: the answer is in the text that Jev gets. Jev cannot make an **audit**: the answer needs evidence outside the text, such as a probe against code or a source. These terms come from `~/fleet/GLOSSARY.md`.

## Rules for a later Jev build

The grill settled these rules. A later build in this repo must obey them.

1. Jev runs only in the build pipeline. The add-on never calls Jev.
2. A candidate must have enough volume to justify the cost of calibration labels, or it must sit inside a loop.
3. Jev never writes to a file. A Jev mistake costs at most one rerun or one extra turn of a reasoning model. A Jev mistake never loses a finding or a row.
4. Jev acts from the first day, in that safe direction. There is no shadow trial. Calibration comes later, from the logged decisions.
5. Calibration labels: Opus 5.5 labels each row with the same state that Jev got. The owner checks 20 random rows blind. More than 3 disagreements in 20 rejects the labels.
6. Jev calls cost at most $1 per day.
7. Code in this repo loads the fleet client by path: `~/fleet/config/claude/hooks/typesafe_client.py`. Do not copy it. Do not print the key in `~/.local/state/typesafe/client.env`. A different client must send its own `User-Agent` header, because Cloudflare refuses the default one (error 1010).

## Candidates and why each one failed

The numbers are from the grill measurements of 2026-09-22.

| Candidate | Result | Reason |
| --- | --- | --- |
| Backlog triage | Removed | `memory-bank/gap-backlog.json` has 45 rows: 24 `merged`, 0 `pending`, 15 distinct status strings. `tools/gap_driver.py` starts only `pending` rows with `root_cause == "transcription"`. The Completion Kanban is the live list. |
| Review-finding survival | Removed | No record of rejected findings exists. Survival needs a probe against code, so it is an audit. |
| Citation drift | Removed | `tools/audit_citation_drift.py` ran once, on 2026-08-22: 1,432 citations and 261 actionable rows. Jev can sort only the 305 `changed` and `moved` rows, and the reasoning model still reads all of them. No turns are saved. |
| Papercut classes | Removed | 2,297 lines (about 170K tokens) since 2026-08-05, and 114 to 478 new lines each week. One Opus call for each sweep classifies a week of lines with no calibration. |
| Game-value source check | Removed | Only 13 of 47 rows in `tools/sourced_xp_rates.py` store the quoted wiki text. The other 34 store only a reference, so the check is an audit. |
| Review-verdict screen | Removed | Reviews check code and sources, so they are audits. |
| Dispatch routing | Removed | Fleet calibration: Jev picked the correct model seat in 52.6% of dispatches. |
| Report claim screen | Removed | Fleet calibration: 9 of 10 warnings were false. |
| Test failure screen | Not built | Jev reads the log of a failed test lane. On "environment problem", the runner reruns the lane once. Keyword counts in `memory-bank/papercuts.md` give at most about 42 orchestrator turns in 7 weeks, about 6 per week. This saving is too small for new code. |

## Follow-ups

### 1. Mark the gap backlog as closed (this repo)

The grill found that `memory-bank/gap-backlog.json` is a historical record, and the Completion Kanban is the live list. Other files still send work to the backlog:

- `memory-bank/README.md` line 17
- `memory-bank/roadmap.md` line 12
- `memory-bank/future-work-kanban.md` lines 3, 160, and 1267
- `memory-bank/projectbrief.md` line 12
- `memory-bank/archive/progress-2026-09.md` lines 1027 and 1040

Do these steps in the next staleness sweep of this repo:

1. For each of the 21 rows that do not say `merged`, find the Completion Kanban card that owns the work.
2. If a row has no card, add a card to `memory-bank/future-work-kanban.md`.
3. Change each line in the list above so that it calls the backlog a closed historical record.

### 2. Papercut count rule (fleet thread)

Copy this prompt into the fleet thread:

```text
The global papercut rule in ~/fleet/config/claude/CLAUDE.md says: "When the papercuts.md file grows to have ~25 unaddressed papercuts, propose to dispatch an agent to fix them." No papercuts.md file marks a line as fixed, so no agent can count the unaddressed lines, and the proposal never happens. For example, the AnkiScape file /Users/ArmanTarkhanian1/Library/Application Support/Anki2/addons21/ankiscape_fork/memory-bank/papercuts.md has 2,565 lines on 2026-09-23. Remove the failure with a data-structure change, not with more prose: when an agent fixes papercuts, it moves those lines to a separate fixed file, so the unaddressed count is the line count of papercuts.md. AnkiScape already has one such file: memory-bank/papercuts-fixed-2026-08-11.md. Change the rule text in CLAUDE.md to state this move. Keep the change to one or two sentences. Report the old and new rule text, and the commit hash in the fleet repo.
```

### 3. Citation drift in the staleness sweep (fleet thread)

Copy this prompt into the fleet thread:

```text
The dated-sweep bullet in ~/fleet/skills/universal/cline-rules/SKILL.md says to "re-verify the bank's checkable claims against the repo", but it names no check for file citations. The AnkiScape sweep of 2026-09-13 checked only six core files. The AnkiScape repo has a tool for this: /Users/ArmanTarkhanian1/Library/Application Support/Anki2/addons21/ankiscape_fork/tools/audit_citation_drift.py. On 2026-08-22 it found 261 actionable rows in 1,432 citations, and nobody has run it since. Add one sentence to the dated-sweep bullet: when the repo has a citation drift tool, run it first and fix its actionable rows in the same sweep. Do not copy the tool into the fleet. Report the old and new bullet text, and the commit hash in the fleet repo.
```

### 4. Quota for small judgments at the harness level (fleet thread)

Copy this prompt into the fleet thread:

```text
A grill in the AnkiScape repo (/Users/ArmanTarkhanian1/Library/Application Support/Anki2/addons21/ankiscape_fork/memory-bank/jev-fit-decision-2026-09-23.md) looked for places where Jev can cut Claude quota. It found none in that repo. Most quota goes to audits, which Jev cannot do, and to orchestrator turns that make small judgments, which happen at the harness level. Find where those turns are. Do not repeat the work in ~/Documents/Claude Code/memory-bank/specs/jev-hooks/ (tickets 01 to 08). Use the transcripts under ~/.claude/projects/. Classify a sample of orchestrator turns by the judgment that the turn made. Mark each class as glance check or audit, per ~/fleet/GLOSSARY.md. For each glance-check class, give the count of turns each week and the quota that Jev can save. Obey these limits: Jev costs at most $1 per day, there is no shadow trial, and a Jev mistake costs at most one extra turn, never lost work. Output: a table of classes with counts, and one recommendation. Do not build anything.
```

## Open questions

None.
