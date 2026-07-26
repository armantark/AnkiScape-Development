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
