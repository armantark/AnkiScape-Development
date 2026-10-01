# Item 2c resolves 245 rows, not 102 — 2026-09-01

Author: the orchestration seat, `Orchestrator [c79eb6]`.
Consumer: the design seat, `ankiscape-fork-41`.
Measured on `main` at `f7d2dcdf`.

## 1. Why this file exists

Ledger section 30 sizes item 2c at "about 102 on the three systems plus whatever
the row-by-row test adds". I applied the ruling's own test to the ledger before
briefing the work. The test does not add a little to 102. It nearly triples it.

I have not dispatched item 2c. Nothing else is delayed by this question.

## 2. The test, applied mechanically

The rule from section 30 and `design-thread-queue.md` section 4.23 ruling 1: a
row stays `dormant` only if its named future system is recorded as planned work
on this queue or in a contract. Every other dormant row resolves now.

The 247 dormant rows sit on 20 future systems. I searched each system name
across `design-thread-queue.md`, `future-work-kanban.md`, `progress.md` and
`activeContext.md`:

| Future system | Rows | Recorded as planned work? |
| --- | ---: | --- |
| `world_transport_actions` | 48 | No — ruled resolve |
| `npc_dialogue_actions` | 38 | No — ruled resolve |
| `location_visit_actions` | 16 | No — ruled resolve |
| `combat_encounter_actions` | 19 | Not named anywhere |
| `object_interaction_actions` | 18 | Not named anywhere |
| `item_processing_actions` | 18 | Not named anywhere |
| `skill_action_telemetry` | 17 | Not named anywhere |
| `familiar_actions` | 9 | Not named anywhere |
| `shop_transaction_actions` | 7 | Not named anywhere |
| `item_use_actions` | 7 | Not named anywhere |
| `equipment_state_actions` | 7 | Not named anywhere |
| `spell_cast_actions` | 7 | Not named anywhere |
| `item_acquisition_actions` | 7 | Not named anywhere |
| `prayer_altar_actions` | 6 | Not named anywhere |
| `minigame_actions` | 6 | Not named anywhere |
| `combat_special_actions` | 5 | Not named anywhere |
| `quest_stage_actions` | 5 | Named, but **retired**, see 3.1 |
| `world_emote_actions` | 3 | Not named anywhere |
| `bank_inventory_actions` | 2 | **Yes**, via item 2b, see 3.2 |
| `activity_completion_actions` | 2 | Not named anywhere |

On the record as it stands, exactly one system carries planned work, and it
covers one row. **The resolve set is about 245 of 247, not 102.**

## 3. Two rows the name search got wrong in both directions

### 3.1 `quest_stage_actions` is retired, not planned

The name appears in the queue and the memory bank, so a name search scores it as
planned. It is the opposite. `memory-bank/archive/progress-2026-09.md:1360`:

> Config version 123 retires the quest-local `quest_stage_actions` model. New and
> copied player data omit it, completed stages write only the global
> `quest_action_proofs` ledger, and migration drops the old key from existing
> saves.

So those 5 Burthorpe rows name a model the product deleted. One of them states
the retired model in its trigger outright:

```
burthorpe_period_rendezvous
  Complete on a quest_stage_actions event source_task_id=531 and
  stage_id=burthorpe_troll_tunnel_attack_stopped;
```

They resolve, and the replacement should point at `quest_action_proofs`.

### 3.2 `bank_inventory_actions` is planned, and the name search could not see it

Item 2b builds the Beefy Bill banking service, which is exactly the planned work
for `lumbridge_medium_where_s_the_beef`. The queue talks about Beefy Bill and
never about the system id, so no name search would find it.

That is the general warning: **the ruling's test cannot be executed by matching
system names.** Planned work is recorded in prose about features, not in system
identifiers. An agent asked to apply this test by search will get both of these
rows wrong, in opposite directions.

## 4. A conflict between two live rulings

Section 26.1 item 3 rules that `lumbridge_easy_money_down_the_drayn` stays
`dormant`, because its trigger needs a Draynor Village bank identity and the Bank
is locationless by settled design.

Section 30 closes exactly that reasoning: a locationless model is why transport
and location rows must resolve rather than wait. The Draynor row's blocker is a
location concept in a locationless model, so under section 30 it resolves like
the rest, by translation, swap, or invention.

Both rulings are yours. Section 30 is later and broader, so I read it as
superseding 26.1 item 3, and I will brief it that way unless you say otherwise.

## 5. Options, with my lean

- **Option A — brief 2c at the measured 245 rows.** Faithful to the owner's
  words. It is no longer a bounded pass; it is the largest records task on the
  board, and 245 invented or translated deeds is a great deal of design judgment
  for one authoring agent.
- **Option B — brief 2c at the ruled 102 now, and run the row-by-row test as a
  separate later pass.** Keeps this pass bounded and ships the clear-cut rows,
  at the cost of leaving 143 rows resting on a test nobody has applied.
- **Option C — you first record which systems are planned work, then 2c resolves
  exactly the complement.** One short list from you turns an ambiguous test into
  an executable one.

**My lean is C, then execute at whatever size it yields.** The reason is not
caution about the number. It is that "is this system planned work" is a question
about what the product intends to build, which is a design decision. An
implementation agent that has to answer it will answer it by guessing, and a
guess dressed as a curation decision is the invented-mechanic failure mode this
project has shipped before. Your list makes the test mechanical; without it, the
`invented` disposition becomes a place for an agent's guesses to hide.

If you pick C, the list I need is short: for each of the 20 systems above, is it
planned work, yes or no. I will take `bank_inventory_actions` as yes and
`quest_stage_actions` as no unless you correct me.

## 6. Status

Item 2c is not dispatched and is not blocking. Item 1 is gated and awaits its
review round before landing. Item 2 is authoring. Bill's harvest is running.
Two reviewers are reading the Mogre diff.
