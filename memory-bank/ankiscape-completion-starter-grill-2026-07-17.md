# AnkiScape Completion Starter Grill — 2026-07-17

Status: **starter proposal with later owner-settled Achievement/Aura/recurring/
Help/Tears decisions; cadence-reconciled 2026-07-17.** Unsettled activity
families remain design work rather than implementation-ready requirements.

This packet curates the next design program after Slayer and Summoning. It
combines a repository audit, three bounded Sol-high read-only surveys, and an
independent Fable product critique. Its purpose is to expose the few decisions
that shape the rest of the product, not to turn every remembered RuneScape page
into an immediate implementation card.

## The proposed completion line

AnkiScape should be called complete when all of the following are true:

1. All 25 pre-EOC skills have complete loops or an explicit product exclusion.
2. Every visible item, gate, unlock, reward, and help promise works end to end,
   or appears on a deliberate exclusion ledger. The item reachability audit is
   one machine-checkable part of this rule.
3. Every distinct mechanical archetype in scope has at least one complete,
   authentic representative. Examples include a temporary session economy,
   reward-currency shop, resumable Combat instance, recurring D&D, collection
   layer, degradation/repair loop, and background management system.
4. The review-pacing invariant holds across shipped content:
   `effective XP per review ∝ real pre-EOC XP per hour`.
5. The in-product Help Center explains both the supported systems and deliberate
   exclusions. A boundary hidden only in development notes is not a finished
   product boundary.

This is a **systems-complete final product**, not a small first version. It
avoids the opposite mistake of making completion synonymous with manually
rebuilding every one of roughly 2,600 source NPC combat definitions before the
product can ever finish. Long-tail instances of an already-proven archetype can
remain measured content breadth after the completion line.

Repository grounding:

- The project already rejects disconnected slices and defines the 25-skill,
  end-to-end goal in `memory-bank/projectbrief.md:7-38`.
- The product is explicitly full pre-EOC breadth translated to Anki, not a world
  simulator, in `memory-bank/productContext.md:23-36`.
- The live roadmap already sequences activities, acquisition, economy,
  collections, balance, and release after the planned skills in
  `memory-bank/roadmap.md:17-52`.
- The current reachability tool reports 1,200 action routes and 273 orphan
  inputs: 110 root and 163 cascade. This is a real closure meter, not a hand
  estimate.

## Honest current boundary

| Surface | Current truth | Why the headline can mislead |
|---|---:|---|
| Skills | 17 complete, 5 Combat-trained partial, 3 planned | The three planned skills are only one completion layer. |
| Quests | 194 runtime/catalog rows, 27 authored overrides | The other 167 are generated scaffolding, not equivalent quest fidelity. |
| Combat targets | 131 live enemy rows | This is far smaller than the source bestiary and omits many quest, Slayer, drop, and instance contexts. |
| Utility/Activities | 124 rows | These are primarily atomic conversions; they are not a reusable minigame/session engine. |
| Achievements | 168 rows | They are AnkiScape achievements, not an authentic achievement-diary system. |
| Acquisition | 1,200 routes, 273 orphan inputs | A visible recipe can still depend on an unobtainable root material. |

The exact counts above were recomputed from the current checkout on 2026-07-17.
They are snapshots; repository tools outrank this note after later changes.
The same inspection found 2,719 registered items, 626 equipment definitions,
273 runtime shops with 267 visible, 2,690 live shop-stock rows, 1,120 quest-stage
rows, and 288 quest combat encounters. Only 185 of those encounters are
resolver-ready; 103 remain statless.

These tools are not yet a complete oracle. The item reachability tables omit
some shipped action producers/consumers, including complete Farming,
Construction, Thieving, and Agility surfaces, while visible Shop rows are seeded
as reachable even when their owning skill remains planned. The live cadence
catalog now sees 2,197 selectable foreground routes: 24 rate-limited, four
embedded-probability, 131 Combat, 1,513 passthrough, and 208
`source_blocked`, plus explicit Quest/Utility/Farming/future-attachment rows. A
machine-derived readiness graph is therefore its own completion feature, not
just reporting polish.

## Architecture before content

### One narrow session substrate

Do not build one giant declarative "minigame engine." Do establish a shared
session boundary that Dungeoneering, Fight Caves, Stealing Creation, and some
activities can consume:

- one active session identity and typed family-owned state;
- optional session-scoped inventory and equipment;
- review-driven progress with no wall-clock expiry;
- atomic resume, abandon, completion, save/load, and undo;
- a clear boundary rule for what persists when the session ends; and
- a concise review result line explaining the simulated room, round, wave, or
  duty that just resolved.

Each content family still owns its actual reducer. A Fishing Trawler pressure
meter is not a reskinned Fight Cave wave, and neither should become a pile of
configuration switches.

Session suspension is source-owned rather than a blanket platform convenience.
An activity may preserve and resume an unfinished run only when the cutoff game
supported leaving and resuming that activity. Otherwise, switching away uses
the source-authentic reset, cash-out, or abandonment consequence, with a
confirmation before destructive loss. Merely viewing another page does not
invent a pause point; each activity contract must pin what counts as leaving.

All activity abstractions also follow the global computational boundary in
`memory-bank/simulation-computation-budget-contract-2026-07-17.md`. A concise
result line summarizes the complete consequential state transition; it must
never hide an unnecessary world simulation. Existing settled designs receive
the same implementation-time audit rather than being grandfathered into
unbounded or invisible work.

