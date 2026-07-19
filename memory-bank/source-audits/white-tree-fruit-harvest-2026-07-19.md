# White Tree fruit harvest and run-energy substrate — 2026-07-19

## Scope and cutoff

This audit closes the owner-settled White Tree fruit card admitted by
`memory-bank/source-audits/recon-coverage-closure-2026-07-18.md`. The target is
RuneScape immediately before EOC on `2012-11-20`. Quest implementation remains
owned by the Darkan restoration thread; this slice adds only the post-quest
Farming harvest, item effects, run-energy transaction, assets, and UI.

## Direct period record

The literal wikitext of `White tree fruit` oldid
[`5838367`](https://runescape.wiki/w/White_tree_fruit?oldid=5838367), timestamp
`2012-06-26T04:41:55Z`, states:

- the last remaining White Tree after completing Garden of Tranquillity is the
  only acquisition method;
- four fruit grow at a time and have a fast respawn rate;
- each picked fruit awards `12` Farming XP;
- each fruit heals `30` life points and restores `17` run energy;
- White tree fruit is valid supercompost material;
- picking one is a medium Varrock task; and
- Ube accepts one for the Beacon Network tending service.

The MediaWiki API response used for that literal read has SHA-256
`f65ca5a639ff921a7f4d7d2db201a3e3fcdabf600db3a4837d67a69157682fbe`.
There is no pre-cutoff `Talk:White tree fruit` revision. The discovery trail is
`Talk:Repeatable events` oldid `5147379`, as recorded in
`memory-bank/audits/overnight-content-recon-2026-07-19.md`.

`Summer pie` oldid `6358590` independently states that each half restores
`20%` run energy. The live consumable table already carried its period Agility
boost and healing; this slice closes the previously omitted run-energy output
through the same substrate.

## Cache and restored-quest reconciliation

OpenRS2 rev 742 (`2012-11-07`) contains:

- item `6464`, `White tree sapling`, with the client option `Destroy`; and
- item `6469`, `White tree fruit`, with the client options `Eat` and `Drop`.

These definitions corroborate identity and client interactions only. They do
not supply XP, effects, or respawn cadence.

The Darkan repository at
`/Users/ArmanTarkhanian1/Documents/2012scape with bots` was read at
`e121503b2f4571e27e06701d725b3aff6e1acc35`. The relevant restoration history is
`1f06225` (`Close Garden of Tranquillity and advance the restoration loop`);
its accepted runtime world is
`c7803c6ef3f1b90d985a5e9bacc78edd1db8dfb2`, cache commit
`ed4b36bd9add4946c068ca2324bfb4ea11bbcae2`.

The frozen contract at
`memory-bank/audit/evidence/static/garden-of-tranquillity-target-contract.json`
names White Tree fruit picking as a permanent completion unlock. The canonical
headless runtime artifact
`memory-bank/audit/evidence/runtime/quests/garden-of-tranquillity/garden-of-tranquillity-e2-20260715T024507Z.json`
passes its completion, White Tree fruit, replay, and downstream-gate check; the
artifact SHA-256 is
`9c9acfb6a5b657d4687a134ea63df4229e19fad8a53159cabfd3378d27f3532b`.
That restoration explicitly leaves the exact post-quest fruit regrowth cadence
source-blocked.

## Shipped values and bounded abstractions

The source-closed behavior ships literally:

- Garden of Tranquillity completion gate;
- one permanent, disease-free White Tree in the Varrock Palace garden;
- capacity of four fruit;
- `12` Farming XP per fruit actually picked;
- `30` LP and `17%` run-energy restoration per fruit;
- no spade, planting, compost, gardener, watering, curing, replanting, or
  digging controls for the permanent tree; and
- White tree fruit as a supercompost input.

The period record says only “fast respawn.” Exact cadence is
`source_blocked`. Under the owner-approved answered-card clock and the
pattern-determined special-patch contract, the smallest disclosed abstraction
is one fruit regrown per answered card, capped at four. No wall clock is read.

AnkiScape has no continuously simulated run-energy bar. Restored run energy is
therefore represented as a percentage credit against the next moving travel
transaction. A `17%` fruit credit reduces that trip's review cost by `17%`;
credits accumulate to `100%`, stationary routes do not consume them, and a
fully waived trip proceeds into the selected action on the same answer. This
is an AnkiScape representation of the sourced effect, not a claim about a
historical hidden formula.

The post-quest completion flag is the existing AnkiScape quest-boundary
flattening adopted by the recon closure. This slice does not duplicate quest
stages or infer additional dialogue state.

## Explicit exclusions and dependencies

- Garden of Tranquillity stages, rewards, dialogue, and White Tree planting
  remain Darkan/quest-owned.
- The medium Varrock task is recorded but not duplicated; it belongs to the
  achievement-system rework.
- Ube and Beacon Network tending are recorded but not duplicated; they belong
  to the Beacon Network activity.
- Exact fruit respawn timing remains source-blocked.
- The fetched item art is visual provenance only and supplies no mechanic.

## Acceptance mapping

- `tests/test_farming.py`: fixed-patch gate, four-fruit harvest, XP, answered-card
  regrowth, queue-full-run integration, immutable controls, and frontend
  projection.
- `tests/test_logic.py`: White tree fruit LP/run-energy transaction and Summer
  pie run-energy restoration.
- `tests/test_agility.py`: run-energy travel-credit math, cap, and stationary
  preservation.
- `tests/test_runtime_actions.py`: next-moving-trip consumption and fully
  waived-trip continuation.
- `tests/test_integration_smoke.py`: full-run harvest preemption and exact
  answer-undo restoration.
- `tests/test_main_menu_widget.py`: the focused permanent-tree Qt surface and
  truthful locked-state presentation.
- Restarted macOS Anki: real-compositor visual acceptance of the focused
  Farming surface; offscreen Qt is retained only as a regression gate.
