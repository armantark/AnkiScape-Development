# Design-thread queue

Status: **live queue. This file has no date. It is the one address for design
decisions that block implementation.**

## 1. Goal

The implementation sessions ship only what needs no design decision. When a
session finds a decision that the owner must make, it stops that family and adds
the decision here. The owner reads this file in the design thread and answers.

Dated records are snapshots. A reader must know the date to find them, and four
decisions stayed open for six days because of that. This file replaces the search
with one path.

## 2. Rules

1. Add one section for each decision. Give it the next number.
2. State the conflict, the options, and your recommendation. The owner must be
   able to decide without opening another file.
3. Give the exact paths of the records that disagree.
4. Name what the decision blocks. An unblocked decision can wait; a blocked
   family cannot.
5. Move a decision to section 4 when the owner answers. Keep the answer.
6. Never guess an answer to clear a row. A recorded decision is a success. An
   invented mechanic is a defect.

## 3. Open decisions

### 3.1 Skeletal Horror wish lists are satisfied by a free button click

Raised 2026-07-26 during adversarial verification of the Skeletal Horror family.

The period gate is the Rag and Bone Man and Fur 'n Seek **post-quest wish
lists**, not the quests themselves. In the period game each wish list is a long
bone-collection errand. AnkiScape has no wish-list state, because
`memory-bank/source-audits/skeletal-horror-implementation-harvest-2026-07-19.md`
assigns that restoration to the Darkan quest-parity thread.

The shipped family stands in two commands, `complete_rag_wish_list` and
`complete_fur_wish_list`, stored on the Skeletal Horror state. They correctly
require the parent quest and Slayer 78, so the gate's *shape* is faithful, but
the wish lists themselves cost the player nothing beyond one button press.

Options:

- **A. Keep the stand-in** (recommended, and what is implemented). The gate
  keeps its authentic prerequisites and the boss is reachable now. The button is
  a placeholder for state the quest program will own.
- **B. Block the family** until the quest program persists real wish-list
  completion. Faithful, but parks a mechanically complete boss indefinitely on
  another thread's schedule.
- **C. Invent a bone-collection errand inside this family.** Rejected: it would
  duplicate the quest program and invent content whose period shape we have not
  harvested.

Records that disagree: the harvest audit calls this dependency-blocked; the
shipped code treats it as satisfiable. Blocks: nothing today under option A.
### 3.2 Clan Wars purple portal — who gets a crossfire kill?

Answering 4.3 settled both free-for-all portals but left the purple team battle
as "the settled bounded team-score race", and Darkan has no clan-versus-clan
controller to read (only `FFAController.java`), so nothing settles this.

Clan Wars matches are decided by a crossfire model: the rival the player is
fighting is also being worn down by the rest of the arena, and someone
eventually lands its killing blow. In the two free-for-all portals that someone
is a stranger, so the kill scores against the player. The purple portal is the
question: in a clan-versus-clan battle, the combatants around the player are
clan mates.

- **Option A (implemented).** A crossfire kill in the purple portal scores for
  the player's clan, and the opposing clan scores once every three reviews.
  This gives the team battle a mechanic the free-for-all does not have, and it
  is the only reading under which a purple win is reachable at all.
- **Option B.** Purple behaves exactly like the white portal, and its team
  identity is cosmetic. Under this reading the player is the only source of
  their clan's score, and a purple win was never observed in 400 simulated
  matches at any combat level.

Recommendation and current behaviour: **Option A**. Option B makes the purple
portal's win outcome an inert row, which is the specific defect this loop is
meant to prevent.

- Blocks: nothing. Clan Wars ships on Option A; switching to B is a small edit
  in `logic/clan_wars_logic.py`.
- Evidence: `memory-bank/source-audits/clan-wars-horizontal-implementation-2026-07-26.md`

### 3.3 Tears of Guthix — how many review beats one cavern visit is worth

Raised 2026-07-26 while building the Tears of Guthix family.

The period timer is exact: `Tears of Guthix` oldid `6579712` says "the time a
player has is the player's Quest Points in Ticks", capped at three minutes, so a
visit is `min(quest_points, 300)` game ticks. What no source states is how many
*answered cards* that is worth, because the period game had no such unit.
`source-audits/activity-cadence-reconciliation-2026-07-18.md` settled the shape —
one Tears handler action advances one automatic collection beat — and left the
beat count open.

Options:

- **A. One review is six game ticks** (recommended, and what is implemented).
  It reuses the cadence the live Combat activities already run at, so nothing new
  is invented. A 44-point player gets 8 beats and a capped 300-point player gets
  50, which scales with quest progress exactly as the period timer does.
- **B. A fixed beat count per visit**, the same for everyone. Simpler to read in
  the UI, but it throws away the one part of the mechanic the source states
  precisely — that Quest Points buy cavern time.
- **C. One review is one tick.** Faithful to the unit, but a capped visit becomes
  300 answered cards, which is a fifth of a simulated week for one D&D.

Blocks: nothing. Changing the answer later is a one-constant edit to
`TEARS_OF_GUTHIX_TICKS_PER_REVIEW`, and the tests read the constant rather than
restating the beat counts.
### 3.4 Do No Evil's one-time elite clue can be lost permanently

Raised 2026-08-22 while applying the one-clue ownership rule to quest rewards.
This is an owner-only decision; the current behaviour is unchanged.

At `logic_pure/logic_pure_quest.py:1470`, `apply_quest_progress_pure`
filters Do No Evil's rewards against the post-stage player data. Reproduction:
put the player at Do No Evil stage 9 with its required action complete and
`{"Clue scroll (easy)": 1}` in the inventory, then call
`apply_quest_progress_pure(player_data, "do_no_evil", QUEST_DATA)`. The quest is
marked complete and the Cramulet lands, but the one-time `Clue scroll (elite)`
is withheld permanently. No pending-reward or reclaim path records it;
`reclaim_death_office_items_pure` covers deaths only.

Options:

- **Keep the current behaviour.** The one-clue rule applies immediately, so a
  held clue permanently displaces the unique elite clue reward.
- **Hold the reward for later collection.** Complete the quest, but preserve the
  elite clue as pending until the player no longer owns another clue.

Recommendation: the owner must choose between these readings; implementation
must not decide by inference. Blocks: the final policy for unique quest rewards,
not the current clue-ownership fix.

### 3.5 Two Crucible reward rows have nothing to act on

Raised 2026-07-26 while building The Crucible. Not a blocker: the family shipped
with the other twenty-eight rows of its shop.

Marv's reward interface has thirty-three rows. Thirty ship as death taunts and
death titles, and the Supreme champion's helm ships gated on having been named
Supreme Champion. The remaining three are the fissure energy boosts (24, 36 and
48 Trophy bones), which increase the run energy the arena's fissures restore, and
a fourth is the 15-bone Rogue glove repair. Both prices are exactly sourced —
rev-727 enum 5901 and the pinned article agree — but AnkiScape has no fissure
travel and no Rogue glove, so buying either would take the bones and change
nothing.

- Option A: leave the four rows out, as shipped. The shop tells the truth about
  what it sells, and nothing is advertised that does not work.
- Option B: build the surfaces they need. Fissure travel would have to become a
  real in-arena action with a run-energy cost for a boost to it to mean anything,
  and the Rogue gloves need a five-tier degradable equipment family with a
  maximum-lifepoints bonus and a charge count that no source states.
- Recommendation: **A** for now. Option B is a second family's worth of work
  hanging off four shop rows, and the glove bonus and charge count are both
  unsourced, so it would be built mostly out of placeholders.

Blocks: nothing. Worth answering if the Rogue gloves are ever wanted in their own
right, since they are period equipment rather than only a shop row.

### 3.6 The Supreme Champion's invulnerable phase is not modelled

Raised 2026-07-26 by an independent audit of the shipped Crucible family, and
confirmed against the code.

The launch update is exact: the event runs two and a half minutes, the champion is
invulnerable for the first two of them, and the arena is safe throughout. Our
event is one review long, so there is no fifth of a window for the vulnerable
phase to occupy, and the champion is attackable for the whole event. The data
module's own comment described the phase split that its constants make impossible,
which is how this reached a merged family.

Options:

- **A. Say plainly that the phase is not modelled** (implemented). The event stays
  one review, the champion is attackable throughout, and the code says so instead
  of implying otherwise. Cheapest, and honest.
- **B. Lengthen the event to five reviews**, with the first four invulnerable. It
  reproduces the 80/20 split exactly and gives the phase a reason to exist. It also
  makes the event occupy every review between its own arrivals, since the interval
  is five reviews, so the arena would effectively always be in an event.
- **C. Lengthen the interval as well**, so a five-review event fits inside a longer
  gap. Faithful to the shape, but it abandons the half-hourly cadence that the
  240-card day clock derives exactly, and that cadence is sourced while the event
  length is not.

Recommendation: **A** until the event's own pacing matters to play. B and C both
trade a sourced cadence for an unsourced one.

Blocks: nothing. Related: fork 3.3 sets the reviews-to-ticks conversion that
`CRUCIBLE_COMBAT_TICKS` reuses; answering that one should change this constant too.

### 3.7 Activity-owned population base ceilings

Raised 2026-07-26 while removing the superseded Quiet / Normal / Busy player dial.
The owner settled that each public activity grows its own population with the
existing fuzzy curve, but did not set the activity-owned base ceilings that
replace the selected profile.

- **Option A (implemented).** Give Shooting Stars and Big Chinchompa independent
  constants both set to `0.92`, preserving the former Normal profile's observed
  behaviour while removing every player control. They can diverge later without
  restoring shared save state.
- **Option B.** Recover or choose different activity-specific ceilings now. No
  period population statistics have been recovered, so any different values
  would be invented rather than sourced.

Recommendation: **A** until playtesting or a source-backed range justifies a
specific divergence. The event-seeded `±20%` ceiling shift, world-day envelope,
S-curve shifts, and phase noise remain active, so this does not make events
deterministic. Blocks: nothing.

### 3.8 How a geography-bound period task becomes a predicate

Raised 2026-07-26 while building the Achievement Diaries family. The design
contract's curation rules say to preserve the distinctive feat and to remove
geography, emotes and inventory choreography. For many period tasks, removing
the choreography removes the whole task: "Have Thessalia show you what outfits
you can wear" is a place and a conversation, and nothing else.

Two honest readings, and they produce different rosters:

- **A. Requirement-as-predicate (implemented).** Keep a period task only when
  its pinned row states a requirement, and make its predicate exactly that
  stated requirement. The name and description are preserved verbatim, so the
  feat survives as identity and narrative while the measurable part is the
  period's own published gate. 171 of the roughly 500 harvested rows survive.
  Nothing is invented, but a task reads as "be able to do this" rather than
  "do this".
- **B. Hand-translated feats.** Map each task onto an AnkiScape action counter
  by hand — "Mine some iron" becomes an iron-ore ledger threshold. Truer to the
  design's intent, and much better play. It is also roughly 380 individual
  judgement calls, each of which invents a quantity the period never stated,
  which is exactly the failure mode the placeholder rule exists to prevent.

Recommendation, and what shipped: **A**, because it is the only one of the two
that cannot fabricate. B is worth doing later per family, as an explicit
curation pass with the owner, on top of A rather than instead of it — the
catalog is generated, so a hand-curated override table can replace any row
without disturbing the rest.

### 3.9 Three families' task tables did not parse, and their tiers ship empty — resolved 2026-07-27

Resolution: the generator no longer depends on those wiki table layouts. Darkan's
rev-727 enum 3483 supplies the names, descriptions and encoded requirements, and
the per-family Java classes supply tier membership. Falador, Fremennik and Seers'
Village now all carry non-empty rosters.

Raised 2026-07-26. Darkan gives every one of the eight families its exact tier
membership, so Falador, Fremennik and Seers' Village ship with real tiers, real
reward items and real taskmasters. Their pinned wiki task tables use a third
layout the harvester does not read, so those twelve tiers carry no tasks.

An empty tier must not read as a finished one, so the engine gives it the status
"Roster pending harvest" and never lets it become claimable. That is a real
mechanical state rather than an invented one, but it is visible to the player.

Recommendation: finish the harvester for the three layouts rather than
hand-entering the rows. The counts are already known from Darkan, so a correct
parse is self-checking — it either matches Darkan's per-tier count exactly, as
it does for the other five families, or it is wrong.

### 3.11 The all-skills capes have 24 skills to ask for, and the period has 25

Raised 2026-07-27. The pinned Max revision (oldid `6549092`) requires level 99
in all 25 cutoff skills. AnkiScape has 24 of them. Dungeoneering is in the skill
registry with `surface_state="planned"`, and no shipped code writes
`dungeoneering_exp`, so no save can raise `dungeoneering_level` above 1.

That leaves two ways to read the contract, and they lead to opposite failures.

Enforcing the period's 25 makes Max unobtainable forever, and with it the
Completionist cape above it and all nine milestone capes, whose wear gate is
"level N in every skill". That is the inert-reward failure the milestone-cape
repair already removed once, for the same reason and in the same place.

Deriving the gate from the skill registry keeps all three reachable, but a
player who reaches 24 is told they are maxed when the period figure is 25.

Recommendation, and what is implemented: derive the gate from the skill
registry, and name the shortfall out loud rather than dropping it silently. The
Max requirement row reads "Level 99 in every skill (Dungeoneering latent until
the skill ships)", the Cabinet's cape card says the same thing once, and
`latent_cutoff_skills_pure()` is the single list every surface reads. The gate
becomes 25 by itself on the day Dungeoneering becomes trainable, which is the
latent-activation pattern the contract already uses for Completionist
requirement families and for Music Log tracks.

The Dungeoneering skillcape follows the same rule and is deliberately not
shipped. `SKILLCAPES` carries its complete period row — item ids 18508-18510
and Thok, Master of Dungeoneering — and `skillcape_definitions()` filters it out
because a cape that no save can reach level 99 to buy is an inert reward. It
joins the shipped list on its own when the skill does. The level-120 master cape
the contract also asks for is blocked behind the same gap.