The owner decision rule is **faithful without overengineering**. Preserve every
source mechanic that changes requirements, agency, risk, rewards, or downstream
state. Compress spatial repetition, compulsory busywork, and object-by-object
simulation into the smallest visible action or result line that preserves those
consequences. Do not delete a real consequence merely because its source
presentation is inconvenient, and do not build a subsystem merely to reenact
presentation that creates no AnkiScape decision.

### One special-currency wallet, authentic separate balances

Use one persisted wallet/ledger substrate, but retain authentic per-activity
currencies: FoG tokens, TokKul, commendations, tickets, and so on never collapse
into generic "activity points." Reuse the existing Shop transaction, display,
and undo primitives, but present special-currency stores in an **Activity
Rewards** sub-surface and omit stock/restock behavior where it is not authentic.

### One degradation and charge substrate

FoG gauntlets, Barrows equipment, chaotics, jewellery, and other charged items
need the same persisted vocabulary:

- current and maximum charge;
- what consumes charge;
- degraded/broken transformations;
- repair, recharge, and replacement routes;
- Bank, equipment, grave, and Death's Office semantics; and
- atomic undo.

Build this before the first charged reward, rather than making every owning
activity invent another counter.

### Utility/Activities is the umbrella, not one flat data model

Keep the settled top-level product location, but give the page nested families:

- Processing;
- Skill Activities;
- Minigames;
- D&Ds;
- Activity Rewards.

Skill-owned activities remain reachable from their skill page and can also be
cross-linked from the hub. Boss instances remain Combat contexts.
Dungeoneering remains its own skill surface. The current flat deterministic
conversion model in `constants.py:350-507` is retained for Processing instead of
being stretched until every row behaves differently.

### Cutoff correction lead: generic random events

The parked minigame seed proposes injecting a generic random-event table into
every run. That is weak design even before sourcing: activities should vary
because their authentic state machines vary, not because a platform dice table
adds flavor. It is also likely inconsistent with the exact cutoff. The
remaining RuneScape random events were reportedly removed on 2012-10-24, before
the 2012-11-20 freeze:

- <https://wiki.darkan.org/Random_Event>
- <https://runescape.fandom.com/wiki/Random_events>

This is a source lead, not the final pin. Before contracting the activity
platform, resolve the dated update through the normal source hierarchy.
Recommendation: remove generic random-event injection, preserve only
source-shaped event variance inside each activity, and put legacy random events
on the explicit exclusion/nostalgia ledger.

## Dungeoneering thesis

Dungeoneering is AnkiScape's integration capstone and its renewable "fresh
account" loop. A floor repeatedly compresses the early-game experience:
starting with little, gathering and crafting under scarcity, solving gates,
improving a temporary loadout, and defeating a boss. That is more valuable than
another target list.

The source-shaped constraints are already clear:

- Daemonheim uses a closed temporary economy; its 54 Herblore targets must not
  leak into the ordinary Bank or Herblore catalog
  (`memory-bank/dungeoneering-product-decision-deferred-2026-07-13.md:3-22`).
- Floors combine rooms, keys, skill checks, combat, deaths, binds, complexity,
  prestige, tokens, rewards, and resumability
  (`memory-bank/future-work-kanban.md:366-370`).
- Dungeoneering is late because it depends on every skill and Combat, not
  because those mechanics can be flattened away.

### Recommended floor model

- **One successful review resolves one room-scale beat.** The result line can
  summarize several simulated micro-actions: "Clear the frozen room: cut the
  roots, cook the dusk eel, and defeat the forgotten ranger."
- A floor is a seeded node graph compiled at entry, with only the reachable
  frontier revealed. This preserves keys, branches, optional rooms, and routing
  without a world map.
- Casual mode chooses a sensible frontier route and temporary loadout policy.
  Advanced mode chooses the next reachable room and exact temporary inventory,
  equipment, and binds.
- "Again" advances the existing world/background clocks but does not clear a
  room. The floor neither expires nor decays.
- Only one floor can be active. Target switching freezes it; explicit Abandon
  destroys the session after confirmation.
- The critical path is generated so the player's real levels can complete it.
  Bonus rooms may exceed the player's levels and remain optional.
- Death reuses shared LP/food/death behavior, respawns the player at the floor
  start, preserves the floor, and contributes to the authentic completion
  penalty. It does not silently erase hours of study progress.
- Ordinary skill XP earned in the dungeon remains authentic. Items do not cross
  the boundary. Dungeoneering XP and tokens pay out at floor completion rather
  than per room.
- Solo is canonical. Authentic solo scaling is used; simulated 5-player parties
  and fake teammate administration are excluded unless a later multiplayer
  product is ever justified.
- Preserve authentic Complexity 1–6. Casual defaults to the highest sensible
  unlocked complexity; Advanced exposes the actual selector.
- Preserve authentic binds. Casual chooses the best owned in-session item for a
  selected combat archetype; Advanced manages exact active bind slots.
- Stage the token shop by runtime readiness. A reward appears only when earning,
  purchasing, item behavior, recharge/degradation, storage, and undo all work.

### Dungeoneering starter expedition

The smallest compelling vertical slice is not a generic XP button:

1. Frozen theme, one small solo floor band.
2. Two source-audited complexity settings spanning the low and full rulesets
   (expected to be 1 and 6) so the complexity architecture is real.
3. Seeded frontier with six room families: ordinary Combat, resource/skilling,
   skill door, key door, puzzle, and boss.
4. Session-local inventory/equipment, one bind slot, food, one resource chain,
   and one of the quarantined Herblore chains.
