# Thieving table closure — 2026-07-13

## Shipped authority

- Pickpocket levels, chance endpoints, XP, loot, damage, and stun are transcribed
  from `PickpocketTarget.kt:63-565` in the local 2011Scape snapshot. The runtime
  uses the source's inclusive roll, so a threshold `q` succeeds on `q + 1` of
  the 255 possible integers.
- Multi-pickpocket is transcribed from `Pickpocketing.kt:97-113`: the 1-in-7
  trigger and exact Thieving/Agility overshoot tiers produce two, three, or four
  loot grants while XP remains once per successful attempt.
- Stall levels, XP, complete loot tables, and respawn ticks are transcribed from
  `StallTarget.kt:22-351`. `Stalls.kt:33-69` has no stochastic catch roll; its
  only catch path is a positional guard sight check that AnkiScape cannot
  represent. Ordinary stall catch chance is therefore zero.
- Each stall cadence is exactly `6000 / respawnTicks` actions per balancing
  hour. Vegetable, baker, and wall safe explicitly declare the kernel's
  one-action cap. The exact high-level rates are silver 6,480 XP/hour, spice
  `486000/133` XP/hour, and gem 3,200 XP/hour.
- Wall safe is the only chance-bearing stall-family row. It uses level-1/99
  endpoints 8/160 from `StallTarget.kt:244-264`, but not the pickpocket helper:
  `thieving.plugin.kts:72-99` calls the standalone three-argument
  `interpolate(...) > RANDOM.nextInt(255)`. `MiscExt.kt:51-57` therefore yields
  an exact success-count function distinct from pickpocketing and applies
  20–60 LP trap damage on failure.

## Owner-resolved additions

- Pompous merchant ships from the pinned period page
  `https://runescape.wiki/w/Pompous_merchant?oldid=6437126`: level 1, 8 XP,
  3 coins, 10 LP failure damage, and the one-review stun contract. Its chance
  endpoints use the level-1 ordinary-person row as a documented provisional
  bridge because the period page supplies no hidden roll.
- Menaphite thug blackjacking ships from
  `https://runescape.wiki/w/Menaphite_Thug?oldid=6546629`: level 65, 10 knockout
  XP, two guaranteed unconscious picks, 137.5 XP and 60 coins per pick, and 40
  LP on a failed knockout. The hidden knockout threshold is the owner-approved
  provisional Darkan lead `Utils.skillSuccess(level, multiplier, 185, 255)` at
  `Knock-Out.kt:13-20`; Darkan core 2.0.5 uses
  `floor(185 + 70 * level / 99)` against an inclusive 0..254 roll. Picks do not
  reuse Darkan's independent roll because the period source says unconscious
  picks cannot fail.
- Fight-back uses the period Menaphite level 55 and the Darkan combat definition
  `data/npcs/combatdefs/uncategorized/menaphite_thug (noanims).json` for hidden
  stats: 600 LP, Attack 60, Strength 50, Defence 20, max hit 70, melee/crush.
- Desert Phoenix is a no-XP Utility action, not a Thieving target. It yields one
  Phoenix feather and is gated on The Golem, from
  `https://runescape.wiki/w/Desert_Phoenix?oldid=6295341`.
- The visible skill icon is RuneScape Wiki `File:Thieving-icon.png` (SHA-1
  `beea7bf8eb20ed9cb1014474cc5bd1fe146fd76e`, 2022-11-23); the fetcher queries
  RuneScape Wiki before any OSRS fallback. The Phoenix image is also RS3-sourced.

## Parked rows

- Dorgesh-Kaan chests remain visible, quest-gated, and `source_blocked`: the
  period record does not close the success/loot table.
- Lletya elf remains visible, quest-gated, and `source_blocked`: 2011Scape is
  silent and Darkan is only a lead.
- Pirates' Hideout chest remains parked because its period XP is literally
  unknown.
- Bearded/Pollnivnian blackjack variants and monkey knife fighter remain parked:
  their complete hidden rolls and/or failure values are not closed without
  analogy. Menaphite provides the complete playable blackjack loop.
- Pyramid Plunder, Sorceress's Garden, the Rogues' Den maze, and Thieves' Guild
  belong to the Activities program. Only the separable Rogues' Den wall safe is
  in this skill.

## Source pins

- 2011Scape snapshot: local `~/Downloads/game-main` (no repository metadata).
- Darkan working HEAD: `4cd64632000d736d4360f09335149d2d115e2e12`.
- Darkan blackjack file origins: `Knock-Out.kt` at
  `4194d27d650cb578de7c2a53a735a65e09b3560b`, `Blackjacking.java` at
  `2efc2c98ddfcdd012b0f7f49ef095b9ac55308e2`, and `LootThug.java` at
  `3d9d9394676ab10e356f8209961b5962dc73b5f9`.
- Darkan core 2.0.5 jar SHA-256:
  `bfaf99f7bb04a55418a9aeb07a01f2724034692637b435a87df4f3f4b029e3`.