### 3.12 New predicates overfill Ardougne Easy's twelve-task budget

Raised 2026-07-27. Ardougne Easy had ten shipped tasks. The approved expansion
makes four more source tasks evaluable, but the design contract fixes every
regional tier at exactly twelve tasks. Keeping raw source order would admit
Silky Smooth and A Gift from Khazard, while Vial Deeds has the stronger exact
provider, item and transaction proof that the live shop handler records.

Recommendation, and what is implemented: preserve all ten shipped rows, then
use the two remaining places for A Gift from Khazard and Vial Deeds. Do not
replace existing tasks and do not raise the twelve-task budget. Silky Smooth
and Don't Eat the Pointy Bit stay omitted because the live game does not have
the exact silk-trader haggling or Poison Arrow skewered-kebab route.
### 3.13 Shattered Heart has no recovered strange-rock rate table

Raised while building Shattered Heart to breadth one. The cutoff articles prove
that successful training actions can award strange rocks, that different actions
felt different in practice, and that the second rock in one skill has half the
ordinary chance until another skill produces a rock. Darkan and game-main contain
only item identities, and no recovered cache or server routine states the base
probability or a per-skill table.

- **Option A (implemented and recommended).** Use one registered placeholder
  probability for every eligible skill action, then apply the sourced one-half
  second-rock modifier. This is the verification standard's explicit estimation
  floor: one global constant instead of a fabricated per-skill table.
- **Option B.** Invent separate rates for fifteen skills or individual actions.
  This may feel closer to player reports, but every difference would be invented.
- **Option C.** Disable rock acquisition until a rate table is recovered. This is
  rejected by the breadth-phase rule because the placeholder would disable the
  family's central mechanic instead of completing it.

Blocks: nothing under option A. Evidence:
`memory-bank/source-audits/shattered-heart-loop-2026-07-17.md` and placeholder
`shattered_heart.rock_chance`.

### 3.14 Shattered Heart conflicts on reacquiring a placed skill pair

The pinned `Shattered Heart` article says repeatedly that the second rock's chance
is merely halved until another skill yields a rock, and that rocks for later
statues can be collected without waiting for the next weekly completion. One
stale detailed-information bullet instead says a completed skill pair blocks all
more rocks from that skill until every other non-combat skill is complete.

- **Option A (implemented and recommended).** Follow the repeated lead rule. Once
  a pair is placed, that skill can build a two-rock buffer for the next statue;
  the buffered pair cannot be placed until the current statue explodes.
- **Option B.** Follow the lone stale bullet and block the skill after its current
  pair is placed. This removes the stated early-collection behavior.

Blocks: nothing under option A. Evidence: RuneScape Wiki `Shattered Heart`
oldid `6514590` and `Strange rock` oldid `6564676`, reconciled in
`memory-bank/source-audits/shattered-heart-loop-2026-07-17.md`.
### 3.15 Temple Trekking and Burgh de Rott Ramble share one surface

The period exposes two directions with different quest gates, but companions,
progression, follower food and reward tokens are one system. Separate cards would
duplicate policy and make shared state harder to read.

Recommendation and implemented behaviour: keep one Temple Trekking card with a
direction selector. The pure view changes the available companions and quest gate
for that direction. Blocks nothing; splitting later is a presentation-only change.

### 3.16 Route choice applies to each encounter, not the whole trek

The earlier owner note described one route tier chosen at entry. The pinned period
page instead lets the player choose easy, medium or hard again after each event.
A literal prompt between every answered card would interrupt the review loop.

Recommendation and implemented behaviour: the saved route is the next-encounter
policy. Entry freezes it for the first node; completing a node freezes the current
policy for the next node. `route_history` records every actual choice for token
quality and diary proof. This preserves the period choice point without a modal
review interruption.

### 3.17 Breadth-one follower supplies stay compact and explicit

The period follower inventory accepted food generally and the Druid pouch had
charges. A full carried-food editor would add a second inventory surface to a
breadth activity, while a Boolean pouch would erase an attested resource.

Recommendation and implemented behaviour: use one shared 28-slot Lobster pack as
an explicit AnkiScape abstraction, allow it to be stocked during a trek, and store
three Druid-pouch charges separately from the item. The direct fill action
compresses Bloom, flora collection and filling; the placeholder register names the
remaining follower eating policy. This can widen to ordinary food rows without a
save migration.

### 3.18 Mage Training Arena ordinary dragonstone spawns in breadth one

Raised 2026-07-27. The period Enchanting Chamber spawned six dragonstones every
five minutes, each worth twice the enchantment level. The settled Arena contract
excluded world-hopping the spawn, but did not say whether the ordinary timed
spawn belongs in the breadth-one room loop. At Enchant Level 6 the ordinary
spawn can contribute up to 864 points per hour, so silently mixing it into the
placeholder shape throughput or silently omitting it from a claim of exhaustive
room fidelity would both be misleading.

Recommendation, and what is implemented: breadth one models the chamber's core
bonus-shape loop, tenth-shape bonus, twentieth-orb rune reward, and exact spell
XP, while leaving the separate timed dragonstone opportunity for the later
catalog/depth pass. The UI and source strings make no claim that the room's
maximum period throughput is closed. This keeps the requested smallest
mechanically complete room loop without inventing a conversion between the
five-minute world spawn and answered reviews.

The replacement seam is explicit: add a separately persisted dragonstone spawn
clock and route it through the same Enchantment wallet. Do not fold it into
`mage_training_arena.enchantment_shapes_per_hour`, because the two opportunities
had different counters and rewards in the period game.

### 3.15 Does the reviewer badge list only favourited Distractions?

Raised 2026-07-28 while building the always-visible strip from section 4.8.

Section 4.8 gives the badge one permanent seat and says its popover lists
"favourited D&Ds and farming state". It does not say what happens to a live
Distraction the player never pinned. Before this work the badge showed the three
review-clock events and nothing else, so reading the record strictly would
*remove* notifications the player already had.

- **Option A (implemented and recommended).** A favourite adds a line; it never
  removes one. Every live event still appears whether or not it is pinned,
  because the strip's rule is "only what is live" and a live star is live. A pin
  adds a permanent line for a Distraction that is quiet, so the player can watch
  a weekly errand he would otherwise forget. The badge count counts only live or
  attention-needing lines, so pinning ten quiet Distractions does not turn the
  badge into a "10".
- **Option B.** Strict favourites: the popover shows pinned Distractions only.
  Cleanest reading of the words, but a fresh save with no pins loses the star and
  Evil Tree alerts that already work, and the owner would have to discover the
  pin before the notification system does anything at all.
- **Option C.** Pin everything by default, then let the player unpin. Rejected:
  sixteen lines in a reviewer popover is the clutter section 4.8 exists to stop.

Two smaller calls ride along, both open to reversal:

1. **Only Distractions can be pinned.** The record names D&Ds and Farming, so the
   pin is hidden on minigames, Warriors' Guild and landmark surfaces. Castle Wars
   has no live state worth a notification line today.
2. **A quiet favourite's status line comes from the shared target-row metadata**
   ("Ready — nothing live", or its first locked reason). No cross-family live
   status exists: each family has a bespoke `*_view_pure`, and only three feed
   `world_event_rows_pure`. A richer quiet line means either fifteen bespoke
   formatters or a new per-family status contract.

Blocks: nothing under option A.
### 3.19 Mobilising Armies' hourly rank cap has no clock to hang on

Raised 2026-07-28. The period rule is exact: "A maximum of 12 ranks can be gained
per hour." Its whole purpose is to stop rank farming through three-minute suicide
games, which the Siege article documents as a mainstream strategy. AnkiScape's
review loop has no wall clock, so an hour has to become something else or the cap
has to be dropped — and dropping it would leave the fastest rank route
uncapped, which is exactly the behaviour Jagex added the cap to prevent.

Three options were considered. A real timestamp would be faithful but would make
rank progress depend on how long the player leaves Anki open, which contradicts
the review-driven model everywhere else. Dropping the cap would let a player
forfeit-farm rank far faster than the period allowed. Counting review beats keeps
the cap's purpose intact and stays inside the existing model.

Recommendation, and what is implemented: the hour is a rolling window of
**36 review beats** — two full eighteen-beat scenarios, which is one hour of
scenario time. Registered as
`mobilising_armies.rank_window_reviews`. The replacement seam is a single
counter: if a real-time clock ever becomes available to the review loop, swap the
window without touching the award rules.

### 3.20 Winning by the primary objective can outrun the ten-order rank gate

Raised 2026-07-28. Two sourced rules interact awkwardly once a thirty-minute
battle becomes eighteen orders. Rank needs "at least 10 actions"; some primary
objectives can be reached in fewer orders than that. In the period game the two
never collided, because ten commands in thirty minutes is trivial.

Breadth one resolves it by calibration rather than by special-casing: every
scenario's primary objective is tuned to need at least ten orders, so a legitimate
win always earns rank. Siege's direct assault deals 10 wall damage per order
(exactly ten orders), its catapult route needs twelve, Hoard needs thirteen and
Rescue fourteen. The rank gate still bites on forfeits, on early wipes, and on
players who spend reviews on Again — which is where the period rule bit too.

The alternative, and the fork the owner may prefer: waive the ten-order threshold
whenever the primary objective is completed, and keep it only for participation
rank. That would decouple rank from the objective rates so the rates could later
be re-tuned freely. It is not implemented, because it would add an unsourced
exception to an otherwise exact rule.
### 3.21 Gnome Restaurant: one delivery ticket, or an order-and-reward board

Raised 2026-07-28. This is the presentation fork deferred on 2026-07-17 "after the
data surface is known". The data surface now exists, so here it is as a choice you
can answer from your phone.

**What the card has to carry.** Nineteen easy customers and twenty hard ones; one
outstanding order naming a customer, a location and one of twenty gnome dishes;
the delivery window in the source's own minutes (six easy, eleven hard) which each
`Again` spends six of; a cumulative point ledger with a reward every twelve points;
a Reward token that banks up to ten free meals; and a tip that is coins on an easy
job and one of thirty-seven sourced rows on a hard one. The whole card has to fit
in about 560 points.

**Option A — one delivery ticket (implemented).** The card answers "what do I do
next" in one line and keeps the reward economy to one more:

```
[icon] Gnome Restaurant                                   ON A JOB
Hard job: 1 Chocolate bomb for Captain Ninto — the dwarven bar
under White Wolf Mountain · 0 held
[####################--------]  5 of 11 delivery minutes left
27 points · 9 to the next reward · token holds 2/10 meals · 4 easy / 5 hard delivered
Jobs [ Hard job, anywhere in Gielinor v ]              [ Save ]
Cook or bank 1 Chocolate bomb
[ Take a job ]                        [ Decline ]  [ Quit job ]
[ Order free food ]                              [ Replace token ]
```

**Option B — order-and-reward board.** The card splits: the live order on the left,
the reward economy permanently on the right, and both job offers as their own
buttons showing what each pays:

```
[icon] Gnome Restaurant                                   ON A JOB
+-- Order ------------------------+-- Rewards ------------------+
| Captain Ninto                   | Points        27            |
| the dwarven bar under White     | Next reward   9 points      |
| Wolf Mountain                   | Token         2 / 10 meals  |
| Wants 1 Chocolate bomb (0 held) | Last tip      8 Mint cake   |
| [#########-----] 5 of 11 min    | Delivered     4 easy 5 hard |
+---------------------------------+-----------------------------+
[ Easy job · 1 point · 6 min ]   [ Hard job · 3 points · 11 min ]
[ Decline ]  [ Order free food ]  [ Replace token ]  [ Quit job ]
```

**The trade.** A keeps one idea on screen and costs no new UI vocabulary, but the
reward economy — the mint cake, the gnome scarf and goggles, the whole reason to
run hard jobs — shrinks to one grey line. B keeps the payoff visible and makes the
two job offers self-explaining, at the cost of a two-column grid inside a card that
already carries a progress bar, which is exactly the shape the offscreen-Qt rule
warns produces min-height overflow at 560 points.

**Recommendation, and what is implemented: A.** One review is one delivery, so the
card's job is to say what to deliver and whether you are holding it; the reward
ledger changes once every twelve deliveries and does not deserve a permanent
column. If you would rather see the payoff than the instruction, say B and the
swap is confined to `ui/gnome_restaurant_panel.py` — every flag it renders already
comes from `gnome_restaurant_view_pure`, so no logic moves.

**Blocks:** nothing. Gnome Restaurant is at breadth one either way; this decides
which layout ships.

### 3.28 Camouflaged jadinko needs its own source-backed tracker slice

Raised 2026-08-21 while closing the grimy-herb re-land audit. This is a content
gap to preserve, not a request to widen that slice.

Darkan commit `7e7d67b` defines `CAMOUFLAGED` as the third tracker: Hunter 79,
guaranteed Camo vine item `19978`, Juju hunter potion required, Standing Stones,
`ProduceType.Lergberry`, and an empty fruit-tree patch. Descendant restoration
commit `16b179a` adds the exact tracker XP, `600.0`. At `7e7d67b`,
`data/npcs/drops/hunter/hunter_jadinko_camouflaged.json` independently rolls
bush seeds at `16/256`, one of Ugune, Argway, Shengo, or Samaden seed at `4/256`,
and blossom seeds at `4/256`, in addition to the guaranteed Camo vine.

AnkiScape has no `track_camouflaged_jadinko` action, no Standing-Stones plus
Lergberry tracker gate, and therefore no route to item `19978`. The grimy-herb
slice registers the other twelve source rows; adding this third tracker is new
Hunter content and must not be hidden inside the six-row independent-table fix.

