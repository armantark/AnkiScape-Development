# Clan Wars Horizontal Implementation Source Audit

Date: 2026-07-26

## Scope decision

This family implements the two free-for-all portals and a bounded team-score
race. The portal set and the red portal's consequences follow the settled
answer in `memory-bank/design-thread-queue.md` section 4.3.

The interrupted commit `711a87c8` cited Darkan `FFAController.java`,
`Potions.kt`, and OpenRS2 object definitions `38698`, `38699`, `38700`,
`49255`, and `49256` in `CLAN_WARS_SOURCE`. This pass read those sources.
Two of the five object IDs are real; three could not be found anywhere in the
Darkan tree, so the citation string was rewritten to name only what was
actually read. That correction is the reason this audit exists in its current
form.

## Sources in required order

### 1. Darkan

- repository:
  `/Users/ArmanTarkhanian1/Documents/2012scape with bots/darkan-world-server`
- commit: `d14face35aa5c851b7d3c48df79f619ef399a366`
- controller:
  `src/main/java/com/rs/game/content/minigames/clanwars/FFAController.java`
- boost clamp: `src/main/java/com/rs/game/content/Potions.kt`,
  `checkPVPPotionBoosts`
- death handling: `src/main/java/com/rs/game/model/entity/player/Player.java`,
  `sendPVPItemsOnDeath`
- comparison controller:
  `src/main/java/com/rs/game/content/minigames/crucible/CrucibleController.java`

Sourced facts harvested:

- Two portal objects exist, `38698` and `38699`. `38699` sets varbit `5279` to
  `1` and constructs `FFAController(dangerous = true)`; `38698` is the safe
  one. Object IDs `38700`, `49255`, and `49256` appear nowhere in the tree and
  are not carried into the code or this audit.
- Entering the dangerous portal calls `Potion.checkPVPPotionBoosts(player)` and
  adds `Effect.OVERLOAD_PVP_REDUCTION`. The safe portal does neither.
- `checkPVPPotionBoosts` lowers each boosted skill to
  `base + flat + base * multiplier` with `(5, 0.15)` for Attack, Strength and
  Defence, `(5, 0.1)` for Ranged, and `(5, 0.0)` for Magic, and messages
  "Your extreme potion bonus has been reduced."
- `FFAController.sendDeath` calls `player.sendPVPItemsOnDeath(killer)` **only**
  when `dangerous`. A safe death does no item handling at all.
- `sendPVPItemsOnDeath` clears equipment and inventory and hands the items to
  the killer's ground pile. It creates no gravestone and no Death's Office
  entry. The kept count is three when unskulled, plus one more while Protect
  Item is active.
- `CrucibleController` calls the identical `checkPVPPotionBoosts` and
  `sendPVPItemsOnDeath` pair, which confirms the owner's instruction that the
  red portal reuses the Crucible's dangerous-death path rather than a new one.
- The `clanwars` package contains `FFAController.java` and nothing else. There
  is **no** clan-versus-clan or team-battle controller in this tree, so the
  purple team race has no server-side model here.

### 2. Pinned historical wiki

- Clan Wars: `https://runescape.wiki/w/Clan_Wars?oldid=6288405`
  - revision timestamp: `2012-09-24T05:10:06Z`
  - this is the revision the owner recorded when answering design decision 4.3

### 3. Asset provenance

`tools/fetch_clan_wars_assets.py` installs `activityicons/clan_wars.png` from
`File:Clan wars portal.png`. The recorded upload timestamp is
`2011-11-19T06:16:44Z`, inside the period, and the entry is in
`assets_provenance.json`.

## Sourced facts implemented

- Both portals ship as explicit modes; exactly one of them is dangerous.
- The dangerous portal clamps boosted Attack, Strength, Defence, Ranged and
  Magic on entry using the exact Darkan formula and reports the reduction.
- A dangerous death destroys carried and worn items, writes **no** gravestone
  and **no** Death's Office entry, and Protect Item saves the single
  highest-value item. `logic_pure_combat_model._combat_apply_pvm_death` gained
  a `no_grave` mode for this; the default grave-writing behaviour every other
  caller relies on is unchanged.
- A safe-portal death costs nothing but a point.
- Teleport escape is refused inside the red portal.

## AnkiScape abstractions

These are product mechanics, disclosed as such, and claim nothing about period
rates:

- one bounded match is eight successful reviews of six combat ticks each;
- one simulated rival at a time, drawn from a player-relative
  `(-6, +2, +8)` combat-level cycle clamped to levels `3` through `138`;
- **crossfire**, the model for the rest of the arena. Each review the engaged
  rival loses `maximum_lifepoints // 3`, and from review `3` onward the player
  loses `maximum_lifepoints // 6`. Without it a match could only ever end
  `0-0`: measured across levels 10 to 99, the player could not kill a rival
  before the review bound and could not be killed by one, so `win`, `loss`,
  `kill` and `death` were all unreachable and the red portal's entire
  consequence was dead code. Crossfire is the same disclosed device TzHaar
  Fight Pit ships as roster attrition plus late-round pressure.
- The player-side crossfire is floored at one lifepoint and can never kill.
  That is deliberate: the red portal must have exactly one death path, the
  combat burst, because that is the path that destroys items.
- In the free-for-all portals a rival that falls to crossfire was finished by a
  stranger and scores against the player. In the purple team battle the
  surrounding combatants are clan mates, so the same kill scores for the
  player. The opposing clan scores once every three reviews. See the design
  fork recorded in `memory-bank/design-thread-queue.md`.

## Deliberately not implemented

- No loot from a rival kill. A period red-portal kill let the victor take the
  victim's items, but the rivals here are simulated and hold nothing, and
  inventing a drop table for them would be inventing content. Combat
  experience is the family's real reward.
- The interrupted commit shipped a three-way `balanced` / `pressure` /
  `survival` combat-policy dial with `1.0` / `1.12` / `0.88` damage
  multipliers. It has been removed. Nothing in either source supports a
  strategy selector, the descriptions promised a defence trade that was never
  implemented, and `survival` was therefore strictly worse than `balanced`
  with no compensating benefit. The portal choice is the family's policy
  surface.

## Placeholder register

None. The one value this pass was ready to register as a placeholder, the red
portal's boost caps, turned out to be exactly recoverable from Darkan, so it
ships as an exact sourced value with a test pinning the literals.

## Data depth deferred

- The real free-for-all crowd size, respawn cadence and kill rates.
- Any period scoring or reward for the team battle, which needs a source this
  tree does not contain.
- Rival equipment, loadouts and combat styles beyond a melee rival scaled from
  the player's combat level.
