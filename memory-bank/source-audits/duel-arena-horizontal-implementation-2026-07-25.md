# Duel Arena Horizontal Implementation Source Audit

Date: 2026-07-25

## Scope decision

This family implements free, friendly Duel Arena challenges only. It excludes
staking, coin debits, coin rewards, and Duel Tournaments. The tournament
exclusion follows the settled decision in
`memory-bank/design-thread-queue.md` section 4.6 and the pinned period article,
which records their removal on 2011-02-01.

## Sources in required order

### 1. Darkan and its rev-727 lineage

Primary local checkout:

- repository:
  `/Users/ArmanTarkhanian1/Documents/2012scape with bots/darkan-world-server`
- commit: `d1d10fe9f9f9692e4a9d14d2435e2028934efe85`
- rule model:
  `src/main/java/com/rs/game/content/minigames/duel/DuelRules.java`
- arena lifecycle:
  `src/main/java/com/rs/game/content/minigames/duel/DuelArenaController.java`
- challenge entry:
  `src/main/java/com/rs/game/content/minigames/duel/DuelController.java`
- item metadata:
  `data/items/config.json`, item IDs `20795` through `20800`
- interface inventory:
  `developer-information/interfaceList.txt`, interface `640`
- item CS2 export:
  `developer-information/itemListCS2.txt`, item IDs `20795` through `20800`

The local Darkan sources and the rev-727 cache are one source lineage, so they
are not counted as independent corroboration.

Sourced facts harvested:

- `DuelRules.canAccept` rejects a rule set that disables Ranged, Melee, and
  Magic together.
- The rule interface maps the counted options to rule IDs `0`, `1`, `2`, `9`,
  `8`, `7`, `3`, `4`, `5`, `25`, and `6`.
- Rule `7` blocks use of the in-arena forfeit object.
- Rules `3`, `4`, and `25` block drinks, food, and movement respectively.
- Rule `6` selects obstacle arenas.
- `DuelArenaController.endDuel` resets both victor and loser and returns both
  through the safe ending path.
- Items `20795` through `20800` are the six Duellist's cap tiers.

Staking code exists in Darkan but is deliberately not carried into AnkiScape.

### 2. `game-main`

Local extracted tree:

- `/Users/ArmanTarkhanian1/Downloads/game-main`
- revision status: this extract is not a Git checkout, so no commit hash is
  available
- item table: `data/cfg/items.yml`, lines `248349` through `248384`

This tree independently preserves item IDs `20795` through `20800` under the
name `Duellist's cap`. It contains no Duel Arena implementation usable for this
family. Its generated `tradeable: true` rows conflict with the pinned period
pages, so they do not control the non-tradeable item flag.

### 3. Dated OpenRS2 cache

- cache revision: `742`
- cache date: `2012-11-07`
- disk archive:
  `/Users/ArmanTarkhanian1/Library/Caches/codex/2012scape-openrs2/runescape-742-2012-11-07-openrs2-544-disk.zip`
- SHA-256:
  `9f5fdba0d22cdc1b4ad86c984cc0ba4bcd4b3c22039f3290ba48f5083bc100b8`
- extracted cache:
  `/Users/ArmanTarkhanian1/Library/Caches/codex/2012scape-openrs2/extracted/742-2012-11-07/cache`
- query command:
  `tools/query_openrs2_cache.sh <cache-path> duellist`

The cache returns six item definitions, IDs `20795` through `20800`, all named
`Duellist's cap`, with `Wear`, `Options`, `Change-look`, and `Destroy` actions.

### 4. Pinned historical wiki corroboration

- Duel Arena:
  `https://runescape.wiki/w/Duel_Arena?oldid=6398696`
  - revision timestamp: `2012-10-14T03:38:01Z`
- Duellist's cap aggregate:
  `https://runescape.wiki/?oldid=6591278`
  - revision timestamp: `2012-11-20T05:33:12Z`
- tier pages:
  revisions `6591280`, `6591282`, `6591283`, `6591285`, `6591286`, and
  `6591288`, all created after the strict `2012-11-20T00:00:00Z` cutoff

The aggregate and tier pages are near-cutoff fallback evidence, not period-pinned
pages. Their win thresholds therefore ship as the registered
`duel_arena_cap_thresholds` placeholder rather than as a closed period claim.

Sourced facts harvested:

- friendly challenges are free and safe;
- no items are lost in a friendly challenge;
- entry normalizes stats and the ending restores stats, health, run energy,
  poison, and other stat effects;
- the interface describes eleven counted duel options:
  No Ranged, No Melee, No Magic, No Special Attacks, Fun Weapons, No Forfeit,
  No Drinks, No Food, No Prayer, No Movement, and Obstacles;
- Summoning Enabled is a separate members option and is not one of the counted
  eleven in this family;
- the cap is non-tradeable and obtained from Estocada; its appearance can be
  changed after reaching the next win threshold;
- the near-cutoff fallback tier pages state `0`, `10`, `100`, `500`, `2,000`,
  and `5,000` wins, but those values remain a registered placeholder because
  the pages miss the strict cutoff by about five hours.

## Sourced facts implemented

- Exactly eleven configurable rule toggles are registered.
- Impossible all-style-disabled rules and mutually exclusive
  No Movement/Obstacles are rejected before entry.
- A duel has explicit inactive, active, won, lost, and abandoned result states.
- `No Forfeit` blocks direct abandonment; every duel still resolves within five
  successful reviews, so the period rule cannot trap a player indefinitely.
- Win, loss, and allowed abandonment are safe and restore lifepoints, Prayer
  points, current combat levels, special attack energy, status effects, run
  energy, the previous combat target, and the empty combat encounter.
- Wins persist and deterministically select the six registered Duellist's cap
  tiers without a redundant persisted tier key.
- Estocada's claim/change-look interaction is represented by an undoable cap
  action. It grants the currently unlocked wearable cap, upgrades an owned cap
  at each reached threshold, and never creates duplicate tiers.
- The family never reads, debits, or awards Coins.
- Tournaments and staking have no data, controls, messages, or runtime path.

## AnkiScape abstractions

These values are product mechanics, not claims about the period game:

- one simulated opponent is selected from a fixed player-relative
  `(-8, 0, +8)` combat-level cycle and clamped to combat levels `3` through
  `138`;
- each eligible successful review resolves one duel exchange;
- the review duel is first to three exchanges with an absolute maximum of five
  reviews;
- the per-exchange player chance is bounded to `0.25` through `0.75` from the
  combat-level difference;
- direct abandonment is the AnkiScape control for the period trapdoor forfeit;
  `No Forfeit` disables it, while the five-review bound guarantees completion.

All eleven rule choices are persisted symmetrically for the simulated
challenge. The bounded simulation never consumes food, drinks, Prayer, special
attack energy, or equipment, so the corresponding prohibitions do not create
invented secondary effects.

## Assets

`tools/fetch_duel_arena_assets.py` installs:

- `activityicons/duel_arena.png`
- `activityitems/duellists_cap_tier_1.png` through
  `activityitems/duellists_cap_tier_6.png`

The pinned 2012 tier pages explicitly name the exact sprite files. The migrated
RuneScape Wiki file histories begin in 2022, so the fetcher uses current exact
item sprites only as an asset fallback. They are not mechanics evidence and
are not described as period-dated art. Every installed path is recorded in
`assets_provenance.json`.

## Placeholder register

`duel_arena_cap_thresholds` registers the six win thresholds. The mechanic is
complete around the fallback values, but they are not period-closed because the
available wiki tier revisions were created about five hours after the strict
cutoff. A pre-cutoff server/config source or dated page that states all six
thresholds would settle it.