Recommendation: implement Camouflaged in its own slice, using the established
tracker action shape plus its source feature, produce, Juju, empty-tree, XP, and
three independent drop tables. Blocks: the Camo vine route and a complete
thirteen-row Jadinko roster, but not the five live vine-herb chains.

**Resolved 2026-08-22** on `goal/camo-jadinko-2026-08-22`: `track_camouflaged_jadinko`
now exists as the third tracker row, following the Shadow/Diseased shape with
all three source-backed secondary tables live in Darkan order. One correction
to the record above: item 19978's period name is **Striped vine** (wiki
`Striped_vine`, infobox `id = 19978`; Darkan
`HerbloreHabitatTransactions.kt:21` `STRIPED_VINE = 19978`), not "Camo vine" —
that name exists nowhere. Full sourcing in
`memory-bank/source-audits/camouflaged-jadinko-tracker-2026-08-22.md`.

### 3.29 Durable line citations need a mechanical drift check

Raised 2026-08-21 after a grimy-herb record still pointed at pre-merge line
numbers and three pinned enum citations pointed at the following rows. These
errors are mechanically checkable but currently depend on reviewers opening
every cited location by hand.

Schedule a documentation-audit slice that parses `path:line` and
`path:start-end` citations in Memory Bank Markdown, resolves repository-local
paths against the current tree and pinned external paths against their named
commits, and verifies that each target still exists. The check should report the
record location, cited target, and target text so a reviewer can confirm the
semantic claim; existence alone cannot prove that the cited lines say what the
record says. It must not rewrite citations automatically, because a moved line
and a changed source claim require different fixes.

Blocks: nothing in the grimy-herb family. This is a cross-cutting record-quality
check to schedule as its own slice, not tooling to add during family promotion.

### 3.30 Rune Mysteries stage 1 has no action emitter and blocks its dependants

Raised 2026-08-22 while extending the item-reachability audit through Bank
claims. This is a player-visible defect for a dedicated quest slice, not work to
hide inside the audit.

- **Broken quest stage:** `rune_mysteries`, stage `1`. Its exact required action
  is `Deliver the strange talisman to Sedridor` at
  `data/quest_data.py:7086`. No production path emits that action. The matching
  pure-logic test at `tests/test_logic.py:3183-3188` injects it directly into
  `quest_stage_actions`, so it does not prove a player can produce it.
- **Measured failure:** `build_reachability_report()` returns a
  `blocked_quest_stage_products` row for `rune_mysteries`, stage `1`, with
  `missing_required_actions` equal to
  `['Deliver the strange talisman to Sedridor']`.
- **Direct downstream blocks:** the Wicked hood claim inherits
  `ClaimDefinition.required_quest = RUNE_MYSTERIES_ID` from
  `data/quest_data.py:978` because its row at `data/quest_data.py:9668-9674`
  does not override the field; the `rune_essence` Mining target is gated by the
  quest at `data/quest_data.py:9438`; and Lunar Diplomacy requires Rune Mysteries
  at `data/quest_data.py:3462`, which in turn withholds its Lunar Spellbook and
  Astral Altar unlocks, including the `craft_astral_runes` target.

The next quest agent should add a real runtime emitter for the exact action and
prove stage 1 through the real kernel from an ordinary started quest, without
pre-seeding `quest_stage_actions`. Do not repair this by weakening the quest-stage
reachability audit or by making the Wicked hood unconditional.

### 3.31 Forty-five quests require specific actions that no runtime path emits

Raised 2026-08-22 after the Rune Mysteries repair exposed the same
player-visible defect across the quest catalog. This is an implementation
queue for quest slices, not a reason to relax the reachability gate.

- **Measured class:** at `d1b242ac`,
  `build_reachability_report()["blocked_quest_stage_products"]` returned
  `184` rows. Flattening each row's `missing_required_actions` and applying
  `re.fullmatch(r"^Complete .+ stage \d+ objective$", action)` split the values into `148`
  generated stubs and `49` specific actions across `45` quests. The counts
  classify missing-action values, not rows: a row can carry more than one
  missing action.
- **Fix pattern:** preserve each stage's sourced action text and source
  constants, then connect the action through the established production
  mechanism. For dialogue, hand-in, and puzzle steps abstracted by ordinary
  quest review progression, the worked repairs move the exact string from
  `required_actions` to `auto_actions`. See Rune Mysteries commit `8aafd995`
  and Ernest the Chicken commit `3e4576fb`. The regression must
  start the quest normally, drive `apply_quest_progress_pure`, and never
  pre-seed `quest_stage_actions`.
- **Audit rail:** do **not** repair any quest below by weakening, filtering,
  suppressing, or changing the semantics of the quest-stage reachability
  audit. Repair the missing production path. Re-run the same regex split
  after each slice so the specific set shrinks for a real reason.

**Audit-generated scheduling snapshot (`d1b242ac`):**

- **A Soul's Bane** (`a_souls_bane`)
  - Stage `2`: `Fill the rage meter with an anger weapon`
- **Biohazard** (`biohazard`)
  - Stage `1`: `Ask Jerico about crossing the West Ardougne wall`
- **Black Knights' Fortress** (`black_knights_fortress`)
  - Stage `1`: `Infiltrate the Black Knights' Fortress`
- **Carnillean Rising** (`carnillean_rising`)
  - Stage `1`: `Speak to Ceril Carnillean`
  - Stage `1`: `Speak to Xenia`
- **Clock Tower** (`clock_tower`)
  - Stage `1`: `Pick up rat poison in the Clock Tower dungeon`
- **Deadliest Catch** (`deadliest_catch`)
  - Stage `1`: `Pickpocket the Master fisher for the sea chart`
- **Dealing with Scabaras** (`dealing_with_scabaras`)
  - Stage `1`: `Prepare bronze equipment for the High Priest's tests`
- **Demon Slayer** (`demon_slayer`)
  - Stage `8`: `Recite Aber, Gabindo, Purchai, Camerinthum, Carlem`
- **Dragon Slayer** (`dragon_slayer`)
  - Stage `2`: `Accept Oziach's dragon-slaying challenge`
- **Dwarf Cannon** (`dwarf_cannon`)
  - Stage `1`: `Accept replacement railings from Captain Lawgof`
- **Elemental Workshop II** (`elemental_workshop_ii`)
  - Stage `1`: `Find and slash the Beaten Book open in the workshop`
  - **Source conflict found 2026-08-22:** do not add an emitter for this
    string. The pinned quest article (`oldid=6358871`,
    `2012-10-06T20:56:17Z`) says the player finds the distinct Beaten book in
    the Exam Centre and reads its hidden scroll; it separately identifies the
    Slashed book as an Elemental Workshop I item reclaimed in Seers' Village.
    The pinned quick guide (`oldid=6333340`, `2012-10-02T07:32:08Z`) agrees.
    Darkan commit `fd901261fbf3a3ccee75236c422765c9d9383f4a` implements those
    same search-and-read steps with Beaten book id `9717`, while Slashed book
    remains id `9715`; rev-727 and rev-742 cache definitions and game-main's
    item table preserve the same two identities. The cleanup row at
    `data/quest_data.py:7924` instead invents slashing the Beaten Book in the
    workshop and produces `Slashed book`. This needs a source-correction slice,
    not reachability for the reported action.
- **Elemental Workshop III** (`elemental_workshop_iii`)
  - Stage `1`: `Find and read the Ragged book in the workshop`
- **Ernest the Chicken** (`ernest_the_chicken`)
  - Stage `1`: `Ask Professor Oddenstein about Ernest`
- **Family Crest** (`family_crest`)
  - Stage `2`: `Ask Caleb about the fish salad`
- **Fight Arena** (`fight_arena`)
  - Stage `3`: `Talk to Jeremy about the key holder`
- **Fishing Contest** (`fishing_contest`)
  - Stage `1`: `Receive a fishing pass from Austri or Vestri`
- **Gertrude's Cat** (`gertrudes_cat`)
  - Stage `1`: `Speak to Shilop and Wilough in Varrock Marketplace`
- **Heroes' Quest** (`heroes_quest`)
  - Stage `1`: `Accept Achietties' three proof item challenge`
- **Holy Grail** (`holy_grail`)
  - Stage `1`: `Ask Merlin about the Holy Grail`
- **Kennith's Concerns** (`kenniths_concerns`)
  - Stage `1`: `Talk to a villager past the rocks`
- **King's Ransom** (`kings_ransom`)
  - Stage `1`: `Recover the animate rock scroll during the Sinclair Mansion investigation`
- **Lost City** (`lost_city`)
  - Stage `1`: `Find Shamus in the Lumbridge Swamp tree`
- **Merlin's Crystal** (`merlins_crystal`)
  - Stage `1`: `Complete the round-table investigation with Sir Gawain, Sir Lucan, and Sir Lancelot`
- **Monk's Friend** (`monks_friend`)
  - Stage `1`: `Recover the child's blanket from the thieves' hideout`
- **Monkey Madness** (`monkey_madness`)
  - Stage `1`: `Acquire the monkey dentures, m'amulet mould, and monkey talisman during the Ape Atoll infiltration`
- **Pirate's Treasure** (`pirates_treasure`)
  - Stage `1`: `Smuggle Karamja rum off Karamja`
- **Plague City** (`plague_city`)
  - Stage `2`: `Talk to Edmond with the gas mask`
- **Priest in Peril** (`priest_in_peril`)
  - Stage `1`: `Speak through the Paterdomus temple door`
- **Rat Catchers** (`rat_catchers`)
  - Stage `1`: `Have Hooknosed Jack make rat poison`
- **Scorpion Catcher** (`scorpion_catcher`)
  - Stage `1`: `Accept Thormac's scorpion cage`
- **Sheep Herder** (`sheep_herder`)
  - Stage `1`: `Accept poisoned sheep feed from Councillor Halgrive`
- **Shield of Arrav** (`shield_of_arrav`)
  - Stage `1`: `Find and read the Shield of Arrav book`
- **Some Like It Cold** (`some_like_it_cold`)
  - Stage `1`: `Entertain the seal`
  - Stage `1`: `Speak to Chuck again for teleport`
  - Stage `1`: `Travel to the Iceberg`
- **Song from the Depths** (`song_from_the_depths`)
  - Stage `1`: `Drink the restless sleep potion`
  - Stage `1`: `Follow the souls to the cave entrance`
- **Tai Bwo Wannai Trio** (`tai_bwo_wannai_trio`)
  - Stage `2`: `Catch karambwanji for Tiadeche`
- **The Restless Ghost** (`the_restless_ghost`)
  - Stage `1`: `Receive the ghostspeak amulet from Father Urhney`
- **The Tale of the Muspah** (`the_tale_of_the_muspah`)
  - Stage `1`: `Cast Enchant Level 1 Jewellery for the sapphire preparations`
- **Tree Gnome Village** (`tree_gnome_village`)
  - Stage `1`: `Ask Commander Montai how to help the gnome battlefield`
- **Tribal Totem** (`tribal_totem`)
  - Stage `1`: `Ask Wizard Cromperty about the teleportation block`
- **Vampyre Slayer** (`vampyre_slayer`)
  - Stage `4`: `Tell Morgan that Count Draynor is dead`
- **Waterfall Quest** (`waterfall_quest`)
  - Stage `1`: `Speak to Hudon by the waterfall`
- **While Guthix Sleeps** (`while_guthix_sleeps`)
  - Stage `1`: `Cast NPC Contact to reach the quest contacts`
- **Witch's House** (`witchs_house`)
  - Stage `2`: `Enter the Witch's house with the door key`
- **Within the Light** (`within_the_light`)
  - Stage `1`: `Recover the Temple of Light keys and crystal puzzle pieces`
- **Wolf Whistle** (`wolf_whistle`)
  - Stage `1`: `Find Scalectrix at the Taverley well`

Ernest the Chicken is the first item removed from this snapshot by the worked
repair above. Schedule the remaining 44 quests from this list; before each
slice, re-measure because earlier slices can expose later blocked stages in
the same quest.

### 3.32 Thirty quests require routes that no player can select

Raised 2026-08-22 after a catalog scan found quest-stage route gates that no
player can set. This is failure mode 3 from the standing slice contract: an
inert row gated on a state no player reaches. This entry records the defect and
an open design fork; it does not choose or implement a repair.

- **Broken runtime path:** `apply_quest_route_choice_pure` at
  `logic_pure/logic_pure_quest.py:425-457` is the only production writer of
  route values in `quest_route_states`. It accepts a route only when a
  registered `QuestChoice` for the current stage offers the same `route_id`;
  otherwise `logic_pure/logic_pure_quest.py:432-440` returns
  `(player_data, False)`. The Quests tab likewise creates a route button only
  inside the loop over a `QuestChoice` option at
  `ui/ui_tab_quests.py:392-405`. A stage can therefore require a route that the
  player can neither select nor cause the logic layer to record, so the quest
  stays blocked forever.
- **Measured catalog class:** at `a23f80f3`, scanning `QUESTS` and subtracting
  the union of every `choices` option's `route_id` from the union of every
  stage's `required_routes` found **30 quests** with at least one unsatisfiable
  route and **44 distinct unsatisfiable route ids**. These counts describe the
  complete static catalog, not reachability-audit rows.
- **Measured reachability view:** at the same commit,
  `build_reachability_report()["blocked_quest_stage_products"]` returned
  **178 rows**. Counting rows that carry each field gave
  `missing_required_actions`: **172**, `missing_required_items`: **77**,
  `missing_required_routes`: **16**, and `missing_required_tools`: **2**. A row
  can carry more than one field, so these field counts do not sum to 178.
- **Why 16 is not 30:** the reachability audit reports only the earliest blocked
  stage for each quest. The **16 rows** carrying `missing_required_routes` are
  what the current audit exposes; the static scan's **30 quests** are the true
  size of this defect class. Entry 3.31 records the same exit behavior: its
  Biohazard snapshot exposed one stage before the earlier gates were repaired,
  while the landed repair covered 27 actions across all 13 playable stages.
