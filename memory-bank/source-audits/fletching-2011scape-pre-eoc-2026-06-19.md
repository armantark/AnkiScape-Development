# Fletching 2011Scape + Pre-EOC Audit (2026-06-19)

## Scope

Fletching was audited against the local 2011Scape rev 667 source first, then
pinned 2011 knowledge-base pages for bolt-tip and dart deltas that are
historically live Fletching actions but not fully represented by local plugin
bindings.

Primary implementation file: `fletching_data.py`.

## Local 2011Scape Sources

- `gg/rsmod/plugins/content/skills/fletching/whittling/WhittleItem.kt`
- `gg/rsmod/plugins/content/skills/fletching/whittling/LogData.kt`
- `gg/rsmod/plugins/content/skills/fletching/whittling/WhittleAction.kt`
- `gg/rsmod/plugins/content/skills/fletching/stringing/BowItem.kt`
- `gg/rsmod/plugins/content/skills/fletching/stringing/StringData.kt`
- `gg/rsmod/plugins/content/skills/fletching/stringing/BowStringAction.kt`
- `gg/rsmod/plugins/content/skills/fletching/feathering/FeatheringData.kt`
- `gg/rsmod/plugins/content/skills/fletching/feathering/FeatherAction.kt`
- `gg/rsmod/plugins/content/skills/fletching/arrows/ArrowData.kt`
- `gg/rsmod/plugins/content/skills/fletching/arrows/ArrowAction.kt`
- `gg/rsmod/plugins/content/inter/slayer/slayer_rewards.plugin.kts`
- `gg/rsmod/plugins/api/cfg/Items.kt`
- `data/cfg/items.yml`

## Implemented Source Rows

Whittling:

- Normal logs produce `Arrow shafts` x15 at level 1 for 5.0 XP.
- Normal/oak/willow/maple/yew/magic logs produce unstrung shortbows and longbows
  at the source levels and XP.
- Normal/oak/willow/teak/maple/mahogany/yew logs produce crossbow stocks.
- Achey tree logs produce `Ogre arrow shaft` and `Unstrung comp bow`.

Stringing:

- Finished shortbows and longbows are implemented for normal/oak/willow/maple/
  yew/magic.
- `COMP_OGRE_BOW` remains excluded because it is commented out in `StringData.kt`.

Feathering:

- Headless arrows use 15 shafts and 15 feathers for 15.0 XP.
- Flighted ogre arrows use 6 ogre arrow shafts and 24 feathers for 5.4 XP.
- Bronze through runite bolts and broad bolts use 10 unfinished bolts and 10
  feathers per action.
- Bronze through dragon darts use 10 dart tips and 10 feathers per action.

Arrows:

- Bronze, iron, steel, mithril, broad, adamant, rune, and dragon arrows use 15
  headless arrows and 15 tips/heads per action.
- Broad arrows and broad bolts require the Slayer `BROAD_FLETCHING` ability.

## Pinned Pre-EOC Deltas

The 2011 knowledge-base pages used as pinned evidence:

- `https://www.2011.rs/kb/fletching_making_bolts`
- `https://www.2011.rs/kb/fletching_making_darts`
- `https://www.2011.rs/kb/fletching_making_arrows`
- `https://www.2011.rs/kb/fletching_making_bows`
- `https://www.2011.rs/kb/fletching_making_crossbows`

Gem/pearl bolt-tip cutting and bolt tipping are included from the 2011 bolts
page. Enchanted bolts remain Magic-owned and are not Fletching rows.

Mithril grapple attachment is included from the same pinned bolt table. Crossbow
limb attachment and crossbow stringing remain deferred because the local
Fletching plugin does not expose a live action binding for those steps.

The darts page states that Tourist Trap is required to smith dart tips, while
adding feathers to premade dart tips can be done without the quest. Fletching
therefore does not gate dart feathering on Tourist Trap in this pass.

## Explicit Corrections From The Old Pilot

- Tiered arrow-shaft rows for oak/willow/maple/yew/magic/redwood are removed.
  The local source only binds normal logs to arrow shafts.
- Common reusable tools stay ambient. `WhittleAction.kt` checks a knife, but
  knives, chisels, needles, hammers, and moulds are not progression-bearing
  toolbelt items in AnkiScape.
- Missing inputs remain ordinary material locks. Real historical permissions
  use target unlock rules.

## Unlocks

- `broad_fletching`: required for broad arrows and broad bolts. Evidence lives
  in `slayer_rewards.plugin.kts`, where Broad Fletching is a Slayer reward and
  maps to the broad ammo reward shop.
- `barbarian_fishing`: added as a generic ability gate for leaping fish, based
  on the local Fishing runtime's Barbarian Fishing permission reference.

Ability acquisition is not implemented in this pass; locked rows remain visible
and disabled until the flat `unlocked_abilities` state contains the ability id.
