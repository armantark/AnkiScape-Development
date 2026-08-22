# Camouflaged jadinko tracker row — sourcing, 2026-08-22

The `track_camouflaged_jadinko` row in `data/hunter_data.py` is enumerated from
Darkan commit `7e7d67b481f1b94599de38a98c470419ab7c96b3` and the live wiki,
matching the conventions of the twelve existing jadinko rows.

## Values

- Level 79, tracker XP 600.0, vine item 19978, Juju potion required:
  `JadinkoType.kt:42`
  (`CAMOUFLAGED(-1, 79, null, null, -1, 8389, 19978, true,
  HabitatFeature.STANDING_STONES, null, ProduceType.Lergberry, null,
  trackerXp = 600.0, requireEmptyTreePatch = true)`).
  Darkan commit `16b179a` added `trackerXp = 600.0`; both are on the current
  checked-out tree.
- Tracking group (Noose-wand tool) comes from `JadinkoType.kt:127`, where
  `trackerJadinkos = listOf(SHADOW, DISEASED, CAMOUFLAGED)` groups it with the
  two existing Noose-wand tracker rows.
- Success curve reuses the registered
  `PLACEHOLDER(hunter.herblore_habitat_success_curves)` fallback (128/256),
  same as Shadow and Diseased; no period Camouflaged catch routine exists.
- Drop tables: `data/npcs/drops/hunter/hunter_jadinko_camouflaged.json` rolls
  guaranteed 19978 at quantity 1, bush seeds via `hh_bush_seed` at 16/256, one
  of Ugune/Argway/Shengo/Samaden seed (19902/19907/19912/19917) at 4/256, and
  blossom seeds via `hh_blossom_seed` at 4/256. The ordered
  `secondary_drop_tables` contract preserves that source order and rolls all
  three tables independently through the pure and runtime Hunter paths.
- Standing-Stones plus Lergberry plus empty-tree-patch setup: from the
  `JadinkoType.kt` fields above. The AnkiScape Hunter contract models persistent
  setup as route context, not per-catch gating, matching every other jadinko row.

## Name correction: "Striped vine", not "Camo vine"

Design-thread section 3.28 called item 19978 "Camo vine". That name does not
exist on the RuneScape Wiki or anywhere else; the period name is **Striped
vine**:

- Wiki page `Striped_vine`, infobox pins `id = 19978`, released 2010-11-24
  with Herblore Habitat, examine "A striped vine from a jadinko."
- Darkan names it `HerbloreHabitatTransactions.kt:21`
  `const val STRIPED_VINE = 19978`.

The row, its item registration, and the icon therefore use Striped vine.

## Icon

`hunteritems/striped_vine.png` is the archived pre-cutoff wiki sprite,
revision timestamped 2010-11-27T00:31:13Z (314 bytes, sha1
`9025bfed955b13b49859273f7cfe0be5da09bf88`, downloaded from
`https://runescape.wiki/images/archive/20160502081508%21Striped_vine.png?04b49`),
registered in `assets_provenance.json`. The current live wiki image is a
post-cutoff nxt render (2016-05-02T08:15:08Z) and was not used — see the
papercut about post-cutoff sprites reaching main.