5. Resume, explicit abandon, death penalty, completion marks, the first
   prestige reset, Dungeoneering XP, and tokens.
6. A reward trader with only one or two fully functional period rewards.
   Prefer the Coal bag as the proof purchase if its cutoff-era cost and capacity
   revalidate: its capacity behavior already exists while acquisition is
   deliberately absent, so the slice closes a real dependency rather than
   inventing a demonstration reward.

This proves the architecture. It does not claim that one theme, boss, herb, or
reward makes the skill complete. The completion program then fills themes,
rooms, puzzles, bosses, resource tiers, binds, ring upgrades, journals/sagas,
resource-dungeon unlocks, achievements, and the period reward catalog.

## Starter activity portfolio

The portfolio is ordered by reusable architecture proven, not nostalgia.

| Order | Proof case | What it proves | Recommended review-native shape |
|---:|---|---|---|
| 0 | Flash Powder Factory / Brimhaven | In-flight Agility reference for finite skill-owned sessions and currencies | Flash Powder Factory now has a focused eight-slot contract; retain Agility ownership and finish Brimhaven through its own settled contract. |
| 1 | Tears of Guthix | Recurring D&D eligibility and dynamic lowest-skill reward | Review-clock eligibility; compact session; quest promise becomes real. |
| 2 | Shooting Stars | Timed world event, finite shared resource, contribution cap, exchange | One Mining attempt/review; simulated population also depletes the star. |
| 3 | Fist of Guthix | Bounded simulated opponent, currency, reward shop, degradation/recharge | Resumable match phases; automatic random pairing; tokens only at resolution. |
| 4 | Barrows | Multi-encounter Combat instance, chest state, repair loop, unique drops | Live six-tick Combat slices within a persistent brother/crypt/chest run. |
| 5 | Warriors' Guild | Token-metered access, armour sink, escalating defender ladder | Earn and drain tokens through review actions; repeat cyclops encounters. |
| 6 | Fight Caves | Long resumable wave instance, target priority, safe death, prestige reward | Live Combat slices inside persistent waves; explicit Leave; no timeout. |
| 7 | Fishing Trawler | Cooperative pressure system flattened for solo | Player duty plus fixed automatic public-crew pressure; persistent leaks/water/net/supplies. |
| 8 | Stealing Creation | Temporary closed economy before Dungeoneering | Gather, craft, and fight with session-only items; bounded opponent simulation. |
| 9 | Managing Miscellania | Background allocation, approval, coin sink, resource faucet | Review-clock production with explicit allocation and collection, never wall time. |
| 10 | Gnome Restaurant | Persistent order/delivery/reward chain using existing recipes | Receive, prepare, abstract-deliver, resolve, return; no duplicated Cooking data. |
| 11 | Dominion Tower | Quest-boss replay and roster growth | Persistent boss challenge context fed by playable quest completions. |

Shooting Stars retain real communal scarcity. Simulated miners may exhaust the
star before the player reaches the personal contribution cap. Cumulative crowd
arrival follows an S-curve over answered-card world ticks: sparse early
discovery, a rapid middle influx, and late saturation. The resulting active
population, together with remaining star mass, drives communal depletion.
Prompt participation is calibrated toward the source-expected opportunity;
delaying or leaving may produce only a partial reward. Each event uses the
shared naturalized-population inputs: answered-card time of day, an
event-randomized population ceiling, bounded midpoint and steepness variation,
and smooth phase jitter. Equal population profiles therefore do not produce
identical depletion rhythms while cumulative arrivals remain monotonic. Wall
time is never read.

Big Chinchompa reuses that same aggregate S-curve population pressure rather
than simulating individual hunters. Two events occur per 240-card day, each
with the source twenty-minute rational world-clock window; late entry retains
only the remaining opportunity, and either the window or communal fullness may
end it. The shared Quiet / Normal / Busy world-population profile drives both
Shooting Stars and Big Chinchompa, avoiding another activity-specific control.
One activity kernel step resolves one complete fifteen-moth jar circuit at the
highest eligible tier; multiplier stops at the event boundary, and the personal
point cap never stops continued Hunter XP. Competence rewards, the exact cutoff
shop, and per-success private-ground quota-ticket consumption are recorded in
`memory-bank/source-audits/big-chinchompa-loop-2026-07-18.md`.

Livid Farm uses its exact five-round source cycle as one finite activity group.
The source twelve-cycle/hour rate maps cleanly through the live kernel as six
cycles per five successful reviews, with the result line explicitly reporting
the occasional two-cycle emission. Each cycle atomically consumes its literal
Lunar runes and grants exact Magic, Farming, Construction, Crafting, Agility,
and Produce-point outputs without simulating plots, dialogue, or sixty-second
resets. One saved Farm routine defaults to every source duty, including
half-point/no-Magic-XP duties below level 91; a full-reward-only alternative
conserves runes without creating per-duty toggles. The pinned cycle and policy
are recorded in
`memory-bank/source-audits/livid-farm-loop-2026-07-18.md`.
The owner explicitly retained its notorious long progression as part of the
activity's identity: the full-output path remains 538 emitted cycles and 449
successful reviews, with no invented catch-up multiplier. Automatic
distractions, all cumulative spell unlocks, the complete Borrowed Power
capacitor loop, and every period wish are now specified in that focused
contract; only the named hidden rolls and two undocumented reward magnitudes
remain source-blocked.

