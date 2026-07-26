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

### 3.1 Fish Flingers: two sourced mechanics have no reachable home

Found 2026-07-25 while verifying the Fish Flingers breadth-one slice. Both come
from the same cause — the settled six-review compression and the hidden period
distributions leave two sourced rewards with nothing to attach to. Neither was
invented around, so the family ships with them recorded instead.

**a. The Master Angler medal can never be earned.**
The source names four medals: Junior Angler at three perfect tackles, Master
Angler at six, Whopper at three big fish, Team Player at six assists. But
`logic/fish_flingers_logic.py:315` derives `perfect_tackles` as
`max(0, next_review - 2)` and the event ends at `next_review == 6`, so every
completed event yields exactly four. Master Angler's `>= 6` branch is therefore
dead code, Junior Angler is granted unconditionally, and the token term
`min(3, perfect_tackles // 2)` is a hard-coded 2 with no variance.

The audit at `source-audits/fish-flingers-loop-2026-07-17.md:80-84` already
predicted this and accepted it, saying the compression "does not fabricate a
six-perfect Master Angler medal". What it did not do is record that one of four
sourced medals becomes permanently unearnable, which is a real divergence.

- Option A, accept and document: leave three medals earnable, mark Master Angler
  as unreachable-by-compression in the audit, and delete the dead branch so the
  code stops implying otherwise.
- Option B, make perfect tackles cumulative across events rather than per-event,
  so six is reachable over two events. Cheap, but the source reads as a
  per-event award and this would be our invention.
- Option C, lengthen the event past six reviews so six perfect tackles fit.
  Faithful to the medal table and unfaithful to the settled compression, which
  every other part of this family is built on.
- **Recommendation: A.** The compression is settled and load-bearing; one medal
  is a smaller loss than reopening the event length, and B invents a rule.

**b. Weight — RESOLVED 2026-07-25, no decision needed.**
Removed rather than referred to you, because it was an invention rather than a
choice between two defensible readings.

The round added a `weight_modifier` to each species and location, accumulated a
`total_weight` across a session, persisted and clamped it, and printed it on the
card. Nothing else read it. That is the same inert-state defect the round existed
to fix.

Two things settled it. The name collided with a sourced term meaning something
else: "weight" in this family's audit is one of the three tackle controls — bait,
hook and weight — that the six-review ramp already discovers, so a future reader
would have taken the invented fish weight for the sourced tackle weight. And the
sentence describing it was added to the audit by the same change that added the
code, so the audit documented an invention instead of settling a design.

Both are gone, along with the assertions that pinned them. Removing an invention
is not a design decision, so this needed nothing from you.

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