- **Worked example:** Dwarf Cannon stage `6` requires
  `Reach the Dwarf Cannon goblin hideout` at `data/quest_data.py:6219-6224`,
  while `dwarf_cannon.choices` is empty. No route button exists, and the only
  writer rejects that route because no registered option offers it.
- **Relationship to entry 3.31:** **19 quests** occur in both the missing-action
  scheduling snapshot and this unsatisfiable-route class: Biohazard, Dealing
  with Scabaras, Dwarf Cannon, Family Crest, Gertrude's Cat, Heroes' Quest,
  Holy Grail, Kennith's Concerns, Lost City, Merlin's Crystal, Plague City,
  Scorpion Catcher, Sheep Herder, The Tale of the Muspah, Tree Gnome Village,
  Tribal Totem, Waterfall Quest, Witch's House, and Within the Light. Repairing
  an action emitter does not make any of these quests finishable while its
  route remains impossible to set.
- **Correction to the landed record:** four quests in that 19-quest overlap
  carry a landed entry 3.31 action-emitter repair. Their commit subjects read as
  though the quest is now finishable:
  - `Biohazard was impossible to finish; emit every quest step` (`e8efa7ae`)
  - `Dealing with Scabaras was impossible to finish; emit every quest step`
    (`6c0cda7d`)
  - `Holy Grail was impossible to finish; emit its quest steps` (`17656ce4`)
  - `Dwarf Cannon was impossible to finish; emit every quest step` (`e473ffa0`)

  That reading is wrong for all four. Each still carries an unsatisfiable route,
  so each landed repair is incomplete. Two further quests repaired in the same
  batch are not affected: Shield of Arrav satisfies its routes through a real
  two-option `QuestChoice`, and Priest in Peril declares no route at all.

  Counted against the live audit rather than the entry 3.31 snapshot, the open
  overlap at `a23f80f3` is **17 quests**; the snapshot figure of 19 adds
  Biohazard and Dealing with Scabaras, whose action emitters had already
  landed.

**Catalog-generated scheduling snapshot (`a23f80f3`):**

- **Lost City** (`lost_city`)
  - Stage `2`: `Reach Entrana without combat gear`
- **Witch's House** (`witchs_house`)
  - Stage `5`: `Avoid the witch's patrol through the house`
- **Merlin's Crystal** (`merlins_crystal`)
  - Stage `2`: `Reach Keep Le Faye through the Catherby crate delivery`
- **Heroes' Quest** (`heroes_quest`)
  - Stage `5`: `Reach a lava eel fishing spot in Taverley Dungeon or the Lava Maze`
  - Stage `7`: `Reach the Ice Queen lair through a Dusty key or Agility shortcut route`
  - Stage `8`: `Reach Entrana without prohibited combat equipment`
- **Scorpion Catcher** (`scorpion_catcher`)
  - Stage `3`: `Reach the Taverley Dungeon scorpion room`
  - Stage `4`: `Reach the Barbarian Outpost scorpion room`
  - Stage `5`: `Reach the Edgeville Monastery scorpion room`
- **Family Crest** (`family_crest`)
  - Stage `8`: `Reach the Witchaven perfect gold mine`
  - Stage `13`: `Reach Chronozon's lair in Edgeville Dungeon`
- **Tribal Totem** (`tribal_totem`)
  - Stage `2`: `Reach the Ardougne RPDT depot`
- **Temple of Ikov** (`temple_of_ikov`)
  - Stage `1`: `Enter the Temple of Ikov`
  - Stage `3`: `Cross the Temple of Ikov lava bridge at low weight`
- **Holy Grail** (`holy_grail`)
  - Stage `2`: `Travel to Entrana`
  - Stage `4`: `Reach the Draynor Manor whistle room`
  - Stage `5`: `Reach the Fisher Realm crossing at the six stone heads`
- **Tree Gnome Village** (`tree_gnome_village`)
  - Stage `1`: `Reach Commander Montai on the battlefield`
  - Stage `5`: `Enter the Khazard stronghold through the broken wall`
- **Sheep Herder** (`sheep_herder`)
  - Stages `3`, `4`, and `5`: `Reach the Ardougne sheep enclosure`
- **Plague City** (`plague_city`)
  - Stage `8`: `Reach West Ardougne through the sewer pipe`
- **Waterfall Quest** (`waterfall_quest`)
  - Stage `3`: `Reach Golrie under Tree Gnome Village`
- **Biohazard** (`biohazard`)
  - Stage `4`: `Reach Jerico's pigeon release tile`
  - Stage `5`: `Reach Omart by the south West Ardougne wall`
  - Stages `6` and `7`: `Reach the Mourner HQ garden in West Ardougne`
  - Stage `11`: `Reach Guidor's house without Varrock guards confiscating the vials`
- **Dwarf Cannon** (`dwarf_cannon`)
  - Stage `6`: `Reach the Dwarf Cannon goblin hideout`
- **Gertrude's Cat** (`gertrudes_cat`)
  - Stage `3`: `Reach Fluffs in the Varrock Lumber Yard`
- **Mourning's End Part I** (`mournings_end_part_i`)
  - Stage `1`: `Reach Lletya`
- **Making History** (`making_history`)
  - Stage `1`: `Reach the Outpost, Rellekka, and Port Phasmatys travel legs`
- **Cabin Fever** (`cabin_fever`)
  - Stage `1`: `Reach the Port Phasmatys charter route`
- **Death to the Dorgeshuun** (`death_to_the_dorgeshuun`)
  - Stage `5`: `Reach the Tears of Guthix cavern`
- **Enlightened Journey** (`enlightened_journey`)
  - Stage `1`: `Reach Auguste on Entrana`
- **Back to my Roots** (`back_to_my_roots`)
  - Stage `1`: `Reach the Karamja jungle route`
- **Dealing with Scabaras** (`dealing_with_scabaras`)
  - Stage `1`: `Reach the Agility Pyramid`
- **Kennith's Concerns** (`kenniths_concerns`)
  - Stage `1`: `Reach the Witchaven shrine tunnels`
- **Rocking Out** (`rocking_out`)
  - Stage `1`: `Reach the Rimmington customs office`
- **Myths of the White Lands** (`myths_of_the_white_lands`)
  - Stage `1`: `Reach the Wizard's Tower ice cave`
- **In Pyre Need** (`in_pyre_need`)
  - Stage `1`: `Reach the Phoenix lair`
- **Glorious Memories** (`glorious_memories`)
  - Stage `1`: `Reach Rellekka and Miscellania`
- **The Tale of the Muspah** (`the_tale_of_the_muspah`)
  - Stage `1`: `Reach the Muspah cave route through Rellekka and Pollnivneach`
  - Stage `2`: `Reach Rellekka`
  - Stage `3`: `Reach Pollnivneach`
- **Within the Light** (`within_the_light`)
  - Stage `1`: `Reach the Temple of Light through West Ardougne and Lletya`

**OWNER DECISION — answered 2026-08-22 in 4.17**

- **Fork:** how does a player satisfy a required route that offers no genuine
  alternative?
- **Option A:** a stage whose `required_routes` has exactly one possible value is
  a step, not a choice, and the existing stage auto-action mechanism satisfies
  it. `QuestChoice` stays for real forks with two or more options, such as the
  Phoenix Gang and Black Arm Gang fork in Shield of Arrav and Heroes' Quest.
- **Option B:** register a one-option `QuestChoice` for every such route, so the
  player clicks a route button before the stage opens.
- **Option C:** use another approach that the design thread prefers.
- **Orchestrator's lean, not a ruling:** Option A. A single-valued route is not a
  decision the player makes, so presenting it as a choice adds a click that
  carries no information. Option B also grows the choice registry by 44 entries
  that never branch.

### 3.33 Six Dealing with Scabaras stages use a generated stub as their only action record

Raised 2026-08-22 after a complete scan of the generated quest-action fallback
found a distinct unresolved shape. This is an unsettled design question, not
pending implementation work.

- **Measured shape:** at `2a1d454f`, six cleanup rows re-added a generated
  `Complete {display_name} stage {stage} objective` stub as the only
  `auto_actions` value for that stage. Every row belongs to **Dealing with
  Scabaras**: stages `2`, `3`, `4`, `5`, `6`, and `7`.
- **Why this is separate:** unlike a row where a specific player-meaningful
  action exists, removing one of these stubs would leave the stage with no
  recorded action at all. The settled rule for redundant stubs therefore does
  not decide these rows.

**OWNER DECISION — answered 2026-08-22 in 4.17**

- **Fork:** should a stage with no specific action record keep its generated
  completion stub, or should completing that stage record no action?

### 3.34 Source-audit test selectors can silently outlive their tests

Raised 2026-08-22 after an AST-backed scan compared qualified test selectors in
`memory-bank/source-audits` with the test methods currently defined under
`tests`.

- **Measured class:** at `2a1d454f`, the scan found **27 dangling selector
  occurrences**, representing **24 unique test names across 19 documents**.
  The dispatch reported 26 occurrences, 23 unique names, and 18 documents. The
  independently reproduced result adds
  `memory-bank/source-audits/combat-standard-spells-2026-06-23.md` and its
  `tests.test_main_menu_widget.MainMenuWidgetTest.test_combat_exposes_style_and_spell_controls`
  selector; that method is absent from the test AST, so the record keeps the
  disagreement rather than dropping it to match the earlier count.
- **Why this accumulated unseen:** `tools/audit_docs.py` checks documentation
  integrity but does not resolve qualified unittest selectors against the
  current test AST. A dangling-test-name check belongs in that audit.
- **Scope:** this is second-level work. Do not rewrite the historical source
  audits or change `tools/audit_docs.py` as part of the stub-consistency slice.

**Dangling selector snapshot (`2a1d454f`):**

- `memory-bank/source-audits/combat-mugger-2026-06-23.md`
  - `tests.test_combat_logic.CombatLogicTest.test_mugger_quantity_range_drop_rolls`
  - `tests.test_combat_logic.CombatLogicTest.test_mugger_drop_rolls_nested_minor_herb_table`
- `memory-bank/source-audits/combat-standard-spells-2026-06-23.md`
  - `tests.test_main_menu_widget.MainMenuWidgetTest.test_combat_exposes_style_and_spell_controls`
- `memory-bank/source-audits/combat-thief-2026-06-23.md`
  - `tests.test_combat_logic.CombatLogicTest.test_thief_quantity_range_drop_rolls`
  - `tests.test_combat_logic.CombatLogicTest.test_thief_drop_rolls_nested_minor_herb_table`
- `memory-bank/source-audits/combat-thug-2026-06-23.md`
  - `tests.test_combat_logic.CombatLogicTest.test_thug_drop_rolls_nested_minor_herb_table`
- `memory-bank/source-audits/combat-tutorial-starter-kit-2026-06-23.md`
  - `tests.test_main_menu_widget.MainMenuWidgetTest.test_bank_claims_collapse_locked_rows_into_summary`
- `memory-bank/source-audits/combat-v1-implementation-2026-06-23.md`
  - `tests.test_integration_smoke.TestIntegrationSmoke.test_hunter_supply_purchase_runs_once_and_switches_off`
  - `tests.test_integration_smoke.TestIntegrationSmoke.test_utility_fishing_bait_batches_without_skill_xp`
  - `tests.test_integration_smoke.TestIntegrationSmoke.test_utility_multiplier_runs_feather_scavenging_ticks`
- `memory-bank/source-audits/quest-biohazard-stage-detail-2026-06-22.md`
  - `tests.test_logic.TestLogic.test_biohazard_stage_gates_pigeons_mourner_distillator_and_guidor`
- `memory-bank/source-audits/quest-combat-resolver-contract-2026-06-22.md`
  - `tests.test_main_menu_widget.MainMenuWidgetTest.test_quests_tab_shows_generated_combat_gate_as_stage_blocker`
- `memory-bank/source-audits/quest-darkan-no-combatlevels-beast-stat-fallback-2026-06-22.md`
  - `tests.test_integration_smoke.TestIntegrationSmoke.test_quest_answer_resolves_no_combat_levels_beast_stat_gate`
- `memory-bank/source-audits/quest-dragon-slayer-stage-detail-2026-06-22.md`
  - `tests.test_main_menu_widget.MainMenuWidgetTest.test_quests_tab_allows_dragon_slayer_elvarg_combat_gate_selection`
- `memory-bank/source-audits/quest-dwarf-cannon-stage-detail-2026-06-22.md`
  - `tests.test_logic.TestLogic.test_dwarf_cannon_stage_gates_noncombat_items_actions_and_reward`
- `memory-bank/source-audits/quest-generated-pseudo-item-cleanup-2026-06-23.md`
  - `tests.test_logic.TestLogic.test_dwarf_cannon_stage_gates_noncombat_items_actions_and_reward`
  - `tests.test_logic.TestLogic.test_shield_of_arrav_black_arm_route_requires_key_and_isolates_variant_rewards`
  - `tests.test_main_menu_widget.MainMenuWidgetTest.test_quests_tab_shows_shield_black_arm_partner_key_action`
- `memory-bank/source-audits/quest-holy-grail-tree-gnome-stage-detail-2026-06-22.md`
  - `tests.test_logic.TestLogic.test_holy_grail_stage_gates_excalibur_titan_and_holy_grail_handin`
- `memory-bank/source-audits/quest-merlins-crystal-stage-detail-2026-06-22.md`
  - `tests.test_runtime_actions.TestRuntimeActions.test_quest_answer_resolves_merlins_crystal_mordred_before_stage_progress`
- `memory-bank/source-audits/quest-priest-in-peril-stage-detail-2026-06-22.md`
  - `tests.test_logic.TestLogic.test_priest_in_peril_blocks_on_source_backed_stage_gates_and_consumes_essence`
- `memory-bank/source-audits/quest-sheep-herder-stage-detail-2026-06-22.md`
  - `tests.test_integration_smoke.TestIntegrationSmoke.test_quest_answer_progresses_sheep_herder_feed_gate`
  - `tests.test_main_menu_widget.MainMenuWidgetTest.test_quests_tab_shows_sheep_herder_current_stage_blocker`