Mage Training Arena preserves its four rooms, four Pizazz wallets, exact rune
and XP economy, bonuses, hazards, and four-column reward prices without
reproducing its spatial puzzles. A selected reward goal automatically routes
successful reviews toward the largest source-rate-normalized remaining room
workload; a direct room override remains available. Auto may switch rooms only
after a completed maze, 100 Alchemist coins, a ten-enchantment bonus, or sixteen
deposited Graveyard fruit. It never blends currencies, purchases the reward,
acquires supplies, or treats every room point as equal. The focused contract is
`memory-bank/source-audits/mage-training-arena-loop-2026-07-18.md`.

Evil Trees reuse Shooting Stars' review-clock discovery surface without its
communal-population simulation. About every twenty answered cards, a random
period tier appears directly in the D&D UI while active, even when its real
skill requirements exceed the player; the twice-per-simulated-day participation
cap remains. Its finite session preserves three visible phases—Farming nurture,
root-cutting/kindling preparation, and combined chopping/burning—without
simulating worlds, root positions, or individual fires. The focused contract is
`memory-bank/source-audits/evil-tree-loop-2026-07-18.md`.
Farming-qualified players may take the authentic nurture-only participation
when they cannot fell the drawn tier; the UI says so before entry, then awards
only the Farming action and consumes the participation without another dialog.

Phoenix Lair compresses five spatially repetitive twig caverns into one visible
aggregate Reborn-guardian front that persists through live six-tick Combat
reviews, followed by one pyre-preparation review and the standard live Phoenix
Combat encounter. The killing review lights the pyre and grants the fixed
reward atomically.
Leaving or dying resets the unfinished run without consuming its daily
completion. Rare eggs use the contextual `Clap` / `Kick` action to choose Cute
or Mean, with a remembered choice and `Clap` default; sub-72 eggs remain
source-owned items until the shared pet surface can hatch them. The focused
contract is `memory-bank/source-audits/phoenix-lair-loop-2026-07-18.md`.

Skeletal Horror is a weekly four-phase live Combat encounter. Limb thresholds
automatically pick up and bury the right arm, left arm, and tail in the same
review transaction, because ignoring them only heals the boss and creates no
useful AnkiScape choice. Bork's daily source and reward shape are pinned, but
its Ork-legion encounter remains parked behind the already-parked general
multi-enemy design rather than receiving a bespoke hidden simulator.

Troll Invasion preserves all twenty Standard or seven Hard wave markers, but a
wave is not one review. Combat uses the live kernel's six-tick review slices
against one persistent, visible aggregate wave front; clearing it advances the
source wave counter and partial-reward fraction. Repair is an automatic
one-maintenance-action passthrough that selects the most urgent of oil, ballista,
wall, and barricade work, while exposing only four condition values, morale,
and progress. Its source endpoints become 1,500 defeated trolls or a
167-eligible-review ceiling, never wall time. The focused contract is
`memory-bank/source-audits/troll-invasion-loop-2026-07-18.md`.

Jade Vine remains part of the ordinary background Farming clock. After its
health check, one saved patch policy keeps it tame through one-review prune
actions, lets it become a live six-tick Wild Vine encounter, or pays Horacio's
source produce cost and replants for another Farming cycle. The focused
contract is `memory-bank/source-audits/jade-vine-loop-2026-07-18.md`.

Vinesweeper is completely flattened rather than reproducing Minesweeper or
simulating a hidden field. Each successful review resolves one automatic
source-shaped operation and reports its point, flag, coin, Ogleroot, and Hunter
XP deltas. The source point wallet, ten-flag cap, penalties, 30 Hunter XP rabbit
repulsion, direct Farming-XP redemption, and complete cutoff reward shop remain.
Lost flags refill automatically for 500 coins, then 50 points, and the activity
pauses only when neither can pay. The focused contract is
`memory-bank/source-audits/vinesweeper-loop-2026-07-18.md`.

Fishing Trawler trips are event-scaled rather than duration-scaled. The
source twelve-minute trip becomes the count of its consequential pressure
events — leak clusters, net rips, and bailing junctures, expected on the
order of ten duty reviews — with the level-shaped haul and its 40%-rate
Fishing XP paid at trip end, scaled to preserve XP-per-review parity. The
fixed public-crew baseline, one-duty-per-review reducer, and real sinking
consequence remain as settled in
`memory-bank/source-audits/fishing-trawler-computation-reconciliation-2026-07-17.md`,
which now also records the trip-granularity decision.

Pest Control uses a shared-assault engine: the fixed competent crowd both
damages the active portal and holds pests off the Void Knight at bounded
rates, while the player's reviews are live six-tick Combat slices against the
current portal front or a defense diversion. Attested portal LP stays real —
the crowd, not rescaled numbers, closes the solo gap — losing the knight
remains a zero-reward outcome, and the zeal gate is recorded as trivially met
because reviews are always contribution. The focused record is
`memory-bank/source-audits/pest-control-game-model-2026-07-18.md`.

Fist of Guthix does not expose opponent selection or difficulty profiles. The
cutoff game paired waiting-room players randomly regardless of Combat level,
randomized the first-round roles, and swapped roles for round two. AnkiScape
therefore draws one simulated opponent from a period-shaped player population at
match entry and keeps that opponent for both rounds. Any approximation of the
population distribution must be labeled and source-audited; neither Casual nor
Advanced may choose an easier or harder rival.

The hunted role preserves its source-authentic positioning tradeoff as one
pre-round stance rather than per-review movement controls: **Centre** pursues
maximum charge gain at maximum exposure, **Hybrid** balances charging and
evasion, and **Evasive** favors houses and portals at the cost of charge gain.
Casual selects a stance from the actual matchup; Advanced selects explicitly.
The hunter role continues through the ordinary Combat equipment and style
contracts rather than creating a second FoG-only combat loadout system.

