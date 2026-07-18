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

## Remaining design fork

Artefacts are useful outside the run for selling, quests, and Pharaoh's sceptre
recharging. The remaining owner decision is whether they occupy the player's
real inventory during the run or sit in a temporary activity ledger until the
run ends.