- `memory-bank/source-audits/quest-stage-gates-catalog-wide-2026-06-22.md`
  - `tests.test_main_menu_widget.MainMenuWidgetTest.test_quests_tab_shows_generated_combat_gate_as_stage_blocker`
- `memory-bank/source-audits/quest-stage-no-stage-closure-2026-06-22.md`
  - `tests.test_main_menu_widget.MainMenuWidgetTest.test_quests_tab_shows_generated_combat_gate_as_stage_blocker`
- `memory-bank/source-audits/quest-witchs-house-stage-detail-2026-06-22.md`
  - `tests.test_integration_smoke.TestIntegrationSmoke.test_quest_answer_resolves_witchs_house_first_form_combat_gate`
  - `tests.test_runtime_actions.TestRuntimeActions.test_quest_answer_resolves_witchs_house_first_form_before_stage_progress`

- **Second-level follow-up (2026-08-24):** Source-audit verification
  snapshots also pin historical run totals beside mutable commands. For example,
  `quest-witchs-house-stage-detail-2026-06-22.md` still says `ran 18 tests` after
  two retired selectors with no replacement were removed from that command.
  Audit result-count drift separately; this selector-existence slice does not
  rewrite historical totals.

### 3.35 King’s Ransom assigns the animate rock scroll to the wrong quest step

Raised 2026-08-22 while repairing the missing stage-1 action emitter. The live
row says `Recover the animate rock scroll during the Sinclair Mansion
investigation`, but both primary quest evidence and the pinned period guide put
that handoff much later. Darkan
`src/main/java/com/rs/game/content/quests/kingsransom/KingsRansom.kt` at commit
`38d66e0b7` issues item `4428` from Wizard Cromperty only at stage `55`, after
the Holy Grail is recovered; the pinned `King's Ransom` revision `oldid=6548731`
(`2012-11-12T01:02:00Z`, “Freeing King Arthur”) says the same. Rev-727, rev-742,
and game-main independently confirm item `4428` as `Animate rock scroll`, but
do not support the Sinclair Mansion timing.

The sourcing contract forbids manufacturing reachability for a contradicted
stage action, so the emitter repair is blocked. Decide whether to replace the
action with the sourced Cromperty handoff inside the current coarse stage map,
or first replace King’s Ransom’s six generated checkpoints with source-backed
stages. Until then, stage `1` keeps its missing specific action and the quest is
not claimed finishable.

## 4. Answered decisions

### 4.1 Grand Exchange offer-slot count — answered 2026-07-19

The design records asked for eight player offer slots. The pre-cutoff wiki
revision gives six slots to members and two to free players.

- Answer: use six slots. Period parity wins.
- Authority: `memory-bank/grand-exchange-slot-count-supersession-2026-07-19.md`

### 4.2 Grand Exchange price buttons — answered 2026-07-25

The owner remembered the buttons as additive. The period client script compounds
off the shown price.

- Answer: use the recovered client behaviour. The owner asked for whatever the
  real game does, and the cache gives it.
- Authority: `memory-bank/source-audits/ge-offer-price-controls-2026-07-24.md`

### 4.3 Clan Wars free-for-all portals — answered 2026-07-25

The settled competitive record collapsed both portals into one safe skirmish.
The period had a white portal and a red portal.

- Answer: **ship both portals as explicit modes.** White uses safe death. Red is
  genuinely dangerous: it loses every carried and worn item except the one that
  Protect Item saves, creates no gravestone, forbids teleport escape, and clamps
  extreme and Overload boosts on entry.
- Red reuses the dangerous-death path that The Crucible already uses. Do not
  build a second one, and do not add a gravestone or partial-loss rule. The owner
  rejected the softened version explicitly.
- **Implementation note, checked in the code on 2026-07-25.**
  `logic_pure/logic_pure_combat_model.py:730` `_combat_apply_pvm_death` already
  does the hard half correctly: it removes worn equipment and protects the single
  highest-value slot when Protect Item is active. But it **always** writes the
  lost items into `combat_grave`, and pushes an older grave into `death_office`.
  There is no variant that destroys the items.
  The red portal must destroy them. Reusing this function unchanged makes a red
  death recoverable and silently reverses the decision above. Add a no-grave mode
  rather than accepting the default, and make a test assert that a red-portal
  death leaves both `combat_grave` and `death_office` empty.
- The purple team mode stays the settled bounded team-score race.
- Source: RuneScape Wiki `Clan Wars`, oldid `6288405`, 2012-09-24.
- Unblocks: the Clan Wars family, which had no module at all.

### 4.4 Daily Challenges queue and reroll — answered 2026-07-25

Our record asked for one challenge per 240-card day plus a skip or reroll. The
cutoff revision was re-read live during this decision and contradicts it.

- Answer: **use the period system.** Up to five challenges are active at once,
  one new challenge arrives each 240-card day, and the oldest is removed when a
  sixth would be added. One challenge can be pinned at a time.
- **There is no skip and no reroll.** The revision does not mention either. Our
  record invented that action; it does not ship.
- Maxed-skill blocking is an opt-in the player requests per skill from the
  Quartermaster, not automatic and not a blanket switch.
- Source: RuneScape Wiki `Challenge System (historical)`, oldid `6579729`,
  2012-11-19, one day before the cutoff. Quoted: "if the list exceeds 5
  challenges, the oldest challenge is removed from the list"; "Only one task can
  be pinned at a time"; "players may choose not to receive new challenges in
  their max level skills. This is not a blanket turn off".
- Unblocks: the Daily Challenges family.

### 4.5 Treasure Trails clue ownership — answered 2026-07-25

The settled contract allowed one clue per tier. The period allowed one clue in
total.

- Answer: **one clue across every tier.** A new clue can arrive only when the
  player holds none in inventory, bank, or Kingdom Management resources.
- Caskets stay outside the ownership check, so a finished trail opens normally.
- The one-per-tier rule is a 2015 mechanic. It reached our contract by
  anachronism, not by a decision, and it does not ship.
- Source: RuneScape Wiki `Treasure Trails`, oldid `6473708`, 2012-10-26.
- Unblocks: the first complete Easy Treasure Trails slice. The easy-clue
  selection and casket reward rolls stay `source_blocked` separately.

### 4.6 Duel Arena tournament mode — answered 2026-07-25

The settled competitive record required period Duel Tournaments. The cutoff
revision was re-read live during this decision: "With the Wilderness & Free trade
updates on 1 February 2011, the tournaments were removed from the game."

- Answer: **remove Duel Tournaments.** They did not exist for the last 21 months
  of the period, so they fail the same cutoff test that removed
  fletch-javelin-construction and the Chaos Temple altar.
- Ship free challenge duels against bounded simulated opponents, the eleven
  configurable rule presets, safe death, stat restoration, and the win-count
  Duellist's cap progression.
- Staking stays excluded by the settled contract, so the activity creates no
  invented coin faucet. The owner declined to reopen it.
- Source: RuneScape Wiki `Duel Arena`, oldid `6398696`, 2012-10-14.
- Unblocks: the Duel Arena family.

### 4.7 Fish Flingers Master Angler — answered 2026-07-25

Our six-review event length fixed perfect tackles at exactly four forever, so the
sourced Master Angler medal (six perfect tackles) could never be earned and Team
Player (six assists) was nearly unreachable. Measured effect: exactly 1.00 medals
per event, putting the 500-medal tackle box 3,000 reviews away.

- Owner: "whatever is most faithful feeling".
- Answer: **lengthen the event to eight reviews.** The medal thresholds are
  sourced (oldid 6529096); the event length is our own pacing abstraction, which
  this family's audit states outright. So the abstraction bends and the source
  does not.
- At eight reviews a flawless event yields exactly six perfect tackles, so all
  four sourced medals are reachable and no sourced number moved. The discovery
  ramp is unchanged — bait, hook and weight still land on the first three
  reviews — the event simply runs two more at full efficiency.
- Rewards scale with fish caught, so the longer event earns proportionally more
  rather than diluting the pace.

## 5. Cross-cutting defects found on 2026-07-25

These are not design decisions. They are one defect each, showing up in many
families, and each is cheaper to fix once than family by family. The frontier
recomputation reported them as separate per-family failures; they are not.

### 5.1 Direct actions have no undo (breadth criterion 5)

`__init__.py` holds 31 `_apply_*_command` handlers that mutate or persist the
save. **None of them registers a direct-action undo snapshot.** The only code
that creates one is inline inside `resolve_review_context_action`
(`__init__.py:574-625`), which serves the reviewer context strip alone.

The frontier audit reported this as a criterion-5 failure in Shooting Stars,
Sorceress's Garden, Big Chinchompa, Livid Farm and Warriors' Guild. Those are
five symptoms of one missing seam. Extract the snapshot, custom-undo-entry and
restore logic into a shared wrapper, route the mutating handlers through it, and
five families advance at once — with every later family getting undo for free.

Do this before shipping more families. Each family built on the current seam adds
another handler that must be retrofitted.

### 5.2 Post-cutoff art — measured, and mostly deliberate

**This entry replaces an earlier version that called the art a defect needing a
provenance check. That was wrong, and the numbers say so.**

`assets_provenance.json` holds 3,665 entries. 3,026 of them (83%) carry a
post-cutoff timestamp. A check that failed on "timestamp after 2012-11-20" would
therefore fail most of the asset library, which makes it useless as a gate.

The breakdown is what matters:

| source_wiki | count | what it means |
| --- | --- | --- |
| `osrs` | 1,518 | Old School launched in 2013, so every OSRS image is post-cutoff by construction. Using it is a deliberate visual choice, not drift. |
| `rs3` | 1,499 | Modern RS3 art. This is the bucket worth caring about, because RS3 reworked graphics heavily after EOC. |
| `*-visual-fallback` | 9 | Already labelled as fallbacks. |
| pre-cutoff (`rs3`, `rs3-period`, `rs3-fandom-period`) | 639 | Period art. |

The two images the frontier audit named are in the modern-RS3 bucket:
`woodcuttingitems/evil_tree_kindling.png` (2020-11-24) and
`runecraftingitems/wicked_hood.png` (2019-12-01).

**Recommendation: defer this, and do not treat it as a breadth blocker.**
Replacing 1,499 modern-RS3 images is exactly the "slow data harvesting" the
programme says to defer until every family is mechanically complete. Blocking
Evil Tree and Wicked hood on criterion 7 while thirty families have no mechanics
at all inverts the programme's own priority.

When it is taken up, the useful gate is narrow rather than global: assert that
the small set of **visible family and activity icons** uses period or OSRS art
rather than modern RS3, since those are the images a player actually looks at.
A blanket provenance check is not the tool.

## 5. What this round showed about our records

Two of the four answers came from re-reading the period source during the
decision, and both times the source contradicted a settled record of ours:

- Daily Challenges: our skip and reroll action does not appear in the source at
  all. We invented it.
- Duel Arena: our record required a feature Jagex had removed 21 months before
  the cutoff.

A third, Treasure Trails, carried a 2015 mechanic into a 2012 product.

Three of four conflicts were our error, not a source ambiguity. When a settled
record and a pinned revision disagree, re-read the revision before assuming the
record won an argument.

### 4.8 Pass 3 of the playtest notes — answered 2026-07-26

The owner reviewed a running build and answered five forks. Two of them overturn
his own earlier records, which is noted at each.

**The always-visible strip shows only what is live.** Skill experience bars appear
for the running activity, the Grand Exchange fills drawer appears while an offer
is open, and nothing holds a permanent seat — except a compact badge on the left
for Distractions and Diversions and for Farming, which persists and opens a small
status popover. Clicking a line in that popover goes to the activity. This is what
stops the strip from becoming a second cluttered rectangle.

**The Agility panel's seventeen buttons split four ways.** Ticket redemptions,
claims and herb purchases move to the reward-shops area of the shop interface.
The Agility cape moves there too, with every other skillcape. Named buyers get
their own section in the shop interface, so selling a Pyramid top happens at
Simon Templeton for the sourced 1,000 coins instead of at an unlabelled button.
What remains on the panel is one control row, present only while an activity runs.

**Skillcapes are passive, auras are activated.** The rule is the cooldown: a
skillcape has none, so its boost simply holds while the cape is worn, and the
"Activate cape" button does not exist. An aura has one, so it needs a real
control. Auras get their own inventory inside the equipment tab with an activate
button, which is where Surefooted belongs — it is already an aura and already has
`surefooted_cooldown_reviews`.

The shipped cape behaviour was invented: it granted a +1 Agility boost for exactly
ten actions. The period skillcape boost is passive while worn and cannot be used
from the inventory at all.

**Population is never user-facing, and grows per activity.** SUPERSEDES the
2026-07-10 record, which granted advanced mode "preferred starting sizes and a
quiet/normal/busy population", and amends
`simulation-computation-budget-contract-2026-07-17.md`, whose event-seeded ceiling
varies "±20% around the selected Quiet / Normal / Busy profile". There is no
selected profile any more. Each activity grows its own population with the
contract's existing fuzziness — the time-of-day envelope, the seeded ceiling,
midpoint and steepness shifts, and phase noise — and the shared
`world_population_profile` stops being a player dial.

**Advanced mode leaves the shooting star.** SUPERSEDES the same 2026-07-10 record.
Choosing which star sizes spawn is a capability no player ever had, and there is
no case where a player would decline the star in front of them. The star the
simulation produces is the star you mine.

**Leave activity behaves like every other activity.** Agility alone uses a generic
`leave_activity` command while every other family uses its own `abandon`. This is
a behaviour inconsistency, not only a visual one.

### Open decisions queued by the pass-3 shop-UI work — 2026-07-26

