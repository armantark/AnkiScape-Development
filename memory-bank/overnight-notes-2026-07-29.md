# Running notes — overnight goal run, 2026-07-29

Autonomous mode: running notes here; one results artifact at the end. The
standing breadth goal was re-issued verbatim at ~22:30.

## Budget amendment (owner, mid-run)

The owner authorized spending up to another 24-hour block's worth of codex
beyond today's line. Quota-based parking is off for this run; availability
(upstream "overloaded" refusals) is the only remaining gate, and the
sentinel owns that. The Sol cross-lineage pass over the Opus-authored
miniquest work is affordable the moment Sol serves.

## Budget stance at start

Codex reads over its fresh day line by 3 (carryover from yesterday) but auth
works (verified by probe); the owner issued the goal knowing the queue is
codex-seated, so the two parked builds run on Sol and park again only if the
hard auth wall returns. Claude 66/77 covers orchestration. Kimi (85/86) is
untouched tonight by design.

## In flight

1. Dungeoneering phase C resumed (`wf_aad2b78c-a75`): kinship tiers, the
   staged 42-row trader with the functional Coal bag, period assets.
2. Conquest breadth one resumed (`wf_b1e6a35a-735`) in the `conquest`
   worktree, schema 102.

## Queue after those land

- 4.14 grill consequences: minimal miniquest ledger (Hunt for Surok → Bork;
  Lair of Tarn Razorlor → Dominion class H), then guardian coin drops
  replacing the 3.25 cache. Held until phase C frees ui/ui.py.
- Slayer off-task XP source check (pin Slayer oldid + Darkan/game-main kill
  handlers; amend the contract sentence if confirmed).
- Diary D1 growth from any new routes the miniquests open.
- Merges, both full lanes, memory-bank close-out, one results artifact.

## Mid-run restructure (owner steer: dynamic workflows)

Both codex resumes died on upstream "servers currently overloaded" (proxy
502→503; auth record fresh, patch intact — verified via the
restore-custom-models diagnostics). Replaced the static retry with
`codex-sentinel` (`wf_32a99f49-374`): an Opus probe loop pinging the gateway
through claude-mockingbird every 7 minutes for up to ~3.5h, then running
phase C and Conquest serially as nested child workflows on recovery.
Meanwhile the miniquest work runs on the Anthropic seat as a staged pipeline
(`wf_f6439686-f7f`, Opus medium, `miniquests` worktree, schema 103):
substrate+both quests → Bork ∥ Tarn branches → integration verifier with
per-area parallel refixes. A Sol cross-lineage pass over the Opus-authored
miniquest work is queued for after codex recovers.

## Transport diagnosis and the CLI reroute

The gateway failures are now understood: session client tokens match
client.env (not stale), small Sol requests succeed, and the harness
subagent's single giant first request draws upstream "overloaded", after
which the proxy cools its codex credential and fast-fails 503
auth_unavailable. The codex CLI never trips this because it builds context
incrementally with small requests — every CLI run tonight worked. Both
builds therefore moved to CLI transport: workflow `wf_d7522c72-fde` runs
phase C then Conquest as codex-exec tasks (sol, xhigh implement / high
verify, refix loops), each driven by a thin Opus wrapper that nohup-launches
codex and polls past the ten-minute Bash cap, with one auto-retry after a
ten-minute sleep if the launch itself draws the overload error. Sentinel v2
is retired. The miniquest Opus pipeline continues in parallel.

## Done this run

- Dungeoneering phase C shipped and execution-verified clean over CLI
  transport (`d0cac104`) — the family is fully at breadth one, trader staging
  truthful on all 41 catalogued rows, Coal bag real through Smithing. The
  implementer's full discovery ran 3,572 tests green. Note: the codex
  implementer also wrote a status artifact and opened Arc, which autonomous
  runs shouldn't do — fold its content into the final artifact and tighten
  the next brief.
- Conquest codex build is running as an orphaned CLI process (PID 1032,
  healthy log); a persistent Monitor watches for exit, then a verify+refix
  workflow follows, then rebase-merge.
