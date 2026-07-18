# Pyramid Plunder Review Loop

Date: `2026-07-17`

Cutoff: RuneScape immediately before EOC, `2012-11-20`.

## Pinned period evidence

`Pyramid Plunder` oldid `6529238` (`2012-11-03T18:18:22Z`) establishes a
dangerous Thieving minigame with:

- level 21 entry and eight rooms requiring Thieving levels
  `21/31/41/51/61/71/81/91`;
- five source minutes to loot a run;
- urns that emphasize Thieving XP but can bite and poison;
- a golden chest in each room with better treasure and scarab risk;
- sarcophagi that award Strength XP, can awaken a mummy, and trade time for a
  Pharaoh's sceptre chance;
- progressively better rewards in deeper rooms; and
- pottery/stone/gold artefacts, Pharaoh's sceptre, and Black ibis rewards.

<https://runescape.wiki/w/Pyramid_Plunder?oldid=6529238>

The cutoff page explicitly distinguishes the common XP route—rush to the
deepest accessible rooms and loot urns there—from treasure-oriented chest and
sarcophagus routes.

## Entry and room gates

Starting a run requires level 21 Thieving and access to Sophanem through either
of the two source routes: `Icthlarin's Little Helper` started, or a Pharaoh's
sceptre that bypasses the quest route. This is an ordinary alternative gate,
not travel simulation.

The eight rooms require exact Thieving levels
`21/31/41/51/61/71/81/91`. The engraved sarcophagus in room eight additionally
requires 75 Runecrafting. Completion of `Contact!` for the local bank and
`The Feud` for cheaper carpet travel remain optional benefits rather than entry
requirements. These gates are also indexed in
`activity-entry-gate-ledger-2026-07-18.md`.

## Settled AnkiScape run contract

Starting a run presents one standing priority:

- **Max XP** rushes through early rooms and concentrates productive looting on
  urns in the deepest accessible rooms.
- **Treasure** opens valuable chests and sarcophagi throughout the run,
  accepting lower Thieving XP for artefacts and rare-reward chances.
- **Balanced** opens useful chests while advancing, then emphasizes urns in the
  two deepest accessible rooms.

Neither Casual nor Advanced requires per-room object selection. The chosen
priority automatically drives the run until completion or an explicit leave.
One successful review resolves one accessible room, including its advancement
and priority-shaped looting. A run therefore lasts from one review at level 21
to eight reviews at level 91, with room access following the exact source level
thresholds. The source five-minute limit is represented by this finite room
budget, never by wall time or answered-card minutes.

Persist only current room, chosen priority, accumulated XP/loot, carried
supplies, and shared LP/poison state. Every room transition and reward must
remain atomic and undoable.

## Hazard contract

Urn snakes, scarab swarms, and awakened mummies are room hazards, not separate
Combat encounters:

- the triggering room review applies its sourced or source-audited LP and
  poison consequence through the shared Combat damage channels;
- the period page establishes `10-40` snake-bite damage with `20` starting
  poison, scarab poison starting at `38`, and a level-84 mummy;
- the exact trigger and mummy-damage rolls remain source work rather than being
  inferred from those identities;
- a surviving player advances or finishes the room normally, with the hazard
  summarized in the same review-result line; and
- lethal damage uses the ordinary death/grave pipeline and ends the run.

There is no hazard combat target, extra combat review, hidden attack loop, or
paused encounter state. The Treasure priority naturally accepts more hazard
exposure because it searches more chests and sarcophagi.

## Inventory and loot contract

The run-priority dropdown also controls ordinary artefact retention:

- **Max XP** immediately discards ivory, pottery, stone, gold, and jewelled
  ordinary artefacts. They never occupy an inventory slot.
- **Balanced** immediately discards ivory, pottery, and stone artefacts, but
  retains gold and jewelled artefacts. The period value table makes this a
  stable `750`-coin threshold: gold seal, golden scarab, golden statuette,
  jewelled golden statuette, and jewelled diamond statuette.
- **Treasure** retains every ordinary artefact tier.

Retained artefacts use real carried-inventory slots and therefore compete with
food and antipoison. If the retained haul fills the inventory, the run ends
early and atomically deposits the retained haul into the bank. A normally
completed run does the same after its final room, with one non-blocking summary
and no additional review or manual banking step.

Pharaoh's sceptre, Sceptre of the gods, and Black ibis pieces are protected
unique rewards in every mode and never enter the discard path. Finding a
Pharaoh's sceptre immediately ends the run as the pinned source specifies; a
full inventory routes the protected reward directly to the bank instead of
reproducing the source's ground-drop loss risk.

This closes the owner-facing Pyramid Plunder design. Exact loot and hazard rolls
remain source-audit work, not design forks.