Barrows preserves its cutoff nine-room crypt as a bounded seeded graph rather
than flattening the tunnels into one navigation beat. The graph is generated
once, inactive runs perform no work, and each successful review resolves only
the current transition and encounter. Casual automatically routes toward the
central chest; Advanced chooses among currently revealed doors. The central
door puzzle is completely flattened into the successful room-transition result:
there is no puzzle UI, answer choice, failure roll, or puzzle-driven graph
reshuffle. The exact source-backed state and persistence boundary are recorded
in `memory-bank/source-audits/barrows-tunnel-session-2026-07-17.md`.

Warriors' Guild preserves its five authentic token balances and earning
activities. Casual automation rotates toward the multi-token Cyclops-room
threshold because that mode improves defender progression and keeps all five
rooms relevant; if every pool cannot currently be earned, it falls back to the
fastest viable single-token route. Advanced selects the exact earning activity
and Cyclops-room payment mode. Source values and the defender ladder are
recorded in
`memory-bank/source-audits/warriors-guild-defender-loop-2026-07-17.md`.

Gnome Restaurant keeps accepted orders persistent rather than mapping the
source six- and eleven-minute limits onto brittle one- and two-review
expirations. Each `Again` answered before delivery lowers a bounded, clamped
punctuality state that affects only eventual tip quality. It cannot destroy the
order, consume prepared food, or remove the source base points. Easy and hard
orders retain their distinct customer pools, requirements, points, and rewards;
the activity reuses player-prepared gnome food from Cooking, including eligible
items prepared and banked before assignment. The pinned structure and remaining
source work are recorded in
`memory-bank/source-audits/gnome-restaurant-delivery-loop-2026-07-17.md`.
Its source tutorial remains a one-time checklist for four prescribed dishes and
four prescribed cocktails, fulfilled through ordinary Cooking production.
Qualifying lifetime production counts retroactively, so opening the Activity
does not force an established player to remake the eight items.

Penguin Hide and Seek is deliberately flatter than its source travel and
community-hunting loop. Each answered-card week exposes the eligible penguin
roster with exact source locations. Selecting an entry starts one atomic review
action whose successful result abstracts travel, spying, and the point award;
there are no hints, searches, discovery rolls, roaming NPCs, trapping, or
community-intel modes. Quest upgrades, point values, the point cap, and
coin/chosen-skill redemption remain source-shaped. The pinned structure and
remaining source work are recorded in
`memory-bank/source-audits/penguin-hide-and-seek-loop-2026-07-17.md`.

Shattered Heart preserves strange rocks as real inventory items rather than an
invisible collection ledger. Loose rocks occupy slots and retain the source
output-replacement risk; the optional 10 kg collection bag only catches rocks
while it is actually carried. The museum exposes one instantaneous **Add all
completed pairs** command that batches XP and statue progress without consuming
a review. An opt-in **Automatically discard strange rocks** setting suppresses
future awards before inventory mutation but never deletes rocks already owned.
The pinned structure and remaining source work are recorded in
`memory-bank/source-audits/shattered-heart-loop-2026-07-17.md`.

Each Circus skill performance resolves as one atomic successful review rather
than ten or six separate reviews. The player first selects **Max XP**,
**Entertain for costume**, or **Balanced**; Casual builds the bounded source
routine, while Advanced may edit its exact lineup. The three base performances
are Magic, Ranged, and Agility. `The Firemaker's Curse` adds fire-breathing and
flaming poi, while `Some Like It Cold` adds Thieving magic tricks, producing a
three-to-six-review weekly visit. The pinned structure and remaining source work
are recorded in
`memory-bank/source-audits/circus-performance-loop-2026-07-17.md`.

Gnome Ball uses a three-review match: goals one and two, goals three and four,
then goal five with its source completion bonus and referee reward. Each review
is one bounded match slice that may report passes, misses, and tackle damage but
does not persist or simulate individual gnomes, field position, or possession.
Ordinary dangerous-activity death handling and an explicit leave abort the
match. The pinned structure and remaining source work are recorded in
`memory-bank/source-audits/gnome-ball-loop-2026-07-17.md`.

Werewolf Skullball resolves its ten-goal course in one atomic successful review.
The player chooses **Careful**, **Fast**, or **Balanced**; Advanced may provide
the exact tap/kick/shoot route. Source elapsed-time scoring becomes bounded
route-efficiency scoring derived from that choice and any sourced mistakes,
never wall-clock time, answered-card seconds, or a hidden tile simulation. The
pinned structure and remaining source work are recorded in
`memory-bank/source-audits/werewolf-skullball-loop-2026-07-17.md`.

Fish Flingers exposes no bait, hook, or weight controls in either mode. Its
source tackle-deduction game becomes a visible three-review automatic ramp:
each review catches fish while successively discovering the best bait, hook,
and weight, reaching full efficiency on the third. Each event lasts six
successful reviews, so the remaining three catches run at full efficiency and
the sixth atomically awards XP, medals, and tokens. Species/location rotation
and cooperative big-fish captures are automatic. Bounded stock and a fixed
communal pressure preserve depletion without simulating individual players.
The complete contract is recorded in
`memory-bank/source-audits/fish-flingers-loop-2026-07-17.md`.

