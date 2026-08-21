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
### 3.4 Quest-awarded clue scrolls bypass the one-clue rule

Raised 2026-07-26 while building Easy Treasure Trails. Not a blocker: the Easy
family shipped without it.

The period allows one clue scroll in total (4.5), and the drop paths now enforce
it. One quest in the generated catalog awards a `Clue scroll (elite)` as an item
reward, and quest rewards do not pass through the ownership filter. A player can
therefore end a quest holding two clues.

- Option A: route quest item rewards through the same filter, so the clue is
  withheld while another is held.
- Option B: treat a quest reward as a period exception and let it through.
- Recommendation: **A**, for consistency with every other grant path. It was not
  implemented here because it is one level outside the Treasure Trails change and
  touches the quest reward pipeline that this family does not own.

Blocks: nothing. Worth answering before medium, hard or elite trails ship.

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
- Re-measured after the arithmetic fixes: **39 shipped roll paths still change**
  between 99 and the cape's 100 — 33 Hunter, 3 Firemaking, 2 Thieving and 1
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

### 3.26 Jungle Potion — retain the rock safeguard or restore source stage semantics — owner decision required

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

### 3.27 Shattered Heart output-replacement eligibility — owner decision required

- **Current layering:** the four `shattered_heart_output_items=` call sites are `runtime/runtime_actions_production.py:693` for Herblore, `runtime/runtime_actions_gathering.py:668` for Hunter, `runtime/runtime_actions_gathering.py:911` for Woodcutting, and `runtime/runtime_actions_gathering.py:1061` for Mining. Hunter derives tradeability eligibility, Woodcutting and Mining pass `primary_outputs` raw, and Herblore carries the hand-written Jungle Potion exception.
- **Decision:** determine whether output-replacement eligibility belongs in `logic/shattered_heart_logic.py:307`'s shared hook rather than in each caller. A future untradeable output under any other rock-eligible skill would otherwise silently regain the defect. This slice keeps the wider shared-hook change out of scope.
