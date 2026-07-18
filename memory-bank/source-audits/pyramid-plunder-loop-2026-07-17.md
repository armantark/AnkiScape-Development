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
supplies, LP/poison state, and any active hazard required by the eventual hazard
decision. Every room transition and reward must remain atomic and undoable.

## Open design fork

The source permits scarab swarms and mummies to attack while the looting run
continues. AnkiScape still needs to decide whether those hazards become separate
Combat encounters or immediate shared-LP/poison consequences inside the room
review.