Pyramid Plunder begins with one standing run priority: **Max XP**,
**Treasure**, or **Balanced**. It applies automatically across the run with no
per-room object controls. One successful review resolves one accessible room,
so the exact level-gated eight-room structure produces runs from one to eight
reviews. XP rushes toward the deepest urns, Treasure favors chests and
sarcophagi, and Balanced opens useful chests while emphasizing the final two
accessible rooms. The source five-minute limit becomes this finite room budget,
never wall time. Urn snakes, scarab swarms, and mummies resolve as shared
LP/poison consequences inside the triggering room review; they never launch a
separate Combat encounter, though lethal damage still ends the run through the
ordinary death/grave pipeline. The same priority controls real inventory:
Max XP discards ordinary artefacts, Balanced keeps only gold and jewelled
artefacts, and Treasure keeps every tier. Retained loot competes with supplies
until completion or a full-inventory early exit, then banks automatically;
unique sceptres and Black ibis pieces are always protected. The complete
contract is recorded in
`memory-bank/source-audits/pyramid-plunder-loop-2026-07-17.md`.

Sorceress's Garden separates **Harvest** (Fruit / Herbs / Alternate) from
**Completed juice** (Hand to Osman automatically / Keep as juice). Each
non-`Again` review resolves one garden attempt. The Activity assumes a busy
public world as scene context: the crowd provides cover on successful answers,
while `Again` is narrated as an elemental capture that returns the player to
the centre without output or damage. There is no extra catch roll, crowd
selector, stored population, or elemental simulation. Fruit is real staging inventory but
automatically squeezes at the source `5/4/3/2` threshold using an abstracted
free beer glass and the cutoff tool-belt pestle and mortar. The complete juice
can then become exact Osman XP or remain available for its boost and run-energy
effect without another review. The pinned structure, crowd abstraction, and
cutoff quest-gate conflict are recorded in
`memory-bank/source-audits/sorceress-garden-loop-2026-07-18.md`.

Entry, quest, item, ticket, and recurrence gates for the recently grilled
activity set are consolidated in
`memory-bank/source-audits/activity-entry-gate-ledger-2026-07-18.md`. Focused
activity audits remain authoritative for their loops; the ledger prevents gate
requirements from being lost between design and implementation.

Flash Powder Factory uses an eight-slot answered-card session, extended to nine
by a Rogue or Factory top. Every answered card consumes a slot: non-`Again`
answers resolve one complete reagent/catalyst/mixer circuit, while `Again`
spends the live-session opportunity without producing powder. A standing
**Max Brianpoints / Rogue equipment / Balanced** strategy controls charge,
rubble, and apparatus priorities. Pickpocketing survives only as at most one
visible apparatus contest inside a productive review; no opponents, paths, or
population are simulated. The full contract is recorded in
`memory-bank/source-audits/flash-powder-factory-loop-2026-07-18.md`.

The Pit invitation applies to nine of the eleven ordinary live lap-course
variants: Gnome and Barbarian basic/advanced, Pyramid, Ape Atoll, Wilderness,
Werewolf, and Dorgesh-Kaan. Burthorpe and Penguin cannot trigger it. One global
**Automatically accept Talent Scout invitations** checkbox is checked by
default and behaves identically in Casual and Advanced; unchecked offers remain
available for manual acceptance or decline. The focused contract and current
implementation mismatches are recorded in
`memory-bank/source-audits/the-pit-loop-2026-07-18.md`.

The Pit reward is the first contextual reviewer action. **Take XP / Gamble**
appears in one shared row above the XP/LP HUD with one answered-card grace
period; ignoring it uses the last explicitly clicked valid Pit choice or the
conservative `Take XP` default inside the next review's undo transaction. This
creates no auto-gamble checkbox and no Casual/Advanced split. The reusable
contract and later candidate-harvest boundary are recorded in
`memory-bank/review-hud-context-actions-contract-2026-07-18.md`.

Managing Miscellania preserves the source's unusual retroactive allocation
rule. Answered-card days accumulate only funded, approval-weighted production
credit; the current subject distribution converts the entire unclaimed pool
into source-shaped resources and bonus rolls when **Collect** is clicked. No
resource-by-resource background simulation runs. Approval, coffer funding,
worker allocation, reward preview, and collection share one bespoke Activity
management panel rather than generic target rows. The focused contract is
`memory-bank/source-audits/managing-miscellania-loop-2026-07-18.md`.
Approval is restored through one **Help the subjects** review target with a
saved source-chore dropdown shared across both UI modes. A successful review
performs the selected eligible chore and grants its small source-shaped skill
XP and approval opportunity; unrelated reviews never maintain approval for
free.
The coffer never draws from the Bank automatically. One-day, seven-day,
thirty-day, maximum, and exact deposit/withdraw controls calculate convenient
explicit transfers from the source salary formula; underfunding simply reduces
or stops production credit.
Worker allocation preserves individual subject counts: one row per source
resource family with decrement, increment, **Max**, and visible pips; ten
subjects expand to fifteen after `Royal Trouble`, while the per-family cap
remains ten. The allocation persists, immediately refreshes the retroactive
collection preview, and has no mode split or speculative profit optimizer.

The architecture wave is Tears, Shooting Stars, FoG, Barrows, Fight Caves, and
Stealing Creation. The others validate additional families rather than blocking
the shared substrate.

### Wider family ledger

Design coverage should name the broader trees even when they are not first:

- **Skill-owned activities:** Artisan's Workshop, Blast Furnace, Runespan,
  Beacon Network, Bonfires/fire spirits, Habitat/Jadinkos, Livid Farm, Mage
  Training Arena, Rogues' Den, Sorceress's Garden, Pyramid Plunder, Flash Powder
  Factory, Brimhaven, Fish Flingers, and Gnome Restaurant.