1. **Where do the other skillcapes come from?** The pass-3 record moves every
   skillcape into the shop interface, but Agility's is the only cape purchase
   that exists (`purchase_agility_cape`); no other cape is obtainable today.
   Recommendation: as each cape becomes obtainable, give it a sourced master
   seller in the Shop tab's Skillcapes subsection (period: the skill's master,
   99,000 coins, cape and hood), and keep the Agility row as the template.
   The section is built and labelled; only Agility has a row.

2. **Resolved — the Spria chathead exists before the cutoff.** The complete
   MediaWiki upload history for canonical `File:Spria chathead.png` includes
   revision `2012-01-29T12:46:43Z` with SHA-1
   `ee75d74b7f4d6f979914593b2c4c015ec0d301ee`. The card now swaps to Spria's
   own registered face after While Guthix Sleeps; it never retains Turael's
   face while naming Spria.

### 4.9 Post-diary grill — answered 2026-07-27

Four forks closed in one sitting.

**The eight rejected condition kinds ship.** The workflow's design judge dropped
them as "too thin to be worth their evaluation surface", but every one reads
durable state the game already records, and the contract contains no
fewest-kinds rule — its rule is to preserve every task whose translation stays
recognisable. Authority: "I just want whatever I designed." Expected recovery is
about 18 tasks (310 to ~328).

**Narrow telemetry ledgers are approved** for the ~56 remaining recordable feats:
finer keys on existing ledgers (per-variant kills, per-shop transactions), added
only where a contract task needs them. Not a new system.

**Dungeoneering follows the parked-XP pattern.** `pending_skill_exp_rewards`
already parks XP for unimplemented skills; Dungeoneering joins it, plus stub
telemetry ledgers so its counters accrue now. The cape and the 25-skill Max gate
then clear by construction the day the skill ships.

**The 140-threshold ladder stays as hidden substrate.** It is instrumentation the
semantics clauses and the v88 migration read, not player-visible content.

### 4.10 Skillcape boost mechanic — answered 2026-07-27

- Answer: reshape D13 to the verified worn `Boost` option's visible +1 temporary
  boost, ported as full uptime while worn because AnkiScape has no real-time
  decay clock. Do not add an activation button.
- Visible boosts take the larger value, so an Agility cape does not stack its +1
  on a +3 potion. Invisible familiar boosts add after the visible boost.
- Re-measured after the arithmetic fixes: **49 shipped roll paths still change**
  between 99 and the cape's 100 — 43 Hunter, 3 Firemaking, 2 Thieving and 1
  Cooking. The blast radius stands, but it now flows through boost semantics.
- Authority:
  `memory-bank/source-audits/skillcape-mechanics-verification-2026-07-27.md`.

### 4.12 Gravestone expiry consequence — implemented recommendation, owner review pending

- **Fork:** At the 2012-11-20 cutoff, an unretrieved gravestone ultimately exposed/dropped its contents and then deleted them; the paid Death's Office item-reclaim system is a later mechanic and is not the period expiry consequence.
- **Recommendation implemented:** Expired AnkiScape gravestones permanently lose their held items. Keep the existing Death's Office bridge isolated to its pre-existing stacked-grave behavior until that subsystem receives its own source-parity replacement.
- **Evidence:** Darkan `GraveStone` expiry adjusts remaining public/delete time and finishes the grave rather than transferring items to paid reclaim; `memory-bank/source-audits/combat-death-office-reclaim-2026-06-23.md` records that 2011Scape has no full gravestone plugin and that the current Death's Office fee is explicitly an AnkiScape bridge. The rev-727/game-main local evidence supplies no paid expiry reclaim path.

### 3.22 Dominion Tower — the tower-only reward items are obtainable but thin — implemented recommendation, owner review pending

- **Fork:** The three dominion weapons, the four two-dose tower potions, the
  three bombs and the help horn are all real period rewards, but the period
  record describes their effects and never quantifies most of them. The
  crossbow's hundred shots, the sword's five minutes of combat, the diminutive
  bomb's tenth of current lifepoints, the horn's five charges and the scorpion
  meat's 220 healing are exact; the weapons' combat bonuses, the massive and
  colossal bombs' damage, and the staff's hit budget are stated nowhere.
- **Recommendation implemented:** the weapons are power-ups a player activates
  for a match rather than equipment with a slot, because no source gives them a
  bonus block to equip. They carry their sourced charge budgets and a single
  registered damage multiplier, and every one of them keeps the sourced
  Xp-book exchange as a second real sink.
- **What would change it:** a period item revision with a bonus block, or a
  decoded interface script for the arena weapon rack.

### 3.23 Dominion Tower — Tarn Razorlor is gated on a miniquest the ledger has no room for — closed 2026-07-29, the ledger landed

- **Fork:** The tower's class H includes Tarn Razorlor and his terror dogs, but
  its gate is The Lair of Tarn Razorlor, a *miniquest*. The tower's own list of
  thirty-eight quests does not include it, and AnkiScape's quest ledger carries
  the 194 pre-EOC quests with no miniquest rows at all.
- **What shipped:** the encounter row is present and gated on
  `lair_of_tarn_razorlor` exactly as the period gates it, so it lights up by
  itself the day the ledger grows miniquests. Until then it was the one boss of
  forty-eight a player could not reach, and it belongs to no reward set, so no
  reward was blocked by it.
- **Resolution (2026-07-29):** section 4.14 item 1 chose the minimal miniquest
  ledger, and it landed — the two rows are in `QUESTS`, the tower's class-H gate
  resolves off the completed miniquest row, and the boss count is whole again.
  The no-reward-set claim was re-checked against `DOMINION_TOWER_GLOVE_SETS` and
  still holds. Both facts are pinned by
  `tests/test_miniquest_ledger.py::TestLairOfTarnRazorlor`; the ledger's own
  sourcing lives in `source-audits/miniquest-ledger-2026-07-29.md`.

### 3.24 Dominion Tower — a defeat's Dominion Factor cost is nowhere in the record — implemented recommendation, owner review pending

- **Fork:** The tower page says plainly that "Losing a fight reduces the
  player's dominion factor" and advises cashing out before a fight you expect to
  lose. No pre-cutoff revision, no guide page and no Darkan code gives the
  amount; Darkan's own loss path reduces nothing at all.
- **Recommendation implemented:** a defeat forfeits the factor the last won
  round paid, which is the smallest reduction that makes the article's own
  advice rational, and it is registered as
  `dominion_tower.loss_factor_penalty`.
- **Alternatives if you prefer:** a flat percentage of the banked factor, or a
  reset to zero. Both are inventions of the same size; this one is the least.

### 4.13 Pass 4 of the playtest notes — owner directives, 2026-07-28

Source: `~/Downloads/ankiscape notes.rtfd` (pass-4 section plus its screenshot
of the Arachnophagia modal over a mackerel cook). These are directives, not
open forks, except where marked.

1. **The review overlay must never cover card material,** the footnotes
   especially. Reposition or shrink; the card wins every collision.
2. **The merged D&D·Farming badge is overruled.** Pass 3's single
   `ReviewStatusBadge` (rider on 3.15) is not what the owner wanted: the two
   badges stay separate, both sit to the **left of the XP-bar area** rather
   than on top of it, and the current sometimes-pops-left behaviour is a bug
   to remove, not a fallback to keep.
3. **An event-log drawer replaces missed popovers.** Last ten actions by
   default, lazily expandable indefinitely, timestamped in "x reviews ago"
   units, containing exactly what the floating popovers emit — XP drops
   included. It is a drawer, like the GE fills drawer.
4. **The Equipment tab shows current points** — life, Prayer, and whatever
   else is live (summoning points).
5. **Arachnophagia fired while cooking mackerel.** The gnome-cooking
   achievement predicate triggers on the wrong target; it must fire only on an
   actual Spider on a stick cook.
6. **Favoriting a D&D happens by right-click on its row** (add/remove). The
   pass-3 star on the detail card was not discoverable and is not the asked-for
   surface; keep or drop it, but right-click must work.
7. **Treasure Trails start from the Bank:** right-click a clue scroll to
   start. The existing activity-target UI survives but locks behind a
   bank-started trail.
8. **"Weren't there supposed to be extra cooking options?"** — investigation
   item: the twenty gnome cooking targets merged 2026-07-28; determine why the
   owner's build did not show them (gate, ordering, or build staleness) before
   changing anything.
9. **Lag, again.** Pass-1 noted menu load; pass 4 reports in-review lag and
   suspects backend calculation cost. Profile before fixing.

### 3.25 Dungeoneering — starter Herblore chain funding — implemented per 4.14: guardian drops

- **Fork:** the ratified contract requires the quarantined starter Herblore
  chain to be mechanically reachable inside a floor, but the audit's pinned
  Smuggler prices (Vial of water 10, Void dust 1,000) exceed anything a
  natural starter floor can earn by selling gathered goods (~120 coins).
  The period game funded floor purchases through monster coin drops, whose
  starter-floor amounts no source pins.
- **Recommendation implemented:** on C5+ floors for players with Druidic
  Ritual complete and Herblore 5, critical-path guardian-room enemies split
  1,010 coins, registered as
  `PLACEHOLDER(dungeoneering.starter_guardian_coin_drops)` — the smallest
  disclosed translation that makes the contract's chain real without letting
  optional rooms dilute or extend the payout. C1-C4 and players who cannot run
  the chain receive none because its Smuggler spend is unavailable to them.
  Session coins evaporate at floor end like everything else. A decoded period
  drop table for the Frozen-floor guardians would retire the placeholder
  entirely.

### 3.26 Jungle Potion — retain the rock safeguard or restore source stage semantics — answered 2026-08-22 in 4.17

- **Source behavior:** Darkan permits a search only when
  `questStage == requiredStage` and advances that stage only when Trufitus
  accepts the clean herb. If the herb is lost, the same search remains
  available until turn-in.
- **Shipped behavior:** AnkiScape splits search and turn-in into separate review
  stages. The search stage advances when the grimy herb is found, making that
  search one-shot until the quest advances again. The current safeguard keeps
  Shattered Heart from replacing any of the five clean herbs before quest
  completion.
- **Owner decision:** either retain the shipped exemption, or remove it and use
  the source-faithful stage model in which each search remains reachable until
  its matching turn-in completes. No behavior changes until the owner chooses.
  Evidence: `memory-bank/source-audits/quest-jungle-potion-playable-2026-08-13.md`.

### 4.14 Grill of 2026-07-29 — six answers

1. **3.23 answered: minimal miniquest ledger now.** Miniquests become a
   flagged category on the existing quest ledger — same storage, same unlock
   engine, separate UI grouping — starting with exactly the two consumers:
   Hunt for Surok (unblocks Bork) and The Lair of Tarn Razorlor (lights the
   Dominion class-H boss). No up-front catalog sweep; other miniquests join
   as content needs them.
2. **3.25 answered: guardian coin drops replace the cache.** Same registered
   placeholder magnitude, but the period mechanism — guardian-room enemies
   drop the coins that fund the starter Herblore chain. The resource-room
   cache is to be removed when this lands.
3. **3.15 rider affirmed: favourites stay Distractions-only.** Rows without
   live-event state get no right-click entry; the badge remains a notifier,
   not a bookmark list.
4. **4.12 confirmed:** expired gravestones permanently lose their items; the
   Death's Office bridge keeps only legacy stacked-grave behaviour.
5. **3.22 and 3.24 confirmed:** dominion weapons stay activated power-ups
   with sourced charge budgets; a defeat forfeits the last won round's
   Dominion Factor.
6. **3.19 confirmed:** the Gnome Restaurant ticket card stays; the order
   board alternative is retired.

Follow-up harvest (not a fork): the Slayer off-task XP scoping lead from
2026-07-15 — pin a pre-cutoff Slayer oldid plus Darkan/game-main kill
handlers; if confirmed, amend the contract sentence to "no assignment
progress, and no Slayer XP for monsters without a Slayer-level requirement."

Build queue consequences, sequenced behind the two parked codex items:
the miniquest ledger with its two rows, and the 3.25 guardian-drop reshape.

### 4.15 Grill of 2026-07-30 — design-gap answers

1. **Conquest squad budget stays 1,000** (registered placeholder, 800
   discrepancy noted). The owner defers on Conquest specifics.
2. **Event-log retention: large bounded window.** Keep the last ~2,000
   events, trimmed oldest-first on write; "indefinitely" governs drawer
   scroll depth, not immortal storage.
3. **Tarn Tower gate ratified:** Haunted Mine per the pinned source; the
   Lair miniquest stays optional for the fight.
4. **Kinship reopens fork 14: party simulation is wanted.** The owner
   designed a fake-player simulation suite in Darkan and wants a flattened
   port giving AnkiScape simulated party members (player-chosen count),
   restoring real correspondence for Medic-type classes. Deliverable:
   a DESIGN PACKET ONLY for owner review before any implementation —
   the flattened-port proposal, per-class effect mapping with the party sim
   in place, and a propose-and-review analog table for classes that remain
   without correspondence (smallest effect in the spirit of the sourced
   description, labeled as an AnkiScape analog; nothing ships unsigned).
   Requires coordination with the Darkan restoration thread over the suite.
   Until the packet is approved, the honest no-effect display stays.

### 3.27 Shattered Heart output-replacement eligibility — answered 2026-08-22 in 4.17

- **Current layering:** the four `shattered_heart_output_items=` call sites are `runtime/runtime_actions_production.py:693` for Herblore, `runtime/runtime_actions_gathering.py:668` for Hunter, `runtime/runtime_actions_gathering.py:911` for Woodcutting, and `runtime/runtime_actions_gathering.py:1061` for Mining. Hunter derives tradeability eligibility, Woodcutting and Mining pass `primary_outputs` raw, and Herblore carries the hand-written Jungle Potion exception.
- **Decision:** determine whether output-replacement eligibility belongs in `logic/shattered_heart_logic.py:307`'s shared hook rather than in each caller. A future untradeable output under any other rock-eligible skill would otherwise silently regain the defect. This slice keeps the wider shared-hook change out of scope.

