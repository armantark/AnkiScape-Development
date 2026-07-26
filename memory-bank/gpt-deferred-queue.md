# Deferred GPT work

Status: **live queue.** The owner's goal says to defer GPT work until the quota
hook reports the Codex subscription is back inside its daily share.

The hook prints a `[quota used/allowed]` line on every turn. When `codex` is no
longer marked OVER, drain this queue before starting new GPT work.

## Why these items are GPT's rather than anyone else's

Each one is mechanical, high-volume, or verification-shaped — the work Codex does
better and cheaper than the alternatives. None of them blocks a family from
reaching breadth level one, so deferring them costs nothing today.

## Queue

| item | why GPT | blocked family, if any |
| --- | --- | --- |
| ~~Independent verification pass over every family that reached breadth one this week~~ **running 2026-07-26** on `verify/sol-pass` | Sol is the right verifier for did-this-actually-run questions, and a different lineage from the Claude models that wrote all nine families | none; a quality gate, not a blocker |
| Exhaustive drop-table and rare-roll harvest for the boss families | high-volume, bounded extraction from Darkan and the rev-727 cache | none; the breadth rule defers exhaustive catalogs |
| Period-art provenance sweep across the asset library | mechanical, ~83% of the library, tedious rather than hard | Evil Tree, Wicked hood |
| Placeholder retirement pass | each row in `placeholder-values.md` is a bounded dig | none by construction |

## Rules for draining it

1. Read the quota line first. Do not start on a subscription the hook marks OVER.
2. Take items in order. The verification pass comes first because it can
   invalidate work the later items would otherwise build on.
3. A GPT run never gets git, release, or other external side effects. Those stay
   with Claude, per the owner's routing rules.