- **Cooperative/simulated-population:** Pest Control, Barbarian Assault, Fishing
  Trawler, Trouble Brewing, Shades of Mort'ton, Temple Trekking. Scope settled
  2026-07-18: all receive solo adaptations. Temple Trekking and Shades of
  Mort'ton are (near-)solo in the period game and need no crew simulation;
  Pest Control reuses the Trawler pattern of a fixed competent crowd offset
  around the player's own duty; Barbarian Assault adapts as one role per wave
  with a simulated competent team; Trouble Brewing, the owner's deliberate
  breadth call past the individual-agency bar, adapts last with a bounded
  opposing-team pressure model. Each still requires its own contract and
  source audit before implementation.
- **Competitive:** Fist of Guthix, Great Orb Project, Stealing Creation, Castle
  Wars, Soul Wars, Conquest, Clan Wars, Duel Arena, and Mobilising Armies.
  Only content with meaningful individual agency under a bounded opponent model
  should receive a solo adaptation; intrinsically social siblings remain parked.
- **Recurring D&Ds:** Tears of Guthix, Familiarisation, Shooting Stars, Evil
  Tree, Penguin Hide and Seek, Circus, Shattered Heart/strange rocks, Troll
  Invasion, Big Chinchompa, Skeletal Horror, Bork, Phoenix, and Jade Vine.
- **Combat instances and encounter contexts:** Barrows, Fight Caves/Kiln,
  God Wars, Corporeal Beast, Nex, Dominion Tower, Warriors' Guild, quest bosses,
  and minigame enemies.
- **Persistent management:** Managing Miscellania and other source-authentic
  background allocation/collection systems.

Every name still requires cutoff and source verification before its own
contract. This ledger prevents forgotten trees; it is not evidence that every
named activity is period-valid or implementation-ready.

## Forgotten or under-owned feature trees

### Must close

1. **Canonical completion/readiness graph.** Every quest, enemy variant,
   activity, item, reward, shop row, and collection entry needs distinct
   machine-derived states for catalogued, source-closed, runtime-complete,
   obtainable, UI-visible, tested, and release-certified. Generate numeric
   Kanban summaries from this graph so metadata cannot masquerade as gameplay.
2. **Shared search and filters.** One reusable Qt component is already settled
   for Combat, Slayer-task filtering, Help, Bank, quests, achievements, and
   other large catalogs (`future-work-kanban.md:420-445`).
3. **Offline Help Center and contextual `?`.** The architecture is settled and
   should move forward before the interface becomes still denser
   (`help-system-contract-2026-07-16.md:12-82`).
4. **Reward currencies and reward shops.** They are a cross-program substrate,
   not one FoG implementation detail.
5. **Equipment charges, degradation, repair, and recharge.** FoG, Barrows,
   chaotics, jewellery, and several existing deferred items depend on it.
6. **Skill capes and level-99 recognition.** Seventeen complete skill surfaces
   can reach the milestone; the final product needs the authentic master
   purchase and trim progression.
7. **Warriors' Guild and defenders.** This is a core melee equipment progression
   route with no current owning card.
8. **Quest promise audit.** Generated quest unlock text can promise activities
   that do not exist. Play UI and reference catalog need an honest separation.
9. **Charm-bearing bestiary breadth.** Summoning needs source-authentic charm
   acquisition across useful level bands, not only a pouch-production UI.
10. **Acquisition and item-use closure.** Reachability, drop tables, ground
   spawns, services, quests, charges, specials, poison, set effects, and
   consumables are one dependency graph.

### Representative-breadth trees

- authentic region diary tasks and rewards;
- clue scroll steps, caskets, and reward tables;
- passive collection layers such as strange rocks;
- miniquests and Dungeoneering sagas;
- resource dungeons and other Dungeoneering surface unlocks;
- quest-boss replay;
- alternate skilling activities;
- recurring D&D cadence families; and
- full enemy/drop/context ingestion after live dependency classes are closed.

### Deliberate exclusion or parked ledger

- persistent world map and standalone transportation;
- full multiplayer, clans, house parties, social trading, and intrinsically
  social competitive modes;
- random events removed before the exact cutoff, pending final source pin;
- Squeal of Fortune and Solomon's Store lootbox/cosmetic commerce;
- Loyalty Programme acquisition as a literal subscription-tenure simulation;
- holiday calendars, general emotes, and titles unless a later cosmetic pass
  finds a compelling review-native reason. Music unlocks are no longer
  excluded: `memory-bank/achievement-diary-item-grants-design.md` now defines
  the passive Music Log required by the cutoff Completionist contract;
- post-cutoff and OSRS-only substitutions; and
- visible inert previews.

Gameplay-affecting auras need a separate policy decision: exclude them, grant
them through transparent AnkiScape milestones as a labeled invention, or expose
them as optional account entitlements. Do not silently turn a period
subscription benefit into a free shop item.

## Release-only closure

These are not reasons to delay the design work, but they are part of the final
product rather than an afterthought:

1. **Save portability and recovery:** golden migration fixtures for every
   supported config version; idempotent upgrades; safe handling of partial or
   corrupt state; independent export, validation, import, and restore.
2. **Reproducible packaging and licensing:** one build command that validates
   bundled assets, provenance/licenses, excluded development files, clean-profile
   installation, versioning, checksums, and release notes.
