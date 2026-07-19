# Slayer Harpie Bug Swarm Combat closure

Date: 2026-07-18  
Status: **implemented; no owner-facing design fork**

## Period identity and combat

RuneScape Wiki `Harpie Bug Swarm`, oldid `6530649`, timestamp
`2012-11-04T07:56:04Z`, establishes the ordinary level-46 form at 250 LP,
Slayer 33, 25 Slayer XP, six-tick melee, a 60-LP maximum hit, aggression,
Vannaka/Chaeldar assignment membership, and no guaranteed drop.

Source:
<https://runescape.wiki/w/Harpie_Bug_Swarm?oldid=6530649>.

The pinned Darkan sources supply the executable data beneath that identity:

- `HarpieBug.java:27-42` binds NPC 3153 and zeroes every player hit unless
  lit bug lantern item 7053 is currently in the shield slot. This is a
  continuous damage gate, not merely a start check.
- `data/npcs/combatdefs/uncategorized/harpie_bug_swarm (noanims).json:1-30`
  supplies 250 LP, a 60-LP maximum hit, melee, aggression, respawn 59, and
  Attack 54, Strength 46, Defence 32, Magic 1, and Ranged 1.
- `developer-information/npcList.txt:3154` identifies NPC 3153 as the
  level-46 ordinary form.
- `developer-information/npcListBonuses.txt:3155` supplies zero attack
  bonuses and defences 10 stab, 5 slash, 10 crush, 5 magic, and 10 ranged.

## Lit bug lantern chain

RuneScape Wiki `Lit bug lantern`, oldid `6591557`, timestamp
`2012-11-20T05:41:16Z`, establishes:

- the shield-slot identity and zero bonuses;
- Slayer 33 to wield it;
- Firemaking 33 plus a tinderbox to light the unlit lantern;
- the unlit lantern's 130-coin Slayer-master purchase;
- lit being untradeable; and
- the important exception that it is **not** a functional cave light source.

Source:
<https://runescape.wiki/w/Lit_bug_lantern?oldid=6591557>.

Darkan `src/main/java/com/rs/game/content/world/LightSource.java:29-33,72-101`
places 7051→7053 in the tinderbox transform and 7053→7051 in the Extinguish
binding. AnkiScape therefore adds the same one-review, zero-XP Utility pair as
the existing lantern actions. `Lit bug lantern` is deliberately excluded from
`LIT_LIGHT_SOURCE_ITEMS`, so lighting it does not accidentally satisfy cave,
quest, or Agility-course illumination gates.

game-main `data/cfg/items.yml:78899-78975` supplies the two 2.2 kg shield
identities and zero bonuses. Darkan
`data/items/shops/vannakas_slayer_equipment.json:91-95` and the generated live
shop ledger supply the ten-item, 130-coin unlit stock. The generated equipment
row uses lit item 7053; the existing shop row already exposes unlit item 7051.

## Drops and charm selector

Darkan `data/npcs/drops/harpie_bug_swarm.json:1-210` has 17 nonzero sibling
rows. Under Darkan's executable `DropList` semantics, already audited for this
repository, those rows share one cumulative ordinary selection rather than 17
independent rolls. Their least common denominator is 100,000:

- each `5257/50000` row occupies 10,514 slots;
- each `73/3125` row occupies 2,336 slots;
- each `467/100000` row occupies 467 slots; and
- 471 slots remain empty.

The two Bones rows remain separately transcribed because they are distinct
source rows, although both award one Bones item. The source's quantity ranges
remain inclusive.

`data/npcs/charmDrops.txt:85` records `2-6-0-0`. Darkan
`src/main/java/com/rs/tools/old/CharmDrop.java:54-75` rolls uniformly over
inclusive integers 0–100, admits every nonzero threshold containing the roll,
then selects uniformly among admitted charm types. For this row:

- rolls 0–2 admit Gold and Green equally;
- rolls 3–6 admit Green only; and
- rolls 7–100 yield no charm.

The exact executable selector is therefore 3 Gold, 11 Green, and 188 empty
slots out of 202. Crimson and Blue have zero threshold and are never admitted.

The cutoff wiki's qualitative drop table differs materially from Darkan's
JSON contents. AnkiScape uses the exact executable Darkan selectors and labels
the conflict; it does not claim the JSON rows are a period-exact wiki drop
reconstruction.

## Runtime and UI mapping

- The target cannot be selected below Slayer 33 or without the lit lantern in
  the shield slot.
- Because the requirement is persistent, an active encounter also blocks the
  next review if the player removes or extinguishes the lantern.
- The Combat picker exposes the continuous gate, exact LP/max-hit/speed,
  independent ordinary and charm selectors, and the period target sprite.
- The Utility surface exposes both lighting and extinguishing. The lit item
  has its own period lantern sprite and is wearable shield equipment.
- No quest state is added. The ordinary habitat and Slayer-master acquisition
  path require no quest completion, so this slice does not overlap Darkan's
  quest-parity work.

## Workflow and design-gap record

The bounded read-only Sol-high Codex Workflows run
`0f0fc5e1-e1e7-41b8-bb7f-4bfe4641f7a1` produced no review material and failed
before session creation with
`provider emitted no startup event within 30s`. Its stderr adds
`failed to refresh available models: timeout waiting for child process to
exit`, but the externally visible failure remains the already-known
zero-startup-event signature. Root independently reproduced the evidence and
owns implementation and verification.

No creative-direction question emerged. The drop-content conflict is an
evidence-confidence issue, not a materially different player-experience fork.

## Verification

- Focused Combat/Slayer/Firemaking/equipment/registry/runtime/metadata suite:
  **747 tests passed**.
- Targeted real offscreen Qt Combat picker: **1 test passed**.
- Full non-Qt repository suite: **1,640 tests passed**, with 215 declared
  Qt-environment skips and no failures or errors.
- Full real offscreen Qt repository suite: **1,640 tests executed**, with zero
  skips, failures, or errors.
- Documentation, test-quality, generated-data, asset-provenance, diff, and
  worktree-layout gates pass. The reachability audit retains the known global
  debt at 1,253 actions, 1,836 reachable items, 297 orphan inputs, and 324
  blocked actions.
- `tools/audit_slayer_readiness.py`: Vannaka is **29/35**, hidden, with six
  exact Combat-target blockers.
- Full repository closure results are recorded in
  `memory-bank/status-updates/slayer-harpie-bug-swarm-results-2026-07-18.html`
  and its mobile-safe copy at <https://lwn2getn9lo2.postplan.dev>.
