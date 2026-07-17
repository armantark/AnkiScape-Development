# Summoning pet acquisition source audit (2026-07-16)

Scope: give every pre-EOC pet an authentic acquisition owner and a discoverable
AnkiScape route without creating a generic pet-vending system. Cutoff is
2012-11-20.

## Primary period evidence

**Pet**, oldid
[6579897](https://runescape.wiki/w/Pet?oldid=6579897),
2012-11-19 05:28:42 UTC. Its literal wikitext contains both the Summoning-pet
and non-Summoning-pet tables, including level/quest requirements, stages, food,
the acquisition family, and colour count. Individual acquisition pages still
need their own pre-cutoff pins for exact prices, token costs, XP, hidden catch
or drop rates, incubation durations, repeatability, and colour-selection rules.

Repository reconciliation:

- `woodcutting_data.py:140-197` already gives bird nests a `1 / 257` drop roll,
  includes Zamorak, Guthix, and Saradomin egg nests at weight `1` each, and
  opens each into the corresponding bird egg. Those eggs are dead-end
  materials until pet incubation exists. Raven egg acquisition is still
  absent.
- `hunter_data.py` has no gecko, platypus, squirrel, raccoon, monkey, or pet
  Broav route.
- `quest_catalog_generated.py:5787-5818` already records the Gertrude's Cat
  kitten reward as `Kitten`, while focused quest item metadata uses
  `Pet kitten` at `quest_data.py:8028`. Implementation must reconcile these
  identities into one stable pet entity instead of granting two differently
  named items.
- `shop_data.py` already has Taverley and Yanille Pet Shop records, but their
  stock is limited to Summoning supplies/food and exposes no dog-grant service.
  Harry's Fishing Shop likewise exists without its pet-fish service. Acquisition
  should extend these owners rather than add duplicate shops.
- Construction already parks its Menagerie behavior on the future pet system;
  its clockwork-cat Workshop route must become a real pet grant rather than an
  orphaned build output.

## Acquisition ownership matrix

The Pet page closes which system owns the route. It does not close every
numeric parameter inside that route.

| Owning system | Pets | AnkiScape route |
|---|---|---|
| NPC pet shops | Bulldog, Dalmatian, Greyhound, Labrador, Sheepdog, Terrier | Ordinary NPC-shop/service entries with the sourced Summoning gate, price, stock, and colour choice. |
| Harry's Fishing Shop | Pet fish | Harry-owned service or shop action, after pinning the period procedure; never a generic Pets-page purchase. |
| Quest reward/NPC follow-up | Rune guardian, Tooth creature, Ex-ex-parrot, Cat/kitten, Pet rock, Searing Flame/Glowing Ember/Twisted Firestarter/Warming Flame, Baby troll | The quest stage or its named post-quest NPC grants the pet entity. Repeat claims, payments, and variants follow that pet's individual source. |
| Quest transformation | Hellcat/hellkitten | Recipe for Disaster: Freeing Evil Dave transforms the owned cat entity; it does not mint a parallel generic pet. |
| Hunter | Gecko, Platypus, Squirrel, Raccoon, Monkey | Normal Hunter targets with exact Hunter/Summoning/quest gates, tools, bait, XP, and success behavior. The catch awards the pet entity. |
| Quest-owned Hunter action | Broav | While Guthix Sleeps stage action, not a repeatable generic Hunter target unless its individual period source proves repeatability. |
| Item/token exchange | Giant crab | Exchange the sourced crunchy claw token after the Pirate Pete subquest. |
| Nest/drop/found egg plus hatch route | Raven, Saradomin owl, Guthix raptor, Zamorak hawk, Penguin, Vulture, Chameleon, Baby dragons | The owning source awards the exact egg: Woodcutting nest, NPC/zoo interaction, monster drop, or found-world action. The per-pet source then determines pet-shop incubation, NPC hatching, or another hatch surface; these must not be flattened into one invented procedure. |
| Phoenix Lair D&D | Cute and Mean phoenix egglings | Phoenix Lair reward/hatch flow after In Pyre Need, using the activity's own cadence and choice rules. |
| Soul Wars rewards | Creeping hand, Minitrice, Baby basilisk, Baby kurask, Abyssal minion, TzRek-Jad | Soul Wars reward shop with the sourced Slayer/Summoning gates, zeal cost, and any item sacrifice. |
| Dungeoneering rewards | Sneakerpeeper spawn | Dungeoneering reward shop for the sourced token cost; the overworld pet remains separate from Daemonheim session inventory. |
| Slayer co-op rewards | Freezy, Baby aquanite | Slayer co-op reward shop with the sourced co-op-point cost. |
| Construction Workshop | Clockwork cat | Existing Construction action family creates the pet entity with exact materials, level, and quest gate. |
| Discontinued events | Sparkles, Eek, Mackers | No new-save acquisition route existed at the freeze. Their data may be retained for historical/save compatibility, but AnkiScape must not invent a replay, shop, or random grant. Main-log visibility remains an owner decision. |

## Final-product architecture

One future `pet_data.py` catalog owns pet identity and lifecycle. Every row must
carry stable `pet_id`, stages, compatible food, colour variants, Summoning and
cross-system gates, exceptional functions, and a typed `acquisition_route`:

- `owner_kind` and stable owner id (quest, Hunter target, shop/service,
  Construction target, combat drop, nest table, activity reward, or legacy
  entitlement);
- exact grant point and whether it is repeatable;
- required skills, quests, items, and currencies;
- selection versus random colour/variant behavior;
- reclaim/replacement route when period evidence provides one; and
- source state for every exact price, rate, XP value, timer, and cost.

The catalog never mints a pet. The owning quest, target, shop, drop table, or
activity performs one atomic, undo-safe grant into the shared pet-entity store.
This prevents duplicate identity between inventory items, Bank rows, active
followers, and Menagerie residents.

The canonical follower surface gains a searchable **Pets** log. It projects the
same catalog and shows owned state, current growth stage, compatible food, and
one plain acquisition line such as `Obtained from Hunter`, `Gertrude after
Gertrude's Cat`, or `Soul Wars reward`. A source action may navigate to the
owning skill/shop/quest/activity when that surface exists, but the log never
buys, rolls, catches, or grants a pet itself. It should use the future shared
page-search component rather than another one-off search implementation.

### Egg and incubation state

An egg remains an ordinary source-owned item until deposited into its
period-correct hatch surface. Where a pet-shop incubator is sourced, depositing
the egg starts a persistent incubation record whose duration advances only on
the global answered-card clock, never wall time. Completion makes the pet
collectable; the source audit already establishes that an incubated pet may
remain safely uncollected. Direct-hatch and activity-owned egglings use their
own source flow instead of being forced through the pet-shop incubator.

### Quest cats

Gertrude's Cat must grant one real kitten entity, and the sourced post-quest
Gertrude replacement route must produce the same entity type. Cat-dependent
quests inspect that entity's colour/stage/state and use it through the follower
slot only where the sourced step needs an active cat. Hellcat conversion mutates
the entity and preserves ownership/growth identity. No quest relies on a
free-floating `Kitten` versus `Pet kitten` string mismatch.

## Explicitly unresolved numeric harvest

The route exists even when one of these exact parameters remains
`source_blocked`; implementation may not guess it:

- pet-shop and service prices, stock, and replacement prices;
- Soul Wars zeal, Slayer co-op points, Dungeoneering tokens, crunchy claw
  exchange, sacrifices, and repeatability;
- Hunter XP, tools/bait, success rolls, and repeat-catch rules for each pet;
- raven nest weight and all vulture/chromatic-dragon egg drop rates;
- each egg's exact hatch surface and incubation duration;
- quest/post-quest replacement costs and eligibility;
- colour choice versus random roll; and
- whether a one-time pet has any period reclaim route.

## Open owner fork: legacy event visibility

Sparkles, Eek, and Mackers existed as pets at the freeze but their acquisition
events had ended. The recommended boundary is to retain their stable definitions
for historical completeness and legacy-state safety while excluding them from
the main obtainable Pets log and every completion count. Showing impossible
empty rows would turn authenticity into a permanently unfinishable collection.
