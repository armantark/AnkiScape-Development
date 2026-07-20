# Easy Treasure Trails source boundary

Date: `2026-07-19`

Cutoff: RuneScape immediately before EOC, `2012-11-20`.

Status: **implementation blocked by one contract/source conflict and unresolved
hidden reward rolls.**

## Period-qualified behavior

`Clue scroll (easy)`, oldid `6333359`, timestamp
`2012-10-02T09:39:55Z`, establishes that easy trails:

- come from lower-level monsters and H.A.M. pickpocketing;
- do not use coordinate clues, combat, or the Wilderness;
- use simple, emote, map, and cryptic steps; and
- produce another clue in a Scroll box (easy) or the final Casket (easy).

Source:
<https://runescape.wiki/w/Clue_scroll_%28easy%29?oldid=6333359>

`Treasure Trails`, oldid `6473708`, timestamp
`2012-10-26T00:01:09Z`, establishes:

- only a player with no clue in inventory, bank, or Kingdom Management
  resources may receive another clue;
- an easy trail is between one and five clues long;
- the reward is determined when the casket opens rather than by trail length;
  and
- the period common and easy-exclusive reward families.

Source:
<https://runescape.wiki/w/Treasure_Trails?oldid=6473708>

Period guide snapshots close the human-readable clue content:

- `Treasure Trails/Guide/Simple clues`, oldid `6579176`, timestamp
  `2012-11-18T16:48:49Z`;
- `Treasure Trails/Guide/Emotes`, oldid `6538968`, timestamp
  `2012-11-06T15:34:10Z`;
- `Treasure Trails/Guide/Maps`, oldid `6362741`, timestamp
  `2012-10-07T05:35:23Z`; and
- `Treasure Trails/Guide/Cryptics`, oldid `6550565`, timestamp
  `2012-11-13T01:21:29Z`.

The guide pages prove clue text, solutions, tier labels where present,
equipment requirements, and quest/skill gates. They do not state the server's
selection weights.

## Cache identity

The rev-742 cache (`2012-11-07`) contains the complete easy clue item family:

- item `2677` and its variants: `Clue scroll (easy)`, option `Read`;
- item `2714` and its variants: `Casket (easy)`, option `Open`; and
- item `19005` and its variants: `Scroll box (easy)`, option `Open`.

The cache proves client identities and options only. It does not prove the
trail-length, clue-selection, or reward rolls.

## Darkan candidate behavior and conflicts

Darkan commit `f4bb8cab1ea8bce566a8eccb4031e5b14fe77446` contains:

- `src/main/java/com/rs/game/content/minigames/treasuretrails/TreasureTrailsManager.java`
  with typed easy simple, map, and emote rows, a `1 + Utils.random(3)` easy
  trail length, and two-to-four reward rolls;
- `data/npcs/drops/treasure_trails/easy_casket.json` with a `1/12` rare-table
  candidate and `11/12` standard-table candidate; and
- `easy_rare.json` and `easy_standard.json` with candidate item weights and
  quantities.

The period page says one-to-five steps, so Darkan's one-to-three roll is
rejected. The local rev-667 `game-main` checkout contains clue/casket item
identities but no executable Treasure Trails behavior, so it cannot
corroborate Darkan's hidden selection or reward rolls.

Later RuneScape documentation still corroborates the two-to-four reward-spot
shape, but its published rare-item rates do not match Darkan's `1/12 × 1/64`
table. Modern RuneScape can corroborate a period-lineage implementation but
cannot supply a pre-EOC value. The exact clue-type weights, per-row selection
weights, rare/common roll, standard reward weights, and quantities therefore
remain `source_blocked`.

## Contract/source conflict

`memory-bank/treasure-trails-design-contract-2026-07-19.md` calls one clue per
tier the authentic rule. The pinned period page instead permits a new clue only
when the player owns no clue at all. Later RuneScape history dates per-tier
ownership to 2015, after the cutoff.

The design-closure instruction requires implementation to stop rather than
silently reinterpret a settled contract that conflicts with period evidence.
This conflict is recorded in
`memory-bank/design-gaps-implementation-2026-07-19.md`.

## Implementation boundary

Do not activate Easy Treasure Trails yet. A complete atomic slice needs:

1. owner resolution of global one-clue ownership versus the settled per-tier
   clause;
2. a corroborated pre-EOC-lineage clue-selection roll; and
3. a corroborated pre-EOC-lineage casket reward roll, or an owner-authorized
   minimal provisional hidden-roll model that satisfies the verification
   standard.

The period clue text, step count, item identities, and reward membership are
harvested and reusable once those blockers close. No product code was changed
by this audit.

## Research workflow note

Codex Workflows run `743195fa-8342-48af-afbd-6de5af81801c` produced no accepted
read-only result. One leaf escaped its bounded repository scope and was
canceled; the other consumed `221,238` tokens over seven tool calls without a
valid final result and was canceled. All findings above were independently
reproduced by the root agent.