### 4.16 Jadinko secondary drops need independent tables — decided 2026-08-21

- Darkan commit `7e7d67b` rolls three independent secondary tables for Common,
  Guthix, Saradomin, Zamorak, Shadow, and Diseased jadinkos. One Hunter action can
  therefore award more than one secondary item. The current pure Hunter contract
  has one `secondary_drop_chance` and one `secondary_outputs` list, so merging the
  tables would change both marginal chances and same-catch combinations.
- Do not approximate the missing rolls and do not widen the pure contract inside
  the grimy-herb slice. Each affected row implements its vine-herb table and marks
  the exact omission as
  `PLACEHOLDER(hunter.jadinko_multi_secondary_tables)`.
- The smallest follow-up is to replace the single secondary slot with an ordered
  tuple of tables, each carrying its own chance and weighted outputs, and to pass
  one independent chance/pick pair per table through the pure action and runtime
  adapter. Existing one-table rows migrate one-for-one. Common then adds bush
  `14/256` and blossom `17/256`; Guthix, Saradomin, and Zamorak each add bush
  `6/256` and blossom `4/256`; Shadow and Diseased each add bush `8/256` and
  blossom `4/256`.
- **Implemented 2026-08-22:** `secondary_drop_tables` now preserves Darkan's
  source order and rolls each table independently through the pure Hunter action
  and runtime adapter. The six live rows carry the exact chances above; all
  existing one-table Jadinko rows migrated one-for-one. Real-kernel regressions
  prove all three secondaries can land on one catch. Source: Darkan commit
  `7e7d67b`, `data/npcs/drops/hunter/hunter_jadinko_{common,guthix,saradomin,zamorak,shadow,diseased}.json`
  and `data/npcs/drops/hunter/jadinko_sub/{hh_bush_seed,hh_blossom_seed}.json`.
  All six `PLACEHOLDER(hunter.jadinko_multi_secondary_tables)` markers are
  retired; Camouflaged remains separate under section 3.28.

### 3.35 Melee/ranged Vengeance parity — recorded fork, not scheduled

Raised 2026-08-23 by the Pass 11 `runes` slice. The owner's ruling gates all
rune handling on an effective magic combat class, so Vengeance is disabled end
to end for melee and ranged. Period parity note: at 94 Magic on Lunars, a
melee player could carry Vengeance runes and cast it beside melee swings. If
the owner ever wants that tactic, the fork is a deliberate carve-out from
ruling 4 of the Pass 11 brief: a Vengeance-only rune-carry path for non-magic
classes. Until then the current behavior is settled and correct.

### 4.17 Owner rulings of 2026-08-22 — four forks closed

The owner ruled these through the design thread on 2026-08-22. Each ruling
carries full authority.

1. **3.32 answered: Option A.** A stage whose `required_routes` has exactly one
   possible value is a step, not a choice. The existing stage auto-action
   mechanism satisfies it. `QuestChoice` stays only for real forks with two or
   more options. Do not register one-option route buttons. This ruling reopens
   the four incomplete "impossible to finish" repairs (Biohazard, Dealing with
   Scabaras, Holy Grail, Dwarf Cannon): convert their single-valued routes to
   auto-steps, then the rest of the 30-quest class in 3.32's snapshot.
2. **3.33 answered: harvest real actions.** The six Dealing with Scabaras
   stub-only stages are a sourcing gap, not a design fork. Recover the real
   stage steps through the evidence order (Darkan first) and replace each stub
   with sourced action text. A stage keeps its generated stub only when the
   evidence order is exhausted.
3. **3.26 answered: source-faithful stage model.** Jungle Potion returns to
   Darkan semantics: each search stays reachable until its matching turn-in
   completes. The shipped one-shot search model and the Shattered Heart
   herb-protection exemption are removed together.
4. **3.27 answered: shared hook.** Output-replacement eligibility moves into
   the shared hook at `logic/shattered_heart_logic.py:307`. The four callers
   (`runtime/runtime_actions_production.py:693`,
   `runtime/runtime_actions_gathering.py:668`, `:911`, `:1061`) route through
   it, so a future rock-eligible skill cannot silently regain the
   untradeable-output defect.

### 4.18 Fable is barred for the remainder of this goal — ruled directly by the owner

The owner ruled this directly to the orchestration seat on 2026-08-23, not
through the design thread. It carries full authority.

- **Ruling, verbatim:** "Do not ever use fable again during this goal."
- **Scope:** the `fable` model seat, for every remaining slice of the active
  autonomous goal. It covers authoring, reviewing, judging, and any panel seat.
  It is not limited to a quota window, so a Fable reset does not lift it.
- **State when ruled:** Fable held no in-flight work. It had been the
  cross-lineage reviewer for batches three, four and five, and was already 5
  points past its window, so the practical effect is on future routing only.
- **Consequence for routing:** the cross-lineage reviewer seat for
  Ox Alpha-authored slices stays with Sol. Where a slice is Sol-authored and
  needs a reviewer of a different lineage, the remaining candidates are Opus and
  Kimi K3, both currently past their windows. If none is available, record the
  slice as quota-blocked rather than seating Fable or accepting a same-lineage
  review.

### 4.19 Fleet-wide Fable rule, relayed by a peer — does not loosen 4.18 here

A peer session (`claude-code-0c`, socket `uds:/tmp/cc-socks/89632.sock`) relayed
a standing owner ruling on 2026-08-23, citing fleet commit `2edbb0e` and the
design seat as relay.

- **Relayed rule:** Fable dispatches only on the owner's explicit approval for
  that specific task. Never automatically, never as a routine or default
  reviewer, and never as a self-chosen escalation. A work order that wants Fable
  is parked for the owner and other seats continue.
- **Stated cause:** overnight loops spent an entire Fable block on routine
  review dispatches.
- **Verification status:** UNVERIFIED from this seat. `2edbb0e` is not an object
  in the AnkiScape repository, and this seat cannot read the fleet repository
  that would contain it. It is recorded as relayed, not as confirmed.
- **Effect here: none.** Entry 4.18 is stricter and was ruled by the owner
  directly to this seat: Fable is barred outright for the remainder of this
  goal. A peer relay cannot loosen a direct owner ruling, so no Fable dispatch
  becomes available under 4.19 that 4.18 forbids. Where the two differ, 4.18
  governs this goal.
- **After this goal:** 4.18 expires with the goal and 4.19 does not, so the
  per-task approval rule is the standing constraint for later work. Confirm it
  against the fleet record before relying on it.

### 5.3 Quest reward strings can become inventory keys without semantic validation

Raised 2026-08-24 after two reward corrections exposed a catalog-wide parser
hazard. This entry records the class and the measurement disagreement below. It
is **not scheduled work** and is not a quest-by-quest task list.

- **Measurement disagreement at the instructed base:** at
  `8ec703a9bbceba7c4cb278b99155f1111ea189e4`, `QUESTS` contains `196`
  quests. Of those, `144` carry at least one final item reward. Flattening each
  `QuestDefinition.rewards` tuple as `(name, amount)` produced `318` reward
  occurrences, `294` distinct `(name, amount)` tuples, and `275` distinct
  names. Comparing those names with
  `{definition.storage_key for definition in core.constants.ITEM_DEFINITIONS}`
  found **0 undefined names**, not `269`. All `275` names are storage keys in
  the final `3,503`-row registry. The reported `269` and the earlier wrong
  `288` therefore do not reproduce on this base and are not adopted here.
- **Why a direct membership probe is false evidence:**
  `ITEM_DEFINITIONS` is a tuple of `ItemDefinition` objects, not a mapping or a
  set of strings. Testing either a reward tuple or a reward name directly with
  `value not in ITEM_DEFINITIONS` compares unlike types and flags every value.
  The catalog also self-registers raw quest reward strings:
  `data/quest_data.py:10078-10090` emits each raw `item_name`,
  `core/constants.py:1411` loads that output,
  `core/constants.py:2643-2655` merges it into extra item data, and
  `core/constants.py:2777` builds the final registry. The final registry is
  therefore not an independent validator of quest reward semantics.
- **Semantic shape of the `275`-name candidate pool:** this is a manual,
  one-bucket-per-name classification of all final reward names on this base. It
  is not a claim that all `275` are defects.
  - **`176` concrete item or currency-shaped labels:** examples are
    `Air talisman`, `Ammo mould`, and `Catspeak amulet`. These need source-level
    confirmation and canonical item identity; on this base all three examples
    already have final item definitions.
  - **`20` generic item families or bundles:** examples are `Arrowheads`,
    `Dagon'hai robes set`, and `Proselyte armour`. A true completion grant must
    expand to concrete items or move to the owning unlock system.
  - **`8` experience or activity-point labels:** examples are
    `2,100 Cooking`, `6,500 Prayer`, and `Zeal points`. `Construction` is in
    this bucket because Missing My Mummy stores it with amount `2,100`, even
    though Carnillean Rising also uses the same name once. These values belong
    in XP or activity-state data, not inventory.
  - **`64` unlock, destination, activity, NPC, spell, title, or other state
    labels:** examples are `Pyramid Plunder`, `Castle Wars`,
    `South of Brimhaven`, and `Varrock Museum`. These belong in unlock or
    activity state.
  - **`5` wiki-furniture strings:** examples are
    `File:Apmeken's tomb entrance.jpg`, `The concept art for Thalassus`, and
    `Expensive spices (necklace) (page does not exist)`. These should never
    enter runtime data.
  - **`2` prose fragments:** `A box trap.` and
    `20 noted Pure/Rune essence and the other items (from chasing Solus)`.
    These require a sourced replacement or removal, not an item definition.
- **Runtime consequence:** `logic_pure/logic_pure_quest.py:1468-1475` obtains
  the completion reward mapping and grants every row with the bare assignment
  `inventory[item_name] = inventory.get(item_name, 0) + _positive_int(amount, 1)`.
  It performs no
  definition lookup and no semantic type check. A reward string therefore
  becomes an inventory key when its quest completes. Self-registration means
  that adding a definition lookup alone would not reject the parser artifacts
  above.
- **Candidate-pool live-versus-latent split:** applying
  `re.fullmatch(r"^Complete .+ stage \d+ objective$", action)` to every
  affected quest's stage `required_actions`, then capturing the existing
  reachability closure's `completable_quests` set, split the `144` reward-bearing
  quests into **`112` generated-stub-blocked**, **`18` completable today**, and
  **`14` blocked by other gates**. The `18` live quests are A Soul's Bane,
  Biohazard, Black Knights' Fortress, Clock Tower, Cook's Assistant, Dwarf
  Cannon, Family Crest, Imp Catcher, Monk's Friend, Plague City, Rune
  Mysteries, Shield of Arrav, Stolen Hearts, Temple of Ikov, The Restless
  Ghost, Tree Gnome Village, Tribal Totem, and Waterfall Quest. The other
  `126` are latent at this base. Within the `99` obviously non-concrete names
  in the five non-concrete buckets above, `56` quests are affected: `51` are
  generated-stub-blocked, Biohazard is the only completable live quest, and
  Carnillean Rising, Deadliest Catch, Dealing with Scabaras, and The Tale of
  the Muspah are blocked by non-stub gates.
- **Reachability-audit blind spot:** the audit does not diagnose reward names.
  It measures blocked stage products and their missing actions, routes, items,
  tools, and combat gates at `tools/audit_item_reachability.py:442-470`, and it
  exports only `blocked_quest_stage_products` at
  `tools/audit_item_reachability.py:1363-1366`. For a completable quest it
  intersects reward names with the already self-populated registry and adds
  them as sources at `tools/audit_item_reachability.py:600-603`. It therefore
  cannot expose this class.
- **Established repair route:** use
  `QUEST_ITEM_REWARD_REPLACEMENTS_BY_ID` at `data/quest_data.py:4197-4206` to
  replace or suppress a quest's scraped item rows before
  `data/quest_data.py:8947-8953` builds its final rewards. Route experience
  through `QUEST_XP_REWARD_REPLACEMENTS_BY_ID`, and keep unlocks in their
  owning quest or activity state. Apply those corrections only after
  source-checking each quest; this record does not schedule them.
### 5.4 Fresh queue audit found five unblocked records — 2026-08-24

Raised by a full read of this file at
`8f96c02fcbf42d23fd9743af774d12e883418248`. The audit examined **35**
current or explicitly pending entries: **9 COMPLETE**, **7 DEFERRED DATA
DEPTH**, **14 BLOCKED** (**12 owner**, **2 source**), and **5 UNBLOCKED**.
The pending reward-name record is included because the dispatch names it, but it
is not in the audited tree: its heading exists only at
`a468d18a:memory-bank/design-thread-queue.md:1619` on
`goal/reward-artifact-record-2026-08-24` and its `8ec703a9` measurements are
stale against this base.

**COMPLETE — measured in this tree:**

- `### 3.11 The all-skills capes have 24 skills to ask for, and the period has 25`
  (`memory-bank/design-thread-queue.md:270`) — the live registry now measures
  `25` trainable skills and `25` skillcape rows, including Dungeoneering;
  `b60f2fcf` is an ancestor of the audited commit.
- `### 3.15 Does the reviewer badge list only favourited Distractions?`
  (`memory-bank/design-thread-queue.md:414`) — `b94de70b` implements the
  superseding pass-4 two-badge/right-click surface and 4.14 affirms
  Distractions-only favourites.
- `### 3.21 Gnome Restaurant: one delivery ticket, or an order-and-reward board`
  (`memory-bank/design-thread-queue.md:491`) — 4.14 confirms the ticket and
  `49769d21` is in the audited history.
- `### 3.29 Durable line citations need a mechanical drift check`
  (`memory-bank/design-thread-queue.md:586`) — `b5addc1d` adds
  `tools/audit_citation_drift.py`; the dispatch forbids running that tool, so
  this audit verified the closing commit and file instead.