3. **Performance and accessibility:** startup and page-open budgets against
   large real saves; keyboard navigation; light/dark contrast; supported Anki
   and Python/Qt matrix.
4. **Semantic documentation:** mechanical documentation audits stay necessary,
   but the Help corpus and release notes must also be checked against current
   runtime behavior rather than merely for valid links and HTML.
5. **Product disposition — settled 2026-07-17:** prepare a distinctly named
   public derivative release, with upload still gated by the licensing,
   attribution, asset-provenance, packaging, and verification sequence in
   `public-release-lineage-and-license-2026-07-17.md`.

## Morning decision queue

The HTML companion presents these as selectable cards. Review them in order;
later answers assume earlier architecture.

### A. Define the finish line

1. **Completion rule**
   - A: enumerate every quest, NPC, activity, and item before completion.
   - B: use the five closure rules in this packet. **Recommended.**
   - C: use the closure rules plus mandate collapsed playability for all 194
     quests.
2. **Quest and bestiary breadth**
   - A: keep "every attackable NPC / every quest" as a blocking manual program.
   - B: close live demand classes and archetypes, measure the long tail as
     post-completion breadth. **Recommended.**
   - C: all quests are collapsed-playable, but only demand-class NPCs block.
3. **Exclusion ledger**
   - A: development notes only.
   - B: a player-visible Help Center topic with the reason and nearest supported
     abstraction. **Recommended.**

### B. Decide shared platform primitives

4. **Activity placement**
   - A: one flat Utility list.
   - B: Utility/Activities umbrella with nested families; skill activities,
     Combat instances, and Dungeoneering retain ownership. **Recommended.**
   - C: a new top-level Minigames tab.
5. **Currency and shops**
   - A: generic activity points.
   - B: authentic separate balances on one wallet; shared Shop backend with an
     Activity Rewards surface. **Recommended.**
   - C: bespoke currencies and shops per activity.
6. **Session state**
   - A: every activity owns everything.
   - B: a narrow shared session boundary plus family-owned reducers.
     **Recommended.**
   - C: one giant configurable minigame engine.
7. **Review-cost grammar**
   - A: entry costs a review.
   - B: entry/selection is free; every meaningful room, round, wave, or duty
     consumes the review that resolves it. **Recommended.**
   - C: bespoke per activity.
8. **Charged equipment**
   - A: ad hoc counters.
   - B: one shared degradation/repair/recharge substrate before FoG or Barrows.
     **Recommended.**
9. **Multiplayer adaptation**
   - A: park all multiplayer-shaped content.
   - B: allow bounded, labeled opponent/crew simulations only when individual
     agency survives; park intrinsically social modes. **Recommended.**
   - C: generic party-size multipliers.
10. **Generic random events**
    - A: inject them into every activity.
    - B: remove the generic layer; model only authentic activity variance and
      record legacy randoms as excluded/nostalgia content. **Recommended.**

### C. Ratify the starter portfolio

11. **Architecture proof set**
    - A: the ranked portfolio in this packet. **Recommended.**
    - B: move Stealing Creation immediately after FoG to bias toward
      Dungeoneering.
    - C: cut the first architecture wave to Tears, FoG, Barrows, Fight Caves,
      and Stealing Creation.
12. **XP-multiplying rewards**
    - A: ship source values immediately.
    - B: keep their shop rows hidden until the global cadence invariant can
      account for them. **Recommended.**
    - C: invent compensating reductions now.

### D. Close Dungeoneering's consequential forks

13. **Floor unit**
    - A: fixed review counter.
    - B: seeded room graph, one room-scale beat per successful review.
      **Recommended.**
    - C: boss-only floor.
14. **Solo/party**
    - A: authentic solo as canonical; park party simulation. **Recommended.**
    - B: simulated party profiles.
    - C: generic difficulty multiplier labeled as party size.
15. **Persistence and death**
    - A: indefinite resume; death penalizes completion but does not erase the
      floor. **Recommended.**
    - B: world-clock expiry.
    - C: death or target switch abandons the floor.
16. **Skill XP and cadence**
    - A: authentic ordinary skill XP inside Daemonheim, with cadence calibrated
      so it does not erase overworld methods. **Recommended.**
    - B: Dungeoneering XP only.
17. **Complexity, binds, and critical path**
    - A: preserve authentic complexity and binds; Casual automates; Advanced
      selects; critical path is always level-feasible. **Recommended.**
    - B: Complexity 6 and automatic best binds only.
    - C: remove complexity and binds.
18. **Reward staging**
    - A: expose the whole period shop immediately.
    - B: expose only fully functional reward rows, with the first existing
      cross-system dependency as the proof purchase. **Recommended.**

### E. Resolve two large leftover forks

19. **Achievement diaries**
    - A: fabricated achievements grant authentic diary gear by percentage.
    - B: implement every literal regional diary.
    - C: curate period-authentic tasks AnkiScape can genuinely express and hang
      the authentic reward ladder on them. **Recommended.**
20. **Period account-meta and monetization**
    - A: exclude Squeal, Solomon's, and Loyalty wholesale.
    - B: exclude lootbox/cosmetic commerce; translate gameplay auras to
      transparent AnkiScape milestones, labeled as invention. **Recommended.**
    - C: optional entitlement toggles for every period account benefit.

## Natural stopping point

The next design session should answer questions 1–10 before drilling individual
activities. Those ten choices decide the completion contract and platform. The
portfolio can then be ratified as a batch, followed by the eight Dungeoneering
forks. Nothing in this proposal authorizes implementation; accepted decisions
should be copied into owning contracts and source audits before code begins.