- `### 3.30 Rune Mysteries stage 1 has no action emitter and blocks its dependants`
  (`memory-bank/design-thread-queue.md:605`) — `8aafd995` is present and the
  catalog now emits `Deliver the strange talisman to Sedridor`.
- `### 3.32 Thirty quests require routes that no player can select`
  (`memory-bank/design-thread-queue.md:774`) — the fresh reachability report has
  `rows_with_missing_required_routes=0`.
- `### 3.35 King’s Ransom assigns the animate rock scroll to the wrong quest step`
  (`memory-bank/design-thread-queue.md:1021`) — `fdbec823` is present and the
  live action is `Receive the animate rock scroll from Wizard Cromperty after recovering the Holy Grail`.
- `### 5.1 Direct actions have no undo (breadth criterion 5)`
  (`memory-bank/design-thread-queue.md:1161`) — `aefcc4ea` supplies the shared
  seam; a fresh static scan finds `80` `commit_direct_action(` call sites and
  `0` remaining `def _apply_*_command` handlers in `__init__.py`. The two
  remaining `_apply_` definitions in `runtime/runtime_actions_shared.py` are
  action-calculation helpers, not direct command handlers, and the plain lane
  exercises the migrated seams.
- `### Open decisions queued by the pass-3 shop-UI work — 2026-07-26`
  (`memory-bank/design-thread-queue.md:1275`) — the live registry measures all
  `25` skillcapes and all `25` sourced master-shop rows; Dungeoneering is no
  longer latent.

**DEFERRED DATA DEPTH:**

- `### 3.5 Two Crucible reward rows have nothing to act on`
  (`memory-bank/design-thread-queue.md:141`) — fissure travel and the Rogue-glove
  degradation family are omitted depth surfaces, with the glove charge count
  still unrecovered.
- `### 3.7 Activity-owned population base ceilings`
  (`memory-bank/design-thread-queue.md:200`) — activity-specific population
  statistics remain unrecovered; the mechanically complete fuzzy simulation
  uses the disclosed current ceilings.
- `### 3.8 How a geography-bound period task becomes a predicate`
  (`memory-bank/design-thread-queue.md:220`) — the alternative is the explicit
  per-task hand-curation pass, not missing breadth mechanics.
- `### 3.13 Shattered Heart has no recovered strange-rock rate table`
  (`memory-bank/design-thread-queue.md:316`) — the registered global placeholder
  preserves acquisition; per-skill rate precision is unrecovered depth.
- `### 3.17 Breadth-one follower supplies stay compact and explicit`
  (`memory-bank/design-thread-queue.md:378`) — widening the explicit Lobster
  pack to the ordinary food catalog is depth beyond the working trek loop.
- `### 3.18 Mage Training Arena ordinary dragonstone spawns in breadth one`
  (`memory-bank/design-thread-queue.md:391`) — the separately clocked timed spawn
  is the entry's declared catalog/depth pass.
- `### 5.2 Post-cutoff art — measured, and mostly deliberate`
  (`memory-bank/design-thread-queue.md:1177`) — wholesale modern-RS3 asset
  replacement is the entry's own deferred slow-data harvest, not a breadth
  blocker.

**BLOCKED — owner:** the full-file read found no later ruling for these exact
forks, so the implemented recommendation is not authority to close them.

- `### 3.1 Skeletal Horror wish lists are satisfied by a free button click`
  (`memory-bank/design-thread-queue.md:30`) — owner must keep the stand-in or
  park the boss behind real wish-list state.
- `### 3.2 Clan Wars purple portal — who gets a crossfire kill?`
  (`memory-bank/design-thread-queue.md:59`) — owner must choose the purple-team
  crossfire scoring rule.
- `### 3.3 Tears of Guthix — how many review beats one cavern visit is worth`
  (`memory-bank/design-thread-queue.md:89`) — owner must choose the
  ticks-to-reviews conversion.
- `### 3.4 Do No Evil's one-time elite clue can be lost permanently`
  (`memory-bank/design-thread-queue.md:116`) — owner must choose permanent loss
  or a pending-reward path.
- `### 3.6 The Supreme Champion's invulnerable phase is not modelled`
  (`memory-bank/design-thread-queue.md:168`) — owner must accept the disclosed
  omission or change event cadence.
- `### 3.12 New predicates overfill Ardougne Easy's twelve-task budget`
  (`memory-bank/design-thread-queue.md:303`) — owner has not ruled on the final
  twelve-row curation.
- `### 3.14 Shattered Heart conflicts on reacquiring a placed skill pair`
  (`memory-bank/design-thread-queue.md:339`) — owner has not chosen between the
  repeated lead rule and the stale blocking bullet.
- `### 3.15 Temple Trekking and Burgh de Rott Ramble share one surface`
  (`memory-bank/design-thread-queue.md:356`) — owner has not confirmed the
  one-card direction selector.
- `### 3.16 Route choice applies to each encounter, not the whole trek`
  (`memory-bank/design-thread-queue.md:366`) — owner has not confirmed the saved
  next-encounter policy.
- `### 3.19 Mobilising Armies' hourly rank cap has no clock to hang on`
  (`memory-bank/design-thread-queue.md:450`) — owner has not confirmed the
  `36`-review rolling window.
- `### 3.20 Winning by the primary objective can outrun the ten-order rank gate`
  (`memory-bank/design-thread-queue.md:472`) — owner has not chosen calibrated
  objective lengths versus a completion waiver.
- `### 3.35 Melee/ranged Vengeance parity — recorded fork, not scheduled`
  (`memory-bank/design-thread-queue.md:1538`) — only the owner can carve
  Vengeance out of the settled effective-magic-class ruling.

**BLOCKED — source:**

- `### 3.31 Forty-five quests require specific actions that no runtime path emits`
  (`memory-bank/design-thread-queue.md:633`) — the ordinary reachability report
  now exposes `0` specific missing actions and `131` generated-stub actions
  across `131` quests, but a fresh stage-by-stage catalog walk found **11** later
  specific actions behind at least one earlier missing generated stub. They are:
  `mournings_end_part_i` stage `3` `Have Oronwen repair the mourner trousers`;
  stage `5` `Use the rotten apple to sabotage the mourner food stores`;
  `spirits_of_the_elid` stage `2` `Cast Telegrab for the water channel puzzle`;
  `enakhras_lament` stage `5` `Cast Crumble Undead during the boneguard fight`;
  `in_aid_of_the_myreque` stage `6` `Enchant sapphire for the Myreque preparations`;
  `the_eyes_of_glouphrie` stage `3` `Collect a bucket of sap from an evergreen tree`;
  `cold_war` stage `2` `Build the clockwork penguin on a crafting table 3`;
  `the_fremennik_isles` stage `5` `Cure and stitch yak-hide armour` and
  `Make a Fremennik round shield`; `legacy_of_seergaze` stage `5`
  `Cast Enchant Level 2 Jewellery for the emerald preparations`; and
  `do_no_evil` stage `3` `Recover an m'amulet mould before making the monkeyspeak amulet`.
  Ruling 4.17 makes each earlier stub-only stage a source-harvest task and
  requires real-kernel progression from a normally started quest, so these
  later emitters cannot be proved before that source work lands.
- `### 3.33 Six Dealing with Scabaras stages use a generated stub as their only action record`
  (`memory-bank/design-thread-queue.md:932`) — stages `2` through `7` still have
  exactly one `auto_actions` value each, `Complete Dealing with Scabaras stage N objective`;
  ruling 4.17 requires sourced action text after the evidence order is exhausted.

**UNBLOCKED settled work remains:**

- `### 3.34 Source-audit test selectors can silently outlive their tests`
  (`memory-bank/design-thread-queue.md:952`) — a fresh AST scan found **36
  dangling occurrences**, **33 unique selectors**, and **23 documents**, not
  the recorded `27`/`24`/`19`. Add the qualified-selector check to
  `tools/audit_docs.py`, then repair the historical references against the live
  tests.
- `### 3.26 Jungle Potion — retain the rock safeguard or restore source stage semantics — answered 2026-08-22 in 4.17`
  (`memory-bank/design-thread-queue.md:1437`) — the owner chose the
  source-faithful search-until-turn-in model, but the catalog still alternates
  one-shot search and turn-in stages and
  `runtime/runtime_actions_production.py:694-700` still carries the pre-ruling
  Shattered Heart exemption. Reshape the five stage pairs and remove the
  exemption together.
- `### 4.15 Grill of 2026-07-30 — design-gap answers`
  (`memory-bank/design-thread-queue.md:1484`) — the requested Kinship party
  design packet does not exist, while the named Darkan dependency is available
  in current history at `d4d430606`, `fcad1e89d`, and `f2ed1d725`. Produce the
  flattened-port packet and per-class analog table; runtime implementation then
  waits for owner approval.
- `### 3.27 Shattered Heart output-replacement eligibility — answered 2026-08-22 in 4.17`
  (`memory-bank/design-thread-queue.md:1505`) — the owner chose the shared hook,
  but `apply_shattered_heart_skilling_hook_pure` still accepts caller-filtered
  `output_items` and the four runtime callers still own eligibility. Move the
  tradeability rule into the hook and route all four callers through it.
- `### 5.3 Quest reward strings can become inventory keys without semantic validation`
  (`a468d18a:memory-bank/design-thread-queue.md:1619`, pending integration) — on
  this audited base the fresh measurement is **196 quests**, **142
  reward-bearing quests**, **310 reward occurrences**, **288 distinct
  `(name, amount)` pairs**, **269 distinct names**, **3,502 final item
  definitions**, and **0 unregistered names**. Self-registration is therefore
  still not validation. The live Biohazard completion regression at
  `tests/test_logic.py:5203` affirmatively expects the non-item unlock
  `Combat Training Camp` in inventory. Rebase the record, source-classify the
  current candidate pool, and route non-items through item suppression, XP, or
  their owning unlock state instead of inventory.

**Deciding answer: YES.** The five UNBLOCKED entries above are settled work that
is not implemented. The autonomous goal is not finished on this tree.

### 4.20 Model fallback after an Ox Alpha outage — ruled directly by the owner

The owner ruled this directly on 2026-08-24 at 22:54 PDT, not through the
design thread. It carries full authority.

- **Ruling, verbatim:** "If Ox Alpha access disappears tonight, you can move to GPT models again."
- **Meaning:** when the `ox-alpha` model stops resolving, the orchestrator
  returns to the standard routing rubric without pausing the active goal. This
  agrees with the goal text and needs no further approval.
- **Effect on 4.18:** none. Fable stays barred for this goal under 4.18, which
  the owner also ruled directly. A GPT-model fallback does not reopen the Fable
  seat.
- **After this goal:** 4.18 expires with the goal. This ruling is an outage
  contingency and does not set standing model policy beyond the active goal.

### 5.5 Four quests grant conditional post-quest rewards unconditionally

Raised 2026-08-25 from the reward-work branch review. Four quests grant a reward
at completion that the source gives only after a later condition. Nothing
implements a one-time post-quest claim, so the runtime hands the reward over
unconditionally. Members, each with its citation:

- `cabin_fever` grants 10,000 Coins at completion. Cabin Fever,
  oldid=6533785: "10,000 coins (only if you speak to Bill Teach after the
  quest)".
- `rocking_out` grants Magical cage at completion. Rocking Out,
  oldid=6521879: "Receive Magical cage by talking to Bill Teach after the
  quest."
- `do_no_evil` grants Clue scroll (elite) at completion. Do No Evil,
  oldid=6587790: "Find one \"free\" Clue scroll (elite) with Ava's Alerter.
  This Clue scroll can be found in either Meiyerditch, on the Iceberg, in
  Isafdar or on Lunar Isle." See also blocked owner fork 3.4, which covers the
  same scroll's permanent-loss path.
- `the_golem` has no route at all to its six-gem throne reward. The Golem,
  oldid=6543894: "As an extra reward, use your chisel on Thammaron's throne -
  with a hammer in your inventory, to get six gems - 2 Rubies, 2 Emeralds, and
  2 Sapphires". Measured on the branch: all `the_golem` stage outputs are
  empty, no claims and no utility entries exist, and completion grants nothing.

**Why deferred, not fixed:** the first three quests over-grant today. Deleting
a real player-facing reward is the worse failure, so the class stays recorded
instead of patched blind.

**Needs an owner decision** on the mechanism before any slice work: a one-time
post-quest claim, a new action, or both. This entry is not scheduled work.

### 5.6 Roughly 44 non-item reward rows across 24 quests — typed reward model proposed, not decided

Raised 2026-08-25 from the reward-work branch review. About 44 reward rows in
24 quests name things that are not inventory items: currencies, locations, NPC
access, spells, emotes, and titles. Measured examples on the branch include
Karamja, Daemonheim, Fremennik name, Teleport to House, and Managing
Miscellania.

The reviewer's structural recommendation, recorded here as a proposal only: a
typed reward model that separates inventory items, wallets, unlocks,
locations, NPC access, spells, emotes, and titles before the catalog is
generated, instead of correcting names one at a time. Entry 5.3 documents the
parser hazard that makes row-by-row correction fragile.

This is an architecture decision for the owner and the design thread. Do not
schedule it as slice work.

### 5.7 Hunter tool stackability flags mark non-stackable tools stackable

Raised 2026-08-25 from the reward-work branch review. Pre-existing on canonical
main and unrelated to the reward work; it surfaced because a quest began
granting a box trap again.

`data/hunter_data.py:1513` sets `"stackable": item_name not in {"Marasamaw plant", "Rope"}`.
That marks every other Hunter tool stackable, including Box trap 10008, Bird
snare 10006, Butterfly net 10010, Noose wand 10150, Teasing stick 10029,
Rabbit snare 10031, and Small fishing net 303. The rev-742 cache gives Box trap
10008 as stackable=false. None of these tools stack in the period game.

Deferred with the rest of this round's records; no slice scheduled.
